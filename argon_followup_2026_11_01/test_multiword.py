import tempfile,unittest
from pathlib import Path
from argon_followup_2026_11_01.multiword import select,membership


class MultiwordTests(unittest.TestCase):
    def test_two_changed_tokens_require_two_budget_units(self):
        a=membership('cat dog','cta dgo',1);b=membership('cat dog','cta dgo',2)
        self.assertEqual(a['status'],'outside_channel_or_budget')
        self.assertEqual(b['minimumCostWithinBudget'],2)
        self.assertEqual(len(b['operations']),2)

    def test_selection_does_not_filter_to_channel_or32token_scope(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp)
            for split in ['dev','test']:
                d=root/split;d.mkdir()
                source=['cta dgo','completely unrelated words',' '.join(['misspelt']*40)]
                target=['cat dog','a small sentence',' '.join(['correct']*40)]
                (d/(split+'.src')).write_text('\n'.join(source)+'\n')
                for suffix in ['ref0','spellchecked.src']:(d/(split+'.'+suffix)).write_text('\n'.join(target)+'\n')
            panels,counts=select(root)
            self.assertEqual(counts['human_ref0']['eligible'],3)
            self.assertEqual(len(panels['human_ref0']),3)
            self.assertTrue(any(len(v['target'].split())>32 for v in panels['human_ref0'].values()))


if __name__=='__main__':unittest.main()
