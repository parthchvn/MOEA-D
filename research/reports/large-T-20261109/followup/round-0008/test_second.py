#!/usr/bin/env python3
"""Small adversarial tests for the expansion and bounds; no random draws."""
from fractions import Fraction as F
import unittest
from bounds import Restricted, orphan, polynomial, q_value, remainder, sign_window
from oracle import masks, neighbors as literal_neighbors, replace
from second import Response, kernel, neighbors


class SecondTests(unittest.TestCase):
    def tearDown(self):
        Response.clear()

    def test_kernel_matches_literal_masks(self):
        for n in range(3, 8):
            integers, den = masks(n)
            self.assertEqual(kernel(n), tuple(tuple(F(v, den) for v in row) for row in integers))

    def test_neighborhood_orphan_and_boundary_fill(self):
        for n in range(3, 18):
            for t in (2, 3):
                self.assertEqual([neighbors(n, t, i) for i in range(n+1)],
                                 [tuple(literal_neighbors(n, t, i)) for i in range(n+1)])
            if n % 2 == 0:
                self.assertEqual([i for i in range(n+1) if n in neighbors(n, 2, i)], [n])

    def test_signed_step_matches_literal_active_minus_clean(self):
        n = 3
        for t in (2, 3):
            s = Response(n, t)
            for e in ((), s.corner, ((0, 3), (1, 0), (2, 3))):
                w = tuple(dict(e).get(i, i) for i in range(n+1))
                for i in range(n+1):
                    expected = {}
                    for y in range(n+1):
                        for z in range(n+1):
                            v = replace(w, n, t, i, y, z)
                            key = tuple((k, x) for k, x in enumerate(v) if k != x)
                            mass = s.d[w[i]][y]*(s.d[y][z]-int(y == z))
                            expected[key] = expected.get(key, F(0))+mass
                    self.assertEqual(dict(s.delta(e, i)), {v: p for v, p in expected.items() if p})
                    self.assertEqual(sum(p for _, p in s.delta(e, i)), 0)
                    self.assertLessEqual(sum(abs(p) for _, p in s.delta(e, i)), 2)

    def test_recipient_split_sums_to_full_operator(self):
        s = Response(4, 2)
        for e in ((), s.corner, ((0, 2), (4, 0))):
            for i in range(5):
                result = {}
                for selected in ([4], range(4)):
                    rows = s.delta_targets(e, i, selected)
                    self.assertLessEqual(sum(abs(p) for _, p in rows), 2)
                    for v, p in rows:
                        result[v] = result.get(v, F(0))+p
                self.assertEqual({v: p for v, p in result.items() if p}, dict(s.delta(e, i)))

    def test_boundary_killing_keeps_aligned_prefixes(self):
        s = Response(3, 3)
        self.assertEqual(s.h((), 1), 0)
        self.assertGreater(s.apply((), 0, 1, 0), 0)

    def test_second_is_not_second_derivative(self):
        s = Response(3, 2)
        row = s.coefficients()
        self.assertEqual(F(row['second']), F(row['between'])+F(row['within']))
        self.assertNotEqual(F(row['within']), 0)
        self.assertAlmostEqual(float(F(row['second'])), 7.0337034734929595, places=12)

    def test_omitting_same_sweep_terms_changes_gap(self):
        a = Response(3, 2).coefficients()
        b = Response(3, 3).coefficients()
        self.assertNotEqual(F(b['second'])-F(a['second']), F(b['between'])-F(a['between']))

    def test_zero_noise_corner_and_q_bounds(self):
        for n in range(3, 11):
            s = Response(n, 2)
            q = q_value(n)
            self.assertEqual(s.h(s.corner), 1/q)
            self.assertGreaterEqual(q, F(1, 3*n))
            self.assertLessEqual(q, F(1, 2))
            s.clear()

    def test_orphan_is_not_a_regular_uniform_mean_state(self):
        s = Response(6, 2)
        self.assertEqual(s.h(((6, 0),)), 6**6)
        self.assertGreater(s.h(((6, 0),)), 6*s.n)

    def test_discounted_orphan_formula_matches_insertions(self):
        s = Restricted(4, 2, [4])
        row = s.coefficients()
        analytic = orphan(4)
        self.assertEqual(F(row['first']), analytic['first'])
        self.assertEqual(F(row['second']), analytic['second'])

    def test_polynomial_constant_and_parity_bound(self):
        for n in range(3, 101):
            self.assertLessEqual(polynomial(n)['gap'], 1536*n**5)

    def test_remainder_window_and_domain(self):
        for n, A in ((3, F(2, 9)), (4, F(-3, 2)), (20, F(-10))):
            p = sign_window(n, A)
            self.assertLessEqual(remainder(n, p, 1), abs(A)*p/2)
            self.assertLessEqual(remainder(n, p, 2), remainder(n, p, 1))
        with self.assertRaises(ValueError):
            remainder(3, F(1, 2))


if __name__ == '__main__':
    unittest.main(verbosity=2)
