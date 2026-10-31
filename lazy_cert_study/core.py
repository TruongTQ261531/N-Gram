"""Integer-safe index-first projection before full token-factor scoring.

This implements established nonnegative feature envelopes and anchor bounds.
It is a correctness/performance experiment, not an originality assertion.
"""
import os
for _key in ('OPENBLAS_NUM_THREADS', 'OMP_NUM_THREADS', 'MKL_NUM_THREADS'):
    os.environ[_key] = '1'

from collections import Counter
from dataclasses import dataclass
from pathlib import Path
import sys
import time

import numpy as np
from scipy import sparse

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from pool_study.core import compact_forms, normalize


@dataclass
class Lattice:
    forms: list
    feature_rows: sparse.csr_matrix
    mappings: list
    types: list
    raw_features: sparse.csr_matrix
    words: list


def lattice(index, text):
    tokens = normalize(text).split()
    if not tokens:
        raise ValueError('An empty query has no token lattice')
    form_cache = {t: compact_forms(t) for t in dict.fromkeys(tokens)}
    forms = [form_cache[t] for t in tokens]
    words = list(dict.fromkeys(f['text'] for fs in forms for f in fs))
    lookup = {t: i for i, t in enumerate(words)}
    mappings = [np.array([lookup[f['text']] for f in fs], dtype=int) for fs in forms]
    counts = Counter(tokens)
    types = []
    seen = set()
    for token, mapping in zip(tokens, mappings):
        if token not in seen:
            types.append((mapping, counts[token]))
            seen.add(token)
    X = index.vectorizer.transform(words).tocsr()
    maximum=getattr(index,'_certificate_max_weight',None)
    if maximum is None:
        maximum=int(index.weights.data.max(initial=0))
        index._certificate_max_weight=maximum
    lengths=np.asarray(X.sum(axis=1)).ravel()
    bound=sum(int(lengths[mapping].max(initial=0))*multiplicity
              for mapping,multiplicity in types)*maximum
    if bound>=np.iinfo(np.int64).max//64:
        raise OverflowError('Integer score envelope exceeds the safe range')
    raw_counts = np.bincount([m[0] for m in mappings], minlength=len(words))
    raw = (sparse.csr_matrix(raw_counts[None, :]) @ X).tocsr()
    return Lattice(forms, X, mappings, types, raw, words)


def _insert(top, values, multiplicity):
    """Insert repeated nonnegative gains into coordinatewise top-B arrays."""
    for _ in range(min(multiplicity, len(top))):
        carry = values.copy()
        for row in range(len(top)):
            old = top[row].copy()
            top[row] = np.maximum(old, carry)
            carry = np.minimum(old, carry)


def upper_features(Q, budget):
    columns = np.unique(Q.feature_rows.indices)
    local = Q.feature_rows[:, columns].tocsr()
    top = np.zeros((budget, len(columns)), dtype=np.int64)
    if budget:
        for mapping, multiplicity in Q.types:
            rows = local[mapping]
            delta = (rows.max(axis=0).tocsr() - rows[0]).tocsr()
            delta.eliminate_zeros()
            if np.any(delta.data < 0):
                raise AssertionError('Raw option must be included in the maximum')
            active = delta.indices
            temporary = top[:, active].copy()
            _insert(temporary, delta.data, multiplicity)
            top[:, active] = temporary
    gains = top.sum(axis=0)
    addition = sparse.csr_matrix((gains, (np.zeros(len(columns), dtype=int), columns)),
                                 shape=Q.raw_features.shape)
    return (Q.raw_features + addition).tocsr()


def feature_projection(index, columns, documents):
    """Ordinary sparse submatrix extraction: omit unrelated vocabulary rows.

    Preserve the original integer weights; never refit on the selected docs.
    """
    return index.transpose[columns][:,documents].tocsr()


