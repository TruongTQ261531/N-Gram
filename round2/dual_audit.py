"""Development-only solver audit; does NOT retune or replace frozen test models."""
import pickle,json,time
from core import RES
from dual_solver import fit_dual
from run import valstats
with open(RES/'UIT-VSFC_prepared.pkl','rb') as f:en,td,y,dd,yd,le,ix=pickle.load(f)
cf=json.loads((RES/'selected.json').read_text())['UIT-VSFC']['bolt'];tr=[td[i] for i in ix];yy=y[ix]
t=time.perf_counter();W,logs=fit_dual(en,tr,yy,len(le.classes_),cf['alpha'],cf['eta'],17,max_outer=12,epochs=50,budget=3,gap_tol=1e-4)
rows=json.loads((RES/'dev_search.json').read_text());ref=next(r for r in rows if r['dataset']=='UIT-VSFC' and r['method']=='bolt' and r['alpha']==cf['alpha'] and r['eta']==cf['eta'])
last=ref['training']['rounds'][-1]
out={'scope':'development training subset only; diagnostic, not substituted into final test models','training_n':len(yy),'alpha':cf['alpha'],'eta':cf['eta'],'primal_dual_seconds':time.perf_counter()-t,'rounds':logs,'reference_restricted_plus_separation_objective':last['restricted_objective']+last['separation_gap'],'reference_gradient_norm':last['gradient_norm'],'dual_validation':valstats(en,dd,yd,W,len(le.classes_)),'reference_validation':ref['metrics'],'warning':'Primal-dual coordinate ascent and cutting planes are established techniques. This is a solver/convergence audit, not a claim of a new general optimization algorithm. Validation-only changes here do not modify the frozen confirmation configuration.'}
(RES/'dual_solver_audit.json').write_text(json.dumps(out,indent=2));print(json.dumps(out,indent=2))
