import itertools,unittest
import numpy as np
from compatibility import incompatible,cover_bound

class CompatibilityChecks(unittest.TestCase):
 def test_pareto_against_exhaustive(self):
  rng=np.random.default_rng(733)
  for _ in range(200):
   n=int(rng.integers(1,5));b=int(rng.integers(1,n+1))
   D=[rng.normal(-.3,1,(3,2)) for i in range(n)]
   true=max(min(sum(d[a] for d,a in zip(D,z))) for z in itertools.product(range(3),repeat=n) if sum(a!=0 for a in z)<=b)
   r=incompatible(D,D,b)
   if r['incompatible']:self.assertLess(true,0.)
   if r['method']=='pareto':self.assertAlmostEqual(true,r['upper'],places=10)

 def test_discrete_edge_beyond_convex_support(self):
  D=[np.array([[-2.,-2.],[1.,-1.],[-1.,1.]])]
  r=incompatible(D,D,1)
  self.assertTrue(r['incompatible']);self.assertEqual(r['method'],'pareto')

 def test_cover_count(self):
  D=[np.array([[-2.,-2.,-2.],[1.,-2.,-2.],[-2.,1.,-2.],[-2.,-2.,1.]])]
  r=cover_bound(D,D,1)
  self.assertEqual(r['count_upper'],1)

 def test_resource_cap_never_claims_edge(self):
  D=[np.array([[-2.,-2.],[1.,-1.],[-1.,1.]])]
  r=incompatible(D,D,1,max_points=1)
  self.assertFalse(r['incompatible']);self.assertEqual(r['method'],'resource_cap')

if __name__=='__main__':unittest.main()
