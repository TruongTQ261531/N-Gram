"""Bounded matched ablations of the existing certifier, not a new method."""
import os
for key in ['OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS','NUMEXPR_NUM_THREADS']:os.environ[key]='1'
import time
import numpy as np
from reviewer_audit_2026_10_31.retention import native
from core import outward_scores
from screening import coarse_candidates
from rank_bound import ranges,envelope,direct_reference,support
from compatibility import cover_bound
from enumeration import exhaustive_count
from mip_reference import solve as mip_solve

CONFIG={
 'pair_only':{'enum':False},
 'pair_enum':{'enum':True},
 'lp_no_enum':{'enum':False,'lp':True,'generic':True},
 'custom_lp_enum':{'enum':True,'lp':True},
 'best_lp_enum':{'enum':True,'lp':True,'generic':True},
 'discrete_no_enum':{'enum':False,'lp':True,'graph':'full'},
 'discrete_no_lp':{'enum':True,'graph':'full'},
 'discrete_support_only':{'enum':True,'lp':True,'graph':'support'},
 'discrete':{'enum':True,'lp':True,'graph':'full'},
 'milp_enum':{'enum':True,'milp':True},
 'discrete_no_screen':{'enum':True,'lp':True,'graph':'full','screen':False},
}


def context(index,text,budget,screen=True,max_cells=20_000_000):
    start=time.perf_counter();query=index.query(text);ranking=query.rankings();ref=int(ranking[0]);prepared=time.perf_counter()
    if screen:
        coarse=coarse_candidates(query,ranking,budget);zero=coarse['zero'][budget]
        docs=np.array([ref]+sorted(set(coarse['keep'][budget])-{ref}),dtype=int)
    else:
        R=[(a@index.W[ref].T.tocsr()).toarray()[:,0] for a in query.features]
        eligible=[np.flatnonzero(r==0.) for r in R]
        zero=all(len(e)>0 for e in eligible) and sum(int(e[0]!=0) for e in eligible)<=budget
        docs=np.array([ref]+[j for j in range(index.n) if j!=ref],dtype=int)
    screened=time.perf_counter();cells=sum(a.shape[0] for a in query.features)*len(docs)
    base={'n':index.n,'ref':ref,'zero':bool(zero),'scoreCellsPlanned':cells,'materializedDocuments':0,
          'querySeconds':prepared-start,'screenSeconds':screened-prepared,'formCounts':[a.shape[0] for a in query.features]}
    if zero:return {**base,'status':'zero_witness','contextSeconds':time.perf_counter()-start}
    if cells>max_cells:return {**base,'status':'context_resource_cap','contextSeconds':time.perf_counter()-start}
    W=index.W[docs].T.tocsr();F=[(a@W).toarray() for a in query.features];materialized=time.perf_counter()
    lo,hi=outward_scores(F,query.features)
    _,L,U=ranges(F,lo,hi,0,np.arange(1,len(docs)),budget)
    keep=U[budget]>=0;candidate=np.arange(1,len(docs))[keep]
    D=[f[:,candidate]-f[:,0,None] for f in F]
    Du=[np.nextafter(h[:,candidate]-l[:,0,None],np.inf) for l,h in zip(lo,hi)]
    return {**base,'status':'ready','docs':docs,'candidate':candidate,'D':D,'Du':Du,'lower':L[budget,keep],
            'materializedDocuments':len(docs),'candidateCount':len(candidate),
            'materializeSeconds':materialized-screened,'pairIntervalSeconds':time.perf_counter()-materialized,
            'contextSeconds':time.perf_counter()-start}


def support_cover(D,Du,budget,max_checks=120,max_candidates=80):
    """Same first-fit schedule/budget, with support only; never calls Pareto."""
    m=D[0].shape[1] if D else 0
    if m>max_candidates:return {'count_upper':m,'groups':[[j] for j in range(m)],'checks':[],'skipped':'candidate_resource_cap'}
    groups=[];checks=[];cache={}
    for j in range(m):
        placed=False
        for group in groups:
            okay=True
            for k in group:
                pair=(min(j,k),max(j,k))
                if pair not in cache:
                    if len(checks)>=max_checks:okay=False;break
                    _,upper,_,_=support([d[:,pair] for d in D],[u[:,pair] for u in Du],np.array([.5,.5]),budget)
                    result={'left':pair[0],'right':pair[1],'method':'support','upper':upper,'incompatible':bool(upper<0)}
                    checks.append(native(result));cache[pair]=result['incompatible']
                if not cache[pair]:okay=False;break
            if okay:group.append(j);placed=True;break
        if not placed:groups.append([j])
    return {'count_upper':len(groups),'groups':groups,'checks':checks}


def kernel(C,method,budget):
    if C['status']!='ready':return C['n'],{'status':C['status']}
    spec=CONFIG[method];D,Du,lower=C['D'],C['Du'],C['lower'];m=len(lower);rank=m+1
    detail={'status':'bounded','pairRank':rank,'stages':{}}
    if spec['enum']:
        start=time.perf_counter();enum=exhaustive_count(D,Du,budget);detail['stages']['enumeration']=time.perf_counter()-start
        rank=min(rank,enum.get('rank_upper',rank));detail['enumeration']=enum
    if spec.get('lp'):
        start=time.perf_counter();lp=envelope(D,Du,lower,budget,40);detail['stages']['customLP']=time.perf_counter()-start
        lp_rank=int(np.floor(np.nextafter(lp['upper_count'],np.inf)))+1
        rank=min(rank,lp_rank);detail['customLP']={'rankUpper':lp_rank,'iterations':lp['iterations'],'history':lp.get('history',[])}
    if spec.get('generic'):
        start=time.perf_counter()
        if sum(len(d) for d in D)*m<=2_000_000:
            direct=direct_reference(D,Du,lower,budget)
            if direct.get('success'):rank=min(rank,int(np.floor(np.nextafter(direct['upper_count'],np.inf)))+1)
        else:direct={'skipped':'matrix_entries_resource_cap'}
        detail['stages']['genericLP']=time.perf_counter()-start;detail['genericLP']=direct
    if spec.get('graph'):
        start=time.perf_counter();g=(support_cover if spec['graph']=='support' else cover_bound)(D,Du,budget,120,80)
        detail['stages']['graph']=time.perf_counter()-start;rank=min(rank,g['count_upper']+1);detail['graph']=g
    if spec.get('milp'):
        start=time.perf_counter();milp=mip_solve(Du,lower,budget,1.);detail['stages']['MILP']=time.perf_counter()-start
        if milp.get('count_upper') is not None:rank=min(rank,int(np.floor(np.nextafter(milp['count_upper']+1e-6,np.inf)))+1)
        detail['MILP']=milp
    return int(rank),native(detail)
