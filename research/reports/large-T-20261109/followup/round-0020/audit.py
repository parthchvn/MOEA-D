#!/usr/bin/env python3
"""Independent rational audit of RORR; no prior solver imports or RNG.

For a population held fixed until its first clean change, sum one circular
pass of phase forcings and divide by its escape probability. Every changed
clean successor has fewer errors. This rotation solve uses neither the
round-19 sweep insertion products nor an earlier implementation's answers.
"""
import argparse
from collections import defaultdict
import csv
from fractions import Fraction as F
from functools import lru_cache
import hashlib
import json
from pathlib import Path
import sys

if hasattr(sys, 'set_int_max_str_digits'):
    sys.set_int_max_str_digits(0)
ZERO = F(0)


def overwrite(s, k, x):
    return tuple(x if j == k else z for j, z in enumerate(s))


def fingerprint(x):
    return hashlib.sha256(str(x).encode()).hexdigest()


def write_csv(path, rows):
    with path.open('w', newline='') as f:
        w = csv.DictWriter(f, list(rows[0]))
        w.writeheader()
        w.writerows(rows)


def check_manifest(path):
    manifest = json.loads((path/'provenance.json').read_text())
    matches = {name: hashlib.sha256((path/name).read_bytes()).hexdigest() == value
               for name, value in manifest['artifacts_sha256'].items()}
    assert all(matches.values()), matches
    return matches


class Audit:
    def __init__(self, n):
        if n < 4 or n % 2:
            raise ValueError('even n >= 4 required')
        self.n, self.m, self.L = n, n+1, 20*n
        self.aligned = tuple(range(n+1))
        self.corner = overwrite(self.aligned, 0, 2)
        # Direct convolution of the surviving-one and newly-created-one laws.
        rows = []
        for x in range(n+1):
            poly = [1]
            for bit in range(n):
                one = n-1 if bit < x else 1
                new = [0]*(len(poly)+1)
                for k, a in enumerate(poly):
                    new[k] += a*(n-one)
                    new[k+1] += a*one
                poly = new
            rows.append(tuple(F(a, n**n) for a in poly))
        self.d = tuple(rows)
        self.q = 1-(1-self.d[2][0])*(1-self.d[1][0])

    def neighbors(self, i):
        # Literal alternating-distance construction, including endpoint fill.
        out = [i]
        for distance in range(1, self.n+1):
            sides = (1, -1) if i % 2 == 0 else (-1, 1)
            for side in sides:
                k = i+side*distance
                if 0 <= k <= self.n:
                    out.append(k)
                    if len(out) == 2:
                        return tuple(out)
        raise AssertionError('unfilled neighborhood')

    def base(self, y):
        return overwrite(self.aligned, self.n, y)

    @lru_cache(None)
    def kernel(self, s, i, active=False, part='all'):
        """Recipient-restricted *stochastic* kernel, built before subtraction."""
        allowed = [k for k in self.neighbors(i)
                   if part == 'all' or (part == 'O') == (k == self.n)]
        row = defaultdict(F)
        for child, pm in enumerate(self.d[s[i]]):
            observations = enumerate(self.d[child]) if active else ((child, F(1)),)
            for obs, pn in observations:
                v = overwrite(s, obs, child) if obs in allowed else s
                row[v] += pm*pn
        return tuple(sorted((v, p) for v, p in row.items() if p))

    @lru_cache(None)
    def signed(self, s, i, letter):
        row = defaultdict(F)
        for active, sign in ((True, 1), (False, -1)):
            for v, p in self.kernel(s, i, active, letter):
                row[v] += sign*p
        return tuple((v, p) for v, p in row.items() if p)

    def apply(self, s, i, letter, key):
        nxt = (i+1) % self.m
        return sum((p*self.values(v, key)[nxt]
                    for v, p in self.signed(s, i, letter)), ZERO)

    @lru_cache(None)
    def values(self, s, key=''):
        """All phases; only the aligned phase-zero boundary is killed.

        Keys R/O words are ordered signed resolvent responses. '@visits'
        counts final-turn visits; '@gamma' integrates centered O forcing;
        '@outer' applies the first R to that integrated forcing.
        """
        if key.startswith('@'):
            assert s[-1] == self.n
        stay, rhs = [], []
        for i in range(self.m):
            nxt = (i+1) % self.m
            if not key:
                b = F(1, self.m)
            elif key == '@visits':
                b = F(i == self.n)
            elif key == '@gamma':
                b = self.gamma(s) if i == self.n else ZERO
            elif key == '@outer':
                b = self.apply(s, i, 'R', '@gamma')
            else:
                b = self.apply(s, i, key[0], key[1:])
            a = ZERO
            for v, p in self.kernel(s, i):
                if v == s:
                    a += p
                else:
                    assert sum(x != k for k, x in enumerate(v)) < sum(x != k for k, x in enumerate(s))
                    b += p*self.values(v, key)[nxt]
            stay.append(a)
            rhs.append(b)
        if s == self.aligned:
            assert all(a == 1 for a in stay)
            return (ZERO,)+tuple(sum(rhs[i:], ZERO) for i in range(1, self.m))
        survival = F(1)
        for a in stay:
            survival *= a
        assert 0 <= survival < 1
        result = []
        for start in range(self.m):
            mass, value = F(1), ZERO
            for step in range(self.m):
                i = (start+step) % self.m
                value += mass*rhs[i]
                mass *= stay[i]
            result.append(value/(1-survival))
        return tuple(result)

    def centered(self, s):
        return tuple(x-y for x, y in zip(self.values(s, 'RR'), self.values(self.base(s[-1]), 'RR')))

    @lru_cache(None)
    def beta(self):
        return sum((self.d[self.n][y]*self.d[y][self.n]
                    *self.values(self.base(y), 'RR')[0]
                    for y in range(self.n)), ZERO)

    @lru_cache(None)
    def gamma(self, s):
        assert s[-1] == self.n
        old = self.centered(s)[0]
        return sum((self.d[self.n][y]*self.d[y][self.n]
                    *(self.centered(overwrite(s, self.n, y))[0]-old)
                    for y in range(self.n)), ZERO)

    def clear(self):
        for key in ('kernel', 'signed', 'values', 'beta', 'gamma'):
            getattr(self, key).cache_clear()


