import unittest
import numpy as np
from scipy import sparse
from scipy.optimize import minimize,LinearConstraint,Bounds
from dual_solver import optimize_pool,dual_value
class DualTest(unittest.TestCase):
 def check_qp(self,K):
  rng=np.random.default_rng(121);F=5;G=4;M=12
  X=sparse.csr_matrix(rng.normal(size=(M,F)));gr=np.repeat(np.arange(G,dtype=np.int32),3);gy=np.arange(G)%K;gc=(gy+1)%K;ys=gy[gr].astype(np.int32);cs=gc[gr].astype(np.int32);lam=np.array([.2,.3,.1,.4]);alpha=.5
  a=np.zeros(M);A=np.zeros(G);W=np.zeros((F,K));a,A,W,hist=optimize_pool(X,cs,ys,gr,lam,alpha,a,A,W,epochs=10000)
  dv=dual_value(a,A,W,lam,alpha);marg=np.asarray(X@W);v=1+marg[np.arange(M),cs]-marg[np.arange(M),ys];hh=np.zeros(G);np.maximum.at(hh,gr,v)
  primal=.5*alpha*np.sum(W*W)+np.sum(lam*hh*hh);self.assertGreaterEqual(primal-dv,-1e-10);self.assertLess(primal-dv,1e-7)
  mat=np.zeros((M,F*K+G));xx=X.toarray()
  for i in range(M):
   for j in range(F):mat[i,j*K+ys[i]]=xx[i,j];mat[i,j*K+cs[i]]=-xx[i,j]
   mat[i,F*K+gr[i]]=1
  def obj(z):return .5*alpha*np.sum(z[:F*K]**2)+np.sum(lam*z[F*K:]**2),np.r_[alpha*z[:F*K],2*lam*z[F*K:]]
  out=minimize(obj,np.zeros(F*K+G),jac=True,method='SLSQP',constraints=[LinearConstraint(mat,np.ones(M),np.full(M,np.inf))],bounds=Bounds(np.r_[np.full(F*K,-np.inf),np.zeros(G)],np.full(F*K+G,np.inf)),options={'ftol':1e-12,'maxiter':1000})
  self.assertTrue(out.success);self.assertAlmostEqual(out.fun,primal,places=7)
  wr=np.zeros_like(W)
  for i in range(M):wr[:,cs[i]]-=a[i]*xx[i]/alpha;wr[:,ys[i]]+=a[i]*xx[i]/alpha
  self.assertTrue(np.allclose(W,wr,atol=1e-10));self.assertTrue(np.all(a>=-1e-15));self.assertTrue(np.all(np.diff(hist)>=-1e-8))
 def test_binary(self):self.check_qp(2)
 def test_three_class(self):self.check_qp(3)
 def test_seven_class(self):self.check_qp(7)
if __name__=='__main__':unittest.main(verbosity=2)
