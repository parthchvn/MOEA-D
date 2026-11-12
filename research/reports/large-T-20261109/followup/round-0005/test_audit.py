#!/usr/bin/env python3
"""Regression tests for model fidelity, certificate failures and renewal indexing."""
import csv
from fractions import Fraction as F
from itertools import product
import json
from math import comb
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from audit import (constants, find_boundary_witness, literal_replace, mask_kernel,
                   posterior_witness, recipients, solve_exact, transitions)
from forest import advance
from verify import verify

HERE=Path(__file__).resolve().parent


class ModelTests(unittest.TestCase):
    def test_masks_against_independent_binomial_formula(self):
        for n in range(2,6):
            d,den=mask_kernel(n)
            for x,y in product(range(n+1),repeat=2):
                expected=sum(comb(x,a)*comb(n-x,b)*(n-1)**(n-a-b)
                             for a in range(x+1) for b in range(n-x+1) if x-a+b==y)
                self.assertEqual(d[x][y],expected)
            self.assertTrue(all(sum(row)==den for row in d))

    def test_scalarization_matches_single_target_replacement(self):
        count=0
        for n in (2,3):
            for t in range(1,n+2):
                for w in product(range(n+1),repeat=n+1):
                    for i,y,k in product(range(n+1),repeat=3):
                        expected=list(w)
                        if k in recipients(n,t,i): expected[k]=y
                        self.assertEqual(literal_replace(w,n,t,i,y,k),tuple(expected))
                        count+=1
        self.assertEqual(count,67723)

    def test_transition_row_mass_and_no_internal_absorption(self):
        n,t,p=3,2,F(1,192)
        states,index,steps,den=transitions(n,t,p)
        i=index[(0,1,2,3)]
        self.assertEqual(sum(m for j,m in steps[1][i]),den)
        self.assertGreater(dict(steps[1][i])[index[(0,0,2,3)]],0)

    def test_donor_sets_and_asymmetry(self):
        for t in (2,3):
            self.assertEqual([i for i in range(4) if 0 in recipients(3,t,i)],[0,1])
        self.assertIn(3,recipients(4,2,4))
        self.assertNotIn(4,recipients(4,2,3))

    def test_posterior_bias_is_strict(self):
        v=posterior_witness()
        self.assertEqual(F(v['wrong_given_accepted']),F(32,5197))
        self.assertGreater(F(v['wrong_given_accepted']),F(v['p']))

    def test_boundary_witness_requires_noise(self):
        v=find_boundary_witness()
        self.assertEqual((v['n'],v['T']),(3,2))
        self.assertTrue(any(y!=k for i,x,y,k,w in v['path']))
        self.assertGreater(F(v['probability']),0)
        self.assertNotEqual(v['final'],list(range(4)))

    def test_upper_bound_conditions_not_silently_extended(self):
        for t in (2,3,4):
            c=constants(3,t,F(1,3))
            self.assertNotIn('C_lower',c)
            self.assertNotIn('B0',c)


class ForestTests(unittest.TestCase):
    def test_ignored_base_creates_particle(self):
        w,parts=advance((2,1,2),((0,2,True),),2,3,0,[(2,1),(2,2)])
        self.assertEqual(w,(2,1,2))
        self.assertIn((1,2,False),parts)
        self.assertIn((0,2,True),parts)

    def test_own_base_birth_not_processed_immediately(self):
        w,parts=advance((0,1,2),(),2,3,1,[(0,1)])
        self.assertEqual((w,parts),((0,0,2),((1,0,True),)))

    def test_external_child_acts_in_same_sweep(self):
        w,parts=advance((2,1,2),((0,2,True),),2,3,0,[(0,0),(2,1)])
        self.assertEqual(w,(2,2,2))
        w,parts=advance(w,parts,2,3,1,[(1,1),(1,1)])
        self.assertEqual(w,(2,1,2))
        self.assertEqual(parts,((0,2,True),))

    def test_clean_repair_keeps_unused_particle(self):
        w,parts=advance((0,0,2),((1,0,True),),2,3,0,[(1,1)])
        self.assertEqual(w,(0,1,2))
        self.assertEqual(parts,((1,0,False),))

    def test_many_unselected_particles_preserve_tag(self):
        particles=((0,1,False),(0,2,True),(0,2,False),(1,0,False))
        w,parts=advance((2,1,2),particles,2,3,0,
                        [(1,0),(2,0),(2,1),(0,0)])
        self.assertEqual(w,(2,2,2))
        self.assertIn((0,2,True),parts)
        self.assertIn((1,2,True),parts)


class RenewalTests(unittest.TestCase):
    def test_random_initial_lifetime_and_multiple_sources(self):
        laws=([F(3,4),F(1,4)],[F(1,2),F(1,3),F(1,6)],
              [F(1,3),F(1,6),F(1,6),F(1,3)])
        initials=([F(1)],[F(1,4),F(1,4),F(1,2)],
                  [F(0),F(1,3),F(0),F(0),F(2,3)])
        cases=0
        for left,right in product(laws,repeat=2):
            # Combined source duration is their maximum, with independent draws.
            law=[F(0)]*max(len(left),len(right))
            for a,b in product(range(len(left)),range(len(right))):
                law[max(a,b)]+=left[a]*right[b]
            for initial in initials:
                m=max(len(initial),len(law))-1
                q=[F(1)]
                for s in range(1,m+1):
                    q.append(q[-1]*sum(law[:s]))
                matrix=[[F(i==j)-sum(prob for length,prob in enumerate(law)
                                    if max(i-1,length)==j)
                         for j in range(1,m+1)] for i in range(1,m+1)]
                hit=[F(0)]+solve_exact(matrix,[F(1)]*m)
                direct=sum(prob*hit[i] for i,prob in enumerate(initial))
                renewal=sum(sum(initial[s+1:])*q[s] for s in range(m))/q[-1]
                self.assertEqual(direct,renewal)
                self.assertLessEqual(direct,sum(i*p for i,p in enumerate(initial))/q[-1])
                cases+=1
        self.assertEqual(cases,27)

    def test_family_independence_is_necessary_for_product(self):
        # Two duration-one families with one shared gate: emptiness is 1/2,
        # whereas multiplying marginal emptiness gives 1/4.
        self.assertNotEqual(F(1,2),(1-F(1,2))**2)


class CertificateTests(unittest.TestCase):
    def test_full_exact_certificate_check(self):
        result=verify(HERE)
        self.assertEqual(result['counts']['state_cells'],4339)

    def test_certificate_tampering_is_detected(self):
        with tempfile.TemporaryDirectory() as directory:
            out=Path(directory)
            for name in ('verification.json','expectations.csv','certificates.csv'):
                shutil.copyfile(HERE/name,out/name)
            path=out/'certificates.csv'
            rows=list(csv.DictReader(path.open()))
            rows[0]['time_num']=str(int(rows[0]['time_num'])+1)
            with path.open('w',newline='') as f:
                writer=csv.DictWriter(f,fieldnames=list(rows[0]))
                writer.writeheader();writer.writerows(rows)
            with self.assertRaises(AssertionError): verify(out)

    def test_verifier_runs_without_site_packages(self):
        result=subprocess.run([sys.executable,'-S',str(HERE/'verify.py'),'--bundle',str(HERE)],
                              text=True,capture_output=True,check=True)
        self.assertEqual(json.loads(result.stdout)['status'],'pass')


if __name__=='__main__':
    unittest.main(verbosity=2)
