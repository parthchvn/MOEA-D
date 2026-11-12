#!/usr/bin/env python3
"""Exact real-p pair Schur checks. No stochastic trajectories or prior solvers."""
import argparse
import csv
from fractions import Fraction as F
from functools import lru_cache
import json
from math import comb
from pathlib import Path


@lru_cache(None)
def kernel(n):
    # Count lost ones and gained zeros independently.
    rows = []
    for x in range(n + 1):
        row = []
        for y in range(n + 1):
            total = 0
            for lost in range(x + 1):
                gained = y - x + lost
                if 0 <= gained <= n - x:
                    flips = lost + gained
                    total += comb(x, lost) * comb(n - x, gained) * (n - 1) ** (n - flips)
            row.append(F(total, n ** n))
        rows.append(tuple(row))
    return tuple(rows)


def literal_kernel(n):
    out = []
    for x in range(n + 1):
        row = [F(0)] * (n + 1)
        for mask in range(1 << n):
            y = (((1 << x) - 1) ^ mask).bit_count()
            row[y] += F((n - 1) ** (n - mask.bit_count()), n ** n)
        out.append(tuple(row))
    return tuple(out)


def add(row, key, value):
    if value:
        row[key] = row.get(key, F(0)) + value


class Pair:
    """Autonomous pair with target a then b=a+1; boundary observation only."""
    def __init__(self, n, a):
        assert n >= 3 and 0 <= a < n
        self.n, self.a, self.b = n, a, a + 1
        self.targets = (a, a + 1)
        self.states = tuple((x, y) for x in range(n + 1) for y in range(n + 1))
        self.index = {s: i for i, s in enumerate(self.states)}
        self.d = kernel(n)
        self.D = tuple(i for i, (x, y) in enumerate(self.states) if x != a and y != a + 1)
        self.S = tuple(i for i, (x, y) in enumerate(self.states) if (x == a) != (y == a + 1))
        self.A = self.index[self.targets]
        self.G = self.S + (self.A,)
        self.r = tuple(self.d[x][a] + self.d[x][a + 1] for x in range(n + 1))
        self.v = tuple(tuple(self.potential(s, phase) for s in self.states) for phase in (0, 1))

    def potential(self, state, phase):
        x, y = state
        if x == self.a or y == self.b:
            return F(0)
        q = self.r[x] + self.r[y] - self.r[x] * self.r[y]
        return (2 - self.r[state[phase]]) / q

    @lru_cache(None)
    def step(self, phase, active):
        rows = []
        for s in self.states:
            row, mass = {}, F(0)
            for child, prob in enumerate(self.d[s[phase]]):
                for slot, target in enumerate(self.targets):
                    accept = prob * (self.d[child][target] if active else F(child == target))
                    t = list(s)
                    t[slot] = child
                    add(row, self.index[tuple(t)], accept)
                    mass += accept
            add(row, self.index[s], 1 - mass)
            assert sum(row.values()) == 1 and all(v >= 0 for v in row.values())
            rows.append(row)
        return tuple(rows)

    def literal_step(self, phase, active):
        # Independent genotype XOR enumeration and scalar comparison.
        n = self.n
        masks = [(m, F((n - 1) ** (n - m.bit_count()), n ** n)) for m in range(1 << n)]
        rows = []
        for s in self.states:
            parent = (1 << s[phase]) - 1
            row = {}
            for mutation, pm in masks:
                child = parent ^ mutation
                for noise, pn in (masks if active else [(0, F(1))]):
                    obs = (child ^ noise).bit_count()
                    t = list(s)
                    for slot, target in enumerate(self.targets):
                        cost = max(target * (n - obs), (n - target) * obs)
                        incumbent = target * (n - target)
                        if cost <= incumbent:
                            t[slot] = child.bit_count()
                    add(row, self.index[tuple(t)], pm * pn)
            rows.append(row)
        return tuple(rows)

    def mixed_step(self, phase, p):
        k, j = self.step(phase, False), self.step(phase, True)
        return tuple({t: (1-p)*u.get(t, F(0)) + p*w.get(t, F(0))
                      for t in u.keys() | w.keys()} for u, w in zip(k, j))

    def sweep(self, p):
        first, second = self.mixed_step(0, p), self.mixed_step(1, p)
        rows = []
        for u in first:
            row = {}
            for mid, prob in u.items():
                for t, chance in second[mid].items():
                    add(row, t, prob * chance)
            rows.append(row)
        return tuple(rows)


