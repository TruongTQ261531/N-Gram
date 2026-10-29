"""Post-hoc mechanism and solver-availability audit; no new hypothesis tests."""
from pathlib import Path
import json
import pandas as pd
from analyze import load,ranks
from verify_predictions import load as load_any
R=Path(__file__).resolve().parent/'results'
def main():
 rows=[]
 for ds in ['scifact','nfcorpus','fiqa']:
  for x in load(ds):
   z=x['bounds'][1];v=ranks(z);ref=z['direct_lp'];pro=v['proposed'];base=v['best_lp_enum']
   rows.append({'stage':'primary','dataset':ds,'query_id':x['query_id'],'proposed':pro,'best_lp_enum':base,'gain':pro<=10<base,'loss':base<=10<pro,
    'reference_relevant':x['reference_relevant'],'generic_lp_success':bool(ref.get('success',False)),'generic_lp_objective':ref.get('lp_objective'),
    'generic_cap_skip':ref.get('skipped')=='matrix_entries_resource_cap','envelope_gap':z.get('envelope_gap'),'zero_shortcut':z['zero_reference_shortcut']})
  for x in load_any(ds+'_independent_replication.jsonl'):
   z=x['proposed_details'];ref=x['direct_details'].get('direct_certificate',{});pro=x['proposed_rank_upper'];base=x['best_lp_enum_rank_upper']
   rows.append({'stage':'independent','dataset':ds,'query_id':x['query_id'],'proposed':pro,'best_lp_enum':base,'gain':pro<=10<base,'loss':base<=10<pro,
    'reference_relevant':x['reference_relevant'],'generic_lp_success':bool(ref.get('success',False)),'generic_lp_objective':ref.get('lp_objective'),
    'generic_cap_skip':not z.get('zero_reference',False) and 'direct_certificate' not in x['direct_details'],'envelope_gap':z.get('lp_certificate',{}).get('envelope_gap'),'zero_shortcut':z.get('zero_reference',False)})
 A=pd.DataFrame(rows);A.to_csv(R/'mechanism_query_audit.csv',index=False);summary=[]
 for (stage,ds),a in A.groupby(['stage','dataset'],sort=False):
  win=a.gain;relevant=a.reference_relevant;obj=a.generic_lp_objective
  summary.append({'stage':stage,'dataset':ds,'queries':len(a),'wins':int(win.sum()),'losses':int(a.loss.sum()),'wins_generic_lp_success':int((win&a.generic_lp_success).sum()),
   'wins_generic_lp_cap_skipped':int((win&a.generic_cap_skip).sum()),'wins_nominal_lp_objective_above_count_threshold_by_1e_6':int((win&(obj>10+1e-6)).sum()),
   'wins_nominal_lp_objective_within_1e_6_of_10':int((win&(abs(obj-10)<=1e-6)).sum()),
   'positive_qrel_wins':int((win&relevant).sum()),'positive_qrel_losses':int((a.loss&relevant).sum()),
   'baseline_positive_qrel_certified':int(((a.best_lp_enum<=10)&relevant).sum()),'proposed_positive_qrel_certified':int(((a.proposed<=10)&relevant).sum()),
   'generic_lp_success_total':int(a.generic_lp_success.sum()),'generic_lp_cap_skips_total':int(a.generic_cap_skip.sum()),'zero_shortcuts':int(a.zero_shortcut.sum())})
 B=pd.DataFrame(summary);B.to_csv(R/'mechanism_summary.csv',index=False);print(B.to_string(index=False))
 (R/'mechanism_notes.json').write_text(json.dumps({'posthoc':True,'new_p_values':False,'numerical_lp_objectives_are_not_formally_verified_lower_bounds':True,
  'reason':'Distinguish actual matched generic-LP runs from optimizer/cap artifacts and positive-qrel utility from mere stability. Near-integer threshold effects and source numerical assumptions remain visible.'},indent=2))
if __name__=='__main__':main()
