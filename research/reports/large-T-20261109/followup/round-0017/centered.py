#!/usr/bin/env python3
"""Exact regular-state centering for the ordered ORRR response.

This implementation solves centered Poisson equations, killed when regular
slots are correct. The boundary compensation is essential. No sampling/RNG.
Independent published sweep/phase implementations are used only by checks.
"""
import argparse
import csv
from fractions import Fraction as F
from functools import lru_cache
import hashlib
import importlib.util
import json
from math import comb
from pathlib import Path
import sys

if hasattr(sys, 'set_int_max_str_digits'):
    sys.set_int_max_str_digits(0)
ZERO = F(0)


def mutation(n):
    # Enumerate lost ones and gained zeros with an integer denominator.
    return tuple(tuple(F(sum(comb(x, a)*comb(n-x, b)*(n-1)**(n-a-b)
                             for a in range(x+1) for b in range(n-x+1)
                             if x-a+b == z), n**n)
                       for z in range(n+1)) for x in range(n+1))


def change(s, k, x):
    return s[:k]+(x,)+s[k+1:]


def digest(x):
    return hashlib.sha256(str(x).encode()).hexdigest()


def load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class Centered:
    def __init__(self, n):
        if n < 4 or n % 2:
            raise ValueError('Even n >= 4, filled T=2 only')
        self.n, self.m, self.L = n, n+1, 20*n
        self.d = mutation(n)
        self.target = tuple(range(n+1))
        self.corner = change(self.target, 0, 2)
        self.neighbors = tuple((i, i-1 if i % 2 or i == n else i+1)
                               for i in range(n+1))

    def baseline(self, y):
        return change(self.target, self.n, y)

    @lru_cache(None)
    def clean(self, s, i):
        row = {}
        for z, p in enumerate(self.d[s[i]]):
            end = change(s, z, z) if z in self.neighbors[i] else s
            row[end] = row.get(end, ZERO)+p
        return tuple(row.items())

    @lru_cache(None)
    def signed(self, s, i, letter='R'):
        if letter not in ('R', 'O'):
            raise ValueError(letter)
        row = {}
        for k in self.neighbors[i]:
            if (k == self.n) != (letter == 'O'):
                continue
            for z, p in enumerate(self.d[s[i]]):
                end = change(s, k, z)
                weight = p*(self.d[z][k]-F(z == k))
                row[end] = row.get(end, ZERO)+weight
                row[s] = row.get(s, ZERO)-weight
        return tuple((s, p) for s, p in row.items() if p)

    @lru_cache(None)
    def forcing(self, s, i, degree):
        if degree < 1:
            raise ValueError(degree)
        nxt = (i+1) % self.m
        return sum((p*self.excess(v, degree-1)[nxt]
                    for v, p in self.signed(s, i)), ZERO)

    @lru_cache(None)
    def flux(self, degree):
        if not degree:
            return F(1)
        return sum((self.forcing(self.target, i, degree)
                    for i in range(self.m)), ZERO)

    @lru_cache(None)
    def excess(self, s, degree):
        """H_degree(s,i)-H_degree(all-regular-correct,s[-1],i)."""
        if s[:-1] == self.target[:-1]:
            return (ZERO,)*self.m
        alpha, beta = F(1), ZERO
        affine = [None]*self.m
        for i in range(self.n, -1, -1):
            nxt = (i+1) % self.m
            rhs = self.flux(degree)*F(i == 0 and s[-1] == self.n)
            if degree:
                rhs += (self.forcing(s, i, degree)
                        -self.forcing(self.baseline(s[-1]), i, degree))
            stay = ZERO
            for v, p in self.clean(s, i):
                if v == s:
                    stay += p
                else:
                    rhs += p*self.excess(v, degree)[nxt]
            alpha, beta = stay*alpha, stay*beta+rhs
            affine[i] = (alpha, beta)
        boundary = beta/(1-alpha)
        return tuple(a*boundary+b for a, b in affine)

    @lru_cache(None)
    def response(self, s, degree):
        """Full killed clean occupation of R H_(degree-1), all phases."""
        alpha, beta = F(1), ZERO
        affine = [None]*self.m
        for i in range(self.n, -1, -1):
            nxt = (i+1) % self.m
            rhs = self.forcing(s, i, degree)
            stay = ZERO
            for v, p in self.clean(s, i):
                if v == s:
                    stay += p
                else:
                    rhs += p*self.response(v, degree)[nxt]
            alpha, beta = stay*alpha, stay*beta+rhs
            affine[i] = (alpha, beta)
        boundary = ZERO if s == self.target else beta/(1-alpha)
        result = tuple(a*boundary+b for a, b in affine)
        return (boundary,)+result[1:]

    def orrr(self):
        # Before the first O, only the corner error can survive. At phase n
        # its survival probability in the current sweep is exactly 1-q.
        q = 1-(1-self.d[2][0])*(1-self.d[1][0])
        value = ZERO
        for s, weight in ((self.corner, 1-q), (self.target, q)):
            value += weight*sum((p*self.response(v, 3)[0]
                                 for v, p in self.signed(s, self.n, 'O')), ZERO)/q
        return value

    def clean_cap(self, s):
        bad = [k for k in range(0, self.n, 2)
               if s[k] != k and s[k+1] != k+1
               and not (k == 0 and s[0] == 2)]
        if len(bad) > 1:
            raise ValueError('Outside the two-birth family')
        if not bad:
            return F(self.L)
        k = bad[0]
        return self.L+2/(self.d[s[k]][k]+self.d[s[k+1]][k+1])

    def clear(self):
        for name in ('clean', 'signed', 'forcing', 'flux', 'excess', 'response'):
            getattr(self, name).cache_clear()


