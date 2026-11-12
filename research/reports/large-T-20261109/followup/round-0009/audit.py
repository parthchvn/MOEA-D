#!/usr/bin/env python3
"""Independent rational audit of the even-n orphan; no trajectory sampling.

The transition builder uses literal masks and full population tuples. It does
not import an earlier response solver. All stopping is at sweep boundaries.
"""
import argparse
import csv
from fractions import Fraction as F
from functools import lru_cache
import json
from pathlib import Path
import sys


def mutation(n):
    rows = []
    for x in range(n + 1):
        genotype = (1 << x) - 1
        row = [0] * (n + 1)
        for mask in range(1 << n):
            row[(genotype ^ mask).bit_count()] += (n - 1) ** (n - mask.bit_count())
        rows.append(tuple(F(v, n ** n) for v in row))
    return tuple(rows)


def recipients(n, t, i):
    # Closed interval, independent of the earlier alternating enumeration.
    left = (t - 1) // 2 + int(t % 2 == 0 and i % 2 == 1)
    start = min(max(0, i - left), n + 1 - t)
    return tuple(range(start, start + t))


def change(w, k, y):
    return w[:k] + (y,) + w[k + 1:]


def add(out, key, value):
    out[key] = out.get(key, F(0)) + value


class Chain:
    def __init__(self, n, t=2, omit_orphan_help=False):
        self.n, self.t = n, t
        self.d = mutation(n)
        self.target = tuple(range(n + 1))
        self.corner = change(self.target, 0, 2)
        self.neighbors = tuple(recipients(n, t, i) for i in range(n + 1))
        self.omit_orphan_help = omit_orphan_help

    @lru_cache(None)
    def step(self, w, i, kind='K'):
        """Literal offspring/observation sum; R/O are restricted J minus K."""
        out = {}
        accepted = self.neighbors[i]
        if kind == 'O':
            accepted = tuple(k for k in accepted if k == self.n)
        elif kind == 'R':
            accepted = tuple(k for k in accepted if k != self.n)
        elif kind != 'K':
            raise ValueError(kind)
        if self.omit_orphan_help and i == self.n:
            accepted = tuple(k for k in accepted if k == self.n)
        for y, py in enumerate(self.d[w[i]]):
            if kind == 'K':
                v = change(w, y, y) if y in accepted else w
                add(out, v, py)
            else:
                for z, pz in enumerate(self.d[y]):
                    v = change(w, z, y) if z in accepted else w
                    add(out, v, py * pz)
                v = change(w, y, y) if y in accepted else w
                add(out, v, -py)
        return tuple((v, p) for v, p in out.items() if p)

    @lru_cache(None)
    def sweep(self, w):
        dist = {w: F(1)}
        for i in range(self.n + 1):
            out = {}
            for v, p in dist.items():
                for u, a in self.step(v, i):
                    add(out, u, p * a)
            dist = out
        return tuple(dist.items())

    @lru_cache(None)
    def value(self, w, mode='mean'):
        if mode in ('count', 'residual'):
            if w[self.n] == self.n or w[:self.n] == self.target[:self.n]:
                return F(0)
        elif w == self.target:
            return F(0)
        dist = self.sweep(w)
        escape = sum(p for v, p in dist if v != w)
        if mode == 'mean':
            rhs = F(1)
        elif mode in ('R', 'O'):
            rhs = self.insert(w, 0, (mode,), 'mean')
        elif mode in ('count', 'residual'):
            rhs = self.reward(w, 0, mode)
        else:
            raise ValueError(mode)
        rhs += sum(p * self.value(v, mode) for v, p in dist if v != w)
        return rhs / escape

    @lru_cache(None)
    def suffix(self, w, phase, mode='mean'):
        if phase == self.n + 1:
            return self.value(w, mode)
        return sum(p * self.suffix(v, phase + 1, mode)
                   for v, p in self.step(w, phase))

    @lru_cache(None)
    def insert(self, w, phase, word, terminal='mean'):
        """Sum over strictly increasing attempt positions for an ordered word."""
        if not word:
            return self.suffix(w, phase, terminal)
        if phase == self.n + 1:
            return F(0)
        return (sum(p * self.insert(v, phase + 1, word, terminal)
                    for v, p in self.step(w, phase))
                + sum(p * self.insert(v, phase + 1, word[1:], terminal)
                      for v, p in self.step(w, phase, word[0])))

    @lru_cache(None)
    def reward(self, w, phase, mode):
        """Expected predictable count/residual reward within this suffix."""
        if phase == self.n + 1:
            return F(0)
        reward = F(0)
        if (phase == self.n and w[self.n] != self.n
                and w[:self.n] != self.target[:self.n]):
            if mode == 'count':
                reward = F(1)
            else:
                reward = self.d[w[self.n]][self.n] * self.value(change(w, self.n, self.n))
        return reward + sum(p * self.reward(v, phase + 1, mode)
                            for v, p in self.step(w, phase))

    def total_reward(self, w, phase, mode):
        return self.reward(w, phase, mode) + self.suffix(w, phase, mode)

    def clear(self):
        for f in (Chain.step, Chain.sweep, Chain.value, Chain.suffix,
                  Chain.insert, Chain.reward):
            f.cache_clear()


