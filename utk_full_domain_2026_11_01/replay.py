"""Post-timing, independent whole-corpus sparse-text replay of EVERY state."""
import os
for key in ['OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS','NUMEXPR_NUM_THREADS']:os.environ[key]='1'
import argparse,gzip,hashlib,itertools,json,pickle,time
from pathlib import Path
import numpy as np
import pandas as pd
from lazy_cert_study.core import lattice
from lazy_cert_study.benchmark import states
from utk_full_domain_2026_11_01.run import ROOT,digest


def main():
    p=argparse.ArgumentParser();p.add_argument('--data',type=Path,required=True);a=p.parse_args()
    freeze=json.loads((ROOT/'FREEZE.json').read_text())
    assert digest(a.data/'index.pkl')==freeze['privateIndexSha256']
    for item in json.loads((ROOT.parent/'lazy_cert_study/sources.json').read_text())['files']:
        assert digest(a.data/item['path'])==item['sha256']
    with (a.data/'index.pkl').open('rb') as f:index=pickle.load(f)
    q=pd.read_csv(a.data/'dataset/query.csv',sep='\t',dtype={'query_id':str}).fillna('')
    texts=dict(zip(q.query_id,q['query']));path=ROOT/'results/oracle.jsonl.gz'
    started=time.perf_counter();total=0
    with gzip.open(path,'xt') as out:
        for qid in freeze['queryIds']:
            Q=lattice(index,texts[qid]);state_list=list(states(Q.forms,2));records=[];union=set()
            for offset in range(0,len(state_list),32):
                batch=state_list[offset:offset+32]
                rendered=[' '.join(f[a]['text'] for f,a in zip(Q.forms,s)) for s in batch]
                # Re-vectorize complete text and score the UNPROJECTED original corpus.
                scores=(index.vectorizer.transform(rendered)@index.transpose).toarray()
                cut=np.partition(scores,-10,axis=1)[:,-10]
                for s,text,value,threshold in zip(batch,rendered,scores,cut):
                    top=np.flatnonzero(value>=threshold).tolist();union.update(top)
                    records.append({'state':s,'textSha256':hashlib.sha256(text.encode()).hexdigest(),'top':top,'threshold':int(threshold)})
            row={'queryId':qid,'modelHash':index.model_hash,'states':records,'union':sorted(union)}
            out.write(json.dumps(row,separators=(',',':'))+'\n');out.flush();total+=len(records)
            print(qid,'states',len(records),'union',len(union),flush=True)
    (ROOT/'results/replay.json').write_text(json.dumps({'status':'COMPLETE','queries':len(freeze['queryIds']),
        'states':total,'seconds':time.perf_counter()-started,'oracleSha256':digest(path),
        'modelHash':index.model_hash,'privateIndexSha256':freeze['privateIndexSha256'],
        'scope':'Independent full-text, full-corpus, all-state replay; separate from method timers'},indent=2)+'\n')


if __name__=='__main__':main()
