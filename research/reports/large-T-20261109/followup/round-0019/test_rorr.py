#!/usr/bin/env python3
"""Literal-mask, phase, and signed-entrance regressions; no RNG."""
from collections import defaultdict
from fractions import Fraction as F
from itertools import product
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parent))
from rorr import Sweep, put, ZERO


def masks(n):
    return tuple((x, F((n-1)**(n-x.bit_count()), n**n)) for x in range(1 << n))


def literal(solver, state, i, active, allowed):
    """Use actual bit masks, scalarization and true/stored weights."""
    n = solver.n
    parent = (1 << state[i])-1
    result = defaultdict(F)
    for mutation, p in masks(n):
        child_bits = parent ^ mutation
        child = child_bits.bit_count()
        for noise, a in (masks(n) if active else ((0, F(1)),)):
            observed = (child_bits ^ noise).bit_count()
            successor = state
            for k in allowed:
                cost = max(k*(n-observed), (n-k)*observed)
                incumbent = k*(n-k)
                if cost <= incumbent:
                    successor = put(successor, k, child)
            result[successor] += p*a
    return {v: a for v, a in result.items() if a}


class Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.s = Sweep(4)

    @classmethod
    def tearDownClass(cls):
        cls.s.clear()

    def test_domain(self):
        for n in (2, 3, 5):
            with self.assertRaises(ValueError):
                Sweep(n)

    def test_mutation_literal(self):
        s = self.s
        for x in range(5):
            row = [ZERO]*5
            for mask, p in masks(4):
                row[(((1 << x)-1) ^ mask).bit_count()] += p
            self.assertEqual(tuple(row), s.d[x])
            self.assertEqual(sum(row), 1)

    def test_neighborhood_edge(self):
        self.assertEqual(tuple(self.s.recipients(i) for i in range(5)),
                         ((0, 1), (1, 0), (2, 3), (3, 2), (4, 3)))

    def test_clean_literal(self):
        s = self.s
        for state in (s.target, s.corner, (3, 0, 4, 0, 1)):
            for i in range(5):
                self.assertEqual(dict(s.row(state, i)),
                                 literal(s, state, i, False, s.recipients(i)))

    def test_signed_restricted_literal(self):
        s = self.s
        for state in (s.target, s.corner, (3, 0, 4, 0, 1)):
            for i in range(5):
                for letter in ('R', 'O'):
                    allowed = [k for k in s.recipients(i) if (letter == 'O') == (k == 4)]
                    active = literal(s, state, i, True, allowed)
                    clean = literal(s, state, i, False, allowed)
                    diff = {v: active.get(v, ZERO)-clean.get(v, ZERO)
                            for v in active.keys() | clean.keys()}
                    self.assertEqual(dict(s.row(state, i, letter)),
                                     {v: a for v, a in diff.items() if a})

    def test_shared_kernel_split(self):
        s = self.s
        state = (3, 0, 4, 0, 1)
        for i in range(5):
            active = literal(s, state, i, True, s.recipients(i))
            clean = literal(s, state, i, False, s.recipients(i))
            combined = defaultdict(F)
            for letter in ('R', 'O'):
                for v, a in s.row(state, i, letter):
                    combined[v] += a
            for v in active.keys() | clean.keys() | combined.keys():
                self.assertEqual(combined[v], active.get(v, ZERO)-clean.get(v, ZERO))

    def test_signed_mass_and_orphan_autonomy(self):
        s = self.s
        for state in (s.target, s.corner, (3, 0, 4, 0, 1)):
            for i in range(5):
                for letter in ('R', 'O'):
                    row = s.row(state, i, letter)
                    self.assertEqual(sum(a for _, a in row), 0)
                    self.assertLessEqual(sum(abs(a) for _, a in row), 2)
                    if letter == 'R':
                        self.assertTrue(all(v[-1] == state[-1] for v, _ in row))
                    elif i < 4:
                        self.assertEqual(row, ())

    def test_clean_deletes_errors(self):
        s = self.s
        state = (3, 0, 4, 0, 1)
        for i in range(5):
            for v, a in s.row(state, i):
                self.assertGreater(a, 0)
                self.assertTrue(all(x in (state[k], k) for k, x in enumerate(v)))

    def test_killing_only_at_boundary(self):
        s = self.s
        self.assertEqual(s.boundary(s.target), 0)
        self.assertEqual(s.boundary(s.target, 'RORR'), 0)
        for i in range(1, 5):
            self.assertEqual(s.phase(s.target, i), F(5-i, 5))

    def test_corner_mean_and_visit_phase(self):
        s = self.s
        self.assertEqual(s.boundary(s.corner), 1/s.q)
        for state in (s.target, s.corner, put(s.target, 3, 0)):
            visit = s.auxiliary(state, 'visit')
            for i in range(5):
                self.assertEqual(visit[i], s.phase(state, i)+F(i, 5))

    def test_orphan_entrance_has_negative_stay(self):
        s = self.s
        row = dict(s.row(s.corner, 4, 'O'))
        total = ZERO
        for y in range(4):
            c = s.d[4][y]*s.d[y][4]
            self.assertEqual(row[put(s.corner, 4, y)], c)
            total += c
        self.assertEqual(row[s.corner], -total)
        self.assertGreater(total, 0)

    def test_scalar_entrance_inequalities(self):
        L = 80
        for a, b in product((F(1), F(1, 2), F(1, 256), F(1, 1000000)), repeat=2):
            self.assertLessEqual(b*(L+2/(a+b))**2, 2*L*L+2/a)
            self.assertLessEqual(a*(L*L+1/a), L*L+1)

    def test_baseline_orphan_response_decomposition(self):
        s = self.s
        beta = s.beta()
        self.assertNotEqual(beta, 0)
        for state in (s.target, s.corner, put(s.corner, 3, 0)):
            direct = sum((a*s.boundary(v, 'RR') for v, a in s.row(state, 4, 'O')), ZERO)
            self.assertEqual(direct, beta+s.gamma(state))
        self.assertEqual(s.gamma(s.target), 0)
        self.assertEqual(s.phase(s.target, 4, 'ORR'), beta)

    def test_baseline_cannot_be_deleted_before_orphan(self):
        s = self.s
        # At a live aligned final turn, O D2=0 but O H2=beta != 0.
        centered = sum((a*s.centered(v, 0) for v, a in s.row(s.target, 4, 'O')), ZERO)
        self.assertEqual(centered, 0)
        raw = sum((a*s.boundary(v, 'RR') for v, a in s.row(s.target, 4, 'O')), ZERO)
        self.assertEqual(raw, s.beta())
        self.assertNotEqual(raw, 0)

    def test_last_pair_orphan_dependence(self):
        s = self.s
        state = (0, 1, 2, 0, 0)
        row = s.row(state, 4)
        regular = sum(a for v, a in row if v[3] == 3)
        orphan = sum(a for v, a in row if v[4] == 4)
        joint = sum(a for v, a in row if v[3] == 3 and v[4] == 4)
        self.assertEqual((regular, orphan, joint), (F(3, 64), F(1, 256), 0))
        self.assertNotEqual(joint, regular*orphan)


if __name__ == '__main__':
    unittest.main(verbosity=2)
