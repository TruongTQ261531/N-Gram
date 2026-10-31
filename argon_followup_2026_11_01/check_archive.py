"""Archive-level checks; actual model/corpus replay remains separately documented."""
import gzip,hashlib,itertools,json,math
from pathlib import Path
import numpy as np
from argon_followup_2026_11_01.analyze import load,analyze
from argon_followup_2026_11_01.schedule_certificate import certificate

ROOT=Path(__file__).resolve().parent


def check_graph(n,result):
    edges={tuple(sorted(e)) for e in result['conflictEdges']}
    groups=result['coloring']['groups']
    assert sorted(i for g in groups for i in g)==list(range(n))
    assert len(groups)==result['coloring']['colors']
    assert all(tuple(sorted((i,j))) in edges for g in groups for i,j in itertools.combinations(g,2))
    clique=result['maxClique']['clique']
    assert len(clique)==len(set(clique))==result['maxClique']['size']
    assert all(tuple(sorted((i,j))) not in edges for i,j in itertools.combinations(clique,2))
    assert result['maxClique']['size']<=len(groups)
    assert result['pairwiseUpper']==(result['maxClique']['size'] if result['maxClique']['optimal'] else len(groups))


def qrel(top,grades,ids):
    rel=[grades.get(ids[d],0) for d in top[:10]];ideal=sorted(grades.values(),reverse=True)[:10]
    dcg=sum((2**r-1)/math.log2(i+2) for i,r in enumerate(rel));idcg=sum((2**r-1)/math.log2(i+2) for i,r in enumerate(ideal))
    return {'nDCG10':dcg/idcg if idcg else 0.,'hasPositiveQrel':bool(idcg),'judgedTop10':sum(ids[d] in grades for d in top[:10]),'positiveTop10':sum(r>=1 for r in rel)}


def ranked(logits,documents,ids):
    assert len(logits)==len(documents) and all(math.isfinite(x) for x in logits)
    return [d for d,_ in sorted(zip(documents,logits),key=lambda item:(-item[1],ids[item[0]]))[:10]]


def check_qrel(observed,top,grades,ids):
    expected=qrel(top,grades,ids)
    assert abs(observed['nDCG10']-expected['nDCG10'])<1e-12
    assert all(observed[k]==expected[k] for k in expected if k!='nDCG10')


