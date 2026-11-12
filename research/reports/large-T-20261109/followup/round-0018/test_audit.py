#!/usr/bin/env python3
"""Independent literal-mask and stopping-convention regressions."""
from fractions import Fraction as F
import unittest

from audit import Raw, fingerprint, geometry, put


def literal(c, s, i, active, restricted=None):
    row = {}
    genome = (1 << s[i])-1
    for mutation in range(1 << c.n):
        child = genome ^ mutation
        probability = F((c.n-1)**(c.n-mutation.bit_count()), c.n**c.n)
        for noise in (range(1 << c.n) if active else (0,)):
            p = probability*(F((c.n-1)**(c.n-noise.bit_count()), c.n**c.n) if active else 1)
            observed = (child ^ noise).bit_count()
            end = list(s)
            for k in c.recipients(i):
                if restricted == 'R' and k == c.n or restricted == 'O' and k != c.n:
                    continue
                if max(k*(c.n-observed), (c.n-k)*observed) <= k*(c.n-k):
                    end[k] = child.bit_count()
            key = tuple(end)
            row[key] = row.get(key, F(0))+p
    return row


class AuditTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.c = Raw(4)

    @classmethod
    def tearDownClass(cls):
        cls.c.clear()

    def test_literal_mutation_convolution(self):
        c = self.c
        for x in range(c.n+1):
            row = [F(0)]*c.m
            for mask in range(1 << c.n):
                y = (((1 << x)-1) ^ mask).bit_count()
                row[y] += F((c.n-1)**(c.n-mask.bit_count()), c.n**c.n)
            self.assertEqual(tuple(row), c.d[x])
            self.assertEqual(sum(row), 1)

    def test_filled_cardinality_and_final_orphan_feed(self):
        self.assertEqual([self.c.recipients(i) for i in range(5)],
                         [(0, 1), (1, 0), (2, 3), (3, 2), (4, 3)])

    def test_literal_clean_rows(self):
        c = self.c
        for s in (c.target, c.corner, (4, 0, 1, 0, 0)):
            for i in range(c.m):
                self.assertEqual(dict(c.clean(s, i)), literal(c, s, i, False))

    def test_raw_forcing_matches_literal_active_minus_clean(self):
        c = self.c
        for s in (c.corner, (2, 1, 0, 0, 0)):
            for i in range(c.m):
                active = literal(c, s, i, True, 'R')
                clean = literal(c, s, i, False, 'R')
                for j in (1, 2):
                    nxt = (i+1) % c.m
                    expected = sum(p*c.values(v, j-1)[nxt] for v, p in active.items())
                    expected -= sum(p*c.values(v, j-1)[nxt] for v, p in clean.items())
                    self.assertEqual(c.forcing(s, i, j), expected)

    def test_baseline_only_functions_are_annihilated_including_wrap(self):
        c = self.c
        s = (4, 0, 1, 0, 0)
        for i in range(c.m):
            nxt = (i+1) % c.m
            active = literal(c, s, i, True, 'R')
            clean = literal(c, s, i, False, 'R')
            self.assertEqual(sum(p*(v[-1]**2+3*nxt+7) for v, p in active.items()),
                             sum(p*(v[-1]**2+3*nxt+7) for v, p in clean.items()))

    def test_boundary_killing_and_live_interior_rewards(self):
        c = self.c
        self.assertEqual(c.values(c.target, 0), (F(0), F(4, 5), F(3, 5), F(2, 5), F(1, 5)))
        self.assertEqual(c.values(c.corner, 0)[0], 1/c.q)
        self.assertEqual(c.values(c.target, 1)[0], 0)
        self.assertNotEqual(c.values(c.target, 1)[1], 0)

    def test_unrestricted_equation_requires_compensation(self):
        c = self.c
        for j in (0, 1, 2):
            wrong = c.forcing(c.target, 0, j)+c.values(c.target, j)[1]
            self.assertEqual(wrong-c.values(c.target, j)[0], c.flux(j))
            self.assertGreater(abs(c.flux(j)), 0)

    def test_centered_correct_orphan_boundary_residual(self):
        c = self.c
        for j in (0, 1, 2):
            s = c.corner
            rhs = sum(p*c.centered(v, j)[1] for v, p in c.clean(s, 0))
            if j:
                rhs += c.forcing(s, 0, j)-c.forcing(c.target, 0, j)
            self.assertEqual(c.centered(s, j)[0]-rhs, c.flux(j))

    def test_centered_wrong_orphan_has_no_immediate_flux(self):
        c = self.c
        s = put(c.corner, c.n, 0)
        for j in (0, 1, 2):
            rhs = sum(p*c.centered(v, j)[1] for v, p in c.clean(s, 0))
            if j:
                rhs += c.forcing(s, 0, j)-c.forcing(c.base(0), 0, j)
            self.assertEqual(c.centered(s, j)[0], rhs)

    def test_centered_zero_at_all_regular_complete_phases(self):
        c = self.c
        for y in range(c.m):
            for j in (0, 1, 2):
                self.assertEqual(c.centered(c.base(y), j), (F(0),)*c.m)

    def test_D0_equals_stopped_correct_boundary_reward(self):
        c = self.c
        for s in (c.corner, (2, 1, 0, 0, 0), (4, 0, 2, 3, 1)):
            self.assertEqual(c.centered(s, 0), c.boundary_reward(s))

    def test_last_pair_orphan_not_independent(self):
        c = self.c
        row = c.clean((0, 1, 2, 0, 0), 4)
        reg = sum(p for s, p in row if s[:-1] == c.target[:-1])
        orphan = sum(p for s, p in row if s[-1] == 4)
        joint = sum(p for s, p in row if s == c.target)
        self.assertEqual((reg, orphan, joint), (F(3, 64), F(1, 256), 0))
        self.assertNotEqual(joint, reg*orphan)

    def test_actual_orphan_entrance_and_negative_stay(self):
        c = self.c
        active = literal(c, c.corner, 4, True, 'O')
        clean = literal(c, c.corner, 4, False, 'O')
        for y in range(4):
            self.assertEqual(active[put(c.corner, 4, y)], c.d[4][y]*c.d[y][4])
        self.assertEqual(active[c.corner]-clean[c.corner],
                         -sum(c.d[4][y]*c.d[y][4] for y in range(4)))

    def test_support_budget_and_first_excluded_state(self):
        c = self.c
        self.assertEqual(c.budget((2, 0, 0, 0, 0)), 3)
        self.assertEqual(c.bad_pairs((2, 0, 0, 0, 0)), (2,))
        self.assertEqual(c.budget((3, 0, 0, 0, 0)), 4)
        with self.assertRaises(ValueError):
            c.cap((3, 0, 0, 0, 0))
        self.assertTrue(all(r['budget3'] > 0 for r in geometry()))

    def test_acceptance_mark_cancels_inverse(self):
        c = self.c
        for a in c.d[0]:
            for b in c.d[1]:
                self.assertLessEqual(b*(c.L+2/(a+b))**2, 2*c.L*c.L+2/a)

    def test_independent_ORRR_fraction(self):
        self.assertEqual(fingerprint(self.c.orrr()),
                         'e1f370a5361766437f233a3616fc63aead43324f2e4d6bc53b4a385b67d084c2')

    def test_scope_restriction(self):
        for n in (2, 3, 5):
            with self.assertRaises(ValueError):
                Raw(n)


if __name__ == '__main__':
    unittest.main(verbosity=2)
