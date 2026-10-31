"""Check complete records/freezes without downloading licensed corpora."""
from pathlib import Path
from fractions import Fraction
import gzip,hashlib,json

ROOT=Path(__file__).resolve().parent

def main():
    for name in ['DECISION_FREEZE.json','BUDGET_FREEZE.json','TYPO_FREEZE.json','WIDE_ENUM_FREEZE.json','BOUNDARY_FREEZE.json']:
        freeze=json.loads((ROOT/name).read_text())
        assert freeze['retrospective']
        for file,digest in freeze['files'].items():
            assert hashlib.sha256((ROOT.parent/file).read_bytes()).hexdigest()==digest,file
    with gzip.open(ROOT/'results/decisions.json.gz','rt') as f:decision=json.load(f)
    freeze=json.loads((ROOT/'DECISION_FREEZE.json').read_text());expected={(ds,qid) for ds,ids in freeze['replicationIds'].items() for qid in ids}
    rows=decision['rows'];assert len(rows)==970
    assert {(r['dataset'],r['queryId']) for r in rows}==expected
    counts={label:sum(r['label']==label for r in rows) for label in ['ROBUST','NONROBUST','UNKNOWN']}
    assert counts==decision['classification']=={'ROBUST':266,'NONROBUST':704,'UNKNOWN':0}
    for row in rows:
        if row['label']=='ROBUST':
            enclosure=row.get('positiveEnclosure') or row['resolutionEnclosure']
            assert enclosure['status']=='COMPLETE' and enclosure['rankUpper']<=10
        else:
            proof=row['exactWitness'];assert proof['proved'] and proof['rankLower']>10
            assert sum(a!=0 for a in proof['choices'])<=2
            if proof['reason']=='exact_zero_reference_nonnegative_index':assert proof['exactReference']=='0'
            else:
                assert len(set(proof['competitorIds']))==10 and row['referenceId'] not in proof['competitorIds']
                assert Fraction(proof['minimumExactMargin'])>=0
    budget_freeze=json.loads((ROOT/'BUDGET_FREEZE.json').read_text())
    for ds,ids in budget_freeze['timingPanelIds'].items():
        path=ROOT/'results/budgets'/(ds+'.jsonl.gz')
        with gzip.open(path,'rt') as f:records=[json.loads(line) for line in f]
        metadata=json.loads(path.with_name(path.name+'.metadata.json').read_text())
        assert metadata['status']=='COMPLETE' and len(records)==48
        assert metadata['rowsSha256']==hashlib.sha256(path.read_bytes()).hexdigest()
        assert metadata['freezeSha256']==hashlib.sha256((ROOT/'BUDGET_FREEZE.json').read_bytes()).hexdigest()
        assert [r['queryId'] for r in records]==ids
        for row in records:
            assert len(row['runs'])==6 and set(row['order'])==set(metadata['profiles'])
            assert {r['profile'] for r in row['runs']}==set(metadata['profiles'])
            assert all(r['seconds']>0 and r['rankUpper']>=1 for r in row['runs'])
    analysis=json.loads((ROOT/'results/analysis.json').read_text())
    assert analysis['status']=='COMPLETE' and analysis['decisionTotals']['robust']==266
    for dataset in analysis['budgetProfiles'].values():
        assert all(not p['unsafeNumericalDecisionIds'] for p in dataset['profiles'].values())
    widefreeze=json.loads((ROOT/'WIDE_ENUM_FREEZE.json').read_text())
    for ds,ids in widefreeze['timingPanelIds'].items():
        path=ROOT/'results/wide_enum'/(ds+'.jsonl.gz')
        with gzip.open(path,'rt') as f:records=[json.loads(line) for line in f]
        metadata=json.loads(path.with_name(path.name+'.metadata.json').read_text())
        assert metadata['status']=='COMPLETE' and [r['queryId'] for r in records]==ids
        assert metadata['rowsSha256']==hashlib.sha256(path.read_bytes()).hexdigest()
        assert metadata['freezeSha256']==hashlib.sha256((ROOT/'WIDE_ENUM_FREEZE.json').read_bytes()).hexdigest()
        assert all(len(r['runs'])==2 for r in records)
        assert all(not r['unsafeDecisionIds'] for r in analysis['wideEnumerationControl'][ds]['methods'].values())
    pilot=json.loads((ROOT/'results/typo-pilot.json').read_text());selection=json.loads((ROOT/'results/typo-pilot.selection.json').read_text())
    assert pilot['status']=='COMPLETE' and pilot['samplePairs']==len(pilot['rows'])==100
    assert not pilot['rawTextsRedistributed']
    assert [r['pairHash'] for r in pilot['rows']]==selection['selectedPairHashes']
    assert len(set(selection['selectedPairHashes']))==100 and selection['selectedPairHashes']==sorted(selection['selectedPairHashes'])
    assert sum(pilot['categories'].values())==100
    for budget in [1,2]:
        count=sum(r['status']=='covered' and r['minimumCostWithinBudget']<=budget for r in pilot['rows'])
        assert count==pilot['coverage'][str(budget)]['coveredNontrivialPairs']
    for row in pilot['rows']:
        assert 'erroneous' not in row and 'corrected' not in row
        if row['status']=='covered':assert row['minimumCostWithinBudget']==len(row['operations'])
    boundary=json.loads((ROOT/'results/boundary.json').read_text());freeze=json.loads((ROOT/'BOUNDARY_FREEZE.json').read_text())
    expected={(ds,qid) for ds,ids in freeze['queryIds'].items() for qid in ids}
    assert boundary['status']=='COMPLETE' and boundary['queries']==len(boundary['rows'])==8
    assert {(r['dataset'],r['queryId']) for r in boundary['rows']}==expected
    original={(r['dataset'],r['queryId']):r for r in rows}
    for row in boundary['rows']:
        assert len(row['runs'])==7 and original[(row['dataset'],row['queryId'])]['label']=='ROBUST'
        default=next(r for r in row['runs'] if r['profile']=='discrete_default')
        assert default['rankUpper']==original[(row['dataset'],row['queryId'])]['originalBounds']['discrete']
    for path in ROOT.rglob('*'):
        assert path.suffix.lower() not in {'.tex','.bib','.cls','.bst','.pdf','.parquet','.pkl','.dat'},path
    print('PASS:970 decisions,144x6 profiles,144x2 paired enumeration controls,100 preselected typo pairs,source freezes and no manuscript/raw corpus files')

if __name__=='__main__':main()
