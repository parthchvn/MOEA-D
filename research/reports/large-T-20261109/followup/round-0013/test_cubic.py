#!/usr/bin/env python3
"""Focused deterministic tests of cubic semantics and new cancellations."""
from fractions import Fraction as F
from itertools import product
import unittest
import cubic
import oracle
import words


class CubicTests(unittest.TestCase):
    def tearDown(self):
        cubic.Response.clear()

    def test_mutation_matches_literal_masks(self):
        for n in (3, 4):
            d, den = oracle.masks(n)
            self.assertEqual(cubic.kernel(n), tuple(tuple(F(x, den) for x in row) for row in d))

    def test_neighborhoods_literal(self):
        for n in range(3, 10):
            for t in (2, 3):
                for i in range(n+1):
                    self.assertEqual(cubic.neighbors(n, t, i), tuple(oracle.neighbors(n, t, i)))

    def test_signed_rows_zero(self):
        s = cubic.Response(4, 2)
        for e in ((), s.corner, ((2, 0), (3, 0)), ((0, 2), (4, 0))):
            for i in range(5):
                self.assertEqual(sum(p for _, p in s.delta(e, i)), 0)

    def test_clean_steps_only_delete_errors(self):
        s = cubic.Response(4, 3)
        e = ((0, 2), (1, 4), (3, 0))
        for i in range(5):
            for v, _ in s.clean(e, i):
                self.assertTrue(set(v) <= set(e))

    def test_boundary_zero_is_retained_inside_sweep(self):
        s = cubic.Response(3, 3)
        self.assertEqual(s.h((), 3), 0)
        self.assertNotEqual(s.apply((), 0, 1, 0), 0)

    def test_four_error_budget(self):
        s = cubic.Response(3, 2)
        r = s.coefficients()
        self.assertEqual(r['maximum_clean_errors'], 4)
        self.assertEqual(r['maximum_first_errors'], 3)
        self.assertEqual(r['maximum_second_errors'], 2)

    def test_independent_n3_full_state_oracle(self):
        for t in (2, 3):
            reference = oracle.Full(3, t).coefficients()
            s = cubic.Response(3, t)
            row = s.coefficients()
            for key in ('mean0', 'first', 'second', 'cubic', 'cubic_12', 'cubic_21', 'cubic_30'):
                self.assertEqual(F(row[key]), F(reference[key]))
            s.clear()

    def test_n3_gap_and_normalization(self):
        s = cubic.Response(3, 2)
        a = s.h(s.corner, 3)
        s.clear()
        s = cubic.Response(3, 3)
        b = s.h(s.corner, 3)
        self.assertAlmostEqual(float(b-a), 0.7833960714258787, places=13)

    def test_recipient_split_exact(self):
        s = words.Words(4)
        for e in (s.corner, ((0, 2), (4, 0)), ((2, 0), (3, 0), (4, 0))):
            for i in range(5):
                row = {}
                for letter in 'RO':
                    for v, p in s.insertion(e, i, letter):
                        row[v] = row.get(v, F(0))+p
                self.assertEqual({v: p for v, p in row.items() if p}, dict(s.delta(e, i)))
        s.clear_words()

    def test_two_orphan_insertions_cannot_share_sweep(self):
        s = words.Words(4)
        self.assertEqual(s.suffix(s.corner, 0, 'OO', ''), 0)
        s.clear_words()

    def test_word_sum_is_full_cubic(self):
        s = words.Words(4)
        self.assertEqual(sum(s.value(s.corner, ''.join(w)) for w in product('RO', repeat=3)),
                         s.h(s.corner, 3))
        s.clear_words()

    def test_orphan_excess_identity_with_feedback(self):
        s = words.Words(4)
        e = ((0, 2), (3, 4), (4, 0))
        local = words.local_coefficients(4, s.d)
        b = 1-s.d[4][4]
        for order in range(3):
            excess = s.value(e, 'O'*order)-local[order][0]
            self.assertEqual(excess, sum(b**(order-j)*s.occupancy(e, j) for j in range(order+1)))
        s.clear_words()

    def test_two_birth_inverse_square_cancellation(self):
        for a in (F(1), F(1, 100), F(1, 10**80)):
            for b in (F(1, 2), F(1, 100), F(1, 10**90)):
                L = F(80)
                self.assertLessEqual(a*b*(L+2/(a+b))**2, (L+1)**2)

    def test_phase_excess_bounds(self):
        s = words.Words(4)
        L = F(80)
        for y in (0, 3, 4):
            e = s.put(((0, 2), (3, 4)), 4, y)
            orphan = s.put((), 4, y)
            for i in range(6):
                for j, bound in enumerate((L, 64*L**2, 512*L**3)):
                    excess = s.phase(e, i, 'O'*j)-s.phase(orphan, i, 'O'*j)
                    self.assertLessEqual(abs(excess), bound)
                    if j == 0 and y != 4:
                        self.assertGreaterEqual(excess, 0)
                        self.assertLessEqual(excess, s.d[y][4]*L**2)
        s.clear_words()

    def test_R_annihilates_local_coefficients_at_every_phase(self):
        s = words.Words(4)
        for e in (s.corner, ((0, 2), (3, 4), (4, 0)), ((3, 0),)):
            for i in range(5):
                for j in range(3):
                    value = sum(p*s.phase(s.put((), 4, dict(v).get(4, 4)), i+1, 'O'*j)
                                for v, p in s.insertion(e, i, 'R'))
                    self.assertEqual(value, 0)
        s.clear_words()

    def test_domain_exclusions(self):
        for n in (3, 5):
            with self.assertRaises(ValueError):
                words.Words(n)
        s = cubic.Response(3, 2)
        with self.assertRaises(ValueError):
            s.h(s.corner, 4)


if __name__ == '__main__':
    unittest.main(verbosity=2)
