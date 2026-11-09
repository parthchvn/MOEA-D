#!/usr/bin/env python3
"""Deterministic regression and reduction checks; no scientific RNG draws."""
from fractions import Fraction as F
import unittest
from coefficient import Solver,kernel,recipients
from verify import literal_kernel,replace,full_derivative


class CoefficientTests(unittest.TestCase):
    def tearDown(self):Solver.clear()

    def test_mutation_against_literal_masks(self):
        for n in range(2,8):
            d,den=literal_kernel(n)
            self.assertEqual(kernel(n),[[F(v,den) for v in row] for row in d])

    def test_kernel_probabilities_and_complement(self):
        for n in range(3,10):
            d=kernel(n)
            for x,row in enumerate(d):
                self.assertEqual(sum(row),1)
                self.assertEqual(row,list(reversed(d[n-x])))

    def test_pinned_scalarization_all_proposals(self):
        for n in range(3,7):
            w=(2,)+tuple(range(1,n+1))
            for t in (2,3):
                for i in range(n+1):
                    for y in range(n+1):
                        for z in range(n+1):
                            new=list(w)
                            if z in recipients(n,t,i):new[z]=y
                            self.assertEqual(tuple(new),replace(w,n,t,i,y,z))

    def test_endpoint_donors_and_orphan(self):
        for n in range(3,40):
            for t in (2,3):
                inc=[i for i in range(n+1) if 0 in recipients(n,t,i)]
                self.assertEqual(inc,[0,1])
            inc=[i for i in range(n+1) if n in recipients(n,2,i)]
            self.assertEqual(inc,[n] if n%2==0 else [n-1,n])

    def test_noiseless_corner(self):
        for n in range(3,10):
            for t in (2,3):
                s=Solver(n,t)
                self.assertEqual(s.h(((0,2),)),1/s.q)
                self.assertEqual(s.h(()),0)

    def test_noiseless_error_sets_only_shrink(self):
        s=Solver(5,3)
        for y in range(6):
            for k in range(1,6):
                if y==k:continue
                state=((0,2),(k,y))
                for start in range(7):
                    dist=s.sweep(state,start)
                    self.assertEqual(sum(dist.values()),1)
                    self.assertTrue(all(set(v)<=set(state) for v in dist))

    def test_disjoint_formula_exact(self):
        for n in range(3,9):
            for t in (2,3):
                s=Solver(n,t);slow=s.derivative()
                for k in range(2,n+1):
                    if not set(s.inc[k])&{0,1}:
                        self.assertEqual(slow[k],s.disjoint(k))
                self.assertEqual(slow,s.fast())
                s.clear()

    def test_full_population_derivative(self):
        for t in (2,3):
            s=Solver(3,t);full=full_derivative(3,t)
            self.assertEqual(F(full['baseline']),F(729,154))
            self.assertEqual(F(full['derivative']),sum(s.derivative()))

    def test_mid_sweep_alignment_cannot_be_killed(self):
        for t in (2,3):
            full=full_derivative(3,t)
            self.assertGreater(F(full['aligned_prefix_contribution']),0)

    def test_common_direct_endpoint_coefficient(self):
        for n in range(3,10):
            a=Solver(n,2).derivative(targets={0})[0]
            b=Solver(n,3).derivative(targets={0})[0]
            self.assertEqual(a,b)

    def test_small_n_sign_reversal_exact(self):
        for n in range(3,11):
            a=sum(Solver(n,2).fast());b=sum(Solver(n,3).fast())
            self.assertEqual(b>a,n==3)
            Solver.clear()

    def test_float_against_exact(self):
        for n in (3,4,7,10):
            for t in (2,3):
                a=Solver(n,t,exact=True).fast();b=Solver(n,t,exact=False).fast()
                for x,y in zip(a,b):self.assertAlmostEqual(float(x),y,places=9)
                Solver.clear()


if __name__=='__main__':unittest.main(verbosity=2)
