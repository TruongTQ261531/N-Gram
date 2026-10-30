"""Descriptive analysis on every case; no IID tests or post-hoc selection."""
from pathlib import Path
import csv,json,statistics
ROOT=Path(__file__).resolve().parent;R=ROOT/'results'
def main():
 a=json.loads((R/'query-results.json').read_text());rows=[];policy=[]
 keys=sorted(set((x['split'],x['language'],x['channel'],x['budget']) for x in a))
 for split,language,channel,budget in keys:
  z=[x for x in a if (x['split'],x['language'],x['channel'],x['budget'])==(split,language,channel,budget)];e=[x for x in z if x['oracleStatus']=='exact']
  row={'split':split,'language':language,'channel':channel,'budget':budget,'cases':len(z),'exact':len(e),'identity':sum(x['identityLattice'] for x in z),'cover_improvements_over_pair':sum(x['cover']<x['pair'] for x in z),'production_enumerates':sum(x['productionEnumerates'] for x in z),'graph_resource_unknown_checks':sum(x['graphUnknown'] for x in z)}
  for name in ['pair','cover','deployed']:
   gaps=[x[name]-x['gold'] for x in e];row[name+'_mean_excess']=statistics.mean(gaps) if gaps else None
  row['oracle_mean_depth']=statistics.mean(x['gold'] for x in e) if e else None;rows.append(row)
  for cap in [1,5,10,20]:
   for method in ['pair','cover','deployed']:
    policy.append({'split':split,'language':language,'channel':channel,'budget':budget,'cap':cap,'method':method,'cases':len(z),'certified':sum(x[method]<=cap for x in z),'oracle_feasible':sum(x['gold']<=cap for x in e),'oracle_feasible_but_abstained':sum(x['gold']<=cap<x[method] for x in e)})
 for filename,data in [('summary.csv',rows),('depth_policy.csv',policy)]:
  with (R/filename).open('w') as f:w=csv.DictWriter(f,fieldnames=list(data[0]));w.writeheader();w.writerows(data)
 summary={'cases':len(a),'exact':sum(x['oracleStatus']=='exact' for x in a),'identity':sum(x['identityLattice'] for x in a),'cover_improvement_cases':sum(x['cover']<x['pair'] for x in a),'deployed_improvement_cases':sum(x['deployed']<x['pair'] for x in a),'production_enumerates':sum(x['productionEnumerates'] for x in a),'evaluation_cases':sum(x['split']=='evaluation' for x in a),'development_cases':sum(x['split']=='development' for x in a),'families':len(set(x['family'] for x in a)),'synthetic':True,'q1_novelty':'unconfirmed; descriptive v0.1 audit only'}
 (R/'analysis.json').write_text(json.dumps(summary,indent=2));print(json.dumps(summary,indent=2))
if __name__=='__main__':main()
