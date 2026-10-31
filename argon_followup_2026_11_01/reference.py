"""Complete raw-U FP32 reference; preserve the earlier completed partial rows."""
import argparse,gzip,hashlib,json,pickle
from pathlib import Path
import pandas as pd
from argon_followup_2026_11_01.neural_torch_original import Predictor
from argon_followup_2026_11_01.neural import rank_scores

ROOT=Path(__file__).resolve().parent


def main():
    p=argparse.ArgumentParser();p.add_argument('--data',type=Path,required=True);p.add_argument('--model',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    if a.output.exists():raise FileExistsError(a.output)
    spec=json.loads((ROOT/'MODEL_SOURCE.json').read_text())
    for item in spec['files']:assert hashlib.sha256((a.model/item['name']).read_bytes()).hexdigest()==item['sha256']
    with gzip.open(ROOT/'results/neural-torch-partial/raw.jsonl.gz','rt') as f:partial={r['queryId']:r for r in map(json.loads,f)}
    with gzip.open(ROOT.parent/'lazy_cert_study/results/confirmation.jsonl.gz','rt') as f:old=[json.loads(s) for s in f]
    with (a.data/'index.pkl').open('rb') as f:index=pickle.load(f)
    assert all(r['modelHash']==index.model_hash for r in old)
    q=pd.read_csv(a.data/'dataset/query.csv',sep='\t',dtype={'query_id':str}).fillna('');queries=dict(zip(q.query_id,q['query']))
    product=pd.read_csv(a.data/'dataset/product.csv',sep='\t',dtype={'product_id':str}).fillna('')
    by_id={str(r['product_id']):' '.join(str(r[k]) for k in ['product_name','product_class','product_description']) for r in product.to_dict('records')}
    model=Predictor(a.model,[by_id[i] for i in index.ids])
    with gzip.open(a.output,'xt') as out:
        for r in old:
            qid=r['queryId'];docs=r['oracleUnion']
            if qid in partial:
                row=partial[qid];assert row['union']==docs
                z=row['logits'];measure=row['measure'];reused=True
            else:z,measure=model.score(queries[qid],docs);z=z.tolist();reused=False
            ordered=rank_scores(z,docs,index.ids)
            out.write(json.dumps({'queryId':qid,'union':docs,'logits':z,'top10':ordered[:10],'measure':measure,'reusedCompletedPartial':reused},separators=(',',':'))+'\n');out.flush()
            print('FP32 reference',qid,'pairs',len(docs),'reused',reused,flush=True)


if __name__=='__main__':main()
