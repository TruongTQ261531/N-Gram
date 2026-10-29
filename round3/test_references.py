import itertools,unittest
import numpy as np
from enumeration import exhaustive_count
from mip_reference import solve

class ReferenceChecks(unittest.TestCase):
 def test_enumeration_and_mip(self):
  rng=np.random.default_rng(911)
  for case in range(25):
   D=[rng.normal(-.4,1,(3,4)) for i in range(3)];b=2
   V=np.array([sum(d[a] for d,a in zip(D,z)) for z in itertools.product(range(3),repeat=3) if sum(a!=0 for a in z)<=b])
   exact=int((V>=0).sum(1).max());L=np.minimum(V.min(0)-1e-8,-1e-8)
   e=exhaustive_count(D,D,b);self.assertEqual(e['upper_count'],exact)
   r=solve(D,L,b,1.);self.assertTrue(r['success']);self.assertEqual(r['optimal_count'],exact)

 def test_enumeration_resource_limit(self):
  D=[np.zeros((3,2)) for i in range(4)]
  self.assertIn('skipped',exhaustive_count(D,D,3,max_states=1))

if __name__=='__main__':unittest.main()
