"""Portable numerical model: no pickle and no corpus text cache."""
import numpy as np
from scipy import sparse
from sklearn.feature_extraction.text import TfidfVectorizer
from core import Encoder

def save_model(path,en,W,labels):
 vocab=np.empty(en.f,dtype=object)
 for token,i in en.v.vocabulary_.items():vocab[i]=token
 np.savez_compressed(path,W=W,idf=en.v.idf_,vocab=np.array(vocab,dtype=str),bins=np.array(en.bins),labels=np.array(labels,dtype=str))
def load_model(path):
 z=np.load(path,allow_pickle=False);vocab=z['vocab'];v=TfidfVectorizer(analyzer='char',ngram_range=(2,5),sublinear_tf=True,lowercase=False,vocabulary={str(t):i for i,t in enumerate(vocab)})
 v.fit(['dummy']);v.idf_=z['idf']
 en=Encoder.__new__(Encoder);en.v=v;en.f=len(vocab);en.bins=int(z['bins']);en.d=2*en.f+2*en.bins+1;en.words=[];en.index={};en.V=sparse.csr_matrix((0,en.f))
 return en,z['W'],z['labels']
