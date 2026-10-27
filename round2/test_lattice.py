import unittest,itertools,json
import numpy as np
from lattice import exact_path,path_score,greedy_path,factor_upper
from core import Encoder,variants,train,evaluate
class OracleTests(unittest.TestCase):
 def test_exhaustive(self):
  rng=np.random.default_rng(20261027);cases=0;maxerr=0.
  for trial in range(600):
   n=int(rng.integers(1,7));q=int(rng.integers(2,4));budget=int(rng.integers(0,8));u=rng.normal(size=(n,q));e=rng.normal(size=(n,q,q));e[0]=0
   cost=rng.integers(1,5,(n,q));cost[:,0]=0
   if trial%3==0:cost[0,-1]=100000
   val,p=exact_path(u,e,cost,budget);brute=-np.inf
   for z in itertools.product(range(q),repeat=n):
    z=np.array(z,dtype=np.int16)
    if cost[np.arange(n),z].sum()<=budget:brute=max(brute,path_score(u,e,z))
   self.assertLessEqual(cost[np.arange(n),p].sum(),budget)
   self.assertAlmostEqual(val,path_score(u,e,p),places=9);self.assertAlmostEqual(val,brute,places=9)
   self.assertGreaterEqual(factor_upper(u,e,cost,budget)+1e-9,val)
   self.assertLessEqual(greedy_path(u,e,cost,budget)[0],val+1e-9)
   maxerr=max(maxerr,abs(val-brute));cases+=1
  __import__('pathlib').Path(__file__).with_name('oracle_exhaustive.json').write_text(json.dumps({'cases':cases,'mismatches':0,'max_abs_error':maxerr},indent=2))
 def test_interaction_counterexample(self):
  u=np.array([[0.,-2.],[0.,-2.]]);e=np.zeros((2,2,2));e[1,1,1]=10.;c=np.array([[0,1],[0,1]])
  self.assertEqual(exact_path(u,e,c,2)[0],6.)
  self.assertEqual(greedy_path(u,e,c,2)[0],0.)
 def test_variants(self):
  for t in ['không','được','tốt','école','cœur','abc','.', '😀', '\u0301']:
   vs=variants(t);self.assertEqual(len(vs),len(set(vs)));self.assertEqual(vs[0],t);self.assertTrue(all(len(s)==len(t) for s in vs))
 def test_feature_factorization(self):
  ss=['tôi không được học','môn này thật dễ','école très intéressante','được tốt thật']
  en=Encoder(ss,max_features=1000,bins=32);docs=[en.encode(s) for s in ss];rng=np.random.default_rng(71);W=rng.normal(size=(en.d,3));tab=en.tables(W)
  for d in docs:
   u,e=en.potentials(W,d,tab)
   for z in itertools.product(range(3),repeat=len(d.ids)):
    z=np.array(z,np.int16)
    if np.any(d.costs[np.arange(len(z)),z]>100):continue
    actual=np.asarray(en.features([d],[z])@W).ravel()
    for c in range(3):self.assertAlmostEqual(path_score(u[:,:,c],e[:,:,:,c],z)+W[-1,c],actual[c],places=9)
 def test_canonical_invariant(self):
  ss=['tôi không được học','môn này thật dễ','école très intéressante'];en=Encoder(ss,1000,32);ds=[en.encode(s) for s in ss]
  W=np.random.default_rng(17).normal(size=(en.d,3))*en.mask('canonical')[:,None]
  for d in ds:
   u,e=en.potentials(W,d,en.tables(W))
   for c in range(3):
    v,_=exact_path(u[:,:,c],e[:,:,:,c],d.costs,100)
    clean=path_score(u[:,:,c],e[:,:,:,c],np.zeros(len(d.ids),np.int16));self.assertAlmostEqual(v,clean,places=9)
 def test_training_gradient(self):
  import core
  from unittest.mock import patch
  original=core.minimize;checks=[]
  def checked(fun,x,*a,**kw):
   probe=np.random.default_rng(123).normal(0,.02,len(x));value,grad=fun(probe)
   for j in np.random.default_rng(44).choice(len(x),30,replace=False):
    z=probe.copy();z[j]+=1e-6;vp=fun(z)[0];z[j]-=2e-6;vm=fun(z)[0]
    self.assertAlmostEqual((vp-vm)/2e-6,grad[j],places=6)
   checks.append(True);return original(fun,x,*a,**kw)
  ss=['tôi thích môn học','không thích môn này','giảng bài rất hay','giảng bài thật tệ','tốt thật','quá chán']
  en=Encoder(ss,200,16);ds=[en.encode(s) for s in ss];y=np.array([1,0,1,0,1,0])
  with patch('core.minimize',checked):train(en,ds,y,2,.001,.7,17,'random',rounds=1,maxiter=3)
  self.assertEqual(len(checks),1)
 def test_budget_monotone(self):
  rng=np.random.default_rng(1);u=rng.normal(size=(8,3));e=rng.normal(size=(8,3,3));e[0]=0;c=rng.integers(1,4,(8,3));c[:,0]=0
  vals=[exact_path(u,e,c,k)[0] for k in range(12)];self.assertTrue(np.all(np.diff(vals)>=-1e-12))
if __name__=='__main__':unittest.main(verbosity=2)
