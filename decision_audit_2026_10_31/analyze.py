"""Finite-benchmark decision completeness and retrospective budget diagnostics."""
from pathlib import Path
import argparse,csv,gzip,hashlib,json
import numpy as np

ROOT=Path(__file__).resolve().parent

def records(path):
    with gzip.open(path,'rt') as f:return [json.loads(line) for line in f]

def main():
    p=argparse.ArgumentParser();p.add_argument('--runs',type=Path,required=True)
    p.add_argument('--decisions',type=Path,required=True);p.add_argument('--wide-runs',type=Path,required=True)
    p.add_argument('--boundary',type=Path,default=ROOT/'results/boundary.json')
    p.add_argument('--output',type=Path,required=True)
    args=p.parse_args()
    with gzip.open(args.decisions,'rt') as f:decision=json.load(f)
    assert decision['status']=='COMPLETE' and decision['queries']==970
    truth={(r['dataset'],r['queryId']):r['label'] for r in decision['rows']}
    assert len(truth)==970
    datasets={};totals={'queries':0,'robust':0,'nonrobust':0,'unknown':0,'lp':0,'discrete':0,'milp':0}
    for ds in ['scifact','nfcorpus','fiqa']:
        rows=[r for r in decision['rows'] if r['dataset']==ds]
        count={'queries':len(rows),'robust':sum(r['label']=='ROBUST' for r in rows),
            'nonrobust':sum(r['label']=='NONROBUST' for r in rows),'unknown':sum(r['label']=='UNKNOWN' for r in rows)}
        for name,key in [('lp','best_lp_enum'),('discrete','discrete'),('milp','milp_enum')]:
            positive=[r for r in rows if r['originalBounds'][key]<=10]
            assert all(r['label']=='ROBUST' for r in positive)
            count[name]=len(positive)
        count['discreteFractionOfVerifiedRobust']=count['discrete']/count['robust']
        count['lpFractionOfVerifiedRobust']=count['lp']/count['robust']
        gap=count['robust']-count['lp'];count['trueGapClosedByDiscrete']=(count['discrete']-count['lp'])/gap
        for key in totals:totals[key]+=count[key]
        datasets[ds]=count
    totals['discreteFractionOfVerifiedRobust']=totals['discrete']/totals['robust']
    totals['lpFractionOfVerifiedRobust']=totals['lp']/totals['robust']
    totals['trueGapClosedByDiscrete']=(totals['discrete']-totals['lp'])/(totals['robust']-totals['lp'])
    scope=json.loads((ROOT/'BUDGET_FREEZE.json').read_text());budget={};csvrows=[]
    for ds,ids in scope['timingPanelIds'].items():
        path=args.runs/(ds+'.jsonl.gz');meta=path.with_name(path.name+'.metadata.json')
        if not meta.exists():budget[ds]={'status':'NOT_COMPLETE'};continue
        metadata=json.loads(meta.read_text());assert metadata['status']=='COMPLETE'
        assert metadata['rowsSha256']==hashlib.sha256(path.read_bytes()).hexdigest()
        rows=records(path);assert [r['queryId'] for r in rows]==ids
        summary={}
        for name in metadata['profiles']:
            selected=[next(x for x in r['runs'] if x['profile']==name) for r in rows]
            values=np.array([r['seconds'] for r in selected]);certified=[row['queryId'] for row,run in zip(rows,selected) if run['rankUpper']<=10]
            wrong=[qid for qid in certified if truth[(ds,qid)]!='ROBUST']
            statuses={};dual=0
            for run in selected:
                d=run['detail'];m=d.get('milp',{})
                key='zero_reference' if d.get('zeroReference') else m.get('skipped') or ('solver_'+str(m.get('status')) if m else 'discrete_work_profile')
                statuses[key]=statuses.get(key,0)+1;dual+=m.get('count_upper') is not None
            r={'queries':len(rows),'verifiedRobustPanel':sum(truth[(ds,qid)]=='ROBUST' for qid in ids),
                'certified':len(certified),'unsafeNumericalDecisionIds':wrong,
                'median':float(np.median(values)),'q25':float(np.quantile(values,.25)),
                'q75':float(np.quantile(values,.75)),'p95':float(np.quantile(values,.95)),
                'statusCounts':statuses,'finiteMilpDualBounds':int(dual)}
            summary[name]=r;csvrows.append({'dataset':ds,'profile':name,**{k:r[k] for k in ['queries','verifiedRobustPanel','certified','median','q25','q75','p95']}})
        budget[ds]={'status':'COMPLETE','profiles':summary}
    wide={};widecsv=[]
    for ds,ids in scope['timingPanelIds'].items():
        path=args.wide_runs/(ds+'.jsonl.gz');meta=path.with_name(path.name+'.metadata.json')
        if not meta.exists():wide[ds]={'status':'NOT_COMPLETE'};continue
        metadata=json.loads(meta.read_text());assert metadata['status']=='COMPLETE'
        assert metadata['rowsSha256']==hashlib.sha256(path.read_bytes()).hexdigest()
        rows=records(path);assert [r['queryId'] for r in rows]==ids
        methods={}
        for name in ['wide_enum','discrete_default']:
            selected=[next(x for x in r['runs'] if x['method']==name) for r in rows]
            values=np.array([r['seconds'] for r in selected]);positive=[row['queryId'] for row,run in zip(rows,selected) if run['rankUpper']<=10]
            methods[name]={'queries':48,'certified':len(positive),'median':float(np.median(values)),
                'q25':float(np.quantile(values,.25)),'q75':float(np.quantile(values,.75)),
                'p95':float(np.quantile(values,.95)),
                'unsafeDecisionIds':[qid for qid in positive if truth[(ds,qid)]!='ROBUST'],
                'resourceUnknown':sum(r['detail'].get('status')=='RESOURCE_UNKNOWN' for r in selected)}
            widecsv.append({'dataset':ds,'method':name,**{k:methods[name][k] for k in ['queries','certified','median','q25','q75','p95','resourceUnknown']}})
        ratios=[next(x['seconds'] for x in r['runs'] if x['method']=='wide_enum')/
                next(x['seconds'] for x in r['runs'] if x['method']=='discrete_default') for r in rows]
        wide[ds]={'status':'COMPLETE','methods':methods,'pairedGeometricEnumCostOverDiscrete':float(np.exp(np.log(ratios).mean()))}
    report={'status':'COMPLETE' if all(r['status']=='COMPLETE' for r in list(budget.values())+list(wide.values())) else 'INCOMPLETE',
        'retrospective':True,'decisionDatasets':datasets,'decisionTotals':totals,'budgetProfiles':budget,
        'wideEnumerationControl':wide,
        'decisionScope':'All fixed970 B2/K10 decisions resolved under the frozen scoring/numerical assumptions; not exact worst ranks or independent confirmation',
        'budgetScope':'Fixed144 previously observed queries; independent resource settings, not continuous anytime traces or a population latency claim'}
    boundary_path=args.boundary
    if boundary_path.exists():
        b=json.loads(boundary_path.read_text());assert b['status']=='COMPLETE' and b['queries']==8
        names=b['rows'][0]['order'];boundary={}
        for name in names:
            selected=[next(r for r in row['runs'] if r['profile']==name) for row in b['rows']]
            boundary[name]={'certified':sum(r['rankUpper']<=10 for r in selected),'queries':8,
                'medianSecondsDescriptive':float(np.median([r['seconds'] for r in selected]))}
        report['boundaryDiagnostic']={'status':'COMPLETE','outcomeSelected':True,'profiles':boundary}
        with args.output.with_name(args.output.stem+'-boundary.csv').open('w') as f:
            writer=csv.DictWriter(f,fieldnames=['dataset','queryId','profile','rankUpper','seconds']);writer.writeheader()
            for row in b['rows']:
                for r in row['runs']:writer.writerow({key:value for key,value in {**r,'dataset':row['dataset'],'queryId':row['queryId']}.items() if key in writer.fieldnames})
    else:report['status']='INCOMPLETE';report['boundaryDiagnostic']={'status':'NOT_COMPLETE'}
    args.output.write_text(json.dumps(report,indent=2)+'\n')
    if csvrows:
        with args.output.with_suffix('.csv').open('w') as f:
            writer=csv.DictWriter(f,fieldnames=list(csvrows[0]));writer.writeheader();writer.writerows(csvrows)
    if widecsv:
        with args.output.with_name(args.output.stem+'-wide.csv').open('w') as f:
            writer=csv.DictWriter(f,fieldnames=list(widecsv[0]));writer.writeheader();writer.writerows(widecsv)
    print(json.dumps({k:v for k,v in report.items() if k not in ['budgetProfiles','wideEnumerationControl']},indent=2))

if __name__=='__main__':main()