def verify(repo, out, ns):
    out.mkdir(parents=True, exist_ok=True)
    prior = repo/'research/reports/large-T-20261109/followup'
    for folder in ('round-0018', 'round-0019'):
        check_manifest(prior/folder)
    refs = {int(r['n']): r for r in csv.DictReader((prior/'round-0019/words.csv').open())}
    rows = {key: [] for key in ('words', 'baseline', 'phases', 'entrances', 'branches')}
    counts = dict(equalities=0, inequalities=0, marked_cases=0, marked_phases=0,
                  joint_entrance_cases=0, baseline_phases=0, positive_kernel_cases=0,
                  published_word_matches=0, published_baseline_matches=0)

    def eq(a, b):
        assert a == b, (a, b)
        counts['equalities'] += 1

    def le(a, b):
        assert a <= b, (a, b)
        counts['inequalities'] += 1

    for n in ns:
        s = Audit(n)
        m, L = s.m, s.L
        beta = s.beta()
        baseline_refs = [r for r in csv.DictReader((prior/'round-0019/entrance.csv').open()) if int(r['n']) == n]
        for y in range(n+1):
            d = s.d[y][n]
            birth = s.d[n][y]*d if y != n else ZERO
            h = s.values(s.base(y), 'RR')
            bound = F(10*m*m*L*L, 1)/d if y != n else ZERO
            le(abs(h[0]), bound)
            le(birth*abs(h[0]), 10*m*m*L*L*s.d[n][y])
            for i in range(m):
                le(abs(s.apply(s.base(y), i, 'R', 'R')), 10*m*L*L)
                counts['baseline_phases'] += 1
            rows['baseline'].append(dict(n=n, y=y, repair=str(d), entrance=str(birth),
                response_sha256=fingerprint(h[0]), response=float(h[0]),
                entrance_response=float(birth*h[0]), bound_ratio=float(abs(h[0])/bound) if bound else 0.0))
            if baseline_refs:
                ref = next(r for r in baseline_refs if int(r['y']) == y)
                eq(fingerprint(h[0]), ref['baseline_sha256'])
                counts['published_baseline_matches'] += 1
        le(abs(beta), 10*m*m*L*L)
        eq(s.gamma(s.aligned), 0)
        eq(s.apply(s.aligned, n, 'O', 'RR'), beta)
        print(json.dumps(dict(stage='baseline', n=n, beta=float(beta))), flush=True)

        # Full child/orphan grid at n=4. At n=6 retain every target and orphan,
        # with child in {0,target,n}; this is a declared bounded proof check.
        for origin, initial in (('corner', s.corner), ('aligned', s.aligned)):
            for k in range(n):
                children = range(n+1) if n == 4 else sorted({0, k, n})
                for x in children:
                    mark = s.d[x][k]
                    regular = overwrite(initial, k, x)
                    cap = 64*m*m*L*(L*L+1/mark)
                    u = 138*m*m*L**4
                    vcap = 138*m*m*L*L*(L*L+1/mark)
                    for y in range(n+1):
                        state = overwrite(regular, n, y)
                        centered = s.centered(state)
                        for v in centered:
                            le(abs(v), cap)
                        counts['marked_cases'] += 1
                        counts['marked_phases'] += m
                        entry = ZERO
                        if y < n:
                            birth = s.d[n][y]*s.d[y][n]
                            entry = mark*birth*(abs(s.values(state, 'RR')[0])+abs(s.values(regular, 'RR')[0]))
                            envelope = s.d[n][y]*(10*mark*m*m*L*L+128*m*m*L*s.d[y][n]*(mark*L*L+1))
                            le(entry, envelope)
                            counts['joint_entrance_cases'] += 1
                            rows['entrances'].append(dict(n=n, origin=origin, k=k, x=x, y=y,
                                acceptance=str(mark), orphan_entrance=str(birth),
                                weighted_value=float(entry), envelope=float(envelope),
                                ratio=float(entry/envelope), value_sha256=fingerprint(entry)))
                        rows['phases'].append(dict(n=n, origin=origin, k=k, x=x, y=y,
                            phase_count=m, centered_sha256=fingerprint(centered),
                            max_centered_ratio=float(max(map(abs, centered))/cap)))
                    # Correct-orphan phase identities are the new assembly's
                    # essential obligations; all phases and signed branches stay.
                    j = s.values(regular, 'ORR')
                    visits = s.values(regular, '@visits')
                    gam = s.values(regular, '@gamma')
                    h0 = s.values(regular)
                    eq(s.apply(regular, n, 'O', 'RR'), beta+s.gamma(regular))
                    for i in range(m):
                        eq(visits[i], h0[i]+F(i, m))
                        eq(j[i], beta*visits[i]+gam[i])
                        le(visits[i], L)
                        le(abs(j[i]), vcap)
                    # Two extensions, plus partial-cycle and boundary slack.
                    le(max(visits), 6*n+2)
                    le(abs(s.gamma(regular)), 2*cap)
        print(json.dumps(dict(stage='marked', n=n, cases=counts['marked_cases'])), flush=True)

        u = 138*m*m*L**4
        for origin, state in (('corner', s.corner), ('aligned', s.aligned)):
            for v in s.centered(state):
                le(abs(v), 64*m*m*L**3)
            for j in s.values(state, 'ORR'):
                le(abs(j), u)
            for i in range(m):
                nxt = (i+1) % m
                plus = sum((p*abs(s.values(v, 'ORR')[nxt]) for v, p in s.kernel(state, i, True, 'R')), ZERO)
                minus = sum((p*abs(s.values(v, 'ORR')[nxt]) for v, p in s.kernel(state, i, False, 'R')), ZERO)
                signed = s.apply(state, i, 'R', 'ORR')
                direct = sum((p*s.values(v, 'ORR')[nxt] for v, p in s.kernel(state, i, True, 'R')), ZERO)-sum((p*s.values(v, 'ORR')[nxt] for v, p in s.kernel(state, i, False, 'R')), ZERO)
                eq(signed, direct)
                le(plus, 690*m*m*L**4)
                le(minus, u)
                le(abs(signed), plus+minus)
                le(plus+minus, 828*m*m*L**4)
                counts['positive_kernel_cases'] += 1
                rows['branches'].append(dict(n=n, origin=origin, phase=i,
                    active_absolute=float(plus), clean_absolute=float(minus), signed=float(signed),
                    active_sha256=fingerprint(plus), clean_sha256=fingerprint(minus)))

        word = s.values(s.corner, 'RORR')[0]
        omitted = s.values(s.corner, '@outer')[0]
        missing = beta*s.values(s.corner, 'R')[0]
        eq(word, omitted+missing)
        eq(s.values(s.corner)[0], 1/s.q)
        eq(fingerprint(word), refs[n]['coefficient_sha256'])
        counts['published_word_matches'] += 1
        bound = F(1024*m**3*L**4)/s.q
        le(abs(word), bound)
        le(bound, 3932160000*n**8)
        rows['words'].append(dict(n=n, word='RORR', value=float(word), rational_sha256=fingerprint(word),
            baseline_contribution=float(missing), baseline_sha256=fingerprint(missing),
            invalid_baseline_omission=float(omitted), omission_sha256=fingerprint(omitted),
            bound=float(bound), ratio=float(abs(word)/bound)))
        print(json.dumps(dict(stage='word', n=n, value=float(word))), flush=True)
        s.clear()
    for name, data in rows.items():
        write_csv(out/(name+'.csv'), data)
    result = dict(status='mechanically checked', arithmetic='exact fractions; float fields display only',
        ns=ns, scope='Every phase, regular target and orphan value from corner/aligned origins; every child at n=4, children {0,k,n} at n=6. Additional states are computed recursively, not claimed as exhaustive checks.',
        counts=counts, scientific_trajectories=0, scientific_seeds=[],
        independent_method='New direct circular first-change recurrence; no earlier solver imports. Published hashes are comparison targets only.')
    (out/'verification.json').write_text(json.dumps(result, indent=2, sort_keys=True)+'\n')
    return result


if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--repo', type=Path, default=Path('.'))
    p.add_argument('--out', type=Path, required=True)
    p.add_argument('--ns', nargs='+', type=int, default=[4, 6])
    a = p.parse_args()
    print(json.dumps(verify(a.repo.resolve(), a.out, a.ns)), flush=True)
