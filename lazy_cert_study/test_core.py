"""Differential checks against full-query re-encoding, not the bound formula."""
from pathlib import Path
import itertools
import sys
import unittest
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from pool_study.core import Index
from lazy_cert_study.core import screen, materialize, IncrementalScorer, topk


class TestProjection(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        rng = np.random.default_rng(20261031)
        tokens = ['alpha','beta','gamma','delta','search','query','token','rank',
                  'bài','giảng','tốt','dữ','liệu','a','b','é']
        docs = [{'id':str(i), 'text':' '.join(rng.choice(tokens,size=8))}
                for i in range(30)]
        cls.index = Index(docs)

    def check_query(self, query, budget, k):
        I = self.index
        pool, Q, proof = screen(I, query, budget, k)
        F, _ = materialize(I, Q, pool)
        union = set()
        for state in itertools.product(*(range(len(f)) for f in Q.forms)):
            if sum(a != 0 for a in state) > budget:
                continue
            changed = ' '.join(f[a]['text'] for f,a in zip(Q.forms,state))
            scores = I.score(changed)
            gold = topk(scores,k)
            union.update(gold.tolist())
            self.assertTrue(set(gold) <= set(pool))
            self.assertTrue(np.all(scores <= proof['upperScores']))
            self.assertTrue(np.all(scores[proof['anchors']] >= proof['anchorLower']))
            projected = sum(f[a] for f,a in zip(F,state))
            np.testing.assert_array_equal(projected,scores[pool])
            np.testing.assert_array_equal(pool[topk(projected,k)],gold)
        self.assertTrue(union <= set(pool))

    def test_exhaustive_whole_query(self):
        for query in ['alpha beta','search rank query','bài giảng tốt',
                      'a a beta','alpha alpha alpha beta','unseen xyz']:
            for budget in [0,1,2,3]:
                self.check_query(query,budget,3)

    def test_zero_scores_and_all_ties(self):
        pool,_,_=screen(self.index,'☃ ☄',2,3)
        np.testing.assert_array_equal(pool,np.arange(self.index.n))

    def test_k_equals_corpus(self):
        self.check_query('alpha beta',2,self.index.n)

    def test_incremental_against_full_queries(self):
        I=self.index;control=IncrementalScorer(I,'alpha alpha beta',3)
        for text in ['alpha beta','beta alpha alpha','alpha gamma beta',
                     'bài giảng tốt','','☃','alpha beta','alpha alpha beta']:
            np.testing.assert_array_equal(control.query(text),topk(I.score(text),3))

    def test_invalid_inputs(self):
        for query,budget,k in [('',2,3),('a',-1,3),('a',2,0),('a',2,31)]:
            with self.assertRaises(ValueError):screen(self.index,query,budget,k)

    def test_complete_pipelines_against_original_state_oracle(self):
        from lazy_cert_study.benchmark import build, oracle
        from lazy_cert_study.core import lattice
        for query in ['alpha beta','a a','☃ ☄','alpha alpha alpha beta','bài giảng tốt']:
            Q=lattice(self.index,query)
            for budget in [0,1,2]:
                gold,record=oracle(self.index,Q.forms,budget,3)
                self.assertEqual(record['status'],'exact')
                for kind in ['parent','screened','batch','screen_batch']:
                    pool,raw,detail=build(self.index,query,kind,budget,3)
                    self.assertEqual(detail['status'],'exact')
                    np.testing.assert_array_equal(pool,gold)
                    np.testing.assert_array_equal(raw,self.index.score(query)[pool])

    def test_pipeline_rejects_unsupported_budget(self):
        from lazy_cert_study.benchmark import build
        for kind in ['parent','screened','batch','screen_batch']:
            with self.assertRaises(ValueError):build(self.index,'alpha beta',kind,3,3)


if __name__=='__main__':unittest.main()
