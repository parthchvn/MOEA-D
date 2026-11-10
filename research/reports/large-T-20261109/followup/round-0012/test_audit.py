#!/usr/bin/env python3
"""Small falsification/regression cases; the main audit does the large solve."""
from fractions import Fraction as F
import unittest
import audit as a


class AuditTests(unittest.TestCase):
    def test_kernel_endpoint_and_row_sums(self):
        for n in (3, 4, 7):
            d = a.mutation(n)
            self.assertEqual(d[0][n], F(1, n**n))
            self.assertEqual(d[0][0], F(n-1, n)**n)
            self.assertTrue(all(sum(row) == 1 for row in d))

    def test_mutation_and_noise_masks(self):
        for state in ((0, 0), (1, 2), (3, 0)):
            for donor in (1, 2):
                for active in (False, True):
                    self.assertEqual(a.attempt(3, (1, 2), state, donor, (1, 2), active),
                                     a.literal_attempt(3, (1, 2), state, donor, (1, 2), active))

    def test_accepts_only_target_observation(self):
        for obs in range(4):
            new = a.selected(3, (0, 1, 2, 3), (3, 3, 0, 0), (0, 1, 2, 3), 1, obs)
            expected = [3, 3, 0, 0]
            expected[obs] = 1
            self.assertEqual(new, tuple(expected))

    def test_phase_recurrences_in_both_orders(self):
        pair = a.Pair(4, 1)
        for phase in (0, 1):
            v = a.apply(pair.K[phase], pair.V[1-phase])
            for s in pair.D:
                self.assertEqual(v[s]-pair.V[phase][s], -1)

    def test_bernstein_basis_conversion(self):
        coeff = (F(2, 3), F(-5, 7), F(11, 13))
        b = a.bernstein2(coeff)
        for t in (F(0), F(1, 7), F(1, 2), F(1)):
            p = t/6
            self.assertEqual(sum(c*p**j for j, c in enumerate(coeff)),
                             b[0]*(1-t)**2+2*b[1]*t*(1-t)+b[2]*t*t)

    def test_interval_certificate_covers_even_n_and_odd_a(self):
        for n, target in ((3, 0), (4, 1), (6, 4)):
            self.assertTrue(a.phase_certificate(n, target)['exact_pass'])

    def test_closed_pair_qualification(self):
        for n in range(3, 13):
            for target in range(n):
                expected = target % 2 == 0 and not (n % 2 == 0 and target == n-2)
                self.assertEqual(a.closed_pair(n, target), expected)

    def test_midpoint_paths_are_positive(self):
        row = a.witnesses()
        self.assertGreater(F(row['repair_then_reinfection']), 0)
        self.assertGreater(F(row['midpoint_alignment_then_corruption']), 0)
        self.assertGreater(F(row['orphan_repairs_last_pair']), 0)

    def test_fraction_free_solver_exact_residual(self):
        solution = a.rational_solve([[F(2), F(1)], [F(1), F(3)]],
                                    [[F(1), F(0)], [F(2), F(1)]])
        self.assertEqual(solution, [[F(1, 5), F(-1, 5)], [F(3, 5), F(2, 5)]])

    def test_pair_schur_with_nonabsorbing_midpoint(self):
        row, _, _, _ = a.pair_solve(3, 2, F(1, 81))
        self.assertTrue(row['exact_schur_equals_direct'])
        self.assertLess(F(row['max_weighted_residence']), F(row['residence_bound']))

    def test_moment_lower_bound(self):
        row = a.moment(33)
        self.assertGreaterEqual(F(row['iterated_residence_path']), F(row['coarse']))
        self.assertGreater(row['iterated_residence_decimal'], 1e43)

    def test_domain_exclusions(self):
        for n, target in ((2, 0), (3, -1), (3, 3)):
            with self.assertRaises(ValueError):
                a.Pair(n, target)
        with self.assertRaises(ValueError):
            a.moment(4)


if __name__ == '__main__':
    unittest.main(verbosity=2)
