from fractions import Fraction
import unittest
import numpy as np
from scipy import sparse
from reviewer_audit_2026_10_31.bridge_refinement import exact_topk,exact_reference_rank,dyadic_sum


class TestExactBoundary(unittest.TestCase):
    def test_dyadic_sum_against_fraction_oracle(self):
        values=[0.,1/3,np.nextafter(1.,np.inf),1e-200,20.0000000001]
        counts=[2,3,7,2,1]
        gold=sum((Fraction.from_float(float(v))*c for v,c in zip(values,counts)),Fraction(0))
        self.assertEqual(dyadic_sum(values,counts),gold)

    def test_complete_rank_and_ties_against_exact_all_document_sums(self):
        rng=np.random.default_rng(20261031)
        for _ in range(80):
            W=rng.choice([0.,1/3,1.,np.nextafter(1.,np.inf),2.],size=(5,30))
            counts=rng.integers(1,4,size=5)
            X=sparse.csr_matrix(counts[None,:]);T=sparse.csr_matrix(W)
            z=(X@T).toarray()[0]
            gold=[sum((Fraction.from_float(float(W[g,j]))*int(counts[g]) for g in range(5)),Fraction(0)) for j in range(30)]
            cut=sorted(gold,reverse=True)[9]
            expected=[j for j,value in enumerate(gold) if value>=cut]
            answer,exact,_=exact_topk(T,X,z,10)
            self.assertTrue(exact);self.assertEqual(answer.tolist(),expected)
            for reference in [0,5,29]:
                interval,_=exact_reference_rank(T,X,z,reference)
                rank=sum(v>=gold[reference] for v in gold)
                self.assertEqual(interval,(rank,rank))

    def test_cap_returns_unknown_instead_of_breaking_ties(self):
        X=sparse.csr_matrix([[1]]);T=sparse.csr_matrix(np.ones((1,300)))
        answer,exact,_=exact_topk(T,X,np.ones(300),10)
        self.assertFalse(exact);self.assertEqual(len(answer),300)

    def test_zero_query_is_exact_all_tie(self):
        X=sparse.csr_matrix((1,5));T=sparse.csr_matrix(np.ones((5,30)))
        answer,exact,_=exact_topk(T,X,np.zeros(30),10)
        self.assertTrue(exact);self.assertEqual(len(answer),30)
        self.assertEqual(exact_reference_rank(T,X,np.zeros(30),0)[0],(30,30))


if __name__=='__main__':unittest.main()
