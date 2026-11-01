"""Independent, tie-aware finite-domain adaptations of UTK RSA/JAA.

These are matched baseline implementations, not the original C++ programs.
No convex relaxation, quantization, relevance labels or oracle input is used.
"""
import itertools,time
import numpy as np


class ResourceCap(RuntimeError):pass


def guard(deadline):
    if time.perf_counter()>deadline:raise ResourceCap('wall_guard')


def states_for(sizes,budget):
    out=[]
    for cost in range(min(budget,len(sizes))+1):
        for positions in itertools.combinations(range(len(sizes)),cost):
            for options in itertools.product(*(range(1,sizes[i]) for i in positions)):
                s=[0]*len(sizes)
                for i,a in zip(positions,options):s[i]=a
                out.append(s)
    return out


def minimum_margins(F,left,right,budget):
    """Exact min(S_left-S_right) for each left under ONE shared token budget."""
    raw=np.zeros(len(left),dtype=np.int64);loss=[]
    for f in F:
        d=f[:,left]-f[:,right,None]
        raw+=d[0];loss.append(d[0]-d.min(axis=0))
    if budget and loss:
        a=np.asarray(loss);b=min(budget,len(a))
        raw-=np.partition(a,len(a)-b,axis=0)[-b:].sum(axis=0)
    return raw


def regional_filter(F,budget,k,deadline):
    """Finite-region strict r-skyband, using pivot order instead of an R-tree."""
    n=F[0].shape[1];raw=sum(f[0] for f in F)
    order=np.lexsort((np.arange(n),-raw));kept=[];ancestors={};rejected=[];tests=0
    for j in order.tolist():
        guard(deadline);dominators=[];gaps=[]
        eligible=[i for i in kept if raw[i]>raw[j]]
        for offset in range(0,len(eligible),32):
            guard(deadline);block=eligible[offset:offset+32]
            minimum=minimum_margins(F,block,j,budget);tests+=len(block)
            for i,gap in zip(block,minimum.tolist()):
                if gap>0:dominators.append(i);gaps.append(gap)
            if len(dominators)>=k:break
        if len(dominators)>=k:
            rejected.append({'document':j,'dominators':dominators[:k],'minimumMargins':gaps[:k]})
        else:
            ancestors[j]=dominators;kept.append(j)
    return kept,ancestors,{'strictDominanceTests':tests,'rejected':rejected}


def score_states(F,states,max_cells=50_000_000):
    n=F[0].shape[1]
    if len(states)*n>max_cells:raise ResourceCap('state_score_cells')
    choices=np.asarray(states,dtype=int);scores=np.zeros((len(states),n),dtype=np.int64)
    for i,f in enumerate(F):scores+=f[choices[:,i]]
    return scores


def rsa_arrangements(scores,ancestors,k,deadline,node_cap=1_000_000):
    """Candidate-specific finite half-space cells; regional ancestors + drills."""
    states,n=scores.shape;witnesses={};drill_cache={};comparisons=0;nodes=0
    def drill(s):
        if s not in drill_cache:
            cut=np.partition(scores[s],-k)[-k]
            drill_cache[s]=np.flatnonzero(scores[s]>=cut).tolist()
        for j in drill_cache[s]:witnesses.setdefault(j,s)
    drill(0)
    order=sorted(range(n),key=lambda j:(-len(ancestors[j]),j))
    competitors=sorted(range(n),key=lambda j:(len(ancestors[j]),j))
    for j in order:
        guard(deadline)
        if j in witnesses:continue
        certain=set(ancestors[j]);count=np.full(states,len(certain),dtype=np.int32)
        active=np.ones(states,dtype=bool)
        for c in competitors:
            if c==j or c in certain:continue
            guard(deadline);nodes+=1
            if nodes>node_cap:raise ResourceCap('arrangement_nodes')
            live=np.flatnonzero(active);comparisons+=len(live)
            count[live]+=scores[live,c]>scores[live,j]
            active[live[count[live]>=k]]=False
            live=np.flatnonzero(active)
            if not len(live):break
            drill(int(live[0]))
            if j in witnesses:break
        if j not in witnesses and active.any():witnesses[j]=int(np.flatnonzero(active)[0])
        if j in witnesses:
            for a in certain:witnesses.setdefault(a,witnesses[j])
    return sorted(witnesses),{'witnesses':witnesses,'drilledStates':len(drill_cache),
                              'stateComparisons':comparisons,'arrangementNodes':nodes}


