"""Single deterministic reanalysis; queries, not timing repeats, are the units."""
import csv,gzip,json,math,statistics
from pathlib import Path
import numpy as np
from argon_followup_2026_11_01.schedule_certificate import certificate

ROOT=Path(__file__).resolve().parent


def load(path):
    with gzip.open(path,'rt') as f:return [json.loads(s) for s in f]


def first_fit(n,edges):
    known={tuple(sorted(e)) for e in edges};groups=[]
    for j in range(n):
        for g in groups:
            if all(tuple(sorted((j,k))) in known for k in g):g.append(j);break
        else:groups.append([j])
    return groups


def analyze():
    rows=load(ROOT/'results/graphs.jsonl.gz');hard=[r for r in rows if 'fullGraph' in r]
    graph={'verifiedRobustCases':len(rows),'originalCertified':sum(r['originalBounds']['discrete']<=10 for r in rows),
        'samePartialGraphCertified':sum(r['sameGraphRankUpper']<=10 for r in rows),
        'sameGraphExactColoringProven':sum(r.get('sameGraph',{}).get('coloring',{}).get('optimal',False) for r in rows),
        'hardCases':[]}
    graph['sameGraphGreedyAlreadyOptimal']=sum(r.get('sameGraph',{}).get('coloring',{}).get('optimal',False) and
        r['sameGraph']['coloring']['colors']==len(r['greedy']['groups']) for r in rows)
    graph['firstFitScheduleCertificates']=[{'dataset':r['dataset'],'queryId':r['queryId'],**certificate(r['greedy']['groups'],r['greedy']['checks'])} for r in rows]
    for r in hard:
        f=r['fullGraph'];ff=first_fit(r['candidateCount'],f['conflictEdges'])
        graph['hardCases'].append({'dataset':r['dataset'],'queryId':r['queryId'],'candidates':r['candidateCount'],
            'pairChecks':len(r['fullChecks']),'allPairsChecked':r['allPairsChecked'],'pairResourceUnknown':sum(x['method']=='resource_cap' for x in r['fullChecks']),
            'originalRank':r['originalBounds']['discrete'],'partialRefinedRank':r['sameGraphRankUpper'],
            'fullFirstFitRank':len(ff)+1,'fullDSATURRank':f['dsaturGreedyColors']+1,'fullOptimalCoverRank':f['coloring']['colors']+1,
            'maxCliqueUpperRank':f['pairwiseUpper']+1,'maxCliqueOptimal':f['maxClique']['optimal'],'coloringOptimal':f['coloring']['optimal'],
            'pairConstructionSeconds':r['fullPairConstructionSeconds'],'graphSolveSeconds':f['coloring']['seconds']+f['maxClique']['seconds']})
    graph['afterCompletePairsAndDSATUR']=graph['originalCertified']+sum(r['fullDSATURRank']<=10 for r in graph['hardCases'])
    multi=json.loads((ROOT/'results/multiword.json').read_text())
    multiword={p:d['metrics'] for p,d in multi['panels'].items()}
    lexical=load(ROOT/'results/lexical-full-trace.jsonl.gz')
    cascade={'queries':len(lexical),'states':sum(len(r['states']) for r in lexical),
        'uniquePairsPerQuerySummed':sum(r['uniqueNeuralPairsFull'] for r in lexical),
        'identicalInputSets':all(r['uniqueNeuralPairsFull']==r['uniqueNeuralPairsGivenUnion'] for r in lexical)}
    with gzip.open(ROOT.parent/'lazy_cert_study/results/confirmation.jsonl.gz','rt') as f:old={r['queryId']:r for r in map(json.loads,f)}
    cascade['scoreAllUnionPerDistinctStatePairs']=sum(len({s['requestSha256'] for s in r['states']})*len(old[r['queryId']]['oracleUnion']) for r in lexical)
    cascade['scoreAllUnionPairCountRatio']=cascade['scoreAllUnionPerDistinctStatePairs']/cascade['uniquePairsPerQuerySummed']
    result={'retrospective':True,'graphs':graph,'multiword':multiword,'fullDomainCascadeInputs':cascade}
    gtc=json.loads((ROOT/'results/gtc.json').read_text())
    result['gtc']={'metrics':gtc['metrics'],'counts':gtc['counts'],'source':gtc['source']}
    d=ROOT/'results/neural-fp32-bucket'
    meta=json.loads((d/'metadata.json').read_text());raw=load(d/'raw.jsonl.gz');cost=load(d/'cost.jsonl.gz');trace=load(d/'trace.jsonl.gz')
    neural={'backend':meta['backend'],'status':meta.get('status'),'rawQueries':len(raw),'costQueries':len(cost),'sessionQueries':len(trace),
        'sessionRequests':sum(len(r['requests']) for r in trace),'rawUnionPairs':sum(len(r['union']) for r in raw),
        'meanRawUnionNDCG10':statistics.mean(r['qrel']['nDCG10'] for r in raw),
        'judgedRelevantInsideU':sum(r['judgedRelevantInsideU'] for r in raw),'judgedRelevantTotal':sum(r['judgedRelevantTotal'] for r in raw),
        'judgedExactInsideU':sum(r['judgedExactInsideU'] for r in raw),'judgedExactTotal':sum(r['judgedExactTotal'] for r in raw),
        'macroJudgedRelevantRecallU':statistics.mean(r['judgedRelevantInsideU']/r['judgedRelevantTotal'] for r in raw if r['judgedRelevantTotal']),
        'sessionNeuralPairsBothControls':sum(r['neuralPairsFullControl'] for r in trace),
        'meanRawLexicalTop10CascadeNDCG10':statistics.mean(r['requests'][0]['qrel']['nDCG10'] for r in trace),
        'variantQrelsAreOriginalQueryProxy':True,
        'rawPairsAtTokenLimitUpperBound':sum(r['measure']['atTokenLimit'] for r in raw),
        'sessionNeuralSeconds':sum(r['neuralSecondsSharedExactTrace'] for r in trace),'costPanel':[]}
    speed=[];recall=[]
    for r in cost:
        by={(x['repeat'],x['method']):x for x in r['runs']}
        times={m:by[(0,m)]['seconds'] for m in ['U','P']}
        ptop=by[(0,'P')]['top10'];contain=len(set(ptop)&set(r['union']))/len(ptop)
        ratio=times['P']/times['U'];speed.append(ratio);recall.append(contain)
        neural['costPanel'].append({'queryId':r['queryId'],'U':len(r['union']),'P':len(r['pool']),
            'primaryUSeconds':times['U'],'primaryPSeconds':times['P'],'ratioPoverU':ratio,
            'top10PContainmentInU':contain,'outsideUTop10P':sorted(set(ptop)-set(r['union'])),
            'maxOverlapLogitDifference':max(r['maxOverlapScoreDifference']),
            'U_NDCG10':by[(0,'U')]['qrel']['nDCG10'],'P_NDCG10':by[(0,'P')]['qrel']['nDCG10']})
    neural.update({'geometricRawCandidateCostRatio':math.exp(statistics.mean(math.log(s) for s in speed)),
        'meanTop10PContainmentInU':statistics.mean(recall),'costQueriesWithOutsideU':sum(s<1 for s in recall),
        'costTotalPpairsPerRepeat':sum(len(r['pool']) for r in cost),
        'maxCrossPoolOverlapLogitDifference':max(max(r['maxOverlapScoreDifference']) for r in cost)})
    neural['costPanelMeanU_NDCG10']=statistics.mean(r['U_NDCG10'] for r in neural['costPanel'])
    neural['costPanelMeanP_NDCG10']=statistics.mean(r['P_NDCG10'] for r in neural['costPanel'])
    refs=load(ROOT/'results/fp32-reference.jsonl.gz');refmap={r['queryId']:r for r in refs}
    diffs=[];ordered=set_equal=0
    for r in raw:
        ref=refmap[r['queryId']];assert ref['union']==r['union']
        diffs.extend(np.abs(np.array(ref['logits'])-np.array(r['logits'])).tolist())
        ordered+=ref['top10']==r['top10'];set_equal+=set(ref['top10'])==set(r['top10'])
    neural['fp32Reference']={'queries':len(refs),'pairs':len(diffs),'maxAbsoluteLogitDifference':max(diffs),'meanAbsoluteLogitDifference':statistics.mean(diffs),
        'orderedTop10Equal':ordered,'top10SetEqual':set_equal,'reusedPartialRows':sum(r['reusedCompletedPartial'] for r in refs)}
    result['neural']=neural
    fixed=load(ROOT/'results/fixed-depth.jsonl.gz')
    controls={'queries':len(fixed),'primaryScope':'Actual raw-query reranking; static-pool reuse reported separately','costPanel':[]}
    for name in ['T50','T100']:
        controls[name]={'meanNDCG10':statistics.mean(r['runs'][name]['qrel']['nDCG10'] for r in fixed),
            'medianCandidates':statistics.median(len(r['runs'][name]['documents']) for r in fixed),
            'totalNeuralPairs':sum(len(r['runs'][name]['documents']) for r in fixed),
            'staticPoolContainsAllVariantsQueries':sum(r['staticReuseDiagnostic'][name]['allStatesContained'] for r in fixed),
            'meanStaticWorstStateRecall':statistics.mean(r['staticReuseDiagnostic'][name]['worstStateRecall'] for r in fixed)}
    for r in fixed:
        if not r['costPanel']:continue
        runs=r['runs'];u=runs['U']['measure']['seconds']
        controls['costPanel'].append({'queryId':r['queryId'],'USeconds':u,'T50Seconds':runs['T50']['measure']['seconds'],
            'T100Seconds':runs['T100']['measure']['seconds'],'T50overU':runs['T50']['measure']['seconds']/u,
            'T100overU':runs['T100']['measure']['seconds']/u})
    for name in ['T50','T100']:
        controls[name]['geometricFreshCostRatioOverU']=math.exp(statistics.mean(math.log(r[name+'overU']) for r in controls['costPanel']))
    result['fixedDepthControls']=controls
    return result


if __name__=='__main__':
    result=analyze();(ROOT/'results/analysis.json').write_text(json.dumps(result,indent=2)+'\n')
    for name,rows in [('graph-hard',result['graphs']['hardCases']),('neural-cost',result['neural']['costPanel'])]:
        with (ROOT/'results'/(name+'.csv')).open('w',newline='') as f:
            writer=csv.DictWriter(f,fieldnames=list(rows[0]),lineterminator='\n');writer.writeheader();writer.writerows(rows)
    print(json.dumps(result,indent=2))
