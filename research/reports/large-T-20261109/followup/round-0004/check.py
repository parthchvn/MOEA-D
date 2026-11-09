#!/usr/bin/env python3
"""Deterministic proof checks. No simulator, sampling, or scientific seeds.

Run from the repository root: python deliverables/check.py --out /tmp/corner-check
Uses exact fractions for the kernels, potentials, and renewal identity.
"""
import argparse
import csv
from fractions import Fraction as F
from itertools import product
import json
from math import comb, exp
from pathlib import Path


def mutation(n):
    """Independent binomial removal/addition, exact integer numerator."""
    den = n ** n
    return [[sum(comb(i, a) * comb(n-i, u) * (n-1)**(n-a-u)
                 for a in range(i+1) for u in range(n-i+1)
                 if i-a+u == j) / F(den)
             for j in range(n+1)] for i in range(n+1)]


def multiply(a, b):
    return [[sum(x*y for x, y in zip(row, col)) for col in zip(*b)] for row in a]


def solve(a, b):
    """Exact Gaussian elimination, independent of numerical linear algebra."""
    a = [list(row)+[rhs] for row, rhs in zip(a, b)]
    n = len(a)
    for i in range(n):
        pivot = next(k for k in range(i, n) if a[k][i])
        a[i], a[pivot] = a[pivot], a[i]
        scale = a[i][i]
        a[i] = [x/scale for x in a[i]]
        for k in range(n):
            if k != i and a[k][i]:
                scale = a[k][i]
                a[k] = [x-scale*y for x, y in zip(a[k], a[i])]
    return [row[-1] for row in a]


def noise(d, p):
    return [[p*x+(1-p)*int(i == j) for j, x in enumerate(row)]
            for i, row in enumerate(d)]


def pinned(d, p, k):
    obs = noise(d, p)
    q = [[d[i][j]*obs[j][k] if i != j else F(0)
          for j in range(len(d))] for i in range(len(d))]
    for i in range(len(d)):
        q[i][i] = 1-sum(q[i])
    return q


def repair(d, p, k):
    q = pinned(d, p, k)
    ids = [i for i in range(len(d)) if i != k]
    answer = solve([[F(i == j)-q[i][j] for j in ids] for i in ids],
                   [F(1)]*len(ids))
    h = [F(0)]*len(d)
    for i, value in zip(ids, answer):
        h[i] = value
    return h


def neighbors(n, t, i):
    """Literal alternating choices, not the native interval implementation."""
    out = [i]
    delta = 1
    sign = 1 if i % 2 == 0 else -1
    while len(out) < t:
        for s in (sign, -sign):
            k = i+s*delta
            if 0 <= k <= n and len(out) < t:
                out.append(k)
        delta += 1
    return out


def incoming(n, t, k):
    return [i for i in range(n+1) if k in neighbors(n, t, i)]


def advance(weights, n, t, breeder, child, obs):
    result = list(weights)
    if obs in neighbors(n, t, breeder):
        result[obs] = child
    return tuple(result)


def coupled_step(weights, particles, tags, n, t, breeder, proposals):
    """One exact domination step. The caller supplies EVERY fresh outcome.

    particles: id -> (site, weight); tags: actual wrong site -> particle id.
    proposals keys are 'base' and the ids present at breeder BEFORE the turn.
    New own-site base particles wait until the next sweep.
    """
    particles, tags = dict(particles), dict(tags)
    old = [key for key, (site, _) in particles.items() if site == breeder]
    selected = tags.get(breeder, 'base')
    child, obs = proposals[selected]
    actual = advance(weights, n, t, breeder, child, obs)
    created = {}
    for source in ['base']+old:
        j, k = proposals[source]
        if source != 'base' and k == breeder:
            if j == breeder:
                del particles[source]
            else:
                particles[source] = (breeder, j)
        if k in neighbors(n, t, breeder) and j != k:
            if source != 'base' and k == breeder:
                created[source] = source
            else:
                serial = 0
                while ('birth', serial) in particles:
                    serial += 1
                key = ('birth', serial)
                particles[key] = (k, j)
                created[source] = key
    if obs in neighbors(n, t, breeder):
        if child == obs:
            tags.pop(obs, None)
        else:
            tags[obs] = created[selected]
    assert all((k in tags) == (w != k) for k, w in enumerate(actual))
    assert all(particles[key] == (k, actual[k]) for k, key in tags.items())
    return actual, particles, tags


