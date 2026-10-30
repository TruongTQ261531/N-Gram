import itertools
import unittest
import numpy as np
from core import candidate_pools,choices,compact_forms,oracle,envelopes,Index

class Checks(unittest.TestCase):
    def test_all_small_states_and_conditional_bounds(self):
        rng=np.random.default_rng(30731)
        for trial in range(80):
            F=[rng.integers(0,25,size=(int(rng.integers(1,5)),9),dtype=np.int64) for _ in range(4)]
            for b in (0,1,2):
                truth,_=oracle(F,b,(1,3))
                for k in (1,3):
                    pools,_=candidate_pools(F,b,k)
                    for name,pool in pools.items():
                        self.assertTrue(set(truth[k]) <= set(pool), (trial,b,k,name))
                    self.assertTrue(set(pools['partitioned'])<=set(pools['coupled'])<=set(pools['independent']))
                for first in range(len(F[0])):
                    if first!=0 and not b:continue
                    lo,hi=envelopes(F,b,{0:first})
                    for a in choices([len(f) for f in F],b):
                        if a[0]!=first:continue
                        z=sum(f[v] for f,v in zip(F,a))
                        self.assertTrue(np.all(lo<=z) and np.all(z<=hi))

    def test_ties_zero_scores_and_repeated_tokens(self):
        F=[np.zeros((4,7),dtype=np.int64)]*3
        pools,_=candidate_pools(F,2,1)
        for pool in pools.values():self.assertEqual(len(pool),7)
        self.assertEqual(len(list(choices([4,4,4],2))),37)
        self.assertEqual(compact_forms('search'),compact_forms('search'))

    def test_integer_factors_match_full_query_reencoding(self):
        I=Index([{'id':'a','text':'Tìm kiếm nghiên cứu n-gram search engine'},{'id':'b','text':'query cache typo retrieval research'},{'id':'c','text':'😀 tìm tài liệu'}])
        fs,F,_=I.factors('Tìm search research')
        for a in choices([len(f) for f in F],2):
            q=' '.join(f[v]['text'] for f,v in zip(fs,a))
            np.testing.assert_array_equal(I.score(q),sum(f[v] for f,v in zip(F,a)))

if __name__=='__main__':unittest.main()
