"""Combinatorial claim checks against the actual first-fit query scheduler."""
import itertools,unittest
from unittest.mock import patch
import numpy as np
from reviewer_audit_2026_10_31.retention import cover_bound
from argon_followup_2026_11_01.schedule_certificate import certificate

PAIRS=list(itertools.combinations(range(4),2))


def groups_of_known_graph(edges):
    groups=[]
    for v in range(4):
        g=next((g for g in groups if all(tuple(sorted((u,v))) in edges for u in g)),None)
        if g is None:groups.append([v])
        else:g.append(v)
    return groups


def query_schedule(edges):
    factors=[np.arange(4,dtype=float).reshape(1,4)]
    def oracle(D,Du,budget):
        pair=tuple(sorted(int(v) for v in D[0][0]))
        return {'incompatible':pair in edges,'method':'test_oracle'}
    with patch('compatibility.incompatible',side_effect=oracle):
        graph=cover_bound(factors,factors,1,max_checks=100,max_candidates=80)
    certificate(graph['groups'],graph['checks'])
    return graph


class GraphReview(unittest.TestCase):
    def test_actual_query_schedule_last_representatives_all_64_oracles(self):
        for mask in range(64):
            edges={pair for j,pair in enumerate(PAIRS) if mask&(1<<j)}
            g=query_schedule(edges)
            for group in g['groups']:
                self.assertTrue(all(pair in edges for pair in itertools.combinations(sorted(group),2)))

    def test_stronger_oracle_can_weaken_cover_without_caps(self):
        e={(0,2),(1,3)};a=query_schedule(e);b=query_schedule(e|{(0,1)})
        self.assertEqual(a['groups'],[[0,2],[1,3]])
        self.assertEqual(b['groups'],[[0,1],[2],[3]])
        self.assertLess(len(a['checks']),100);self.assertLess(len(b['checks']),100)
        # The stronger oracle's on-demand receipt omits the unqueried (1,3).
        self.assertNotIn((1,3),{(x['left'],x['right']) for x in b['checks']})

    def test_completed_graph_first_fit_is_not_monotone(self):
        worsened=0;transitions=0
        for mask in range(64):
            e={pair for j,pair in enumerate(PAIRS) if mask&(1<<j)}
            for pair in set(PAIRS)-e:
                transitions+=1;worsened+=len(groups_of_known_graph(e|{pair}))>len(groups_of_known_graph(e))
        self.assertEqual((transitions,worsened),(192,3))

    def test_additive_separation_integer_scaled_instances(self):
        for m in range(2,65):
            edited=[[m-1 if i==j else -1 for j in range(m)] for i in range(m)]
            self.assertEqual(max(sum(v>=0 for v in row) for row in edited),1)
            self.assertTrue(all(sum(row[j] for row in edited)==0 for j in range(m)))


if __name__=='__main__':unittest.main()