def screen(index, text, budget=2, k=10, anchors=20, prepared=None):
    """Return a whole-corpus safe superset BEFORE dense form scoring.

    The feature envelope may combine incompatible feature choices, which only
    loosens its upper bound. Anchor minima retain the original token budget.
    """
    started = time.perf_counter()
    if not 1 <= k <= index.n or budget < 0:
        raise ValueError('Invalid k or budget')
    Q = lattice(index, text) if prepared is None else prepared
    built = time.perf_counter()
    upper = upper_features(Q, budget)
    maximum = getattr(index, '_certificate_max_weight', None)
    if maximum is None:
        maximum = int(index.weights.data.max(initial=0))
        index._certificate_max_weight = maximum
    guard = maximum * int(upper.sum())
    if guard >= np.iinfo(np.int64).max // 64:
        raise OverflowError('Integer score envelope exceeds the safe range')
    raw_scores = (Q.raw_features @ index.transpose).toarray()[0]
    high = (upper @ index.transpose).toarray()[0]
    scored = time.perf_counter()
    count = min(index.n, max(k, anchors))
    selected = np.argpartition(raw_scores, -count)[-count:]
    selected = selected[np.lexsort((selected, -raw_scores[selected]))]
    columns=np.unique(Q.feature_rows.indices)
    values = (Q.feature_rows[:,columns] @ feature_projection(index,columns,selected)).toarray()
    losses = np.zeros((budget, count), dtype=np.int64)
    for mapping, multiplicity in Q.types:
        drop = values[mapping[0]] - values[mapping].min(axis=0)
        _insert(losses, drop, multiplicity)
    lower = raw_scores[selected] - losses.sum(axis=0)
    threshold = int(np.partition(lower, -k)[-k])
    pool = np.flatnonzero(high >= threshold)
    if len(pool) < k:
        raise AssertionError('A safe pool cannot contain fewer than k documents')
    finished = time.perf_counter()
    proof = {
        'budget': budget, 'k': k, 'anchors': selected.tolist(),
        'anchorLower': lower.tolist(), 'threshold': threshold,
        'upperScores': high, 'rawScores': raw_scores,
        'tokens': len(Q.forms), 'uniqueForms': len(Q.words),
        'documents': index.n, 'coarsePool': len(pool),
        'featureSeconds': built-started,
        'upperScoreSeconds': scored-built,
        'anchorSeconds': finished-scored,
        'seconds': finished-started,
        'anchorScoreCells': int(values.size),
        'fullFactorScoreCells': len(Q.words)*index.n,
    }
    return pool, Q, proof


def materialize(index, Q, documents):
    """Score all required forms only on the already certified projection."""
    documents = np.asarray(documents, dtype=int)
    if len(documents)==index.n and np.array_equal(documents,np.arange(index.n)):
        values=(Q.feature_rows @ index.transpose).toarray()
    else:
        columns=np.unique(Q.feature_rows.indices)
        values=(Q.feature_rows[:,columns] @ feature_projection(index,columns,documents)).toarray()
    F = [values[m] for m in Q.mappings]
    return F, int(values.size)


def zero_witness(Q, budget):
    """Standard all-zero/tie shortcut; shared by both certificate controls."""
    costs=0;state=[]
    nnz=np.diff(Q.feature_rows.indptr)
    for mapping in Q.mappings:
        eligible=np.flatnonzero(nnz[mapping]==0)
        if not len(eligible):return None
        choice=int(eligible[0]);costs+=int(choice!=0);state.append(choice)
    return state if costs<=budget else None


def topk(scores, k):
    threshold = np.partition(scores, -k)[-k]
    return np.flatnonzero(scores >= threshold)


class IncrementalScorer:
    """Strong standard control: memoized sparse token-count delta scoring.

    This is ordinary incremental computation, not a novelty claim. It does
    not require that a request belongs to a preselected finite edit lattice.
    """
    def __init__(self, index, text, k=10, base_scores=None):
        self.index = index
        self.k = k
        self.base = Counter(normalize(text).split())
        self.scores = index.score(text) if base_scores is None else np.asarray(base_scores)
        self.memo = {}

    def query(self, text):
        text = normalize(text)
        if text in self.memo:
            return self.memo[text]
        now = Counter(text.split())
        words = [t for t in self.base.keys() | now.keys() if now[t] != self.base[t]]
        if words:
            coefficients = np.array([now[t]-self.base[t] for t in words], dtype=np.int64)
            features = self.index.vectorizer.transform(words)
            delta = sparse.csr_matrix(coefficients[None, :]) @ features
            scores = self.scores + (delta @ self.index.transpose).toarray()[0]
        else:
            scores = self.scores
        result = topk(scores, self.k)
        self.memo[text] = result
        return result
