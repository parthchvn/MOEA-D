#!/usr/bin/env python3
"""Independent exact phase-equation audit; no earlier solver imports or RNG.

The unknowns are full population tuples at every breeder phase. Clean steps
delete errors. For each tuple and ordered word, a backward affine recurrence
around the phase cycle solves the unknown boundary value. This differs from
the earlier sweep-product/subset insertion implementation.
"""
import argparse
import csv
from fractions import Fraction as F
from functools import lru_cache
import hashlib
from itertools import product
import json
from pathlib import Path
import sys

if hasattr(sys, 'set_int_max_str_digits'):
    sys.set_int_max_str_digits(0)
csv.field_size_limit(sys.maxsize)
ZERO = F(0)


def mutation(n):
    """Per-bit generating polynomial, with integer probability numerators."""
    rows = []
    for x in range(n+1):
        coeff = [1]
        for bit in range(n):
            p0, p1 = (1, n-1) if bit < x else (n-1, 1)
            out = [0]*(len(coeff)+1)
            for j, a in enumerate(coeff):
                out[j] += a*p0
                out[j+1] += a*p1
            coeff = out
        rows.append(tuple(F(a, n**n) for a in coeff))
    return tuple(rows)


def recipients(n, t, i):
    if t == 2:
        return (i, i-1 if i % 2 or i == n else i+1)
    if t == 3:
        start = max(0, min(i-1, n-2))
        return tuple(range(start, start+3))
    raise ValueError('T must be 2 or 3')


def replace(s, k, x):
    return s[:k]+(x,)+s[k+1:]


def digest(x):
    return hashlib.sha256(str(x).encode()).hexdigest()


class Phase:
    def __init__(self, n, t=2):
        self.n, self.m, self.t = n, n+1, t
        self.d = mutation(n)
        self.target = tuple(range(n+1))
        self.corner = replace(self.target, 0, 2)
        self.b = tuple(recipients(n, t, i) for i in range(n+1))

    @lru_cache(None)
    def clean(self, s, i):
        row = {}
        for child, p in enumerate(self.d[s[i]]):
            v = replace(s, child, child) if child in self.b[i] else s
            row[v] = row.get(v, ZERO)+p
        return tuple(row.items())

    @lru_cache(None)
    def delta(self, s, i, letter):
        allowed = tuple(k for k in self.b[i]
                        if letter == 'D' or (letter == 'O') == (k == self.n))
        if letter in 'RO' and (self.t != 2 or self.n % 2):
            raise ValueError('R/O split requires even n and T=2')
        row = {}
        # Build the two recipient-restricted stochastic kernels separately.
        for active, sign in ((False, -1), (True, 1)):
            for child, p in enumerate(self.d[s[i]]):
                if active:
                    observed = enumerate(self.d[child])
                else:
                    observed = ((child, F(1)),)
                for k, a in observed:
                    v = replace(s, k, child) if k in allowed else s
                    row[v] = row.get(v, ZERO)+sign*p*a
        return tuple((v, p) for v, p in row.items() if p)

    @lru_cache(None)
    def values(self, s, word='', mode='time'):
        """Values at phases 0,...,n, including elapsed partial-sweep reward.

        mode='occupation': killed when nonorphans are correct at a boundary;
        reward 1{orphan correct} only at phase zero, and only for empty word.
        A nonempty word denotes G X G Y ... h0, not a trajectory event.
        """
        if mode not in ('time', 'occupation'):
            raise ValueError(mode)
        killed = s == self.target if mode == 'time' else s[:-1] == self.target[:-1]
        alpha, beta = F(1), ZERO
        coeff = [None]*self.m
        for i in range(self.n, -1, -1):
            next_i = (i+1) % self.m
            stay = ZERO
            rhs = ZERO
            if not word:
                rhs = F(1, self.m) if mode == 'time' else F(i == 0 and s[-1] == self.n)
            for v, p in self.clean(s, i):
                if v == s:
                    stay += p
                else:
                    rhs += p*self.values(v, word, mode)[next_i]
            if word:
                rhs += sum((p*self.values(v, word[1:], mode)[next_i]
                            for v, p in self.delta(s, i, word[0])), ZERO)
            alpha, beta = stay*alpha, stay*beta+rhs
            coeff[i] = (alpha, beta)
        boundary = ZERO if killed else beta/(1-alpha)
        result = tuple(a*boundary+b for a, b in coeff)
        # Only phase zero is killed; interior aligned states must survive.
        return (boundary,)+result[1:]

    def local(self):
        """Separate one-coordinate Poisson solve, through degree two."""
        d, n = self.d, self.n
        h0 = tuple(1/d[y][n] if y != n else ZERO for y in range(n+1))
        delta = []
        for x in range(n+1):
            row = [ZERO]*(n+1)
            for z in range(n+1):
                if z == x:
                    continue
                p = d[x][z]*(d[z][n]-F(z == n))
                row[z] += p
                row[x] -= p
            delta.append(tuple(row))
        ans = [h0]
        for _ in range(2):
            ans.append(tuple(sum((delta[x][z]*ans[-1][z] for z in range(n+1)), ZERO)/d[x][n]
                             if x != n else ZERO for x in range(n+1)))
        return tuple(ans), tuple(delta)

    def clear(self):
        self.values.cache_clear()
        self.clean.cache_clear()
        self.delta.cache_clear()


