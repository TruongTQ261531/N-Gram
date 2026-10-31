"""Descriptive analysis only; unlike workloads and failed outputs stay visible."""
import gzip
import json
from pathlib import Path
import statistics

ROOT = Path(__file__).resolve().parent


def summary(rows):
    valid = [r for r in rows if r['oracleStatus'] == 'EXACT']
    result = {'queries':len(rows), 'exactOracles':len(valid),
        'oracleResourceUnknown':len(rows)-len(valid),
        'segmentsWithExtraOverEndpoints':sum(bool(r['extraOverEndpoints']) for r in valid),
        'segmentsWithExtraOverFullFiniteLattice':sum(bool(r['extraOverFullFiniteLattice']) for r in valid),
        'extraOverFullFiniteLatticeTotal':sum(len(r['extraOverFullFiniteLattice']) for r in valid),
        'quantizationUnionEqual':sum(r['quantizationUnionEqual'] for r in valid),
        'medianProjectedDocuments':statistics.median(len(r['pool']) for r in rows),
        'medianPreparationSeconds':statistics.median(r['preparationSeconds'] for r in rows),
        'methods':{},
        'scope':'Retrospective two-state NLP segments; not all states or the entire convex hull',
        'timingScope':'One run/method/query; native launch + parse + R-tree + solver; preparation separate',
        'universalSpeedOrQ1Claim':False}
    for method in ['RSA','JAA']:
        runs = [r['runs'][method] for r in valid]
        exited = [r for r in runs if r['status']=='EXITED']
        matched = [r for r in exited if r.get('matchesExportOracle')]
        result['methods'][method] = {
            'attempted':len(runs), 'exited':len(exited), 'timeout':sum(r['status']=='TIMEOUT' for r in runs),
            'errors':sum(r['status'] not in ('EXITED','TIMEOUT') for r in runs),
            'matchesExactExportedScoreUnion':len(matched),
            'exitedButDisagrees':sum(not r.get('matchesExportOracle') for r in exited),
            'withMissingIds':sum(bool(r.get('missing')) for r in exited),
            'withExtraIds':sum(bool(r.get('extra')) for r in exited),
            'medianWallSecondsAllAttempts':statistics.median(r['wallSeconds'] for r in runs),
            'medianWallSecondsCorrectOnly':statistics.median(r['wallSeconds'] for r in matched) if matched else None}
    return result


if __name__=='__main__':
    with gzip.open(ROOT/'results/records.jsonl.gz','rt') as f: rows=[json.loads(s) for s in f]
    result = summary(rows)
    (ROOT/'results/analysis.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2))
