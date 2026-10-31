from fractions import Fraction
import unittest
import numpy as np
from reviewer_audit_2026_10_31.bridge import quantization_bound,transfer,SCALE


class TestBridge(unittest.TestCase):
    def test_quantizer_bound_against_exact_rationals(self):
        values=[]
        for integer in [0,1,10,100000,9999999,19999999]:
            midpoint=(integer+.5)/SCALE
            values.extend([np.nextafter(midpoint,-np.inf),midpoint,np.nextafter(midpoint,np.inf)])
        values.extend(np.random.default_rng(20261031).uniform(0,20,300))
        delta=Fraction.from_float(quantization_bound(max(values)))
        for value in values:
            rounded=int(np.floor(value*SCALE+.5))
            residual=abs(Fraction.from_float(float(value))-Fraction(rounded,SCALE))
            self.assertLessEqual(residual,delta)

    def test_rank_transfer_against_adversarial_weight_residuals(self):
        rng=np.random.default_rng(20261031);delta=quantization_bound(20)
        for _ in range(100):
            z=rng.integers(1,100000,size=30,dtype=np.int64)
            safe,answer,_=transfer(z,5,100,delta)
            if safe:
                for _ in range(10):
                    w=z/SCALE+rng.uniform(-100*delta,100*delta,size=30)
                    cut=np.partition(w,-5)[-5]
                    np.testing.assert_array_equal(np.flatnonzero(w>=cut),answer)

    def test_tied_boundary_is_unresolved(self):
        safe,answer,gap=transfer(np.array([10,9,9,8]),2,10,quantization_bound(1))
        self.assertFalse(safe);self.assertEqual(answer.tolist(),[0,1,2])

    def test_zero_query_has_exact_persistent_ties(self):
        safe,answer,_=transfer(np.zeros(15,dtype=np.int64),10,0,quantization_bound(1))
        self.assertTrue(safe);self.assertEqual(len(answer),15)


if __name__=='__main__':unittest.main()
