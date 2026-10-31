"""Resolve backend boundary ties with exact dyadic sums; same-data audit."""
from pathlib import Path
from fractions import Fraction
import argparse
import gzip
import hashlib
import json
import pickle
import sys
import numpy as np
import pandas as pd

ROOT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT.parent))
from reviewer_audit_2026_10_31.bridge import rebuild_float,states,SCALE
from reviewer_audit_2026_10_31.retention import Index,native
from lazy_cert_study.core import lattice,topk


def dyadic_sum(values,coefficients):
    total=0;power=0
    for value,coefficient in zip(values,coefficients):
        numerator,denominator=float(value).as_integer_ratio()
        exponent=denominator.bit_length()-1
        if exponent>power:total<<=exponent-power;power=exponent
        total+=(int(coefficient)*numerator)<<(power-exponent)
    return Fraction(total,1<<power)


def exact_scores(transpose,X,documents):
    documents=np.asarray(documents,dtype=int)
    local=transpose[X.indices][:,documents].tocsc()
    counts=X.data
    assert np.all(counts==counts.astype(np.int64))
    result=[]
    for column in range(len(documents)):
        start,end=local.indptr[column:column+2]
        result.append(dyadic_sum(local.data[start:end],counts[local.indices[start:end]]))
    return result


def dot_error(X,z):
    up=lambda v:float(np.nextafter(v,np.inf))
    operations=2*X.nnz+2;eps=np.finfo(float).eps
    gamma=up(operations*eps/(1-operations*eps))
    return up(up(gamma/(1-gamma))*float(np.abs(z).max(initial=0))+
        operations*np.nextafter(0.,1.))


def exact_topk(transpose,X,z,k,cap=256):
    error=dot_error(X,z)
    low=np.nextafter(z-error,-np.inf);high=np.nextafter(z+error,np.inf)
    observed=topk(z,k)
    if X.nnz==0:return np.arange(len(z)),True,0
    threshold=float(np.partition(z,-k)[-k])
    # kth order statistic is within [threshold-error,threshold+error].
    threshold_low=float(np.nextafter(threshold-error,-np.inf))
    threshold_high=float(np.nextafter(threshold+error,np.inf))
    above=np.flatnonzero(low>threshold_high)
    ambiguous=np.flatnonzero((low<=threshold_high)&(high>=threshold_low))
    if len(ambiguous)>cap:return observed,False,len(ambiguous)
    exact=exact_scores(transpose,X,ambiguous)
    remaining=k-len(above)
    assert 1<=remaining<=len(ambiguous)
    boundary=sorted(exact,reverse=True)[remaining-1]
    selected=[int(j) for j,value in zip(ambiguous,exact) if value>=boundary]
    return np.sort(np.r_[above,selected]).astype(int),True,len(ambiguous)


def exact_reference_rank(transpose,X,z,reference,cap=256):
    exact_reference=exact_scores(transpose,X,[reference])[0]
    if exact_reference==0:return (len(z),len(z)),0
    error=dot_error(X,z)
    low=np.nextafter(z-error,-np.inf);high=np.nextafter(z+error,np.inf)
    above=low>high[reference]
    uncertain=np.flatnonzero((low<=high[reference])&(high>=low[reference]))
    uncertain=uncertain[uncertain!=reference]
    certain=int(above.sum())+1
    if len(uncertain)>cap:return (certain,certain+len(uncertain)),len(uncertain)
    exact=exact_scores(transpose,X,uncertain)
    rank=certain+sum(value>=exact_reference for value in exact)
    return (rank,rank),len(uncertain)


