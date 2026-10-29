import itertools,unittest
import numpy as np
from scipy.optimize import linprog
from rank_bound import envelope,support

class BoundChecks(unittest.TestCase):
 def test_against_enumerated_relaxation(self):
  rng=np.random.default_rng(29)
  for case in range(60):
   t=int(rng.integers(1,5));m=int(rng.integers(2,8));b=int(rng.integers(1,t+1))
   D=[rng.normal(-.4,2,(int(rng.integers(2,4)),m)) for _ in range(t)]
   states=[z for z in itertools.product(*[range(len(d)) for d in D]) if sum(a!=0 for a in z)<=b]
   V=np.array([sum(d[a] for d,a in zip(D,z)) for z in states]);L=V.min(0)-1e-9
   # All competitors here have negative individual minima, as after pruning.
   if np.any(L>=0):continue
   out=envelope(D,D,L,b,max_iterations=250,tolerance=1e-8)
   exact=int((V>=0).sum(1).max())
   self.assertGreaterEqual(out['upper_count']+1e-7,exact)
   caps=1/(-L)
   # Primal LP over a distribution on all feasible discrete query states.
   A=np.column_stack((-V.T*caps[:,None],np.eye(m)))
   eq=np.r_[np.ones(len(states)),np.zeros(m)][None,:]
   r=linprog(np.r_[np.zeros(len(states)),-np.ones(m)],A_ub=A,b_ub=np.ones(m),A_eq=eq,b_eq=[1.],bounds=[(0,None)]*len(states)+[(0,1)]*m,method='highs',options={'threads':1})
   self.assertTrue(r.success);self.assertAlmostEqual(out['upper_count'],-r.fun,places=5)

 def test_incompatible_promotions(self):
  # Either competitor can win, but a single shared choice cannot promote both.
  D=[np.array([[-2.,-2.],[1.,-5.],[-5.,1.]])]
  r=envelope(D,D,np.array([-5.,-5.]),1)
  self.assertLess(r['upper_count'],2.)
  self.assertGreaterEqual(r['upper_count'],1.)

 def test_support_bruteforce(self):
  rng=np.random.default_rng(31)
  for _ in range(100):
   D=[rng.normal(size=(3,5)) for i in range(4)];w=rng.uniform(0,1,5);b=2
   point,up,z,margin=support(D,D,w,b)
   brute=max(sum(d[a]@w for d,a in zip(D,c)) for c in itertools.product(range(3),repeat=4) if sum(a!=0 for a in c)<=b)
   self.assertAlmostEqual(point,brute,places=10);self.assertGreaterEqual(up+1e-12,brute)

if __name__=='__main__':unittest.main()
