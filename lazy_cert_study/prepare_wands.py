"""Pin public WANDS inputs, select untouched queries, and build an external index."""
from pathlib import Path
import argparse
import hashlib
import json
import pickle
import sys
import time

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from pool_study.core import Index
import pandas as pd

ROOT = Path(__file__).resolve().parent


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--data', type=Path, required=True)
    args = parser.parse_args()
    data = args.data
    sources = json.loads((data/'source-manifest.json').read_text())
    for source in sources['files']:
        assert hashlib.sha256((data/source['path']).read_bytes()).hexdigest() == source['sha256']
    query = pd.read_csv(data/'dataset/query.csv', sep='\t', dtype={'query_id':str}).fillna('')
    assert len(query) == 480 and query.query_id.is_unique
    assert query['query'].str.strip().str.len().min() > 0
    ordered = sorted(query.query_id, key=lambda q:hashlib.sha256(('lazy-cert-wands-v1|'+q).encode()).digest())
    text = dict(zip(query.query_id, query['query']))
    selection = {
        'sourceCommit':sources['commit'], 'rule':'SHA256(lazy-cert-wands-v1|query_id), before retrieval outcomes',
        'development':ordered[:64], 'confirmation':ordered[64:192],
        'reserved_unseen':ordered[192:],
        'querySha256':{q:hashlib.sha256(text[q].encode()).hexdigest() for q in ordered},
        'representation':'product_name + product_class + product_description; no truncation',
        'labelUse':'Existing labels for evaluation context only, never query selection or index fitting',
    }
    destination = ROOT/'selection.json'
    if destination.exists():
        assert json.loads(destination.read_text()) == selection
    else:
        destination.write_text(json.dumps(selection,indent=2)+'\n')
    (ROOT/'sources.json').write_text(json.dumps(sources,indent=2)+'\n')
    cache = data/'index.pkl'
    if cache.exists():
        print('Index already exists; preserving:',cache)
        return
    started = time.perf_counter()
    product = pd.read_csv(data/'dataset/product.csv',sep='\t',dtype={'product_id':str}).fillna('')
    assert len(product)==42994 and product.product_id.is_unique
    docs=[{'id':str(r['product_id']),
           'text':' '.join(str(r[x]) for x in ['product_name','product_class','product_description'])}
          for r in product.to_dict('records')]
    index=Index(docs)
    with cache.open('wb') as f:pickle.dump(index,f,protocol=5)
    receipt={'documents':index.n,'modelHash':index.model_hash,
             'vocabulary':index.weights.shape[1],'nonzeroWeights':index.weights.nnz,
             'seconds':time.perf_counter()-started,'sourceCommit':sources['commit'],
             'representation':selection['representation'],'queryOutcomesComputed':False}
    (data/'index-receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
    print(json.dumps(receipt,indent=2),flush=True)


if __name__=='__main__':main()