def act(rows, values):
    return tuple(sum((v * values[j] for j, v in row.items()), F(0)) for row in rows)


def solve(matrix, rhs):
    """Exact elimination with multiple RHS columns, no floating-point solves."""
    n = len(matrix)
    width = len(rhs[0])
    rows = [list(a) + list(b) for a, b in zip(matrix, rhs)]
    for k in range(n):
        pivot = next(i for i in range(k, n) if rows[i][k])
        rows[k], rows[pivot] = rows[pivot], rows[k]
        value = rows[k][k]
        rows[k] = [v/value for v in rows[k]]
        for i in range(n):
            if i == k or not rows[i][k]:
                continue
            value = rows[i][k]
            rows[i] = [u-value*v for u, v in zip(rows[i], rows[k])]
    return [row[n:n+width] for row in rows]


def check_inequalities(pair, p):
    assert 0 <= p < F(1, 6)
    v0, v1 = pair.v
    first, second = pair.mixed_step(0, p), pair.mixed_step(1, p)
    pv = act(first, act(second, v0))
    delta = 1 - 6*p
    for i in pair.D:
        assert v0[i] - pv[i] >= delta, (pair.n, pair.a, p, pair.states[i])
    for i in pair.S:
        assert pv[i] <= 4*p
    assert pv[pair.A] <= 2*p*p
    return dict(n=pair.n, a=pair.a, b=pair.b, p=str(p), double_states=len(pair.D),
                min_drift=str(min(v0[i]-pv[i] for i in pair.D)), drift_bound=str(delta),
                max_single_entry_potential=str(max(pv[i] for i in pair.S)),
                single_entry_bound=str(4*p), aligned_entry_potential=str(pv[pair.A]),
                aligned_entry_bound=str(2*p*p), exact_pass=True)


def schur_cell(n, a, p):
    pair = Pair(n, a)
    rows = pair.sweep(p)
    D, S, G = pair.D, pair.S, pair.G
    matrix = [[F(i == j) - rows[i].get(j, F(0)) for j in D] for i in D]
    rhs = [[F(1)] + [rows[i].get(g, F(0)) for g in G] for i in D]
    solution = solve(matrix, rhs)
    # First column is residence R1, remaining columns are exit probabilities R P_DG.
    residence = {i: solution[t][0] for t, i in enumerate(D)}
    exits = {i: solution[t][1:] for t, i in enumerate(D)}
    delta = 1-6*p
    for i in D:
        assert 0 < residence[i] <= pair.v[0][i]/delta
        assert all(v >= 0 for v in exits[i]) and sum(exits[i]) == 1
    dwell, trace = {}, {}
    for i in G:
        dwell[i] = sum(rows[i].get(j, F(0))*residence[j] for j in D)
        trace[i] = [rows[i].get(g, F(0)) +
                    sum(rows[i].get(j, F(0))*exits[j][k] for j in D)
                    for k, g in enumerate(G)]
        assert all(v >= 0 for v in trace[i]) and sum(trace[i]) == 1
        assert dwell[i] <= (2*p*p if i == pair.A else 4*p)/delta
        entrance = sum(rows[i].get(j, F(0)) for j in D)
        assert entrance <= (p*p if i == pair.A else 2*p)
    eta = (1-p)**2 / (3*n)
    for i in S:
        assert rows[i].get(pair.A, F(0)) >= eta
        assert trace[i][-1] >= eta
    reduced = [[F(i == j) - trace[i][k] for k, j in enumerate(S)] for i in S]
    hs = solve(reduced, [[1+dwell[i]] for i in S])
    transient = tuple(i for i in range(len(rows)) if i != pair.A)
    full = [[F(i == j) - rows[i].get(j, F(0)) for j in transient] for i in transient]
    hf = solve(full, [[F(1)] for i in transient])
    full_h = {i: hf[t][0] for t, i in enumerate(transient)}
    bound = (1+4*p/delta)/eta
    for t, i in enumerate(S):
        assert hs[t][0] == full_h[i] <= bound
    for i in D:
        assert residence[i] + sum(exits[i][k]*hs[k][0] for k in range(len(S))) == full_h[i]
    smax = max(S, key=lambda i: dwell[i])
    e = pair.index[(0, 0)] if a > 0 else pair.index[(n, n)]
    return dict(n=n, a=a, b=a+1, p=str(p), double_states=len(D),
                single_states=len(S), max_weighted_residence=str(dwell[smax]),
                max_weighted_residence_decimal=float(dwell[smax]),
                residence_bound=str(4*p/delta), residence_bound_decimal=float(4*p/delta),
                aligned_weighted_residence=str(dwell[pair.A]),
                aligned_bound=str(2*p*p/delta), max_single_alignment=str(max(x[0] for x in hs)),
                max_single_alignment_decimal=float(max(x[0] for x in hs)),
                alignment_bound=str(bound), alignment_bound_decimal=float(bound),
                extreme_residence=str(residence[e]), extreme_residence_decimal=float(residence[e]),
                exact_schur_equals_direct=True, stochastic_exit=True)


