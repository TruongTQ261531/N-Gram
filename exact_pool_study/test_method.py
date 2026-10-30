import itertools,unittest
import numpy as np
from method import CompiledBounds,compiled_pool,exact_from_pool,legacy

def brute(F,b,k):
    out=set()
    for a in itertools.product(*(range(len(f)) for f in F)):
        if sum(v!=0 for v in a)>b:continue
        score=sum(f[v] for f,v in zip(F,a));threshold=sorted(score.tolist())[-k]
        out.update(j for j,v in enumerate(score) if v>=threshold)
    return out

class Tests(unittest.TestCase):
    def test_compiled_conditional_bounds(self):
        rng=np.random.default_rng(7719)
        for _ in range(100):
            F=[rng.integers(0,50,(int(rng.integers(1,5)),11),dtype=np.int64) for _ in range(int(rng.integers(2,7)))]
            for b in (0,1,2):
                C=CompiledBounds(F,b)
                for values in itertools.product(range(len(F[0])),range(len(F[1]))):
                    if sum(v!=0 for v in values)>b:continue
                    fixed=dict(enumerate(values));a=legacy.envelopes(F,b,fixed);z=C.envelopes(fixed)
                    for x,y in zip(a,z):np.testing.assert_array_equal(x,y)
                p,_=compiled_pool(F,b,3);old,_=legacy.candidate_pools(F,b,3,include_fixed=False)
                np.testing.assert_array_equal(p,old['partitioned'])

    def test_all_quotients_match_complete_oracle(self):
        rng=np.random.default_rng(7720)
        for _ in range(80):
            # Identical effect sets with position-specific common shifts.
            original=rng.integers(0,50,(4,9),dtype=np.int64)
            F=[original.copy(),original+rng.integers(0,8,(4,1)),rng.integers(0,50,(3,9),dtype=np.int64)]
            forms=[[{'text':str(t)+'-'+str(a)} for a in range(len(f))] for t,f in enumerate(F)]
            for b in (0,1,2):
                truth=brute(F,b,3);pool,_=compiled_pool(F,b,3)
                for mode in ('none','score','text','rank'):
                    result,proof=exact_from_pool(F,pool,forms,b,3,mode,collect=True)
                    self.assertEqual(set(result['pool']),truth)
                    self.assertEqual(len(proof['descriptors']),result['states'])
                    for j,w in result['witnesses'].items():
                        self.assertEqual(len({t for t,a in w}),len(w));self.assertLessEqual(len(w),b)
                        a=[0]*len(F)
                        for t,v in w:a[t]=v
                        z=sum(f[v] for f,v in zip(F,a));self.assertGreaterEqual(z[int(j)],sorted(z.tolist())[-3])

    def test_zero_effects_min_cost_ties_and_caps(self):
        F=[np.zeros((4,12),dtype=np.int64)]*4;forms=[[{'text':str(a)} for a in range(4)]]*4
        result,proof=exact_from_pool(F,np.arange(12),forms,2,5,collect=True)
        self.assertEqual(result['states'],1);self.assertEqual(len(result['pool']),12)
        other=[np.array([[5,0,0],[0,8,0],[0,0,8]],dtype=np.int64)]
        result,_=exact_from_pool(other,np.arange(3),[[{'text':str(a)} for a in range(3)]],2,1,mode='none',max_states=1)
        self.assertEqual(result['status'],'resource_unknown')
        # A single token cannot supply two simultaneous edit effects.
        F=[np.array([[5,0,0],[0,8,0],[0,0,8]],dtype=np.int64)]
        result,_=exact_from_pool(F,np.arange(3),[[{'text':str(a)} for a in range(3)]],2,1)
        self.assertEqual(set(result['pool']),{0,1,2});self.assertEqual(result['states'],3)

if __name__=='__main__':unittest.main()
