"""Exact deterministic checks of acceptance-weighted unseeded excursions.

No random sampling, Taylor expansion, scheduler change, or prior-round import.
Small kernels preserve shared observations. Floating linear solves only propose
rational vectors; exact Bellman residuals certify all reported intervals.
"""
from __future__ import annotations

import argparse
import csv
from fractions import Fraction as F
from functools import lru_cache
import itertools
import json
import math
from pathlib import Path

MAX_PHASE_STATES = 324


@lru_cache(None)
def neighbors(n, t, i):
    left = (t - 1) // 2 + int(t % 2 == 0 and i % 2 == 1)
    first = max(0, min(i - left, n + 1 - t))
    return tuple(range(first, first + t))


def literal_neighbors(n, t, i):
    out = [i]
    for d in range(1, n + 1):
        for sign in ((1, -1) if i % 2 == 0 else (-1, 1)):
            j = i + sign * d
            if 0 <= j <= n and len(out) < t:
                out.append(j)
    return tuple(sorted(out))


@lru_cache(None)
def mutation(n, x):
    counts = [0] * (n + 1)
    for down in range(x + 1):
        for up in range(n - x + 1):
            counts[x - down + up] += (math.comb(x, down) * math.comb(n-x, up)
                                      * (n-1)**(n-down-up))
    assert sum(counts) == n**n
    return tuple(F(v, n**n) for v in counts)


def mask_mutation(n, x):
    out = [F(0)] * (n + 1)
    base = (1 << x) - 1
    for mask in range(1 << n):
        out[(base ^ mask).bit_count()] += F((n-1)**(n-mask.bit_count()), n**n)
    return tuple(out)


@lru_cache(None)
def incoming(n, t, k):
    return tuple(i for i in range(n+1) if k in neighbors(n, t, i))


@lru_cache(None)
def degrees(n, t):
    difference = [0]*(n+2)
    for i in range(n+1):
        left = (t-1)//2 + int(t % 2 == 0 and i % 2 == 1)
        first = max(0,min(i-left,n+1-t))
        difference[first] += 1
        difference[first+t] -= 1
    out, running = [], 0
    for i in range(n+1):
        running += difference[i]
        out.append(running)
    return tuple(out)


@lru_cache(None)
def delta(n, t, p, k):
    return 1 - (degrees(n,t)[k] + 1) * p


@lru_cache(None)
def phase_correction(n, t, p, k, phase):
    """g(k)=0, g(a)=r*delta/m + p*external visits before next own turn."""
    d = delta(n, t, p, k)
    if d <= 0:
        raise ValueError('positive drift condition is required')
    r = (k - phase) % (n + 1)
    before = tuple((phase+j) % (n+1) for j in range(r))
    external = sum(k in neighbors(n, t, i) for i in before)
    return F(r, n+1)*d + p*external


def potential(n, t, p, k, w, phase):
    if w[k] == k:
        return F(0)
    return (n+1) / delta(n, t, p, k) * (
        1/mutation(n, w[k])[k] + phase_correction(n, t, p, k, phase))


def uniform_charge(n, t, p):
    dmax = max(degrees(n,t))
    d = 1 - (dmax+1)*p
    if d <= 0:
        return None
    return 2*(n+1)*p*(1-p)/d


def entry_charge(n, t, p, i, k, x):
    """Bound BEFORE drawing child/observation; units: future attempts."""
    assert k in neighbors(n, t, i)
    rho = sum(mutation(n, x)[y]*mutation(n, y)[k]
              for y in range(n+1) if y != k)
    g = phase_correction(n, t, p, k, (i+1) % (n+1))
    return (n+1)*p / delta(n, t, p, k) * (1-mutation(n, x)[k] + g*rho)


def step(n, t, p, w, i):
    """Unrestricted pinned kernel; one shared observation, at most one update."""
    row = {}
    for y, py in enumerate(mutation(n, w[i])):
        for z in range(n+1):
            pz = (1-p)*int(z == y) + p*mutation(n, y)[z]
            new = list(w)
            if z in neighbors(n, t, i):
                new[z] = y
            new = tuple(new)
            row[new] = row.get(new, F(0)) + py*pz
    assert sum(row.values()) == 1
    return {w: v for w, v in row.items() if v}


