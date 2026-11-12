#!/usr/bin/env python3
"""Deterministic falsification tests for the independent RORR audit."""
from collections import defaultdict
from fractions import Fraction as F
from itertools import combinations, product
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parent))
from audit import Audit, overwrite, ZERO


def bitmasks(n):
    return [(mask, F((n-1)**(n-mask.bit_count()), n**n)) for mask in range(1 << n)]


def literal(solver, state, phase, active, part):
    row = defaultdict(F)
    n = solver.n
    parent = (1 << state[phase])-1
    recipients = solver.neighbors(phase)
    for mutation, pm in bitmasks(n):
        child_bits = parent ^ mutation
        for noise, pn in (bitmasks(n) if active else [(0, F(1))]):
            observed = (child_bits ^ noise).bit_count()
            result = state
            for k in recipients:
                if part != 'all' and (part == 'O') != (k == n):
                    continue
                cost = max(k*(n-observed), (n-k)*observed)
                if cost <= k*(n-k):
                    result = overwrite(result, k, child_bits.bit_count())
            row[result] += pm*pn
    return dict(row)


class Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.s = Audit(4)

    @classmethod
    def tearDownClass(cls):
        cls.s.clear()

    def test_domain(self):
        for n in (1, 2, 3, 5):
            with self.assertRaises(ValueError):
                Audit(n)

    def test_weight_rows_against_masks(self):
        for x in range(5):
            expected = [ZERO]*5
            for mask, p in bitmasks(4):
                expected[(((1 << x)-1) ^ mask).bit_count()] += p
            self.assertEqual(tuple(expected), self.s.d[x])

    def test_parity_and_orphan(self):
        self.assertEqual([self.s.neighbors(i) for i in range(5)],
                         [(0, 1), (1, 0), (2, 3), (3, 2), (4, 3)])
        self.assertEqual([i for i in range(5) if 4 in self.s.neighbors(i)], [4])

    def test_stochastic_kernels_against_genotypes(self):
        for state in (self.s.corner, self.s.aligned, (3, 0, 4, 0, 1)):
            for i, active, part in product(range(5), (False, True), ('R', 'O', 'all')):
                actual = dict(self.s.kernel(state, i, active, part))
                self.assertEqual(actual, literal(self.s, state, i, active, part))
                self.assertEqual(sum(actual.values()), 1)
                self.assertTrue(all(p >= 0 for p in actual.values()))

    def test_shared_observation_split(self):
        for state in (self.s.corner, self.s.aligned, (3, 0, 4, 0, 1)):
            for i in range(5):
                row = defaultdict(F)
                for letter in ('R', 'O'):
                    for v, p in self.s.signed(state, i, letter):
                        row[v] += p
                for active, sign in ((True, -1), (False, 1)):
                    for v, p in self.s.kernel(state, i, active):
                        row[v] += sign*p
                self.assertTrue(all(v == 0 for v in row.values()))

    def test_signed_total_variation(self):
        for state in (self.s.corner, self.s.aligned, (3, 0, 4, 0, 1)):
            for i, letter in product(range(5), ('R', 'O')):
                row = self.s.signed(state, i, letter)
                self.assertEqual(sum(p for _, p in row), 0)
                self.assertLessEqual(sum(abs(p) for _, p in row), 2)

    def test_only_boundary_killed(self):
        for word in ('', 'R', 'RR', 'ORR'):
            self.assertEqual(self.s.values(self.s.aligned, word)[0], 0)
        self.assertEqual(self.s.values(self.s.aligned), (0, F(4, 5), F(3, 5), F(2, 5), F(1, 5)))
        self.assertEqual(self.s.values(self.s.aligned, 'ORR')[4], self.s.beta())
        self.assertNotEqual(self.s.beta(), 0)

    def test_rotation_satisfies_first_step_equations(self):
        s = self.s
        for state in (s.corner, s.aligned, (2, 0, 2, 3, 0)):
            for word in ('', 'R', 'RR'):
                values = s.values(state, word)
                for i in range(5):
                    if state == s.aligned and i == 0:
                        continue
                    rhs = F(1, 5) if not word else s.apply(state, i, word[0], word[1:])
                    rhs += sum((p*s.values(v, word)[(i+1) % 5] for v, p in s.kernel(state, i)), ZERO)
                    self.assertEqual(values[i], rhs)

    def test_compensated_killed_row(self):
        s = self.s
        for word in ('R', 'RR'):
            flux = sum((s.apply(s.aligned, i, 'R', word[1:]) for i in range(5)), ZERO)
            residual = s.apply(s.aligned, 0, 'R', word[1:])+s.values(s.aligned, word)[1]
            self.assertEqual(residual, flux)
            self.assertNotEqual(residual, 0)

    def test_phase_only_term_annihilated(self):
        for state in (self.s.corner, self.s.aligned):
            for i in range(5):
                self.assertEqual(sum(p*F((i+1) % 5, 5) for _, p in self.s.signed(state, i, 'R')), 0)

    def test_orphan_turn_count_has_final_turn(self):
        s = self.s
        for state in (s.corner, s.aligned, overwrite(s.corner, 1, 0)):
            self.assertEqual(s.values(state, '@visits'), tuple(v+F(i, 5) for i, v in enumerate(s.values(state))))
        self.assertEqual(s.values(s.aligned, '@visits')[4], 1)
        self.assertEqual(s.values(s.aligned, '@visits')[0], 0)

    def test_orphan_entrance_and_negative_branch(self):
        s = self.s
        row = dict(s.signed(s.corner, 4, 'O'))
        total = ZERO
        for y in range(4):
            c = s.d[4][y]*s.d[y][4]
            self.assertEqual(row[overwrite(s.corner, 4, y)], c)
            total += c
        self.assertEqual(row[s.corner], -total)

    def test_baseline_decomposition(self):
        s = self.s
        for state in (s.aligned, s.corner, overwrite(s.corner, 3, 0)):
            self.assertEqual(s.apply(state, 4, 'O', 'RR'), s.beta()+s.gamma(state))
            self.assertEqual(s.values(state, 'ORR'), tuple(s.beta()*a+b for a, b in zip(s.values(state, '@visits'), s.values(state, '@gamma'))))

    def test_centering_inside_O_is_false(self):
        s = self.s
        centered = sum((p*s.centered(v)[0] for v, p in s.signed(s.aligned, 4, 'O')), ZERO)
        self.assertEqual(centered, 0)
        self.assertNotEqual(s.apply(s.aligned, 4, 'O', 'RR'), centered)

    def test_marked_clean_family_is_good(self):
        for n in (4, 6, 8, 10):
            target = tuple(range(n+1))
            for origin in (target, overwrite(target, 0, 2)):
                for k, x in product(range(n), range(n+1)):
                    state = overwrite(origin, k, x)
                    errors = [j for j in range(n) if state[j] != j]
                    self.assertLessEqual(len(errors), 2)
                    for size in range(len(errors)+1):
                        for repairs in combinations(errors, size):
                            child = tuple(j if j in repairs else a for j, a in enumerate(state))
                            for left in range(0, n, 2):
                                if child[left] != left and child[left+1] != left+1:
                                    self.assertEqual(left, 0)
                                    self.assertEqual(child[0], 2)

    def test_acceptance_weighted_square(self):
        for a, b in product((F(1), F(1, 2), F(1, 256), F(1, 10**20)), repeat=2):
            self.assertLessEqual(b*(80+2/(a+b))**2, 2*80**2+2/a)

    def test_last_pair_dependence_preserved(self):
        state = (0, 1, 2, 0, 0)
        row = self.s.kernel(state, 4)
        left = sum(p for v, p in row if v[3] == 3)
        right = sum(p for v, p in row if v[4] == 4)
        both = sum(p for v, p in row if v[3] == 3 and v[4] == 4)
        self.assertEqual((left, right, both), (F(3, 64), F(1, 256), 0))
        self.assertNotEqual(both, left*right)


if __name__ == '__main__':
    unittest.main(verbosity=2)
