#!/usr/bin/env python3
"""Independent deterministic red-team audit; never runs trajectory sampling.

Small-state kernels use literal mutation masks and integer transition weights.
Floating linear solves only propose certificates; integer Bellman arithmetic
certifies all reported expectation intervals. Requires NumPy, one BLAS thread.
"""
import argparse
import csv
from fractions import Fraction as F
from itertools import product
import json
from math import factorial, lcm
import os
from pathlib import Path
for key in ('OPENBLAS_NUM_THREADS', 'OMP_NUM_THREADS', 'MKL_NUM_THREADS',
            'VECLIB_MAXIMUM_THREADS', 'NUMEXPR_NUM_THREADS'):
    os.environ[key] = '1'

SCALE = 10**10


def recipients(n, t, i):
    order = [i]
    for distance in range(1, n+1):
        for side in ((1, -1) if i % 2 == 0 else (-1, 1)):
            k = i + side*distance
            if 0 <= k <= n:
                order.append(k)
    return tuple(order[:t])


def mask_kernel(n):
    den = n**n
    law = []
    for w in range(n+1):
        genome = (1,)*w + (0,)*(n-w)
        row = [0]*(n+1)
        for mask in product((0, 1), repeat=n):
            child = sum(a ^ b for a, b in zip(genome, mask))
            row[child] += (n-1)**(n-sum(mask))
        assert sum(row) == den
        law.append(row)
    return law, den


def literal_replace(w, n, t, i, child, observed):
    # Recompute scalar comparisons, rather than assume the pinned shortcut.
    result = list(w)
    for k in recipients(n, t, i):
        proposed = max(k*(n-observed), (n-k)*observed)
        stored = k*(n-k)
        if proposed <= stored:
            result[k] = child
    return tuple(result)


def transitions(n, t, p):
    states = list(product(range(n+1), repeat=n+1))
    index = {state:i for i, state in enumerate(states)}
    d, md = mask_kernel(n)
    denominator = p.denominator*md*md
    steps = []
    for i in range(n+1):
        rows = []
        for w in states:
            row = {}
            for child, observed in product(range(n+1), repeat=2):
                mass = d[w[i]][child] * ((p.denominator-p.numerator)*md*int(child == observed)
                                         + p.numerator*d[child][observed])
                if mass:
                    new = literal_replace(w, n, t, i, child, observed)
                    j = index[new]
                    row[j] = row.get(j, 0) + mass
            assert sum(row.values()) == denominator
            rows.append(tuple(sorted(row.items())))
        steps.append(rows)
    return states, index, steps, denominator


def exact_back(steps, den, nums):
    """Apply an entire un-killed sweep; numerator denominator multiplies by den^m."""
    result = list(nums)
    for rows in reversed(steps):
        result = [sum(mass*result[j] for j, mass in row) for row in rows]
    return result


def reward_nums(states, steps, den, own_only):
    # One sweep's expected number of wrong pre-attempt donor-1 states.
    result, denominator = [0]*len(states), 1
    for i in reversed(range(len(steps))):
        result = [sum(mass*result[j] for j, mass in row) for row in steps[i]]
        denominator *= den
        if not own_only or i == 1:
            result = [v + denominator*int(w[1] != 1) for v, w in zip(result, states)]
    return result


def boundary_matrix(steps, den):
    import numpy as np
    result = np.eye(len(steps[0]))
    for rows in reversed(steps):
        new = np.zeros_like(result)
        for i, row in enumerate(rows):
            for j, mass in row:
                new[i] += (mass/den)*result[j]
        result = new
    assert np.max(np.abs(result.sum(axis=1)-1)) < 1e-12
    return result


def time_certificate(states, steps, den, matrix, event):
    import numpy as np
    target = [event(w) for w in states]
    ids = [i for i, hit in enumerate(target) if not hit]
    vector = np.zeros(len(states))
    vector[ids] = np.linalg.solve(np.eye(len(ids))-matrix[np.ix_(ids, ids)], np.ones(len(ids)))
    nums = [int(round(float(v)*SCALE)) for v in vector]
    assert all(nums[i] > 0 for i in ids)
    propagated = exact_back(steps, den, nums)
    factor = den**len(steps)
    drift = [F(nums[i]*factor-propagated[i], SCALE*factor) for i in ids]
    dmin, dmax = min(drift), max(drift)
    assert dmin > 0
    lower = [F(v, SCALE)/dmax for v in nums]
    upper = [F(v, SCALE)/dmin for v in nums]
    return dict(nums=nums, ids=ids, lower=lower, upper=upper, dmin=dmin, dmax=dmax)


