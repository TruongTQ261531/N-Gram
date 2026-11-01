"""Post-run oracle joins and complete-denominator matched-control summaries."""
import csv,gzip,hashlib,json
from pathlib import Path
from collections import Counter
import numpy as np
from utk_full_domain_2026_11_01.run import ROOT,METHODS,digest
from utk_full_domain_2026_11_01.archive import execution_bytes,execution_rows


def load(path):
    with gzip.open(path,'rt') as f:return [json.loads(s) for s in f]


def analyze():
    freeze=json.loads((ROOT/'FREEZE.json').read_text())
    for name,sha in freeze['sourceHashes'].items():assert digest(ROOT.parent/name)==sha,name
    meta=json.loads((ROOT/'results/metadata.json').read_text());replay=json.loads((ROOT/'results/replay.json').read_text())
    assert meta['status']==replay['status']=='COMPLETE'
    assert meta['oldOutcomesReadByRunner'] is False and meta['numericalThreads']==1
    assert meta['freezeSha256']==digest(ROOT/'FREEZE.json')
    assert meta['recordsSha256']==hashlib.sha256(execution_bytes()).hexdigest()
    assert replay['oracleSha256']==digest(ROOT/'results/oracle.jsonl.gz')
    assert replay['privateIndexSha256']==freeze['privateIndexSha256']
    rows=[];cap_reasons={m:Counter() for m in ['rsa_fd','jaa_fd']};oracle=load(ROOT/'results/oracle.jsonl.gz')
    assert [r['queryId'] for r in oracle]==freeze['queryIds']
    truths={r['queryId']:r for r in oracle};old=load(ROOT.parent/'lazy_cert_study/results/confirmation.jsonl.gz')
    old={r['queryId']:r['oracleUnion'] for r in old}
    old_differences=[r['queryId'] for r in oracle if r['union']!=old[r['queryId']]]
    assert len(oracle)==128 and not old_differences
    for row in execution_rows():
        truth=truths[row['queryId']];assert len(row['runs'])==12
        assert {(r['method'],r['repeat']) for r in row['runs']}=={(m,i) for m in METHODS for i in range(3)}
        for run in row['runs']:
            assert run['seconds']>0 and np.isfinite(run['seconds'])
            if run['status']=='exact':assert run['union']==truth['union'],(row['queryId'],run['method'])
            elif run['status']=='resource_unknown':assert set(truth['union'])<=set(run['union'])
            else:assert run['status']=='error'
        for method in ['rsa_fd','jaa_fd']:
            detail=row['receipts'].get(method,{})
            if detail.get('status')=='resource_unknown':cap_reasons[method][detail.get('proof',{}).get('reason','unspecified')]+=1
            if detail.get('status')!='exact' or 'proof' not in detail:continue
            proof=detail['proof'];mapping=proof['poolMapping'];kept=proof['survivors'];scores=proof['survivorFactors']
            assert len(mapping)==len(set(mapping)) and proof['states']==[r['state'] for r in truth['states']]
            assert set(mapping[j] for j in kept)<=set(mapping)
            rejected=proof['filter']['rejected'];kept_set=set(kept)
            assert sorted(kept+[r['document'] for r in rejected])==list(range(len(mapping)))
            for rejected_row in rejected:
                ds=rejected_row['dominators'];assert len(ds)==len(set(ds))==10
                assert all(d in kept_set for d in ds) and all(g>0 for g in rejected_row['minimumMargins'])
            F=[np.asarray(f,dtype=np.int64) for f in scores]
            for state,original in zip(proof['states'],truth['states']):
                values=sum(f[a] for f,a in zip(F,state))
                cut=np.partition(values,-10)[-10]
                assert {mapping[kept[j]] for j in np.flatnonzero(values>=cut)}==set(original['top'])
            if method=='jaa_fd':
                covered=[]
                for cell in proof['cells']:
                    top={mapping[kept[j]] for j in cell['top']}
                    for s in cell['states']:
                        assert top==set(truth['states'][s]['top']);covered.append(s)
                assert sorted(covered)==list(range(len(truth['states'])))
            else:
                for j,s in proof['witnesses'].items():assert mapping[kept[int(j)]] in truth['states'][s]['top']
        rows.append({key:value for key,value in row.items() if key!='receipts'})
    assert len(rows)==128 and [r['queryId'] for r in rows]==freeze['queryIds']
    medians={m:[] for m in METHODS};summary={}
    for method in METHODS:
        complete=[];runs=[];unknown=[]
        for row in rows:
            selected=[r for r in row['runs'] if r['method']==method];runs.extend(selected)
            medians[method].append(float(np.median([r['seconds'] for r in selected])))
            if all(r['status']=='exact' for r in selected):complete.append(row['queryId'])
            else:unknown.append(row['queryId'])
        values=np.asarray(medians[method])
        summary[method]={'queries':128,'allThreeRepeatsExact':len(complete),'incompleteQueryIds':unknown,
            'runStatuses':dict(sorted(Counter(r['status'] for r in runs).items())),
            'medianSeconds':float(np.median(values)),'p95Seconds':float(np.quantile(values,.95)),
            'maxSeconds':float(values.max()),'mismatchedExactRuns':0,
            'terminations':dict(sorted(Counter(str(r.get('termination')) for r in runs).items()))}
        # Cap statuses are stored for every repeat; full proof reasons are first-repeat receipts.
        if method in ['rsa_fd','jaa_fd']:
            summary[method]['firstRepeatCapReasons']=dict(sorted(cap_reasons[method].items()))
    base=np.asarray(medians['screen_batch']);rng=np.random.default_rng(20261101)
    for method in METHODS:
        paired=[i for i,r in enumerate(rows) if all(x['status']=='exact' for x in r['runs'] if x['method'] in ['screen_batch',method])]
        if not paired:continue
        values=np.asarray(medians[method])[paired];reference=base[paired];logs=np.log(values/reference)
        boots=np.exp(logs[rng.integers(0,len(logs),size=(2000,len(logs)))].mean(axis=1))
        summary[method]['costRelativeToScreenBatch']={'queries':len(paired),'geometric':float(np.exp(logs.mean())),
            'bootstrap95':np.quantile(boots,[.025,.975]).tolist(),'slowerQueries':int(np.sum(values>reference)),
            'fasterQueries':int(np.sum(values<reference)),'scope':'Descriptive retrospective, instrumented finite implementations'}
    return {'status':'COMPLETE','retrospective':True,'queries':128,'corpus':42994,
            'allAdmissibleStates':sum(len(r['states']) for r in oracle),'methods':summary,
            'originalOracleDifferences':old_differences,'originalCppRuntimeReproduction':False,
            'scope':'Full finite-channel matched controls; no convex-domain or global-SOTA claim'},rows,medians


if __name__=='__main__':
    result,rows,medians=analyze()
    (ROOT/'results/analysis.json').write_text(json.dumps(result,indent=2)+'\n')
    with (ROOT/'results/per_query.csv').open('w',newline='') as f:
        writer=csv.writer(f);writer.writerow(['queryId']+METHODS)
        for i,r in enumerate(rows):writer.writerow([r['queryId']]+[medians[m][i] for m in METHODS])
    print(json.dumps(result,indent=2))