def write(path, rows):
    with path.open('w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def check(repo, out, ns=(4, 6)):
    out.mkdir(parents=True, exist_ok=True)
    prior = repo/'research/reports/large-T-20261109/followup'
    sweep_module = load(prior/'round-0016/audit.py', 'round16_sweep')
    phase_module = load(prior/'round-0014/audit.py', 'round14_phase')
    centered_rows, word_rows, flux_rows, entrance_rows = [], [], [], []
    identities = inequalities = 0
    for n in ns:
        c = Centered(n)
        phase = phase_module.Phase(n)
        L, m = c.L, c.m
        # All marked values and orphan weights, at n=4; endpoint stress at n=6.
        values = range(n+1) if n == 4 else (0, 1, n-1, n)
        states = {}
        for base in (c.target, c.corner):
            for y in values:
                states[(change(base, n, y), 0)] = F(1)
                for k in range(n):
                    for x in values:
                        if x != k:
                            states[(change(change(base, k, x), n, y), 1)] = c.d[x][k]
        for (s, marked), a in sorted(states.items()):
            cap2 = 64*m*m*L*(L*L+1/a) if marked else 64*m*m*L**3
            maxima = [ZERO]*3
            base = c.baseline(s[-1])
            for j in range(3):
                centered = c.excess(s, j)
                # The n=4 independent check covers every tested degree/phase.
                if n == 4:
                    raw, ref = phase.values(s, 'R'*j), phase.values(base, 'R'*j)
                    assert centered == tuple(x-y for x, y in zip(raw, ref))
                    identities += m
                cap = (L, 5*m*L*L, cap2)[j]
                assert max(map(abs, centered)) <= cap
                maxima[j] = max(map(abs, centered))/cap
                inequalities += m
            centered_rows.append(dict(n=n, state=' '.join(map(str, s)), marked=marked,
                                      acceptance=str(a), phase_count=m,
                                      degree0_ratio=float(maxima[0]),
                                      degree1_ratio=float(maxima[1]),
                                      degree2_ratio=float(maxima[2]),
                                      centered_sha256=digest(tuple(c.excess(s, 2)))))
        # Double errors test the new first-response bound, including wrong orphans.
        for k in range(0, n, 2):
            for x in values:
                for z in values:
                    if x == k or z == k+1:
                        continue
                    for y in values:
                        s = change(change(change(c.corner, k, x), k+1, z), n, y)
                        M = c.clean_cap(s)
                        e1 = c.excess(s, 1)
                        assert max(map(abs, e1)) <= 5*m*M*M
                        inequalities += m
                        if n == 4:
                            raw = phase.values(s, 'R')
                            ref = phase.values(c.baseline(y), 'R')
                            assert e1 == tuple(x-y for x, y in zip(raw, ref))
                            identities += m
                        centered_rows.append(dict(n=n, state=' '.join(map(str, s)), marked=2,
                                                  acceptance='', phase_count=m,
                                                  degree0_ratio='', degree1_ratio=float(max(map(abs, e1))/(5*m*M*M)),
                                                  degree2_ratio='', centered_sha256=digest(e1)))
        for j in (1, 2):
            cap = m*L if j == 1 else 10*m*m*L*L
            flux = c.flux(j)
            assert abs(flux) <= cap
            inequalities += 1
            flux_rows.append(dict(n=n, degree=j, boundary_compensation=str(flux),
                                  value_decimal=float(flux), bound=cap))
        B = 512*m*m*L**3
        for s0 in (c.corner, c.target):
            for y in range(n+1):
                s = change(s0, n, y)
                assert max(abs(c.forcing(s, i, 3)) for i in range(m)) <= B
                inequalities += m
                H = c.response(s, 3)[0]
                d = c.d[y][n]
                cap = B*m*(L+(1/d if y != n else 0))
                assert abs(H) <= cap
                inequalities += 1
                entrance_rows.append(dict(n=n, corner_survives=int(s0 == c.corner), orphan=y,
                                          repair=str(d), entrance=str(c.d[n][y]*d if y != n else 0),
                                          response_decimal=float(H), response_sha256=digest(H),
                                          acceptance_weighted_decimal=float(d*H),
                                          bound_ratio=float(abs(H)/cap)))
        value = c.orrr()
        q = 1-(1-c.d[2][0])*(1-c.d[1][0])
        bound = 2048*m**3*L**4/q
        assert abs(value) <= bound
        inequalities += 1
        if n == 4:
            sweep = sweep_module.Sweep(n)
            assert value == sweep.value(sweep.corner, 'ORRR')
            assert value == phase.values(phase.corner, 'ORRR')[0]
            ref = next(r for r in csv.DictReader((prior/'round-0015/words.csv').open()) if r['word'] == 'ORRR')
            assert digest(value) == ref['coefficient_sha256']
            identities += 3
            sweep.clear()
        word_rows.append(dict(n=n, word='ORRR', value_decimal=float(value), rational_sha256=digest(value),
                              independent_oracles=2 if n == 4 else 0,
                              bound_decimal=float(bound), bound_ratio=float(abs(value)/bound)))
        print(json.dumps(dict(n=n, stage='complete', orrr=float(value), rows=len(centered_rows))), flush=True)
        c.clear()
        phase.clear()
    for name, rows in [('centered.csv', centered_rows), ('words.csv', word_rows),
                       ('flux.csv', flux_rows), ('entrance.csv', entrance_rows)]:
        write(out/name, rows)
    result = dict(status='mechanically checked', exact_identities=identities,
                  exact_inequalities=inequalities, centered_rows=len(centered_rows),
                  phase_rows=sum(r['phase_count'] for r in centered_rows), ns=list(ns),
                  arithmetic='exact rational; decimals display only',
                  scientific_trajectories=0, scientific_seeds=[],
                  all_n_bound='candidate proof; independent analytic audit still required',
                  scope='All marked/orphan values at n=4; endpoint stress values at n=6; two independent ORRR oracles at n=4 only.')
    (out/'verification.json').write_text(json.dumps(result, indent=2, sort_keys=True)+'\n')
    print(json.dumps(result), flush=True)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--repo', type=Path, default=Path('.'))
    parser.add_argument('--out', type=Path, required=True)
    parser.add_argument('--ns', type=int, nargs='+', default=[4, 6])
    args = parser.parse_args()
    check(args.repo.resolve(), args.out, args.ns)
