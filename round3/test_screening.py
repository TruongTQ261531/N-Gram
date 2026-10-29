import itertools,unittest
from decimal import Decimal,localcontext
import numpy as np
from core import Index,outward_scores
from screening import coarse_candidates,screened_retention
from rank_bound import retention,direct_reference,envelope

class ScreeningChecks(unittest.TestCase):
 def setUp(self):
  self.I=Index(['ab bc cd','ab ca bd','ac ba cd','abc ab cd','xy zz pq','xy ab bc','ad bc da'],list(map(str,range(7))))

 def test_coarse_exhaustive(self):
  q=self.I.query('ab bc');rank=q.rankings();c=coarse_candidates(q,rank,2);F=q.all_scores()
  for a in itertools.product(*[range(len(f)) for f in F]):
   b=sum(x!=0 for x in a)
   if b>2:continue
   score=sum(f[z] for f,z in zip(F,a))
   self.assertTrue(np.all(score<=c['upper_scores'][b]+1e-12))
   self.assertGreaterEqual(score[rank[0]]+1e-12,c['reference_lower'][b])

 def test_screened_matches_full(self):
  for text in ['ab bc','ab cd','xy zz','ab','unknown']:
   q=self.I.query(text);rank=q.rankings();full=retention(q.all_scores(),q.features,rank,3)
   cut,_,_,_=screened_retention(q,rank,3)
   self.assertEqual([x['rank_upper'] for x in cut],[x['rank_upper'] for x in full])

 def test_decimal_dot_intervals(self):
  q=self.I.query('abc ab cd');F=q.all_scores();lo,hi=outward_scores(F,q.features)
  checked=0
  with localcontext() as ctx:
   ctx.prec=80
   for t,A in enumerate(q.features):
    for a in range(min(10,A.shape[0])):
     counts=dict(zip(A[a].indices,A[a].data))
     for doc in range(self.I.n):
      weights=dict(zip(self.I.W[doc].indices,self.I.W[doc].data))
      true=sum((Decimal.from_float(float(v))*Decimal.from_float(float(weights.get(g,0.))) for g,v in counts.items()),Decimal(0))
      self.assertLessEqual(Decimal.from_float(float(lo[t][a,doc])),true)
      self.assertGreaterEqual(Decimal.from_float(float(hi[t][a,doc])),true);checked+=1
  print('High-precision dot-product interval checks:',checked)

 def test_generic_lp_matches_oracle_solver(self):
  D=[np.array([[-2.,-2.],[1.,-5.],[-5.,1.]]),np.array([[-1.,-1.],[0.,-2.]])]
  L=np.array([-7.,-7.]);a=envelope(D,D,L,1);b=direct_reference(D,D,L,1)
  self.assertTrue(b['success']);self.assertAlmostEqual(a['upper_count'],b['upper_count'],places=7)

if __name__=='__main__':unittest.main()
