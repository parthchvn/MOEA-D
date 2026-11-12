#!/usr/bin/env python3
"""Focused exact falsification/regression checks for the pair elimination."""
from fractions import Fraction as F
import unittest
import check as c


class PairTests(unittest.TestCase):
    def test_mutation_kernel(self):
        for n in (3, 4, 5):
            self.assertEqual(c.kernel(n), c.literal_kernel(n))
            self.assertTrue(all(sum(row) == 1 for row in c.kernel(n)))

    def test_literal_scalar_attempts(self):
        pair = c.Pair(3, 2)
        for phase in (0, 1):
            for active in (False, True):
                self.assertEqual(pair.step(phase, active), pair.literal_step(phase, active))

    def test_clean_phase_equations(self):
        pair = c.Pair(5, 2)
        for phase in (0, 1):
            values = c.act(pair.step(phase, False), pair.v[1-phase])
            for i in pair.D:
                self.assertEqual(values[i]-pair.v[phase][i], -1)

    def test_all_sweep_bounds(self):
        for n, a in ((3, 0), (3, 2), (5, 4)):
            for p in (F(0), F(1, n**4), F(1, 12)):
                self.assertTrue(c.check_inequalities(c.Pair(n, a), p)['exact_pass'])

    def test_repair_then_reinfection_is_retained(self):
        pair = c.Pair(3, 2)
        p = F(1, 81)
        first, second = pair.mixed_step(0, p), pair.mixed_step(1, p)
        e = pair.index[(0, 0)]
        killed = sum(first[e].get(j, F(0))*second[j].get(e, F(0)) for j in pair.D)
        actual = pair.sweep(p)[e][e]
        self.assertGreater(actual, killed)
        # E -> (2,0) by a clean first attempt, then -> E by active noise.
        f = pair.index[(2, 0)]
        self.assertGreater(first[e][f]*second[f][e], 0)

    def test_midpoint_alignment_is_not_absorbed(self):
        pair = c.Pair(3, 2)
        p = F(1, 81)
        first, second = pair.mixed_step(0, p), pair.mixed_step(1, p)
        s = pair.index[(2, 0)]
        wrong = pair.index[(2, 2)]
        self.assertGreater(first[s][pair.A]*second[pair.A][wrong], 0)
        self.assertGreater(pair.sweep(p)[s][wrong], 0)

    def test_schur_equals_direct(self):
        row = c.schur_cell(3, 2, F(1, 81))
        self.assertTrue(row['exact_schur_equals_direct'])
        self.assertTrue(row['stochastic_exit'])

    def test_aligned_double_entry_is_quadratic(self):
        pair = c.Pair(3, 0)
        for phase in (0, 1):
            for active in (False, True):
                row = pair.step(phase, active)[pair.A]
                self.assertEqual(sum(row.get(i, F(0)) for i in pair.D), 0)
        row = c.schur_cell(3, 0, F(1, 192))
        self.assertLessEqual(F(row['aligned_weighted_residence']), F(row['aligned_bound']))

    def test_higher_residence_path(self):
        pair = c.Pair(5, 4)
        s, e = pair.index[(0, 5)], pair.index[(0, 0)]
        first, second = pair.step(0, True), pair.step(1, False)
        path = first[s][e]*second[e][e]
        witness = c.moment_obstruction(5)
        self.assertGreaterEqual(path, F(witness['entrance_derivative_lower']))
        q = 1-pair.sweep(F(0))[e][e]
        self.assertEqual(q, F(witness['clean_exit']))

    def test_moment_obstruction_grows(self):
        for n in (3, 9, 33):
            row = c.moment_obstruction(n)
            self.assertGreaterEqual(F(row['iterated_residence_lower']), F(row['coarse_lower']))
        self.assertGreater(c.moment_obstruction(33)['iterated_residence_decimal'], 1e40)

    def test_closed_pair_neighborhood_qualification(self):
        def neighbors(n, i):
            for distance in range(1, n+1):
                for sign in ((1, -1) if i % 2 == 0 else (-1, 1)):
                    j = i+sign*distance
                    if 0 <= j <= n:
                        return (i, j)
        for n in (3, 5, 7):
            for a in range(0, n, 2):
                self.assertEqual(set(neighbors(n, a)), {a, a+1})
                self.assertEqual(set(neighbors(n, a+1)), {a, a+1})
                self.assertFalse(any(a in neighbors(n, j) or a+1 in neighbors(n, j)
                                     for j in range(n+1) if j not in (a, a+1)))
        self.assertIn(5, neighbors(6, 6))  # Last pair receives orphan input.
        self.assertNotIn(6, neighbors(6, 5))

    def test_domain_and_solver(self):
        with self.assertRaises(AssertionError):
            c.check_inequalities(c.Pair(3, 0), F(1, 6))
        self.assertEqual(c.solve([[F(2), F(1)], [F(1), F(3)]], [[F(1)], [F(2)]]),
                         [[F(1, 5)], [F(3, 5)]])

    def test_full_tensor_kernel(self):
        self.assertTrue(c.full_tensor_checks()['exact_tensor_match'])


if __name__ == '__main__':
    unittest.main(verbosity=2)