def advance(n, t, w, b, lo, hi, i, y, z):
    """Literal moving-reference cost comparisons, including pre-pinning."""
    lo, hi = min(lo, z), max(hi, z)
    w, b = list(w), list(b)
    for k in literal_neighbors(n, t, i):
        cost = lambda label: max(k*(hi-label), (n-k)*(label-lo))
        if cost(z) <= cost(b[k]):
            w[k], b[k] = y, z
    return tuple(w), tuple(b), lo, hi


def unseeded(w):
    return all(x != k for k, x in enumerate(w))


def polarized(n, t):
    assert t < n+1
    out = []
    for i in range(n+1):
        row = neighbors(n,t,i)
        out.append(n if n-row[-1] >= row[0] else 0)
    assert unseeded(out)
    return tuple(out)


def first_change(n, t, p, w):
    """Exact mean attempts to first true-weight change, from phase zero.

    Stop at the first change, even if later reinfection would return to w.
    No claim about boundary-state residence is made.
    """
    survival, numerator = F(1), F(0)
    rates = []
    for i in range(n+1):
        rate = F(0)
        for y, py in enumerate(mutation(n,w[i])):
            for k in neighbors(n,t,i):
                if y != w[k]:
                    rate += py*((1-p)*int(y == k)+p*mutation(n,y)[k])
        numerator += survival
        survival *= 1-rate
        rates.append(rate)
    return numerator/(1-survival), tuple(rates)


def unseeded_kernel(n, t, p):
    populations = list(itertools.product(*(tuple(x for x in range(n+1) if x != k)
                                          for k in range(n+1))))
    states = [(w, a) for w in populations for a in range(n+1)]
    if len(states) > MAX_PHASE_STATES:
        raise ValueError('phase-state cap exceeded')
    index = {s: j for j, s in enumerate(states)}
    rows = []
    for w, a in states:
        rows.append({index[(v, (a+1) % (n+1))]: q
                     for v, q in step(n, t, p, w, a).items() if unseeded(v)})
    return states, index, rows


def exact_solve(rows):
    """Independent Fraction Gaussian elimination, restricted to <=24 states."""
    size = len(rows)
    if size > 24:
        raise ValueError('exact dense solve cap exceeded')
    matrix = [[F(int(i == j))-rows[i].get(j, F(0)) for j in range(size)] + [F(1)]
              for i in range(size)]
    for k in range(size):
        pivot = next(i for i in range(k, size) if matrix[i][k])
        matrix[k], matrix[pivot] = matrix[pivot], matrix[k]
        scale = matrix[k][k]
        matrix[k] = [x/scale for x in matrix[k]]
        for i in range(size):
            if i != k and matrix[i][k]:
                scale = matrix[i][k]
                matrix[i] = [x-scale*y for x, y in zip(matrix[i], matrix[k])]
    return [row[-1] for row in matrix]


def certificate(rows):
    import numpy as np
    size = len(rows)
    matrix = np.eye(size)
    for i, row in enumerate(rows):
        for j, prob in row.items():
            matrix[i, j] -= float(prob)
    floats = np.linalg.solve(matrix, np.ones(size))
    # Fixed decimal rational rounding, not a claimed floating error estimate.
    values = [F(format(x, '.12f')) for x in floats]
    residual = [values[i]-sum(q*values[j] for j, q in row.items())
                for i, row in enumerate(rows)]
    low, high = min(residual), max(residual)
    assert low > 0 and all(v > 0 for v in values)
    return values, low, high


