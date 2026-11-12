"""Regression and independent literal-kernel checks; no random draws."""
from fractions import Fraction as F
import itertools
import unittest

import excursions as e


class ExcursionsTests(unittest.TestCase):
    def test_weight_kernel_from_literal_masks(self):
        for n in range(2,7):
            for x in range(n+1):
                self.assertEqual(e.mutation(n,x),e.mask_mutation(n,x))

    def test_directed_geometry_and_degrees(self):
        for n in range(2,13):
            for t in range(1,n+2):
                for i in range(n+1):
                    self.assertEqual(e.neighbors(n,t,i),e.literal_neighbors(n,t,i))
                self.assertEqual(e.degrees(n,t),tuple(len(e.incoming(n,t,k)) for k in range(n+1)))
        self.assertIn(2,e.neighbors(6,3,0))
        self.assertNotIn(0,e.neighbors(6,3,2))

    def test_literal_shared_observation_update(self):
        n=2
        target=tuple(range(n+1))
        for t in range(1,n+2):
            for w in itertools.product(range(n+1),repeat=n+1):
                for i,y,z in itertools.product(range(n+1),repeat=3):
                    literal,b,lo,hi=e.advance(n,t,w,target,0,n,i,y,z)
                    expected=list(w)
                    if z in e.neighbors(n,t,i):
                        expected[z]=y
                    self.assertEqual(literal,tuple(expected))
                    self.assertEqual((b,lo,hi),(target,0,n))

    def test_phase_correction_is_required(self):
        # At T=1, phase 1 cannot change slot 0. Its uncorrected reciprocal
        # potential has zero drift, and cannot pay one unit per attempt.
        n,t,p,k,a=3,1,F(1,192),0,1
        self.assertNotIn(k,e.neighbors(n,t,a))
        g=e.phase_correction(n,t,p,k,a)
        nxt=e.phase_correction(n,t,p,k,a+1)
        self.assertGreater(g,0)
        self.assertEqual(nxt-g,-e.delta(n,t,p,k)/(n+1))

    def test_acceptance_conditioning_is_biased(self):
        n,p,x,k=3,F(1,192),2,0
        wrong=p*sum(e.mutation(n,x)[y]*e.mutation(n,y)[k] for y in range(n+1) if y!=k)
        total=wrong+e.mutation(n,x)[k]*(1-p+p*e.mutation(n,k)[k])
        self.assertEqual(wrong/total,F(32,5197))
        self.assertGreater(wrong/total,p)

    def test_interior_alignment_can_be_reinfected(self):
        n,t=6,5
        corner=(2,1,2,3,4,5,6)
        target=tuple(range(n+1))
        aligned,_,_,_=e.advance(n,t,corner,target,0,n,1,0,0)
        end,_,_,_=e.advance(n,t,aligned,target,0,n,2,2,0)
        self.assertEqual(aligned,target)
        self.assertEqual(end,corner)

    def test_final_pin_can_coincide_with_ideal_discovery(self):
        n,t=3,3
        w=(3,0,0,0)
        labels=(1,1,2,3)
        new,b,lo,hi=e.advance(n,t,w,labels,1,3,0,2,0)
        self.assertEqual((b,lo,hi),(tuple(range(n+1)),0,3))
        self.assertEqual(new,(2,0,0,0))
        self.assertTrue(e.unseeded(new))

    def test_actual_noisy_excursion_supersolutions(self):
        n,t,p=2,3,F(1,8)
        states,_,rows=e.unseeded_kernel(n,t,p)
        exact=e.exact_solve(rows)
        for k in range(n+1):
            phi=[e.potential(n,t,p,k,w,a) for w,a in states]
            for i,row in enumerate(rows):
                self.assertGreaterEqual(phi[i]-sum(q*phi[j] for j,q in row.items()),1)
                self.assertLessEqual(exact[i],phi[i])

    def test_drift_condition_and_state_caps(self):
        with self.assertRaises(ValueError):
            e.phase_correction(3,4,F(1,4),0,0)
        with self.assertRaises(ValueError):
            e.unseeded_kernel(4,3,F(1,256))
        self.assertIsNone(e.uniform_charge(3,4,F(1,4)))

    def test_full_communication_seeds_even_when_degree_condition_fails(self):
        n,t,p=3,4,F(3,4)
        self.assertLess(e.delta(n,t,p,0),0)
        _,_,rows=e.unseeded_kernel(n,t,p)
        self.assertTrue(all(sum(row.values())<=p for row in rows))

    def test_noisy_trap_first_change_lower_bound(self):
        for n,t in ((3,3),(6,3),(8,3),(8,4)):
            for p in (F(0),F(1,n)):
                w=e.polarized(n,t)
                mean,_=e.first_change(n,t,p,w)
                a=(n+2-t)//2
                import math
                lower=F(math.factorial(a),1)/(1-p+p*2**a)
                self.assertGreaterEqual(mean,lower)
                # A first change may be followed by more changes. This
                # formula explicitly stops immediately on the first one.
                rates=[1-e.step(n,t,p,w,i).get(w,F(0)) for i in range(n+1)]
                survival,numerator=F(1),F(0)
                for rate in rates:
                    numerator+=survival
                    survival*=1-rate
                self.assertEqual(mean,numerator/(1-survival))


if __name__=='__main__':
    unittest.main()