def check_coupling():
    # Every population, T, breeder, and fresh proposal at n=2, with/without
    # one extra untagged particle at the breeder. Includes wrong parents,
    # ignored base draws, own-site births, external replacement, and repairs.
    n, count = 2, 0
    for weights in product(range(n+1), repeat=n+1):
        for t in range(1, n+2):
            for i in range(n+1):
                for extra in [None]+[j for j in range(n+1) if j != i]:
                    particles = {k: (k, w) for k, w in enumerate(weights) if w != k}
                    tags = {k: k for k, w in enumerate(weights) if w != k}
                    if extra is not None:
                        particles['extra'] = (i, extra)
                    sources = ['base']+[key for key, (k, _) in particles.items() if k == i]
                    outcomes = list(product(range(n+1), repeat=2))
                    for draws in product(outcomes, repeat=len(sources)):
                        coupled_step(weights, particles, tags, n, t, i, dict(zip(sources, draws)))
                        count += 1
    return count


def check_renewal():
    cases = 0
    # Immigration length: number of boundaries occupied from its birth sweep.
    # State r at a boundary evolves to max(r-1, new_length).
    for probs in ([F(3, 4), F(1, 4)],
                  [F(1, 2), F(1, 4), F(1, 4)],
                  [F(1, 3), F(1, 6), F(1, 6), F(1, 3)]):
        for initial in range(1, 9):
            m = max(initial, len(probs)-1)
            q = [F(1)]
            for time in range(1, m+1):
                q.append(q[-1]*sum(probs[:time]))
            q_inf = q[-1]
            a = [[F(i == j)-sum(prob for length, prob in enumerate(probs)
                               if max(i-1, length) == j)
                  for j in range(1, m+1)] for i in range(1, m+1)]
            hit = solve(a, [F(1)]*m)[initial-1]
            assert hit == sum(q[:initial])/q_inf
            assert hit <= initial/q_inf
            cases += 1
    return cases


def analytic_bounds():
    """Illustrate formulas only: no trajectories, fitting, or estimated means."""
    rows = []
    for n, t, c in product((64, 512), (3, 23), (F(1, 64), F(1))):
        p = c/n
        a = p/(1-2*p)
        d0, d1 = incoming(n, t, 0), incoming(n, t, 1)
        later = len(d0)-2
        beta = (t-1)*a
        assert beta < 1 and len(d1)*a < 1
        qstar = (1-p)**(later+1)*F(1, n)*F(n-1, n)**(n-1)
        b0 = 1/((1-len(d1)*a)*qstar)
        immigration = (n+1)*t*a
        rest = ((n+1)*t-len(d0))*a
        cleanup = exp(float(immigration/((1-beta)*(1-p))))/float(1-beta)
        protected = set().union(*(set(incoming(n, t, k)) for k in d0))
        failure = F(1)
        for i in d0:
            w = 2 if i == 0 else i
            failure *= 1-F(1, n)**w*F(n-1, n)**(n-w)
        lower = 1/(1-(1-p)**len(protected)*failure)
        rows.append(dict(n=n, T=t, c=str(c), p=str(p), d0=len(d0), d1=len(d1),
                         later_donors=later, protected_breeders=len(protected),
                         endpoint_mean_sweeps_upper=float(b0),
                         donor_bad_own_turns_before_endpoint_upper=float(len(d1)*a*b0),
                         donor_bad_sweep_equivalents_before_endpoint_upper=float(len(d1)*(a+p)*b0),
                         simultaneous_mean_sweeps_lower=float(lower),
                         candidate_simultaneous_mean_sweeps_upper=float(b0)*(1+cleanup*float(rest)),
                         status='analytic bounds, rounded; no empirical observations'))
    return rows


