#!/usr/bin/env python3
"""Literal-mask and independent-equation regressions for the ORRR bound."""
from fractions import Fraction as F
from pathlib import Path
import unittest

from centered import Centered, change, digest, load


ROOT = next(p for p in Path(__file__).resolve().parents if (p/'large.py').exists())
PRIOR = ROOT/'research/reports/large-T-20261109/followup'


def literal(c, s, i, active, recipient):
    n, row = c.n, {}
    parent = (1 << s[i])-1
    for mask in range(1 << n):
        p = F((n-1)**(n-mask.bit_count()), n**n)
        child = parent ^ mask
        masks = range(1 << n) if active else (0,)
        for noise in masks:
            a = F((n-1)**(n-noise.bit_count()), n**n) if active else F(1)
            observed = (child ^ noise).bit_count()
            end = list(s)
            for k in c.neighbors[i]:
                if recipient == 'R' and k == n or recipient == 'O' and k != n:
                    continue
                # Literal pinned max-Chebyshev comparison, not k == observed.
                proposed = max(k*(n-observed), (n-k)*observed)
                incumbent = k*(n-k)
                if proposed <= incumbent:
                    end[k] = child.bit_count()
            key = tuple(end)
            row[key] = row.get(key, F(0))+p*a
    return row


class Checks(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.c = Centered(4)
        cls.oracle = load(PRIOR/'round-0014/audit.py', 'phase_oracle').Phase(4)

    @classmethod
    def tearDownClass(cls):
        cls.c.clear()
        cls.oracle.clear()

    def test_mutation_rows_and_literal_clean(self):
        c = self.c
        for row in c.d:
            self.assertEqual(sum(row), 1)
        for s in (c.target, c.corner, (4, 0, 1, 0, 0)):
            for i in range(c.m):
                self.assertEqual(dict(c.clean(s, i)), literal(c, s, i, False, 'all'))

    def test_literal_signed_restricted_kernels(self):
        c = self.c
        for s in (c.corner, (4, 0, 1, 0, 0)):
            for i in range(c.m):
                for letter in ('R', 'O'):
                    active = literal(c, s, i, True, letter)
                    clean = literal(c, s, i, False, letter)
                    expected = {v: active.get(v, 0)-clean.get(v, 0)
                                for v in set(active) | set(clean)}
                    expected = {v: p for v, p in expected.items() if p}
                    self.assertEqual(dict(c.signed(s, i, letter)), expected)

    def test_R_preserves_orphan_and_annihilates_baseline(self):
        c = self.c
        s = (4, 0, 1, 0, 0)
        for i in range(c.m):
            row = c.signed(s, i)
            self.assertEqual(sum(p for _, p in row), 0)
            self.assertTrue(all(v[-1] == s[-1] for v, _ in row))
            self.assertEqual(sum(p*F(v[-1]**2+7) for v, p in row), 0)

    def test_actual_orphan_birth_and_negative_stay(self):
        c = self.c
        row = dict(c.signed(c.corner, c.n, 'O'))
        for y in range(c.n):
            self.assertEqual(row[change(c.corner, c.n, y)], c.d[c.n][y]*c.d[y][c.n])
        self.assertEqual(row[c.corner], -sum(c.d[c.n][y]*c.d[y][c.n] for y in range(c.n)))

    def test_no_orphan_insertion_before_final_phase(self):
        c = self.c
        for i in range(c.n):
            self.assertEqual(c.signed(c.corner, i, 'O'), ())

    def test_centered_values_match_independent_equations(self):
        c, p = self.c, self.oracle
        for s in (c.corner, (2, 1, 0, 3, 0), (2, 1, 0, 0, 1)):
            for j in (0, 1, 2):
                v = p.values(s, 'R'*j)
                b = p.values(c.baseline(s[-1]), 'R'*j)
                self.assertEqual(c.excess(s, j), tuple(x-y for x, y in zip(v, b)))

    def test_centering_zero_for_every_baseline_phase(self):
        c = self.c
        for y in range(c.n+1):
            for j in (0, 1, 2):
                self.assertEqual(c.excess(c.baseline(y), j), (F(0),)*c.m)

    def test_nonzero_boundary_compensation_is_required(self):
        c = self.c
        for j in (1, 2):
            s = c.corner
            lhs = c.excess(s, j)[0]
            uncompensated = (c.forcing(s, 0, j)-c.forcing(c.target, 0, j)
                             +sum(p*c.excess(v, j)[1] for v, p in c.clean(s, 0)))
            self.assertNotEqual(c.flux(j), 0)
            self.assertEqual(lhs-uncompensated, c.flux(j))

    def test_phase_zero_killing_and_live_interior(self):
        c, p = self.c, self.oracle
        self.assertEqual(c.response(c.target, 1)[0], 0)
        self.assertEqual(c.response(c.target, 1), p.values(c.target, 'R'))
        self.assertNotEqual(c.response(c.target, 1)[1], 0)

    def test_last_pair_and_orphan_dependence(self):
        c = self.c
        s = (0, 1, 2, 0, 0)
        row = c.clean(s, 4)
        regular = sum(p for v, p in row if v[:-1] == c.target[:-1])
        orphan = sum(p for v, p in row if v[-1] == 4)
        both = sum(p for v, p in row if v == c.target)
        self.assertEqual((regular, orphan, both), (F(3, 64), F(1, 256), 0))

    def test_ORRR_matches_published_exact_hash(self):
        expected = 'e1f370a5361766437f233a3616fc63aead43324f2e4d6bc53b4a385b67d084c2'
        self.assertEqual(digest(self.c.orrr()), expected)

    def test_refuses_out_of_scope_parity(self):
        for n in (2, 3, 5):
            with self.assertRaises(ValueError):
                Centered(n)


if __name__ == '__main__':
    unittest.main(verbosity=2)
