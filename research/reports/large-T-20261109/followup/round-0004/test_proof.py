#!/usr/bin/env python3
"""Independent small-state/unit checks of the proposed proof machinery."""
from fractions import Fraction as F
from itertools import product
from math import comb
import unittest

from check import (advance, check_renewal, coupled_step, incoming, mutation,
                   multiply, neighbors, noise, pinned, repair, solve)


class ProofTests(unittest.TestCase):
    def test_mutation_against_literal_bit_masks(self):
        for n in range(2, 6):
            d = mutation(n)
            for i in range(n+1):
                genome = (1,)*i+(0,)*(n-i)
                law = [F(0)]*(n+1)
                for mask in product((0, 1), repeat=n):
                    flips = sum(mask)
                    child = sum(x ^ bit for x, bit in zip(genome, mask))
                    law[child] += F((n-1)**(n-flips), n**n)
                self.assertEqual(law, d[i])

    def test_pinned_chain_against_all_outcomes(self):
        n, p = 4, F(1, 17)
        d, obs = mutation(n), noise(mutation(n), p)
        for k in range(n+1):
            q = pinned(d, p, k)
            for i in range(n+1):
                law = [F(0)]*(n+1)
                for j, observed in product(range(n+1), repeat=2):
                    new = j if observed == k else i
                    law[new] += d[i][j]*obs[j][observed]
                self.assertEqual(law, q[i])

    def test_zero_noise_hitting_is_geometric(self):
        d = mutation(5)
        for k in range(6):
            h = repair(d, F(0), k)
            for i in range(6):
                self.assertEqual(h[i], F(0) if i == k else 1/d[i][k])

    def test_composed_endpoint_kernel(self):
        for n in range(2, 7):
            d = mutation(n)
            dd = multiply(d, d)
            q = F(2*(n-1), n*n)
            self.assertEqual(dd[2][0], q*q*(1-q)**(n-2))

    def test_exact_solver_residual(self):
        a = [[F(0), F(2)], [F(3), F(4)]]
        b = [F(5), F(6)]
        x = solve(a, b)
        self.assertEqual([sum(u*v for u, v in zip(row, x)) for row in a], b)

    def test_even_cardinality_is_not_assumed_reciprocal(self):
        self.assertIn(5, neighbors(6, 2, 6))
        self.assertNotIn(6, neighbors(6, 2, 5))
        for n in (3, 6, 11):
            self.assertEqual(incoming(n, 2, 0), [0, 1])
            self.assertEqual(incoming(n, 3, 0), [0, 1])
        self.assertEqual(incoming(6, 4, 0), [0, 1])

    def test_pinned_observation_has_at_most_one_recipient(self):
        before = (2, 1, 2, 3, 4)
        after = advance(before, 4, 5, 0, 3, 1)
        self.assertEqual(after, (2, 3, 2, 3, 4))

    def test_reinfection_is_not_absorbing(self):
        w = (2, 1, 2, 3, 4, 5, 6)
        w = advance(w, 6, 5, 1, 0, 0)
        self.assertEqual(w, tuple(range(7)))
        self.assertEqual(advance(w, 6, 5, 2, 1, 0), (1, 1, 2, 3, 4, 5, 6))

    def test_correct_donor_can_be_corrupted(self):
        self.assertEqual(advance((2, 1, 2, 3), 3, 3, 1, 0, 1), (2, 0, 2, 3))

    def test_unused_base_is_still_an_independent_immigrant(self):
        w, particles, tags = coupled_step(
            (2, 1, 2), {0: (0, 2)}, {0: 0}, 2, 3, 0,
            {'base': (2, 1), 0: (2, 2)})
        self.assertEqual(w, (2, 1, 2))
        self.assertEqual(tags, {0: 0})
        self.assertIn((1, 2), particles.values())

    def test_external_child_can_act_later_same_sweep(self):
        w, particles, tags = coupled_step(
            (2, 1, 2), {0: (0, 2)}, {0: 0}, 2, 3, 0,
            {'base': (0, 0), 0: (2, 1)})
        child = tags[1]
        self.assertEqual(w, (2, 2, 2))
        w, particles, tags = coupled_step(w, particles, tags, 2, 3, 1,
                                         {'base': (1, 1), child: (1, 1)})
        self.assertEqual(w, (2, 1, 2))
        self.assertNotIn(child, particles)
        self.assertNotIn(1, tags)

    def test_own_base_birth_waits_until_next_sweep(self):
        w, particles, tags = coupled_step((0, 1, 2), {}, {}, 2, 3, 1,
                                         {'base': (0, 1)})
        self.assertEqual(w, (0, 0, 2))
        self.assertEqual(len(particles), 1)
        self.assertEqual(particles[tags[1]], (1, 0))

    def test_repeated_base_births_have_distinct_live_ids(self):
        w, particles, tags = (0, 1, 2), {}, {}
        for i in (0, 1, 2):
            draws = {'base': ((i+1) % 3, i)}
            draws.update({key: (weight, site) for key, (site, weight) in particles.items()
                          if site == i})
            w, particles, tags = coupled_step(w, particles, tags, 2, 3, i, draws)
        self.assertEqual(len(particles), 3)
        self.assertEqual(len(tags), 3)

    def test_clean_external_repair_erases_tag_not_particle(self):
        w, particles, tags = coupled_step((0, 0, 2), {4: (1, 0)}, {1: 4},
                                         2, 3, 0, {'base': (1, 1)})
        self.assertEqual(w, (0, 1, 2))
        self.assertEqual(tags, {})
        self.assertEqual(particles, {4: (1, 0)})

    def test_renewal_against_finite_markov_chains(self):
        self.assertEqual(check_renewal(), 24)


if __name__ == '__main__':
    unittest.main(verbosity=2)