def jaa_arrangements(scores,k,deadline,node_cap=1_000_000):
    """Shared finite arrangement, kth pivot anchor and explicit equality cells."""
    count,n=scores.shape;stack=[(np.arange(count),np.arange(n),k,())]
    cells=[];union=set();nodes=0;comparisons=0
    while stack:
        guard(deadline);rows,candidates,quota,prefix=stack.pop();nodes+=1
        if nodes>node_cap:raise ResourceCap('arrangement_nodes')
        if len(candidates)<quota:raise AssertionError('Invalid remaining rank quota')
        if len(candidates)==quota:
            top=sorted(set(prefix)|set(candidates.tolist()))
            cells.append({'states':rows.tolist(),'top':top});union.update(top);continue
        pivot=scores[rows[0],candidates]
        anchor=int(candidates[np.lexsort((candidates,-pivot))[quota-1]])
        selected=scores[np.ix_(rows,candidates)];a=scores[rows,anchor,None]
        signs=(selected>a).astype(np.int8)-(selected<a).astype(np.int8)
        patterns,inverse=np.unique(signs,axis=0,return_inverse=True)
        comparisons+=int(signs.size)
        for group,pattern in enumerate(patterns):
            region=rows[inverse==group]
            higher=candidates[pattern>0];equal=candidates[pattern==0];lower=candidates[pattern<0]
            if len(higher)>=quota:
                stack.append((region,higher,quota,prefix))
            elif len(higher)+len(equal)>=quota:
                top=sorted(set(prefix)|set(higher.tolist())|set(equal.tolist()))
                cells.append({'states':region.tolist(),'top':top});union.update(top)
            else:
                known=prefix+tuple(higher.tolist())+tuple(equal.tolist())
                stack.append((region,lower,quota-len(higher)-len(equal),known))
    return sorted(union),{'cells':cells,'arrangementNodes':nodes,'stateComparisons':comparisons}


def finite_union(F,budget,k,method,deadline=None,max_cells=50_000_000,node_cap=1_000_000):
    if deadline is None:deadline=time.perf_counter()+120.
    if not F or method not in ['rsa_fd','jaa_fd']:raise ValueError('Invalid factors/method')
    n=F[0].shape[1]
    if not 1<=k<=n or budget<0:raise ValueError('Invalid k/budget')
    for f in F:
        if f.ndim!=2 or f.shape[1]!=n or not len(f) or f.dtype.kind not in 'iu':raise ValueError('Integer factors required')
        if max(abs(int(f.min())),abs(int(f.max())))*max(1,len(F))*4>=2**62:raise OverflowError('Unsafe integer range')
    try:
        kept,ancestors,proof=regional_filter(F,budget,k,deadline)
        local={j:i for i,j in enumerate(kept)}
        graph={local[j]:[local[a] for a in ancestors[j]] for j in kept}
        states=states_for([len(f) for f in F],budget)
        scores=score_states([f[:,kept] for f in F],states,max_cells)
        if method=='rsa_fd':union,detail=rsa_arrangements(scores,graph,k,deadline,node_cap)
        else:union,detail=jaa_arrangements(scores,k,deadline,node_cap)
        detail.update({'status':'exact','survivors':kept,'filter':proof,'states':states,
                       'survivorFactors':[f[:,kept].tolist() for f in F]})
        return [kept[j] for j in union],detail
    except ResourceCap as e:
        return list(range(n)),{'status':'resource_unknown','reason':str(e)}
