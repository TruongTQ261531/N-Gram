import unittest
import numpy as np
from reviewer_audit_2026_10_31.verify_discordant import exhaustive_enclosure
from reviewer_audit_2026_10_31.retention import exhaustive_count


class TestBatchedEnclosure(unittest.TestCase):
    def test_batches_match_frozen_scalar_enumeration(self):
        rng=np.random.default_rng(20261031)
        for _ in range(12):
            D=[rng.normal(size=(3,7)) for i in range(4)]
            Du=[np.nextafter(d,np.inf) for d in D]
            for budget in [0,1,2]:
                expected=exhaustive_count(D,Du,budget)
                got=exhaustive_enclosure(Du,budget)
                self.assertEqual(got['status'],'COMPLETE')
                self.assertEqual(got['states'],expected['states'])
                self.assertEqual(got['rankUpper'],expected['rank_upper'])

    def test_cap_is_unknown_not_a_certificate(self):
        result=exhaustive_enclosure([np.zeros((20,10))]*4,max_states=1)
        self.assertEqual(result['status'],'RESOURCE_UNKNOWN')
        self.assertNotIn('rankUpper',result)

    def test_zero_competitors_and_unsupported_budget(self):
        self.assertEqual(exhaustive_enclosure([np.zeros((2,0))])['rankUpper'],1)
        with self.assertRaises(ValueError):exhaustive_enclosure([np.zeros((2,1))],3)


if __name__=='__main__':unittest.main()
