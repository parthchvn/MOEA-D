#!/usr/bin/env python3
"""Exact acceptance-weighted resolvent obstruction; no random trajectories."""
import argparse
import csv
from fractions import Fraction as F
from functools import lru_cache
import json
from math import comb
from pathlib import Path


@lru_cache(None)
def kernel(n):
    """Integer polynomial multiplication, then one rational normalization."""
    rows = []
    for x in range(n + 1):
        poly = [1]
        for j in range(n):
            lo, hi = (1, n - 1) if j < x else (n - 1, 1)
            new = [0] * (len(poly) + 1)
            for k, v in enumerate(poly):
                new[k] += lo * v
                new[k + 1] += hi * v
            poly = new
        rows.append(tuple(F(v, n ** n) for v in poly))
    return tuple(rows)


def literal_kernel(n):
    rows = []
    for x in range(n + 1):
        bits = (1 << x) - 1
        row = [F(0)] * (n + 1)
        for mask in range(1 << n):
            row[(bits ^ mask).bit_count()] += F((n - 1) ** (n - mask.bit_count()), n ** n)
        rows.append(tuple(row))
    return tuple(rows)


def recipients(n, i):
    """T=2, literal alternating enumeration, including even-n orphan."""
    for dist in range(1, n + 1):
        for direction in ((1, -1) if i % 2 == 0 else (-1, 1)):
            other = i + direction * dist
            if 0 <= other <= n:
                return (i, other)
    raise ValueError(n)


def put(state, k, y):
    result = list(state)
    result[k] = y
    return tuple(result)


def add(dst, state, p):
    dst[state] = dst.get(state, F(0)) + p


def step(state, breeder, targets, indices, d, active):
    """Full accepted/rejected outcomes; a child changes only observed target."""
    out = {}
    for y, py in enumerate(d[state[breeder]]):
        if active:
            observations = enumerate(d[y])
        else:
            observations = ((y, F(1)),)
        for z, pz in observations:
            nxt = put(state, indices[z], y) if z in targets else state
            add(out, nxt, py * pz)
    return out


def derivative_row(n, state, local=False):
    d = kernel(n)
    q0, q1 = {state: F(1)}, {}
    breeders = range(2) if local else range(n + 1)
    for i in breeders:
        targets = (n - 1, n) if local else recipients(n, i)
        indices = {n - 1: 0, n: 1} if local else {j: j for j in targets}
        new0, new1 = {}, {}
        for u in q0.keys() | q1.keys():
            clean = step(u, i, targets, indices, d, False)
            for v, a in clean.items():
                add(new0, v, q0.get(u, F(0)) * a)
                add(new1, v, q1.get(u, F(0)) * a)
            if u in q0:
                active = step(u, i, targets, indices, d, True)
                for v in clean.keys() | active.keys():
                    add(new1, v, q0[u] * (active.get(v, F(0)) - clean.get(v, F(0))))
        q0 = {u: v for u, v in new0.items() if v}
        q1 = {u: v for u, v in new1.items() if v}
    return q0, q1


def pair_formula(n):
    if n < 3 or n % 2 != 1:
        raise ValueError('Odd n >= 3 required')
    v = F(1, n ** n)
    u = n * (n - 1) * v
    r = u + v
    s = 1 - r
    c = F(n - 1, n) ** n
    theta = F(2 * (n - 1), n * n)
    r2 = n * theta ** (n - 1) * (1 - theta) + theta ** n
    q = 1 - s * s
    derivative = 2 * s * (r * (1 + c) - r2) + c * u * u + v ** 3
    lower = -derivative / q
    coarse = F(2 ** n, 8 * n * n) - 5
    assert lower >= coarse
    signed_lower = lower - 6 * n * r
    return dict(n=n, kind='adjacent_pair', escape=q, derivative=derivative,
                lower=lower, coarse=coarse, signed_lower=signed_lower,
                inverse_scale=signed_lower / n ** 4)


def orphan_formula(n):
    if n < 4 or n % 2:
        raise ValueError('Even n >= 4 required')
    d = F(1, n ** n)
    c = F(n - 1, n) ** n
    lower = (2 ** n - 1) * c - 1
    return dict(n=n, kind='orphan', escape=d, derivative=-d * lower,
                lower=lower, coarse=F(2 ** n - 1, 4) - 1,
                signed_lower=lower,
                inverse_scale=lower / n ** 4)