def write_csv(path, rows):
    with path.open('w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def word_audit(repo, ns):
    prior = repo/'research/reports/large-T-20261109/followup/round-0013'
    refs = {(int(r['n']), r['word']): r for r in csv.DictReader((prior/'words.csv').open())}
    rows = []
    bounds = dict(RRR=24, RRO=512, ROR=1024, ROO=1024,
                  ORR=1536, ORO=384, OOR=384)
    for n in ns:
        s = Phase(n)
        q = 1-(1-s.d[2][0])*(1-s.d[1][0])
        z = F(s.m**3*(20*n+1)**3)/q
        total = ZERO
        for letters in product('RO', repeat=3):
            word = ''.join(letters)
            value = s.values(s.corner, word)[0]
            total += value
            bound = bounds[word]*z if word != 'OOO' else 32/q**4
            assert abs(value) <= bound
            ref = refs[n, word]
            assert digest(value) == ref['rational_sha256'], (n, word)
            if ref['coefficient']:
                assert value == F(ref['coefficient'])
            rows.append(dict(n=n, word=word, value_decimal=float(value),
                             rational_sha256=digest(value), published_exact_match=True,
                             bound_decimal=float(bound), bound_ratio=float(abs(value)/bound)))
            print(json.dumps(dict(stage='words', n=n, word=word, value=float(value))), flush=True)
        direct = s.values(s.corner, 'DDD')[0]
        assert total == direct
        arm = next(r for r in csv.DictReader((prior/'coefficients.csv').open())
                   if int(r['n']) == n and r['T'] == '2')
        assert digest(direct) == arm['cubic_sha256']
        s.clear()
    return rows


def phase_audit(ns):
    rows = []
    for n in ns:
        s = Phase(n)
        local, local_delta = s.local()
        b, L = 1-s.d[n][n], F(20*n)
        states, marked_states = set(), {}
        for k in range(n):
            for x in range(n+1):
                if x != k:
                    for y in range(n+1):
                        v = replace(replace(s.corner, k, x), n, y)
                        states.add(v)
                        marked_states[v] = max(marked_states.get(v, ZERO), s.d[x][k])
        # Bad pairs, including orphan-fed last pair and partial clean states.
        for k in range(0, n, 2):
            for x in (0, n):
                for z in (0, n):
                    for y in range(n+1):
                        v = replace(replace(replace(s.corner, k, x), k+1, z), n, y)
                        states.add(v)
        for state in sorted(states):
            y = state[-1]
            orphan = replace(s.target, n, y)
            bad = [(k, k+1) for k in range(0, n, 2)
                   if state[k] != k and state[k+1] != k+1
                   and not (k == 0 and state[0] == 2)]
            assert len(bad) <= 1
            M = L
            if bad:
                k, ell = bad[0]
                M += 2/(s.d[state[k]][k]+s.d[state[ell]][ell])
            # At boundaries identity (10), with a separate stopped reward.
            occupations = [s.values(state, 'O'*j, 'occupation')[0] for j in range(3)]
            maxratios = [ZERO]*4
            for j in range(3):
                h = s.values(state, 'O'*j)
                fphase = s.values(orphan, 'O'*j)
                excess = h[0]-local[j][y]
                occupancy_value = sum((b**(j-r)*occupations[r] for r in range(j+1)), ZERO)
                assert excess == occupancy_value
                for phase in range(s.m):
                    if phase == 0:
                        expected_local = local[j][y]
                    else:
                        # partial reward + A(v)f_v, not merely f_v(y).
                        expected_local = ((1-s.d[y][n])*local[j][y] if y != n else ZERO)
                        if j:
                            expected_local += sum((local_delta[y][z]*local[j-1][z]
                                                   for z in range(n+1)), ZERO)
                        else:
                            expected_local += F(s.m-phase, s.m)
                    assert fphase[phase] == expected_local, (n, state, phase, j)
                    e = h[phase]-fphase[phase]
                    cap = (M, 64*M*M, 512*M**3)[j]
                    assert abs(e) <= cap
                    maxratios[j] = max(maxratios[j], abs(e)/cap)
                    if j == 0:
                        assert e >= 0
                        if y != n:
                            assert e <= s.d[y][n]*M*M
                            maxratios[3] = max(maxratios[3], e/(s.d[y][n]*M*M))
            # Annihilation at every post-proposal phase, including wraparound.
            annihilations = 0
            for i in range(s.m):
                for j in range(3):
                    value = sum((p*s.values(replace(s.target, n, v[-1]), 'O'*j)[(i+1) % s.m]
                                 for v, p in s.delta(state, i, 'R')), ZERO)
                    assert value == 0
                    annihilations += 1
            response_checks = 0
            response_ratio = ZERO
            forcing_ratio = ZERO
            if state in marked_states:
                a = marked_states[state]
                cap = 32*s.m*(L*L+1/a)
                values = s.values(state, 'R')
                for i in range(s.m):
                    assert abs(values[i]) <= cap
                    response_ratio = max(response_ratio, abs(values[i])/cap)
                    forcing = sum((p*s.values(v)[(i+1) % s.m]
                                   for v, p in s.delta(state, i, 'R')), ZERO)
                    fcap = 5*s.d[y][n]*(L*L+1/a) if y != n else 2*L
                    assert abs(forcing) <= fcap
                    forcing_ratio = max(forcing_ratio, abs(forcing)/fcap)
                    response_checks += 2
            elif y == n:
                values = s.values(state, 'R')
                for v in values:
                    assert abs(v) <= 3*s.m*M*M
                    response_ratio = max(response_ratio, abs(v)/(3*s.m*M*M))
                    response_checks += 1
            rows.append(dict(n=n, state=' '.join(map(str, state)), bad_pairs=len(bad),
                             phases=s.m, boundary_identities=3,
                             local_phase_identities=3*s.m, annihilations=annihilations,
                             maximum_e0_ratio=float(maxratios[0]),
                             maximum_e1_ratio=float(maxratios[1]),
                             maximum_e2_ratio=float(maxratios[2]),
                             maximum_predictable_ratio=float(maxratios[3]),
                             response_inequalities=response_checks,
                             maximum_response_ratio=float(response_ratio),
                             maximum_forcing_ratio=float(forcing_ratio)))
        print(json.dumps(dict(stage='phases', n=n, states=len(states))), flush=True)
        s.clear()
    return rows


def acceptance_audit():
    rows = []
    for n in range(3, 17):
        d, L = mutation(n), F(20*n)
        count, maximum, marked = 0, ZERO, ZERO
        for k in range(0, n, 2):
            for x in range(n+1):
                for y in range(n+1):
                    if x == k or y == k+1:
                        continue
                    a, b = d[x][k], d[y][k+1]
                    M = L+2/(a+b)
                    v = a*b*M*M/(L+1)**2
                    w = b*M*M/(2*L*L+2/a)
                    assert v <= 1 and w <= 1
                    maximum, marked = max(maximum, v), max(marked, w)
                    count += 2
        rows.append(dict(n=n, exact_inequalities=count,
                         maximum_two_entry_ratio=float(maximum),
                         maximum_marked_entry_ratio=float(marked)))
    return rows


def birth_audit():
    """Exhaust a superset of all two-birth histories; no probabilities sampled."""
    rows = []
    for n in range(3, 9):
        s = Phase(n)
        checked, bad_count = 0, 0
        starts = (s.corner, s.target)
        for start in starts:
            for i in range(s.m):
                for k in s.b[i]:
                    if n % 2 == 0 and k == n:
                        continue
                    for x in range(s.m):
                        if x == k or x == start[k]:
                            continue
                        first = replace(start, k, x)
                        errs = [j for j in range(s.m) if first[j] != j]
                        for keep in product((False, True), repeat=len(errs)):
                            desc = first
                            for j, retained in zip(errs, keep):
                                if not retained:
                                    desc = replace(desc, j, j)
                            for ii in range(s.m):
                                for ell in s.b[ii]:
                                    if n % 2 == 0 and ell == n:
                                        continue
                                    for y in range(s.m):
                                        if y == ell or y == desc[ell]:
                                            continue
                                        end = replace(desc, ell, y)
                                        checked += 1
                                        bad = [(a, a+1) for a in range(0, n, 2)
                                               if end[a] != a and end[a+1] != a+1
                                               and not (a == 0 and end[0] == 2)]
                                        assert len(bad) <= 1
                                        if bad:
                                            assert set(bad[0]) == {k, ell} and k != ell
                                            assert end[k] == x and end[ell] == y
                                            a, b = bad[0]
                                            assert s.d[x][k]*s.d[y][ell] == s.d[end[a]][a]*s.d[end[b]][b]
                                            bad_count += 1
        rows.append(dict(n=n, histories=checked, bad_histories=bad_count,
                         missing_acceptance_factors=0, support='superset of clean descendants'))
        s.clear()
    return rows


def main(repo, out, ns, phases):
    out.mkdir(parents=True, exist_ok=True)
    acceptance = acceptance_audit()
    write_csv(out/'acceptance.csv', acceptance)
    births = birth_audit()
    write_csv(out/'births.csv', births)
    words = word_audit(repo, ns)
    write_csv(out/'words.csv', words)
    phase = phase_audit(phases)
    write_csv(out/'phases.csv', phase)
    data = dict(status='mechanically checked', arithmetic='exact rational',
                independent_solver='full-population phase-cycle affine equations; no prior imports',
                ordered_words=len(words), mixed_words=sum(r['word'] not in ('RRR','OOO') for r in words),
                acceptance_inequalities=sum(r['exact_inequalities'] for r in acceptance),
                two_birth_histories=sum(r['histories'] for r in births),
                bad_birth_histories=sum(r['bad_histories'] for r in births),
                phase_states=len(phase),
                boundary_excess_identities=sum(r['boundary_identities'] for r in phase),
                local_phase_identities=sum(r['local_phase_identities'] for r in phase),
                annihilation_identities=sum(r['annihilations'] for r in phase),
                phase_excess_bound_checks=sum(4*r['phases'] for r in phase),
                response_inequalities=sum(r['response_inequalities'] for r in phase),
                scientific_trajectories=0, scientific_seeds=[],
                censoring='not applicable to deterministic algebra')
    (out/'verification.json').write_text(json.dumps(data, indent=2, sort_keys=True)+'\n')
    print(json.dumps(data), flush=True)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--repo', type=Path, default=Path('.'))
    parser.add_argument('--out', type=Path, required=True)
    parser.add_argument('--n', type=int, nargs='+', default=[4, 6])
    parser.add_argument('--phases', type=int, nargs='+', default=[4, 6])
    args = parser.parse_args()
    main(args.repo, args.out, args.n, args.phases)
