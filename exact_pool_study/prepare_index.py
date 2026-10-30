"""Build the original pinned index without overwriting frozen parent evidence."""
from method import legacy
from pathlib import Path
import argparse,hashlib,json,pickle,time,urllib.request
import pandas as pd
ROOT=Path(__file__).resolve().parent
def main():
    p=argparse.ArgumentParser();p.add_argument('--data',type=Path,required=True);p.add_argument('--dataset',choices=['arguana','scidocs'],required=True);p.add_argument('--receipt',type=Path);a=p.parse_args()
    destination=a.data/(a.dataset+'-index.pkl')
    if destination.exists():raise FileExistsError('Refusing to overwrite an index. Use a new data directory: '+str(destination))
    started=time.perf_counter();sources=json.loads((ROOT.parent/'pool_study/sources.json').read_text())
    for source in sources:
        if source['dataset']!=a.dataset:continue
        target=a.data/a.dataset/source['path'];target.parent.mkdir(parents=True,exist_ok=True)
        if not target.exists():
            with urllib.request.urlopen(source['url'],timeout=120) as f:target.write_bytes(f.read())
        assert hashlib.sha256(target.read_bytes()).hexdigest()==source['sha256'],target
    corpus=pd.read_parquet(a.data/a.dataset/'corpus/corpus-00000-of-00001.parquet').fillna('')
    docs=[{'id':str(x['_id']),'title':str(x.get('title','')),'text':str(x['text'])} for x in corpus.to_dict('records')]
    I=legacy.Index(docs);expected=json.loads((ROOT.parent/'pool_study/results'/a.dataset/'environment.json').read_text())['modelHash'];assert I.model_hash==expected,'Stored integer ranker differs; do not mix its outcomes with the published target.'
    with destination.open('wb') as f:pickle.dump(I,f,protocol=5)
    receipt={'dataset':a.dataset,'documents':I.n,'modelHash':I.model_hash,'matchesFrozenStoredIntegerIndex':True,'sourceFilesHashChecked':True,'frozenParentFilesModified':False,'seconds':time.perf_counter()-started}
    if a.receipt:a.receipt.write_text(json.dumps(receipt,indent=2))
    print(json.dumps(receipt,indent=2))
if __name__=='__main__':main()
