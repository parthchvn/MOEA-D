#!/usr/bin/env python3
"""Exact small-noise response through order two, without trajectory sampling.

Errors are (slot, true weight) pairs. Clean steps only remove errors. Signed
active-minus-clean steps are composed without killing aligned intermediate
states. The boundary Poisson equations are solved in subset order.
"""
import argparse
import csv
from fractions import Fraction
from functools import lru_cache
import json
from math import comb
from pathlib import Path
import sys
import time


def kernel(n, exact=True):
    den = n ** n
    return tuple(tuple((Fraction(v, den) if exact else v / den)
                       for v in (sum(comb(x, a) * comb(n-x, y-x+a)
                                     * (n-1) ** (n-2*a-y+x)
                                     for a in range(max(0, x-y), min(x, n-y)+1))
                                 for y in range(n+1)))
                 for x in range(n+1))


def neighbors(n, t, i):
    answer = [i]
    for d in range(1, n+1):
        for sign in ((1, -1) if i % 2 == 0 else (-1, 1)):
            j = i + sign*d
            if 0 <= j <= n:
                answer.append(j)
            if len(answer) == t:
                return tuple(answer)
    raise ValueError('Invalid cardinality')


class Response:
    def __init__(self, n, t, exact=True):
        if n < 3 or t not in (2, 3):
            raise ValueError('Requires n>=3, T=2 or 3')
        self.n, self.t, self.exact = n, t, exact
        self.d = kernel(n, exact)
        self.b = tuple(neighbors(n, t, i) for i in range(n+1))
        self.one = Fraction(1) if exact else 1.0
        self.zero = self.one * 0
        self.corner = ((0, 2),)
        self.counts = {'maximum_clean_errors': 0, 'maximum_first_errors': 0}

    @staticmethod
    def put(e, k, y):
        out = dict(e)
        if k == y:
            out.pop(k, None)
        else:
            out[k] = y
        return tuple(sorted(out.items()))

    @lru_cache(None)
    def clean(self, e, i):
        x = dict(e).get(i, i)
        result = {e: self.one}
        for k, _ in e:
            if k in self.b[i]:
                v = self.put(e, k, k)
                p = self.d[x][k]
                result[e] -= p
                result[v] = result.get(v, self.zero) + p
        return tuple((v, p) for v, p in result.items() if p)

    @lru_cache(None)
    def delta(self, e, i):
        """K_active-K_clean, using updates relative to the unchanged state."""
        x = dict(e).get(i, i)
        result = {e: self.zero}
        for k in self.b[i]:
            for y in range(self.n+1):
                p = self.d[x][y] * (self.d[y][k] - (1 if y == k else 0))
                v = self.put(e, k, y)
                if v != e and p:
                    result[v] = result.get(v, self.zero) + p
                    result[e] -= p
        return tuple((v, p) for v, p in result.items() if p)

    def delta_targets(self, e, i, targets):
        """Recipient-restricted signed operator, for bound verification."""
        x = dict(e).get(i, i)
        result = {e: self.zero}
        for k in self.b[i]:
            if k not in targets:
                continue
            for y in range(self.n+1):
                p = self.d[x][y] * (self.d[y][k] - (1 if y == k else 0))
                v = self.put(e, k, y)
                if v != e and p:
                    result[v] = result.get(v, self.zero) + p
                    result[e] -= p
        return tuple((v, p) for v, p in result.items() if p)

    @lru_cache(None)
    def sweep(self, e):
        dist = {e: self.one}
        for i in range(self.n+1):
            out = {}
            for u, p in dist.items():
                for v, a in self.clean(u, i):
                    out[v] = out.get(v, self.zero) + p*a
            dist = out
        return tuple(dist.items())

    @lru_cache(None)
    def h(self, e, order=0):
        if not e:
            return self.zero
        if order > 2:
            raise ValueError('This implementation is bounded to order two')
        if order == 0:
            self.counts['maximum_clean_errors'] = max(self.counts['maximum_clean_errors'], len(e))
        elif order == 1:
            self.counts['maximum_first_errors'] = max(self.counts['maximum_first_errors'], len(e))
        dist = self.sweep(e)
        # Sum non-self transitions rather than subtract near-one numbers.
        escape = sum(p for v, p in dist if v != e)
        rhs = self.one if order == 0 else self.zero
        for r in range(1, order+1):
            rhs += self.apply(e, 0, r, order-r)
        rhs += sum(p*self.h(v, order) for v, p in dist if v != e)
        return rhs/escape

    @lru_cache(None)
    def apply(self, e, i, insertions, value_order):
        """Coefficient of z^insertions in product(K0+z*Delta) h_value_order."""
        if insertions < 0 or insertions > self.n+1-i:
            return self.zero
        if i == self.n+1:
            return self.h(e, value_order) if insertions == 0 else self.zero
        out = sum(p*self.apply(v, i+1, insertions, value_order)
                  for v, p in self.clean(e, i))
        if insertions:
            out += sum(p*self.apply(v, i+1, insertions-1, value_order)
                       for v, p in self.delta(e, i))
        return out

    def coefficients(self):
        h0 = self.h(self.corner)
        h1 = self.h(self.corner, 1)
        # Separate the distinct-sweep and same-sweep signed insertions.
        between = h0 * self.apply(self.corner, 0, 1, 1)
        within = h0 * self.apply(self.corner, 0, 2, 0)
        h2 = between + within
        return dict(n=self.n, T=self.t,
                    arithmetic='rational' if self.exact else 'float64',
                    mean0=str(h0) if self.exact else '',
                    first=str(h1) if self.exact else '',
                    second=str(h2) if self.exact else '',
                    between=str(between) if self.exact else '',
                    within=str(within) if self.exact else '',
                    mean0_decimal=float(h0), first_decimal=float(h1),
                    second_decimal=float(h2), between_decimal=float(between),
                    within_decimal=float(within), **self.counts)

    @staticmethod
    def clear():
        for f in (Response.clean, Response.delta, Response.sweep, Response.h, Response.apply):
            f.cache_clear()