def main(out):
    out.mkdir(parents=True, exist_ok=True)
    rows, comparisons, kernel_count = [], 0, 0
    for n in range(2, 9):
        d = mutation(n)
        assert all(sum(row) == 1 for row in d)
        dd = multiply(d, d)
        rate = F(2*(n-1), n*n)
        for i in range(n+1):
            assert dd[i][0] == rate**i*(1-rate)**(n-i)
            for j in range(n+1):
                assert comb(n, i)*d[i][j] == comb(n, j)*d[j][i]
        for p in dict.fromkeys((F(0), F(1, 64*n), F(1, n), F(1, 4), F(2, 5))):
            if p >= F(1, 2):
                continue
            a = p/(1-2*p)
            obs = noise(d, p)
            for k in range(n+1):
                q, h = pinned(d, p, k), repair(d, p, k)
                kernel_count += 1
                for i in range(n+1):
                    drift = h[i]-sum(q[i][j]*h[j] for j in range(n+1))
                    if i != k:
                        assert drift == 1
                        assert 0 < h[i] <= 1/((1-2*p)*d[i][k])
                    assert obs[i][k]*h[i] <= a
                    injection = sum(d[i][j]*obs[j][k]*h[j] for j in range(n+1))
                    assert injection <= a
                    comparisons += 4 if i != k else 2
                    # Exact rows allow checking every state, not just extrema.
                    rows.append(dict(n=n, p=str(p), target=k, parent=i,
                                     repair=str(h[i]), injection=str(injection),
                                     injection_bound=str(a)))
                pi = obs[k]
                for j in range(n+1):
                    assert sum(pi[i]*q[i][j] for i in range(n+1)) == pi[j]
                lam = sum(q[k][j]*h[j] for j in range(n+1))
                assert lam == (1-obs[k][k])/obs[k][k]
                comparisons += n+2
    geometry = 0
    for n in range(2, 65):
        for t in range(1, n+2):
            d0, d1 = incoming(n, t, 0), incoming(n, t, 1)
            assert len(d1) <= 2*t-1
            if t >= 2:
                assert 0 in d0 and 1 in d0
            for i in range(n+1):
                first = max(0, min(n+1-t, i-(t-1)//2-int(t % 2 == 0 and i % 2 == 1)))
                assert set(neighbors(n, t, i)) == set(range(first, first+t))
            geometry += 1
    # Published reinfection and new donor-persistence witness, all pinned.
    w = tuple([2]+list(range(1, 7)))
    path = [w]
    for i, j, k in [(0, 2, 2), (1, 0, 0), (2, 1, 0),
                    (3, 3, 3), (4, 4, 4), (5, 5, 5), (6, 6, 6)]:
        w = advance(w, 6, 5, i, j, k)
        path.append(w)
    assert path[2] == tuple(range(7)) and w == (1, 1, 2, 3, 4, 5, 6)
    donor = advance((2, 1, 2, 3), 3, 3, 1, 0, 1)
    assert donor[1] == 0
    bounds = analytic_bounds()
    checks = dict(status='pass', scientific_trajectories=0, random_draws=0,
                  arithmetic='fractions.Fraction; exact equalities and inequalities',
                  pinned_kernels=kernel_count, kernel_comparisons=comparisons,
                  rows=len(rows), neighborhood_cells=geometry,
                  coupling_cases=check_coupling(), renewal_cases=check_renewal(),
                  analytic_bound_rows=len(bounds),
                  reinfection_path=path, donor_corruption_state=donor,
                  scope='Finite checks do not establish the infinite-particle construction or its asymptotics.')
    with (out/'kernels.csv').open('w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0]), lineterminator='\n')
        writer.writeheader()
        writer.writerows(rows)
    with (out/'bounds.csv').open('w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=list(bounds[0]), lineterminator='\n')
        writer.writeheader()
        writer.writerows(bounds)
    (out/'verification.json').write_text(json.dumps(checks, indent=2, sort_keys=True)+'\n')
    print(json.dumps(checks, sort_keys=True))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out', type=Path, required=True)
    main(parser.parse_args().out)