def qvalue(n, d):
    return 1 - (1 - d[2][0]) * (1 - d[1][0])


def solve(a, b):
    """Exact Gaussian elimination with row pivoting."""
    rows = [list(row) + [v] for row, v in zip(a, b)]
    for k in range(len(rows)):
        pivot = next(j for j in range(k, len(rows)) if rows[j][k])
        rows[k], rows[pivot] = rows[pivot], rows[k]
        scale = rows[k][k]
        rows[k] = [x / scale for x in rows[k]]
        for j in range(len(rows)):
            if j != k and rows[j][k]:
                scale = rows[j][k]
                rows[j] = [x - scale * y for x, y in zip(rows[j], rows[k])]
    return [row[-1] for row in rows]


def local(n, d):
    """Local kernel R0+p R1, built from mutation and observation, no formula (12)."""
    r0, r1 = [], []
    for x in range(n + 1):
        clean, active = [F(0)] * (n + 1), [F(0)] * (n + 1)
        for y in range(n + 1):
            clean[n if y == n else x] += d[x][y]
            active[y] += d[x][y] * d[y][n]
            active[x] += d[x][y] * (1 - d[y][n])
        r0.append(clean)
        r1.append([a - c for a, c in zip(active, clean)])
    return r0, r1


def orphan_series(n, d):
    q = qvalue(n, d)
    s = 1 - q
    r0, r1 = local(n, d)
    a = [[F(i == j) - s * r0[i][j] for j in range(n + 1)] for i in range(n + 1)]
    vectors = [solve(a, [F(i == n) for i in range(n + 1)])]
    for _ in range(2):
        vectors.append(solve(a, [s * sum(r1[i][j] * vectors[-1][j] for j in range(n + 1))
                                 for i in range(n + 1)]))
    b = 1 - d[n][n]
    return vectors[0][n], vectors[1][n] + b * vectors[0][n], (
        vectors[2][n] + b * vectors[1][n] + b * b * vectors[0][n])


def orphan_finite(n, d, p):
    """Check discounted identity against the independent joint absorbing chain."""
    q = qvalue(n, d)
    r0, r1 = local(n, d)
    r = [[c + p * a for c, a in zip(cr, ar)] for cr, ar in zip(r0, r1)]
    a = [[F(i == j) - (1 - q) * r[i][j] for j in range(n + 1)] for i in range(n + 1)]
    nu = 1 - p + p * d[n][n]
    formula = solve(a, [F(i == n) for i in range(n + 1)])[n] / nu
    states = [(done, y) for done in (0, 1) for y in range(n + 1) if (done, y) != (1, n)]
    pos = {w: i for i, w in enumerate(states)}
    joint = [[F(i == j) for j in range(len(states))] for i in range(len(states))]
    for ix, (done, x) in enumerate(states):
        for flag, weight in ((1, F(1)),) if done else ((0, 1 - q), (1, q)):
            for y in range(n + 1):
                if (flag, y) in pos:
                    joint[ix][pos[(flag, y)]] -= weight * r[x][y]
    direct = solve(joint, [F(1)] * len(states))[pos[(0, n)]]
    assert formula == direct
    return direct


