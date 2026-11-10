#!/usr/bin/env python3
"""Exact RORR checks in the supplied pinned, even-n, filled-T=2 model.

New ordered sweep/suffix implementation; imports no earlier solver for its
answers. The separately published phase solver is loaded only as an oracle.
No RNG, stochastic trajectories, fitted laws or experimental holdout access.
"""
import argparse
import csv
from fractions import Fraction as F
from functools import lru_cache
import hashlib
import importlib.util
import json
from math import comb
from pathlib import Path
import sys
import time

if hasattr(sys, 'set_int_max_str_digits'):
    sys.set_int_max_str_digits(0)
ZERO = F(0)


def put(s, k, x):
    return s[:k]+(x,)+s[k+1:]


def digest(value):
    return hashlib.sha256(str(value).encode()).hexdigest()


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_csv(path, rows):
    with path.open('w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def load_oracle(repo):
    prior = repo/'research/reports/large-T-20261109/followup/round-0014'
    manifest = json.loads((prior/'provenance.json').read_text())
    for name, expected in manifest['artifacts_sha256'].items():
        assert sha(prior/name) == expected, name
    spec = importlib.util.spec_from_file_location('round19_phase_oracle', prior/'audit.py')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class Sweep:
    """Clean error deletion solves boundary equations without matrix inversion.

    suffix(e,i,prefix,tail) sums placements of the given ordered prefix in
    the remaining sweep and applies the boundary response for tail. Thus
    no two insertions use one attempt. Aligned interior states remain live.
    """
    def __init__(self, n):
        if n < 4 or n % 2:
            raise ValueError('Requires even n >= 4 and filled T=2')
        self.n, self.m, self.L = n, n+1, 20*n
        self.target = tuple(range(n+1))
        self.corner = put(self.target, 0, 2)
        self.d = tuple(tuple(F(sum(
            comb(x, lost)*comb(n-x, y-x+lost)*(n-1)**(n-y+x-2*lost)
            for lost in range(max(0, x-y), min(x, n-y)+1)), n**n)
            for y in range(n+1)) for x in range(n+1))
        self.q = 1-(1-self.d[2][0])*(1-self.d[1][0])

    def recipients(self, i):
        # This is the exact filled-cardinality parity rule, including n's edge.
        return (i, i-1 if i % 2 or i == self.n else i+1)

    def base(self, y):
        return put(self.target, self.n, y)

    @lru_cache(None)
    def row(self, s, i, letter=''):
        out = {s: F(1) if not letter else ZERO}
        for k in self.recipients(i):
            if letter and ((letter == 'O') != (k == self.n)):
                continue
            if not letter:
                v = put(s, k, k)
                if v != s:
                    a = self.d[s[i]][k]
                    out[v] = out.get(v, ZERO)+a
                    out[s] -= a
            else:
                for x, mutation in enumerate(self.d[s[i]]):
                    v = put(s, k, x)
                    if v == s:
                        continue
                    a = mutation*(self.d[x][k]-F(x == k))
                    out[v] = out.get(v, ZERO)+a
                    out[s] -= a
        return tuple((v, a) for v, a in out.items() if a)

    @lru_cache(None)
    def clean_sweep(self, s):
        dist = {s: F(1)}
        for i in range(self.m):
            nxt = {}
            for u, a in dist.items():
                for v, b in self.row(u, i):
                    nxt[v] = nxt.get(v, ZERO)+a*b
            dist = nxt
        return tuple(dist.items())

    @lru_cache(None)
    def suffix(self, s, i, prefix, tail):
        if len(prefix) > self.m-i:
            return ZERO
        if i == self.m:
            return self.boundary(s, tail) if not prefix else ZERO
        value = sum((a*self.suffix(v, i+1, prefix, tail)
                     for v, a in self.row(s, i)), ZERO)
        if prefix:
            value += sum((a*self.suffix(v, i+1, prefix[1:], tail)
                          for v, a in self.row(s, i, prefix[0])), ZERO)
        return value

    @lru_cache(None)
    def boundary(self, s, word=''):
        if s == self.target:
            return ZERO
        row = self.clean_sweep(s)
        escape = sum((a for v, a in row if v != s), ZERO)
        value = F(1) if not word else ZERO
        value += sum((a*self.boundary(v, word) for v, a in row if v != s), ZERO)
        for count in range(1, len(word)+1):
            value += self.suffix(s, 0, word[:count], word[count:])
        return value/escape

    @lru_cache(None)
    def phase(self, s, i, word=''):
        if i == 0:
            return self.boundary(s, word)
        value = F(self.m-i, self.m) if not word else ZERO
        return value+sum((self.suffix(s, i, word[:count], word[count:])
                          for count in range(len(word)+1)), ZERO)

    def centered(self, s, i, word='RR'):
        return self.phase(s, i, word)-self.phase(self.base(s[-1]), i, word)

    def g2(self, s, i):
        return sum((a*self.phase(v, (i+1) % self.m, 'R')
                    for v, a in self.row(s, i, 'R')), ZERO)

    @lru_cache(None)
    def beta(self):
        return sum((self.d[self.n][y]*self.d[y][self.n]
                    *self.boundary(self.base(y), 'RR') for y in range(self.n)), ZERO)

    @lru_cache(None)
    def gamma(self, s):
        assert s[-1] == self.n
        stay = self.centered(s, 0)
        return sum((self.d[self.n][y]*self.d[y][self.n]
                    *(self.centered(put(s, self.n, y), 0)-stay)
                    for y in range(self.n)), ZERO)

    @lru_cache(None)
    def auxiliary(self, s, label):
        """Independent backward phase solve of custom *attempt* rewards.

        visit: 1 at every orphan turn; gamma: centered O forcing at that turn;
        outer: R applied to the gamma occupation. Only correct-orphan input
        is needed. This is not the sweep-word algorithm used for RORR.
        """
        assert s[-1] == self.n
        alpha, beta = F(1), ZERO
        affines = [None]*self.m
        for i in range(self.n, -1, -1):
            nxt = (i+1) % self.m
            if label == 'visit':
                rhs = F(i == self.n)
            elif label == 'gamma':
                rhs = self.gamma(s) if i == self.n else ZERO
            elif label == 'outer':
                rhs = sum((a*self.auxiliary(v, 'gamma')[nxt]
                           for v, a in self.row(s, i, 'R')), ZERO)
            else:
                raise ValueError(label)
            stay = ZERO
            for v, a in self.row(s, i):
                if v == s:
                    stay += a
                else:
                    rhs += a*self.auxiliary(v, label)[nxt]
            alpha, beta = stay*alpha, stay*beta+rhs
            affines[i] = (alpha, beta)
        boundary = ZERO if s == self.target else beta/(1-alpha)
        return (boundary,)+tuple(a*boundary+b for a, b in affines[1:])

    def r_absolute(self, s, i):
        """Positive active and clean expectations of |G O H2| separately."""
        nxt = (i+1) % self.m
        stay = abs(self.phase(s, nxt, 'ORR'))
        active_stay, clean_stay = F(1), F(1)
        active, clean = ZERO, ZERO
        for k in self.recipients(i):
            if k == self.n:
                continue
            for x, mutation in enumerate(self.d[s[i]]):
                a = mutation*self.d[x][k]
                active += a*abs(self.phase(put(s, k, x), nxt, 'ORR'))
                active_stay -= a
            a = self.d[s[i]][k]
            clean += a*abs(self.phase(put(s, k, k), nxt, 'ORR'))
            clean_stay -= a
        assert active_stay >= 0 and clean_stay >= 0
        return active+active_stay*stay, clean+clean_stay*stay

    def clear(self):
        for name in ('row', 'clean_sweep', 'suffix', 'boundary', 'phase',
                     'beta', 'gamma', 'auxiliary'):
            getattr(self, name).cache_clear()


def check(repo, out, ns):
    out.mkdir(parents=True, exist_ok=True)
    oracle = load_oracle(repo)
    previous = repo/'research/reports/large-T-20261109/followup/round-0015'
    manifest = json.loads((previous/'provenance.json').read_text())
    assert sha(previous/'words.csv') == manifest['artifacts_sha256']['words.csv']
    refs = {(int(r['n']), r['word']): r for r in csv.DictReader((previous/'words.csv').open())}
    rows, entrances, responses, branches, shortcuts, joint = [], [], [], [], [], []
    counts = dict(identities=0, inequalities=0, phase_oracle_matches=0,
                  marked_phase_cases=0, centered_phase_cases=0,
                  baseline_phase_cases=0, prior_word_matches=0, joint_entrance_cases=0,
                  unmarked_centered_phase_cases=0)

    def equal(a, b):
        assert a == b
        counts['identities'] += 1

    def le(a, b):
        assert a <= b
        counts['inequalities'] += 1

    for n in ns:
        started = time.monotonic()
        s = Sweep(n)
        o = oracle.Phase(n)
        m, L = s.m, s.L
        beta = s.beta()
        for y in range(n+1):
            d = s.d[y][n]
            c = s.d[n][y]*d if y < n else ZERO
            raw = s.boundary(s.base(y), 'RR')
            bound = F(10*m*m*L*L, 1)/d if y < n else ZERO
            le(abs(raw), bound)
            for i in range(m):
                le(abs(s.g2(s.base(y), i)), 10*m*L*L)
                equal(s.phase(s.base(y), i, 'RR'), o.values(s.base(y), 'RR')[i])
                counts['baseline_phase_cases'] += 1
                counts['phase_oracle_matches'] += 1
            entrances.append(dict(n=n, y=y, acceptance=str(d), entrance=str(c),
                                  baseline_sha256=digest(raw), baseline_decimal=float(raw),
                                  accepted_baseline_decimal=float(c*raw),
                                  accepted_bound_ratio=float(abs(c*raw)/(10*m*m*L*L))))
        le(abs(beta), 10*m*m*L*L)
        for origin in (s.target, s.corner):
            for y in range(n+1):
                for i in range(m):
                    le(abs(s.centered(put(origin, n, y), i)), 64*m*m*L**3)
                    counts['unmarked_centered_phase_cases'] += 1
        print(json.dumps(dict(n=n, stage='baseline checked', beta_decimal=float(beta))), flush=True)

        # Exhaust the corner/subset + one marked overwrite family, all phases,
        # all child/target pairs, including marks that produce a correct value.
        for origin in (s.target, s.corner):
            for k in range(n):
                for x in range(n+1):
                    state = put(origin, k, x)
                    a = s.d[x][k]
                    cap = 138*m*m*L*L*(L*L+1/a)
                    centered_cap = 64*m*m*L*(L*L+1/a)
                    for y in range(n+1):
                        sy = put(state, n, y)
                        for i in range(m):
                            le(abs(s.centered(sy, i)), centered_cap)
                            counts['centered_phase_cases'] += 1
                        if y < n:
                            dy, mutation = s.d[y][n], s.d[n][y]
                            cy = mutation*dy
                            envelope = a*cy*(abs(s.boundary(sy, 'RR'))
                                             +abs(s.boundary(state, 'RR')))
                            cap2 = mutation*(10*a*m*m*L*L
                                             +128*m*m*L*dy*(a*L*L+1))
                            le(envelope, cap2)
                            counts['joint_entrance_cases'] += 1
                            joint.append(dict(n=n, origin='corner' if origin == s.corner else 'aligned',
                                              target=k, child=x, orphan=y,
                                              regular_acceptance=str(a), orphan_acceptance=str(dy),
                                              orphan_mutation=str(mutation), joint_weight=str(a*cy),
                                              absolute_envelope_sha256=digest(envelope),
                                              absolute_envelope_decimal=float(envelope),
                                              bound_decimal=float(cap2), bound_ratio=float(envelope/cap2)))
                    visit = s.auxiliary(state, 'visit')
                    centered_occupation = s.auxiliary(state, 'gamma')
                    for i in range(m):
                        raw = s.phase(state, i, 'ORR')
                        equal(raw, o.values(state, 'ORR')[i])
                        counts['phase_oracle_matches'] += 1
                        equal(visit[i], s.phase(state, i)+F(i, m))
                        equal(raw, beta*visit[i]+centered_occupation[i])
                        le(visit[i], L)
                        le(abs(raw), cap)
                        counts['marked_phase_cases'] += 1
                        responses.append(dict(n=n, origin='corner' if origin == s.corner else 'aligned',
                                              target=k, child=x, phase=i, acceptance=str(a),
                                              state=' '.join(map(str, state)),
                                              orr_sha256=digest(raw), orr_decimal=float(raw),
                                              bound_ratio=float(abs(raw)/cap),
                                              visit_decimal=float(visit[i]),
                                              centered_occupation_sha256=digest(centered_occupation[i])))
                    forcing = sum((p*s.boundary(v, 'RR') for v, p in s.row(state, n, 'O')), ZERO)
                    equal(forcing, beta+s.gamma(state))
                    le(abs(forcing), 10*m*m*L*L+2*centered_cap)

        print(json.dumps(dict(n=n, stage='marked continuations checked',
                              identities=counts['identities'], inequalities=counts['inequalities'])), flush=True)

        for state in (s.target, s.corner):
            for i in range(m):
                raw = s.phase(state, i, 'ORR')
                le(abs(raw), 138*m*m*L**4)
                active, clean = s.r_absolute(state, i)
                le(active, 690*m*m*L**4)
                le(clean, 138*m*m*L**4)
                forcing = sum((a*s.phase(v, (i+1) % m, 'ORR')
                               for v, a in s.row(state, i, 'R')), ZERO)
                le(abs(forcing), 828*m*m*L**4)
                branches.append(dict(n=n, state=' '.join(map(str, state)), phase=i,
                                     active_absolute=float(active), clean_absolute=float(clean),
                                     forcing_decimal=float(forcing), forcing_sha256=digest(forcing),
                                     active_bound_ratio=float(active/(690*m*m*L**4)),
                                     clean_bound_ratio=float(clean/(138*m*m*L**4))))

        value = s.boundary(s.corner, 'RORR')
        independent = o.values(s.corner, 'RORR')[0]
        equal(value, independent)
        counts['phase_oracle_matches'] += 1
        bound = F(1024*m**3*L**4, 1)/s.q
        le(abs(value), bound)
        if (n, 'RORR') in refs:
            equal(digest(value), refs[n, 'RORR']['coefficient_sha256'])
            counts['prior_word_matches'] += 1
        missing = beta*s.boundary(s.corner, 'R')
        omitted = s.auxiliary(s.corner, 'outer')[0]
        equal(value, omitted+missing)
        assert missing != 0
        shortcuts.append(dict(n=n, beta_sha256=digest(beta), beta_decimal=float(beta),
                              first_r_sha256=digest(s.boundary(s.corner, 'R')),
                              first_r_decimal=float(s.boundary(s.corner, 'R')),
                              omitted_baseline_value=float(omitted), omitted_baseline_sha256=digest(omitted),
                              missing_term=float(missing), missing_term_sha256=digest(missing)))
        rows.append(dict(n=n, word='RORR', coefficient_decimal=float(value),
                         coefficient_sha256=digest(value), polynomial_bound=str(bound),
                         bound_ratio=float(abs(value)/bound), independent_phase_match=True,
                         arithmetic='exact rational'))
        # Save completed finite prefixes privately; the enclosing reproduction
        # publishes nothing unless the entire declared grid succeeds.
        for name, table in (('words.csv', rows), ('entrance.csv', entrances),
                            ('responses.csv', responses), ('branches.csv', branches),
                            ('shortcuts.csv', shortcuts), ('joint.csv', joint)):
            write_csv(out/name, table)
        print(json.dumps(dict(n=n, completed=True, rorr_decimal=float(value),
                              elapsed_seconds=time.monotonic()-started)), flush=True)
        s.clear()
        o.clear()

    for name, table in (('words.csv', rows), ('entrance.csv', entrances),
                        ('responses.csv', responses), ('branches.csv', branches),
                        ('shortcuts.csv', shortcuts), ('joint.csv', joint)):
        write_csv(out/name, table)
    result = dict(status='mechanically checked', ns=ns,
                  arithmetic='exact rational; decimals are presentation only',
                  scientific_trajectories=0, scientific_seeds=[],
                  scope='All corner/aligned origins, one regular overwrite target and child, all phases and orphan values at the listed even n. Not an all-population or all-n enumeration.',
                  solver='New ordered sweep/suffix solver, matched to the published round-14 direct phase solver. Independent custom forcing recurrence checks the baseline decomposition.',
                  **counts)
    (out/'verification.json').write_text(json.dumps(result, indent=2, sort_keys=True)+'\n')
    print(json.dumps(result), flush=True)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--repo', type=Path, default=Path('.'))
    parser.add_argument('--out', type=Path, required=True)
    parser.add_argument('--n', type=int, nargs='+', default=[4, 6])
    args = parser.parse_args()
    check(args.repo.resolve(), args.out.resolve(), args.n)
