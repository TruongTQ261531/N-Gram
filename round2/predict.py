"""Predict and certify prediction invariance; does not assert semantic correctness."""
import argparse,json
import numpy as np
from artifact import load_model
from lattice import exact_path
p=argparse.ArgumentParser();p.add_argument('--model',required=True);p.add_argument('--text',required=True);p.add_argument('--budget',type=int,default=3);a=p.parse_args()
assert a.budget>=0
en,W,labels=load_model(a.model);d=en.encode(a.text);scores=np.asarray(en.features([d])@W).ravel();y=int(scores.argmax());u,e=en.potentials(W,d,en.tables(W));margins=[]
for c in range(len(labels)):
 if c==y:continue
 v,z=exact_path(np.ascontiguousarray(u[:,:,c]-u[:,:,y]),np.ascontiguousarray(e[:,:,:,c]-e[:,:,:,y]),d.costs,a.budget)
 margins.append(float(v+W[-1,c]-W[-1,y]))
print(json.dumps({'predicted_label':str(labels[y]),'budget_changed_NFC_codepoints':a.budget,'prediction_invariant_within_defined_lattice':bool(max(margins)<-1e-9),'worst_competing_margin':max(margins),'retained_whitespace_tokens':len(d.ids),'scope':'raw/tone-folded/full-folded same-length token variants; first 128 tokens; no semantic correctness guarantee'},ensure_ascii=False,indent=2))
