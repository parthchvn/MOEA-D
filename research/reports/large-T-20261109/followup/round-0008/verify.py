#!/usr/bin/env python3
"""Deterministic cross-checks and proof-inequality searches, without RNG use."""
import argparse
import csv
from fractions import Fraction as F
import json
from pathlib import Path
import sys
from bounds import (Restricted, dyadic_below, local_reversibility, norm_second, orphan,
                    polynomial, q_value, remainder, sign_window)
from second import Response


def csv_rows(path):
    with path.open() as stream:
        return list(csv.DictReader(stream))


def verify(repo, bundle, out):
    exact = csv_rows(bundle/'coefficients.csv')
    full = json.loads((bundle/'oracle.json').read_text())['full_state_results']
    for row in exact:
        other = next(r for r in full if r['n'] == int(row['n']) and r['T'] == int(row['T']))
        for key in ('mean0', 'first', 'second', 'between', 'within'):
            assert F(row[key]) == F(other[key])
        assert int(row['maximum_clean_errors']) == 3
        assert int(row['maximum_first_errors']) == 2
    r6 = repo/'research/reports/large-T-20261109/followup/round-0006'
    previous = csv_rows(r6/'components.csv')
    for row in exact:
        assert F(row['first']) == sum(F(r['coefficient']) for r in previous
                                     if r['n'] == row['n'] and r['T'] == row['T'])
    numeric = csv_rows(bundle/'numeric.csv')
    old = {int(r['n']): r for r in csv_rows(r6/'coefficients.csv')}
    numeric_first_matches = 0
    exact_float_error = 0.0
    for row in numeric:
        n = int(row['n'])
        if n in old:
            assert abs(float(row['first_decimal'])-float(old[n]['gap_sweeps'])) <= 1e-8*max(1, abs(float(old[n]['gap_sweeps'])))
            numeric_first_matches += 1
        if n in (3, 4):
            a, b = [r for r in exact if int(r['n']) == n]
            gap = F(b['second'])-F(a['second'])
            error = abs(float(row['second_decimal'])-float(gap))
            exact_float_error = max(exact_float_error, error)
            assert error < 1e-10
        assert abs(float(row['second_decimal'])) <= float(polynomial(n)['gap'])

    counts = dict(regular_clean_means=0, orphan_suffix_differences=0,
                  orphan_response_matches=0, local_balance_identities=0,
                  mixed_forcings=0, mixed_responses=0)
    maximum_regular_ratio = F(0)
    for n in range(3, 11):
        for t in (2, 3):
            solver = Response(n, t)
            for k in range(n+1):
                if t == 2 and n % 2 == 0 and k == n:
                    continue
                for y in range(n+1):
                    for base in ((), solver.corner):
                        e = solver.put(base, k, y)
                        h = solver.h(e)
                        assert h <= 6*n
                        maximum_regular_ratio = max(maximum_regular_ratio, h/(6*n))
                        counts['regular_clean_means'] += 1
            solver.clear()

    orphan_rows = []
    for n in (4, 6, 8, 10, 12):
        value = orphan(n)
        solver = Restricted(n, 2, [n])
        result = solver.coefficients()
        assert value['first'] == F(result['first'])
        assert value['second'] == F(result['second'])
        counts['orphan_response_matches'] += 2
        counts['local_balance_identities'] += local_reversibility(n)
        orphan_rows.append(dict(n=n, first=str(value['first']), second=str(value['second']),
                                second_decimal=float(value['second']), bound=str(6/q_value(n)**2)))
        solver.clear()

    # Exercise the probability-times-residual bound rather than assuming
    # independence of the orphan and its recipient n-1.
    maximum_suffix_ratio = F(0)
    for n in (4, 6):
        solver = Response(n, 2)
        ell, j_bound = 6*n, 6*n*(6*n+1)
        for y in range(n):
            death = solver.d[y][n]
            for base in ((), solver.corner):
                e = solver.put(base, n, y)
                for k in range(n):
                    for z in range(n+1):
                        v = solver.put(e, k, z)
                        for phase in range(n+2):
                            diff = abs(solver.apply(v, phase, 0, 0)-solver.apply(e, phase, 0, 0))
                            assert diff <= death*j_bound
                            maximum_suffix_ratio = max(maximum_suffix_ratio, diff/(death*j_bound))
                            counts['orphan_suffix_differences'] += 1
                for i in range(n+1):
                    forcing = sum(p*solver.apply(v, i+1, 0, 0)
                                  for v, p in solver.delta_targets(e, i, range(n)))
                    assert abs(forcing) <= 4*death*j_bound
                    counts['mixed_forcings'] += 1
        solver.clear()

    n, t = 4, 2
    ell, m = 6*n, n+1
    K2 = ell*m*(ell+2)
    k_prime = 4*m*ell*(ell+1)+K2
    solver = Restricted(n, t, range(n))
    r_only = solver.coefficients()
    for y in range(n):
        for base in ((), solver.corner):
            h1 = solver.h(solver.put(base, n, y), 1)
            assert abs(h1) <= k_prime
            counts['mixed_responses'] += 1
    solver.clear()
    b_full = F(next(r for r in exact if r['n'] == '4' and r['T'] == '2')['second'])
    b_orphan = orphan(n)['second']
    mixed = b_full-F(r_only['second'])-b_orphan
    assert abs(F(r_only['second'])) <= polynomial(n)['T2_regular']
    assert abs(mixed) <= polynomial(n)['mixed']

    gap_rows = csv_rows(bundle/'gaps.csv')
    bounds_rows = []
    for n in range(3, 11):
        A = F(old[n]['gap_rational'])
        formula_window = sign_window(n, A)
        p = dyadic_below(formula_window)
        assert p <= formula_window < 2*p
        error = remainder(n, p, order=1)
        assert error <= abs(A)*p/2
        b = polynomial(n)
        bounds_rows.append(dict(n=n, q=str(q_value(n)), polynomial_bound=str(b['gap']),
                                parity_free_bound=1536*n**5,
                                resolvent_second_bound=str(norm_second(n)),
                                window=str(p), window_decimal=float(p),
                                formula_window_decimal=float(formula_window),
                                sign='positive' if A > 0 else 'negative',
                                absolute_linear_remainder_bound=str(error)))

    r5 = repo/'research/reports/large-T-20261109/followup/round-0005'
    old_certificate = json.loads((r5/'verification.json').read_text())['witnesses']['expected_monotonicity']
    p = F(1, 192)
    r = next(r for r in gap_rows if r['n'] == '3')
    A, B = F(r['first']), F(r['second'])
    low, high = (F(old_certificate['larger_minus_smaller_sweeps_'+side]) for side in ('lower', 'upper'))
    comparison = dict(n=3, p=str(p),
                      exact_quadratic_prediction=str(p*A+p*p*B),
                      quadratic_prediction_decimal=float(p*A+p*p*B),
                      published_gap_lower=str(low), published_gap_upper=str(high),
                      remainder_lower=str(low-p*A-p*p*B), remainder_upper=str(high-p*A-p*p*B),
                      remainder_lower_decimal=float(low-p*A-p*p*B),
                      remainder_upper_decimal=float(high-p*A-p*p*B),
                      improvement_factor_lower=float((low-p*A)/(high-p*A-p*p*B)),
                      scope='Comparison to a previously published rational finite-p certificate; no new measurement.')
    summary = dict(status='mechanically checked', arithmetic='exact unless explicitly float64',
                   full_state_population_cells=sum(r['states'] for r in full),
                   full_state_coefficient_matches=5*len(exact),
                   numeric_first_matches=numeric_first_matches,
                   maximum_float_second_discrepancy=exact_float_error,
                   counts=counts, maximum_regular_ratio=str(maximum_regular_ratio),
                   maximum_suffix_ratio=str(maximum_suffix_ratio),
                   n4_T2_split=dict(remaining_only=str(r_only['second']), orphan_only=str(b_orphan),
                                    mixed=str(mixed), mixed_decimal=float(mixed)),
                   orphan_checks=orphan_rows,
                   scientific_trajectories=0, scientific_seeds=[],
                   proof_scope='Finite checks do not establish the candidate all-n polynomial bound; see derivation.md.')
    for name, value in (('verification.json', summary), ('comparison.json', comparison)):
        (out/name).write_text(json.dumps(value, indent=2, sort_keys=True)+'\n')
    with (out/'bounds.csv').open('w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=list(bounds_rows[0]))
        w.writeheader()
        w.writerows(bounds_rows)
    print(json.dumps({'status': 'pass', 'counts': counts, 'scientific_trajectories': 0}, sort_keys=True))


if __name__ == '__main__':
    if hasattr(sys, 'set_int_max_str_digits'):
        sys.set_int_max_str_digits(0)
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--repo', type=Path, default=Path('.'))
    p.add_argument('--bundle', type=Path, required=True)
    p.add_argument('--out', type=Path, required=True)
    args = p.parse_args()
    args.out.mkdir(parents=True, exist_ok=True)
    verify(args.repo, args.bundle, args.out)
