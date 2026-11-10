#!/usr/bin/env python3
"""Independent rational sweep-product audit of RROO; no prior solver imports.

Words are noncommuting insertion labels, not counts of noise events.
Clean population transitions only delete errors, giving a triangular boundary
solve. Suffix products then reconstruct every interior phase without killing
there. All scientific calculations are deterministic; no RNG is used.
"""
import argparse
import csv
from fractions import Fraction as F
from functools import lru_cache
import hashlib
from math import comb
import json
from pathlib import Path
import sys

if hasattr(sys, 'set_int_max_str_digits'):
    sys.set_int_max_str_digits(0)
ZERO = F(0)


def mutation(n):
    return tuple(tuple(F(sum(comb(x, lost)*comb(n-x, y-x+lost)
                             * (n-1)**(n-lost-(y-x+lost))
                             for lost in range(x+1)
                             if 0 <= y-x+lost <= n-x), n**n)
                       for y in range(n+1)) for x in range(n+1))


def neighborhood(n, i):
    result = [i]
    for distance in range(1, n+1):
        for offset in ((distance, -distance) if i % 2 == 0 else (-distance, distance)):
            if 0 <= i+offset <= n:
                result.append(i+offset)
                if len(result) == 2:
                    return tuple(result)
    raise ValueError(n)


def change(s, k, x):
    return s[:k]+(x,)+s[k+1:]


def sha_fraction(x):
    return hashlib.sha256(str(x).encode()).hexdigest()


def add(row, state, value):
    row[state] = row.get(state, ZERO)+value


class Sweep:
    def __init__(self, n):
        if n < 4 or n % 2:
            raise ValueError('Even n >= 4 required for the T=2 orphan split')
        self.n, self.m = n, n+1
        self.d = mutation(n)
        self.target = tuple(range(n+1))
        self.corner = change(self.target, 0, 2)
        self.neighbors = tuple(neighborhood(n, i) for i in range(n+1))

    @lru_cache(None)
    def step(self, s, i, letter=''):
        """K, R, or O row, including its negative unchanged branch."""
        row = {}
        allowed = self.neighbors[i]
        if not letter:
            for z, p in enumerate(self.d[s[i]]):
                add(row, change(s, z, z) if z in allowed else s, p)
        else:
            allowed = tuple(k for k in allowed if (k == self.n) == (letter == 'O'))
            if letter not in ('R', 'O'):
                raise ValueError(letter)
            # Off-diagonal overwrite-minus-stay representation. Same-value
            # overwrites cancel before summation, independently of acceptance.
            for k in allowed:
                for z, p in enumerate(self.d[s[i]]):
                    if z == s[k]:
                        continue
                    weight = p*(self.d[z][k]-F(z == k))
                    add(row, change(s, k, z), weight)
                    add(row, s, -weight)
        return tuple((v, p) for v, p in row.items() if p)

    @lru_cache(None)
    def product(self, s, word='', phase=0):
        """Coefficient of one ordered word in the unrestricted suffix."""
        if word.count('O') > 1 or len(word) > self.m-phase:
            return ()
        if phase == self.m:
            return ((s, F(1)),) if not word else ()
        row = {}
        for v, p in self.step(s, phase):
            for end, a in self.product(v, word, phase+1):
                add(row, end, p*a)
        if word:
            for v, p in self.step(s, phase, word[0]):
                for end, a in self.product(v, word[1:], phase+1):
                    add(row, end, p*a)
        return tuple((v, p) for v, p in row.items() if p)

    def killed(self, s, mode):
        return s == self.target if mode == 'time' else s[:-1] == self.target[:-1]

    @lru_cache(None)
    def value(self, s, word='', mode='time'):
        if self.killed(s, mode):
            return ZERO
        if mode not in ('time', 'reward', 'duration', 'second'):
            raise ValueError(mode)
        rhs = ZERO
        if not word:
            if mode == 'reward':
                rhs = F(s[-1] == self.n)
            elif mode == 'second':
                rhs = 2*self.value(s, '', 'duration')-1
            else:
                rhs = F(1)
        stay = ZERO
        for v, p in self.product(s):
            if v == s:
                stay += p
            else:
                assert sum(x != k for k, x in enumerate(v)) < sum(x != k for k, x in enumerate(s))
                rhs += p*self.value(v, word, mode)
        for length in range(1, len(word)+1):
            rhs += sum((p*self.value(v, word[length:], mode)
                        for v, p in self.product(s, word[:length])), ZERO)
        return rhs/(1-stay)

    @lru_cache(None)
    def phase(self, s, word='', i=0, mode='time'):
        if not i:
            return self.value(s, word, mode)
        ans = F(self.m-i, self.m) if not word and mode == 'time' else ZERO
        for length in range(len(word)+1):
            ans += sum((p*self.value(v, word[length:], mode)
                        for v, p in self.product(s, word[:length], i)), ZERO)
        return ans

    def excess(self, s, degree, i=0):
        local = change(self.target, self.n, s[-1])
        return self.phase(s, 'O'*degree, i)-self.phase(local, 'O'*degree, i)

    def clear(self):
        for name in ('step', 'product', 'value', 'phase'):
            getattr(self, name).cache_clear()


