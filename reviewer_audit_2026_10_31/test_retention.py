from pathlib import Path
import itertools
import unittest
import warnings
import numpy as np
from reviewer_audit_2026_10_31.retention import kernel


def brute(D,budget):
    maximum=0
    for state in itertools.product(*(range(len(d)) for d in D)):
        if sum(a!=0 for a in state)>budget:continue
        score=sum(d[a] for d,a in zip(D,state))
        maximum=max(maximum,int((score>=0).sum()))
    return maximum+1


class TestRetentionSupplement(unittest.TestCase):
    def test_all_backends_against_small_exhaustive_rank(self):
        rng=np.random.default_rng(20261031)
        with warnings.catch_warnings():
            warnings.simplefilter('ignore')
            for _ in range(16):
                D=[rng.integers(-4,5,size=(3,5)).astype(float) for i in range(3)]
                for d in D:d[0]=-rng.integers(1,5,size=5)
                Du=[np.nextafter(d,np.inf) for d in D]
                lower=sum(d.min(axis=0) for d in D)
                gold=brute(D,2)
                for method in ['pair_enum','best_lp_enum','discrete','milp_enum']:
                    rank,detail=kernel(D,Du,lower,method)
                    self.assertGreaterEqual(rank,gold)
                    self.assertEqual(rank,gold)  # tiny enumeration completes for all controls

    def test_empty_competitor_set(self):
        D=[np.zeros((3,0)),np.zeros((2,0))]
        for method in ['pair_enum','best_lp_enum','discrete','milp_enum']:
            rank,_=kernel(D,D,np.array([]),method)
            self.assertEqual(rank,1)

    def test_archived_fixture_numerical_controls(self):
        root=Path(__file__).resolve().parents[1]/'round3/results/fixtures'
        with warnings.catch_warnings():
            warnings.simplefilter('ignore')
            for path in sorted(root.glob('*_b2.npz')):
                data=np.load(path);sizes=data['sizes'];offset=np.r_[0,np.cumsum(sizes)]
                D=[data['margins'][offset[i]:offset[i+1]] for i in range(len(sizes))]
                Du=[data['upper_margins'][offset[i]:offset[i+1]] for i in range(len(sizes))]
                for method in ['best_lp_enum','discrete','milp_enum']:
                    rank,detail=kernel(D,Du,data['lower'],method)
                    self.assertTrue(1<=rank<=D[0].shape[1]+1)
                    if method=='milp_enum' and detail['milp'].get('success'):
                        # A solved numerical relaxation cannot have a bound below its incumbent.
                        self.assertGreaterEqual(detail['milp']['count_upper']+1e-5,
                                                detail['milp'].get('feasible_count',0))


if __name__=='__main__':unittest.main()
