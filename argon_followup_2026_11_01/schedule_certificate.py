"""Explicit optimality witness for the original first-fit QUERY graph.

This does not say greedy coloring is optimal on arbitrary or completed graphs.
It applies only to edges disclosed by that particular first-fit query schedule.
"""
import itertools


def certificate(groups,checks):
    known={tuple(sorted((r['left'],r['right']))) for r in checks if r['incompatible']}
    representatives=[g[-1] for g in groups]
    assert all(tuple(sorted((i,j))) not in known for i,j in itertools.combinations(representatives,2))
    assert all(tuple(sorted((i,j))) in known for g in groups for i,j in itertools.combinations(g,2))
    return {'groups':len(groups),'compatibleCliqueWitness':representatives,'chiEqualsOmega':True,
            'scope':'Only original on-demand first-fit query graph, not a completed graph'}
