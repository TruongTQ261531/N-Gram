"""Export only public WANDS IDs and existing grades, no corpus/query text."""
import argparse,gzip,hashlib,json,pickle
from pathlib import Path
import pandas as pd

ROOT=Path(__file__).resolve().parent


def main():
    p=argparse.ArgumentParser();p.add_argument('--data',type=Path,required=True);a=p.parse_args()
    target=ROOT/'results/judgments.json.gz'
    if target.exists():raise FileExistsError(target)
    with (a.data/'index.pkl').open('rb') as f:index=pickle.load(f)
    with gzip.open(ROOT.parent/'lazy_cert_study/results/confirmation.jsonl.gz','rt') as f:old=[json.loads(s) for s in f]
    selected={r['queryId'] for r in old};grades={};policy={'Exact':2,'Partial':1,'Irrelevant':0}
    frame=pd.read_csv(a.data/'dataset/label.csv',sep='\t',dtype={'query_id':str,'product_id':str})
    for r in frame.to_dict('records'):
        if r['query_id'] not in selected:continue
        g=grades.setdefault(r['query_id'],{});g[r['product_id']]=max(g.get(r['product_id'],0),policy[r['label']])
    report={'sourceLabelSha256':hashlib.sha256((a.data/'dataset/label.csv').read_bytes()).hexdigest(),
            'policy':'Maximum existing grade per repeated query/product pair; Exact2 Partial1 Irrelevant0',
            'modelHash':index.model_hash,'documentIds':index.ids,'grades':grades,'rawTextRedistributed':False}
    with gzip.open(target,'xt') as f:json.dump(report,f,separators=(',',':'))
    print('Exported public IDs and original grades for',len(grades),'queries')


if __name__=='__main__':main()