def reward_certificate(states, steps, den, matrix, times, own_only):
    import numpy as np
    ids = times['ids']
    factor = den**len(steps)
    reward = reward_nums(states, steps, den, own_only)
    vector = np.zeros(len(states))
    vector[ids] = np.linalg.solve(np.eye(len(ids))-matrix[np.ix_(ids, ids)],
                                  np.array([float(F(reward[i], factor)) for i in ids]))
    nums = [int(round(float(v)*SCALE)) for v in vector]
    propagated = exact_back(steps, den, nums)
    residual = max(abs(F(nums[i]*factor-propagated[i]-SCALE*reward[i], SCALE*factor)) for i in ids)
    lower = [max(F(0), F(v, SCALE)-residual*times['upper'][i]) for i, v in enumerate(nums)]
    upper = [F(v, SCALE)+residual*times['upper'][i] for i, v in enumerate(nums)]
    return dict(nums=nums, lower=lower, upper=upper, residual=residual)


def solve_exact(a, b):
    # Tiny local Q systems only; full-state expectations use certificates.
    rows = [list(row)+[rhs] for row, rhs in zip(a, b)]
    for j in range(len(rows)):
        pivot = next(i for i in range(j, len(rows)) if rows[i][j])
        rows[j], rows[pivot] = rows[pivot], rows[j]
        q = rows[j][j]
        rows[j] = [x/q for x in rows[j]]
        for i in range(len(rows)):
            if i != j:
                q = rows[i][j]
                rows[i] = [x-q*y for x, y in zip(rows[i], rows[j])]
    return [row[-1] for row in rows]


def local_potentials(n, p):
    d, md = mask_kernel(n)
    all_h = []
    for k in range(n+1):
        ids = [i for i in range(n+1) if i != k]
        q = [[F(d[i][j], md)*((1-p)*int(j == k)+p*F(d[j][k], md)) if i != j else F(0)
              for j in range(n+1)] for i in range(n+1)]
        for i in range(n+1):
            q[i][i] = 1-sum(q[i])
        vals = solve_exact([[F(i == j)-q[i][j] for j in ids] for i in ids], [F(1)]*n)
        h = [F(0)]*(n+1)
        for i, v in zip(ids, vals):
            h[i] = v
        all_h.append(h)
    return all_h


def constants(n, t, p):
    a = p/(1-2*p)
    incoming = [[i for i in range(n+1) if k in recipients(n, t, i)] for k in range(n+1)]
    d0, d1 = len(incoming[0]), len(incoming[1])
    beta, immigration = (t-1)*a, (n+1)*t*a
    result = dict(a=a, beta=beta, d0=d0, d1=d1, Aplus=((n+1)*t-d0)*a)
    if beta < 1:
        exponent = immigration/((1-beta)*(1-p))
        # An exact LOWER bound on the theorem's constant. Passing this stronger
        # inequality certifies the comparison without trusting floating exp().
        exp_lower = sum(exponent**j/factorial(j) for j in range(41))
        result['C_lower'] = exp_lower/(1-beta)
    if t >= 2 and d1*a < 1:
        qstar = (1-p)**(d0-1)*F(1,n)*F(n-1,n)**(n-1)
        result['B0'] = 1/((1-d1*a)*qstar)
    if t >= 2:
        protected = set().union(*(set(incoming[k]) for k in incoming[0]))
        failure = F(1)
        for i in incoming[0]:
            w = 2 if i == 0 else i
            failure *= 1-F(1,n)**w*F(n-1,n)**(n-w)
        result['lower'] = 1/(1-(1-p)**len(protected)*failure)
    return result


def posterior_witness():
    n, p, x, k = 3, F(1,192), 2, 0
    d, md = mask_kernel(n)
    accepted = sum(F(d[x][j],md)*((1-p)*int(j == k)+p*F(d[j][k],md)) for j in range(n+1))
    erroneous = sum(F(d[x][j],md)*p*F(d[j][k],md) for j in range(n+1) if j != k)
    assert erroneous/accepted > p
    return dict(n=n, p=str(p), parent=x, target=k,
                accepted_probability=str(accepted), erroneous_and_accepted=str(erroneous),
                wrong_given_accepted=str(erroneous/accepted),
                inflation_over_p=str(erroneous/accepted/p), status='exact; contradicted naive posterior <= p')