def write_csv(path, rows):
    with path.open('w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def finite_checks(out):
    out.mkdir(parents=True, exist_ok=True)
    counts = {}
    mask_checks = 0
    for n in range(2, 8):
        for x in range(n+1):
            assert mutation(n, x) == mask_mutation(n, x)
            mask_checks += 1
    counts['literal_mask_rows_n2_through7'] = mask_checks

    local = 0
    for n in range(2, 13):
        for p in (F(0), F(1, 64*n), F(1, 4*n)):
            for k in range(n+1):
                v = [F(0) if y == k else 1/mutation(n, y)[k] for y in range(n+1)]
                for x in range(n+1):
                    # External incoming proposal, with every possible incumbent.
                    for old in range(n+1):
                        drift = sum(mutation(n, x)[y] * ((1-p)*int(y == k)+p*mutation(n, y)[k])
                                    * (v[y]-v[old]) for y in range(n+1))
                        assert drift <= p
                        if x == old and x != k:
                            assert drift <= -(1-2*p)
                        local += 1
    counts['local_drift_cases_n2_through12'] = local

    phase_checks = 0
    for n in range(2, 33):
        for t in range(1, n+2):
            for i in range(n+1):
                assert neighbors(n,t,i) == literal_neighbors(n,t,i)
            for p in (F(1,64*n), F(1,4*n)):
                for k in range(n+1):
                    d = delta(n,t,p,k)
                    for a in range(n+1):
                        g = phase_correction(n,t,p,k,a)
                        nxt = phase_correction(n,t,p,k,(a+1) % (n+1))
                        drift = -(1-2*p) if a == k else p*int(k in neighbors(n,t,a))
                        assert 0 <= g <= 1-2*p
                        assert nxt-g+drift == -d/(n+1)
                        phase_checks += 1
    counts['phase_identities_n2_through32_all_T'] = phase_checks

    cert_rows, cell_rows, entrances = [], [], []
    sup_checks = entry_checks = gaussian_checks = 0
    for n in (2,3):
        for t in range(1,n+2):
            for p in (F(1,64*n), F(1,4*n)):
                states, index, rows = unseeded_kernel(n,t,p)
                values, low, high = certificate(rows)
                upper = [v/low for v in values]
                if t == n+1:
                    assert max(upper) <= 1/(1-p)
                if n == 2:
                    exact = exact_solve(rows)
                    for v, u in zip(exact, values):
                        assert u/high <= v <= u/low
                        gaussian_checks += 1
                for k in range(n+1):
                    phi = [potential(n,t,p,k,w,a) for w,a in states]
                    for r, row in enumerate(rows):
                        residual = phi[r]-sum(q*phi[j] for j,q in row.items())
                        assert residual >= 1
                        assert upper[r] <= phi[r]
                        sup_checks += 1
                for r,(w,a) in enumerate(states):
                    cert_rows.append(dict(n=n,T=t,p=str(p),weights=','.join(map(str,w)),phase=a,
                                          proposal=str(values[r])))
                worst = F(0)
                for k in range(n+1):
                    other = [tuple(x for x in range(n+1) if x != j) if j != k else (k,)
                             for j in range(n+1)]
                    for w in itertools.product(*other):
                        for i in incoming(n,t,k):
                            actual = F(0)
                            for y in range(n+1):
                                if y == k:
                                    continue
                                new = list(w)
                                new[k] = y
                                mass = p*mutation(n,w[i])[y]*mutation(n,y)[k]
                                actual += mass*upper[index[(tuple(new),(i+1) % (n+1))]]
                            bound = entry_charge(n,t,p,i,k,w[i])
                            assert actual <= bound <= uniform_charge(n,t,p)
                            ratio = actual/bound
                            worst = max(worst,ratio)
                            entry_checks += 1
                init = sum(math.prod(F(math.comb(n,x),2**n)*p*mutation(n,x)[k]
                                     for k,x in enumerate(w)) * upper[index[(w,0)]]
                           for w in dict.fromkeys(w for w,a in states))
                init_bound = (n+1)*p*(1-F(1,2**n))/delta(n,t,p,0)
                assert init <= init_bound
                cell_rows.append(dict(n=n,T=t,p=str(p),states=len(states),
                                      residual_min=str(low),residual_max=str(high),
                                      max_entry_bound_ratio=float(worst),
                                      init_cost_upper=str(init),init_bound=str(init_bound),
                                      max_mean_upper=float(max(upper))))
    counts['exact_supersolution_cases'] = sup_checks
    counts['last_correct_entrance_cases'] = entry_checks
    counts['independent_fraction_gaussian_values_n2'] = gaussian_checks
    counts['certified_cells'] = len(cell_rows)
    counts['certified_phase_states_total'] = len(cert_rows)
    write_csv(out/'certificates.csv',cert_rows)
    write_csv(out/'cells.csv',cell_rows)

    # Exhaust all stored-label vectors and enclosing references at n=2,3.
    # True weights do not affect acceptance, so one all-wrong vector suffices
    # to check which recipients change when full pinning first occurs.
    pin_checks = pin_events = 0
    for n in (2,3):
        target = tuple(range(n+1))
        w = tuple((k+1) % (n+1) for k in range(n+1))
        for b in itertools.product(range(n+1),repeat=n+1):
            if b == target:
                continue
            for lo in range(min(b)+1):
                for hi in range(max(b),n+1):
                    for t in range(1,n+2):
                        for i in range(n+1):
                            for z in range(n+1):
                                v,c,l,h = advance(n,t,w,b,lo,hi,i,(z+1)%(n+1),z)
                                pin_checks += 1
                                if c == target and l == 0 and h == n:
                                    missing = [k for k in range(n+1) if b[k] != k]
                                    assert missing == [z] and z in neighbors(n,t,i)
                                    assert all(v[k] == w[k] for k in range(n+1) if k != z)
                                    pin_events += 1
    counts['prepin_label_reference_proposals_n2_n3'] = pin_checks
    counts['fullpin_entrances_n2_n3'] = pin_events

    full_rows = 0
    for n in (2,3):
        for p in (F(1,8),F(1,2),F(3,4)):
            _,_,rows = unseeded_kernel(n,n+1,p)
            for row in rows:
                assert sum(row.values()) <= p
                full_rows += 1
    counts['full_communication_seed_hazards_including_large_p'] = full_rows

    # Phase/stopping counterexample: interior completion followed by reinfection.
    n,t = 6,5
    corner = (2,1,2,3,4,5,6)
    target = tuple(range(n+1))
    aligned,_,_,_ = advance(n,t,corner,target,0,n,1,0,0)
    reinfected,_,_,_ = advance(n,t,aligned,target,0,n,2,2,0)
    assert aligned == target and reinfected == corner
    witness = dict(n=n,T=t,start=corner,first=dict(breeder=1,child=0,observed=0),
                   middle=aligned,second=dict(breeder=2,child=2,observed=0),end=reinfected,
                   status='positive-probability partial-sweep path; no boundary stop in middle')
    (out/'witness.json').write_text(json.dumps(witness,indent=2)+'\n')

    # Formula table only, no simulated trajectories. Conditions checked exactly.
    formula_rows = []
    for n in (16,32,64,128,256,512,1024,4096):
        ts = sorted({3,math.ceil(math.log(n)),math.isqrt(n)+(math.isqrt(n)**2<n),n+1})
        for t in ts:
            for c in (F(1,64),F(1),F(2)):
                p = c/n
                dmax = max(degrees(n,t))
                d = 1-(dmax+1)*p
                charge = uniform_charge(n,t,p) if d > 0 else None
                formula_rows.append(dict(n=n,T=t,c=str(c),p=str(p),dmax=dmax,delta_min=str(d),
                                         charge_exact='' if charge is None else str(charge),
                                         charge='' if charge is None else float(charge),
                                         condition=d > 0))
    write_csv(out/'bounds.csv',formula_rows)
    counts['analytic_formula_cells'] = len(formula_rows)

    trap_rows = []
    composed_checks = 0
    for n in (3,4,6,8,16,24,32):
        ts = sorted({3,math.ceil(math.log(n)),math.isqrt(n)+(math.isqrt(n)**2<n)})
        for t in ts:
            if not 3 <= t < n+1:
                continue
            w = polarized(n,t)
            a = (n+2-t)//2
            for p in (F(0),F(1,64*n),F(1,n)):
                mean,rates = first_change(n,t,p,w)
                lower = F(math.factorial(a),1)/((1-p)+p*2**a)
                assert mean >= lower
                bound_rate = ((1-p)+p*2**a)/math.factorial(a)
                assert all(r <= bound_rate for r in rates)
                trap_rows.append(dict(n=n,T=t,p=str(p),a=a,weights=','.join(map(str,w)),
                                      first_change_attempts=str(mean),lower_attempts=str(lower),
                                      first_change_decimal=float(mean),lower_decimal=float(lower)))
        if n <= 8:
            flip = F(2*(n-1),n*n)
            for x in (0,n):
                for z in range(n+1):
                    composed = sum(mutation(n,x)[y]*mutation(n,y)[z] for y in range(n+1))
                    flips = z if x == 0 else n-z
                    direct = math.comb(n,flips)*flip**flips*(1-flip)**(n-flips)
                    assert composed == direct
                    composed_checks += 1
    write_csv(out/'traps.csv',trap_rows)
    counts['noisy_trap_formula_cells'] = len(trap_rows)
    counts['endpoint_composed_mutation_identities'] = composed_checks
    counts['maximum_phase_states_per_cell'] = MAX_PHASE_STATES
    counts['sampling']='none; deterministic enumeration and exact certificates'
    (out/'verification.json').write_text(json.dumps(counts,indent=2,sort_keys=True)+'\n')
    return counts


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--out',type=Path,required=True)
    args = parser.parse_args()
    print(json.dumps(finite_checks(args.out),indent=2,sort_keys=True))
