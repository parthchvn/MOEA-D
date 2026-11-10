#!/usr/bin/env python3
"""Independent, deterministic round-12 audit; no trajectory sampling.

Mutation uses per-bit generating polynomials. Selection uses literal pinned
Tchebycheff comparisons. No previous round's implementation is imported.
"""
import argparse
import csv
from fractions import Fraction as F
from functools import lru_cache
from itertools import product
import json
from math import lcm
from pathlib import Path


def plus(row, key, value):
    if value:
        row[key] = row.get(key, F(0)) + value


@lru_cache(None)
def mutation(n):
    rows = []
    for ones in range(n + 1):
        poly = [1]
        for bit in range(n):
            zero, one = (1, n-1) if bit < ones else (n-1, 1)
            nxt = [0] * (len(poly) + 1)
            for k, count in enumerate(poly):
                nxt[k] += zero * count
                nxt[k+1] += one * count
            poly = nxt
        rows.append(tuple(F(x, n**n) for x in poly))
    return tuple(rows)


def neighbors(n, i):
    order = [i]
    for distance in range(1, n+1):
        for sign in ((1, -1) if i % 2 == 0 else (-1, 1)):
            j = i + sign * distance
            if 0 <= j <= n:
                order.append(j)
                if len(order) == 2:
                    return tuple(order)
    raise ValueError('n must be positive')


def closed_pair(n, a):
    chosen = {a, a+1}
    return all((set(neighbors(n, i)) <= chosen if i in chosen
                else not chosen.intersection(neighbors(n, i))) for i in range(n+1))


def selected(n, targets, state, recipients, child, observed):
    result = list(state)
    for slot, k in enumerate(targets):
        if k in recipients and max(k*(n-observed), (n-k)*observed) <= k*(n-k):
            result[slot] = child
    return tuple(result)


@lru_cache(None)
def attempt(n, targets, state, donor, recipients, active):
    d = mutation(n)
    slot = targets.index(donor)
    row = {}
    for child, pc in enumerate(d[state[slot]]):
        observations = enumerate(d[child]) if active else ((child, F(1)),)
        for observed, po in observations:
            new = selected(n, targets, state, recipients, child, observed)
            plus(row, new, pc*po)
    assert sum(row.values()) == 1 and min(row.values()) >= 0
    return row


def literal_attempt(n, targets, state, donor, recipients, active):
    parent = (1 << state[targets.index(donor)]) - 1
    masks = [(mask, F((n-1)**(n-mask.bit_count()), n**n)) for mask in range(1 << n)]
    row = {}
    for mask, pm in masks:
        child = parent ^ mask
        for noise, pn in masks if active else ((0, F(1)),):
            new = selected(n, targets, state, recipients, child.bit_count(),
                           (child ^ noise).bit_count())
            plus(row, new, pm*pn)
    return row


def blend(left, right, p):
    return {k: (1-p)*left.get(k, F(0)) + p*right.get(k, F(0))
            for k in left.keys() | right.keys()
            if (1-p)*left.get(k, F(0)) + p*right.get(k, F(0))}


def sweep_row(n, targets, initial, p, recipient_map=None):
    dist = {initial: F(1)}
    for donor in targets:
        recipients = recipient_map[donor] if recipient_map else neighbors(n, donor)
        nxt = {}
        for state, prob in dist.items():
            clean = attempt(n, targets, state, donor, recipients, False)
            active = attempt(n, targets, state, donor, recipients, True)
            for new, chance in blend(clean, active, p).items():
                plus(nxt, new, prob*chance)
        dist = nxt
    return dist


