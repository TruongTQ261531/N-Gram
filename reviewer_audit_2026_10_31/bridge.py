"""Retrospective same-feature float/integer audit, not a new confirmation."""
import os
for key in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS','NUMEXPR_NUM_THREADS'):
    os.environ[key]='1'
from pathlib import Path
import argparse
import gzip
import hashlib
import itertools
import json
import math
import pickle
import sys
import time
import unicodedata
import numpy as np
import pandas as pd
from scipy import sparse

ROOT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT.parent))
from lazy_cert_study.core import lattice,topk
from pool_study.core import SCALE,normalize


def states(forms,budget):
    for cost in range(min(budget,len(forms))+1):
        for positions in itertools.combinations(range(len(forms)),cost):
            for alternatives in itertools.product(*(range(1,len(forms[t])) for t in positions)):
                state=[0]*len(forms)
                for t,a in zip(positions,alternatives):state[t]=a
                yield state


def quantization_bound(maximum,scale=SCALE):
    """Upper envelope for fl(fl(scale*w)+.5) followed by floor.

    EPS is deliberately larger than unit roundoff. Inputs/scale and rounded
    integers must fit finite float64/int64 and exactly represented integers.
    Each nonnegative envelope operation rounds upward once.
    """
    if not 0<=maximum*scale<2**52:raise OverflowError('Unverified quantizer range')
    up=lambda z:float(np.nextafter(z,np.inf))
    eps=np.finfo(np.float64).eps
    half=up(.5/scale)
    gamma=up((2*eps)/(1-2*eps))
    return up(half+up(gamma*up(maximum+half)))


def transfer(scores,k,feature_mass,delta):
    answer=topk(scores,k)
    if feature_mass==0:return True,answer,0
    if len(answer)!=k:return False,answer,None
    boundary=np.partition(scores,-(k+1))[-(k+1):]
    gap=int(boundary[1:].min())-int(boundary.min())
    epsilon=float(np.nextafter(feature_mass*delta,np.inf))
    threshold=math.ceil(float(np.nextafter(float(np.nextafter(2*SCALE*epsilon,np.inf)),np.inf)))
    return gap>threshold,answer,gap


def rebuild_float(index,data):
    product=pd.read_csv(data/'dataset/product.csv',sep='\t',dtype={'product_id':str}).fillna('')
    texts={str(r['product_id']):' '.join(str(r[x]) for x in ['product_name','product_class','product_description'])
        for r in product.to_dict('records')}
    ordered=[texts[i] for i in index.ids]
    differing=sum(normalize(t)!=' '.join(unicodedata.normalize('NFC',t).casefold().split()) for t in ordered)
    C=index.vectorizer.transform(ordered).tocsr()
    assert C.shape==index.weights.shape
    lengths=np.asarray(C.sum(axis=1)).ravel()
    df=np.bincount(C.indices,minlength=C.shape[1])
    idf=np.log1p((index.n-df+.5)/(df+.5))
    denominator=1.2*(.25+.75*lengths/max(float(lengths.mean()),1e-30))
    F=C.astype(np.float64)
    F.data=F.data*2.2/(F.data+np.repeat(denominator,np.diff(F.indptr)))*idf[F.indices]
    np.testing.assert_array_equal(F.indptr,index.weights.indptr)
    np.testing.assert_array_equal(F.indices,index.weights.indices)
    np.testing.assert_array_equal(np.floor(F.data*SCALE+.5).astype(np.int64),index.weights.data)
    delta=quantization_bound(float(F.data.max(initial=0)))
    # Observed residual is descriptive; the analytic envelope is the proof.
    residual=float(np.max(np.abs(F.data-index.weights.data/SCALE),initial=0))
    assert residual<=delta
    return F.T.tocsr(),{'quantizationBound':delta,'observedMaxWeightResidual':residual,
        'sameVocabularyAndAllRoundedWeights':True,'documentsWithLowerCasefoldDifference':differing,
        'nonzeroWeights':F.nnz}


