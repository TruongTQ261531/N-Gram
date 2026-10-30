"""Verify frozen source, full data, summaries and independent rank oracle."""
from pathlib import Path
import gzip,hashlib,json,subprocess,sys,tempfile
ROOT=Path(__file__).resolve().parent.parent;A=ROOT/'application_study';R=A/'results'
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 for line in (A/'checksums.sha256').read_text().splitlines():
  h,p=line.split('  ',1);assert digest(ROOT/p)==h,p
 freeze=json.loads((A/'freeze.json').read_text())
 for p,h in freeze['files'].items():assert digest(ROOT/p)==h,p
 meta=json.loads((R/'dataset-manifest.json').read_text());data=(R/'audit-set.jsonl.gz').read_bytes();assert hashlib.sha256(data).hexdigest()==meta['gzipSha256'];raw=gzip.decompress(data);assert hashlib.sha256(raw).hexdigest()==meta['uncompressedSha256']
 assert data==(ROOT/'webapp/dist/data/audit-set.jsonl.gz').read_bytes()
 lines=raw.decode().splitlines();manifest=json.loads(lines[0]);rows=[json.loads(x) for x in lines[1:]];assert manifest['sourceFreeze']==freeze
 encode=lambda x:json.dumps(x,ensure_ascii=False,separators=(',',':')).encode()
 assert hashlib.sha256(encode(manifest['corpus'])).hexdigest()==meta['corpusHash']
 assert hashlib.sha256(encode({'version':manifest['engine'],'weights':manifest['weights']})).hexdigest()==meta['modelHash']
 seeds=json.loads((ROOT/'webapp/dist/data/query-seeds.json').read_text());expected=[q['id']+'|'+c+'|B'+str(b) for q in seeds for c in (['keyboard','curated','mixed'] if q['language']=='en' else ['keyboard','accents','mixed']) for b in [1,2]]
 assert [x['id'] for x in rows]==expected and len(expected)==288 and len(set(expected))==288
 summary=json.loads((R/'query-results.json').read_text());assert [x['id'] for x in summary]==expected
 for row,z in zip(rows,summary):
  assert row['family']==z['family'] and row['split']==z['split'] and row['budget']==z['budget'] and row['channel']==z['channel']
  assert row['bounds']['pairwise']==z['pair'] and row['bounds']['discrete']==z['cover'] and row['deployedDepth']==z['deployed'] and row['oracle'].get('rank')==z['gold']
 analysis=json.loads((R/'analysis.json').read_text());assert analysis['cases']==len(rows) and analysis['cover_improvement_cases']==sum(x['cover']<x['pair'] for x in summary)
 with tempfile.TemporaryDirectory(prefix='ngram-oracle-') as tmp:
  out=Path(tmp)/'verification.json';subprocess.run([sys.executable,str(A/'verify_oracle.py'),'--output',str(out)],check=True)
  actual=json.loads(out.read_text());original=json.loads((R/'independent-oracle.json').read_text())
  for k,v in original.items():
   if k!='seconds':assert actual[k]==v,k
 print('Verified: frozen10 files; complete288-case audit; model/corpus/content hashes; independent full integer oracle and source-family splits.')
if __name__=='__main__':main()
