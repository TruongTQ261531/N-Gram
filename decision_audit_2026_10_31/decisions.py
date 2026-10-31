"""Exact stored-weight negative witnesses; separate upper-enclosure audit."""
import os
for key in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS','NUMEXPR_NUM_THREADS'):
    os.environ[key]='1'
from pathlib import Path
import argparse,gzip,hashlib,json,itertools
from fractions import Fraction
import numpy as np
from threadpoolctl import threadpool_limits
from reviewer_audit_2026_10_31.retention import load_inputs,context,normalize,native,mip_solve
from reviewer_audit_2026_10_31.bridge_refinement import exact_scores
from reviewer_audit_2026_10_31.verify_discordant import exhaustive_enclosure

ROOT=Path(__file__).resolve().parent

def read(path):
    with gzip.open(path,'rt') as f:return [json.loads(line) for line in f]

def prove_witness(index,query,reference,choices,k=10,check_documents=64):
    if len(choices)!=len(query.forms) or sum(int(a)!=0 for a in choices)>2:
        raise ValueError('State outside budget')
    if any(int(a)!=a or not 0<=a<len(forms) for a,forms in zip(choices,query.forms)):
        raise ValueError('State outside variants')
    X=index.v.transform([query.text(choices)]).tocsr()
    factored=sum((a[int(c)] for a,c in zip(query.features,choices))).tocsr()
    assert (X!=factored).nnz==0
    assert np.all(X.data==X.data.astype(np.int64)) and np.all(X.data>=0)
    transpose=index.transpose();r=exact_scores(transpose,X,[reference])[0]
    if r==0:
        return {'proved':True,'rankLower':index.n,'reason':'exact_zero_reference_nonnegative_index',
            'choices':list(map(int,choices)),'exactReference':'0','queryFeatureSha256':hashlib.sha256(X.indices.tobytes()+X.data.tobytes()).hexdigest()}
    z=np.asarray((X@transpose).toarray()).ravel()
    count=min(check_documents,index.n)
    selected=np.argpartition(z,-count)[-count:];selected=selected[selected!=reference]
    values=exact_scores(transpose,X,selected)
    promoted=[(int(j),value) for j,value in zip(selected,values) if value>=r]
    if len(promoted)<k:return {'proved':False,'exactCheckedDocuments':len(selected),'rankLower':len(promoted)+1}
    promoted=sorted(promoted,key=lambda pair:(-pair[1],str(index.ids[pair[0]])))[:k]
    scores=[str(value) for _,value in promoted]
    return {'proved':True,'rankLower':k+1,'reason':'exact_dyadic_competitors_including_ties',
        'choices':list(map(int,choices)),'exactReference':str(r),
        'competitorIds':[str(index.ids[j]) for j,_ in promoted],
        'minimumExactMargin':str(min(v-r for _,v in promoted)),
        'exactCompetitorScoresSha256':hashlib.sha256(json.dumps(scores).encode()).hexdigest()}

def archived_states(old,new,query):
    yield 'raw',[0]*len(query.tokens)
    detail=old['proposed_details']
    if detail.get('choices') is not None:yield 'archived_zero',detail['choices']
    for label,item in [('archived_support',detail.get('lp_certificate',{})),
                       ('archived_generic',old.get('direct_details',{}).get('direct_certificate',{}))]:
        if item.get('choices') is not None:yield label,item['choices']
    for run in new['runs']:
        if run.get('witness'):yield 'milp_repeat_'+str(run['repeat']),run['witness']['choices']

def main():
    p=argparse.ArgumentParser();p.add_argument('--data',type=Path,required=True)
    p.add_argument('--output',type=Path,required=True);args=p.parse_args()
    if args.output.exists():raise FileExistsError(args.output)
    repo=ROOT.parent;rows=[]
    for ds in ['scifact','nfcorpus','fiqa']:
        old={r['query_id']:r for r in read(repo/'round3/results'/(ds+'_independent_replication.jsonl.gz'))}
        records=read(repo/'reviewer_audit_2026_10_31/results/retention'/(ds+'.jsonl.gz'))
        index,texts,model_hash=load_inputs(args.data,ds)
        assert np.isfinite(index.W.data).all() and index.W.data.min(initial=0)>=0
        for number,new in enumerate(records,1):
            qid=new['queryId'];prior=old[qid];text=' '.join(normalize(texts[qid]).split()[:32])
            query=index.query(text);reference=int(np.flatnonzero(index.ids==prior['reference_id'])[0])
            assert int(query.rankings()[0])==reference
            first={r['method']:r for r in new['runs'] if r['repeat']==0}
            positive=any(r['rankUpper']<=10 for r in first.values())
            record={'dataset':ds,'queryId':qid,'modelFingerprint':model_hash,
                'referenceId':prior['reference_id'],'originalCertifiedUnion':positive,
                'originalBounds':{m:r['rankUpper'] for m,r in first.items()}}
            if positive:
                C=context(index,text,2);audit=exhaustive_enclosure(C['Du'])
                record['positiveEnclosure']=audit
                record['label']='ROBUST' if audit.get('rankUpper',index.n)<=10 else 'UNKNOWN'
            else:
                seen=set();proof=None;attempts=0
                for label,state in archived_states(prior,new,query):
                    state=tuple(map(int,state))
                    if state in seen:continue
                    seen.add(state);attempts+=1
                    trial=prove_witness(index,query,reference,state)
                    if trial['proved']:proof={**trial,'source':label};break
                if proof is None:
                    C=context(index,text,2);audit=exhaustive_enclosure(C['Du'])
                    record['resolutionEnclosure']=audit
                    if audit.get('rankUpper',index.n)<=10:record['label']='ROBUST'
                    elif audit.get('upperEnvelopeMaximizer') is not None:
                        trial=prove_witness(index,query,reference,audit['upperEnvelopeMaximizer'])
                        if trial['proved']:proof={**trial,'source':'upper_envelope_candidate'}
                    searches=[]
                    if proof is None and record.get('label')!='ROBUST':
                        for seconds in [10.,30.]:
                            result=mip_solve(C['Du'],C['lower'],2,seconds)
                            searches.append({'secondsLimit':seconds,'solver':native(result)})
                            if result.get('choices') is not None:
                                trial=prove_witness(index,query,reference,result['choices'])
                                if trial['proved']:proof={**trial,'source':'supplementary_milp_'+str(seconds)};break
                        record['verificationOnlySearches']=searches
                if proof:
                    record['label']='NONROBUST';record['exactWitness']=proof
                record.setdefault('label','UNKNOWN');record['archivedStatesChecked']=attempts
            rows.append(record)
            print(ds,number,'/',len(records),qid,record['label'],flush=True)
        del index
    summary={label:sum(r['label']==label for r in rows) for label in ['ROBUST','NONROBUST','UNKNOWN']}
    report={'status':'COMPLETE','retrospective':True,'queries':len(rows),'classification':summary,
        'exactNegativeArithmetic':'Python dyadic integer/Fraction sums of stored float64 weights and integer counts',
        'positiveScope':'Frozen screening and IEEE error model; exhaustive margin-enclosure upper bounds',
        'notUsedToChangeOriginalBoundsOrTimes':True,'rows':rows}
    args.output.parent.mkdir(parents=True,exist_ok=True)
    with gzip.open(args.output,'xt') as f:json.dump(native(report),f,separators=(',',':'))
    args.output.with_suffix('.summary.json').write_text(json.dumps({k:v for k,v in report.items() if k!='rows'},indent=2)+'\n')
    print(summary,flush=True)

if __name__=='__main__':
    with threadpool_limits(limits=1):main()
