import unittest
import numpy as np
from method import legacy
from fast_factors import factors
class Tests(unittest.TestCase):
    def test_equivalent_integer_scores_for_every_position_form_and_document(self):
        I=legacy.Index([{'id':'a','text':'Tìm kiếm search search query'},{'id':'b','text':'retrieval cache source corpus'},{'id':'c','text':'😀 nghiên cứu'}])
        for query in ['search search query search','TÌM kiếm tìm kiếm','😀 x x 😀','retrieval query corpus']:
            fs,F,m=factors(I,query);old,G,n=I.factors(query,max_tokens=1_000_000);self.assertEqual(fs,old);self.assertEqual(m['maxScoreBound'],n['maxScoreBound'])
            for a,b in zip(F,G):np.testing.assert_array_equal(a,b)
        self.assertLess(factors(I,'search search search')[2]['uniqueFormsScored'],factors(I,'search search search')[2]['positionForms'])
if __name__=='__main__':unittest.main()