class Pair:
    def __init__(self, n, a):
        if not (n >= 3 and 0 <= a < n):
            raise ValueError('need n>=3 and adjacent targets in range')
        self.n, self.a = n, a
        self.targets = (a, a+1)
        self.states = tuple(product(range(n+1), repeat=2))
        self.D = tuple(s for s in self.states if all(x != k for x, k in zip(s, self.targets)))
        self.S = tuple(s for s in self.states if sum(x != k for x, k in zip(s, self.targets)) == 1)
        self.A = self.targets
        self.G = self.S + (self.A,)
        self.r = tuple(sum(mutation(n)[z][k] for k in self.targets) for z in range(n+1))
        self.V = tuple({s: self.potential(s, phase) for s in self.states} for phase in (0, 1))
        self.K = tuple({s: attempt(n, self.targets, s, k, self.targets, False)
                        for s in self.states} for k in self.targets)
        self.J = tuple({s: attempt(n, self.targets, s, k, self.targets, True)
                        for s in self.states} for k in self.targets)

    def potential(self, s, phase):
        if s not in self.D:
            return F(0)
        rx, ry = (self.r[x] for x in s)
        return (2-self.r[s[phase]])/(rx+ry-rx*ry)

    def sweep(self, p):
        out = {}
        for s in self.states:
            row = {}
            for t, prob in blend(self.K[0][s], self.J[0][s], p).items():
                for u, chance in blend(self.K[1][t], self.J[1][t], p).items():
                    plus(row, u, prob*chance)
            out[s] = row
        return out


def apply(rows, values):
    return {s: sum((prob*values[t] for t, prob in row.items()), F(0))
            for s, row in rows.items()}


def bernstein2(coeff, upper=F(1, 6)):
    c0, c1, c2 = coeff
    return (c0, c0+c1*upper/2, c0+c1*upper+c2*upper**2)


def phase_certificate(n, a):
    pair = Pair(n, a)
    active_diff = []
    for phase in (0, 1):
        cv = apply(pair.K[phase], pair.V[1-phase])
        jv = apply(pair.J[phase], pair.V[1-phase])
        for s in pair.D:
            assert cv[s] - pair.V[phase][s] == -1
            assert jv[s] - cv[s] <= 4
            assert pair.V[phase][s] <= min(2/pair.r[z] for z in s)
            active_diff.append(jv[s]-cv[s])
        assert all(cv[s] == 0 and jv[s] <= 2 for s in pair.S)
        assert jv[pair.A] == cv[pair.A] == 0
    # P(p)V = c0 + c1*p + c2*p^2, assembled from four fixed gate patterns.
    vv = {}
    for first in (0, 1):
        for second in (0, 1):
            vv[first, second] = apply((pair.K, pair.J)[first][0],
                                     apply((pair.K, pair.J)[second][1], pair.V[0]))
    minima = {'D': [], 'S': [], 'A': []}
    for s in pair.states:
        p0 = vv[0, 0][s]
        p1 = vv[1, 0][s] + vv[0, 1][s] - 2*p0
        p2 = vv[1, 1][s] - vv[1, 0][s] - vv[0, 1][s] + p0
        if s in pair.D:
            kind, coeff = 'D', (pair.V[0][s]-p0-1, 6-p1, -p2)
        elif s in pair.S:
            kind, coeff = 'S', (-p0, 4-p1, -p2)
        else:
            kind, coeff = 'A', (-p0, -p1, 2-p2)
        bs = bernstein2(coeff)
        assert min(bs) >= 0, (n, a, s, coeff, bs)
        minima[kind].extend(bs)
    # Acceptance cancellation checked without conditioning on acceptance.
    for parent in range(n+1):
        assert sum(mutation(n)[parent][z]*pair.r[z]*2/pair.r[z]
                   for z in range(n+1)) == 2
    return dict(n=n, a=a, closed_in_actual_T2=closed_pair(n, a),
                states=len(pair.states), phase_identities=2*len(pair.D),
                bernstein_coefficients=3*len(pair.states),
                min_D_bernstein=str(min(minima['D'])),
                min_S_bernstein=str(min(minima['S'])),
                min_A_bernstein=str(min(minima['A'])),
                max_active_increment=str(max(active_diff)),
                interval='0 <= p <= 1/6; inverse bounds require p < 1/6',
                exact_pass=True)


def rational_solve(matrix, rhs):
    """Independent fraction-free solve, followed by exact residual validation.

SymPy is used only as an integer linear-system engine, never for kernels.
"""
    from sympy import ZZ
    from sympy.polys.matrices import DomainMatrix
    aa, bb = [], []
    for a, b in zip(matrix, rhs):
        scale = lcm(*(F(x).denominator for x in a+b))
        aa.append([ZZ(F(x)*scale) for x in a])
        bb.append([ZZ(F(x)*scale) for x in b])
    A, B = DomainMatrix.from_list(aa, ZZ), DomainMatrix.from_list(bb, ZZ)
    num, den = A.solve_den(B, method='rref')
    assert A.matmul(num) == B*den
    out = [[F(int(v), int(den)) for v in row] for row in num.to_list()]
    return out


