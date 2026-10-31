import itertools,unittest
import numpy as np
from argon_followup_2026_11_01.graph import maximum_clique,coloring,greedy


class GraphTests(unittest.TestCase):
    def test_cycle_separates_cover_from_pairwise_clique_bound(self):
        adj=[(1<<((i+1)%5))|(1<<((i-1)%5)) for i in range(5)]
        w=maximum_clique(adj);c=coloring(adj,lower=w['size'])
        self.assertTrue(w['optimal'] and c['optimal'])
        self.assertEqual(w['size'],2);self.assertEqual(c['colors'],3)

    def test_random_graphs_against_bruteforce(self):
        rng=np.random.default_rng(20261101)
        for _ in range(40):
            n=7;adj=[0]*n
            for i,j in itertools.combinations(range(n),2):
                if rng.random()<.5:adj[i]|=1<<j;adj[j]|=1<<i
            omega=max(len(s) for k in range(n+1) for s in itertools.combinations(range(n),k)
                      if all((adj[i]>>j)&1 for i,j in itertools.combinations(s,2)))
            def valid(c):return all(c[i]!=c[j] for i,j in itertools.combinations(range(n),2) if (adj[i]>>j)&1)
            chi=next(k for k in range(1,n+1) if any(valid(c) for c in itertools.product(range(k),repeat=n)))
            w=maximum_clique(adj);c=coloring(adj,lower=w['size'])
            self.assertTrue(w['optimal'] and c['optimal']);self.assertEqual(w['size'],omega);self.assertEqual(c['colors'],chi)


if __name__=='__main__':unittest.main()
