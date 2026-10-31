"""Run only the predeclared bounded NLP segment pilot, preserving old evidence."""
import os
for key in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS','NUMEXPR_NUM_THREADS'):
    os.environ[key] = '1'
import argparse
import gzip
import hashlib
import json
from pathlib import Path
import pickle
import platform
import resource
import signal
import subprocess
import time
from datetime import datetime, timezone
import numpy as np
import pandas as pd
from reviewer_audit_2026_10_31.bridge import states
from reviewer_audit_2026_10_31.native_utk import parse_ids
from lazy_cert_study.core import lattice
from utk_adapter_study.adapter import embedding, endpoints, point_text, safe_pool, segment_union, selected_state

ROOT = Path(__file__).resolve().parent
REGION = '0.25 0.75 0.05 0.10\n'


def digest(path): return hashlib.sha256(path.read_bytes()).hexdigest()


def limits(): resource.setrlimit(resource.RLIMIT_AS, (2*1024**3, 2*1024**3))


def native(binary, cwd, method, env):
    command = [str(binary), '-d', '3', '-k', '10', '-f', str(cwd/'points.txt'),
               '-i', 'index.bin', '-q', str(cwd/'region.txt'), '-R', '0.1', '-m', method]
    started = time.perf_counter()
    with (cwd/(method+'.stdout.txt')).open('wb') as log:
        child = subprocess.Popen(command, cwd=cwd, env=env, stdout=log,
                                 stderr=subprocess.STDOUT, start_new_session=True, preexec_fn=limits)
        try:
            code = child.wait(timeout=1.0)
            result = {'status': 'EXITED' if code == 0 else 'ERROR', 'exitCode': code}
        except subprocess.TimeoutExpired:
            os.killpg(child.pid, signal.SIGKILL); child.wait()
            result = {'status': 'TIMEOUT', 'exitCode': child.returncode}
    result['wallSeconds'] = time.perf_counter()-started
    log_text = (cwd/(method+'.stdout.txt')).read_text(errors='replace')
    result['logSha256'] = digest(cwd/(method+'.stdout.txt'))
    if result['status'] == 'EXITED':
        try: result['reportedLocalIds'] = [i-1 for i in parse_ids(log_text)]
        except ValueError: result['status'] = 'UNPARSEABLE'
    return result


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--data', type=Path, required=True)
    p.add_argument('--binary', type=Path, required=True)
    p.add_argument('--source', type=Path, required=True)
    p.add_argument('--qhull-bin', type=Path, required=True)
    p.add_argument('--output', type=Path, required=True)
    p.add_argument('--work', type=Path, required=True)
    args = p.parse_args(); args.output.mkdir(parents=True, exist_ok=False)
    args.work.mkdir(parents=True, exist_ok=False)
    source_spec = json.loads((ROOT.parent/'lazy_cert_study/sources.json').read_text())
    for item in source_spec['files']:
        assert digest(args.data/item['path']) == item['sha256']
    old_report = json.loads((ROOT.parent/'reviewer_audit_2026_10_31/results/native_utk/guard-corrected/report.json').read_text())
    assert digest(args.binary) == old_report['binarySha256']
    for name, sha in old_report['localSourceHashes'].items(): assert digest(args.source/name) == sha
    with (args.data/'index.pkl').open('rb') as f: index = pickle.load(f)
    query = pd.read_csv(args.data/'dataset/query.csv', sep='\t', dtype={'query_id':str}).fillna('')
    texts = dict(zip(query.query_id, query['query']))
    with gzip.open(ROOT.parent/'lazy_cert_study/results/confirmation.jsonl.gz','rt') as f:
        old = [json.loads(line) for line in f]
    env = os.environ.copy(); env['PATH'] = str(args.qhull_bin.resolve())+os.pathsep+env['PATH']
    metadata = {'startedUTC': datetime.now(timezone.utc).isoformat(), 'retrospective': True,
        'scope': '128 actual NLP score segments, NOT the entire finite lattice or hull',
        'binarySha256': digest(args.binary), 'sourceHashes': old_report['localSourceHashes'],
        'upstream': old_report['upstream'], 'upstreamCommit': old_report['upstreamCommit'],
        'protocolSha256': digest(ROOT/'PROTOCOL.md'), 'python': platform.python_version(),
        'numpy': np.__version__, 'platform': platform.platform(),
        'cpu': next((s.split(':',1)[1].strip() for s in Path('/proc/cpuinfo').read_text().splitlines() if s.startswith('model name')), None),
        'oraclePairCap': 4_000_000, 'methodWallLimitSeconds': 1.0,
        'sourceFiles': source_spec['files'], 'codeHashes': {n:digest(ROOT/n) for n in ['adapter.py','run.py']},
        'thirdPartySourceRedistributed': False, 'nativeTimesIncludeLaunchAndRtree': True}
    (args.output/'metadata.json').write_text(json.dumps(metadata, indent=2)+'\n')
    with gzip.open(args.output/'records.jsonl.gz', 'xt') as out:
        for number, archived in enumerate(old, 1):
            qid = archived['queryId']; started = time.perf_counter()
            q = lattice(index, texts[qid]); state = selected_state(states(q.forms, 2), qid)
            a = (q.raw_features@index.transpose).toarray()[0]
            altered_text = ' '.join(f[s]['text'] for f,s in zip(q.forms,state))
            b = (index.vectorizer.transform([altered_text])@index.transpose).toarray()[0]
            coords, qa, qb, embedded = embedding(a,b)
            pi, original_screen = safe_pool(a,b,10); pq, export_screen = safe_pool(qa,qb,10)
            pool = np.union1d(pi,pq); pa = a[pool]; pb = b[pool]; eqa = qa[pool]; eqb = qb[pool]
            prepared = time.perf_counter()-started
            row = {'queryId':qid, 'querySha256': archived['querySha256'], 'tokens':len(q.forms),
                'state': state, 'pool':pool.tolist(), 'corpusSize':index.n, 'originalA':pa.tolist(),
                'originalB':pb.tolist(), 'exportA':eqa.tolist(), 'exportB':eqb.tolist(),
                'originalScreen':original_screen, 'exportScreen':export_screen, 'embedding':embedded,
                'preparationSeconds':prepared, 'originalFullLatticeUnion':archived['oracleUnion'],
                'endpointUnion': [int(pool[j]) for j in endpoints(pa,pb,10)], 'runs':{}}
            folder = args.work/qid; folder.mkdir()
            for name, value in [('points.txt',point_text(coords[pool])), ('region.txt',REGION)]:
                (folder/name).write_text(value)
            row['nativePointsSha256'] = digest(folder/'points.txt')
            oracle_start = time.perf_counter()
            trivial = (len(row['endpointUnion']) == len(pool) and
                       len(endpoints(eqa,eqb,10)) == len(pool))
            if len(pool)**2 > 4_000_000 and not trivial:
                row['oracleStatus'] = 'RESOURCE_UNKNOWN'; out.write(json.dumps(row)+'\n'); out.flush()
                print(number, qid, 'oracle cap', len(pool), flush=True); continue
            original = segment_union(pa,pb,10); exported = segment_union(eqa,eqb,10)
            row['oracleSeconds'] = time.perf_counter()-oracle_start
            row['oracleStatus'] = 'EXACT'
            row['originalSegmentWitnesses'] = {str(int(pool[j])):t for j,t in original.items()}
            row['exportSegmentWitnesses'] = {str(int(pool[j])):t for j,t in exported.items()}
            row['originalSegmentUnion'] = sorted(int(pool[j]) for j in original)
            row['exportSegmentUnion'] = sorted(int(pool[j]) for j in exported)
            row['extraOverEndpoints'] = sorted(set(row['originalSegmentUnion'])-set(row['endpointUnion']))
            row['extraOverFullFiniteLattice'] = sorted(set(row['originalSegmentUnion'])-set(archived['oracleUnion']))
            row['quantizationUnionEqual'] = row['originalSegmentUnion'] == row['exportSegmentUnion']
            methods = ['RSA','JAA']
            if int(hashlib.sha256(qid.encode()).hexdigest(),16) % 2: methods.reverse()
            for method in methods:
                result = native(args.binary.resolve(), folder, method, env)
                ids = result.get('reportedLocalIds')
                if ids is not None:
                    invalid = [j for j in ids if not 0 <= j < len(pool)]
                    result['invalidIds'] = invalid
                    reported = sorted(int(pool[j]) for j in ids if 0 <= j < len(pool))
                    result['reportedGlobalIds'] = reported
                    result['missing'] = sorted(set(row['exportSegmentUnion'])-set(reported))
                    result['extra'] = sorted(set(reported)-set(row['exportSegmentUnion']))
                    result['matchesExportOracle'] = not (invalid or result['missing'] or result['extra'])
                row['runs'][method] = result
                # Original stdout is redistributable execution output, not third-party source.
                (args.output/(qid+'-'+method+'.stdout.txt')).write_bytes((folder/(method+'.stdout.txt')).read_bytes())
                (folder/'index.bin').unlink(missing_ok=True)
            out.write(json.dumps(row,separators=(',',':'))+'\n'); out.flush()
            print(number, qid, 'pool',len(pool),'extras',len(row['extraOverFullFiniteLattice']),
                  {m:(v['status'],v.get('matchesExportOracle')) for m,v in row['runs'].items()},flush=True)
    metadata['finishedUTC'] = datetime.now(timezone.utc).isoformat()
    metadata['recordsSha256'] = digest(args.output/'records.jsonl.gz')
    (args.output/'metadata.json').write_text(json.dumps(metadata,indent=2)+'\n')


if __name__ == '__main__': main()