def pair_solve(n, a, p):
    pair = Pair(n, a)
    P = pair.sweep(p)
    D, S, G = pair.D, pair.S, pair.G
    sol = rational_solve([[F(i == j)-P[i].get(j, F(0)) for j in D] for i in D],
                         [[F(1)]+[P[i].get(g, F(0)) for g in G] for i in D])
    residence = {d: sol[k][0] for k, d in enumerate(D)}
    exitrow = {d: sol[k][1:] for k, d in enumerate(D)}
    assert all(sum(exitrow[d]) == 1 and min(exitrow[d]) >= 0 for d in D)
    dwell = {g: sum(P[g].get(d, F(0))*residence[d] for d in D) for g in G}
    trace = {g: {h: P[g].get(h, F(0))+sum(P[g].get(d, F(0))*exitrow[d][k]
                                      for d in D) for k, h in enumerate(G)} for g in G}
    assert all(sum(row.values()) == 1 and min(row.values()) >= 0 for row in trace.values())
    hs = rational_solve([[F(g == h)-trace[g][h] for h in S] for g in S],
                        [[1+dwell[g]] for g in S])
    transient = tuple(s for s in pair.states if s != pair.A)
    hd = rational_solve([[F(s == t)-P[s].get(t, F(0)) for t in transient] for s in transient],
                        [[F(1)] for s in transient])
    h = {s: hd[i][0] for i, s in enumerate(transient)}
    assert all(h[g] == hs[i][0] for i, g in enumerate(S))
    delta, eta = 1-6*p, (1-p)**2/(3*n)
    assert delta > 0
    assert all(residence[d] <= pair.V[0][d]/delta for d in D)
    assert max(dwell[g] for g in S) <= 4*p/delta
    assert dwell[pair.A] <= 2*p*p/delta
    assert max(h[s] for s in S) <= (1+4*p/delta)/eta
    assert all(P[s].get(pair.A, F(0)) >= eta for s in S)
    return dict(n=n, a=a, p=str(p), max_weighted_residence=str(max(dwell[g] for g in S)),
                residence_decimal=float(max(dwell[g] for g in S)),
                residence_bound=str(4*p/delta), aligned_weighted_residence=str(dwell[pair.A]),
                max_single_alignment=str(max(h[s] for s in S)),
                alignment_decimal=float(max(h[s] for s in S)), exact_schur_equals_direct=True), pair, P, residence


def full_tensor_rows(n, p, all_rows=False):
    targets = tuple(range(n+1))
    left = Pair(n, 0)
    LP = left.sweep(p)
    rest_targets = targets[2:]
    assert closed_pair(n, 0)
    starts = (product(range(n+1), repeat=n+1) if all_rows else
              (tuple(targets), (2,)+targets[1:], (n,)*2+(0,)*(n-1), (0,)*(n+1)))
    rest_cache = {}
    checked, entries = 0, 0
    for s in starts:
        rp = rest_cache.setdefault(s[2:], None)
        if rp is None:
            rp = sweep_row(n, rest_targets, s[2:], p)
            rest_cache[s[2:]] = rp
        direct = sweep_row(n, targets, s, p)
        tensor = {l+r: pl*pr for l, pl in LP[s[:2]].items() for r, pr in rp.items()}
        assert direct == tensor
        checked += 1
        entries += len(direct)
    return dict(n=n, p=str(p), selected_pair='0,1', population_rows=checked,
                population_entries=entries, rest_slots=len(rest_targets),
                rest_includes_orphan=(n % 2 == 0), exact_match=True)


