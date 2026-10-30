"""Pinned, attributed optional spelling channel. No codespell code is imported."""
from pathlib import Path
import hashlib,json,re,urllib.request
ROOT=Path(__file__).resolve().parent
REV='4ce1caed2f97a50031225545c9697d9ef885c09b'
URL=f'https://raw.githubusercontent.com/codespell-project/codespell/{REV}/codespell_lib/data/dictionary.txt'
def main():
 import argparse
 p=argparse.ArgumentParser();p.add_argument('--data-dir',type=Path,required=True);a=p.parse_args();a.data_dir.mkdir(parents=True,exist_ok=True)
 b=urllib.request.urlopen(URL,timeout=60).read();words=set()
 for filename in ['demo-corpus.json','query-seeds.json']:
  for s in re.findall(r'[A-Za-z]+',(a.data_dir/filename).read_text()):words.add(s.lower())
 reverse={};pairs=0
 for line in b.decode().splitlines():
  if '->' not in line or line.startswith('#'):continue
  wrong,right=line.split('->',1);wrong=wrong.strip();right=right.strip()
  if re.fullmatch('[a-z]+',wrong) and re.fullmatch('[a-z]+',right) and right in words and wrong!=right:
   reverse.setdefault(right,[]).append(wrong);pairs+=1
 reverse={k:sorted(set(v))[:8] for k,v in sorted(reverse.items())};selected=sum(map(len,reverse.values()))
 (a.data_dir/'typos.json').write_text(json.dumps(reverse,ensure_ascii=False,indent=2))
 meta={'resource':'codespell spelling dictionaries','revision':REV,'source_url':URL,'source_sha256':hashlib.sha256(b).hexdigest(),'upstream_bytes':len(b),'license':'CC-BY-SA-3.0','license_url':'https://creativecommons.org/licenses/by-sa/3.0/',
  'attribution':'codespell contributors; dictionary originated from Wikipedia and subsequent project contributions; see upstream README',
  'license_source':f'https://github.com/codespell-project/codespell/blob/{REV}/README.rst#L430-L456',
  'changes':'Filter single ASCII-word unique corrections whose targets occur in authored inputs; invert correction direction; sort and retain first8 errors per target. No frequency interpretation.',
  'eligible_pairs_before_cap':pairs,'selected_pairs':selected,'target_words':len(reverse),'data_nature':'curated dictionary transplanted into authored queries is semi-synthetic, not natural query logs','code_license':'MIT; no GPL code copied','synthetic_corpus_license':'CC0-1.0','combined_audit_dataset_license':'CC-BY-SA-3.0'}
 (a.data_dir/'data-license.json').write_text(json.dumps(meta,ensure_ascii=False,indent=2));print('Pinned dictionary imported:',len(reverse),'targets;',selected,'selected alternative pairs')
if __name__=='__main__':main()
