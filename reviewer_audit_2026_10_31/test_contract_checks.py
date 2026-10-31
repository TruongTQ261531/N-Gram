import itertools
import unittest
from reviewer_audit_2026_10_31.contract_checks import free_vote_worst_rank,enumerate_free_votes,bundle_fixture,region_fixture


class TestContractExamples(unittest.TestCase):
    def test_tie_cost_specialization_against_all_small_vote_allocations(self):
        for clean in itertools.product(range(3),repeat=3):
            for budget in range(4):
                self.assertEqual(free_vote_worst_rank(clean,0,budget),enumerate_free_votes(clean,0,budget))

    def test_correlated_bundle_is_strictly_smaller_than_free_vote_domain(self):
        for m in range(2,6):
            example=bundle_fixture(m)
            self.assertLess(example['finiteBundleWorstRank'],example['independentAllocationWorstRank'])

    def test_discrete_union_does_not_equal_convex_region_union(self):
        fixture=region_fixture()
        self.assertEqual(fixture['finiteUnion'],[1,2])
        self.assertEqual(fixture['continuousUnion'],[1,2,3])


if __name__=='__main__':unittest.main()
