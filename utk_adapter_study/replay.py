"""Replay all endpoint selections, original scores and whole-corpus exclusions."""
import os
for key in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS','NUMEXPR_NUM_THREADS'):
    os.environ[key]='1'
import argparse
import gzip
import hashlib
import json
from pathlib import Path
import pickle
import numpy as np
import pandas as pd
from reviewer_audit_2026_10_31.bridge import states
from lazy_cert_study.core import lattice
from utk_adapter_study.adapter import embedding, safe_pool, selected_state

ROOT=Path(__file__).resolve().parent


def main():
    p=argparse.ArgumentParser(); p.add_argument('--data',type=Path,required=True)
    p.add_argument('--output',type=Path,required=True); args=p.parse_args()
    if args.output.exists(): raise FileExistsError(args.output)
    with gzip.open(ROOT/'results/records.jsonl.gz','rt') as f: rows=[json.loads(s) for s in f]
    with (args.data/'index.pkl').open('rb') as f: index=pickle.load(f)
    with gzip.open(ROOT.parent/'lazy_cert_study/results/confirmation.jsonl.gz','rt') as f:
        gold=[json.loads(s) for s in f]
    expected=gold[0]['modelHash']
    assert index.model_hash==expected and all(r['modelHash']==expected for r in gold)
    # Reconstruct the canonical hash from current arrays, rather than trusting
    # the model_hash string saved in the pickle.
    h=hashlib.sha256()
    for a in (index.weights.indptr,index.weights.indices,index.weights.data):
        h.update(a.astype('<i8').tobytes())
    h.update('\n'.join(index.ids).encode())
    h.update('\n'.join(index.vectorizer.get_feature_names_out()).encode())
    assert h.hexdigest()==expected
    query=pd.read_csv(args.data/'dataset/query.csv',sep='\t',dtype={'query_id':str}).fillna('')
    texts=dict(zip(query.query_id,query['query']))
    for r in rows:
        text=texts[r['queryId']]
        assert hashlib.sha256(text.encode()).hexdigest()==r['querySha256']
        q=lattice(index,text); chosen=selected_state(states(q.forms,2),r['queryId'])
        assert chosen==r['state']
        a=(q.raw_features@index.transpose).toarray()[0]
        modified=' '.join(f[s]['text'] for f,s in zip(q.forms,chosen))
        b=(index.vectorizer.transform([modified])@index.transpose).toarray()[0]
        _,ea,eb,meta=embedding(a,b)
        pi,ri=safe_pool(a,b,10); pe,re=safe_pool(ea,eb,10)
        pool=np.union1d(pi,pe)
        assert pool.tolist()==r['pool'] and ri==r['originalScreen'] and re==r['exportScreen']
        assert a[pool].tolist()==r['originalA'] and b[pool].tolist()==r['originalB']
        assert ea[pool].tolist()==r['exportA'] and eb[pool].tolist()==r['exportB'] and meta==r['embedding']
    receipt={'status':'PASS','queries':len(rows),'modelHash':expected,
        'independentArrayDigest':h.hexdigest(),'allEndpointSelectionsAndScoresReplayed':True,
        'allOriginalAndExportedContinuousRegionExclusionsReplayed':True,
        'scope':'Same pinned original integer index, no new scorer fitting',
        'recordsSha256':hashlib.sha256((ROOT/'results/records.jsonl.gz').read_bytes()).hexdigest()}
    args.output.write_text(json.dumps(receipt,indent=2)+'\n')
    print(json.dumps(receipt,indent=2))


if __name__=='__main__': main()
