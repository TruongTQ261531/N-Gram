"""Exact one-dimensional score-hull oracle and lossless endpoint embedding."""
from fractions import Fraction
import hashlib
import json
import numpy as np


def selected_state(states, query_id):
    choices = [list(s) for s in states if any(s)]
    if not choices:
        raise ValueError('No nonraw state')
    def key(s):
        encoded = json.dumps(s, separators=(',', ':'))
        return hashlib.sha256(('utk-segment-v1|' + query_id + '|' + encoded).encode()).digest()
    return min(choices, key=key)


def safe_pool(a, b, k):
    a = np.asarray(a, dtype=np.int64); b = np.asarray(b, dtype=np.int64)
    low = np.minimum(a, b); high = np.maximum(a, b)
    threshold = int(np.partition(low, -k)[-k])
    pool = np.flatnonzero(high >= threshold)
    excluded = high[high < threshold]
    return pool, {'threshold': threshold,
                  'maximumExcludedUpper': int(excluded.max()) if len(excluded) else None,
                  'excluded': len(a) - len(pool)}


def endpoints(a, b, k):
    def top(x):
        cut = np.partition(x, -k)[-k]
        return set(np.flatnonzero(x >= cut).tolist())
    return sorted(top(np.asarray(a)) | top(np.asarray(b)))


def segment_union(a, b, k):
    """Exact possible top-k, INCLUDING ties; A/B are arbitrary signed integers."""
    a = [int(x) for x in a]; b = [int(x) for x in b]
    if len(a) != len(b) or not 1 <= k <= len(a):
        raise ValueError('Invalid endpoints/k')
    n = len(a)
    cut0 = sorted(a, reverse=True)[k-1]; cut1 = sorted(b, reverse=True)[k-1]
    result = {j: [0, 1] for j in range(n) if a[j] >= cut0}
    result.update({j: [1, 1] for j in range(n) if b[j] >= cut1 and j not in result})
    for j in range(n):
        if j in result: continue
        events = {}; count = 0
        for i in range(n):
            d0 = a[i] - a[j]; d1 = b[i] - b[j]
            # Count on the open interval immediately to the right of zero.
            count += int(d0 > 0 or (d0 == 0 and d1 > 0))
            if d0 * d1 < 0:
                t = Fraction(-d0, d1 - d0)
                leaving, entering = events.get(t, (0, 0))
                events[t] = (leaving + int(d0 > 0), entering + int(d0 < 0))
        for t, (leaving, entering) in sorted(events.items()):
            count -= leaving
            if count < k:
                result[j] = [t.numerator, t.denominator]; break
            count += entering
    return result


def embedding(a, b):
    """Return 24-bit grid coordinates and exact quantized endpoint scores.

    Prior to quantization, p0+3*p1=8*A+4*shift and
    3*p0+p1=8*B+4*shift, up to a common positive scale.
    """
    a = np.asarray(a, dtype=np.int64); b = np.asarray(b, dtype=np.int64)
    if max(np.abs(a).max(initial=0), np.abs(b).max(initial=0)) >= 2**49:
        raise OverflowError('Embedding needs exactly represented integer numerators')
    u = 3*b-a; v = 3*a-b
    shift = -min(0, int(u.min()), int(v.min()))
    maximum = max(int(u.max()) + shift, int(v.max()) + shift)
    power = max(1, maximum.bit_length())
    coords = np.rint(np.column_stack((u+shift, v+shift)) * (2.0**(24-power))).astype(np.int64)
    assert np.all((coords >= 0) & (coords <= 2**24))
    qa = coords[:, 0] + 3*coords[:, 1]
    qb = 3*coords[:, 0] + coords[:, 1]
    return coords, qa, qb, {'commonIntegerShift': shift, 'scalePower': power, 'gridBits': 24}


def point_text(coords):
    rows = []
    for i, (u, v) in enumerate(coords, 1):
        values = [float(u)/2**24, float(v)/2**24, float(v)/2**24]
        encoded = ' '.join(format(x, '.9g') for x in values)
        # Decimal round trip must preserve the intended native float32 values.
        assert np.array_equal(np.array(encoded.split(), dtype=np.float32), np.array(values, dtype=np.float32))
        rows.append(f'{i} {encoded} {encoded}\n')
    return ''.join(rows)
