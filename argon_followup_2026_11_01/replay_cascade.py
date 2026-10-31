"""Independently compare complete finite-domain lexical inputs to a reranker."""
import os
for k in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS'):os.environ[k]='1'
import argparse,gzip,hashlib,json,pickle
from pathlib import Path
import numpy as np
import pandas as pd
from lazy_cert_study.core import lattice,topk
from reviewer_audit_2026_10_31.bridge import states

ROOT=Path(__file__).resolve().parent


def main():
    p=argparse.ArgumentParser();p.add_argument('--data',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    if a.output.exists():raise FileExistsError(a.output)
    with (a.data/'index.pkl').open('rb') as f:index=pickle.load(f)
    with gzip.open(ROOT.parent/'lazy_cert_study/results/confirmation.jsonl.gz','rt') as f:old=[json.loads(s) for s in f]
    texts=pd.read_csv(a.data/'dataset/query.csv',sep='\t',dtype={'query_id':str}).fillna('');texts=dict(zip(texts.query_id,texts['query']))
    with gzip.open(a.output,'xt') as out:
        for oldrow in old:
            assert index.model_hash==oldrow['modelHash']
            qid=oldrow['queryId'];Q=lattice(index,texts[qid]);U=np.array(oldrow['oracleUnion'],dtype=int)
            union=set();pairs=set();rows=[]
            for state in states(Q.forms,2):
                text=' '.join(f[s]['text'] for f,s in zip(Q.forms,state))
                scores=(index.vectorizer.transform([text])@index.transpose).toarray()[0]
                full=topk(scores,10);local=U[topk(scores[U],10)]
                np.testing.assert_array_equal(full,local)
                digest=hashlib.sha256(text.encode()).hexdigest()
                pairs.update((digest,int(d)) for d in full);union.update(full.tolist())
                rows.append({'state':state,'requestSha256':digest,'lexicalTopIds':full.tolist()})
            assert sorted(union)==U.tolist()
            out.write(json.dumps({'queryId':qid,'states':rows,'uniqueNeuralPairsFull':len(pairs),'uniqueNeuralPairsGivenUnion':len(pairs)},separators=(',',':'))+'\n');out.flush()
            print('lexical replay',qid,len(rows),'pairs',len(pairs),flush=True)


if __name__=='__main__':main()
