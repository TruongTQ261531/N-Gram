"""Posthoc proof diagnostic: fixed grid of linear supports for Pareto edges.

Positive recovery proves that particular edge also has a linear-support proof.
Failure of the grid does NOT prove that no separating weight exists, and this
is NOT a counterfactual end-to-end graph algorithm or coverage benchmark.
"""
import os
for k in ['OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS','NUMEXPR_NUM_THREADS']:os.environ[k]='1'
import argparse,gzip,hashlib,json
from pathlib import Path
import numpy as np
from reviewer_audit_2026_10_31.retention import load_inputs,normalize,context,native
from rank_bound import support

ROOT=Path(__file__).resolve().parent


def main():
    p=argparse.ArgumentParser();p.add_argument('--data',type=Path,required=True);a=p.parse_args()
    scope=json.loads((ROOT/'LINEAR_PROBE_SCOPE.json').read_text())
    assert hashlib.sha256(Path(__file__).read_bytes()).hexdigest()==scope['code_sha256']
    with gzip.open(ROOT/'results/linear_probe.jsonl.gz','xt') as out:
        for ds in ['scifact','nfcorpus','fiqa']:
            with gzip.open(ROOT.parent/'round3/results'/(ds+'_independent_replication.jsonl.gz'),'rt') as f:old={r['query_id']:r for r in map(json.loads,f)}
            index,texts,model_hash=load_inputs(a.data,ds)
            for qid in scope['query_ids'][ds]:
                original=old[qid];C=context(index,' '.join(normalize(texts[qid]).split()[:32]),2)
                assert not C['zero'] and len(C['lower'])+1==original['proposed_details']['pair']
                assert [str(index.ids[C['docs'][v]]) for v in C['candidate']]==original['proposed_details']['candidate_ids']
                checks=[r for r in original['proposed_details']['graph_certificate']['checks'] if r['method']=='pareto' and r['incompatible']]
                for check in checks:
                    pair=[check['left'],check['right']];D=[v[:,pair] for v in C['D']];Du=[v[:,pair] for v in C['Du']];tested=[]
                    for value in scope['lambda_grid']:
                        _,upper,_,_=support(D,Du,np.array([value,1-value]),2)
                        tested.append({'lambda':value,'outward_upper':upper})
                    half=next(r for r in tested if r['lambda']==.5);assert half['outward_upper']>=0
                    best=min(tested,key=lambda r:r['outward_upper'])
                    record={'dataset':ds,'query_id':qid,'model_fingerprint':model_hash,'left':pair[0],'right':pair[1],
                            'original_pareto_upper':check['upper'],'grid_support_proves_incompatible':best['outward_upper']<0,
                            'best_lambda':best['lambda'],'best_outward_upper':best['outward_upper'],'tested':tested}
                    out.write(json.dumps(native(record),sort_keys=True)+'\n');out.flush()
                print(ds,qid,'Pareto edges tested',len(checks),flush=True)


if __name__=='__main__':main()
