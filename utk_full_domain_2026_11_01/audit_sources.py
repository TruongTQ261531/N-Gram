"""Independently recheck dominance minima and screen receipts on full scores.

Post-timing validation only; no change to the frozen timed implementations.
"""
import os
for key in ['OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS','NUMEXPR_NUM_THREADS']:os.environ[key]='1'
import argparse,gzip,json,pickle,time
import numpy as np
import pandas as pd
from lazy_cert_study.core import lattice
from utk_full_domain_2026_11_01.run import ROOT,digest
from utk_full_domain_2026_11_01.archive import execution_rows


def main():
    p=argparse.ArgumentParser();p.add_argument('--data',type=__import__('pathlib').Path,required=True);a=p.parse_args()
    freeze=json.loads((ROOT/'FREEZE.json').read_text())
    assert digest(a.data/'index.pkl')==freeze['privateIndexSha256']
    with (a.data/'index.pkl').open('rb') as f:index=pickle.load(f)
    q=pd.read_csv(a.data/'dataset/query.csv',sep='\t',dtype={'query_id':str}).fillna('')
    texts=dict(zip(q.query_id,q['query']));started=time.perf_counter();reports=[]
    with gzip.open(ROOT/'results/oracle.jsonl.gz','rt') as oracle:
        for row,gold_line in zip(execution_rows(),oracle,strict=True):
            gold=json.loads(gold_line);qid=row['queryId'];assert gold['queryId']==qid
            Q=lattice(index,texts[qid]);states=[s['state'] for s in gold['states']]
            details=[row['receipts'][m] for m in ['rsa_fd','jaa_fd'] if m in row['receipts']]
            screens=[d['screen'] for d in details if 'screen' in d]
            proofs=[d['proof'] for d in details if d.get('status')=='exact' and 'proof' in d]
            if len(screens)==2:assert screens[0]==screens[1]
            if len(proofs)==2:
                assert proofs[0]['poolMapping']==proofs[1]['poolMapping']
                assert proofs[0]['filter']==proofs[1]['filter']
            screen=screens[0] if screens else None;proof=proofs[0] if proofs else None
            if proof:
                mapping=np.asarray(proof['poolMapping']);rejected=proof['filter']['rejected']
                candidate=np.array([r['document'] for r in rejected],dtype=int)
                dominators=np.asarray([r['dominators'] for r in rejected],dtype=int).reshape(-1,10)
                expected=np.asarray([r['minimumMargins'] for r in rejected],dtype=np.int64).reshape(-1,10)
                minimum=np.full(expected.shape,np.iinfo(np.int64).max,dtype=np.int64)
            if screen:
                anchors=np.asarray(screen['anchors'],dtype=int);anchor_min=np.full(len(anchors),np.iinfo(np.int64).max,dtype=np.int64)
                excluded=np.ones(index.n,dtype=bool);excluded[screen['coarsePool']]=False;excluded_max=-1
            for offset in range(0,len(states),32):
                batch=states[offset:offset+32]
                texts_batch=[' '.join(f[s]['text'] for f,s in zip(Q.forms,state)) for state in batch]
                scores=(index.vectorizer.transform(texts_batch)@index.transpose).toarray()
                if screen:
                    anchor_min=np.minimum(anchor_min,scores[:,anchors].min(axis=0))
                    excluded_max=max(excluded_max,int(scores[:,excluded].max(initial=-1)))
                if proof:
                    for block in range(0,len(candidate),512):
                        end=block+512
                        gaps=scores[:,mapping[dominators[block:end]]]-scores[:,mapping[candidate[block:end]],None]
                        minimum[block:end]=np.minimum(minimum[block:end],gaps.min(axis=0))
            if proof:np.testing.assert_array_equal(minimum,expected)
            if screen:
                np.testing.assert_array_equal(anchor_min,np.asarray(screen['anchorLower']))
                assert int(np.partition(anchor_min,-10)[-10])==screen['threshold']
                assert excluded_max<=screen['maximumExcludedUpper']<screen['threshold'] or not excluded.any()
                assert set(gold['union'])<=set(screen['coarsePool'])
            reports.append({'queryId':qid,'states':len(states),'screenChecked':bool(screen),
                            'exactDominanceMinimaChecked':int(expected.size) if proof else 0,
                            'sourceFullCorpusMatches':True})
            print(qid,'dominance minima',reports[-1]['exactDominanceMinimaChecked'],flush=True)
    result={'status':'PASS','queries':len(reports),'states':sum(r['states'] for r in reports),
            'minimaChecked':sum(r['exactDominanceMinimaChecked'] for r in reports),
            'seconds':time.perf_counter()-started,'records':reports,
            'scope':'All-state unprojected sparse text scores, independent of factor support formula',
            'scriptSha256':digest(ROOT/'audit_sources.py'),'privateIndexSha256':freeze['privateIndexSha256']}
    (ROOT/'results/source_audit.json').write_text(json.dumps(result,indent=2)+'\n')


if __name__=='__main__':main()
