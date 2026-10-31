# Equation-level boundary, with explicit source-access limits

This is a mathematical mapping of this implementation, not a new full-text
review or a runtime reproduction of the cited publications. Prior source
inspection levels remain in exact_pool_study/RELATED_WORK.md and
round3/RELATED_WORK_UPDATE.md. Fresh scholarly/API requests are blocked by
the active proxy policy; a saved environment draft is not published access.
Do not interpret the limited search as evidence of no equivalent algorithm.

## Mapping the pool problem to uncertain linear top-k

Flatten (original token position i, alternative a) into coordinates. Give
document j the vector p_j=(F[i,a,j]), and an admissible query the one-hot
vector x: exactly one alternative per position and at most B non-raw choices.
The score is p_j dot x. Since sum(x)=number of original tokens m, x/m lies
in the nonnegative unit simplex; dividing all scores by m changes no rank.
Thus this is uncertain linear top-k over a particular finite, correlated
weight domain. Possible-result unions, dominance and partitioning are not
new problem definitions. UTK is decisive prior art, not a distant analogy.

Replacing that finite domain by its convex hull can introduce documents
that win only at fractional states. For one position with two alternatives,
consider document-score vectors (4,0), (0,4), (3,3). At either allowed
one-hot choice the third document is NOT top1; at the half-half convex
combination it is the strict winner (3 versus2,2). All numbers are
nonnegative integers. This is an additive-factor example, not a claim that
these exact factors are realized by the fixed BM25 corpus/channel.

Consequently a continuous-domain UTK result can be a safe coarse superset
without being the exact discrete union. This explains a contract difference;
it does NOT show that existing UTK enumeration/partition algorithms cannot
be adapted to the finite domain, nor establish originality of doing so.
The parent rank quotient and this screen are candidate specializations.

## Shared-budget retention and CostCert

For reference r, let M_j(a)=sum_i(F[i,a_i,j]-F[i,a_i,r]). Worst-tie rank is
1+max_a sum_j 1[M_j(a)>=0]. The same a and budget constrain every competitor.
Summing separate pairwise possibilities loses these correlations. CostCert
already recognizes shared-budget overcounting for its voting/patch setting.
The present implementation uses arbitrary additive document margins and a
partition-constrained finite choice per token, rather than assuming a token
is one interchangeable vote. These are different input contracts; it is
still necessary to inspect whether a bundled/weighted reduction makes the
complete optimization algorithm equivalent. No non-equivalence theorem has
been proved. Report this as unresolved, not “CostCert does not apply”.

## The discrete layer is a valid-inequality specialization

Introduce promotion indicators z_j. If no admissible query makes both
M_j and M_l nonnegative, z_j+z_l<=1 is valid. Every incompatibility clique C
therefore satisfies sum_{j in C}z_j<=1. A disjoint clique cover upper-bounds
the total simultaneous promotions. Pareto DP proves some incompatibilities;
resource caps omit edges and only weaken the bound. These are established
conflict-graph/clique inequalities and dynamic-programming principles.
The project must be judged on its specific specialization, measured gain
and inspectable numerical treatment, not inventing clique cuts or DP.

## What has and has not been compared

- Executed here: parent compiled projection/rank quotient, ordinary batched
  full-query enumeration, both screened versions, memo and incremental
  scoring, under one identical index and channel.
- Earlier executed: matched shared LP, generic LP, budget-limited full
  enumeration, generic time-limited MILP and discrete cover in round3.
- Not executed: original UTK RSA/JAA, original CostCert code on its native
  data, production fuzzy search or modern neural rankers on this workload.
  Different tasks cannot be ranked by comparing headline percentages.
- Not completed: systematic closest-method equivalence review, independent
  mathematical review, and current journal quartile verification.
