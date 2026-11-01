import itertools,time,unittest
import numpy as np
from utk_full_domain_2026_11_01.algorithms import finite_union,states_for,score_states,minimum_margins


def brute(F,b,k):
    states=states_for([len(f) for f in F],b);score=score_states(F,states)
    tops=[set(np.flatnonzero(s>=np.partition(s,-k)[-k]).tolist()) for s in score]
    return set.union(*tops),tops


class TestFiniteUTK(unittest.TestCase):
    def check(self,F,b,k):
        expected,tops=brute(F,b,k)
        for method in ['rsa_fd','jaa_fd']:
            observed,detail=finite_union(F,b,k,method)
            self.assertEqual(detail['status'],'exact');self.assertEqual(set(observed),expected)
            kept=detail['survivors']
            for r in detail['filter']['rejected']:
                self.assertEqual(len(r['dominators']),k)
                self.assertTrue(all(x>0 for x in r['minimumMargins']))
            if method=='jaa_fd':
                seen=[]
                for cell in detail['cells']:
                    for state in cell['states']:
                        self.assertEqual({kept[j] for j in cell['top']},tops[state]);seen.append(state)
                self.assertEqual(sorted(seen),list(range(len(tops))))
            else:
                for j,state in detail['witnesses'].items():self.assertIn(kept[j],tops[state])

    def test_random_integer_factors_against_enumeration(self):
        rng=np.random.default_rng(20261101)
        for trial in range(60):
            F=[rng.integers(-5,8,size=(int(rng.integers(1,4)),7),dtype=np.int64) for _ in range(int(rng.integers(1,5)))]
            for b in [0,1,2]:self.check(F,b,1+trial%4)

    def test_finite_domain_does_not_add_fractional_winner(self):
        self.check([np.array([[4,0,3],[0,4,3]],dtype=np.int64)],1,1)
        for m in ['rsa_fd','jaa_fd']:
            u,_=finite_union([np.array([[4,0,3],[0,4,3]],dtype=np.int64)],1,1,m)
            self.assertEqual(set(u),{0,1})

    def test_all_boundary_ties_are_preserved(self):
        self.check([np.ones((3,8),dtype=np.int64)],1,2)
        self.check([np.array([[9,8,8,0],[0,8,8,9]],dtype=np.int64)],1,2)

    def test_budget_changes_joint_attainability(self):
        F=[np.array([[3,0,1],[0,2,1]],dtype=np.int64)]*2
        for b in [0,1,2]:self.check(F,b,1)

    def test_minimum_support_matches_all_finite_states(self):
        F=[np.array([[3,0,1],[0,2,1]],dtype=np.int64)]*3
        for b in [0,1,2,3]:
            score=score_states(F,states_for([2]*3,b))
            np.testing.assert_array_equal(minimum_margins(F,[0,1],2,b),(score[:,:2]-score[:,2,None]).min(axis=0))

    def test_caps_never_claim_exactness(self):
        F=[np.array([[4,0,3],[0,4,3]],dtype=np.int64)]
        for m in ['rsa_fd','jaa_fd']:
            for kwargs in [{'deadline':time.perf_counter()-1},{'max_cells':0},{'node_cap':0}]:
                u,d=finite_union(F,1,1,m,**kwargs)
                self.assertEqual(d['status'],'resource_unknown');self.assertEqual(u,[0,1,2])


if __name__=='__main__':unittest.main()
