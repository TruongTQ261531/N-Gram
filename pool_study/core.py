"""Safe possible-top-k pools for finite shared query edits.

This is a candidate implementation of established interval/dominance/partition
ideas, not a claim that possible top-k or branch-and-bound is new.
All guarantees concern the stored integer scorer and the declared finite lattice.
"""
import os
for _name in ('OMP_NUM_THREADS', 'OPENBLAS_NUM_THREADS', 'MKL_NUM_THREADS', 'NUMEXPR_NUM_THREADS'):
    os.environ[_name] = '1'
from collections import Counter
import hashlib
import itertools
import unicodedata
import numpy as np
from sklearn.feature_extraction.text import CountVectorizer

SCALE = 1_000_000
VERSION = 'ngram-pool-integer-v1'

def normalize(text):
    return ' '.join(unicodedata.normalize('NFC', str(text)).lower().split())

def grams(text):
    for token in normalize(text).split():
        s = ' ' + token + ' '
        for n in (3, 4, 5):
            for i in range(len(s) - n + 1):
                yield s[i:i+n]

def compact_forms(token):
    """Three deterministic edits, selected by hash without corpus/labels/scores.

    One deletion, one adjacent swap and one QWERTY-neighbor replacement when
    available. This compact channel is NOT the exhaustive original keyboard set.
    """
    found = {}
    coords = {c:(j+off,i) for i,(row,off) in enumerate(
        [('qwertyuiop',0),('asdfghjkl',.3),('zxcvbnm',.7)]) for j,c in enumerate(row)}
    candidates = {'delete':[], 'swap':[], 'keyboard':[]}
    for i,c in enumerate(token):
        candidates['delete'].append((token[:i]+token[i+1:], {'op':'delete','position':i}))
        if i+1 < len(token):
            candidates['swap'].append((token[:i]+token[i+1]+c+token[i+2:], {'op':'swap','position':i}))
        if c in coords:
            a,b = coords[c]
            for z,(x,y) in coords.items():
                if z != c and (x-a)**2+(y-b)**2 <= 1.6**2:
                    candidates['keyboard'].append((token[:i]+z+token[i+1:], {'op':'keyboard','position':i,'replacement':z}))
    for op, values in candidates.items():
        eligible = [(text,trace) for text,trace in values if text != token]
        if eligible:
            text,trace = min(eligible, key=lambda x:hashlib.sha256((token+'|'+op+'|'+x[0]).encode()).digest())
            found.setdefault(text, trace)
    return [{'text':token,'op':'raw'}]+[{'text':s,**found[s]} for s in sorted(found)]

class Index:
    def __init__(self, documents):
        self.documents = sorted(documents, key=lambda d:str(d['id']))
        self.ids = [str(d['id']) for d in self.documents]
        assert len(self.ids) == len(set(self.ids))
        self.vectorizer = CountVectorizer(analyzer=grams, dtype=np.int64)
        counts = self.vectorizer.fit_transform([d.get('title','')+' '+d['text'] for d in self.documents]).tocsr()
        self.n = len(self.ids)
        lengths = np.asarray(counts.sum(axis=1)).ravel()
        df = np.bincount(counts.indices, minlength=counts.shape[1])
        idf = np.log1p((self.n-df+.5)/(df+.5))
        weights = counts.astype(np.float64)
        denominator = 1.2*(.25+.75*lengths/max(float(lengths.mean()),1e-30))
        weights.data = weights.data*2.2/(weights.data+np.repeat(denominator,np.diff(weights.indptr)))*idf[weights.indices]
        # The rounded integers, not the underlying floating formula, define S.
        weights.data = np.floor(weights.data*SCALE+.5).astype(np.int64)
        self.weights = weights.astype(np.int64)
        self.transpose = self.weights.T.tocsr()
        h = hashlib.sha256()
        for a in (self.weights.indptr, self.weights.indices, self.weights.data):
            h.update(a.astype('<i8').tobytes())
        h.update('\n'.join(self.ids).encode())
        h.update('\n'.join(self.vectorizer.get_feature_names_out()).encode())
        self.model_hash = h.hexdigest()

    def score(self, text):
        return (self.vectorizer.transform([text])@self.transpose).toarray()[0]

    def factors(self, query, max_tokens=16):
        original = normalize(query).split()
        tokens = original[:max_tokens]
        assert tokens
        forms = [compact_forms(t) for t in tokens]
        F = [(self.vectorizer.transform([s['text'] for s in fs])@self.transpose).toarray() for fs in forms]
        # Bounds below may sum +/- differences and anchors. Reject overflow.
        guard = sum(int(np.abs(f).max()) for f in F)
        assert guard < np.iinfo(np.int64).max//32
        return forms,F,{'originalTokens':len(original),'usedTokens':len(tokens),'truncated':len(original)>len(tokens),'maxScoreBound':guard}

