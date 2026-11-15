import unittest
import numpy as np
from reviewer_audit_2026_10_31.retention import Index,context as original_context,kernel as original_kernel
from codex_followup_2026_11_05.experiments import context,kernel,support_cover


class TestControlledAblations(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.index=Index(['cat dog','cat cat','dog dog','cat dog','bird tree','mouse house','red fish','blue fish','dog cat','quiet river','small stone','garden green'],[str(i) for i in range(12)],'char')
        cls.index.transpose()

    def test_screened_context_matches_original(self):
        for b in [1,2,3]:
            a=original_context(self.index,'cat dog',b);c=context(self.index,'cat dog',b)
            self.assertEqual(a['ref'],c['ref']);self.assertEqual(a['zero'],c['zero'])
            if not a['zero']:
                for key in ['D','Du']:
                    for x,y in zip(a[key],c[key]):np.testing.assert_array_equal(x,y)
                np.testing.assert_array_equal(a['lower'],c['lower'])

    def test_unchanged_method_bounds_match_original_kernels(self):
        C=context(self.index,'cat dog',1)
        for method in ['pair_enum','best_lp_enum','discrete','milp_enum']:
            expected,_=original_kernel(C['D'],C['Du'],C['lower'],method,1)
            actual,_=kernel(C,method,1);self.assertEqual(actual,expected)

    def test_context_cap_returns_whole_corpus_unknown(self):
        C=context(self.index,'cat dog',1,max_cells=0)
        self.assertEqual(C['status'],'context_resource_cap')
        rank,detail=kernel(C,'discrete',1);self.assertEqual(rank,self.index.n)
        self.assertEqual(detail['status'],'context_resource_cap')

    def test_zero_witness_not_an_empty_candidate_certificate(self):
        for screen in [True,False]:
            C=context(self.index,'zzzzzz',2,screen=screen)
            self.assertEqual(C['status'],'zero_witness')
            self.assertEqual(kernel(C,'discrete',2)[0],self.index.n)

    def test_unscreened_pipeline_preserves_reference_and_bound(self):
        a=context(self.index,'cat dog',1);b=context(self.index,'cat dog',1,screen=False)
        self.assertEqual(a['ref'],b['ref']);self.assertEqual(b['materializedDocuments'],self.index.n)
        self.assertEqual(kernel(a,'discrete',1)[0],kernel(b,'discrete',1)[0])

    def test_support_only_never_calls_pareto_and_edges_are_safe(self):
        D=[np.array([[1.,-2.],[-2.,1.]])];Du=[d.copy() for d in D]
        g=support_cover(D,Du,1)
        self.assertEqual(g['count_upper'],1)
        self.assertTrue(all(c['method']=='support' and c['upper']<0 for c in g['checks']))


if __name__=='__main__':unittest.main()
