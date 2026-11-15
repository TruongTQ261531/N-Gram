"""Frozen, bounded exploratory sensitivity/ablation panel (one warm-index pass)."""
import os
for key in ['OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS','NUMEXPR_NUM_THREADS']:os.environ[key]='1'
import argparse,gzip,hashlib,json,platform,resource,threading,time,warnings
from pathlib import Path
from scipy.optimize import OptimizeWarning
from codex_followup_2026_11_05.experiments import CONFIG,context,kernel
from reviewer_audit_2026_10_31.retention import load_inputs,normalize,native

ROOT=Path(__file__).resolve().parent


def rss_mib():
    for line in Path('/proc/self/status').read_text().splitlines():
        if line.startswith('VmRSS:'):return int(line.split()[1])/1024


class Monitor:
    def __enter__(self):
        self.start=rss_mib();self.peak=self.start;self.done=threading.Event();self.samples=1
        def loop():
            while not self.done.wait(.020):
                self.peak=max(self.peak,rss_mib());self.samples+=1
        self.thread=threading.Thread(target=loop,daemon=True);self.thread.start();return self
    def __exit__(self,*args):
        self.peak=max(self.peak,rss_mib());self.samples+=1;self.done.set();self.thread.join()


def main():
    p=argparse.ArgumentParser();p.add_argument('--data',type=Path,required=True);a=p.parse_args()
    warnings.filterwarnings('ignore',category=OptimizeWarning)
    warnings.filterwarnings('ignore',message='Unrecognized options detected.*',category=RuntimeWarning)
    freeze=json.loads((ROOT/'FREEZE.json').read_text())
    for path,sha in freeze['code_sha256'].items():
        assert hashlib.sha256((ROOT.parent/path).read_bytes()).hexdigest()==sha,path
    selection=json.loads((ROOT/'selection.json').read_text());output=ROOT/'results/ablation_records.jsonl.gz'
    begin=time.perf_counter();count=0;status={'status':'running','completed':0,'planned':684}
    with gzip.open(output,'xt') as f:
        for ds,selected in selection['datasets'].items():
            index,texts,fingerprint=load_inputs(a.data,ds)
            for item in selected:
                qid=item['queryId'];text=' '.join(normalize(texts[qid]).split()[:32])
                for budget in [2,1,3]:
                    methods=list(CONFIG) if budget==2 else ['pair_enum','best_lp_enum','discrete','milp_enum']
                    methods.sort(key=lambda m:hashlib.sha256(f'ipm-order-v1|{ds}|{qid}|{budget}|{m}'.encode()).hexdigest())
                    for method in methods:
                        if time.perf_counter()-begin>4500:raise TimeoutError('Frozen 75 minute study wall cap; retain completed rows')
                        with Monitor() as memory:
                            t=time.perf_counter();C=context(index,text,budget,screen=CONFIG[method].get('screen',True))
                            t1=time.perf_counter();rank,detail=kernel(C,method,budget);end=time.perf_counter()
                        row={'dataset':ds,'query_id':qid,'query_sha256':hashlib.sha256(text.encode()).hexdigest(),
                             'budget':budget,'method':method,'rank_upper':rank,'reference_id':str(index.ids[C['ref']]),
                             'model_fingerprint':fingerprint,'length_quartile':item['lengthQuartile'],
                             'used_tokens':item['usedTokens'],'context_seconds':t1-t,'kernel_seconds':end-t1,
                             'pipeline_seconds':end-t,'context':{k:v for k,v in C.items() if k not in ['docs','candidate','D','Du','lower']},
                             'detail':detail,'rss_start_mib':memory.start,'rss_sampled_peak_mib':memory.peak,
                             'rss_sample_count':memory.samples,'process_cumulative_hwm_mib':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss/1024}
                        f.write(json.dumps(native(row),sort_keys=True)+'\n');f.flush();count+=1
                        status.update(completed=count,elapsed_seconds=time.perf_counter()-begin,last=f'{ds}:{qid}:B{budget}:{method}')
                        (ROOT/'results/progress.json').write_text(json.dumps(status,indent=2)+'\n')
                        if count%19==0:print(json.dumps(status),flush=True)
    assert count==684
    status['status']='complete';(ROOT/'results/progress.json').write_text(json.dumps(status,indent=2)+'\n')
    print(json.dumps(status),flush=True)


if __name__=='__main__':main()
