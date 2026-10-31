import unittest
from decision_audit_2026_10_31.typos import membership,wilson,parse

class TestActualChannelMembership(unittest.TestCase):
    def test_empty_alternative_can_remove_a_one_letter_token(self):
        self.assertEqual(membership('a cat','cat')['minimumCostWithinBudget'],1)

    def test_two_char_changes_inside_one_token_are_not_budget_two(self):
        self.assertEqual(membership('abcd','ab')['status'],'outside_channel_or_budget')
        self.assertEqual(membership('abcd efgh','abc efg')['minimumCostWithinBudget'],2)

    def test_normalization_does_not_become_covered_typo(self):
        self.assertEqual(membership('HELLO  world','hello world')['status'],'normalization_only')

    def test_corpus_format_and_interval(self):
        pairs=list(parse(b'$a_lot\nalot\n$hello\nhelo\n'))
        self.assertEqual(pairs[0]['corrected'],'a lot')
        lo,hi=wilson(80,100);self.assertLess(lo,.8);self.assertGreater(hi,.8)
        self.assertIsNone(wilson(0,0))

if __name__=='__main__':unittest.main()
