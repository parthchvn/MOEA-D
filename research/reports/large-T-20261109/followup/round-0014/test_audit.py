#!/usr/bin/env python3
"""Independent deterministic tests of the audit semantics."""
import csv
from fractions import Fraction as F
from itertools import product
from pathlib import Path
import unittest
import audit


def literal(n, t, state, breeder, active):
    """Full genotype-mask enumeration and max-Chebyshev comparisons."""
    hood = [breeder]
    for distance in range(1, n+1):
        for sign in ((1, -1) if breeder % 2 == 0 else (-1, 1)):
            k = breeder+sign*distance
            if 0 <= k <= n and len(hood) < t:
                hood.append(k)
    parent = (1 << state[breeder])-1
    row = {}
    for mut in range(1 << n):
        child = parent ^ mut
        true = child.bit_count()
        pm = F((n-1)**(n-mut.bit_count()), n**n)
        for mask in (range(1 << n) if active else (0,)):
            seen = (child ^ mask).bit_count()
            pn = F((n-1)**(n-mask.bit_count()), n**n) if active else F(1)
            v = list(state)
            for k in hood:
                proposed = max(k*(n-seen), (n-k)*seen)
                incumbent = max(k*(n-k), (n-k)*k)
                if proposed <= incumbent:
                    v[k] = true
            v = tuple(v)
            row[v] = row.get(v, F(0))+pm*pn
    return row


class Tests(unittest.TestCase):
    def tearDown(self):
        audit.Phase.values.cache_clear()
        audit.Phase.clean.cache_clear()
        audit.Phase.delta.cache_clear()

    def test_mutation_masks(self):
        for n in range(3, 7):
            d = audit.mutation(n)
            for x in range(n+1):
                row = [F(0)]*(n+1)
                for mask in range(1 << n):
                    row[(((1 << x)-1)^mask).bit_count()] += F((n-1)**(n-mask.bit_count()), n**n)
                self.assertEqual(tuple(row), d[x])

    def test_neighborhood_orientation(self):
        self.assertEqual(audit.recipients(4, 2, 4), (4, 3))
        self.assertEqual(audit.recipients(5, 2, 4), (4, 5))
        self.assertEqual(audit.recipients(4, 3, 0), (0, 1, 2))

    def test_literal_transition_rows(self):
        for n in (3, 4):
            for t in (2, 3):
                s = audit.Phase(n, t)
                for state in (s.target, s.corner, (0,)*s.m, tuple(reversed(s.target))):
                    for i in range(s.m):
                        clean = dict(s.clean(state, i))
                        self.assertEqual(clean, literal(n, t, state, i, False))
                        combined = dict(clean)
                        for v, p in s.delta(state, i, 'D'):
                            combined[v] = combined.get(v, F(0))+p
                        self.assertEqual({v:p for v,p in combined.items() if p},
                                         literal(n, t, state, i, True))

    def test_split_zero_sum(self):
        s = audit.Phase(4)
        for state in (s.corner, (2, 1, 0, 0, 0)):
            for i in range(s.m):
                total = {}
                for letter in 'RO':
                    row = s.delta(state, i, letter)
                    self.assertEqual(sum(p for _,p in row), 0)
                    for v,p in row:
                        total[v] = total.get(v, F(0))+p
                self.assertEqual({v:p for v,p in total.items() if p}, dict(s.delta(state, i, 'D')))

    def test_boundary_only_killing(self):
        s = audit.Phase(4)
        self.assertEqual(s.values(s.target)[0], 0)
        for i in range(1, s.m):
            self.assertEqual(s.values(s.target)[i], F(s.m-i, s.m))
        self.assertGreater(s.values(s.target, 'O')[1], 0)
        self.assertEqual(s.values(s.target, 'O')[0], 0)

    def test_phase_poisson_equations(self):
        s = audit.Phase(4)
        state = (2, 1, 0, 0, 0)
        for word in ('', 'R', 'O', 'OO', 'RO', 'OR'):
            values = s.values(state, word)
            for i in range(s.m):
                j = (i+1)%s.m
                rhs = sum(p*s.values(v, word)[j] for v,p in s.clean(state, i))
                if word:
                    rhs += sum(p*s.values(v, word[1:])[j] for v,p in s.delta(state, i, word[0]))
                else:
                    rhs += F(1, s.m)
                self.assertEqual(values[i], rhs)

    def test_unshifted_boundary_subtraction_fails(self):
        s = audit.Phase(4)
        orphan = audit.replace(s.target, 4, 0)
        local, _ = s.local()
        self.assertEqual(s.values(orphan)[1]-local[0][0], F(-1, 5))
        self.assertEqual(s.values(orphan)[1], F(1279, 5))

    def test_local_correct_phase_coefficients(self):
        s = audit.Phase(4)
        b = 1-s.d[4][4]
        for i in range(1, s.m):
            for j in (1, 2):
                self.assertEqual(s.values(s.target, 'O'*j)[i], b**j)

    def test_excess_identity_with_bad_pair(self):
        s = audit.Phase(4)
        state = (2, 1, 0, 0, 0)
        local, _ = s.local()
        b = 1-s.d[4][4]
        for j in range(3):
            expected = sum(b**(j-r)*s.values(state, 'O'*r, 'occupation')[0] for r in range(j+1))
            self.assertEqual(s.values(state, 'O'*j)[0]-local[j][0], expected)

    def test_first_two_orphan_insertions_need_distinct_turns(self):
        s = audit.Phase(4)
        for i in range(4):
            self.assertEqual(s.delta(s.corner, i, 'O'), ())

    def test_extremely_small_acceptances(self):
        L = F(80)
        for a,b in product((F(1), F(1, 10**80)), repeat=2):
            M = L+2/(a+b)
            self.assertLessEqual(a*b*M*M, (L+1)**2)
            self.assertLessEqual(b*M*M, 2*L*L+2/a)

    def test_n3_published_cubic(self):
        repo = Path(__file__).resolve().parent
        while not (repo/'research/PROJECT.md').exists():
            if repo == repo.parent:
                self.fail('Cannot locate repository')
            repo = repo.parent
        prior = repo/'research/reports/large-T-20261109/followup/round-0013/coefficients.csv'
        with prior.open() as file:
            rows = list(csv.DictReader(file))
        values = []
        for t in (2,3):
            s = audit.Phase(3,t)
            value = s.values(s.corner, 'DDD')[0]
            row = next(r for r in rows if r['n'] == '3' and r['T'] == str(t))
            self.assertEqual(audit.digest(value), row['cubic_sha256'])
            values.append(value)
            s.clear()
        self.assertLessEqual(abs(values[1]-values[0]), 10**10*3**7)


if __name__ == '__main__':
    unittest.main(verbosity=2)
