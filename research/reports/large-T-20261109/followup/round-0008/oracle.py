#!/usr/bin/env python3
"""Independent literal-mask, full-population rational second-order oracle.

This module never imports second.py. It evaluates every population, uses the
literal scalar comparisons, and solves clean boundary Poisson equations in
the order of the number of wrong slots. No noisy trajectories are generated.
"""
import argparse
from fractions import Fraction as F
from functools import lru_cache
from itertools import product
import json
from pathlib import Path
import sys
import time


def neighbors(n, t, i):
    result = [i]
    distance = 1
    while len(result) < t:
        sides = [i+distance, i-distance] if i % 2 == 0 else [i-distance, i+distance]
        result.extend(k for k in sides if 0 <= k <= n)
        distance += 1
    return result[:t]


def masks(n):
    d = []
    for x in range(n+1):
        bits = [1]*x + [0]*(n-x)
        row = [0]*(n+1)
        for mask in product((0, 1), repeat=n):
            row[sum(b ^ m for b, m in zip(bits, mask))] += (n-1)**(n-sum(mask))
        d.append(row)
    return d, n**n


def replace(w, n, t, i, y, z):
    result = list(w)
    for k in neighbors(n, t, i):
        if max(k*(n-z), (n-k)*z) <= k*(n-k):
            result[k] = y
    return tuple(result)


class Full:
    def __init__(self, n, t):
        self.n, self.t = n, t
        self.d, self.den = masks(n)
        self.states = list(product(range(n+1), repeat=n+1))
        self.target = tuple(range(n+1))
        self.corner = (2,) + tuple(range(1, n+1))
        self.order = sorted(self.states, key=lambda w: sum(x != k for k, x in enumerate(w)))
        self.clean, self.active = [], []
        for i in range(n+1):
            clean, active = {}, {}
            for w in self.states:
                c, a = {}, {}
                for y in range(n+1):
                    v = replace(w, n, t, i, y, y)
                    c[v] = c.get(v, 0) + self.d[w[i]][y]
                    for z in range(n+1):
                        v = replace(w, n, t, i, y, z)
                        a[v] = a.get(v, 0) + self.d[w[i]][y]*self.d[y][z]
                assert sum(c.values()) == self.den
                assert sum(a.values()) == self.den**2
                clean[w], active[w] = c, a
            self.clean.append(clean)
            self.active.append(active)
        self.boundary = {}
        for w in self.states:
            dist = {w: 1}
            for i in range(n+1):
                nxt = {}
                for u, mass in dist.items():
                    for v, a in self.clean[i][u].items():
                        nxt[v] = nxt.get(v, 0) + mass*a
                dist = nxt
            assert sum(dist.values()) == self.den**(n+1)
            self.boundary[w] = dist

    def solve(self, rhs):
        values = {self.target: F(0)}
        factor = self.den**(self.n+1)
        for w in self.order[1:]:
            row = self.boundary[w]
            assert all(v == w or v in values for v in row)
            values[w] = (factor*rhs[w] + sum(m*values[v] for v, m in row.items() if v != w)) / (factor-row.get(w, 0))
        return values

    def product(self, value, order):
        """Evaluate every coefficient through order in a full sweep backwards."""
        suffix = [value] + [{w: F(0) for w in self.states} for _ in range(order)]
        for i in reversed(range(self.n+1)):
            nxt = []
            for r in range(order+1):
                row = {}
                for w in self.states:
                    v = sum(F(a, self.den)*suffix[r][u] for u, a in self.clean[i][w].items())
                    if r:
                        v += sum(F(a, self.den**2)*suffix[r-1][u] for u, a in self.active[i][w].items())
                        v -= sum(F(a, self.den)*suffix[r-1][u] for u, a in self.clean[i][w].items())
                    row[w] = v
                nxt.append(row)
            suffix = nxt
        return suffix

    def coefficients(self):
        started = time.monotonic()
        h0 = self.solve({w: F(1) for w in self.states})
        print(json.dumps(dict(n=self.n, T=self.t, stage='all clean means', elapsed_seconds=time.monotonic()-started)), flush=True)
        p0 = self.product(h0, 1)
        h1 = self.solve(p0[1])
        print(json.dumps(dict(n=self.n, T=self.t, stage='all first responses', elapsed_seconds=time.monotonic()-started)), flush=True)
        c = self.corner
        # Only the corner entry is required for the final two products. h0 and
        # h1 above are still solved on every population, without an error cap.
        within = self.product_at(h0, 2, c)*h0[c]
        between = self.product_at(h1, 1, c)*h0[c]
        return dict(n=self.n, T=self.t, states=len(self.states),
                    mean0=str(h0[c]), first=str(h1[c]), second=str(within+between),
                    within=str(within), between=str(between),
                    maximum_clean_mean=str(max(h0.values())),
                    maximum_clean_state=list(max(h0, key=h0.get)),
                    second_decimal=float(within+between))

    def product_at(self, value, order, state):
        @lru_cache(None)
        def visit(i, r, w):
            if r < 0 or r > self.n+1-i:
                return F(0)
            if i == self.n+1:
                return value[w] if r == 0 else F(0)
            result = sum(F(a, self.den)*visit(i+1, r, u)
                         for u, a in self.clean[i][w].items())
            if r:
                result += sum(F(a, self.den**2)*visit(i+1, r-1, u)
                              for u, a in self.active[i][w].items())
                result -= sum(F(a, self.den)*visit(i+1, r-1, u)
                              for u, a in self.clean[i][w].items())
            return result
        return visit(0, order, state)


def main(ns, out):
    rows = []
    for n in ns:
        for t in (2, 3):
            rows.append(Full(n, t).coefficients())
    out.write_text(json.dumps(dict(status='mechanically checked',
                                  arithmetic='exact integer/Fraction',
                                  full_state_results=rows, scientific_trajectories=0),
                              indent=2, sort_keys=True)+'\n')


if __name__ == '__main__':
    if hasattr(sys, 'set_int_max_str_digits'):
        sys.set_int_max_str_digits(0)
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--n', type=int, nargs='+', default=[3, 4])
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    main(args.n, args.out)
