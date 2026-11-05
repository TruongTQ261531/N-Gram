"""Join frozen per-query evidence and replay only descriptive clean-input data."""
import os
for key in ['OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS','NUMEXPR_NUM_THREADS']:os.environ[key]='1'
import argparse,csv,gzip,hashlib,json,platform,subprocess
from collections import Counter
from pathlib import Path
import numpy as np
from reviewer_audit_2026_10_31.retention import load_inputs,normalize,native
from core import variants

ROOT=Path(__file__).resolve().parent


def records(path):
    with gzip.open(path,'rt') as f:return [json.loads(line) for line in f]


def write_csv(path,rows):
    keys=list(dict.fromkeys(k for r in rows for k in r))
    with path.open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=keys);w.writeheader();w.writerows(rows)


def states_count(sizes,budget):
    count=[1]+[0]*budget
    for size in sizes:
        for b in range(budget,0,-1):count[b]+=count[b-1]*(size-1)
    return sum(count)


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--data',type=Path,required=True);a=parser.parse_args()
    out=ROOT/'results';out.mkdir(exist_ok=True,parents=True)
    ids=json.loads((ROOT.parent/'round3/results/replication_ids.json').read_text())
    with gzip.open(ROOT.parent/'decision_audit_2026_10_31/results/decisions.json.gz','rt') as f:decisions=json.load(f)['rows']
    gold={(r['dataset'],r['queryId']):r for r in decisions}
    allrows=[];times=[];traces=[];source_hashes={};selection={}
    for ds,query_ids in ids.items():
        old_path=ROOT.parent/'round3/results'/(ds+'_independent_replication.jsonl.gz')
        runtime_path=ROOT.parent/'reviewer_audit_2026_10_31/results/retention'/(ds+'.jsonl.gz')
        replay_path=ROOT.parent/'claims_consolidation_2026_11_01/results'/(ds+'.jsonl.gz')
        for p in [old_path,runtime_path,replay_path]:source_hashes[str(p.relative_to(ROOT.parent))]=hashlib.sha256(p.read_bytes()).hexdigest()
        old={r['query_id']:r for r in records(old_path)};runtime={r['queryId']:r for r in records(runtime_path)}
        replay={r['queryId']:r for r in records(replay_path)}
        assert set(old)==set(runtime)==set(replay)==set(query_ids) and len(set(query_ids))==len(query_ids)
        index,texts,fingerprint=load_inputs(a.data,ds);lookup={str(x):i for i,x in enumerate(index.ids)}
        dataset_rows=[]
        for number,qid in enumerate(query_ids,1):
            o=old[qid];audit=gold[(ds,qid)];r=replay[qid];qtext=' '.join(normalize(texts[qid]).split()[:32])
            assert hashlib.sha256(qtext.encode()).hexdigest()==r['querySha256']
            assert r['modelFingerprint']==fingerprint and r['referenceId']==o['reference_id']==audit['referenceId']
            score=index.score(qtext);ref=lookup[o['reference_id']]
            best_other=float(np.max(np.delete(score,ref)));sizes=[len(variants(t)[0]) for t in qtext.split()]
            first={x['method']:x for x in runtime[qid]['runs'] if x['repeat']==0};assert len(first)==3
            assert first['discrete']['rankUpper']==o['proposed_rank_upper']
            assert first['best_lp_enum']['rankUpper']==o['best_lp_enum_rank_upper']
            graph=o['proposed_details'].get('graph_certificate',{});checks=graph.get('checks',[])
            enum=o['proposed_details'].get('enumeration_certificate',{})
            milp=first['milp_enum']['detail'].get('milp',{})
            row={'dataset':ds,'query_id':qid,'query_sha256':r['querySha256'],'stage':'locked970_B2K10;later_audits_retrospective',
                 'budget':2,'K':10,'corpus_documents':index.n,'original_tokens':o['original_tokens'],'used_tokens':o['used_tokens'],
                 'truncated':o['original_tokens']>o['used_tokens'],'reference_id':o['reference_id'],'qrel_positive':o['reference_relevant'],
                 'clean_reference_score_point':float(score[ref]),'clean_margin_point':float(score[ref]-best_other),
                 'alternatives_sum':sum(sizes),'alternative_counts':json.dumps(sizes,separators=(',',':')),
                 'logical_states_B1':states_count(sizes,1),'logical_states_B2':states_count(sizes,2),'logical_states_B3':states_count(sizes,3),
                 'candidate_count_materialized':r['candidateCount'],'zero_witness':r['refinement']['status']=='zero_witness',
                 'pair_enum_rank':o['pair_enum_rank_upper'],'lp_enum_rank':o['best_lp_enum_rank_upper'],
                 'discrete_rank':o['proposed_rank_upper'],'milp_enum_rank':first['milp_enum']['rankUpper'],
                 'verified_label':audit['label'],'refined_rank':r['refinedRankUpper'],
                 'graph_rank':o['proposed_details'].get('graph'),'graph_checks':len(checks),
                 'support_conflicts':sum(c['incompatible'] and c['method']=='support' for c in checks),
                 'pareto_conflicts':sum(c['incompatible'] and c['method']=='pareto' for c in checks),
                 'pair_proof_resource_caps':sum(c['method']=='resource_cap' for c in checks),
                 'enumeration_status':enum.get('skipped','complete'),'enumeration_states':enum.get('states'),
                 'generic_lp_success':o['direct_details'].get('direct_success'),
                 'generic_lp_status':o['direct_details'].get('direct_certificate',{}).get('status'),
                 'milp_status':milp.get('status'),'milp_success':milp.get('success'),'milp_skip':milp.get('skipped'),
                 'milp_gap':milp.get('gap'),'milp_nodes':milp.get('nodes'),
                 'historical_process_peak_mib':o.get('peak_process_mib'),'memory_scope':'historical cumulative process HWM;not method-local peak',
                 'lp_to_discrete_gain':o['best_lp_enum_rank_upper']>10>=o['proposed_rank_upper'],
                 'discrete_fail_milp_success':o['proposed_rank_upper']>10>=first['milp_enum']['rankUpper'],
                 'discrete_success_milp_fail':first['milp_enum']['rankUpper']>10>=o['proposed_rank_upper']}
            allrows.append(row);dataset_rows.append(row)
            for x in runtime[qid]['runs']:
                d=x['detail'];m=d.get('milp',{})
                times.append({'dataset':ds,'query_id':qid,'method':x['method'],'repeat':x['repeat'],'seconds':x['seconds'],
                    'rank_upper':x['rankUpper'],'candidate_count':d.get('candidateCount'),'method_order':json.dumps(x['order']),
                    'enum_status':d.get('enumStatus'),'generic_lp_success':d.get('genericLpSuccess'),
                    'milp_status':m.get('status'),'milp_skip':m.get('skipped'),'milp_success':m.get('success'),
                    'milp_gap':m.get('gap'),'milp_nodes':m.get('nodes'),'stage_seconds':'not recorded in this archive',
                    'method_peak_rss_mib':'not measured','source':'reviewer_audit_2026_10_31;retrospective;warm index;one numerical thread'})
            if row['lp_to_discrete_gain'] or row['discrete_fail_milp_success'] or row['discrete_success_milp_fail']:
                traces.append({'dataset':ds,'queryId':qid,'querySha256':r['querySha256'],
                    'referenceId':o['reference_id'],'bounds':{k:row[k] for k in ['pair_enum_rank','lp_enum_rank','discrete_rank','milp_enum_rank']},
                    'verifiedLabel':audit['label'],'coverGroups':graph.get('groups'),
                    'pairProofs':checks,'lpIterations':o['proposed_details'].get('lp_certificate',{}).get('iterations'),
                    'enum':enum,'selection':'ALL coverage-discordant queries;diagnostic,not independent confirmation'})
        # Three hash-selected queries per token-length quartile, without outcomes.
        ordered=sorted(dataset_rows,key=lambda row:(row['used_tokens'],hashlib.sha256(('ipm-length-order-v1|'+ds+'|'+row['query_id']).encode()).hexdigest()))
        selected=[]
        for quartile,chunk in enumerate(np.array_split(np.array(ordered,dtype=object),4)):
            chosen=sorted(chunk.tolist(),key=lambda row:hashlib.sha256(('ipm-followup-v1|'+ds+'|'+row['query_id']).encode()).hexdigest())[:3]
            selected.extend({'queryId':row['query_id'],'lengthQuartile':quartile+1,'usedTokens':row['used_tokens']} for row in chosen)
        selection[ds]=selected
        print(ds,'joined',len(dataset_rows),'LP gains',sum(r['lp_to_discrete_gain'] for r in dataset_rows),flush=True)
        del index
    assert len(allrows)==970 and sum(r['lp_to_discrete_gain'] for r in allrows)==32
    assert sum(r['discrete_rank']<=10 for r in allrows)==259
    assert sum(r['lp_enum_rank']<=10 for r in allrows)==227
    assert sum(r['milp_enum_rank']<=10 for r in allrows)==260
    assert Counter(r['verified_label'] for r in allrows)=={'ROBUST':266,'NONROBUST':704}
    assert all(r['verified_label']=='ROBUST' for r in allrows if min(r['lp_enum_rank'],r['discrete_rank'],r['milp_enum_rank'])<=10)
    write_csv(out/'query_level.csv',native(allrows));write_csv(out/'runtime_per_query.csv',native(times))
    write_csv(out/'disagreement_cases.csv',native([r for r in allrows if r['lp_to_discrete_gain'] or r['discrete_fail_milp_success'] or r['discrete_success_milp_fail']]))
    with gzip.open(out/'disagreement_traces.jsonl.gz','xt') as f:
        for trace in traces:f.write(json.dumps(native(trace),separators=(',',':'))+'\n')
    (ROOT/'selection.json').write_text(json.dumps({'rule':'3hash-selected IDs per within-corpus token-length quartile;no outcomes used','datasets':selection},indent=2)+'\n')
    (out/'extraction.json').write_text(json.dumps({'status':'PASS','queries':970,'sourceFiles':source_hashes,'runtimeRows':len(times),
        'labelsRetrospective':True,'newSourceReplay':'Only clean scores and input descriptors;not970new solver runs',
        'cleanScoresAreDescriptivePointArithmetic':True,'modelOrChannelChanges':False},indent=2)+'\n')


if __name__=='__main__':main()