def signed_diagonal(n, full=False):
    """(R0 Q1)[E,E], with clean subset elimination before absolute values."""
    e = tuple(range(n - 1)) + (0, 0) if full else (0, 0)
    states = [e]
    states += [put(e, n - 1 if full else 0, n - 1),
               put(e, n if full else 1, n)]
    rows = {s: derivative_row(n, s, local=not full) for s in states}
    clean, derivative = rows[e]
    q = 1 - clean[e]
    diagonal = derivative[e] / q
    visits = {}
    for s in states[1:]:
        qs = 1 - rows[s][0][s]
        visits[s] = clean.get(s, F(0)) / (q * qs)
        assert visits[s] <= 3 * n
        diagonal += visits[s] * rows[s][1].get(e, F(0))
    return diagonal


def local_sweep(n, state, p):
    d = kernel(n)
    dist = {state: F(1)}
    for i in range(2):
        out = {}
        for u, mass in dist.items():
            a = step(u, i, (n - 1, n), {n - 1: 0, n: 1}, d, False)
            b = step(u, i, (n - 1, n), {n - 1: 0, n: 1}, d, True)
            for v in a.keys() | b.keys():
                add(out, v, mass * ((1 - p) * a.get(v, F(0)) + p * b.get(v, F(0))))
        dist = out
    return dist


def solve(a, b):
    """Exact pivoted Gauss-Jordan elimination for small independent checks."""
    rows = [list(row) + [value] for row, value in zip(a, b)]
    size = len(rows)
    for k in range(size):
        pivot = next(i for i in range(k, size) if rows[i][k])
        rows[k], rows[pivot] = rows[pivot], rows[k]
        v = rows[k][k]
        rows[k] = [x / v for x in rows[k]]
        for i in range(size):
            if i != k:
                v = rows[i][k]
                rows[i] = [x - v * y for x, y in zip(rows[i], rows[k])]
    return [row[-1] for row in rows]


def orphan_matrix(n, p):
    d = kernel(n)
    matrix = []
    for x in range(n + 1):
        row = [d[x][y] * ((1 - p) * (y == n) + p * d[y][n])
               if y != x else F(0) for y in range(n + 1)]
        row[x] = 1 - sum(row)
        matrix.append(row)
    return matrix


def orphan_tail(n, p_choice):
    d = kernel(n)
    q = 1 - (1 - d[2][0]) * (1 - d[1][0])
    s = 1 - q
    p = F(1, n ** 4) if p_choice == 'n^-4' else q / 4
    assert 0 < p <= q / 4
    r0, j = orphan_matrix(n, F(0)), orphan_matrix(n, F(1))
    delta = [[v - u for u, v in zip(a, b)] for a, b in zip(r0, j)]
    a0 = [[F(i == k) - s * r0[i][k] for k in range(n + 1)] for i in range(n + 1)]
    e = [F(i == n) for i in range(n + 1)]
    z0 = solve(a0, e)
    z1 = solve(a0, [s * sum(v * x for v, x in zip(row, z0)) for row in delta])
    z2 = solve(a0, [s * sum(v * x for v, x in zip(row, z1)) for row in delta])
    b = 1 - d[n][n]
    c0, c1, c2 = z0[n], z1[n] + b * z0[n], z2[n] + b * z1[n] + b * b * z0[n]
    rp = orphan_matrix(n, p)
    ap = [[F(i == k) - s * rp[i][k] for k in range(n + 1)] for i in range(n + 1)]
    value = solve(ap, e)[n] / (1 - b * p)
    remainder = value - c0 - p * c1 - p * p * c2
    bound = 128 * p ** 3 / q ** 4
    assert c0 == 1 / q and abs(remainder) <= bound
    return dict(n=n, p_choice=p_choice, p=str(p), q=str(q), value=str(value),
                first=str(c1), second=str(c2), remainder=str(remainder), bound=str(bound),
                remainder_decimal=float(remainder), bound_decimal=float(bound),
                exact_bound_pass=True)