def main(out, ns, exact):
    out.mkdir(parents=True, exist_ok=True)
    rows, gaps = [], []
    for n in ns:
        arms = []
        for t in (2, 3):
            started = time.monotonic()
            solver = Response(n, t, exact)
            r = solver.coefficients()
            rows.append(r)
            arms.append(r)
            solver.clear()
            print(json.dumps({'completed_n': n, 'T': t, 'elapsed_seconds': time.monotonic()-started}), flush=True)
        a, b = arms
        gap = {key: Fraction(b[key])-Fraction(a[key]) for key in ('first', 'second', 'between', 'within')} if exact else {}
        gaps.append(dict(n=n, arithmetic=a['arithmetic'],
                         **{key: str(value) for key, value in gap.items()},
                         **{key+'_decimal': float(gap[key]) if exact else b[key+'_decimal']-a[key+'_decimal']
                            for key in ('first', 'second', 'between', 'within')}))
    for name, table in (('coefficients.csv', rows), ('gaps.csv', gaps)):
        with (out/name).open('w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=list(table[0]))
            writer.writeheader()
            writer.writerows(table)
    print(json.dumps({'status': 'pass', 'n': ns, 'arithmetic': rows[0]['arithmetic'],
                      'scientific_trajectories': 0}, sort_keys=True))


if __name__ == '__main__':
    if hasattr(sys, 'set_int_max_str_digits'):
        sys.set_int_max_str_digits(0)
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--out', type=Path, required=True)
    p.add_argument('--n', type=int, nargs='+', default=[3, 4])
    p.add_argument('--float', action='store_true')
    args = p.parse_args()
    main(args.out, args.n, not args.float)
