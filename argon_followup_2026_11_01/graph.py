"""Exact coloring and max clique on the COMPATIBILITY complement graph."""
import time


def complement(n, conflict_edges):
    mask=(1<<n)-1; adj=[mask^(1<<i) for i in range(n)]
    for i,j in conflict_edges:
        adj[i]&=~(1<<j);adj[j]&=~(1<<i)
    return adj


def greedy(adj):
    colors={}; groups=[]; left=set(range(len(adj)))
    while left:
        v=max(left,key=lambda x:(len({colors[u] for u in colors if (adj[x]>>u)&1}),adj[x].bit_count(),-x))
        used={colors[u] for u in colors if (adj[v]>>u)&1}
        c=next(k for k in range(len(groups)+1) if k not in used)
        if c==len(groups):groups.append([])
        colors[v]=c;groups[c].append(v);left.remove(v)
    return groups


def maximum_clique(adj, seconds=5.):
    start=time.perf_counter();best=[];nodes=0;complete=True
    def order(p):
        vertices=[];bounds=[];color=0
        while p:
            color+=1;q=p
            while q:
                bit=q&-q;v=bit.bit_length()-1;p^=bit
                vertices.append(v);bounds.append(color);q&=~bit;q&=~adj[v]
        return vertices,bounds
    def visit(current,p):
        nonlocal best,nodes
        nodes+=1
        if time.perf_counter()-start>seconds:raise TimeoutError
        vertices,bounds=order(p)
        for i in range(len(vertices)-1,-1,-1):
            if len(current)+bounds[i]<=len(best):return
            v=vertices[i];q=p&adj[v]
            if q:visit(current+[v],q)
            elif len(current)+1>len(best):best=current+[v]
            p&=~(1<<v)
    try:visit([],(1<<len(adj))-1)
    except TimeoutError:complete=False
    return {'clique':best,'size':len(best),'optimal':complete,'nodes':nodes,'seconds':time.perf_counter()-start}


def coloring(adj,lower=0,seconds=5.,initial=None):
    start=time.perf_counter();groups=initial if initial is not None else greedy(adj)
    best=[list(g) for g in groups];colors=[-1]*len(adj);nodes=0;complete=True
    def visit(left,classes,masks):
        nonlocal best,nodes
        nodes+=1
        if time.perf_counter()-start>seconds:raise TimeoutError
        if len(best)<=lower:return
        if not left:
            if len(classes)<len(best):best=[g.copy() for g in classes]
            return
        candidates=[i for i in range(len(adj)) if (left>>i)&1]
        v=max(candidates,key=lambda x:(sum(bool(adj[x]&m) for m in masks),adj[x].bit_count(),-x))
        rest=left&~(1<<v)
        for c,mask in enumerate(masks):
            if not (adj[v]&mask):
                classes[c].append(v);masks[c]|=1<<v;visit(rest,classes,masks)
                masks[c]&=~(1<<v);classes[c].pop()
        if len(classes)+1<len(best):visit(rest,classes+[[v]],masks+[1<<v])
    try:visit((1<<len(adj))-1,[],[])
    except TimeoutError:complete=False
    return {'groups':best,'colors':len(best),'optimal':complete or len(best)<=lower,'nodes':nodes,'seconds':time.perf_counter()-start}
