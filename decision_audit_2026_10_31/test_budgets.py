import unittest,warnings
import numpy as np
from decision_audit_2026_10_31.budgets import profile_kernel,PROFILES
from reviewer_audit_2026_10_31.retention import kernel

class TestBudgetProfiles(unittest.TestCase):
    def test_default_is_the_frozen_method_on_nontrivial_fixture(self):
        rng=np.random.default_rng(6746)
        D=[rng.normal(size=(18,13)) for _ in range(5)]
        Du=[np.nextafter(d,np.inf) for d in D];lower=sum(d.min(0) for d in D)
        with warnings.catch_warnings():
            warnings.simplefilter('ignore')
            self.assertEqual(profile_kernel(D,Du,lower,'discrete_default')[0],kernel(D,Du,lower,'discrete')[0])

    def test_empty_competitors_never_become_a_failure(self):
        D=[np.zeros((3,0))]
        with warnings.catch_warnings():
            warnings.simplefilter('ignore')
            for name in PROFILES:self.assertEqual(profile_kernel(D,D,np.array([]),name)[0],1)

if __name__=='__main__':unittest.main()
