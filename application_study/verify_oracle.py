"""Independent arbitrary-precision oracle and full-trace verifier. No numpy needed."""
from pathlib import Path
import argparse,gzip,hashlib,itertools,json,math,unicodedata,time
ROOT=Path(__file__).resolve().parent
def normal(s):return ' '.join(unicodedata.normalize('NFC',str(s)).lower().split())
def grams(s):
 out={}
 for token in normal(s).split():
  token=' '+token+' '
  for n in (3,4,5):
   for i in range(len(token)-n+1):out[token[i:i+n]]=out.get(token[i:i+n],0)+1
 return out
def count(sizes,b):
 c=[1]+[0]*b
 for n in sizes:
  for j in range(b,0,-1):c[j]+=c[j-1]*(n-1)
 return sum(c)
def main():
 p=argparse.ArgumentParser();p.add_argument('--input',type=Path,default=ROOT/'results/audit-set.jsonl.gz');p.add_argument('--output',type=Path,default=ROOT/'results/independent-oracle.json');a=p.parse_args()
 start=time.perf_counter()
 with gzip.open(a.input,'rt') as f:manifest=json.loads(next(f));rows=[json.loads(l) for l in f]
 weights=[dict(w) for w in manifest['weights']];n=len(weights);ids=[d['id'] for d in manifest['corpus']];checked=0;factors=0;successful_edges=0;families={};report=[]
 for row in rows:
  assert row['semanticRelevanceLabel'] is None and row['synthetic'] is True
  split='evaluation' if int(hashlib.sha256(row['family'].encode()).hexdigest()[:8],16)%5==0 else 'development'
  assert row['split']==split
  assert families.setdefault(row['family'],split)==split
  F=[]
  for fs,stored in zip(row['forms'],row['factorScores']):
   values=[]
   for form,saved in zip(fs,stored):
    q=grams(form['text']);v=[sum(c*w.get(g,0) for g,c in q.items()) for w in weights];assert v==saved,'Independent character scoring mismatch';values.append(v);factors+=len(v)
   F.append(values)
  b=row['budget'];ref=row['referenceIndex'];assert ids[ref]==row['referenceId'];expected=count([len(f) for f in F],b);assert expected==row['lattice']['states']
  if row['oracle']['status']!='exact':
   assert row['oracle']['status']=='resource_unknown';continue
  traces={tuple(x['choices']):x['worstTieRank'] for x in row['oracle']['records']}
  assert len(traces)==expected==len(row['oracle']['records'])
  base=[sum(f[0][j] for f in F) for j in range(n)];truebest=0;visited=0;co=[0]*n
  for cost in range(b+1):
   for positions in itertools.combinations(range(len(F)),cost):
    for alts in itertools.product(*(range(1,len(F[t])) for t in positions)):
     choices=[0]*len(F);score=base.copy()
     for t,alt in zip(positions,alts):
      choices[t]=alt
      for j in range(n):score[j]+=F[t][alt][j]-F[t][0][j]
     promoted=[j for j in range(n) if j!=ref and score[j]>=score[ref]];rank=1+len(promoted);truebest=max(truebest,rank);assert traces[tuple(choices)]==rank
     mask=sum(1<<j for j in promoted)
     for j in promoted:co[j]|=mask
     visited+=1
  assert visited==expected and truebest==row['oracle']['rank']
  assert truebest<=row['bounds']['pairwise'] and truebest<=row['bounds']['discrete'] and truebest<=row['bounds']['proposed'] and truebest<=row['deployedDepth']
  candidate=set(row['proof']['candidates']);groups=row['proof']['groups'];assert sorted(j for g in groups for j in g)==sorted(candidate)
  edge=set()
  for e in row['proof']['checks']:
   if e['incompatible']:
    u,v=ids.index(e['left']),ids.index(e['right']);assert not (co[u]&(1<<v)),e;edge.add(frozenset((e['left'],e['right'])));successful_edges+=1
  for group in groups:
   for u,v in itertools.combinations(group,2):assert frozenset((u,v)) in edge
  assert len(groups)+1==row['bounds']['discrete']
  exact=[x['choices'] for x in row['oracle']['records'] if x['worstTieRank']==truebest];assert row['oracle']['choices'] in exact
  checked+=visited;report.append({'id':row['id'],'states':visited,'oracle':truebest,'safe':True})
 out={'cases':len(rows),'exactCasesChecked':len(report),'statesChecked':checked,'independentTokenDocumentScores':factors,'independentlyVerifiedConflictEdges':successful_edges,'allBoundsSoundOnEnumeratedStates':True,'familySplitDisjoint':True,'arbitraryPrecisionPythonIntegers':True,'seconds':time.perf_counter()-start,'rows':report}
 a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(out,indent=2));print(json.dumps({k:v for k,v in out.items() if k!='rows'},indent=2))
if __name__=='__main__':main()
