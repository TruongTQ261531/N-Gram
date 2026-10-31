import unittest
from reviewer_audit_2026_10_31.retention import Index
from decision_audit_2026_10_31.decisions import prove_witness

class TestExactWitness(unittest.TestCase):
    def test_tied_competitors_are_real_unfavorable_violations(self):
        index=Index(['alpha beta']*12,[str(i) for i in range(12)])
        q=index.query('alpha');r=int(q.rankings()[0]);proof=prove_witness(index,q,r,[0])
        self.assertTrue(proof['proved']);self.assertEqual(proof['rankLower'],11)
        self.assertEqual(proof['minimumExactMargin'],'0')

    def test_zero_score_is_exact_and_outside_variant_is_rejected(self):
        index=Index(['alpha beta']*12,[str(i) for i in range(12)])
        q=index.query('x');proof=prove_witness(index,q,0,[0])
        self.assertEqual(proof['rankLower'],12)
        with self.assertRaises(ValueError):prove_witness(index,q,0,[999])

    def test_a_unique_winner_is_not_mistaken_for_a_violation(self):
        index=Index(['alpha beta']+['gamma delta']*11,[str(i) for i in range(12)])
        q=index.query('alpha');proof=prove_witness(index,q,0,[0])
        self.assertFalse(proof['proved'])

if __name__=='__main__':unittest.main()
