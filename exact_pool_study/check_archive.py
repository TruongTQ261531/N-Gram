"""Offline full artifact/proof/supplement verification, numpy only."""
from pathlib import Path
import gzip,hashlib,json,subprocess,sys,tempfile,unicodedata,statistics
import numpy as np
ROOT=Path(__file__).resolve().parent

def read(path):
    with gzip.open(path,'rt') as f:return [json.loads(x) for x in f]
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()

def main():
    manifest=(ROOT/'checksums.sha256').read_text().splitlines()
    for line in manifest:
        h,p=line.split('  ',1);assert sha(ROOT.parent/p)==h,p
    for name in ['freeze.json','session_freeze.json','factor_freeze.json']:
        for p,h in json.loads((ROOT/name).read_text())['files'].items():assert sha(ROOT.parent/p)==h,(name,p)
    selection=json.loads((ROOT/'selection.json').read_text());analysis=json.loads((ROOT/'results/analysis.json').read_text());total_sessions=0
    for ds in ('arguana','scidocs'):
        d=ROOT/'results'/ds;rows=read(d/'records.jsonl.gz');audits=read(d/'session-audit.jsonl.gz');factors=read(d/'factor-audit.jsonl.gz')
        assert [x['queryId'] for x in rows]==selection[ds]['ids'] and len(rows)==16
        assert [x['queryId'] for x in audits]==[x['queryId'] for x in factors]==selection[ds]['ids']
        ids=json.loads((d/'document-ids.json').read_text());env=json.loads((d/'environment.json').read_text());assert len(ids)==len(set(ids))==env['documents'] and ids==sorted(ids)
        score_cells=0
        for row,audit,factor in zip(rows,audits,factors):
            assert hashlib.sha256(row['query'].encode()).hexdigest()==selection[ds]['querySha256'][row['queryId']]
            norm=' '.join(unicodedata.normalize('NFC',row['query']).lower().split());assert [fs[0]['text'] for fs in row['forms']]==norm.split()
            assert not row['metadata']['truncated'] and row['metadata']['usedTokens']==len(norm.split())
            assert row['queryId'] not in selection[ds]['excludedPriorIds']
            if ds=='arguana':assert row['queryId'].rsplit('-',1)[0] not in selection[ds]['excludeArguanaTopicFamilies']
            with np.load(d/row['factorFile']) as z:
                R=z['scores'];mapping=z['mapping'];F=[]
                assert R.dtype==np.int64 and R.shape[1]==len(ids) and len(R)==len(row['uniqueFormTexts'])
                assert len(set(row['uniqueFormTexts']))==len(R)
                for t,fs in enumerate(row['forms']):
                    indices=mapping[t,:len(fs)];assert all(0<=int(i)<len(R) for i in indices)
                    assert [row['uniqueFormTexts'][int(i)] for i in indices]==[f['text'] for f in fs]
                    F.append(R[indices])
                score_cells+=R.size
            base=sum(f[0] for f in F)
            assert audit['distinctAvailableIn20']==len({x['query'] for x in audit['requests']})==20
            expected=[]
            for request in audit['requests']:
                edits=request['edits'];assert len(edits)<=2 and len({t for t,a in edits})==len(edits)
                choices={int(t):int(a) for t,a in edits}
                assert all(0<a<len(F[t]) for t,a in choices.items())
                text=' '.join(' '.join(fs[choices.get(t,0)]['text'] for t,fs in enumerate(row['forms'])).split());assert text==request['query']
                score=base.copy()
                for t,a in choices.items():score+=F[t][a]-F[t][0]
                expected.append(np.flatnonzero(score>=np.sort(score)[-10]).tolist())
            for scenario in ['distinct20','repeat10x2']:
                indices=list(range(20)) if scenario=='distinct20' else list(range(10))*2
                truth=[expected[i] for i in indices];stored=audit['scenarios'][scenario];assert stored['requestIndices']==indices and stored['expectedTopK']==truth
                h=hashlib.sha256(json.dumps(truth,separators=(',',':')).encode()).hexdigest()
                for records,count in [(stored['records'],15),(factor['scenarios'][scenario]['records'],18)]:
                    assert len(records)==count
                    for z in records:
                        assert z['answerSha256']==h and 0<z['prefix5Seconds']<=z['total20Seconds']
                        assert z['order'].count(z['method'])==1
                    total_sessions+=len(records)
            assert factor['allArchivedFactorsEqual'] and factor['uniqueFormsScored']==len(row['uniqueFormTexts'])
            assert all(len(v)==3 and all(x>0 for x in v) for v in factor['factorSeconds'].values())
        source=json.loads((d/'source-replay.json').read_text());assert source['mismatches']==0 and source['queries']==16 and source['integerTokenDocumentScores']==score_cells and source['modelHash']==env['modelHash']
        rebuilt=json.loads((d/'index-rebuild.json').read_text())
        assert rebuilt['matchesFrozenStoredIntegerIndex'] and rebuilt['sourceFilesHashChecked'] and not rebuilt['frozenParentFilesModified']
        assert rebuilt['modelHash']==env['modelHash'] and rebuilt['documents']==len(ids)
        with tempfile.TemporaryDirectory(prefix='exact-pool-verify-') as td:
            out=Path(td)/'report.json';subprocess.run([sys.executable,str(ROOT/'verify.py'),'--dataset',ds,'--output',str(out)],check=True)
            actual=json.loads(out.read_text());previous=json.loads((d/'verification.json').read_text())
            for key,value in previous.items():
                if key!='seconds':assert actual[key]==value,(ds,key)
        summary=next(x for x in analysis['summary'] if x['dataset']==ds)
        assert summary['queries']==16 and summary['completeQueries']==16
        assert summary['meanLegacyPool']==statistics.mean(len(x['approximations']['legacyPool']) for x in rows)
        assert summary['meanExactPool']==statistics.mean(len(x['exactModes']['rank']['pool']) for x in rows)
        assert actual['missingOrExtraOracleDocuments']==0
    print(f'Verified {len(manifest)} manifest files,3 source freezes,32 complete new queries, full-corpus safe projections, original-state independent oracles, quotient traces/witnesses, source replay and {total_sessions} supplemental timed-session answer hashes.')
if __name__=='__main__':main()