def main():
    p=argparse.ArgumentParser();p.add_argument('--data',type=Path,required=True)
    p.add_argument('--output',type=Path,required=True);args=p.parse_args()
    if args.output.exists():raise FileExistsError(args.output)
    source=json.loads((ROOT.parent/'lazy_cert_study/sources.json').read_text())
    for item in source['files']:
        assert hashlib.sha256((args.data/item['path']).read_bytes()).hexdigest()==item['sha256']
    with (args.data/'index.pkl').open('rb') as f:integer=pickle.load(f)
    lower_transpose,build=rebuild_float(integer,args.data)
    product=pd.read_csv(args.data/'dataset/product.csv',sep='\t',dtype={'product_id':str}).fillna('')
    text_by_id={str(r['product_id']):' '.join(str(r[x]) for x in ['product_name','product_class','product_description'])
        for r in product.to_dict('records')}
    folded=Index([text_by_id[i] for i in integer.ids],integer.ids,'char')
    folded_transpose=folded.transpose()
    assert folded.W.data.min(initial=1.)>1e-250
    query=pd.read_csv(args.data/'dataset/query.csv',sep='\t',dtype={'query_id':str}).fillna('')
    text_by_qid=dict(zip(query.query_id,query['query']))
    ids=json.loads((ROOT/'scope.json').read_text())['bridgeIds'];rows=[]
    with gzip.open(args.output,'xt') as out:
        for number,qid in enumerate(ids,1):
            Q=lattice(integer,text_by_qid[qid]);count=0;integer_union=np.zeros(integer.n,dtype=bool)
            union={m:np.zeros(integer.n,dtype=bool) for m in ['floatLower','floatCasefold']}
            equal={m:0 for m in union};resolved={m:0 for m in union}
            worst={m:[0,0] for m in union};worst_integer=0;rank_resolved={m:0 for m in union}
            raw_reference_is_winner={};samples=[]
            for state in states(Q.forms,2):
                text=' '.join(f[a]['text'] for f,a in zip(Q.forms,state))
                X=integer.vectorizer.transform([text]);zi=(X@integer.transpose).toarray()[0]
                ti=topk(zi,10);integer_union[ti]=True
                if count==0:reference=int(np.lexsort((np.array(integer.ids),-zi))[0])
                worst_integer=max(worst_integer,int((zi>=zi[reference]).sum()))
                representations=[('floatLower',X,lower_transpose),
                    ('floatCasefold',folded.v.transform([text]),folded_transpose)]
                for name,features,transpose in representations:
                    z=(features@transpose).toarray()[0]
                    true_top,exact,uncertain=exact_topk(transpose,features,z,10)
                    interval,rank_uncertain=exact_reference_rank(transpose,features,z,reference)
                    same=np.array_equal(ti,true_top)
                    union[name][true_top]=True;resolved[name]+=int(exact);equal[name]+=int(exact and same)
                    rank_resolved[name]+=int(interval[0]==interval[1])
                    worst[name]=[max(worst[name][i],interval[i]) for i in [0,1]]
                    if count==0:
                        raw_top,raw_exact,_=exact_topk(transpose,features,z,1)
                        raw_reference_is_winner[name]=bool(raw_exact and reference in raw_top)
                    if (not same or not exact or interval[0]!=interval[1]) and len(samples)<5:
                        samples.append({'state':state,'backend':name,'topExact':exact,'topEqual':same,
                            'topAmbiguous':uncertain,'rankInterval':interval,'rankAmbiguous':rank_uncertain})
                count+=1
            decisions={m:(True if worst[m][1]<=10 else False if worst[m][0]>10 else None) for m in union}
            row={'queryId':qid,'states':count,'integerWorstRank':worst_integer,
                'integerRetained':worst_integer<=10,'stateExactTopKEqual':equal,'stateTopKResolved':resolved,
                'stateRankResolved':rank_resolved,'worstRankIntervals':worst,'retentionDecisions':decisions,
                'queryUnionCertifiedEqual':{m:bool(resolved[m]==count and np.array_equal(integer_union,union[m])) for m in union},
                'rawReferenceIsWinner':raw_reference_is_winner,'samples':samples}
            rows.append(row);out.write(json.dumps(native(row),separators=(',',':'))+'\n');out.flush()
            print(number,'/',len(ids),'id',qid,'states',count,'exact',resolved,'rank',worst,flush=True)
    report={'status':'COMPLETE','retrospective':True,'queries':len(rows),
        'stateCount':sum(r['states'] for r in rows),'build':build,
        'backends':{m:{'stateTopKResolved':sum(r['stateTopKResolved'][m] for r in rows),
            'stateExactTopKEqual':sum(r['stateExactTopKEqual'][m] for r in rows),
            'stateRankResolved':sum(r['stateRankResolved'][m] for r in rows),
            'queryUnionCertifiedEqual':sum(r['queryUnionCertifiedEqual'][m] for r in rows),
            'queryWorstRankExact':sum(r['worstRankIntervals'][m][0]==r['worstRankIntervals'][m][1] for r in rows),
            'queryWorstRankEqual':sum(r['worstRankIntervals'][m]==[r['integerWorstRank']]*2 for r in rows),
            'queryRetentionDecisionCertifiedEqual':sum(r['retentionDecisions'][m] is not None and r['retentionDecisions'][m]==r['integerRetained'] for r in rows),
            'rawReferenceIsWinner':sum(r['rawReferenceIsWinner'][m] for r in rows)} for m in ['floatLower','floatCasefold']},
        'rowsSha256':hashlib.sha256(args.output.read_bytes()).hexdigest(),
        'scope':'Exact dyadic sums of stored float weights; shared WANDS products, compact lattice and reference. Not identity of legacy indexes.'}
    args.output.with_name(args.output.name+'.summary.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report,indent=2),flush=True)


if __name__=='__main__':main()
