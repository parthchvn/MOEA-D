#!/usr/bin/env python3
"""Model-semantic and cancellation regressions for the independent audit."""
from fractions import Fraction as F
from itertools import product
import unittest
from audit import Sweep, change, mutation, neighborhood, dependence_witness


def literal_row(n, state, breeder, active, allowed):
    row = {}
    # Canonical representative genotype: exactly state[breeder] low bits set.
    parent = (1 << state[breeder])-1
    masks = [(mask, F((n-1)**(n-mask.bit_count()), n**n)) for mask in range(1 << n)]
    for mask, p in masks:
        child = parent ^ mask
        for noise, a in masks if active else [(0, F(1))]:
            observed = (child ^ noise).bit_count()
            end = list(state)
            for k in allowed:
                old = max(k*(n-k), (n-k)*k)
                new = max(k*(n-observed), (n-k)*observed)
                if new <= old:
                    end[k] = child.bit_count()
            end = tuple(end)
            row[end] = row.get(end, F(0))+p*a
    return {s: p for s, p in row.items() if p}


class ModelTests(unittest.TestCase):
    def tearDown(self):
        Sweep(4).clear()

    def test_mutation_literal_masks(self):
        for n in range(3, 7):
            d = mutation(n)
            for x in range(n+1):
                parent = (1 << x)-1
                row = [F(0)]*(n+1)
                for mask in range(1 << n):
                    row[(parent ^ mask).bit_count()] += F((n-1)**(n-mask.bit_count()), n**n)
                self.assertEqual(tuple(row), d[x])

    def test_filled_neighborhoods(self):
        self.assertEqual([neighborhood(4, i) for i in range(5)], [(0,1),(1,0),(2,3),(3,2),(4,3)])
        self.assertNotIn(4, neighborhood(4,3))

    def test_literal_recipient_split(self):
        s = Sweep(4)
        states = [s.corner, s.target, (0,1,0,0,0), (4,4,1,2,0)]
        for state, i in product(states, range(5)):
            self.assertEqual(dict(s.step(state, i)), literal_row(4, state, i, False, s.neighbors[i]))
            total = {}
            for letter in ('R','O'):
                allowed = [k for k in s.neighbors[i] if (k == 4) == (letter == 'O')]
                active = literal_row(4, state, i, True, allowed)
                clean = literal_row(4, state, i, False, allowed)
                expected = {v: active.get(v, F(0))-clean.get(v, F(0)) for v in active.keys() | clean.keys()}
                expected = {v:p for v,p in expected.items() if p}
                self.assertEqual(dict(s.step(state,i,letter)), expected)
                self.assertEqual(sum(expected.values()), 0)
                for v,p in expected.items():
                    total[v] = total.get(v,F(0))+p
            active = literal_row(4,state,i,True,s.neighbors[i])
            clean = literal_row(4,state,i,False,s.neighbors[i])
            self.assertEqual({v:p for v,p in total.items() if p},
                             {v:active.get(v,F(0))-clean.get(v,F(0)) for v in active.keys() | clean.keys()
                              if active.get(v,F(0)) != clean.get(v,F(0))})

    def test_clean_corner_geometric(self):
        for n in (4,6):
            s = Sweep(n)
            q = 1-(1-s.d[2][0])*(1-s.d[1][0])
            self.assertEqual(s.value(s.corner), 1/q)
            self.assertEqual(s.value(s.corner,'','second'), (2-q)/q**2)

    def test_boundary_killing_only(self):
        s = Sweep(4)
        self.assertEqual(s.value(s.target), 0)
        self.assertEqual(s.phase(s.target,'',1), F(4,5))
        self.assertNotEqual(s.phase(s.target,'O',1), 0)

    def test_unshifted_subtraction_counterexample(self):
        s = Sweep(4)
        state = change(s.target,4,0)
        self.assertEqual(s.phase(state,'',1)-s.value(state), -F(1,5))
        self.assertEqual(s.excess(state,0,1), 0)

    def test_at_most_one_orphan_insertion_per_sweep(self):
        s = Sweep(4)
        self.assertEqual(s.product(s.corner,'OO'), ())
        self.assertEqual(s.product(s.corner,'OR'), ())
        self.assertTrue(s.product(s.corner,'RO'))
        self.assertNotEqual(s.value(s.corner,'OO'), 0)

    def test_negative_unchanged_birth_branch(self):
        s = Sweep(4)
        state = (0,1,0,0,4)
        row = dict(s.step(state,4,'O'))
        self.assertLess(row[state], 0)
        for y in range(4):
            self.assertEqual(row[change(state,4,y)], s.d[4][y]*s.d[y][4])
        self.assertEqual(sum(row.values()), 0)

    def test_stopped_reward_identity_wrong_orphan(self):
        s = Sweep(4)
        state = (2,1,0,0,0)
        b = 1-s.d[4][4]
        for j in range(3):
            rhs = sum(b**(j-r)*s.value(state,'O'*r,'reward') for r in range(j+1))
            self.assertEqual(s.excess(state,j), rhs)

    def test_phase_suffix_correction(self):
        s = Sweep(4)
        state = (2,1,0,0,4)
        for i in range(1,5):
            constant = sum(p*s.excess(v,2) for v,p in s.product(state,'',i))
            linear = sum(p*s.excess(v,1) for v,p in s.product(state,'O',i))
            self.assertEqual(s.excess(state,2,i), constant+linear)
        self.assertNotEqual(linear,0)

    def test_nonindependence_witness(self):
        w = dependence_witness()
        self.assertEqual(w['joint'],'0')
        self.assertEqual(w['product_of_marginals'],'3/16384')

    def test_scope_rejects_odd_n(self):
        for n in (2,3,5):
            with self.assertRaises(ValueError):
                Sweep(n)


if __name__ == '__main__':
    unittest.main(verbosity=2)
