"""Compiled safe projection and budgeted rank-effect quotients.

Candidate specialization; interval bounds, equivalence and symmetry reduction
are established ideas. No global originality or Q1 claim follows from this code.
"""
import os
for _key in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS','NUMEXPR_NUM_THREADS'):
    os.environ[_key]='1'
from pathlib import Path
import itertools,sys,time
import numpy as np
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'pool_study'))
import core as legacy

class CompiledBounds:
    def __init__(self,F,budget=2,depth=2):
        self.F=F;self.budget=budget;self.n=F[0].shape[1]
        self.raw=sum(f[0] for f in F)
        up=np.stack([f.max(0)-f[0] for f in F]);down=np.stack([f[0]-f.min(0) for f in F])
        self.priority=sorted(range(len(F)),key=lambda t:(-int((up[t]+down[t]).max()),t))
        m=min(len(F),budget+depth)
        def compile(g):
            idx=np.argpartition(g,-m,axis=0)[-m:];values=np.take_along_axis(g,idx,axis=0)
            order=np.argsort(-values,axis=0)
            return np.take_along_axis(values,order,axis=0),np.take_along_axis(idx,order,axis=0)
        self.up=compile(up);self.down=compile(down)

    def envelopes(self,fixed):
        remaining=self.budget-sum(a!=0 for a in fixed.values());assert remaining>=0
        base=self.raw.copy()
        for t,a in fixed.items():base+=self.F[t][a]-self.F[t][0]
        def gains(cache):
            values,indices=cache;allowed=np.ones_like(indices,dtype=bool)
            for t in fixed:allowed&=indices!=t
            # At most depth entries are removed; top(B+depth) suffices.
            masked=np.where(allowed,values,0)
            return np.sort(masked,axis=0)[-remaining:].sum(0) if remaining else np.zeros(self.n,dtype=np.int64)
        return base-gains(self.down),base+gains(self.up)

def compiled_pool(F,budget=2,k=10):
    start=time.perf_counter();C=CompiledBounds(F,budget,2)
    low,high=C.envelopes({});cut=np.partition(low,-k)[-k];independent=np.flatnonzero(high>=cut)
    anchors=np.lexsort((np.arange(C.n),-C.raw))[:min(C.n,max(20,2*k))]
    coupled=legacy.dominance_pool(F,budget,k,independent,anchors)
    selected=C.priority[:2];union=np.zeros(C.n,dtype=bool);leaves=[]
    for values in itertools.product(*(range(len(F[t])) for t in selected)):
        fixed=dict(zip(selected,values))
        if sum(v!=0 for v in values)>budget:continue
        lower,upper=C.envelopes(fixed);threshold=np.partition(lower,-k)[-k]
        pool=coupled[upper[coupled]>=threshold];union[pool]=True
        leaves.append({'fixed':[[int(t),int(a)] for t,a in fixed.items()],'pool':pool.tolist(),'threshold':int(threshold)})
    return np.flatnonzero(union),{'independent':independent.tolist(),'coupled':coupled.tolist(),'anchors':anchors.tolist(),'splitTokens':selected,'leaves':leaves,'seconds':time.perf_counter()-start}

def make_groups(F,pool,forms,mode='rank'):
    """Each nonzero rank effect costs1; min-cost raw-equivalent effects cost0.

    Group positions with identical available effect sets; multiplicity limits
    prevent spending two edits on the same original token.
    """
    assert mode in ('none','score','text','rank')
    groups=[];lookup={};width=len(pool)
    for t,f in enumerate(F):
        delta=f[:,pool]-f[0,pool]
        if mode=='rank':delta=delta-delta[:,0,None]
        if mode in ('rank','score'):
            unique={}
            for a in range(1,len(f)):
                if np.any(delta[a]):unique.setdefault(delta[a].astype('<i8').tobytes(),a)
            keys=sorted(unique);representatives=[unique[key] for key in keys]
            effects=np.stack([delta[a] for a in representatives]) if representatives else np.empty((0,width),dtype=np.int64)
        else:
            effects=delta[1:].copy();representatives=list(range(1,len(f)));keys=[v.astype('<i8').tobytes() for v in effects]
        if not len(effects):continue
        if mode=='rank':key=tuple(keys)
        elif mode=='text':key=(tuple(x['text'] for x in forms[t]),tuple(keys))
        else:key=('position',t)
        if key not in lookup:
            lookup[key]=len(groups);groups.append({'positions':[],'representatives':[],'effects':effects})
        g=groups[lookup[key]];g['positions'].append(t);g['representatives'].append(representatives)
    return groups

