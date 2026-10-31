"""Mathematical domain fixtures; not a native-image or NLP speed benchmark."""
from fractions import Fraction
from pathlib import Path
import itertools
import json

ROOT=Path(__file__).resolve().parent


def free_vote_worst_rank(clean,reference,budget):
    """Single-region independent vote allocation with unfavorable ties.

    Equivalent to the smallest-tie-cost condition in CostCert Sec3.4:
    spend on competitors in ascending order of their clean-vote deficits.
    This is a mathematical specialization, not execution of author software.
    """
    if not isinstance(budget,int) or budget<0 or any(int(x)!=x or x<0 for x in clean):
        raise ValueError('Nonnegative integer vote counts/budget required')
    if not 0<=reference<len(clean):raise ValueError('Invalid reference')
    deficits=sorted(max(0,clean[reference]-value) for j,value in enumerate(clean) if j!=reference)
    promoted=0;spent=0
    for cost in deficits:
        if spent+cost>budget:break
        spent+=cost;promoted+=1
    return 1+promoted


def enumerate_free_votes(clean,reference,budget):
    best=0
    for labels in itertools.product(range(len(clean)),repeat=budget):
        votes=list(clean)
        for label in labels:votes[label]+=1
        rank=sum(value>=votes[reference] for value in votes)
        best=max(best,rank)
    return best


def bundle_fixture(m):
    # One clean vote for r; a shared choice assigns ALL m other votes to
    # r (raw), or to exactly one competitor. It cannot split the bundle.
    states=[[m+1]+[0]*m]
    for j in range(m):
        state=[1]+[0]*m;state[j+1]=m;states.append(state)
    worst=max(sum(v>=state[0] for v in state) for state in states)
    relaxed=free_vote_worst_rank([1]+[0]*m,0,m)
    oracle=enumerate_free_votes([1]+[0]*m,0,m)
    assert worst==2 and relaxed==oracle==m+1
    return {'competitors':m,'mutableVotes':m,'fixedCleanVotes':[1]+[0]*m,
        'allowedBundledStates':states,'finiteBundleWorstRank':worst,
        'independentAllocationWorstRank':relaxed,
        'interpretation':'The free-vote relaxation is sound but omits bundle attainability. This is not a failure of CostCert on its declared input model.'}


def region_fixture():
    records=[[Fraction(1),Fraction(0),Fraction(0)],
             [Fraction(0),Fraction(1),Fraction(1)],[Fraction(5,8)]*3]
    witnesses=[];finite=set();continuous=set()
    for w1 in [Fraction(1,4),Fraction(3,4),Fraction(1,2)]:
        w=[w1,Fraction(3,40),1-w1-Fraction(3,40)]
        scores=[sum(x*y for x,y in zip(p,w)) for p in records]
        top=[j+1 for j,value in enumerate(scores) if value==max(scores)]
        continuous.update(top)
        if w1!=Fraction(1,2):finite.update(top)
        witnesses.append({'weights':list(map(str,w)),'scores':list(map(str,scores)),'top1':top})
    assert finite=={1,2} and continuous=={1,2,3}
    return {'records':[[str(x) for x in p] for p in records],
        'continuousRegion':{'w1':['1/4','3/4'],'w2':['1/20','1/10'],'w3':'1-w1-w2'},
        'finiteAllowedWeights':[witnesses[0]['weights'],witnesses[1]['weights']],
        'finiteUnion':sorted(finite),'continuousUnion':sorted(continuous),'witnesses':witnesses,
        'scope':'Domain/output counterexample, not a claim that RSA/JAA cannot be adapted.'}


def main():
    report={'kind':'Mathematical contract fixtures, not additional corpus evidence',
        'costcertSingleRegionBundleExamples':[bundle_fixture(m) for m in range(2,6)],
        'utkFiniteVsConvex':region_fixture(),
        'noveltyClaim':False,'authorCodeExecution':'Separate native UTK report; no author CostCert execution claimed'}
    path=ROOT/'results/contract_fixtures.json'
    if path.exists():assert json.loads(path.read_text())==report
    else:path.write_text(json.dumps(report,indent=2)+'\n')
    print('PASS: exact allocation and finite/convex domain fixtures; no empirical SOTA inference')


if __name__=='__main__':main()