def choices(sizes,budget):
    for cost in range(min(len(sizes),budget)+1):
        for positions in itertools.combinations(range(len(sizes)),cost):
            for alts in itertools.product(*(range(1,sizes[t]) for t in positions)):
                a = [0]*len(sizes)
                for t,v in zip(positions,alts):
                    a[t] = v
                yield a

def top_sum(gains,budget):
    if not gains or budget == 0:
        return np.zeros_like(gains[0]) if gains else 0
    return np.sort(np.maximum(np.stack(gains),0),axis=0)[-budget:].sum(axis=0)

def envelopes(F,budget,fixed=None):
    fixed = fixed or {}
    n = F[0].shape[1]
    base = np.zeros(n,dtype=np.int64)
    gains,losses = [],[]
    remaining = budget-sum(a != 0 for a in fixed.values())
    assert remaining >= 0
    for t,f in enumerate(F):
        if t in fixed:
            base += f[fixed[t]]
        else:
            base += f[0]
            gains.append(f.max(axis=0)-f[0])
            losses.append(f[0]-f.min(axis=0))
    return base-top_sum(losses,remaining),base+top_sum(gains,remaining)

def interval_pool(F,budget,k,fixed=None):
    lower,upper = envelopes(F,budget,fixed)
    threshold = np.partition(lower,-k)[-k]
    # Including all boundary ties is deliberately conservative.
    return np.flatnonzero(upper >= threshold)

def dominance_pool(F,budget,k,initial,anchors):
    n = F[0].shape[1]
    dominates = np.zeros(n,dtype=np.int32)
    active = np.asarray(initial,dtype=int)
    for anchor in anchors:
        if not len(active):
            break
        base = np.zeros(len(active),dtype=np.int64)
        gains = []
        for f in F:
            delta = f[:,active]-f[:,anchor,None]
            base += delta[0]
            gains.append(delta.max(axis=0)-delta[0])
        max_margin = base+top_sum(gains,budget)
        dominates[active] += max_margin < 0
        active = active[dominates[active] < k]
    return active

def partition_pool(F,budget,k,initial,depth=2,adaptive=True):
    """Intersect initial pool with union of conditional interval pools.

    All assignments of the selected original token(s) are covered. No sample is
    used as a certificate. Depth zero returns the initial safe fallback.
    """
    initial = np.asarray(initial,dtype=int)
    if adaptive:
        priority = sorted(range(len(F)),key=lambda t:(-int((F[t].max(axis=0)-F[t].min(axis=0)).max()),t))
    else:
        priority = list(range(len(F)))
    selected = priority[:depth]
    keep = np.zeros(F[0].shape[1],dtype=bool)
    leafs = []
    for vals in itertools.product(*(range(len(F[t])) for t in selected)):
        fixed = dict(zip(selected,vals))
        if sum(v != 0 for v in vals) > budget:
            continue
        pool = np.intersect1d(initial,interval_pool(F,budget,k,fixed),assume_unique=True)
        keep[pool] = True
        leafs.append({'fixed':[[t,int(a)] for t,a in fixed.items()],'pool':pool.tolist()})
    return np.flatnonzero(keep),{'splitTokens':selected,'leaves':leafs}

def candidate_pools(F,budget,k,include_fixed=True):
    raw = sum(f[0] for f in F)
    order = np.lexsort((np.arange(len(raw)),-raw))
    anchors = order[:min(len(raw),max(20,2*k))]
    independent = interval_pool(F,budget,k)
    coupled = dominance_pool(F,budget,k,independent,anchors)
    proposed,proof = partition_pool(F,budget,k,coupled,depth=2)
    pools = {'independent':independent,'coupled':coupled,'partitioned':proposed}
    traces = {'anchors':anchors.tolist(),'adaptive':proof}
    if include_fixed:
        fixed,fixed_proof = partition_pool(F,budget,k,coupled,depth=2,adaptive=False)
        pools['fixedPartition'] = fixed
        traces['fixed'] = fixed_proof
    return pools,traces

def oracle(F,budget,ks=(5,10),collect=True):
    raw = sum(f[0] for f in F)
    pools = {k:set() for k in ks}
    traces = []
    for a in choices([len(f) for f in F],budget):
        score = raw.copy()
        for t,v in enumerate(a):
            if v:
                score += F[t][v]-F[t][0]
        per = {}
        for k in ks:
            threshold = np.partition(score,-k)[-k]
            top = np.flatnonzero(score >= threshold).tolist()
            pools[k].update(top)
            per[str(k)] = top
        if collect:
            traces.append({'choices':a,'topKWithTies':per})
    return {k:sorted(v) for k,v in pools.items()},traces