def write(path, rows):
    with path.open('w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)


def state_grid(s):
    n = s.n
    result = []
    for k in range(0, n, 2):
        # Full pair grids through n=6, full orphan-fed grid at n=8;
        # endpoint stress states for remaining n=8 and all n=10 pairs.
        choices = range(n+1) if n <= 6 or n == 8 and k == n-2 else (0, n)
        for x in choices:
            for y in choices:
                if x == k or y == k+1:
                    continue
                for base in ((s.target,) if k == 0 else (s.target, s.corner)):
                    v = change(change(base, k, x), k+1, y)
                    result.append((k, x, y, v))
    return result


def reward_audit(ns):
    rows = []
    for n in ns:
        s = Sweep(n)
        L, beta = F(20*n), 1-s.d[n][n]
        for k, x, y, state in state_grid(s):
            M = L+2/(s.d[x][k]+s.d[y][k+1])
            last = k == n-2
            cap = 20*L**3 if last else 5*M*M
            ratios = [ZERO]*4
            checks = 0
            for orphan in range(n+1):
                v = change(state, n, orphan)
                w = [s.value(v, 'O'*j, 'reward') for j in range(3)]
                for j in range(3):
                    expected = sum(beta**(j-r)*w[r] for r in range(j+1))
                    assert s.excess(v, j) == expected
                    checks += 1
                if last:
                    mean_cap = L if orphan == n else min(M, 1/s.d[orphan][n]+L)
                    assert 0 <= w[0] <= L
                    assert abs(w[1]) <= 2*L*mean_cap
                    ratios[0] = max(ratios[0], w[0]/L)
                    ratios[1] = max(ratios[1], abs(w[1])/(2*L*mean_cap))
                    checks += 2
            if last:
                w2 = s.value(state, 'OO', 'reward')
                assert abs(w2) <= 6*L**3
                forcing = sum(p*s.value(v, 'O', 'reward') for v, p in s.product(state, 'O'))
                assert abs(forcing) <= 6*L**2
                ratios[2] = abs(forcing)/(6*L**2)
                checks += 2
            else:
                mean = s.value(state, '', 'duration')
                second = s.value(state, '', 'second')
                assert mean <= M and second <= (2*M+1)*mean <= 3*M*M
                checks += 3
            for i in range(s.m):
                e2 = s.excess(state, 2, i)
                assert abs(e2) <= cap
                suffix0 = sum(p*s.excess(v, 2) for v, p in s.product(state, '', i))
                suffix1 = sum(p*s.excess(v, 1) for v, p in s.product(state, 'O', i))
                if i:
                    assert e2 == suffix0+suffix1
                    if last:
                        assert abs(suffix1) <= 8*L**2
                    checks += 1+int(last)
                # R annihilates each phase-local term, including boundary wrap.
                for j in range(3):
                    annihilation = sum(p*s.phase(change(s.target, n, v[-1]), 'O'*j, (i+1) % s.m)
                                       for v, p in s.step(state, i, 'R'))
                    assert annihilation == 0
                    checks += 1
                ratios[3] = max(ratios[3], abs(e2)/cap)
                checks += 1
            rows.append(dict(n=n, pair=k, x=x, y=y,
                             corner_remaining=bool(k and state[0] == 2),
                             kind='orphan-fed' if last else 'closed',
                             phases=s.m, checks=checks,
                             boundary_e2=float(s.excess(state, 2)),
                             boundary_e2_sha256=sha_fraction(s.excess(state, 2)),
                             max_w0_ratio=float(ratios[0]), max_w1_ratio=float(ratios[1]),
                             forcing_ratio=float(ratios[2]), max_e2_ratio=float(ratios[3])))
        print(json.dumps(dict(stage='rewards', n=n, states=len(state_grid(s)))), flush=True)
        s.clear()
    return rows


def stationary_audit(ns, horizons=(0, 1, 2, 4, 8, 16)):
    rows = []
    for n in ns:
        s = Sweep(n)
        local = tuple(change(s.target, n, y) for y in range(n+1))
        a0 = [dict((v[-1], p) for v, p in s.step(state, n)) for state in local]
        a1 = [dict((v[-1], p) for v, p in s.step(state, n, 'O')) for state in local]
        beta = 1-s.d[n][n]
        nu0, nu1 = [F(y == n) for y in range(n+1)], [s.d[n][y]-F(y == n) for y in range(n+1)]
        # Polynomial stationarity verified coefficient by coefficient.
        for y in range(n+1):
            assert sum(nu0[x]*a0[x].get(y, ZERO) for x in range(n+1)) == nu0[y]
            assert sum(nu0[x]*a1[x].get(y, ZERO)+nu1[x]*a0[x].get(y, ZERO) for x in range(n+1)) == nu1[y]
            assert sum(nu1[x]*a1[x].get(y, ZERO) for x in range(n+1)) == 0
        v = [nu0, [ZERO]*(n+1), [ZERO]*(n+1)]
        for t in range(max(horizons)+1):
            if t in horizons:
                first = v[1][n]+beta*v[0][n]
                second = v[2][n]+beta*v[1][n]+beta**2*v[0][n]
                s0 = sum(s.d[n][y]*v[0][y] for y in range(n))
                s1 = sum(s.d[n][y]*v[1][y] for y in range(n))
                assert second == beta**2-2*beta*s0-s1
                assert first == sum(s.d[n][y]*(1-s.d[y][n])**t for y in range(n))
                assert abs(second) <= 3+2*t
                rows.append(dict(n=n, turns=t, coefficient=float(second),
                                 rational_sha256=sha_fraction(second), bound=3+2*t,
                                 stationarity_coefficients=3*(n+1)))
            v = [[sum(p*v[j][z] for z, p in a0[y].items())+
                  (sum(p*v[j-1][z] for z, p in a1[y].items()) if j else ZERO)
                  for y in range(n+1)] for j in range(3)]
        s.clear()
    return rows


def word_audit(repo, ns):
    prior = repo/'research/reports/large-T-20261109/followup/round-0015/mixed.csv'
    refs = {int(r['n']): r for r in csv.DictReader(prior.open())}
    rows = []
    for n in ns:
        s = Sweep(n)
        value = s.value(s.corner, 'RROO')
        assert sha_fraction(value) == refs[n]['coefficient_sha256']
        L = 20*n
        q = 1-(1-s.d[2][0])*(1-s.d[1][0])
        cap = 5000*s.m**2*L**4/q
        assert abs(value) <= cap
        rows.append(dict(n=n, word='RROO', value=float(value),
                         rational_sha256=sha_fraction(value),
                         published_exact_match=True, bound=float(cap)))
        print(json.dumps(dict(stage='word', n=n, value=float(value))), flush=True)
        s.clear()
    return rows


def dependence_witness():
    s = Sweep(4)
    state = (0, 1, 2, 0, 0)
    row = s.step(state, 4)
    pair = sum(p for v, p in row if v[:-1] == s.target[:-1])
    orphan = sum(p for v, p in row if v[-1] == 4)
    joint = sum(p for v, p in row if v == s.target)
    assert pair == F(3, 64) and orphan == F(1, 256) and joint == 0
    s.clear()
    return dict(status='proved finite counterexample to independent repair events',
                n=4, state=list(state), next_breeder=4,
                nonorphan_completion=str(pair), orphan_repair=str(orphan),
                joint=str(joint), product_of_marginals=str(pair*orphan),
                scope='One pending clean turn; the stopped-reward proof does not assume independence.')


def main(repo, out, ns, words):
    out.mkdir(parents=True, exist_ok=True)
    rewards = reward_audit(ns)
    write(out/'rewards.csv', rewards)
    published = repo/'research/reports/large-T-20261109/followup/round-0015/excess.csv'
    key = lambda r: (int(r['n']), int(r['pair']), int(r['x']), int(r['y']), str(r['corner_remaining']))
    current = {key(r): r for r in rewards}
    matches = 0
    for old in csv.DictReader(published.open()):
        if key(old) in current:
            assert current[key(old)]['boundary_e2_sha256'] == old['boundary_excess_sha256']
            matches += 1
    stationary = stationary_audit((4, 6, 8, 12))
    write(out/'stationary.csv', stationary)
    ordered = word_audit(repo, words)
    write(out/'words.csv', ordered)
    witness = dependence_witness()
    (out/'witness.json').write_text(json.dumps(witness, indent=2, sort_keys=True)+'\n')
    result = dict(status='mechanically checked', arithmetic='exact rational',
                  independent_method='Combinatorial weight probabilities; unrestricted ordered sweep products; triangular boundary solves; explicit suffix reconstruction. No prior solver imports.',
                  states=len(rewards), phases=sum(r['phases'] for r in rewards),
                  inequalities_and_identities=sum(r['checks'] for r in rewards),
                  orphan_fed_states=sum(r['kind'] == 'orphan-fed' for r in rewards),
                  stationary_times=len(stationary), ordered_words=len(ordered),
                  published_excess_exact_matches=matches,
                  scientific_trajectories=0, scientific_seeds=[],
                  censoring='not applicable to deterministic calculations')
    (out/'verification.json').write_text(json.dumps(result, indent=2, sort_keys=True)+'\n')
    print(json.dumps(result), flush=True)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--repo', type=Path, default=Path('.'))
    parser.add_argument('--out', type=Path, required=True)
    parser.add_argument('--n', type=int, nargs='+', default=[4, 6, 8, 10])
    parser.add_argument('--words', type=int, nargs='+', default=[4, 6])
    args = parser.parse_args()
    main(args.repo.resolve(), args.out, args.n, args.words)