def table(path, rows):
    with path.open('w', newline='') as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def audit(repo, out, ns=(4, 6, 8), mixed_ns=(4, 6)):
    out.mkdir(parents=True, exist_ok=True)
    counts = dict(suffix_envelopes=0, suffix_differences=0, predictable_identities=0,
                  regular_without_help=0, mixed_forcings=0, mixed_responses=0,
                  local_balance=0)
    suffix_rows, mixed_rows, local_rows = [], [], []
    # All assertions are exact rational inequalities, not tolerance checks.
    for n in ns:
        chain = Chain(n)
        ell, jbound = 6 * n, 6 * n * (6 * n + 1)
        maxima = [F(0)] * (n + 2)
        envelope_max, count_max, witness = F(0), F(0), None
        for y in range(n):
            d = chain.d[y][n]
            alone = change(chain.target, n, y)
            for base in (chain.target, chain.corner):
                w = change(base, n, y)
                for k in range(n):
                    for z in range(n + 1):
                        v = change(w, k, z)
                        for phase in range(n + 2):
                            original = chain.suffix(w, phase)
                            modified = chain.suffix(v, phase)
                            lag = modified - chain.suffix(alone, phase)
                            num = chain.total_reward(v, phase, 'count')
                            residual = chain.total_reward(v, phase, 'residual')
                            assert residual == lag
                            assert 0 <= lag <= ell * d * num
                            assert num <= ell + 1
                            assert lag <= d * jbound
                            diff = abs(modified - original)
                            assert diff <= d * jbound
                            ratio = diff / (d * jbound)
                            if ratio > maxima[phase]:
                                maxima[phase] = ratio
                            if lag / (d * jbound) > envelope_max:
                                envelope_max = lag / (d * jbound)
                                witness = (y, base == chain.corner, k, z, phase)
                            count_max = max(count_max, num / (ell + 1))
                            counts['suffix_envelopes'] += 1
                            counts['suffix_differences'] += 1
                            counts['predictable_identities'] += 1
                for i in range(n + 1):
                    force = sum(a * chain.suffix(v, i + 1) for v, a in chain.step(w, i, 'R'))
                    assert abs(force) <= 4 * d * jbound
                    counts['mixed_forcings'] += 1
        for phase, ratio in enumerate(maxima):
            suffix_rows.append(dict(n=n, phase=phase, maximum_difference_ratio=str(ratio),
                                    difference_ratio_decimal=float(ratio),
                                    maximum_envelope_ratio=str(envelope_max),
                                    maximum_count_ratio=str(count_max), witness=str(witness)))
        chain.clear()
        shadow = Chain(n, omit_orphan_help=True)
        for base in (shadow.target, shadow.corner):
            for k in range(n):
                for z in range(n + 1):
                    w = change(base, k, z)
                    assert shadow.value(w) <= ell
                    counts['regular_without_help'] += 1
        shadow.clear()
        print(json.dumps(dict(stage='suffix', n=n, counts=counts)), flush=True)

    # Both temporal mixed orders are computed separately, not by subtraction.
    prior = repo / 'research/reports/large-T-20261109/followup/round-0008'
    published = list(csv.DictReader((prior / 'coefficients.csv').open()))
    for n in mixed_ns:
        chain = Chain(n)
        q, ell, m = qvalue(n, chain.d), 6 * n, n + 1
        jbound = ell * (ell + 1)
        kprime = 4 * m * jbound + ell * m * (ell + 2)
        hmax = F(0)
        for y in range(n):
            for base in (chain.target, chain.corner):
                value = chain.value(change(base, n, y), 'R')
                assert abs(value) <= kprime
                hmax = max(hmax, abs(value) / kprime)
                counts['mixed_responses'] += 1
        values = {
            'R_then_O_between': chain.insert(chain.corner, 0, ('R',), 'O') / q,
            'O_then_R_between': chain.insert(chain.corner, 0, ('O',), 'R') / q,
            'R_then_O_within': chain.insert(chain.corner, 0, ('R', 'O')) / q,
            'O_then_R_within': chain.insert(chain.corner, 0, ('O', 'R')) / q,
            'OO': chain.insert(chain.corner, 0, ('O',), 'O') / q,
        }
        assert values['O_then_R_within'] == 0
        assert abs(values['R_then_O_between']) <= 2 * m * jbound / q
        assert abs(values['O_then_R_between']) <= 2 * kprime / q
        assert abs(values['R_then_O_within']) <= 2 * m * (ell + 1) / q
        mixed = sum(v for k, v in values.items() if k != 'OO')
        bound = F(m * (12 * ell * ell + 16 * ell + 2), 1) / q
        assert abs(mixed) <= bound
        assert values['OO'] == orphan_series(n, chain.d)[2]
        if n == 4:
            rr = (chain.insert(chain.corner, 0, ('R',), 'R')
                  + chain.insert(chain.corner, 0, ('R', 'R'))) / q
            pub = next(r for r in published if r['n'] == str(n) and r['T'] == '2')
            assert rr + values['OO'] + mixed == F(pub['second'])
            values['RR'] = rr
        for name, value in values.items():
            mixed_rows.append(dict(n=n, component=name, exact=str(value), decimal=float(value),
                                   mixed_sum=str(mixed), mixed_bound=str(bound),
                                   maximum_response_ratio=str(hmax)))
        chain.clear()
        print(json.dumps(dict(stage='mixed', n=n, mixed_decimal=float(mixed))), flush=True)

    for n in (4, 6, 8, 10, 12):
        d = mutation(n)
        q = qvalue(n, d)
        series = orphan_series(n, d)
        assert series[0] == 1 / q
        assert abs(series[2]) <= 6 / q ** 2
        p = F(1, 64 * n)
        finite = orphan_finite(n, d, p)
        r0, r1 = local(n, d)
        nu = [p * d[n][x] + (1 - p) * (x == n) for x in range(n + 1)]
        for x in range(n + 1):
            for y in range(n + 1):
                assert nu[x] * (r0[x][y] + p * r1[x][y]) == nu[y] * (r0[y][x] + p * r1[y][x])
                counts['local_balance'] += 1
        local_rows.append(dict(n=n, first=str(series[1]), second=str(series[2]),
                               second_decimal=float(series[2]), bound=str(6 / q ** 2),
                               p=str(p), finite_mean=str(finite), finite_mean_decimal=float(finite)))
    # Hash-free comparison: parse the prior rational values themselves.
    old = json.loads((prior / 'verification.json').read_text())
    for row in local_rows:
        prev = next(r for r in old['orphan_checks'] if r['n'] == row['n'])
        assert F(prev['first']) == F(row['first'])
        assert F(prev['second']) == F(row['second'])
    for filename, rows in (('suffix.csv', suffix_rows), ('mixed.csv', mixed_rows), ('local.csv', local_rows)):
        table(out / filename, rows)
    result = dict(status='mechanically checked', counts=counts, suffix_n=list(ns),
                  mixed_n=list(mixed_ns), arithmetic='exact rational', scientific_trajectories=0,
                  scientific_seeds=[], prior_full_second_matches=1, prior_local_matches=10,
                  limitations='Finite checks support the analytic audit; no statistical experiment or higher-order remainder claim.')
    (out / 'verification.json').write_text(json.dumps(result, indent=2, sort_keys=True) + '\n')


if __name__ == '__main__':
    if hasattr(sys, 'set_int_max_str_digits'):
        sys.set_int_max_str_digits(0)
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--repo', type=Path, default=Path('.'))
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    audit(args.repo.resolve(), args.out)