def main():
    p=argparse.ArgumentParser();p.add_argument('--data',type=Path,required=True)
    p.add_argument('--output',type=Path,required=True);p.add_argument('--limit',type=int)
    args=p.parse_args()
    if args.output.exists():raise FileExistsError(args.output)
    source=json.loads((ROOT.parent/'lazy_cert_study/sources.json').read_text())
    for item in source['files']:
        assert hashlib.sha256((args.data/item['path']).read_bytes()).hexdigest()==item['sha256']
    scope=json.loads((ROOT/'scope.json').read_text());ids=scope['bridgeIds']
    if args.limit is not None:ids=ids[:args.limit]
    with (args.data/'index.pkl').open('rb') as f:index=pickle.load(f)
    started=time.perf_counter();float_transpose,build=rebuild_float(index,args.data)
    build['seconds']=time.perf_counter()-started
    query=pd.read_csv(args.data/'dataset/query.csv',sep='\t',dtype={'query_id':str}).fillna('')
    texts=dict(zip(query.query_id,query['query']))
    gold={}
    with gzip.open(ROOT.parent/'lazy_cert_study/results/confirmation.jsonl.gz','rt') as f:
        for line in f:
            row=json.loads(line);gold[row['queryId']]=row['oracleUnion']
    args.output.parent.mkdir(parents=True,exist_ok=True)
    with gzip.open(args.output,'xt') as log:
        for number,qid in enumerate(ids,1):
            Q=lattice(index,texts[qid]);integer_union=np.zeros(index.n,dtype=bool)
            float_union=np.zeros(index.n,dtype=bool);count=equal=certified=unresolved=tied=0
            max_error=0.;raw_equal=None;sample_disagreements=[]
            for state in states(Q.forms,2):
                text=' '.join(f[a]['text'] for f,a in zip(Q.forms,state))
                X=index.vectorizer.transform([text]);mass=int(X.sum())
                zi=(X@index.transpose).toarray()[0]
                zf=(X@float_transpose).toarray()[0]
                safe,ti,gap=transfer(zi,10,mass,build['quantizationBound'])
                tf=topk(zf,10);same=np.array_equal(ti,tf)
                if safe:assert same,(qid,state,'transfer violation')
                numerical_count=2*int(X.nnz)+2;eps=np.finfo(float).eps
                gamma=numerical_count*eps/(1-numerical_count*eps)
                dot_error=float(np.nextafter(gamma/(1-gamma)*np.abs(zf).max(initial=0)+
                    numerical_count*np.nextafter(0.,1.),np.inf))
                float_boundary=np.partition(zf,-11)[-11:]
                float_gap=float(float_boundary[1:].min()-float_boundary.min())
                resolved=(mass==0 or (len(tf)==10 and float_gap>2*dot_error))
                integer_union[ti]=True;float_union[tf]=True
                count+=1;equal+=int(same);certified+=int(safe);unresolved+=int(not resolved)
                tied+=int(len(ti)>10)
                max_error=max(max_error,float(np.max(np.abs(zf-zi/SCALE),initial=0)))
                if count==1:raw_equal=same
                if not same and len(sample_disagreements)<5:
                    sample_disagreements.append({'state':state,'integer':ti.tolist(),'floatObserved':tf.tolist(),
                        'integerGap':gap,'floatBoundaryResolved':resolved})
            np.testing.assert_array_equal(np.flatnonzero(integer_union),gold[qid])
            row={'queryId':qid,'states':count,'stateTopKEqual':equal,'stateTransferCertified':certified,
                'floatBoundaryUnresolved':unresolved,'integerTiedStates':tied,'rawTopKEqual':raw_equal,
                'unionObservedEqual':bool(np.array_equal(integer_union,float_union)),
                'unionTransferCertified':certified==count,'integerUnionSize':int(integer_union.sum()),
                'floatObservedUnionSize':int(float_union.sum()),'maxObservedScoreError':max_error,
                'sampleDisagreements':sample_disagreements}
            log.write(json.dumps(row,separators=(',',':'))+'\n');log.flush()
            print(number,'/',len(ids),'id',qid,'states',count,'equal',equal,'transfer',certified,flush=True)
    with gzip.open(args.output,'rt') as f:rows=[json.loads(line) for line in f]
    report={'status':'COMPLETE' if args.limit is None else 'SMOKE_ONLY','retrospective':True,
        'queries':len(rows),'stateCount':sum(r['states'] for r in rows),
        'stateTopKEqual':sum(r['stateTopKEqual'] for r in rows),
        'stateTransferCertified':sum(r['stateTransferCertified'] for r in rows),
        'floatBoundaryUnresolved':sum(r['floatBoundaryUnresolved'] for r in rows),
        'integerTiedStates':sum(r['integerTiedStates'] for r in rows),
        'queryRawTopKEqual':sum(r['rawTopKEqual'] for r in rows),
        'queryUnionObservedEqual':sum(r['unionObservedEqual'] for r in rows),
        'queryUnionTransferCertified':sum(r['unionTransferCertified'] for r in rows),
        'queryLowerCasefoldDifference':sum(normalize(texts[i])!=' '.join(unicodedata.normalize('NFC',texts[i]).casefold().split()) for i in ids),
        'build':build,'rowsSha256':hashlib.sha256(args.output.read_bytes()).hexdigest(),
        'scope':'Same lowercase features and compact lattice; no transfer of legacy casefold retention results.'}
    args.output.with_name(args.output.name+'.summary.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report,indent=2),flush=True)


if __name__=='__main__':main()
