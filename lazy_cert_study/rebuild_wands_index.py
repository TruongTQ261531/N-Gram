"""Post-run source reconstruction; never used to select a candidate or query."""
from pathlib import Path
import argparse
import hashlib
import json
import pickle
import sys
import time
import numpy as np
import pandas as pd

ROOT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT.parent))
from pool_study.core import Index


def main():
    p=argparse.ArgumentParser();p.add_argument('--data',type=Path,required=True)
    p.add_argument('--output',type=Path,required=True);args=p.parse_args()
    if args.output.exists():raise FileExistsError(args.output)
    source=json.loads((ROOT/'sources.json').read_text())
    for item in source['files']:
        assert hashlib.sha256((args.data/item['path']).read_bytes()).hexdigest()==item['sha256']
    receipt=json.loads((args.data/'index-receipt.json').read_text())
    started=time.perf_counter()
    product=pd.read_csv(args.data/'dataset/product.csv',sep='\t',dtype={'product_id':str}).fillna('')
    docs=[{'id':str(row['product_id']),
        'text':' '.join(str(row[x]) for x in ['product_name','product_class','product_description'])}
        for row in product.to_dict('records')]
    rebuilt=Index(docs)
    assert rebuilt.model_hash==receipt['modelHash']
    with (args.data/'index.pkl').open('rb') as f:original=pickle.load(f)
    assert original.ids==rebuilt.ids
    for name in ['indptr','indices','data']:
        np.testing.assert_array_equal(getattr(original.weights,name),getattr(rebuilt.weights,name))
    np.testing.assert_array_equal(original.vectorizer.get_feature_names_out(),
                                  rebuilt.vectorizer.get_feature_names_out())
    report={'status':'PASS','documents':rebuilt.n,'nonzeroWeights':rebuilt.weights.nnz,
        'modelHash':rebuilt.model_hash,'seconds':time.perf_counter()-started,
        'sourceCommit':source['commit'],'allInputHashesVerified':True,
        'allIntegerWeightsAndDocumentIdsEqual':True,
        'checkerSha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        'scope':'Reconstructs the fixed source index. Does not replace a closest-method or independent human review.'}
    args.output.write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))


if __name__=='__main__':main()
