#!/usr/bin/env python3
"""Semantic checks for the new order and the closed-pair restriction."""
import csv
from fractions import Fraction as F
from functools import lru_cache
from itertools import product
from pathlib import Path
import sys
import unittest
import fourth
import pair
from verify import load

ROOT = Path(__file__).resolve().parent
while not (ROOT/'research/PROJECT.md').exists():
    if ROOT == ROOT.parent:
        raise RuntimeError('Cannot locate repository')
    ROOT = ROOT.parent
PHASE = load(ROOT/'research/reports/large-T-20261109/followup/round-0014/audit.py', 'phase_test')


def literal_pair(n, k, state, breeder, active):
    row = {}
    parent = (1 << state[breeder])-1
    for mut in range(1 << n):
        child = parent ^ mut
        weight = child.bit_count()
        pm = F((n-1)**(n-mut.bit_count()), n**n)
        for noise in (range(1 << n) if active else (0,)):
            observed = (child ^ noise).bit_count()
            pn = F((n-1)**(n-noise.bit_count()), n**n) if active else F(1)
            v = list(state)
            for j, target in enumerate((k, k+1)):
                if max(target*(n-observed), (n-target)*observed) <= target*(n-target):
                    v[j] = weight
            v = tuple(v)
            row[v] = row.get(v, F(0))+pm*pn
    return row


