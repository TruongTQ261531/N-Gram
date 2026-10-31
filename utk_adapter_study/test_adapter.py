import itertools
from fractions import Fraction
import unittest
import numpy as np
from utk_adapter_study.adapter import embedding, endpoints, point_text, safe_pool, segment_union


class AdapterTests(unittest.TestCase):
    def test_strict_interior_extra(self):
        a = [4, 0, 3]; b = [0, 4, 3]
        self.assertEqual(endpoints(a, b, 1), [0, 1])
        out = segment_union(a, b, 1)
        self.assertEqual(set(out), {0, 1, 2})
        t = Fraction(*out[2])
        self.assertLessEqual(max((1-t)*a[i]+t*b[i] for i in (0, 1)), 3)

    def test_simultaneous_crossings_and_persistent_ties(self):
        self.assertEqual(set(segment_union([4, 0, 2, 2], [0, 4, 2, 2], 1)), {0, 1, 2, 3})
        self.assertEqual(set(segment_union([0, 0, 0], [0, 0, 0], 1)), {0, 1, 2})

    def test_oracle_against_global_arrangement(self):
        rng = np.random.default_rng(20261101)
        for _ in range(80):
            a = rng.integers(-5, 6, 7); b = rng.integers(-5, 6, 7)
            k = int(rng.integers(1, 8)); times = {Fraction(0), Fraction(1)}
            for i, j in itertools.combinations(range(7), 2):
                d0 = int(a[i]-a[j]); d1 = int(b[i]-b[j])
                if d0 != d1:
                    t = Fraction(-d0, d1-d0)
                    if 0 <= t <= 1: times.add(t)
            ordered = sorted(times)
            times.update((x+y)/2 for x, y in zip(ordered, ordered[1:]))
            expected = set()
            for t in times:
                scores = [(1-t)*int(x)+t*int(y) for x, y in zip(a, b)]
                cut = sorted(scores, reverse=True)[k-1]
                expected.update(i for i, s in enumerate(scores) if s >= cut)
            self.assertEqual(set(segment_union(a, b, k)), expected)

    def test_screen_and_quantized_embedding(self):
        a = np.array([10, 0, 7, -20]); b = np.array([0, 10, 7, -20])
        pool, _ = safe_pool(a, b, 1)
        self.assertTrue(set(segment_union(a, b, 1)) <= set(pool))
        coords, qa, qb, meta = embedding(a, b)
        u = 3*b-a+meta['commonIntegerShift']; v = 3*a-b+meta['commonIntegerShift']
        np.testing.assert_array_equal(u+3*v, 8*a+4*meta['commonIntegerShift'])
        self.assertEqual(set(segment_union(a, b, 1)), set(segment_union(qa, qb, 1)))
        self.assertEqual(len(point_text(coords).splitlines()), 4)


if __name__ == '__main__': unittest.main()
