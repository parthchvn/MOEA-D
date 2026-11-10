#!/usr/bin/env python3
"""Exact isolated-pair response and acceptance-weighted second-response checks.

Times here are ATTEMPTS (two per isolated-pair sweep). No RNG. The pair is
closed and has targets k,k+1. This is not the even-n orphan-fed last pair.
"""
import argparse
import csv
from fractions import Fraction as F
from functools import lru_cache
import hashlib
import json
from math import comb
from pathlib import Path
import sys

if hasattr(sys, 'set_int_max_str_digits'):
    sys.set_int_max_str_digits(0)
ZERO = F(0)


def mutation(n):
    rows = []
    for x in range(n+1):
        c = [1]
        for j in range(n):
            q0, q1 = (1, n-1) if j < x else (n-1, 1)
            t = [0]*(len(c)+1)
            for h, v in enumerate(c):
                t[h] += q0*v
                t[h+1] += q1*v
            c = t
        rows.append(tuple(F(v, n**n) for v in c))
    return tuple(rows)


class Pair:
    def __init__(self, n, k):
        self.n, self.k = n, k
        self.target = (k, k+1)
        self.d = mutation(n)
        self.r = tuple(row[k]+row[k+1] for row in self.d)

    @lru_cache(None)
    def clean(self, s, i):
        row = {s: F(1)}
        for j, target in enumerate(self.target):
            if s[j] == target:
                continue
            v = tuple(target if z == j else x for z, x in enumerate(s))
            p = self.d[s[i]][target]
            row[v] = row.get(v, ZERO)+p
            row[s] -= p
        return tuple((v, p) for v, p in row.items() if p)

    @lru_cache(None)
    def delta(self, s, i):
        row = {s: ZERO}
        for j, target in enumerate(self.target):
            for child in range(self.n+1):
                v = tuple(child if z == j else x for z, x in enumerate(s))
                if v == s:
                    continue
                p = self.d[s[i]][child]*(self.d[child][target]-F(child == target))
                row[v] = row.get(v, ZERO)+p
                row[s] -= p
        return tuple((v, p) for v, p in row.items() if p)

    @lru_cache(None)
    def values(self, s, degree=0):
        """Clean phase-cycle Poisson recursion for Taylor coefficients."""
        alpha, beta = F(1), ZERO
        coefficients = [None, None]
        for i in (1, 0):
            nxt, stay = 1-i, ZERO
            rhs = F(degree == 0)
            for v, p in self.clean(s, i):
                if v == s:
                    stay += p
                else:
                    rhs += p*self.values(v, degree)[nxt]
            if degree:
                rhs += sum((p*self.values(v, degree-1)[nxt]
                            for v, p in self.delta(s, i)), ZERO)
            alpha, beta = stay*alpha, stay*beta+rhs
            coefficients[i] = (alpha, beta)
        boundary = ZERO if s == self.target else beta/(1-alpha)
        return boundary, coefficients[1][0]*boundary+coefficients[1][1]

    def clear(self):
        for f in (self.clean, self.delta, self.values):
            f.cache_clear()