def full_schur(n=3, p=F(1, 81)):
    """Exact complete-population solve and U-block elimination at n=3."""
    assert n == 3
    left, right = Pair(n, 0), Pair(n, 2)
    L, R = left.sweep(p), right.sweep(p)
    states = tuple(product(range(n+1), repeat=n+1))
    A = tuple(range(n+1))
    P = {s: {l+r: pl*pr for l, pl in L[s[:2]].items() for r, pr in R[s[2:]].items()}
         for s in states}
    U = tuple(s for s in states if s[:2] in left.D)
    W = tuple(s for s in states if s != A and s not in U)
    transient = U + W
    # Joint exit distribution, not just its row sums. A is an exit target.
    exits = W + (A,)
    print('full Schur: solving joint exit equations', flush=True)
    solution = rational_solve([[F(s == t)-P[s].get(t, F(0)) for t in U] for s in U],
                              [[F(1)]+[P[s].get(t, F(0)) for t in exits] for s in U])
    residence = {s: solution[k][0] for k, s in enumerate(U)}
    X = {s: {t: solution[k][j+1] for j, t in enumerate(exits)} for k, s in enumerate(U)}
    print('full Schur: joint exit solve complete', flush=True)
    assert all(sum(X[s].values()) == 1 and min(X[s].values()) >= 0 for s in U)
    _, _, _, local_residence = pair_solve(n, 0, p)
    assert all(residence[s] == local_residence[s[:2]] for s in U)
    dwell = {s: sum(P[s].get(t, F(0))*residence[t] for t in U) for s in W}
    traced = {s: {t: P[s].get(t, F(0))+sum(P[s].get(u, F(0))*X[u][t] for u in U)
                  for t in exits} for s in W}
    assert all(sum(row.values()) == 1 and min(row.values()) >= 0 for row in traced.values())
    # Solve the small-denominator original system with two rewards. Resolving
    # the already rational Schur matrix causes unnecessary integer growth.
    # The second reward deletes time in U, exactly the unit-reward trace.
    print('full Schur: checking against direct integer-cleared equations', flush=True)
    direct = rational_solve([[F(s == t)-P[s].get(t, F(0)) for t in transient] for s in transient],
                            [[F(1), F(s in W)] for s in transient])
    h = {s: direct[i][0] for i, s in enumerate(transient)}
    h_unit = {s: direct[i][1] for i, s in enumerate(transient)}
    print('full Schur: direct solve complete', flush=True)
    for s in W:
        assert h[s]-sum(traced[s][t]*h[t] for t in W) == 1+dwell[s]
        assert h_unit[s]-sum(traced[s][t]*h_unit[t] for t in W) == 1
    # R_D tensor I followed by the actual exit step evolves the rest ONCE.
    # It preserves row sums and the pair exit marginal, but is the wrong
    # joint exit law. Compare it explicitly; changed rest alone is not a test.
    u = (3, 3, 0, 0)
    changed = sum(prob for t, prob in X[u].items() if t[2:] != u[2:])
    assert changed > 0
    marginal = {g: sum(prob for t, prob in X[u].items() if t[:2] == g) for g in left.G}
    frozen = {t: marginal[t[:2]]*R[u[2:]].get(t[2:], F(0)) for t in exits}
    assert sum(frozen.values()) == 1
    frozen_tv = sum(abs(X[u][t]-frozen[t]) for t in exits)/2
    assert frozen_tv > 0
    corner = (2, 1, 2, 3)
    missing_time = h[corner] - h_unit[corner]
    assert missing_time > 0
    other_D = sum(prob for t, prob in traced[corner].items() if t[2:] in right.D)
    assert other_D > 0
    return dict(n=n, p=str(p), full_states=len(states), eliminated_states=len(U),
                retained_transient_states=len(W), exact_joint_exit_rows=len(U),
                exact_residence_equalities=len(U), exact_hitting_equalities=len(W),
                corner_mean=str(h[corner]), corner_mean_decimal=float(h[corner]),
                corner_bias_if_reward_omitted=str(missing_time),
                omitted_reward_bias_decimal=float(missing_time),
                changed_rest_exit_mass=str(changed), changed_rest_exit_decimal=float(changed),
                frozen_rest_exit_total_variation=str(frozen_tv),
                frozen_rest_exit_tv_decimal=float(frozen_tv),
                other_pair_D_exit_mass=str(other_D),
                other_pair_D_exit_mass_decimal=float(other_D),
                changed_rest_start=list(u), exact_pass=True)


