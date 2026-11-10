#!/usr/bin/env python3
"""Adversarial deterministic tests of the independent orphan auditor."""
from fractions import Fraction as F
from math import comb
import unittest
from audit import (Chain, change, local, mutation, orphan_finite, orphan_series,
                   qvalue, recipients, solve)


class AuditTests(unittest.TestCase):
    def tearDown(self):
        Chain(4).clear()

    def test_literal_kernel_balance_and_row_sums(self):
        for n in (3, 4, 6):
            d = mutation(n)
            for x in range(n + 1):
                self.assertEqual(sum(d[x]), 1)
                for y in range(n + 1):
                    self.assertEqual(comb(n, x) * d[x][y], comb(n, y) * d[y][x])

    def test_exact_even_orphan_and_odd_pair(self):
        for n in range(3, 21):
            incoming = [i for i in range(n + 1) if n in recipients(n, 2, i)]
            self.assertEqual(incoming, [n] if n % 2 == 0 else [n - 1, n])
            for i in range(n + 1):
                self.assertEqual(len(recipients(n, 2, i)), 2)

    def test_clean_only_repairs(self):
        c = Chain(4)
        w = (2, 0, 2, 1, 0)
        for i in range(5):
            self.assertEqual(sum(p for _, p in c.step(w, i)), 1)
            for v, _ in c.step(w, i):
                self.assertTrue(all(y == x or y == k for k, (x, y) in enumerate(zip(w, v))))

    def test_recipient_split_against_full_literal_kernel(self):
        c = Chain(4)
        for w in (c.target, c.corner, (2, 0, 2, 4, 0)):
            for i in range(5):
                expected = {}
                for y, py in enumerate(c.d[w[i]]):
                    for z, pz in enumerate(c.d[y]):
                        v = change(w, z, y) if z in c.neighbors[i] else w
                        expected[v] = expected.get(v, F(0)) + py * pz
                    v = change(w, y, y) if y in c.neighbors[i] else w
                    expected[v] = expected.get(v, F(0)) - py
                actual = {}
                for kind in ('R', 'O'):
                    rows = c.step(w, i, kind)
                    self.assertEqual(sum(p for _, p in rows), 0)
                    self.assertLessEqual(sum(abs(p) for _, p in rows), 2)
                    for v, p in rows:
                        actual[v] = actual.get(v, F(0)) + p
                self.assertEqual({v: p for v, p in expected.items() if p},
                                 {v: p for v, p in actual.items() if p})

    def test_corner_and_orphan_geometric_means(self):
        c = Chain(4)
        self.assertEqual(c.value(c.corner), 1 / qvalue(4, c.d))
        for y in range(4):
            w = change(c.target, 4, y)
            self.assertEqual(c.value(w), 1 / c.d[y][4])

    def test_orphan_is_not_uniform_regular(self):
        c = Chain(6)
        self.assertEqual(c.value(change(c.target, 6, 0)), 6 ** 6)
        self.assertGreater(6 ** 6, 6 * 6)

    def test_predictable_count_matches_two_independent_clocks(self):
        c = Chain(4)
        q = qvalue(4, c.d)
        for y in range(4):
            d = c.d[y][4]
            w = change(c.corner, 4, y)
            self.assertEqual(c.value(w), 1 / q + 1 / d - 1 / (q + d - q * d))
            expected_count = (1 - q) / (q + d - q * d)
            self.assertEqual(c.value(w, 'count'), expected_count)
            self.assertEqual(c.value(w, 'residual'), d * expected_count / q)

    def test_phase_reward_identity_with_shared_breeder(self):
        c = Chain(4)
        alone = change(c.target, 4, 0)
        w = change(change(c.corner, 4, 0), 3, 1)
        for phase in range(6):
            lag = c.suffix(w, phase) - c.suffix(alone, phase)
            self.assertEqual(lag, c.total_reward(w, phase, 'residual'))
            self.assertLessEqual(lag, 24 * c.d[0][4] * c.total_reward(w, phase, 'count'))

    def test_aligned_prefix_is_not_killed_early(self):
        c = Chain(4)
        self.assertEqual(c.value(c.target, 'O'), 0)
        self.assertGreater(c.insert(c.target, 0, ('O',)), 0)

    def test_orphan_first_within_sweep_is_impossible(self):
        c = Chain(4)
        self.assertEqual(c.insert(c.corner, 0, ('O', 'R')), 0)
        self.assertNotEqual(c.insert(c.corner, 0, ('R', 'O')), 0)

    def test_local_chain_not_absorbing_at_positive_noise(self):
        c = Chain(4)
        r0, r1 = local(4, c.d)
        self.assertEqual(r0[4][4], 1)
        self.assertGreater(sum(r1[4][y] for y in range(4)), 0)

    def test_discounted_local_and_joint_chains_agree(self):
        c = Chain(4)
        self.assertGreater(orphan_finite(4, c.d, F(1, 256)), c.value(c.corner))
        h0, h1, h2 = orphan_series(4, c.d)
        q = qvalue(4, c.d)
        self.assertEqual(h0, 1 / q)
        self.assertGreater(h1, 0)
        self.assertLessEqual(abs(h2), 6 / q ** 2)

    def test_gaussian_pivot(self):
        self.assertEqual(solve([[F(0), F(1)], [F(2), F(3)]], [F(5), F(19)]), [2, 5])

    def test_polynomial_expansion_and_constant(self):
        for n in range(3, 30):
            ell, m = 6 * n, n + 1
            rsum = 2 * (2 * ell + 5) * (m * m * ell + comb(m, 2))
            mixed = m * (12 * ell * ell + 16 * ell + 2)
            expanded = 432*n**5 + 2376*n**4 + 2427*n**3 + 543*n**2 + 6*n
            self.assertEqual(3 * n * (rsum + mixed) + 54 * n * n, expanded)
            self.assertLessEqual(F(expanded, n**5), F(40874, 27))
        self.assertLess(F(40874, 27), 1536)


if __name__ == '__main__':
    unittest.main(verbosity=2)