def find_boundary_witness():
    # Breadth-first search, retaining the shortest path to each (phase,state,
    # has-ever-been-aligned) until the FIRST sweep boundary. Lexicographic outcomes.
    for n in range(3, 5):
        for t in range(2, n+2):
            initial = (2,)+tuple(range(1,n+1))
            frontier = {(initial, False): []}
            for breeder in range(n+1):
                next_frontier = {}
                for (w, seen), path in sorted(frontier.items()):
                    for child, observed in product(range(n+1), repeat=2):
                        new = literal_replace(w,n,t,breeder,child,observed)
                        aligned = new == tuple(range(n+1))
                        key = (new,seen or aligned)
                        if key not in next_frontier:
                            next_frontier[key] = path+[(breeder,w[breeder],child,observed,new)]
                frontier = next_frontier
            for (w,seen),path in sorted(frontier.items()):
                if seen and sum(k != v for k,v in enumerate(w)) == 1:
                    p, probability = F(1,64*n), F(1)
                    d, md = mask_kernel(n)
                    for i,x,j,k,new in path:
                        probability *= F(d[x][j],md)*((1-p)*int(j==k)+p*F(d[j][k],md))
                    assert probability > 0
                    return dict(n=n,T=t,p=str(p),initial=initial,path=path,
                                probability=str(probability), final=w,
                                status='exact positive-probability witness; not a counterexample to the boundary theorem')
    raise AssertionError('Expected a boundary-vs-interior counterexample')