def main():
    with gzip.open(ROOT.parent/'decision_audit_2026_10_31/results/decisions.json.gz','rt') as f:
        robust=[r for r in json.load(f)['rows'] if r['label']=='ROBUST']
    graphs=load(ROOT/'results/graphs.jsonl.gz')
    assert {(r['dataset'],r['queryId']) for r in graphs}=={(r['dataset'],r['queryId']) for r in robust}
    for r in graphs:
        n=r['candidateCount']
        certificate(r['greedy']['groups'],r['greedy']['checks'])
        if 'sameGraph' in r:check_graph(n,r['sameGraph'])
        if 'fullGraph' in r:
            check_graph(n,r['fullGraph'])
            if r['allPairsChecked']:assert len(r['fullChecks'])==n*(n-1)//2
            assert all(not c['incompatible'] or c['upper']<0 for c in r['fullChecks'])
    with gzip.open(ROOT.parent/'lazy_cert_study/results/confirmation.jsonl.gz','rt') as f:old=[json.loads(s) for s in f]
    lookup={r['queryId']:r for r in old};lex=load(ROOT/'results/lexical-full-trace.jsonl.gz')
    assert [r['queryId'] for r in lex]==[r['queryId'] for r in old]
    for r in lex:
        assert all(set(s['lexicalTopIds'])<=set(lookup[r['queryId']]['oracleUnion']) for s in r['states'])
        assert set(d for s in r['states'] for d in s['lexicalTopIds'])==set(lookup[r['queryId']]['oracleUnion'])
        assert all(sum(a!=0 for a in s['state'])<=2 for s in r['states'])
        assert len({(s['requestSha256'],d) for s in r['states'] for d in s['lexicalTopIds']})==r['uniqueNeuralPairsFull']
        assert r['uniqueNeuralPairsFull']==r['uniqueNeuralPairsGivenUnion']
    label=load_json_gzip(ROOT/'results/judgments.json.gz');ids=label['documentIds']
    assert len(ids)==len(set(ids))==42994 and ids==sorted(ids)
    source=json.loads((ROOT.parent/'lazy_cert_study/sources.json').read_text())
    assert label['sourceLabelSha256']==next(r['sha256'] for r in source['files'] if r['path']=='dataset/label.csv')
    d=ROOT/'results/neural-fp32-bucket';meta=json.loads((d/'metadata.json').read_text())
    assert meta['status']=='COMPLETE' and meta['rawQueries']==meta['traceQueries']==128 and meta['costQueries']==16
    for phase,code in [('neural-fp32-bucket-phase1','neural_frozen_bucket_phase1.py'),('neural-fp32-bucket-phase2','neural.py')]:
        pm=json.loads((ROOT/'results'/phase/'metadata.json').read_text())
        assert pm['codeSha256']==hashlib.sha256((ROOT/code).read_bytes()).hexdigest()
    receipt=json.loads((ROOT/'results/neural-fp32-bucket-phase1/completion.json').read_text())
    prefix=set(receipt['completedQueryIds'])
    for name,sha in meta['fileHashes'].items():assert hashlib.sha256((d/name).read_bytes()).hexdigest()==sha
    for filename in ['raw','cost','trace']:
        rows=load(d/(filename+'.jsonl.gz'))
        for r in rows:
            gold=label['grades'].get(r['queryId'],{})
            assert r['sourcePhase']==(1 if r['queryId'] in prefix else 2)
            if filename=='raw':
                assert r['union']==lookup[r['queryId']]['oracleUnion']
                assert r['top10']==ranked(r['logits'],r['union'],ids)
                check_qrel(r['qrel'],r['top10'],gold,ids)
            elif filename=='cost':
                assert set(r['union'])<=set(r['pool'])
                for s in r['runs']:
                    docs=r['union'] if s['method']=='U' else r['pool']
                    assert s['top10']==ranked(s['logits'],docs,ids)
                    check_qrel(s['qrel'],s['top10'],gold,ids)
            else:
                assert len(r['requests'])==20
                assert r['neuralPairsFullControl']==r['neuralPairsGivenUnion']
                assert sum(s['newPairs'] for s in r['requests'])==r['neuralPairsFullControl']
                memo={}
                for s,original in zip(r['requests'],lookup[r['queryId']]['requests']):
                    assert s['state']==original['state'] and s['textSha256']==hashlib.sha256(original['text'].encode()).hexdigest()
                    keys=[(s['textSha256'],i) for i in s['lexicalTopIds']]
                    assert s['newPairs']==sum(k not in memo for k in keys)
                    for k,z in zip(keys,s['logits']):
                        if k in memo:assert memo[k]==z
                        memo[k]=z
                    assert s['neuralTop10']==ranked(s['logits'],s['lexicalTopIds'],ids)
                    check_qrel(s['qrel'],s['neuralTop10'],gold,ids)
    fixed=load(ROOT/'results/fixed-depth.jsonl.gz')
    assert [r['queryId'] for r in fixed]==[r['queryId'] for r in old]
    for r in fixed:
        for name,run in r['runs'].items():
            assert run['top10']==ranked(run['logits'],run['documents'],ids)
            check_qrel(run['qrel'],run['top10'],label['grades'].get(r['queryId'],{}),ids)
    multi=json.loads((ROOT/'results/multiword.json').read_text())
    selection=json.loads((ROOT/'results/multiword-selection.json').read_text())
    for name,panel in multi['panels'].items():
        assert [r['hash'] for r in panel['rows']]==[r['hash'] for r in selection['panels'][name]]
        for b in [1,2]:assert panel['metrics']['b'+str(b)]==sum(r['status']=='covered' and r['minimumCostWithinBudget']<=b for r in panel['rows'])
    gtc=json.loads((ROOT/'results/gtc.json').read_text());selection=json.loads((ROOT/'results/gtc-selection.json').read_text())
    assert gtc['source']['matchesCdxDigest'] is True and gtc['source']==json.loads((ROOT/'GTC_SOURCE.json').read_text())
    assert [r['hash'] for r in gtc['rows']]==[r['hash'] for r in selection['rows']]
    assert len(gtc['rows'])==len({r['hash'] for r in gtc['rows']})==200
    for b in [1,2]:assert gtc['metrics']['b'+str(b)]==sum(r['status']=='covered' and r['minimumCostWithinBudget']<=b for r in gtc['rows'])
    assert analyze()==json.loads((ROOT/'results/analysis.json').read_text())
    print('PASS:266graphs,7complete refinements,128/6684 lexical inputs,128neural queries,16cost blocks,2560requests,600multiword pairs')


def load_json_gzip(path):
    with gzip.open(path,'rt') as f:return json.load(f)


if __name__=='__main__':main()