def write_csv(path, rows):
    with path.open('w', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def verify(ns):
    rows = []
    for n in ns:
        eta = F(1, n)
        theta = 2*eta*(1-eta)
        chi = (theta*theta/eta+(1-theta)**2/(1-eta))**n
        assert chi < 3
        for k in range(n):
            p = Pair(n, k)
            L, H = F(32*n), F(64*(32*n)**2)
            worst = ZERO
            sums = [ZERO, ZERO, ZERO]
            checks, doubles, singles = 0, 0, 0
            for x in range(n+1):
                rho = sum((p.d[x][z]*p.r[z] for z in range(n+1)), ZERO)
                assert rho*rho <= chi*p.r[x]
                checks += 1
                for y in range(n+1):
                    s = (x, y)
                    errors = sum(s[j] != p.target[j] for j in (0, 1))
                    values = [p.values(s, degree) for degree in range(3)]
                    for degree in range(3):
                        sums[degree] += sum(values[degree])
                    if errors == 2:
                        a, b = p.r[x], p.r[y]
                        rate = a+b
                        for phase in (0, 1):
                            assert values[0][phase] <= L+4/rate
                            # |v1| <= H(1+rate^(-3/2)), without a rounded sqrt.
                            residual = max(ZERO, abs(values[1][phase])/H-1)
                            assert residual*residual*rate**3 <= 1
                            # Main new bound, in attempts, including phase 1.
                            ratio = a*b*abs(values[2][phase])/(34*L*H)
                            assert ratio <= 1
                            worst = max(worst, ratio)
                            checks += 3
                        doubles += 1
                    elif errors == 1:
                        a = p.r[x] if x != k else p.r[y]
                        for phase in (0, 1):
                            assert values[0][phase] <= L
                            assert abs(values[1][phase]) <= 4*L*L
                            residual = max(ZERO, abs(values[2][phase])/(L*H)-4)
                            assert residual*residual*a <= 1
                            checks += 3
                        singles += 1
                    else:
                        assert values[0][0] == values[1][0] == values[2][0] == 0
                        assert values[0][1] <= L
                        assert abs(values[1][1]) <= 4*L*L
                        assert abs(values[2][1]) <= 4*L*H
                        checks += 6
            rows.append(dict(n=n, k=k, double_states=doubles, single_states=singles,
                             phases=2, exact_checks=checks,
                             max_weighted_second_ratio=float(worst),
                             chi_square_bound_decimal=float(chi),
                             value_sums_sha256=hashlib.sha256('|'.join(map(str, sums)).encode()).hexdigest()))
            p.clear()
        print(json.dumps(dict(stage='pair', n=n, pairs=n)), flush=True)
    return rows


def obstruction(ns):
    rows = []
    for n in ns:
        if n % 2 != 1 or n < 3:
            raise ValueError('Use odd n>=3: an actual closed last pair')
        v = F(1, n**n)
        a, b = n*(n-1)*v, v
        M = 20*n+2/(a+b)
        expression = a*b*M**3
        lower = 4*F(n)**(n-4)
        assert expression >= lower
        rows.append(dict(n=n, pair=f'{n-1} {n}', true_values='0 0',
                         two_entry_cubic_majorant=str(expression),
                         majorant_decimal=float(expression), lower_bound=str(lower),
                         status='positive majorant only; not a signed Taylor coefficient'))
    return rows


def supplied_entrance(ns):
    """Two positive one-activation sweeps from the actual supplied corner.

    Retains mutation AND acceptance factors. The output is a positive
    residence majorant, not a signed fourth-order coefficient.
    """
    rows = []
    for n in ns:
        assert n >= 9 and n % 2 == 1
        x = (n-1)//2
        c = F(n-1, n)**n
        corner0 = F(1, n**2)*F(n-1, n)**(n-2)
        corner1 = F(1, n)*F(n-1, n)**(n-1)
        q = 1-(1-corner0)*(1-corner1)
        b = F(1, n)**(n-x)*F(n-1, n)**x
        ratio = (n-x)*(n-1)+F(x, n-1)
        a, r = ratio*b, (ratio+1)*b
        s, escape = 1-r, 1-(1-r)**2
        forward = F(comb(n, x), n)*a
        entry = (1-q)*q*c*c*s*forward*a*b
        value = entry/escape**3
        lower = F(comb(n, x), 12288*n**4)
        exponential = F(2**n, 12288*n**4*(n+1))
        assert 1-q >= F(1, 2) and q >= F(1, 3*n)
        assert c >= F(1, 4) and s >= F(1, 2)
        assert value >= lower >= exponential
        rows.append(dict(n=n, k=n-1, wrong_weight=x, entry_path_weight=str(entry),
                         clean_escape=str(escape), weighted_third_residence=str(value),
                         weighted_third_residence_decimal=float(value),
                         binomial_lower_bound=str(lower), exponential_lower_bound=str(exponential),
                         status='proved positive path lower bound; not a signed coefficient'))
    return rows


def main(out, ns):
    out.mkdir(parents=True, exist_ok=True)
    rows = verify(ns)
    write_csv(out/'pair.csv', rows)
    witness = obstruction([3, 5, 9, 17, 33, 65])
    write_csv(out/'obstruction.csv', witness)
    entrance = supplied_entrance([9, 17, 33, 65, 129])
    write_csv(out/'entrance.csv', entrance)
    result = dict(status='mechanically checked', arithmetic='exact rational',
                  pairs=len(rows), double_phase_states=2*sum(r['double_states'] for r in rows),
                  single_phase_states=2*sum(r['single_states'] for r in rows),
                  exact_checks=sum(r['exact_checks'] for r in rows),
                  obstruction_witnesses=len(witness), scientific_trajectories=0,
                  supplied_entrance_witnesses=len(entrance),
                  scientific_seeds=[], local_time_unit='attempts, two per pair sweep',
                  scope='isolated closed pair only; no inference about the full fourth coefficient')
    (out/'pair.json').write_text(json.dumps(result, indent=2, sort_keys=True)+'\n')
    print(json.dumps(result), flush=True)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out', type=Path, required=True)
    parser.add_argument('--n', type=int, nargs='+', default=[3, 4, 5, 6, 7, 8, 9])
    args = parser.parse_args()
    main(args.out, args.n)