class Tests(unittest.TestCase):
    def tearDown(self):
        fourth.Response.clear()
        for method in (pair.Pair.clean, pair.Pair.delta, pair.Pair.values,
                       PHASE.Phase.clean, PHASE.Phase.delta, PHASE.Phase.values):
            method.cache_clear()

    def test_mutation_independent_implementations(self):
        for n in range(3, 10):
            self.assertEqual(fourth.kernel(n), pair.mutation(n))
            self.assertEqual(pair.mutation(n), PHASE.mutation(n))

    def test_literal_pair_rows(self):
        n = 3
        for k in range(n):
            p = pair.Pair(n, k)
            for state in product(range(n+1), repeat=2):
                for i in (0, 1):
                    clean = dict(p.clean(state, i))
                    self.assertEqual(clean, literal_pair(n, k, state, i, False))
                    active = dict(clean)
                    for v, mass in p.delta(state, i):
                        active[v] = active.get(v, F(0))+mass
                    self.assertEqual({v:m for v,m in active.items() if m},
                                     literal_pair(n, k, state, i, True))
            p.clear()

    def test_pair_boundary_only_killing(self):
        p = pair.Pair(4, 2)
        self.assertEqual(p.values(p.target, 0), (0, 1))
        self.assertEqual(p.values(p.target, 1)[0], 0)
        self.assertGreater(p.values(p.target, 1)[1], 0)

    def test_pair_phase_poisson(self):
        p = pair.Pair(5, 4)
        for state in ((0, 0), (0, 5), (4, 0)):
            for degree in range(3):
                for i in (0, 1):
                    rhs = F(degree == 0)
                    rhs += sum(m*p.values(v, degree)[1-i] for v,m in p.clean(state, i))
                    if degree:
                        rhs += sum(m*p.values(v, degree-1)[1-i] for v,m in p.delta(state, i))
                    self.assertEqual(p.values(state, degree)[i], rhs)

    def test_pair_matches_restricted_full_phase_solver(self):
        class Restricted(PHASE.Phase):
            @lru_cache(None)
            def delta(self, state, i, letter):
                if i not in self.selected:
                    return ()
                return super().delta(state, i, 'D')
        for k in (0, 2):
            full = Restricted(3, 2)
            full.selected = (k, k+1)
            local = pair.Pair(3, k)
            for state in ((0, 0), (3, 3), (k, 0)):
                population = PHASE.replace(PHASE.replace(full.target, k, state[0]), k+1, state[1])
                for j in range(3):
                    self.assertEqual(local.values(state, j)[0]/2,
                                     full.values(population, 'D'*j)[0])
            full.clear()
            local.clear()

    def test_orphan_fed_pair_is_not_closed(self):
        full = PHASE.Phase(4, 2)
        local = pair.Pair(4, 2)
        state = (0, 1, 0, 0, 4)
        self.assertLess(full.values(state)[0], local.values((0, 0))[0]/2)

    def test_fourth_has_all_four_sweep_terms(self):
        solver = fourth.Response(3, 2)
        result = solver.coefficients()
        terms = [F(result[f'fourth_{j}{4-j}']) for j in range(1, 5)]
        self.assertTrue(all(v != 0 for v in terms))
        self.assertEqual(sum(terms), F(result['fourth']))
        oracle = PHASE.Phase(3, 2)
        self.assertEqual(F(result['fourth']), oracle.values(oracle.corner, 'DDDD')[0])

    def test_no_repeated_insertion_at_one_attempt(self):
        solver = fourth.Response(3, 2)
        self.assertEqual(solver.apply(solver.corner, 3, 2, 0), 0)
        self.assertEqual(solver.apply(solver.corner, 0, 5, 0), 0)

    def test_positive_entrance_factors(self):
        n, x = 9, 4
        row = pair.supplied_entrance([n])[0]
        d = pair.mutation(n)
        a, b = d[x][n-1], d[x][n]
        c = F(n-1, n)**n
        q = 1-(1-d[2][0])*(1-d[1][0])
        expected = (1-q)*q*c*c*(1-a-b)*d[n-1][x]*a*b
        self.assertEqual(F(row['entry_path_weight']), expected)
        self.assertEqual(F(row['clean_escape']), 1-(1-a-b)**2)

    def test_supplied_entrance_is_in_actual_signed_sweep_kernel(self):
        n, x = 9, 4
        solver = fourth.Response(n, 2)

        def one_insertion(start):
            dist = [{start: F(1)}, {}]
            for i in range(n+1):
                out = [{}, {}]
                for degree in (0, 1):
                    for state, mass in dist[degree].items():
                        for v, probability in solver.clean(state, i):
                            out[degree][v] = out[degree].get(v, F(0))+mass*probability
                        if degree == 0:
                            for v, probability in solver.delta(state, i):
                                out[1][v] = out[1].get(v, F(0))+mass*probability
                dist = [{s:p for s,p in row.items() if p} for row in out]
            return dist[1]

        intermediate = ((0, 2), (n-1, x))
        end = ((n-1, x), (n, x))
        first = one_insertion(solver.corner)[intermediate]
        second = one_insertion(intermediate)[end]
        witness = F(pair.supplied_entrance([n])[0]['entry_path_weight'])
        self.assertGreater(first, 0)
        self.assertGreater(second, 0)
        self.assertGreaterEqual(first*second, witness)

    def test_likelihood_ratio_bound_event(self):
        for n in (3, 5, 8):
            d = pair.mutation(n)
            eta = F(1, n)
            theta = 2*eta*(1-eta)
            chi = (theta*theta/eta+(1-theta)**2/(1-eta))**n
            self.assertLess(chi, 3)
            for x in range(n+1):
                for k in range(n):
                    base = d[x][k]+d[x][k+1]
                    active = sum(d[x][z]*(d[z][k]+d[z][k+1]) for z in range(n+1))
                    self.assertLessEqual(active*active, chi*base)

    def test_pair_forcing_bounds_without_rounded_roots(self):
        for n in (3, 4, 5):
            for k in range(n):
                p = pair.Pair(n, k)
                L, H = F(32*n), F(64*(32*n)**2)
                for state in product(range(n+1), repeat=2):
                    if state == p.target:
                        continue
                    double = state[0] != k and state[1] != k+1
                    for i in (0, 1):
                        g0 = abs(sum(m*p.values(v, 0)[1-i] for v,m in p.delta(state, i)))
                        g1 = abs(sum(m*p.values(v, 1)[1-i] for v,m in p.delta(state, i)))
                        if double:
                            a, b = p.r[state[0]], p.r[state[1]]
                            u = a+b
                            z = max(F(0), (g0-4*L)/7)
                            self.assertLessEqual(z*z*u, 1)
                            # z <= a^(-1/2)+b^(-1/2), by two exact squarings.
                            z = max(F(0), g1/H-4-4/u)
                            residual = max(F(0), z*z-1/a-1/b)
                            self.assertLessEqual(residual*residual*a*b, 4)
                        else:
                            a = p.r[state[0]] if state[0] != k else p.r[state[1]]
                            self.assertLessEqual(g0, 4*L)
                            z = max(F(0), g1/H-4)
                            self.assertLessEqual(z*z*a, 1)
                p.clear()


if __name__ == '__main__':
    unittest.main(verbosity=2)
