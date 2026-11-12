import itertools
from fractions import Fraction as F
import unittest
from structure import (Clean, candidates, central_distance, components, holding,
                       literal_neighbors, mask_mutation, mutation, neighbors, polarized)
from response import Response


class StructureTests(unittest.TestCase):
    def test_caps(self):
        with self.assertRaises(ValueError):
            Clean(8,3,tuple([8]*8+[0]))
        with self.assertRaises(ValueError):
            Response(4,3)

    def test_candidate_dedup_and_natural_log(self):
        self.assertEqual(set(candidates(3)),{2,3,4})
        self.assertEqual(candidates(16)[4],['4','ceil_sqrt_n'])
        self.assertEqual(candidates(16)[3],['3','ceil_ln_n'])

    def test_even_boundary_orphan(self):
        adj=[neighbors(6,2,i) for i in range(7)]
        groups,sources,rev=components(adj)
        self.assertEqual(set(groups),{(0,1),(2,3),(4,5),(6,)})
        self.assertEqual(set(sources),{(0,1),(2,3),(6,)})
        self.assertEqual(rev[6],[6])
        self.assertIn(5,adj[6])
        self.assertNotIn(6,adj[5])

    def test_center_parity_penalty(self):
        self.assertEqual(central_distance(7,4),3)
        self.assertEqual(central_distance(5,4),1)
        self.assertEqual(central_distance(7,8),0)
        self.assertEqual([neighbors(7,4,i)[0] for i in range(8)],[0,0,1,1,3,3,4,4])

    def test_clean_rows_literal_bit_masks(self):
        count=0
        for n in (2,3):
            for t in range(2,n+2):
                for s in itertools.product(range(n+1),repeat=n+1):
                    solver=Clean(n,t,s)
                    for i in range(n+1):
                        raw={}
                        for y,p in enumerate(mask_mutation(n,s[i])):
                            z=list(s)
                            if y in literal_neighbors(n,t,i):
                                z[y]=y
                            z=tuple(z)
                            raw[z]=raw.get(z,F(0))+p
                        self.assertEqual(raw,solver.step(s,i))
                        count+=1
        self.assertEqual(count,3234)

    def test_shared_observation_only_one_replacement(self):
        solver=Response(3,4)
        for s in solver.states:
            for i in range(4):
                for z in solver.row(s,i,True):
                    self.assertLessEqual(sum(a!=b for a,b in zip(s,z)),1)

    def test_reinfection_later_breeder(self):
        n,t=6,5
        s=[2,1,2,3,4,5,6]
        events=[(2,2,False),(0,0,False),(2,0,True),
                (3,3,False),(4,4,False),(5,5,False),(6,6,False)]
        for i,(y,k,active) in enumerate(events):
            self.assertGreater(mutation(n,s[i])[y],0)
            if active:
                self.assertGreater(mutation(n,y)[k],0)
            else:
                self.assertEqual(y,k)
            if k in neighbors(n,t,i):
                s[k]=y
            if i==1:
                self.assertEqual(s,list(range(7)))
        self.assertEqual(s,[2,1,2,3,4,5,6])

    def test_trap_entrance_without_killed_boundary(self):
        for n in range(3,8):
            for t in candidates(n):
                target,_=polarized(n,t)
                s=[2]+list(range(1,n+1))
                for i,y in enumerate(target):
                    self.assertIn(i,neighbors(n,t,i))
                    self.assertGreater(mutation(n,s[i])[y]*mutation(n,y)[i],0)
                    s[i]=y
                    self.assertNotEqual(s,list(range(n+1)))
                self.assertEqual(tuple(s),target)

    def test_full_neighborhood_seeds_immediately(self):
        for n in range(3,8):
            s,_=polarized(n,n+1)
            self.assertEqual(holding(n,n+1,s),1)
            for z in Clean(n,n+1,s).step(s,0):
                self.assertTrue(any(x==k for k,x in enumerate(z)))

    def test_T2_slow_pair_escape(self):
        for n in (3,5,9,17):
            s=tuple(list(range(n-1))+[0,0])
            r=mutation(n,0)[n-1]+mutation(n,0)[n]
            row=Clean(n,2,s).sweep(s)
            self.assertEqual(row[s],(1-r)**2)
            self.assertGreaterEqual(Clean(n,2,s).mean(),1/(1-(1-r)**2))
            self.assertLessEqual(Clean(n,3,s).mean(),6*n)


if __name__=='__main__':
    unittest.main(verbosity=2)
