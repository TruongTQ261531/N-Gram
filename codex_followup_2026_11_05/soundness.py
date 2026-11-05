"""Independent complete tiny-domain oracle: manual grams and dyadic integers."""
import os
for key in ['OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS','NUMEXPR_NUM_THREADS']:os.environ[key]='1'
import gzip,hashlib,itertools,json,unicodedata,warnings
from collections import Counter
from pathlib import Path
from scipy.optimize import OptimizeWarning
from codex_followup_2026_11_05.experiments import CONFIG,context,kernel
from reviewer_audit_2026_10_31.retention import native
from core import Index,variants

ROOT=Path(__file__).resolve().parent


def counts(text):
    answer=Counter()
    for t in unicodedata.normalize('NFC',text).casefold().split():
        padded=' '+t+' '
        for width in [3,4,5]:
            for start in range(max(0,len(padded)-width+1)):answer[padded[start:start+width]]+=1
    return answer


def exact_oracle(index,text,ref):
    # Index construction/channel define the contract. Feature evaluation, score
    # accumulation, budget filtering and worst ranks below are independent.
    tokens=unicodedata.normalize('NFC',text).casefold().split()
    forms=[variants(t)[0] for t in tokens]
    ratios=[[float(x).as_integer_ratio() for x in row] for row in index.W.toarray()]
    denominator=max(q for row in ratios for _,q in row)
    weights=[[num*(denominator//den) for num,den in row] for row in ratios]
    vocab=index.v.vocabulary_;factors=[]
    for options in forms:
        factors.append([[sum(c*weights[d][vocab[g]] for g,c in counts(t).items() if g in vocab)
                         for d in range(index.n)] for t in options])
    worst={1:0,2:0,3:0};witness={};states={1:0,2:0,3:0}
    for choices in itertools.product(*(range(len(f)) for f in forms)):
        cost=sum(a!=0 for a in choices)
        if cost>3:continue
        scores=[sum(factors[i][a][d] for i,a in enumerate(choices)) for d in range(index.n)]
        rank=1+sum(scores[j]>=scores[ref] for j in range(index.n) if j!=ref)
        for budget in [1,2,3]:
            if cost<=budget:
                states[budget]+=1
                if rank>worst[budget]:worst[budget]=rank;witness[budget]=list(choices)
    return worst,states,witness,denominator


def fixtures():
    stable=' '.join(variants('alpha')[0]+variants('beta')[0])
    yield 'stable','alpha',[stable]+['zzzz qqqq']*15
    yield 'stable_repeated','alpha alpha',[stable]+['zzzz qqqq']*15
    yield 'stable_two','alpha beta',[stable]+['zzzz qqqq']*15
    yield 'all_ties','cat dog',['cat dog']*16
    yield 'single_empty_deletion','a',['a cat','a dog','aaaa']+['zzzz']*13
    yield 'repeated_empty_deletions','a a',['a a cat','a dog','aaaa']+['zzzz']*13
    yield 'oov','zzzxxy',['alpha beta','cat dog']*8
    yield 'casefold','A ß',['a ss cat','ss','a','cat']*4
    yield 'mixed_oov','alpha zzzxxy',['alpha beta','cat dog','alpha','beta']*4
    yield 'three_positions','aa bb cc',['aa bb cc','aa bb','bb cc','aa cc','aa','bb','cc','abc']*2
    yield 'repeated_mixed','cat cat dog',['cat cat dog','cat dog','cat','dog']*4
    yield 'boundary_neighbours','ab ba',['ab ba','ab','ba','aba','baa','bb','aa','x']*2


def main():
    warnings.filterwarnings('ignore',category=OptimizeWarning)
    warnings.filterwarnings('ignore',message='Unrecognized options detected.*',category=RuntimeWarning)
    rows=[];path=ROOT/'results/correctness_cases.jsonl'
    with path.open('x') as f:
        for name,text,docs in fixtures():
            index=Index(docs,[f'd{j:02}' for j in range(len(docs))])
            ref=int(index.query(text).rankings()[0]);worst,states,witness,den=exact_oracle(index,text,ref)
            for budget in [1,2,3]:
                for method in CONFIG:
                    C=context(index,text,budget,screen=CONFIG[method].get('screen',True));assert C['ref']==ref
                    rank,detail=kernel(C,method,budget)
                    row={'case':name,'query':text,'documents':docs,'budget':budget,'method':method,'reference_id':str(index.ids[ref]),
                         'rank_upper':rank,'exact_worst_rank':worst[budget],'states':states[budget],
                         'worst_witness_choices':witness[budget],'dyadic_common_denominator':str(den),
                         'n':index.n,'sound':rank>=worst[budget],
                         'nonvacuous_K_certificates':[k for k in [1,5,10] if rank<=k<index.n],
                         'context_status':C['status'],'detail':native(detail)}
                    f.write(json.dumps(row,sort_keys=True)+'\n');rows.append(row)
                    if not row['sound']:raise AssertionError(f'UNSOUND: {name}, B={budget}, {method}')
            print(name,states,worst,flush=True)
    summary={'cases':12,'method_budget_checks':len(rows),'unsound':sum(not r['sound'] for r in rows),
             'nonvacuous_positive_method_budget_checks':sum(bool(r['nonvacuous_K_certificates']) for r in rows),
             'oracle':'manual NFC/casefold grams; exact stored-float dyadic integer arithmetic; complete Cartesian product with changed-position filtering',
             'limitations':'tiny synthetic domains only; channel and stored index define the common contract; not an independent reconstruction of index training'}
    (ROOT/'results/soundness_summary.json').write_text(json.dumps(summary,indent=2)+'\n');print(summary,flush=True)


if __name__=='__main__':main()
