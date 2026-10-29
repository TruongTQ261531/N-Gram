"""Reconstruct numeric results and independently check exported BOLT models."""
import json,hashlib,itertools
from pathlib import Path
import numpy as np,pandas as pd
from core import RES,ROOT,score_metrics
from run import DS,METHODS,load
from artifact import load_model
from lattice import exact_path

def macro(y,p,k):
 cm=np.bincount(k*y+p,minlength=k*k).reshape(k,k);den=cm.sum(0)+cm.sum(1)
 return float(np.divide(2*np.diag(cm),den,out=np.zeros(k),where=den>0).mean())
fr=json.loads((RES/'selection_freeze.json').read_text());assert hashlib.sha256((RES/'selected.json').read_bytes()).hexdigest()==fr['selected_sha256'];assert hashlib.sha256((ROOT/'PROTOCOL.md').read_bytes()).hexdigest()==fr['protocol_sha256']
met=pd.read_csv(RES/'metrics.csv');diag=pd.read_csv(RES/'diagnostics.csv');count=0;dc=0;reloads=[];realcases=0;maxerr=0.
for ds in DS:
 z=np.load(RES/(ds+'_predictions.npz'));y=z['y'];k=int(y.max()+1);N=len(y)
 assert z['pred'].shape==(3,6,N)
 C=z['cert'];M=z['margins'];assert np.array_equal(C,M.max(-1)<-1e-9)
 assert np.all(~C[:,:,1:]|C[:,:,:-1]);assert np.all(~z['loose']|C);assert np.all(~C|z['greedy'])
 assert np.all(C[:,1]==C[:,1,:1]),'canonical certificate must be flat'
 for si,seed in enumerate(z['seeds']):
  for mi,m in enumerate(z['methods']):
   pp=z['pred'][si,mi];assert np.all(~C[si,mi,0]|(pp==y))
   f=macro(y,pp,k);acc=float(np.mean(y==pp))
   for bi,b in enumerate(z['budgets']):
    rr=met[(met.dataset==ds)&(met.seed==seed)&(met.method==m)&(met.budget==b)];assert len(rr)==1;r=rr.iloc[0]
    ba=float(np.mean([C[si,mi,bi,y==c].mean() for c in range(k)]))
    assert abs(f-r.macro_f1)<1e-12 and abs(acc-r.accuracy)<1e-12
    assert abs(C[si,mi,bi].mean()-r.robust_accuracy)<1e-12 and abs(ba-r.robust_balanced_accuracy)<1e-12
    assert int((z['greedy'][si,mi,bi]&~C[si,mi,bi]).sum())==r.greedy_false_certificates_if_misused
    count+=1
   for di,cname in enumerate(['random10','random30','max_allowed_fold']):
    pp=z['diagnostic_pred'][si,mi,di];r=diag[(diag.dataset==ds)&(diag.seed==seed)&(diag.method==m)&(diag.condition==cname)].iloc[0]
    assert abs(macro(y,pp,k)-r.macro_f1)<1e-12 and abs(np.mean(y==pp)-r.accuracy)<1e-12;dc+=1
 # Raw source data is read only for independent model checks, not fitting.
 _,_,te,le,_=load(ds);assert np.array_equal(te.row_id,z['row_ids'])
 en,W,labels=load_model(RES/(ds+'_bolt_model.npz'));docs=[en.encode(r.text,r.row_id) for r in te.head(100).itertuples()]
 p=(en.features(docs)@W).argmax(1);assert np.array_equal(p,z['pred'][0,5,:len(p)])
 from core import evaluate
 ev=evaluate(en,docs,y[:len(docs)],W,diagnose=False)
 assert np.array_equal(ev['cert'],C[0,5,:,:len(docs)]);err=float(np.max(np.abs(ev['margins']-M[0,5,:,:len(docs)])));assert err<1e-9
 reloads.append({'dataset':ds,'rows':len(docs),'predictions_and_certificates_equal':True,'margin_max_abs_error':err})
 # Exhaustively re-encode real six-token prefixes through the ordinary model pipeline.
 for row in te.head(20).itertuples():
  toks=row.text.split()[:6];base=en.encode(' '.join(toks));n=len(toks);paths=[];strings=[]
  for zz in itertools.product(range(3),repeat=n):
   zz=np.array(zz,np.int16)
   if base.costs[np.arange(n),zz].sum()>3:continue
   ss=' '.join(en.words[base.ids[i,zz[i]]] for i in range(n));assert sum(a!=b for a,b in zip(' '.join(toks),ss))==base.costs[np.arange(n),zz].sum()
   paths.append(zz);strings.append(ss)
  alt=[en.encode(s) for s in strings];scores=np.asarray(en.features(alt)@W);sc0=np.asarray(en.features([base])@W).ravel();yi=int(sc0.argmax());u,e=en.potentials(W,base,en.tables(W))
  for c in range(k):
   if c==yi:continue
   exact=exact_path(np.ascontiguousarray(u[:,:,c]-u[:,:,yi]),np.ascontiguousarray(e[:,:,:,c]-e[:,:,:,yi]),base.costs,3)[0]+W[-1,c]-W[-1,yi]
   brute=float(np.max(scores[:,c]-scores[:,yi]));maxerr=max(maxerr,abs(exact-brute));assert abs(exact-brute)<1e-9;realcases+=1
assert count==270 and dc==162
out={'metric_rows_checked':count,'diagnostic_rows_checked':dc,'reload_checks':reloads,'exhaustive_real_prefix_class_comparisons':realcases,'exhaustive_real_max_error':maxerr,'all_budget_monotonic':True,'no_false_factor_certificates':True,'repeat_fit':json.loads((RES/'repeat_fit.json').read_text())}
(RES/'verification.json').write_text(json.dumps(out,indent=2));print(json.dumps(out,indent=2))