def write_csv(path, rows):
    with path.open('w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0]), lineterminator='\n')
        writer.writeheader()
        writer.writerows(rows)


def main(out):
    out.mkdir(parents=True, exist_ok=True)
    rows, certificates, counts = [], [], dict(cells=0, state_cells=0, transition_rows=0,
        simultaneous_inequalities=0, endpoint_inequalities=0, occupation_inequalities=0,
        corner_lower_inequalities=0, corner_upper_inequalities=0)
    for n in (2,3):
        for p in (F(0), F(1,64*n), F(1,4*n)) + ((F(1,n),) if n == 3 else ()):
            for t in range(1,n+2):
                states,index,steps,den = transitions(n,t,p)
                matrix = boundary_matrix(steps,den)
                exact = time_certificate(states,steps,den,matrix,lambda w: all(i==v for i,v in enumerate(w)))
                endpoint = time_certificate(states,steps,den,matrix,lambda w: w[0]==0)
                own = reward_certificate(states,steps,den,matrix,endpoint,True)
                all_attempts = reward_certificate(states,steps,den,matrix,endpoint,False)
                h, bound = local_potentials(n,p), constants(n,t,p)
                corner = index[(2,)+tuple(range(1,n+1))]
                if p == 0:
                    # Exact zero-noise supersolution, including equality cases
                    # that a rounded solve cannot separate from its error bar.
                    potentials = [sum(h[k][v] for k,v in enumerate(w)) for w in states]
                    hd = lcm(*(v.denominator for v in potentials))
                    hn = [int(v*hd) for v in potentials]
                    hp = exact_back(steps,den,hn)
                    factor = den**len(steps)
                    assert all(hn[i]*factor-hp[i] >= hd*factor for i in exact['ids'])
                    assert all(states[j][1] == 1 for rows in steps for i,row in enumerate(rows)
                               if states[i][1] == 1 for j,mass in row if mass)
                for pos,w in enumerate(states):
                    potential = sum(h[k][v] for k,v in enumerate(w))
                    if 'C_lower' in bound:
                        # In the noiseless case T=1, equality can be approached;
                        # exact rational residual certificates still settle n=2/3.
                        if p:
                            assert exact['upper'][pos] <= bound['C_lower']*potential, (n,t,p,w)
                        counts['simultaneous_inequalities'] += 1
                    if w[1] == 1 and pos in endpoint['ids']:
                        for reward, multiplier in ((own,bound['d1']*bound['a']),
                                                   (all_attempts,(n+1)*bound['d1']*(bound['a']+p))):
                            if p:
                                assert reward['upper'][pos] <= multiplier*endpoint['lower'][pos], (n,t,p,w,'occupation')
                            counts['occupation_inequalities'] += 1
                    certificates.append(dict(n=n,T=t,p=str(p),state=' '.join(map(str,w)),
                        time_num=exact['nums'][pos],endpoint_num=endpoint['nums'][pos],
                        own_num=own['nums'][pos],occupation_num=all_attempts['nums'][pos],scale=SCALE))
                if 'B0' in bound:
                    assert endpoint['upper'][corner] <= bound['B0']
                    counts['endpoint_inequalities'] += 1
                if 'lower' in bound:
                    # At zero noise the geometric lower bound is exact; compare
                    # to the certified interval instead of demand rounding away.
                    assert exact['upper'][corner] >= bound['lower']
                    if p:
                        assert exact['lower'][corner] >= bound['lower']
                    counts['corner_lower_inequalities'] += 1
                if 'C_lower' in bound and 'B0' in bound:
                    assert exact['upper'][corner] <= bound['B0']*(1+bound['C_lower']*bound['Aplus'])
                    counts['corner_upper_inequalities'] += 1
                rows.append(dict(n=n,T=t,p=str(p),states=len(states),
                    simultaneous_lower=str(exact['lower'][corner]),simultaneous_upper=str(exact['upper'][corner]),
                    simultaneous_mid=float((exact['lower'][corner]+exact['upper'][corner])/2),
                    endpoint_lower=str(endpoint['lower'][corner]),endpoint_upper=str(endpoint['upper'][corner]),
                    endpoint_mid=float((endpoint['lower'][corner]+endpoint['upper'][corner])/2),
                    own_bad_lower=str(own['lower'][corner]),own_bad_upper=str(own['upper'][corner]),
                    occupation_lower=str(all_attempts['lower'][corner]),occupation_upper=str(all_attempts['upper'][corner]),
                    time_drift_min=str(exact['dmin']),time_drift_max=str(exact['dmax']),
                    endpoint_drift_min=str(endpoint['dmin']),endpoint_drift_max=str(endpoint['dmax']),
                    own_residual=str(own['residual']),occupation_residual=str(all_attempts['residual']),
                    candidate_endpoint_upper=float(bound['B0']) if 'B0' in bound else '',
                    candidate_simultaneous_upper_lower_approx=float(bound['B0']*(1+bound['C_lower']*bound['Aplus']))
                        if 'C_lower' in bound and 'B0' in bound else '',
                    candidate_conditions=bool('C_lower' in bound and (t==1 or 'B0' in bound))))
                counts['cells'] += 1
                counts['state_cells'] += len(states)
                counts['transition_rows'] += len(states)*(n+1)
    t2 = next(r for r in rows if r['n']==3 and r['T']==2 and r['p']=='1/192')
    t3 = next(r for r in rows if r['n']==3 and r['T']==3 and r['p']=='1/192')
    gap_low = F(t3['simultaneous_lower'])-F(t2['simultaneous_upper'])
    gap_high = F(t3['simultaneous_upper'])-F(t2['simultaneous_lower'])
    assert gap_low > 0
    witnesses = dict(acceptance_bias=posterior_witness(),boundary=find_boundary_witness(),
        expected_monotonicity=dict(n=3,p='1/192',T_small=2,T_large=3,
            donor_sets={str(t):[i for i in range(4) if 0 in recipients(3,t,i)] for t in (2,3)},
            larger_minus_smaller_sweeps_lower=str(gap_low),
            larger_minus_smaller_sweeps_upper=str(gap_high),
            gap_mid=float((gap_low+gap_high)/2),
            status='contradicted universal nonincreasing expected supplied-corner time in T; deterministic certified intervals'))
    write_csv(out/'expectations.csv', rows)
    write_csv(out/'certificates.csv', certificates)
    summary = dict(status='mechanically checked; no counterexample to the stated finite bounds',
                   counts=counts, scientific_trajectories=0, scientific_seeds=[], witnesses=witnesses,
                   arithmetic='Integer transition weights and exact Fraction Bellman certificates; NumPy only proposes values',
                   scale=SCALE, maximum_time_interval_width=max(float(F(r['simultaneous_upper'])-F(r['simultaneous_lower'])) for r in rows))
    (out/'verification.json').write_text(json.dumps(summary,indent=2,sort_keys=True)+'\n')
    print(json.dumps(summary,sort_keys=True))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out',type=Path,required=True)
    main(parser.parse_args().out)
