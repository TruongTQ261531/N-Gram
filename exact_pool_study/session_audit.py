"""Supplemental controlled workloads with ordinary exact-query memoization.

Frozen separately after primary experiment began, before these new timings.
Does not alter primary source, selection, results or prospective freeze.
"""
from method import compiled_pool,exact_from_pool,legacy
from pathlib import Path
import argparse,gzip,hashlib,json,pickle,time
import numpy as np
ROOT=Path(__file__).resolve().parent

def requests(forms,ds,qid):
    seed=int(hashlib.sha256(('independent-session-v1|'+ds+'|'+qid).encode()).hexdigest()[:16],16)
    rng=np.random.default_rng(seed);possible=[t for t,f in enumerate(forms) if len(f)>1]
    values=[];seen=set()
    for target_cost in [0]+[1]*5+[2]*14:
        accepted=False
        for attempt in range(10000):
            cost=min(target_cost,len(possible));edits=[]
            if cost:
                for t in rng.choice(possible,size=cost,replace=False):edits.append([int(t),int(rng.integers(1,len(forms[t])))])
            choice=dict(edits);text=' '.join(' '.join(forms[t][choice.get(t,0)]['text'] for t in range(len(forms))).split())
            if text not in seen:seen.add(text);values.append({'query':text,'edits':edits});accepted=True;break
        if not accepted:break
    assert values
    distinct=len(values)
    values=[values[i%len(values)] for i in range(20)]
    return values,distinct

def main():
    p=argparse.ArgumentParser();p.add_argument('--data',type=Path,required=True);p.add_argument('--dataset',choices=['arguana','scidocs'],required=True);a=p.parse_args()
    freeze=json.loads((ROOT/'session_freeze.json').read_text())
    for name,h in freeze['files'].items():assert hashlib.sha256((ROOT.parent/name).read_bytes()).hexdigest()==h,name
    out=ROOT/'results'/a.dataset/'session-audit.jsonl.gz'
    if out.exists():raise RuntimeError('Refusing to overwrite '+str(out))
    with (a.data/(a.dataset+'-index.pkl')).open('rb') as f:I=pickle.load(f)
    with gzip.open(ROOT/'results'/a.dataset/'records.jsonl.gz','rt') as f:rows=[json.loads(x) for x in f]
    with gzip.open(out,'wt') as log:
        for qi,row in enumerate(rows):
            values,distinct=requests(row['forms'],a.dataset,row['queryId'])
            result={'queryId':row['queryId'],'distinctAvailableIn20':distinct,'requests':values,'scenarios':{}}
            for scenario,sequence in [('distinct20',values),('repeat10x2',values[:10]+values[:10])]:
                records=[];expected=None
                for rep in range(3):
                    names=['full','memo','legacy','compiled','exact'];offset=(qi+rep)%len(names);order=names[offset:]+names[:offset];answers={}
                    for name in order:
                        started=time.perf_counter();selected=np.arange(I.n);status='full_corpus';memo={}
                        if name not in ('full','memo'):
                            forms,F,_=I.factors(row['query'],max_tokens=1_000_000)
                            if name=='legacy':selected=legacy.candidate_pools(F,2,10,include_fixed=False)[0]['partitioned'];status='safe_approximation'
                            else:
                                selected,_=compiled_pool(F);status='safe_approximation'
                                if name=='exact':
                                    exact,_=exact_from_pool(F,selected,forms);selected=np.asarray(exact['pool'],dtype=int);status=exact['status']
                            index=I.weights[selected].T.tocsr()
                        results=[];prefix5=None
                        for qnum,request in enumerate(sequence,1):
                            text=request['query']
                            if name=='memo' and text in memo:answer=memo[text]
                            else:
                                scores=I.score(text) if name in ('full','memo') else (I.vectorizer.transform([text])@index).toarray()[0]
                                threshold=np.partition(scores,-10)[-10];answer=selected[scores>=threshold].tolist()
                                if name=='memo':memo[text]=answer
                            results.append(answer)
                            if qnum==5:prefix5=time.perf_counter()-started
                        elapsed=time.perf_counter()-started;answers[name]=results
                        records.append({'method':name,'repeat':rep,'status':status,'prefix5Seconds':prefix5,'total20Seconds':elapsed,'poolSize':len(selected),'answerSha256':hashlib.sha256(json.dumps(results,separators=(',',':')).encode()).hexdigest(),'order':order})
                    for name,outputs in answers.items():assert outputs==answers['full'],(row['queryId'],scenario,name)
                    expected=answers['full']
                result['scenarios'][scenario]={'records':records,'expectedTopK':expected,'requestIndices':list(range(20)) if scenario=='distinct20' else list(range(10))*2}
            log.write(json.dumps(result,separators=(',',':'))+'\n');log.flush();print(a.dataset,'sessions',qi+1,'/16','distinct',distinct,flush=True)
if __name__=='__main__':main()