def moment_obstruction(n):
    assert n >= 3 and n % 2
    # S=(0,n), E=(0,0) in the last pair (n-1,n).
    c, v = F(n-1, n)**n, F(1, n**n)
    r = (n*(n-1)+1)*v
    s, q = 1-r, 2*r-r*r
    entrance = c*v*s  # one explicit first-active, second-clean path
    lower = entrance/(q*q)
    coarse = F(n**n, 32*n**4)
    assert lower >= coarse
    return dict(n=n, entrance_derivative_lower=str(entrance), clean_exit=str(q),
                weighted_first_path=str(entrance/q), weighted_first_path_decimal=float(entrance/q),
                iterated_residence_lower=str(lower), iterated_residence_decimal=float(lower),
                coarse_lower=str(coarse), exact_lower_pass=True)


def full_tensor_checks():
    """Independent full attempt ordering, with literal T=2 recipient search."""
    n, p = 3, F(1, 81)
    pairs = [Pair(n, a) for a in (0, 2)]
    sweeps = [pair.sweep(p) for pair in pairs]
    d = kernel(n)
    checked = 0
    for initial in ((2,1,2,3), (0,1,0,0), (0,1,2,3), (3,3,0,0)):
        dist = {initial: F(1)}
        for breeder in range(n+1):
            targets = None
            for distance in range(1, n+1):
                for sign in ((1,-1) if breeder % 2 == 0 else (-1,1)):
                    other = breeder+sign*distance
                    if 0 <= other <= n:
                        targets = (breeder, other)
                        break
                if targets is not None:
                    break
            nxt = {}
            for state, weight in dist.items():
                for child, pm in enumerate(d[state[breeder]]):
                    for observed in range(n+1):
                        probability = pm*((1-p)*F(child == observed)+p*d[child][observed])
                        new = list(state)
                        if observed in targets:
                            new[observed] = child
                        add(nxt, tuple(new), weight*probability)
            dist = nxt
        left = sweeps[0][pairs[0].index[initial[:2]]]
        right = sweeps[1][pairs[1].index[initial[2:]]]
        product = {pairs[0].states[i]+pairs[1].states[j]: a*b
                   for i,a in left.items() for j,b in right.items() if a*b}
        assert dist == product and sum(dist.values()) == 1
        checked += len(dist)
    return dict(full_population_rows=4, full_population_entries=checked,
                n=n, p=str(p), exact_tensor_match=True)


