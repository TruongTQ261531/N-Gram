import unittest,sys
from pathlib import Path
import numpy as np
from scipy import sparse
from sklearn.linear_model import Ridge
from noise import *
from study import load_data,vectorizers,reliability,DATASETS
class Integrity(unittest.TestCase):
 def test_identity(self):
  s=normalize('Tôi không thích môn học này 😃')
  for f in FAMILIES:self.assertEqual(corrupt(s,f,0,17),s)
 def test_seed(self):
  s='tôi không biết bạn có được học không'
  for f in FAMILIES:self.assertEqual(corrupt(s,f,.3,71),corrupt(s,f,.3,71))
 def test_fold(self):
  self.assertEqual(fold('đường phố Việt Nam'),'duong pho Viet Nam')
  self.assertEqual(fold(fold('đường phố Việt Nam')),fold('đường phố Việt Nam'))
 def test_unicode(self):
  self.assertEqual(normalize('TÔI   THÍCH'),normalize('tôi thích'))
 def test_splits(self):
  for ds in DATASETS:
   tr,dv,te,enc,au=load_data(ds)
   for a,b in [(tr,dv),(tr,te),(dv,te)]:self.assertFalse(set(a.text)&set(b.text))
 def test_train_only_vocab(self):
  import pandas as pd
  c,w=vectorizers(pd.DataFrame({'text':['đường phố','đường làng','phố đông','làng đông']}))
  for v in [c,w]:
   original=v.vocabulary_.copy();v.transform(['zzzzsentinelzzzz']);self.assertEqual(v.vocabulary_,original)
   self.assertFalse(any('zzz' in x for x in v.vocabulary_))
 def test_nfd_transform(self):
  import pandas as pd,unicodedata
  ss=['đường phố đông','thầy giảng hay','đường làng']
  c,w=vectorizers(pd.DataFrame({'text':ss}))
  for v in [c,w]:self.assertEqual((v.transform(ss)-v.transform([unicodedata.normalize('NFD',s) for s in ss])).nnz,0)
 def test_ridge_penalty(self):
  rng=np.random.default_rng(17);X=rng.normal(size=(24,8));Y=rng.normal(size=(24,3));D=rng.normal(size=(24,8));alpha=1.;lam=3.
  A=np.vstack([X,np.sqrt(lam)*D]);B=np.vstack([Y,np.zeros_like(Y)])
  m=Ridge(alpha=alpha,fit_intercept=False,solver='lsqr',tol=1e-12,max_iter=500).fit(sparse.csr_matrix(A),B)
  W=m.coef_.T;grad=A.T@(A@W-B)+alpha*W
  self.assertLess(np.linalg.norm(grad),1e-8)
  free=np.linalg.solve(X.T@X+alpha*np.eye(8),X.T@Y)
  self.assertLess(np.linalg.norm(D@W),np.linalg.norm(D@free))
 def test_pair_penalty_identity(self):
  # Paired squared-loss consistency is a classic quadratic identity, not novel mathematics.
  rng=np.random.default_rng(43);a,b,y=rng.normal(size=(3,20,7));lam=2.7
  lhs=np.sum((a-y)**2)+np.sum((b-y)**2)+lam*np.sum((a-b)**2)
  rhs=2*np.sum(((a+b)/2-y)**2)+(.5+lam)*np.sum((a-b)**2)
  self.assertAlmostEqual(lhs,rhs,places=9)
 def test_weight_bounds(self):
  ss=['tốt x','tot x','tốt x','tột x','tot x','tột x']*3;y=np.array([0,0,0,1,1,1]*3)
  r=reliability(ss,y,2);self.assertTrue(np.all((r>0)&(r<=1)));self.assertTrue(np.all(np.isfinite(r)))
 def test_keyboard_no_identity_mapping(self):
  self.assertEqual(len(KEY),26)
  for src,dst in KEY.items():
   self.assertNotEqual(src,dst)
   self.assertNotEqual(corrupt(src,'keyboard',1,17),src)
 def test_actual_corruption(self):
  ss=['không được thích bạn','mình biết người yêu','tôi học rất vui']
  for f in FAMILIES:self.assertTrue(any(corrupt(s,f,1,17)!=s for s in ss),f)
if __name__=='__main__':unittest.main(verbosity=2)
