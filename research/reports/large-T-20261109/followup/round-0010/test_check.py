#!/usr/bin/env python3
"""Regression and independent finite checks for the round-10 obstruction."""
from fractions import Fraction as F
import unittest

import check


class ResolventTests(unittest.TestCase):
    def test_literal_masks(self):
        for n in range(2, 7):
            self.assertEqual(check.kernel(n), check.literal_kernel(n))

    def test_two_mask_composition(self):
        for n in range(3, 9):
            d = check.kernel(n)
            theta = F(2 * (n - 1), n * n)
            for y in range(n + 1):
                value = sum(d[0][z] * d[z][y] for z in range(n + 1))
                self.assertEqual(value, check.comb(n, y) * theta ** y * (1 - theta) ** (n - y))

    def test_odd_pairs_are_closed(self):
        for n in range(3, 20, 2):
            for i in range(n + 1):
                self.assertEqual(set(check.recipients(n, i)), {i - i % 2, i - i % 2 + 1})

    def test_even_orphan_has_only_itself(self):
        for n in range(4, 20, 2):
            self.assertEqual([i for i in range(n + 1) if n in check.recipients(n, i)], [n])

    def test_exact_n3_local_witness(self):
        result = check.pair_formula(3)
        self.assertEqual(result['derivative'], F(-2071, 19683))
        self.assertEqual(result['lower'], F(2071, 8883))

    def test_exact_n4_orphan_witness(self):
        self.assertEqual(check.orphan_formula(4)['lower'], F(959, 256))

    def test_exact_local_derivative(self):
        for n in (3, 5, 7):
            a, b = check.derivative_row(n, (0, 0), local=True)
            self.assertEqual(sum(a.values()), 1)
            self.assertEqual(sum(b.values()), 0)
            self.assertEqual(b[(0, 0)], check.pair_formula(n)['derivative'])

    def test_clean_resolvent_before_absolute_values(self):
        for n in (3, 5, 7):
            local = check.signed_diagonal(n)
            full = check.signed_diagonal(n, full=True)
            self.assertLessEqual(full, local)
            self.assertGreaterEqual(-local, check.pair_formula(n)['signed_lower'])

    def test_large_witness_is_inside_requested_scale(self):
        # n^-4 / (log(n)/n^4) -> 0; this is an exact finite norm obstruction.
        self.assertGreater(check.pair_formula(33)['inverse_scale'], 1000)
        self.assertGreater(check.orphan_formula(32)['inverse_scale'], 1000)

    def test_pair_diagonal_resummation(self):
        for n in (3, 5):
            q = check.pair_formula(n)['escape']
            for p in (F(1, n ** 4), F(1, 2), F(3, 4)):
                den = 1 - check.local_sweep(n, (0, 0), p)[(0, 0)]
                self.assertGreaterEqual(den, (1 - p) ** 2 * q)

    def test_discounted_orphan_tail(self):
        for n in (4, 6):
            for p in ('n^-4', 'q/4'):
                result = check.orphan_tail(n, p)
                self.assertLessEqual(abs(F(result['remainder'])), F(result['bound']))

    def test_invalid_parity(self):
        for function, n in ((check.pair_formula, 4), (check.orphan_formula, 5)):
            with self.assertRaises(ValueError):
                function(n)


if __name__ == '__main__':
    unittest.main(verbosity=2)
