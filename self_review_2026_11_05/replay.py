"""All-970 graph-component replay with identical frozen prefix bounds.

This is a retrospective decision ablation, not whole-pipeline runtime or
a new prospective comparison. Original LP/enum prefixes are reused explicitly.
"""
import os
for key in ['OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS','NUMEXPR_NUM_THREADS']:os.environ[key]='1'
import argparse,gzip,hashlib,json,time
from pathlib import Path
from reviewer_audit_2026_10_31.retention import load_inputs,normalize,native,context,cover_bound
from codex_followup_2026_11_05.experiments import support_cover
from argon_followup_2026_11_01.schedule_certificate import certificate

ROOT=Path(__file__).resolve().parent


def compact(graph):
    return {k:v for k,v in graph.items() if k!='groups'} if graph.get('skipped') else graph


def main():
    p=argparse.ArgumentParser();p.add_argument('--data',required=True,type=Path);a=p.parse_args()
    freeze=json.loads((ROOT/'FREEZE.json').read_text())
    for path,digest in freeze['source_sha256'].items():
        assert hashlib.sha256((ROOT.parent/path).read_bytes()).hexdigest()==digest,path
    ids=json.loads((ROOT.parent/'round3/results/replication_ids.json').read_text())
    start=time.perf_counter();count=0
    with gzip.open(ROOT/'results/graph_replay.jsonl.gz','xt') as out:
        for ds,query_ids in ids.items():
            index,texts,model_hash=load_inputs(a.data,ds)
            with gzip.open(ROOT.parent/'round3/results'/(ds+'_independent_replication.jsonl.gz'),'rt') as f:
                old={r['query_id']:r for r in map(json.loads,f)}
            for qid in query_ids:
                if time.perf_counter()-start>2700:raise TimeoutError('45 minute study guard; retain partial receipts')
                text=' '.join(normalize(texts[qid]).split()[:32]);t=time.perf_counter();C=context(index,text,2);context_seconds=time.perf_counter()-t
                original=old[qid];assert str(index.ids[C['ref']])==original['reference_id']
                row={'dataset':ds,'query_id':qid,'model_fingerprint':model_hash,'query_sha256':hashlib.sha256(text.encode()).hexdigest(),
                     'zero_witness':C['zero'],'context_seconds':context_seconds,'prefix_source':'original frozen pair/custom-LP/enumeration bounds;not rerun solvers'}
                if C['zero']:
                    assert original['proposed_rank_upper']==index.n
                    row.update(full_rank=index.n,support_rank=index.n,status='zero_witness',candidate_count=None)
                else:
                    detail=original['proposed_details'];m=len(C['lower'])
                    assert detail['pair']==m+1
                    assert [str(index.ids[C['docs'][v]]) for v in C['candidate']]==detail['candidate_ids']
                    prefix=min(int(detail[k]) for k in ['pair','lp','enum'] if detail[k] is not None)
                    order=sorted(['full','support'],key=lambda method:hashlib.sha256(f'review-order-v1|{ds}|{qid}|{method}'.encode()).hexdigest())
                    row.update(candidate_count=m,prefix_rank=prefix,status='bounded',method_order=order)
                    for name in order:
                        t=time.perf_counter();graph=(cover_bound if name=='full' else support_cover)(C['D'],C['Du'],2,120,80)
                        row[name+'_graph_seconds']=time.perf_counter()-t
                        row[name+'_rank']=min(prefix,graph['count_upper']+1)
                        row[name+'_graph']=native(compact(graph))
                        if not graph.get('skipped'):row[name+'_schedule_certificate']=certificate(graph['groups'],graph['checks'])
                    assert row['full_rank']==original['proposed_rank_upper'],(ds,qid,row['full_rank'],original['proposed_rank_upper'])
                    assert row['full_graph']['count_upper']+1==detail['graph'],(ds,qid,'graph mismatch')
                out.write(json.dumps(native(row),sort_keys=True)+'\n');out.flush();count+=1
                progress={'status':'running','queries_completed':count,'planned':970,'last':ds+':'+qid,'elapsed_seconds':time.perf_counter()-start}
                (ROOT/'results/progress.json').write_text(json.dumps(progress,indent=2)+'\n')
                if count%25==0:print(json.dumps(progress),flush=True)
                del C
    assert count==970
    progress['status']='complete';(ROOT/'results/progress.json').write_text(json.dumps(progress,indent=2)+'\n');print(json.dumps(progress),flush=True)


if __name__=='__main__':main()
