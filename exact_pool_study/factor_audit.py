"""Separately frozen engineering audit; primary/workload outputs unchanged."""
from method import compiled_pool,exact_from_pool
from fast_factors import factors
from pathlib import Path
import argparse,gzip,hashlib,json,pickle,time
import numpy as np
ROOT=Path(__file__).resolve().parent
def main():
    p=argparse.ArgumentParser();p.add_argument('--data',type=Path,required=True);p.add_argument('--dataset',choices=['arguana','scidocs'],required=True);a=p.parse_args()
    freeze=json.loads((ROOT/'factor_freeze.json').read_text())
    for name,h in freeze['files'].items():assert hashlib.sha256((ROOT.parent/name).read_bytes()).hexdigest()==h,name
    out=ROOT/'results'/a.dataset/'factor-audit.jsonl.gz'
    if out.exists():raise RuntimeError('Refusing to overwrite '+str(out))
    with (a.data/(a.dataset+'-index.pkl')).open('rb') as f:I=pickle.load(f)
    with gzip.open(ROOT/'results'/a.dataset/'records.jsonl.gz','rt') as f:rows=[json.loads(x) for x in f]
    with gzip.open(ROOT/'results'/a.dataset/'session-audit.jsonl.gz','rt') as f:audits=[json.loads(x) for x in f]
    with gzip.open(out,'wt') as log:
        for qi,(row,audit) in enumerate(zip(rows,audits)):
            assert row['queryId']==audit['queryId'];times={'scalar':[],'unique':[]}
            with np.load(ROOT/'results'/a.dataset/row['factorFile']) as z:stored=[z['scores'][z['mapping'][t,:len(fs)]] for t,fs in enumerate(row['forms'])]
            for rep in range(3):
                for method in (['scalar','unique'] if (qi+rep)%2 else ['unique','scalar']):
                    t=time.perf_counter();fs,F,meta=factors(I,row['query']) if method=='unique' else I.factors(row['query'],max_tokens=1_000_000);times[method].append(time.perf_counter()-t)
                    for x,y in zip(F,stored):np.testing.assert_array_equal(x,y)
                    assert fs==row['forms'] and not meta['truncated']
            result={'queryId':row['queryId'],'factorSeconds':times,'uniqueFormsScored':len(row['uniqueFormTexts']),'positionForms':sum(len(fs) for fs in row['forms']),'allArchivedFactorsEqual':True,'scenarios':{}}
            for scenario,source in audit['scenarios'].items():
                sequence=[audit['requests'][i] for i in source['requestIndices']];records=[]
                for rep in range(3):
                    names=['full','memo','compiled','exact','fast-compiled','fast-exact'];offset=(qi+rep)%len(names);order=names[offset:]+names[:offset];answers={}
                    for name in order:
                        started=time.perf_counter();selected=np.arange(I.n);status='full_corpus';memo={}
                        if name not in ('full','memo'):
                            fs,F,_=factors(I,row['query']) if name.startswith('fast-') else I.factors(row['query'],max_tokens=1_000_000)
                            selected,_=compiled_pool(F);status='safe_approximation'
                            if name in ('exact','fast-exact'):
                                exact,_=exact_from_pool(F,selected,fs);selected=np.asarray(exact['pool'],dtype=int);status=exact['status']
                            index=I.weights[selected].T.tocsr()
                        outputs=[];prefix5=None
                        for count,request in enumerate(sequence,1):
                            text=request['query']
                            if name=='memo' and text in memo:answer=memo[text]
                            else:
                                z=I.score(text) if name in ('full','memo') else (I.vectorizer.transform([text])@index).toarray()[0]
                                threshold=np.partition(z,-10)[-10];answer=selected[z>=threshold].tolist()
                                if name=='memo':memo[text]=answer
                            outputs.append(answer)
                            if count==5:prefix5=time.perf_counter()-started
                        elapsed=time.perf_counter()-started;answers[name]=outputs
                        records.append({'method':name,'repeat':rep,'prefix5Seconds':prefix5,'total20Seconds':elapsed,'status':status,'poolSize':len(selected),'answerSha256':hashlib.sha256(json.dumps(outputs,separators=(',',':')).encode()).hexdigest(),'order':order})
                    for name,outputs in answers.items():assert outputs==source['expectedTopK'],(row['queryId'],scenario,name)
                result['scenarios'][scenario]={'records':records}
            log.write(json.dumps(result,separators=(',',':'))+'\n');log.flush();print(a.dataset,'factor audit',qi+1,'/16',flush=True)
if __name__=='__main__':main()