def state_count(groups,budget=2):
    q=[len(g['effects']) for g in groups];total=1+(sum(q) if budget else 0)
    if budget>=2:
        total+=sum(q[i]*q[j] for i in range(len(q)) for j in range(i+1,len(q)))
        total+=sum(n*(n+1)//2 for n,g in zip(q,groups) if len(g['positions'])>=2)
    return total

def descriptors(groups,budget=2):
    yield (-1,-1,-1,-1)
    if budget:
        for g,group in enumerate(groups):
            for a in range(len(group['effects'])):yield (g,a,-1,-1)
    if budget>=2:
        for g,G in enumerate(groups):
            for h in range(g+1,len(groups)):
                for a in range(len(G['effects'])):
                    for b in range(len(groups[h]['effects'])):yield (g,a,h,b)
            if len(G['positions'])>=2:
                for a in range(len(G['effects'])):
                    for b in range(a,len(G['effects'])):yield (g,a,g,b)

def representative(groups,descriptor):
    choices=[];usage={}
    for g,a in (descriptor[:2],descriptor[2:]):
        if g<0:continue
        used=usage.get(g,0);G=groups[g]
        choices.append([G['positions'][used],G['representatives'][used][a]])
        usage[g]=used+1
    return choices

def exact_from_pool(F,pool,forms,budget=2,k=10,mode='rank',max_states=2_000_000,max_cells=500_000_000,collect=False):
    start=time.perf_counter();pool=np.asarray(pool,dtype=int);groups=make_groups(F,pool,forms,mode);count=state_count(groups,budget)
    raw=sum(f[0,pool] for f in F);raw_top=raw>=np.partition(raw,-k)[-k]
    # A safe superset whose every member is already witnessed is the exact union.
    # Applied to every exact comparator, not credited exclusively to quotienting.
    if raw_top.all():
        result={'status':'exact','states':1,'theoreticalStates':count,'enumerationComplete':count==1,'termination':'pool_saturation','pool':pool.tolist(),'mode':mode,'groups':len(groups),'options':sum(len(g['effects']) for g in groups),'witnesses':{str(int(j)):[] for j in pool},'seconds':time.perf_counter()-start}
        proof={'descriptors':np.array([[-1,-1,-1,-1]],dtype=np.int32) if collect else None,'topKBits':np.packbits(raw_top[None,:],axis=1,bitorder='little') if collect else None,'groups':[{'positions':g['positions'],'representatives':g['representatives'],'effects':g['effects'].tolist()} for g in groups]}
        return result,proof
    if count>max_states or count*len(pool)>max_cells:
        return {'status':'resource_unknown','states':count,'pool':pool.tolist(),'mode':mode,'seconds':time.perf_counter()-start},None
    union=np.zeros(len(pool),dtype=bool);witnesses={};all_desc=[];all_bits=[];visited=0
    batch_size=max(1,min(2048,2_000_000//len(pool)))
    stream=iter(descriptors(groups,budget))
    while True:
        batch=list(itertools.islice(stream,batch_size))
        if not batch:break
        z=np.tile(raw,(len(batch),1))
        for row,(g,a,h,b) in enumerate(batch):
            if g>=0:z[row]+=groups[g]['effects'][a]
            if h>=0:z[row]+=groups[h]['effects'][b]
        thresholds=np.partition(z,-k,axis=1)[:,-k];top=z>=thresholds[:,None]
        new=np.flatnonzero(top.any(0)&~union)
        for j in new:
            row=int(np.flatnonzero(top[:,j])[0]);witnesses[str(int(pool[j]))]=representative(groups,batch[row])
        union|=top.any(0);visited+=len(batch)
        if collect:all_desc.append(np.asarray(batch,dtype=np.int32));all_bits.append(np.packbits(top,axis=1,bitorder='little'))
        if union.all():break
    assert visited==count or union.all()
    proof={'descriptors':np.concatenate(all_desc) if collect else None,'topKBits':np.concatenate(all_bits) if collect else None,
           'groups':[{'positions':g['positions'],'representatives':g['representatives'],'effects':g['effects'].tolist()} for g in groups]}
    result={'status':'exact','states':visited,'theoreticalStates':count,'enumerationComplete':visited==count,'termination':'complete_enumeration' if visited==count else 'pool_saturation','pool':pool[union].tolist(),'mode':mode,'groups':len(groups),'options':sum(len(g['effects']) for g in groups),'witnesses':witnesses,'seconds':time.perf_counter()-start}
    return result,proof
