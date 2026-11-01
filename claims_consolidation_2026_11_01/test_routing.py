import unittest
from unittest.mock import patch
from claims_consolidation_2026_11_01.run import evaluate_context


class RoutingTests(unittest.TestCase):
    def test_zero_witness_cannot_become_empty_matrix_certificate(self):
        with patch('claims_consolidation_2026_11_01.run.kernel',side_effect=AssertionError('must not call')),patch('claims_consolidation_2026_11_01.run.pairwise_refine',side_effect=AssertionError('must not call')):
            baseline,detail,refinement,extra=evaluate_context({'zero':True,'n':1000})
        self.assertEqual((baseline,refinement['rankUpper']),(1000,1000))
        self.assertEqual(refinement['status'],'zero_witness');self.assertEqual(extra,0.)

    def test_routing_uses_computed_bound_and_margins_without_labels(self):
        C={'zero':False,'D':'point','Du':'upper','lower':'lower'}
        with patch('claims_consolidation_2026_11_01.run.kernel',return_value=(20,{})),patch('claims_consolidation_2026_11_01.run.pairwise_refine',return_value={'rankUpper':10,'status':'complete_pairs'}) as refine:
            baseline,detail,result,extra=evaluate_context(C)
        self.assertEqual((baseline,result['rankUpper']),(20,10))
        refine.assert_called_once_with('point','upper',20,budget=2,k=10,max_candidates=80,seconds=120.)


if __name__=='__main__':unittest.main()
