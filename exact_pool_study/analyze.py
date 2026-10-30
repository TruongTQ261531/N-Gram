from pathlib import Path
import csv,gzip,json,statistics
ROOT=Path(__file__).resolve().parent
def read(path):
    with gzip.open(path,'rt') as f:return [json.loads(x) for x in f]
def median(x):return statistics.median(x)
def main():
    summaries=[];records=[];session_summaries=[];factor_summaries=[];factor_build=[]
    for ds in ('arguana','scidocs'):
        rows=read(ROOT/'results'/ds/'records.jsonl.gz');audit=read(ROOT/'results'/ds/'session-audit.jsonl.gz');assert [x['queryId'] for x in rows]==[x['queryId'] for x in audit]
        for row in rows:
            exact=row['exactModes']['rank'];a=row['approximations'];r={'dataset':ds,'queryId':row['queryId'],'tokens':len(row['forms']),'legacyPool':len(a['legacyPool']),'exactPool':len(exact['pool']),'exactStatus':exact['status'],'legacyBuildMs':1000*median(a['legacySeconds']),'compiledBuildMs':1000*median(a['compiledSeconds']),'termination':exact.get('termination'),'visitedRankStates':exact['states']}
            for mode,z in row['exactModes'].items():r[mode+'TheoreticalStates']=z.get('theoreticalStates',z['states'])
            records.append(r)
        subset=[x for x in records if x['dataset']==ds]
        summaries.append({'dataset':ds,'queries':len(rows),'completeQueries':sum(not x['metadata']['truncated'] for x in rows),'minTokens':min(len(x['forms']) for x in rows),'maxTokens':max(len(x['forms']) for x in rows),'meanLegacyPool':statistics.mean(x['legacyPool'] for x in subset),'meanExactPool':statistics.mean(x['exactPool'] for x in subset),'exactCases':sum(x['exactStatus']=='exact' for x in subset),'medianLegacyBuildMs':median(x['legacyBuildMs'] for x in subset),'medianCompiledBuildMs':median(x['compiledBuildMs'] for x in subset),'medianCompiledBuildSpeedup':median(x['legacyBuildMs']/x['compiledBuildMs'] for x in subset),'originalTheoreticalStates':sum(x['noneTheoreticalStates'] for x in subset),'scoreTheoreticalStates':sum(x['scoreTheoreticalStates'] for x in subset),'textTheoreticalStates':sum(x['textTheoreticalStates'] for x in subset),'rankTheoreticalStates':sum(x['rankTheoreticalStates'] for x in subset),'rankActuallyVisited':sum(x['visitedRankStates'] for x in subset),'fullCorpusOracleExact':sum(x['fullCorpusOracle']['status']=='exact' for x in rows),'fullCorpusOracleUnknown':sum(x['fullCorpusOracle']['status']!='exact' for x in rows),'maxProcessMiB':max(x['peakProcessMiB'] for x in rows),'primarySessionsWithSingleDescriptor':sum(x.get('sessionRequests',{}).get('distinctDescriptors')==1 for x in rows)})
        for scenario in ('distinct20','repeat10x2'):
            for prefix,key in [(5,'prefix5Seconds'),(20,'total20Seconds')]:
                values={method:[median(z[key] for z in row['scenarios'][scenario]['records'] if z['method']==method) for row in audit] for method in ('full','memo','legacy','compiled','exact')}
                session_summaries.append({'dataset':ds,'scenario':scenario,'requests':prefix,'queries':len(audit),**{method+'MedianMs':1000*median(times) for method,times in values.items()},'exactFasterThanFull':sum(a<b for a,b in zip(values['exact'],values['full'])),'exactFasterThanMemo':sum(a<b for a,b in zip(values['exact'],values['memo'])),'exactFasterThanLegacy':sum(a<b for a,b in zip(values['exact'],values['legacy'])),'compiledFasterThanFull':sum(a<b for a,b in zip(values['compiled'],values['full'])),'medianExactSpeedupVsFull':median(b/a for a,b in zip(values['exact'],values['full'])),'allRequestsDistinctIn20':all(x['distinctAvailableIn20']==20 for x in audit)})
        factors=read(ROOT/'results'/ds/'factor-audit.jsonl.gz');assert [x['queryId'] for x in factors]==[x['queryId'] for x in rows]
        factor_build.append({'dataset':ds,'queries':len(factors),'medianScalarMs':1000*median(median(x['factorSeconds']['scalar']) for x in factors),'medianUniqueMs':1000*median(median(x['factorSeconds']['unique']) for x in factors),'medianFactorSpeedup':median(median(x['factorSeconds']['scalar'])/median(x['factorSeconds']['unique']) for x in factors),'allArchivedFactorsEqual':all(x['allArchivedFactorsEqual'] for x in factors)})
        for scenario in ('distinct20','repeat10x2'):
            for prefix,key in [(5,'prefix5Seconds'),(20,'total20Seconds')]:
                values={name:[median(z[key] for z in row['scenarios'][scenario]['records'] if z['method']==name) for row in factors] for name in ('full','memo','compiled','exact','fast-compiled','fast-exact')}
                factor_summaries.append({'dataset':ds,'scenario':scenario,'requests':prefix,'queries':len(factors),**{name+'MedianMs':1000*median(v) for name,v in values.items()},'fastExactFasterThanFull':sum(a<b for a,b in zip(values['fast-exact'],values['full'])),'fastExactFasterThanMemo':sum(a<b for a,b in zip(values['fast-exact'],values['memo'])),'fastExactFasterThanScalarExact':sum(a<b for a,b in zip(values['fast-exact'],values['exact'])),'fastApproxFasterThanFull':sum(a<b for a,b in zip(values['fast-compiled'],values['full'])),'medianFastExactSpeedupVsFull':median(b/a for a,b in zip(values['fast-exact'],values['full']))})
    out={'summary':summaries,'sessionAudit':session_summaries,'factorConstructionAudit':factor_build,'factorSessionAudit':factor_summaries,'limits':['Same corpora/integer rankers as previous study; new query IDs, not new domains.','Full-corpus brute-force oracle capped; independent projection/original-projected enumeration is separate.','Primary workload may repeat after early saturation; stronger supplemental audit reported separately.','All session timings include initialization, shared warm index load excluded.','Factor audit is a separately frozen engineering optimization, not a new independent confirmation.','Synthetic compact edits and controlled request sequences, not natural user-session evidence.','No global novelty, relevance gain, Q1 readiness or universal speed claim.']}
    (ROOT/'results/analysis.json').write_text(json.dumps(out,indent=2))
    for filename,rows in [('summary.csv',summaries),('per-query.csv',records),('session-summary.csv',session_summaries),('factor-summary.csv',factor_build),('factor-session-summary.csv',factor_summaries)]:
        with (ROOT/'results'/filename).open('w',newline='') as f:w=csv.DictWriter(f,fieldnames=rows[0].keys());w.writeheader();w.writerows(rows)
    print(json.dumps(out,indent=2))
if __name__=='__main__':main()
