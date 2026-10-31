"""Combine disjoint completed query blocks, preserving all original phase files."""
import gzip,hashlib,json
from pathlib import Path

ROOT=Path(__file__).resolve().parent


def read(path):
    with gzip.open(path,'rt') as f:return [json.loads(s) for s in f]


def main():
    a=ROOT/'results/neural-fp32-bucket-phase1';b=ROOT/'results/neural-fp32-bucket-phase2';out=ROOT/'results/neural-fp32-bucket'
    out.mkdir(exist_ok=False)
    receipt=json.loads((a/'completion.json').read_text());complete=set(receipt['completedQueryIds'])
    meta1=json.loads((a/'metadata.json').read_text());meta2=json.loads((b/'metadata.json').read_text())
    assert meta2['status']=='COMPLETE'
    for key in ['backend','onnxSource','scorerHash','maxLength','batchSize','threads','padding','costPanelIds','cpu','device','dtype']:
        assert meta1[key]==meta2[key],key
    old=read(ROOT.parent/'lazy_cert_study/results/confirmation.jsonl.gz');order=[r['queryId'] for r in old]
    counts={}
    for name in ['raw','cost','trace']:
        first=[dict(r,sourcePhase=1) for r in read(a/(name+'.jsonl.gz')) if r['queryId'] in complete]
        second=[dict(r,sourcePhase=2) for r in read(b/(name+'.jsonl.gz'))]
        assert not ({r['queryId'] for r in first}&{r['queryId'] for r in second})
        by_id={r['queryId']:r for r in first+second}
        expected=set(meta2['costPanelIds']) if name=='cost' else set(order)
        assert set(by_id)==expected,(name,len(by_id))
        with gzip.open(out/(name+'.jsonl.gz'),'xt') as f:
            for qid in order:
                if qid in by_id:f.write(json.dumps(by_id[qid],separators=(',',':'))+'\n')
        counts[name]=len(by_id)
    metadata={**meta2,'status':'COMPLETE','rawQueries':counts['raw'],'costQueries':counts['cost'],'traceQueries':counts['trace'],
              'plannedIds':order,'phaseProvenance':['neural-fp32-bucket-phase1','neural-fp32-bucket-phase2'],
              'primaryCostRule':'repeat0 on all16queries; extra early repeats are supplementary, not averaged selectively',
              'phaseMetadataHashes':{p.name:hashlib.sha256((p/'metadata.json').read_bytes()).hexdigest() for p in [a,b]},
              'fileHashes':{n:hashlib.sha256((out/n).read_bytes()).hexdigest() for n in ['raw.jsonl.gz','cost.jsonl.gz','trace.jsonl.gz']}}
    metadata.pop('wallSeconds',None) # a phase runtime is not whole-study or end-to-end latency
    (out/'metadata.json').write_text(json.dumps(metadata,indent=2)+'\n')
    print('Merged disjoint completed FP32 blocks',counts)


if __name__=='__main__':main()