def analytic_bounds(n):
    p = F(1, n**4)
    delta = 1-6*p
    residence = 4*p/delta
    return dict(n=n, p=str(p), single_residence_bound=str(residence),
                single_residence_bound_decimal=float(residence),
                aligned_residence_bound=str(2*p*p/delta),
                single_exit_mass_bound=str(2*p),
                pair_alignment_bound=str(3*n*(1+residence)/(1-p)**2),
                status='analytic candidate bound, not a measured mean')


def write_csv(path, rows):
    with path.open('w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)


def main(out):
    out.mkdir(parents=True, exist_ok=True)
    counts = dict(kernel_entries=0, literal_attempt_rows=0, phase_clean_identities=0,
                  active_drift_inequalities=0, active_entry_inequalities=0,
                  sweep_drift_inequalities=0, sweep_entry_inequalities=0,
                  schur_cells=0, direct_transient_equations=0)
    for n in range(3, 8):
        assert kernel(n) == literal_kernel(n)
        counts['kernel_entries'] += (n+1)**2
    inequalities = []
    for n in (3, 5, 7, 9):
        for a in range(0, n, 2):
            pair = Pair(n, a)
            for phase in (0, 1):
                clean, active = pair.step(phase, False), pair.step(phase, True)
                if n in (3, 5):
                    assert clean == pair.literal_step(phase, False)
                    assert active == pair.literal_step(phase, True)
                    counts['literal_attempt_rows'] += 2*len(pair.states)
                cv, jv = act(clean, pair.v[1-phase]), act(active, pair.v[1-phase])
                for i in pair.D:
                    assert cv[i]-pair.v[phase][i] == -1
                    assert jv[i]-cv[i] <= 4
                    state = pair.states[i]
                    assert pair.v[phase][i] <= min(2/pair.r[z] for z in state)
                for i in pair.S:
                    assert cv[i] == 0 and jv[i] <= 2
                assert jv[pair.A] == cv[pair.A] == 0
                counts['phase_clean_identities'] += len(pair.D)
                counts['active_drift_inequalities'] += len(pair.D)
                counts['active_entry_inequalities'] += len(pair.G)
            for p in (F(0), F(1,n**4), F(1,64*n), F(1,12)):
                inequalities.append(check_inequalities(pair, p))
                counts['sweep_drift_inequalities'] += len(pair.D)
                counts['sweep_entry_inequalities'] += len(pair.G)
    write_csv(out/'inequalities.csv', inequalities)
    cells = []
    for n, a, p in ((3,0,F(1,81)), (3,2,F(1,81)),
                    (3,0,F(1,192)), (3,2,F(1,192)),
                    (3,0,F(1,12)), (3,2,F(1,12)),
                    (5,0,F(1,625)), (5,4,F(1,625)),
                    (5,2,F(1,12))):
        cells.append(schur_cell(n,a,p))
        counts['schur_cells'] += 1
        counts['direct_transient_equations'] += (n+1)**2-1
    write_csv(out/'schur.csv', cells)
    moments = [moment_obstruction(n) for n in (3,5,9,17,33,65)]
    write_csv(out/'moments.csv', moments)
    write_csv(out/'bounds.csv', [analytic_bounds(n) for n in (3,5,9,17,33,65)])
    tensor = full_tensor_checks()
    data = dict(status='mechanically checked', counts=counts, arithmetic='exact rational',
                tensor=tensor,
                scope='Autonomous adjacent pairs; actual closed T=2 pairs at odd n. No full-population remainder claim.',
                scientific_trajectories=0, scientific_seeds=[],
                higher_residence_bound='Contradicted: uniform polynomial E1 R0^2 1 on single-error rows.',
                files=['inequalities.csv','schur.csv','moments.csv','bounds.csv'])
    (out/'verification.json').write_text(json.dumps(data,indent=2,sort_keys=True)+'\n')
    print(json.dumps(data,sort_keys=True))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out', type=Path, required=True)
    main(parser.parse_args().out)
