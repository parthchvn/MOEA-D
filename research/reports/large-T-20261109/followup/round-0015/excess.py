#!/usr/bin/env python3
"""Exact checks of the correct-orphan second excess and RROO bound."""
import argparse
from fractions import Fraction as F
import json
from pathlib import Path
from verify import load, write, digest


def stationary(s, horizons):
    n, d = s.n, s.d
    _, delta = s.local()
    b = 1-d[n][n]
    v = [[F(y == n) for y in range(n+1)], [F(0)]*(n+1), [F(0)]*(n+1)]
    rows = []
    for t in range(max(horizons)+1):
        if t in horizons:
            first = v[1][n]+b*v[0][n]
            second = v[2][n]+b*v[1][n]+b*b*v[0][n]
            rhs = b*b-2*b*sum(d[n][y]*v[0][y] for y in range(n))-sum(d[n][y]*v[1][y] for y in range(n))
            expected_first = sum(d[n][y]*(1-d[y][n])**t for y in range(n))
            assert first == expected_first and second == rhs
            assert abs(second) <= 3+2*t
            rows.append(dict(n=n, turns=t, first_decimal=float(first),
                             second_decimal=float(second), second_sha256=digest(second),
                             bound=3+2*t, exact_identities=True))
        out = [[F(0)]*(n+1) for _ in range(3)]
        for j in range(3):
            for y in range(n+1):
                out[j][y] = (1-d[y][n])*v[j][y]+d[y][n]*v[j][n] if y != n else v[j][n]
                if j:
                    out[j][y] += sum(delta[y][z]*v[j-1][z] for z in range(n+1))
        v = out
    return rows


def main(repo, out):
    out.mkdir(parents=True, exist_ok=True)
    mod = load(repo/'research/reports/large-T-20261109/followup/round-0014/audit.py', 'excess_phase')
    rows, identities, words = [], [], []
    for n in (4, 6, 8):
        s = mod.Phase(n, 2)
        L, b = F(20*n), 1-s.d[n][n]
        identities += stationary(s, (0, 1, 2, 4, 8, 16))
        orphan_values = s.values(s.target, 'OO')
        for k in range(0, n, 2):
            choices = range(n+1) if n <= 6 else (0, n)
            for x in choices:
                for y in choices:
                    if x == k or y == k+1:
                        continue
                    starts = (s.target, s.corner) if k else (s.target,)
                    for base in starts:
                        state = mod.replace(mod.replace(base, k, x), k+1, y)
                        M = L+2/(s.d[x][k]+s.d[y][k+1])
                        last = k == n-2
                        cap = 20*L**3 if last else 5*M*M
                        response = s.values(state, 'OO')
                        ratio = F(0)
                        for phase in range(n+1):
                            e = response[phase]-orphan_values[phase]
                            assert abs(e) <= cap, (n, state, phase, e, cap)
                            ratio = max(ratio, abs(e)/cap)
                        w = [s.values(state, 'O'*j, 'occupation')[0] for j in range(3)]
                        assert response[0] == w[2]+b*w[1]+b*b*w[0]
                        reward_checks = 1
                        if last:
                            assert abs(w[2]) <= 6*L**3
                            assert abs(response[0]) <= 9*L**3
                            reward_checks += 2
                            for orphan in range(n+1):
                                v = mod.replace(state, n, orphan)
                                w0 = s.values(v, '', 'occupation')[0]
                                w1 = s.values(v, 'O', 'occupation')[0]
                                assert 0 <= w0 <= L
                                mean_cap = L if orphan == n else min(M, 1/s.d[orphan][n]+L)
                                assert abs(w1) <= 2*L*mean_cap
                                reward_checks += 2
                        rows.append(dict(n=n, pair=k, x=x, y=y,
                                         corner_remaining=bool(state[0] == 2 and k != 0),
                                         kind='orphan-fed' if last else 'closed',
                                         phase_checks=n+1, reward_checks=reward_checks,
                                         max_bound_ratio=float(ratio),
                                         boundary_excess_decimal=float(response[0]),
                                         boundary_excess_sha256=digest(response[0])))
        if n in (4, 6):
            value = s.values(s.corner, 'RROO')[0]
            q = 1-(1-s.d[2][0])*(1-s.d[1][0])
            cap = 5000*s.m**2*L**4/q
            assert abs(value) <= cap
            words.append(dict(n=n, word='RROO', coefficient_decimal=float(value),
                              coefficient_sha256=digest(value), bound_decimal=float(cap)))
        print(json.dumps(dict(stage='excess', n=n, states=sum(r['n'] == n for r in rows))), flush=True)
        s.clear()
    write(out/'excess.csv', rows)
    write(out/'stationary.csv', identities)
    write(out/'mixed.csv', words)
    result = dict(status='mechanically checked; all-n mixed bound remains a candidate proof',
                  phase_states=len(rows), phase_checks=sum(r['phase_checks'] for r in rows),
                  stopped_reward_checks=sum(r['reward_checks'] for r in rows),
                  stationary_times=len(identities), stationary_identities=2*len(identities),
                  mixed_words=len(words), scientific_trajectories=0, scientific_seeds=[],
                  scope='RROO only; correct orphan after two R insertions, including last-pair feedback')
    (out/'excess.json').write_text(json.dumps(result, indent=2, sort_keys=True)+'\n')
    print(json.dumps(result), flush=True)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--repo', type=Path, default=Path('.'))
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    main(args.repo.resolve(), args.out)
