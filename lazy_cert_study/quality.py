"""Descriptive clean-query relevance context, separate from robustness claims."""
from pathlib import Path
import argparse
import hashlib
import json
import pickle
import sys
import numpy as np
import pandas as pd

ROOT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT.parent))
from pool_study.core import Index  # pickle dependency; fixed ranker, not trained here


def main():
    p=argparse.ArgumentParser();p.add_argument('--data',type=Path,required=True)
    p.add_argument('--phase',choices=['development','confirmation'],required=True)
    p.add_argument('--output',type=Path,required=True);args=p.parse_args()
    if args.output.exists():raise FileExistsError(args.output)
    if args.phase=='confirmation' and not (ROOT/'confirmation_freeze.json').exists():
        raise RuntimeError('Freeze confirmation first')
    selection=json.loads((ROOT/'selection.json').read_text())
    source=json.loads((ROOT/'sources.json').read_text())
    label_source=next(x for x in source['files'] if x['path']=='dataset/label.csv')
    label_path=args.data/'dataset/label.csv'
    assert hashlib.sha256(label_path.read_bytes()).hexdigest()==label_source['sha256']
    q=pd.read_csv(args.data/'dataset/query.csv',sep='\t',dtype={'query_id':str}).fillna('')
    texts=dict(zip(q.query_id,q['query']))
    labels=pd.read_csv(label_path,sep='\t',dtype={'query_id':str,'product_id':str})
    assert len(labels)==233448
    assert set(labels.label)=={'Exact','Partial','Irrelevant'}
    gains={'Exact':3.,'Partial':1.,'Irrelevant':0.}
    labels['gain']=labels.label.map(gains)
    duplicate=labels[labels.duplicated(['query_id','product_id'],keep=False)]
    integrity={'rawJudgments':len(labels),'duplicatePairs':duplicate.groupby(['query_id','product_id']).ngroups,
        'discordantPairs':int((duplicate.groupby(['query_id','product_id']).label.nunique()>1).sum()),
        'policy':'Collapse repeated query-product pairs by maximum existing grade; fixed before any quality outcome.'}
    labels=labels.groupby(['query_id','product_id'],as_index=False)['gain'].max()
    integrity['uniquePairs']=len(labels)
    with (args.data/'index.pkl').open('rb') as f:index=pickle.load(f)
    rows=[];discount=1/np.log2(np.arange(2,12))
    for qid in selection[args.phase]:
        judged=labels[labels.query_id==qid]
        rel={str(r.product_id):r.gain for r in judged.itertuples()}
        scores=index.score(texts[qid]);rank=np.lexsort((np.arange(index.n),-scores))[:10]
        ids=[index.ids[i] for i in rank]
        ideal=sorted(rel.values(),reverse=True)[:10];ideal+= [0.]*(10-len(ideal))
        dcg=float(sum(rel.get(doc,0.)*discount[i] for i,doc in enumerate(ids)))
        idcg=float(np.dot(ideal,discount))
        rows.append({'queryId':qid,'top10':ids,'nDCG10':dcg/idcg if idcg else 0.,
            'judgedTop10':sum(doc in rel for doc in ids),'hasPositiveQrel':bool(idcg)})
    report={'phase':args.phase,'queries':len(rows),'modelHash':index.model_hash,
        'convention':'Exact=2 Partial=1 Irrelevant=0; gain2^rel-1; unjudged0; deterministic score/doc-id ties for this metric only',
        'meanNDCG10':float(np.mean([r['nDCG10'] for r in rows])),
        'sourceIntegrity':integrity,
        'judgedTop10Fraction':sum(r['judgedTop10'] for r in rows)/(10*len(rows)),
        'queriesWithPositiveQrels':sum(r['hasPositiveQrel'] for r in rows),'rows':rows,
        'interpretation':'Same fixed clean ranker for every certifier. No relevance gain or semantic preservation claim.'}
    args.output.write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps({k:v for k,v in report.items() if k!='rows'},indent=2))


if __name__=='__main__':main()
