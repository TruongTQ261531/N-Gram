"""Deterministic, auditable Vietnamese synthetic corruptions; not human validated."""
import re, unicodedata as ud, hashlib, random
from functools import lru_cache
FAMILIES = ['fold','tone','keyboard','delete','swap','repeat','whitespace','teencode']
TEEN = {'không':['ko','k','hong'], 'được':['dc','đc'], 'biết':['bit'], 'người':['ng'], 'yêu':['iu'], 'rất':['r'], 'với':['vs'], 'gì':['j'], 'vậy':['z'], 'thích':['thik'], 'bạn':['bn'], 'mình':['mik'], 'nhưng':['nhg'], 'trước':['trc'], 'bây':['bi'], 'giờ':['h'], 'học':['hok']}
KEY = dict(zip('qwertyuiopasdfghjklzxcvbnm','wwertyuioppsdfghjkllxcvbnmm'))
TONES = ['','\u0300','\u0301','\u0303','\u0309','\u0323']
def normalize(s):return ' '.join(ud.normalize('NFC',str(s)).lower().split())
@lru_cache(maxsize=100000)
def fold(s):
 return ''.join(c for c in ud.normalize('NFD',s) if ud.category(c)!='Mn').replace('đ','d').replace('Đ','D')
def rng_for(s,seed):return random.Random(int.from_bytes(hashlib.sha256((str(seed)+'|'+s).encode()).digest()[:8],'little'))
def _token(t,f,r):
 positions=[i for i,c in enumerate(t) if c.isalpha()]
 if not positions:return t
 if f=='fold':return fold(t)
 if f=='teencode':return r.choice(TEEN[t]) if t in TEEN else t
 if f=='tone':
  pos=[i for i in positions if fold(t[i]) in 'aeiouy']
  if not pos:return t
  i=r.choice(pos); n=ud.normalize('NFD',t[i]); base=''.join(c for c in n if c not in TONES[1:]);old=''.join(c for c in n if c in TONES[1:]);new=r.choice([x for x in TONES if x!=old]);return t[:i]+ud.normalize('NFC',base+new)+t[i+1:]
 i=r.choice(positions)
 if f=='keyboard':
  c=KEY.get(fold(t[i]));return t[:i]+c+t[i+1:] if c else t
 if f=='delete':return t[:i]+t[i+1:] if len(positions)>1 else t
 if f=='swap':
  pos=[j for j in positions if j+1<len(t) and t[j+1].isalpha() and t[j]!=t[j+1]]
  if not pos:return t
  j=r.choice(pos);return t[:j]+t[j+1]+t[j]+t[j+2:]
 if f=='repeat':return t[:i]+t[i]*r.choice([2,3])+t[i+1:]
 raise ValueError(f)
def corrupt(s,f,p,seed):
 if f=='clean':return s
 if f=='fullfold':return fold(s)
 if f=='nfd':return ud.normalize('NFD',s)
 if p==0:return s
 r=rng_for(s,seed);tokens=s.split(' ')
 if f=='whitespace':
  return ''.join(t+('' if r.random()<p else ' ') for t in tokens[:-1])+tokens[-1]
 return ' '.join(_token(t,f,r) if r.random()<p else t for t in tokens)
def augment(s,seed):
 r=rng_for(s,seed+333);f=r.choice(['fold','keyboard','repeat','teencode']);return corrupt(s,f,.3,seed)
