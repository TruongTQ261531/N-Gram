import itertools,unittest
import numpy as np
from argon_followup_2026_11_01.graph import maximum_clique,coloring,greedy


class GraphTests(unittest.TestCase):
    def test_first_fit_query_graph_last_representative_lemma(self):
        from unittest.mock import patch
        from reviewer_audit_2026_10_31.retention import cover_bound
        from argon_followup_2026_11_01.schedule_certificate import certificate
        rng=np.random.default_rng(127)
        for _ in range(120):
            n=int(rng.integers(2,14));edges=rng.random((n,n))<.5
            factors=[np.arange(n,dtype=float)[None,:]]
            def oracle(d,u,budget):
                i,j=map(int,d[0][0]);return {'incompatible':bool(edges[min(i,j),max(i,j)])}
            cap=int(rng.integers(0,n*(n-1)//2+1))
            with patch('compatibility.incompatible',side_effect=oracle):
                graph=cover_bound(factors,factors,2,cap,80)
            witness=certificate(graph['groups'],graph['checks'])
            self.assertEqual(len(witness['compatibleCliqueWitness']),graph['count_upper'])

    def test_label_free_refinement_certificate(self):
        from argon_followup_2026_11_01.refine import pairwise_refine
        D=[np.array([[1.,-1.],[-1.,1.]])]
        result=pairwise_refine(D,D,3,budget=1,k=2)
        self.assertEqual(result['rankUpper'],2)
        self.assertFalse(result['usesVerifiedLabels'])
        self.assertEqual(result['status'],'complete_pairs')

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

    def test_pair_proofs_never_underestimate_joint_lattice_count(self):
        from reviewer_audit_2026_10_31.retention import context
        from compatibility import incompatible
        from argon_followup_2026_11_01.graph import complement
        rng=np.random.default_rng(44)
        for _ in range(20):
            factors=[rng.integers(-5,6,(3,6)).astype(float) for t in range(3)]
            edges=[]
            for i,j in itertools.combinations(range(6),2):
                local=[f[:,[i,j]] for f in factors]
                if incompatible(local,local,2)['incompatible']:edges.append((i,j))
            adj=complement(6,edges);w=maximum_clique(adj);c=coloring(adj,w['size'])
            actual=max(int((sum(f[s] for f,s in zip(factors,state))>=0).sum())
                       for state in itertools.product(range(3),repeat=3) if sum(s!=0 for s in state)<=2)
            self.assertGreaterEqual(w['size'],actual);self.assertGreaterEqual(c['colors'],actual)


if __name__=='__main__':unittest.main()
