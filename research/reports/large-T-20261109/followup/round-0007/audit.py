#!/usr/bin/env python3
"""Exact deterministic audit of the round-6 coefficient and uniform estimates.

No trajectory sampling, PRNG, numerical differentiation, or fitted constants.
An independent polynomial kernel and full-population clean suffix oracle check
exceptional sites. The published literal-mask oracle is extended to n=4.
"""
import argparse
import csv
from fractions import Fraction as F
from functools import lru_cache
import importlib.util
import json
from pathlib import Path
import sys


def load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def kernel(n):
    """Coefficient product of n integer linear polynomials, not binomial sums."""
    rows = []
    for x in range(n + 1):
        poly = [1]
        for bit in range(n):
            a, b = (1, n - 1) if bit < x else (n - 1, 1)
            new = [0] * (len(poly) + 1)
            for j, value in enumerate(poly):
                new[j] += a * value
                new[j + 1] += b * value
            poly = new
        rows.append(tuple(F(value, n ** n) for value in poly))
    return tuple(rows)


def neighbors(n, t, i):
    # Independent closed interval expression; literal enumeration checked below.
    start = max(0, min(n + 1 - t, i - (t - 1) // 2 - int(t % 2 == 0 and i % 2 == 1)))
    return tuple(range(start, start + t))


class Oracle:
    """Clean phase values on full population tuples; no disjoint-clock premise."""
    def __init__(self, n, t):
        self.n, self.t = n, t
        self.d = kernel(n)
        self.target = tuple(range(n + 1))
        self.corner = (2,) + self.target[1:]
        self.b = [neighbors(n, t, i) for i in range(n + 1)]
        self.inc = [tuple(i for i in range(n + 1) if k in self.b[i]) for k in range(n + 1)]
        self.q = self.d[1][0] + self.d[2][0] - self.d[1][0] * self.d[2][0]

    @staticmethod
    def put(w, k, y):
        return w[:k] + (y,) + w[k + 1:]

    @lru_cache(None)
    def clean(self, w, i):
        result = {w: F(1)}
        for k in self.b[i]:
            if w[k] != k:
                p = self.d[w[i]][k]
                result[w] -= p
                v = self.put(w, k, k)
                result[v] = result.get(v, F(0)) + p
        return result

    @lru_cache(None)
    def sweep(self, w, start=0):
        dist = {w: F(1)}
        for i in range(start, self.n + 1):
            nxt = {}
            for u, mass in dist.items():
                for v, p in self.clean(u, i).items():
                    nxt[v] = nxt.get(v, F(0)) + mass * p
            dist = nxt
        return dist

    @lru_cache(None)
    def h(self, w):
        if w == self.target:
            return F(0)
        dist = self.sweep(w)
        return (1 + sum(p * self.h(v) for v, p in dist.items() if v != w)) / (1 - dist[w])

    @lru_cache(None)
    def value(self, w, start):
        return sum(p * self.h(v) for v, p in self.sweep(w, start).items())

    def contribution(self, k):
        total = F(0)
        prefix = {self.corner: F(1)}
        for i in range(self.n + 1):
            if k in self.b[i]:
                for w, prob in prefix.items():
                    base = self.value(w, i + 1)
                    for y, mutation in enumerate(self.d[w[i]]):
                        # Literal active-minus-clean acceptance into this slot.
                        active = self.d[y][k] * (self.value(self.put(w, k, y), i + 1) - base)
                        clean = self.value(self.put(w, k, k), i + 1) - base if y == k else 0
                        total += prob * mutation * (active - clean)
            nxt = {}
            for w, mass in prefix.items():
                for v, p in self.clean(w, i).items():
                    nxt[v] = nxt.get(v, F(0)) + mass * p
            prefix = nxt
        return total / self.q

    @staticmethod
    def clear():
        for name in ('clean', 'sweep', 'h', 'value'):
            getattr(Oracle, name).cache_clear()


def pair_terms(d, q, k, j):
    """Equation (7), preserving the two different ascending suffix orders."""
    a = d[j][k]
    result = {}
    for y in range(len(d)):
        if y == k:
            continue
        dy = d[y][k]
        r = a + (1 - a) * dy
        numerator = d[j][y] + (1 - a) * d[k][y] if j > k else (1 - dy) * d[j][y] + d[k][y]
        result[y] = dy * numerator / (r * (q + (1 - q) * r))
    return result


def edges(ns):
    rows = []
    for n in ns:
        d = kernel(n)
        q = d[1][0] + d[2][0] - d[1][0] * d[2][0]
        assert F(1, 3 * n) <= q <= F(2, n)
        for k in range(2, n):
            # Exclude the extra incoming donor at n-1 when n is even.
            if n % 2 == 0 and k == n - 1:
                continue
            left = k % 2 == 0 and 4 * k <= n
            right = k % 2 == 1 and 4 * k >= 3 * n
            if not (left or right):
                continue
            j = k + 1 if left else k - 1
            u = k + 1 if left else n - k + 1
            a = d[j][k]
            assert F(u, 3 * n) <= a <= F(u, n)
            terms = pair_terms(d, q, k, j)
            lead = terms[j]
            low = sum(v for y, v in terms.items() if y < k) if left else sum(v for y, v in terms.items() if y > k)
            high = sum(v for y, v in terms.items() if y > k + 1) if left else sum(v for y, v in terms.items() if y < k - 1)
            normalized = abs(lead - F(n, 2 * u)) / (1 + F(n, u * u))
            assert normalized <= 64
            assert 0 <= low <= 6
            assert 0 <= high <= 18
            rows.append(dict(n=n, target=k, edge='left' if left else 'right', u=u,
                             leading_term=float(lead), harmonic_term=float(F(n, 2 * u)),
                             normalized_error=float(normalized), normalized_error_bound=64,
                             opposite_errors=float(low), opposite_errors_bound=6,
                             multi_step_errors=float(high), multi_step_errors_bound=18,
                             arithmetic='exact rational; decimal display'))
    return rows


def exceptions(ns):
    rows = []
    maxima = dict(two_error_mean_over_n=F(0), slot2_wrong_prefix_delay_over_q=F(0),
                  slot2_aligned_prefix_delay=F(0), recipient1_injection_times_n=F(0))
    counts = dict(two_error_means=0, slot2_phase_delays=0, injection_masses=0)
    for n in ns:
        for t in (2, 3):
            s = Oracle(n, t)
            for x in (1, 2):
                mass = sum(s.d[x][y] * s.d[y][1] for y in range(n + 1) if y != 1)
                assert mass <= F(5, n)
                maxima['recipient1_injection_times_n'] = max(maxima['recipient1_injection_times_n'], n * mass)
                counts['injection_masses'] += 1
            for y in range(n + 1):
                if y == 1:
                    continue
                for w in (s.corner, s.target):
                    value = s.h(s.put(w, 1, y))
                    assert value <= 5 * n
                    maxima['two_error_mean_over_n'] = max(maxima['two_error_mean_over_n'], value / n)
                    counts['two_error_means'] += 1
            for k, bound in ((0, 36 * n), (1, 225 * n)):
                v = s.contribution(k)
                assert abs(v) <= bound
                rows.append(dict(n=n, T=t, target=k, contribution=float(v), absolute_bound=bound,
                                 ratio_to_bound=float(abs(v) / bound), arithmetic='exact rational; decimal display'))
            if t == 3:
                for y in range(n + 1):
                    if y == 2:
                        continue
                    for i in s.inc[2]:
                        for w in (s.corner, s.target):
                            delta = s.value(s.put(w, 2, y), i + 1) - s.value(w, i + 1)
                            assert delta >= 0
                            key = 'slot2_wrong_prefix_delay_over_q' if w == s.corner else 'slot2_aligned_prefix_delay'
                            scaled = delta / s.q if w == s.corner else delta
                            assert scaled <= (98 if w == s.corner else 7)
                            maxima[key] = max(maxima[key], scaled)
                            counts['slot2_phase_delays'] += 1
                v = s.contribution(2)
                assert 0 <= v <= 420
                rows.append(dict(n=n, T=t, target=2, contribution=float(v), absolute_bound=420,
                                 ratio_to_bound=float(v / 420), arithmetic='exact rational; decimal display'))
            s.clear()
    return rows, dict(counts=counts, maxima={k: float(v) for k, v in maxima.items()},
                      maxima_rational={k: str(v) for k, v in maxima.items()})


def write_csv(path, rows):
    with path.open('w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def main(repo, out):
    if hasattr(sys, 'set_int_max_str_digits'):
        sys.set_int_max_str_digits(0)
    out.mkdir(parents=True, exist_ok=True)
    prior = repo / 'research/reports/large-T-20261109/followup/round-0006'
    old = load(prior / 'coefficient.py', 'prior_coefficient')
    literal = load(prior / 'verify.py', 'prior_literal')
    neighborhood_cases = kernel_entries = 0
    for n in range(3, 66):
        for t in (2, 3):
            for i in range(n + 1):
                assert set(neighbors(n, t, i)) == set(literal.neighbors(n, t, i))
                neighborhood_cases += 1
    for n in range(3, 11):
        d = kernel(n)
        ld, den = literal.literal_kernel(n)
        for x in range(n + 1):
            assert sum(d[x]) == 1
            assert d[x] == tuple(reversed(d[n - x]))
            for y in range(n + 1):
                assert d[x][y] == F(ld[x][y], den)
                kernel_entries += 1
    # Independent full-state phase oracle vs published recipient decomposition.
    saved = list(csv.DictReader((prior / 'components.csv').open()))
    component_matches = 0
    for n in range(3, 11):
        for t in (2, 3):
            s = Oracle(n, t)
            for k in range(n + 1):
                expected = F(next(r['coefficient'] for r in saved if (int(r['n']), int(r['T']), int(r['target'])) == (n, t, k)))
                assert s.contribution(k) == expected
                component_matches += 1
            s.clear()
    # Extend the earlier independent, literal-mask full-state check to n=4.
    full = []
    for t in (2, 3):
        record = literal.full_derivative(4, t)
        s = old.Solver(4, t)
        assert F(record['derivative']) == sum(s.derivative())
        record['matches_two_error_formula_exactly'] = True
        full.append(record)
        old.Solver.clear()
    edge_ns = list(range(8, 33)) + [64, 65]
    exceptional_ns = list(range(8, 25)) + [32, 33]
    edge_rows = edges(edge_ns)
    exception_rows, detail = exceptions(exceptional_ns)
    write_csv(out / 'edges.csv', edge_rows)
    write_csv(out / 'exceptions.csv', exception_rows)
    result = dict(status='mechanically checked', arithmetic='exact integer/Fraction; displayed decimals are rounded',
                  scientific_trajectories=0, scientific_seeds=[],
                  neighborhood_cases=neighborhood_cases, kernel_entries=kernel_entries,
                  exact_recipient_matches=component_matches, full_population_n4=full,
                  full_population_gap=str(F(full[1]['derivative']) - F(full[0]['derivative'])),
                  edge_grid=edge_ns, edge_site_cases=len(edge_rows),
                  edge_maxima={k: max(r[k] for r in edge_rows) for k in ('normalized_error', 'opposite_errors', 'multi_step_errors')},
                  exceptional_grid=exceptional_ns, exceptional_contribution_cases=len(exception_rows),
                  exceptional_details=detail,
                  proof_scope='Finite checks support implementation only; universal bounds are proved in audit.md. No uniform Taylor remainder or all-n>=4 negativity is asserted.')
    (out / 'verification.json').write_text(json.dumps(result, indent=2, sort_keys=True) + '\n')
    print(json.dumps({k: result[k] for k in ('status', 'neighborhood_cases', 'kernel_entries', 'exact_recipient_matches', 'edge_site_cases', 'exceptional_contribution_cases')}, sort_keys=True))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--repo', type=Path, default=Path('.'))
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    main(args.repo.resolve(), args.out.resolve())
