from pathlib import Path
import itertools,json,unittest
import numpy as np
from scipy import sparse
from core import *

class Checks(unittest.TestCase):
 def test_differential(self):
  rng=np.random.default_rng(20261029);count=0
  for _ in range(300):
   n=int(rng.integers(3,8));t=int(rng.integers(1,5));k=int(rng.integers(1,min(n,3)))
   F=[rng.uniform(0,10,(int(rng.integers(2,4)),n)) for i in range(t)]
   A=[sparse.csr_matrix(np.ones((len(f),2))) for f in F]
   ranking=np.argsort(-sum(f[0] for f in F));full=certify(F,A,ranking,k,3,False);screen=certify(F,A,ranking,k,3,True)
   np.testing.assert_array_equal(full['cert'],screen['cert'])
   self.assertTrue(np.all(~screen['loose']|screen['cert']))
   for b in range(4):
    exact=brute_margin(F,list(ranking[:k]),b)
    self.assertAlmostEqual(full['point'][b],exact,places=10)
    self.assertGreaterEqual(full['upper'][b]+1e-12,exact)
    w=full['witness'][b];v=sum(f[a] for f,a in zip(F,w['choices']))
    self.assertAlmostEqual(v[w['outside']]-v[w['inside']],exact,places=10);count+=1
  print('Independent exhaustive comparisons:',count)

 def test_shared_shift(self):
  F=[np.array([[20.,19.,0.],[10.,9.,0.]])];A=[sparse.csr_matrix(np.ones((2,2)))]
  r=certify(F,A,np.array([0,1,2]),1,1,False)
  self.assertFalse(r['loose'][1]);self.assertTrue(r['cert'][1])

 def test_features_and_witness(self):
  I=Index(['the example is useful','another sample example','rare words survive'],['a','b','c'])
  q=I.query('the example');F=q.all_scores()
  np.testing.assert_allclose(sum(f[0] for f in F),I.score('the example'),atol=1e-12)
  for _ in range(20):
   choices=[len(f)-1 for f in F]
   np.testing.assert_allclose(sum(f[a] for f,a in zip(F,choices)),I.score(q.text(choices)),atol=1e-12)

 def test_variants(self):
  f,ops=variants('book');self.assertEqual(f[0],'book');self.assertEqual(len(f),len(set(f)))
  self.assertIn('bok',f);self.assertIn('boook',f);self.assertIn('obok',f)
  self.assertEqual(normalize(' A\u0301  TEST '),'á test')

 def test_zero_tie(self):
  F=[np.zeros((2,4))];A=[sparse.csr_matrix(np.ones((2,2)))]
  r=certify(F,A,np.arange(4),1,2);self.assertFalse(r['cert'].any())

if __name__=='__main__':unittest.main()