def witnesses():
    pair, p = Pair(3, 2), F(1, 81)
    s, mid, e = (0, 0), (2, 0), (0, 0)
    reinfection = ((1-p)*pair.K[0][s][mid] * p*pair.J[1][mid][e])
    assert reinfection > 0
    # All aligned at midpoint, corrupted again at boundary.
    s, mid, end = (2, 0), pair.A, (2, 2)
    lost_alignment = (1-p)*pair.K[0][s][mid] * p*pair.J[1][mid][end]
    assert lost_alignment > 0
    # Even n last pair is fed by the orphan; clean orphan can repair its slot.
    n, state = 4, (2, 0, 4)
    row = attempt(n, (2, 3, 4), state, 4, neighbors(n, 4), False)
    orphan_repair = row[(2, 3, 4)]
    assert orphan_repair > 0 and not closed_pair(4, 2)
    return dict(repair_then_reinfection=str(reinfection),
                midpoint_alignment_then_corruption=str(lost_alignment),
                orphan_repairs_last_pair=str(orphan_repair))


def moment(n):
    if n < 3 or not n % 2:
        raise ValueError('odd n>=3 required')
    d = mutation(n)
    v, c = d[0][n], d[0][0]
    r = d[0][n-1] + v
    s, q = 1-r, 1-(1-r)**2
    entry = c*v*s
    lower, coarse = entry/q**2, F(n**n, 32*n**4)
    assert lower >= coarse
    return dict(n=n, entrance=str(entry), clean_escape=str(q),
                first_moment_path=str(entry/q), iterated_residence_path=str(lower),
                iterated_residence_decimal=float(lower), coarse=str(coarse))


def write_csv(path, rows):
    with path.open('w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)


def main(repo, out, skip_full=False):
    out.mkdir(parents=True, exist_ok=True)
    counts = {'literal_rows': 0}
    for n in (3, 4, 5):
        for a in range(n):
            pair = Pair(n, a)
            for donor in pair.targets:
                for active in (False, True):
                    for state in pair.states:
                        assert attempt(n, pair.targets, state, donor, pair.targets, active) == \
                            literal_attempt(n, pair.targets, state, donor, pair.targets, active)
                        counts['literal_rows'] += 1
    phases = [phase_certificate(n, a) for n in range(3, 9) for a in range(n)]
    write_csv(out/'phase.csv', phases)
    prior = repo/'research/reports/large-T-20261109/followup/round-0011'
    cells = []
    for old in csv.DictReader((prior/'schur.csv').open()):
        row, _, _, _ = pair_solve(int(old['n']), int(old['a']), F(old['p']))
        for key in ('max_weighted_residence', 'aligned_weighted_residence', 'max_single_alignment'):
            assert F(row[key]) == F(old[key]), (key, row, old)
        cells.append(row)
    write_csv(out/'pair.csv', cells)
    tensors = [full_tensor_rows(3, F(1, 81), all_rows=True), full_tensor_rows(4, F(1, 256))]
    write_csv(out/'tensor.csv', tensors)
    moments = [moment(n) for n in (3, 5, 9, 17, 33, 65)]
    write_csv(out/'moments.csv', moments)
    for old, row in zip(csv.DictReader((prior/'moments.csv').open()), moments):
        assert F(old['iterated_residence_lower']) == F(row['iterated_residence_path'])
    checks = dict(status='mechanically checked', arithmetic='exact rational; integer linear solves',
                  counts=counts, phase_pairs=len(phases),
                  phase_identities=sum(r['phase_identities'] for r in phases),
                  bernstein_coefficients=sum(r['bernstein_coefficients'] for r in phases),
                  independent_pair_solves=len(cells), published_rationals_matched=3*len(cells),
                  tensor=tensors, witnesses=witnesses(), scientific_trajectories=0, scientific_seeds=[])
    if not skip_full:
        checks['full_schur'] = full_schur()
    (out/'verification.json').write_text(json.dumps(checks, indent=2, sort_keys=True)+'\n')
    print(json.dumps({k: v for k, v in checks.items() if k != 'full_schur'}, sort_keys=True), flush=True)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--repo', type=Path, default=Path('.'))
    parser.add_argument('--out', type=Path, required=True)
    parser.add_argument('--skip-full', action='store_true', help='development only; not a complete audit')
    args = parser.parse_args()
    main(args.repo.resolve(), args.out.resolve(), args.skip_full)
