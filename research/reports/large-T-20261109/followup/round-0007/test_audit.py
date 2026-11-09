#!/usr/bin/env python3
"""Deterministic adversarial checks for the mathematical audit; no RNG draws."""
from fractions import Fraction as F
import unittest
from audit import Oracle, kernel, pair_terms


class AuditTests(unittest.TestCase):
    def tearDown(self):
        Oracle.clear()

    def test_polynomial_kernel_literal_masks(self):
        # Enumerate masks directly, independently of coefficient multiplication.
        for n in range(3, 8):
            d = kernel(n)
            for x in range(n + 1):
                parent = (1 << x) - 1
                row = [0] * (n + 1)
                for mask in range(1 << n):
                    row[(parent ^ mask).bit_count()] += (n - 1) ** (n - mask.bit_count())
                self.assertEqual(d[x], tuple(F(v, n ** n) for v in row))

    def test_kernel_normalization_and_complement(self):
        for n in (3, 8, 17):
            d = kernel(n)
            for x in range(n + 1):
                self.assertEqual(sum(d[x]), 1)
                self.assertEqual(d[x], tuple(reversed(d[n - x])))

    def test_literal_scalarization_pins_single_recipient(self):
        for n in range(3, 9):
            for z in range(n + 1):
                accepted = [k for k in range(n + 1) if max(k * (n - z), (n - k) * z) <= k * (n - k)]
                self.assertEqual(accepted, [z])

    def test_neighborhood_donors_even_orphan(self):
        for n in range(4, 26, 2):
            s = Oracle(n, 2)
            self.assertEqual(s.inc[n], (n,))
            self.assertEqual(s.inc[n - 1], (n - 2, n - 1, n))
            self.assertEqual(s.inc[0], (0, 1))
            s.clear()

    def test_endpoint_geometric_mean(self):
        for n in range(3, 11):
            for t in (2, 3):
                s = Oracle(n, t)
                self.assertEqual(s.h(s.corner), 1 / s.q)
                self.assertTrue(F(1, 3 * n) <= s.q <= F(2, n))
                s.clear()

    def test_clean_suffix_never_changes_wrong_value(self):
        s = Oracle(6, 3)
        w = s.put(s.corner, 1, 6)
        for start in range(8):
            dist = s.sweep(w, start)
            self.assertEqual(sum(dist.values()), 1)
            for v in dist:
                self.assertTrue(all(y in (w[k], k) for k, y in enumerate(v)))

    def test_arbitrary_donor1_wrong_weight_is_covered(self):
        for t in (2, 3):
            s = Oracle(8, t)
            for y in range(9):
                for w in (s.corner, s.target):
                    self.assertLessEqual(s.h(s.put(w, 1, y)), 40)
            s.clear()

    def test_insertion_parent_zero_invalidates_mass_shortcut(self):
        d = kernel(64)
        # A real counterexample to the unjustified extension to parent zero.
        self.assertGreater(d[0][0] * d[0][1], F(5, 64))
        for x in (1, 2):
            self.assertLessEqual(sum(d[x][y] * d[y][1] for y in range(65) if y != 1), F(5, 64))

    def test_recipient1_donors_have_valid_prefix_weights(self):
        for n in range(8, 25):
            for t in (2, 3):
                s = Oracle(n, t)
                self.assertLessEqual(set(s.inc[1]), {0, 1, 2})
                prefix = {s.corner}
                for i in range(n + 1):
                    if i in s.inc[1]:
                        self.assertTrue(all(w[i] in (1, 2) for w in prefix))
                    prefix = {v for w in prefix for v in s.clean(w, i)}
                self.assertEqual(prefix, {s.corner, s.target})
                s.clear()

    def test_slot2_shared_breeder_delay_bound(self):
        s = Oracle(8, 3)
        self.assertIn(1, s.inc[2])
        for y in (0, 1, 3, 8):
            for i in s.inc[2]:
                delta = s.value(s.put(s.corner, 2, y), i + 1) - s.value(s.corner, i + 1)
                self.assertGreaterEqual(delta, 0)
                self.assertLessEqual(delta, 98 * s.q)
        self.assertLessEqual(s.contribution(2), 420)

    def test_aligned_mid_sweep_errors_remain_in_value(self):
        s = Oracle(4, 3)
        self.assertEqual(s.h(s.target), 0)
        self.assertGreater(s.value(s.put(s.target, 4, 3), 5), 0)

    def test_pair_formula_both_cyclic_orders(self):
        for n in range(5, 10):
            s = Oracle(n, 2)
            for k in range(2, n):
                if len(s.inc[k]) != 2:
                    continue
                j = next(i for i in s.inc[k] if i != k)
                self.assertEqual(sum(pair_terms(s.d, s.q, k, j).values()), s.contribution(k))
            s.clear()

    def test_order_factors_cannot_be_swapped(self):
        s = Oracle(8, 2)
        k, j = 2, 3
        a = s.d[j][k]
        correct = pair_terms(s.d, s.q, k, j)[j]
        wrong = ((1 - a) * s.d[j][j] + s.d[k][j]) / ((2 - a) * (s.q + (1 - s.q) * a * (2 - a)))
        self.assertNotEqual(correct, wrong)

    def test_q_correction_is_positive_and_bounded(self):
        s = Oracle(16, 2)
        k, j, u = 2, 3, 3
        a = s.d[j][k]
        lead = pair_terms(s.d, s.q, k, j)[j]
        zero_q = (s.d[j][j] + (1 - a) * s.d[k][j]) / (a * (2 - a) ** 2)
        self.assertGreater(zero_q, lead)
        self.assertLessEqual(zero_q - lead, F(36 * s.n, u * u))
        self.assertLessEqual(abs(lead - F(s.n, 2 * u)), 64 * (1 + F(s.n, u * u)))

    def test_common_endpoint_contribution(self):
        for n in (3, 4, 8):
            a, b = Oracle(n, 2), Oracle(n, 3)
            self.assertEqual(a.contribution(0), b.contribution(0))
            Oracle.clear()


if __name__ == '__main__':
    unittest.main(verbosity=2)
