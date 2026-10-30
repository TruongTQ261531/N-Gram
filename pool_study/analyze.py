"""Descriptive prespecified outcomes; written after freeze, no inferential claims."""
from pathlib import Path
import csv,gzip,json,statistics
ROOT=Path(__file__).resolve().parent

def main():
    summaries=[];per_query=[];counts={}
    for ds in ('arguana','scidocs'):
        with gzip.open(ROOT/'results'/ds/'records.jsonl.gz','rt') as f:rows=[json.loads(x) for x in f]
        expected=json.loads((ROOT/'selection.json').read_text())[ds]['queryIds']
        assert [r['queryId'] for r in rows]==expected
        counts[ds]={'queries':len(rows),'documents':json.loads((ROOT/'results'/ds/'environment.json').read_text())['documents'],
                    'uniqueMaxBudgetStates':sum(next(c['states'] for c in row['cases'] if c['budget']==2) for row in rows),
                    'budgetStateChecks':sum(sum(next(c['states'] for c in row['cases'] if c['budget']==b) for b in (1,2)) for row in rows),
                    'truncatedQueries':sum(row['metadata']['truncated'] for row in rows),
                    'maximumSecondsPerQuery':max(row['seconds'] for row in rows),'peakProcessMiB':max(row['peakProcessMiB'] for row in rows)}
        for budget in (1,2):
            for k in (5,10):
                cases=[next(x for x in row['cases'] if x['budget']==budget and x['k']==k) for row in rows]
                means={name:statistics.mean(len(x['pools'][name]) for x in cases) for name in cases[0]['pools']}
                gold=statistics.mean(len(x['oracleUnion']) for x in cases)
                breaks=[x['breakEvenEdits'] for x in cases if x['breakEvenEdits'] is not None]
                summaries.append({'dataset':ds,'budget':budget,'k':k,'queries':len(cases),**{'mean_'+name:value for name,value in means.items()},
                    'mean_exactUnion':gold,'relativeReductionVsCoupled':1-means['partitioned']/means['coupled'],
                    'relativeReductionVsFixed':1-means['partitioned']/means['fixedPartition'],
                    'improvedVsCoupled':sum(len(x['pools']['partitioned'])<len(x['pools']['coupled']) for x in cases),
                    'betterThanFixed':sum(len(x['pools']['partitioned'])<len(x['pools']['fixedPartition']) for x in cases),
                    'worseThanFixed':sum(len(x['pools']['partitioned'])>len(x['pools']['fixedPartition']) for x in cases),
                    'equalExactUnion':sum(len(x['pools']['partitioned'])==len(x['oracleUnion']) for x in cases),
                    'medianInitializationMs':1000*statistics.median(x['initialSeconds'] for x in cases),
                    'medianFullPerEditMs':1000*statistics.median(statistics.median(x['fullSparsePerEditSeconds']) for x in cases),
                    'medianCachedPerEditMs':1000*statistics.median(statistics.median(x['poolSparsePerEditSeconds']) for x in cases),
                    'medianProjectedBreakEvenEdits':statistics.median(breaks) if breaks else None,
                    'noPerEditSpeedup':sum(x['breakEvenEdits'] is None for x in cases),
                    'projectedBreakEvenWithinMeasuredEdits':sum(x['breakEvenEdits'] is not None and x['breakEvenEdits']<=x['measuredEdits'] for x in cases)})
                for row,case in zip(rows,cases):
                    per_query.append({'dataset':ds,'queryId':row['queryId'],'budget':budget,'k':k,'states':case['states'],
                        **{name:len(value) for name,value in case['pools'].items()},'oracle':len(case['oracleUnion']),
                        'initialSeconds':case['initialSeconds'],'projectedBreakEvenEdits':case['breakEvenEdits']})
    report={'status':'complete descriptive results; correctness separately verified','counts':counts,'summary':summaries,
            'limits':['Real inherited corpora with synthetic compact edits, not natural typo logs.','All first16-token truncations retained and disclosed.','Repeated B/k records are dependent; no IID p-values.','Break-even is projected from separately measured initialization and per-edit components, not an observed user session.','No comparison to the original UTK RSA/JAA implementation or production retrieval infrastructure.','No global novelty, relevance improvement or Q1 acceptance claim.']}
    (ROOT/'results/analysis.json').write_text(json.dumps(report,indent=2))
    for filename,records in [('summary.csv',summaries),('per-query.csv',per_query)]:
        with (ROOT/'results'/filename).open('w',newline='') as f:
            w=csv.DictWriter(f,fieldnames=records[0].keys());w.writeheader();w.writerows(records)
    print(json.dumps(report,indent=2))

if __name__=='__main__':main()
