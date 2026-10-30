"""Checksums, prospective freeze, exact selections and independent state replay."""
from pathlib import Path
import gzip,hashlib,json,subprocess,sys,tempfile,unicodedata
ROOT=Path(__file__).resolve().parent

def digest(path):return hashlib.sha256(path.read_bytes()).hexdigest()

def main():
    verified=0
    for line in (ROOT/'checksums.sha256').read_text().splitlines():
        expected,name=line.split('  ',1);assert digest(ROOT.parent/name)==expected,name;verified+=1
    freeze=json.loads((ROOT/'freeze.json').read_text())
    for name,expected in freeze['files'].items():assert digest(ROOT.parent/name)==expected,name
    analysis=json.loads((ROOT/'results/analysis.json').read_text())
    selection=json.loads((ROOT/'selection.json').read_text())
    for ds in ('arguana','scidocs'):
        d=ROOT/'results'/ds
        with gzip.open(d/'records.jsonl.gz','rt') as f:rows=[json.loads(x) for x in f]
        assert [row['queryId'] for row in rows]==selection[ds]['queryIds'] and len(rows)==64
        ids=json.loads((d/'document-ids.json').read_text());env=json.loads((d/'environment.json').read_text())
        assert len(ids)==len(set(ids))==env['documents']==selection[ds]['corpusDocuments'] and ids==sorted(ids)
        total_forms=0
        for row in rows:
            assert row['dataset']==ds and row['modelHash']==env['modelHash']
            normalized=' '.join(unicodedata.normalize('NFC',row['query']).lower().split()).split()
            assert [f[0]['text'] for f in row['forms']]==normalized[:16]
            assert row['metadata']['originalTokens']==len(normalized) and row['metadata']['truncated']==(len(normalized)>16)
            assert [(x['budget'],x['k']) for x in row['cases']]==[(1,5),(1,10),(2,5),(2,10)]
            for forms in row['forms']:
                raw=forms[0]['text'];assert forms[0]['op']=='raw' and len(forms)<=4 and len({x['text'] for x in forms})==len(forms)
                for form in forms[1:]:
                    i=form['position'];op=form['op']
                    if op=='delete':expected=raw[:i]+raw[i+1:]
                    elif op=='swap':expected=raw[:i]+raw[i+1]+raw[i]+raw[i+2:]
                    else:
                        assert op=='keyboard';expected=raw[:i]+form['replacement']+raw[i+1:]
                    assert expected==form['text'] and expected!=raw
                total_forms+=len(forms)
        source=json.loads((d/'source-replay.json').read_text())
        assert source['queries']==64 and source['mismatches']==0 and source['modelHash']==env['modelHash']
        assert source['independentTokenDocumentScores']==total_forms*len(ids)
        with tempfile.TemporaryDirectory(prefix='ngram-pool-verify-') as td:
            output=Path(td)/'verify.json'
            subprocess.run([sys.executable,str(ROOT/'verify.py'),'--dataset',ds,'--output',str(output)],check=True)
            actual=json.loads(output.read_text());expected=json.loads((d/'verification.json').read_text())
            for key,value in expected.items():
                if key!='seconds':assert actual[key]==value,(ds,key)
        assert actual['queries']==64 and actual['cases']==256 and actual['missingOracleDocuments']==0
        assert analysis['counts'][ds]['budgetStateChecks']==actual['states']
        for summary in (x for x in analysis['summary'] if x['dataset']==ds):
            cases=[next(x for x in row['cases'] if x['budget']==summary['budget'] and x['k']==summary['k']) for row in rows]
            for name in cases[0]['pools']:
                assert summary['mean_'+name]==sum(len(x['pools'][name]) for x in cases)/64
            assert summary['mean_exactUnion']==sum(len(x['oracleUnion']) for x in cases)/64
    print(f'Verified {verified} manifest files, prospective10-file freeze, all128 selected queries,512 cases, complete finite-state top-k traces, source-replay receipts and summaries.')

if __name__=='__main__':main()