def verify():
    counts = dict(kernel_entries=0, local_pair_formulas=0, full_pair_rows=0,
                  full_orphan_rows=0, reachable_insertions=0, positive_p_denominators=0,
                  closed_form_bounds=0, signed_resolvent_diagonals=0)
    for n in range(2, 8):
        assert kernel(n) == literal_kernel(n)
        assert all(sum(row) == 1 for row in kernel(n))
        counts['kernel_entries'] += (n + 1) ** 2
    details = []
    for n in (3, 5, 7, 9):
        f = pair_formula(n)
        q0, q1 = derivative_row(n, (0, 0), local=True)
        assert sum(q0.values()) == 1 and sum(q1.values()) == 0
        assert 1 - q0[(0, 0)] == f['escape']
        assert q1[(0, 0)] == f['derivative']
        signed = signed_diagonal(n)
        assert -signed >= f['signed_lower']
        counts['signed_resolvent_diagonals'] += 1
        counts['local_pair_formulas'] += 1
        for p in (F(0), F(1, n ** 4), F(1, 2), F(3, 4)):
            dist = local_sweep(n, (0, 0), p)
            den = 1 - dist[(0, 0)]
            assert den >= (1 - p) ** 2 * f['escape'] > 0
            counts['positive_p_denominators'] += 1
        if n <= 7:
            e = tuple(range(n - 1)) + (0, 0)
            a, b = derivative_row(n, e)
            assert 1 - a[e] == f['escape']
            assert b[e] <= f['derivative'] < 0
            full_signed = signed_diagonal(n, full=True)
            assert full_signed <= signed
            counts['signed_resolvent_diagonals'] += 1
            counts['full_pair_rows'] += 1
            c = (2,) + tuple(range(1, n + 1))
            first = put(c, n - 1, 0)
            _, dc = derivative_row(n, c)
            _, df = derivative_row(n, first)
            assert dc[first] > 0 and df[e] > 0
            counts['reachable_insertions'] += 2
            details.append(dict(n=n, Q1_corner_first=str(dc[first]),
                                Q1_first_pair=str(df[e]),
                                full_diagonal=str(b[e]), local_diagonal=str(f['derivative']),
                                local_signed_resolvent_diagonal=str(signed),
                                full_signed_resolvent_diagonal=str(full_signed)))
    for n in (4, 6, 8):
        f = orphan_formula(n)
        e = tuple(range(n)) + (0,)
        a, b = derivative_row(n, e)
        assert 1 - a[e] == f['escape']
        assert b[e] <= f['derivative'] < 0
        counts['full_orphan_rows'] += 1
    for n in range(3, 130):
        f = pair_formula(n) if n % 2 else orphan_formula(n)
        assert f['lower'] >= f['coarse']
        counts['closed_form_bounds'] += 1
    return dict(status='pass', arithmetic='exact rational', counts=counts,
                reachable_pair_receipts=details, scientific_trajectories=0,
                scientific_seeds=[], censoring='not applicable; deterministic identities',
                scope='No-go for the positive absolute insertion majorant, not for every signed or resummed resolvent.')


def main(out):
    out.mkdir(parents=True, exist_ok=True)
    result = verify()
    rows = []
    for n in (3, 4, 5, 8, 9, 16, 17, 32, 33, 64, 65, 128, 129):
        f = pair_formula(n) if n % 2 else orphan_formula(n)
        row = {k: (str(v) if isinstance(v, F) else v) for k, v in f.items()}
        row.update(lower_decimal=float(f['lower']), signed_lower_decimal=float(f['signed_lower']),
                   n_minus_four_times_lower=float(f['inverse_scale']),
                   majorant_diverges_at_n_minus_four=f['inverse_scale'] >= 1)
        rows.append(row)
    with (out / 'obstruction.csv').open('w', newline='') as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    tails = [orphan_tail(n, p) for n in (4, 6, 8, 10, 12) for p in ('n^-4', 'q/4')]
    with (out / 'orphan.csv').open('w', newline='') as stream:
        writer = csv.DictWriter(stream, fieldnames=list(tails[0]))
        writer.writeheader()
        writer.writerows(tails)
    result['counts']['discounted_orphan_remainders'] = len(tails)
    (out / 'verification.json').write_text(json.dumps(result, indent=2, sort_keys=True) + '\n')
    print(json.dumps(result['counts'], sort_keys=True))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out', type=Path, required=True)
    main(parser.parse_args().out)
