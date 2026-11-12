#!/usr/bin/env python3
"""Round 18: independent uncentered response and support audit. No sampling.

No earlier solver is imported. All scientific decisions use Fraction equality.
The raw Bellman solver first sums a complete clean cycle's forcing forward,
then recovers interior phases backwards. Centering is performed only AFTER
the raw response has been solved. This differs from round 17's directly
centered, regular-killed solver.
"""
import argparse
import csv
from fractions import Fraction as F
from functools import lru_cache
import hashlib
from itertools import combinations, product
import json
from math import comb
from pathlib import Path
import sys

if hasattr(sys, 'set_int_max_str_digits'):
    sys.set_int_max_str_digits(0)
Z = F(0)


def put(s, k, x):
    a = list(s)
    a[k] = x
    return tuple(a)


def fingerprint(value):
    return hashlib.sha256(str(value).encode()).hexdigest()


def write_csv(path, rows):
    with path.open('w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)


class Raw:
    def __init__(self, n):
        if n < 4 or n % 2:
            raise ValueError('Only even n >= 4 and filled T=2')
        self.n, self.m, self.L = n, n+1, 20*n
        self.target = tuple(range(n+1))
        self.corner = put(self.target, 0, 2)
        # Coefficient convolution: surviving ones plus gained zeros.
        self.d = []
        for x in range(n+1):
            numerator = [0]*(n+1)
            for kept in range(x+1):
                for gained in range(n-x+1):
                    numerator[kept+gained] += (comb(x, kept)*comb(n-x, gained)
                                              *(n-1)**(kept+n-x-gained))
            self.d.append(tuple(F(v, n**n) for v in numerator))
        self.d = tuple(self.d)
        self.q = 1-(1-self.d[2][0])*(1-self.d[1][0])

    def recipients(self, i):
        # Literal alternating filled-cardinality construction, not radius.
        order = (-1, 1) if i % 2 else (1, -1)
        for sign in order:
            if 0 <= i+sign <= self.n:
                return (i, i+sign)
        raise AssertionError('No adjacent slot')

    def base(self, y):
        return put(self.target, self.n, y)

    def budget(self, s):
        return sum(s[k] != k for k in range(self.n)) - int(s[0] == 2)

    def bad_pairs(self, s):
        return tuple(k for k in range(0, self.n, 2)
                     if s[k] != k and s[k+1] != k+1
                     and not (k == 0 and s[0] == 2))

    def cap(self, s):
        bad = self.bad_pairs(s)
        if len(bad) > 1:
            raise ValueError('More than one slow pair')
        if not bad:
            return F(self.L)
        k = bad[0]
        return self.L+2/(self.d[s[k]][k]+self.d[s[k+1]][k+1])

    @lru_cache(None)
    def clean(self, s, i):
        changes = tuple((put(s, k, k), self.d[s[i]][k])
                        for k in self.recipients(i) if s[k] != k)
        return ((s, 1-sum((p for _, p in changes), Z)),)+changes

    @lru_cache(None)
    def forcing(self, s, i, degree):
        """R H_(degree-1), using positive accepted birth minus stay,
        then subtracting clean repair minus stay. No centered equation here.
        """
        if degree == 0:
            return F(1, self.m)
        nxt = (i+1) % self.m
        stay = self.values(s, degree-1)[nxt]
        result = Z
        for k in self.recipients(i):
            if k == self.n:
                continue
            for child, mutation in enumerate(self.d[s[i]]):
                if child != s[k]:
                    result += (mutation*self.d[child][k]
                               *(self.values(put(s, k, child), degree-1)[nxt]-stay))
            if s[k] != k:
                result -= self.d[s[i]][k]*(self.values(put(s, k, k), degree-1)[nxt]-stay)
        return result

    @lru_cache(None)
    def values(self, s, degree):
        # Clean off-diagonal transitions strictly delete errors. Recursion
        # therefore terminates, including aligned-but-live interior phases.
        rhs, stays = [], []
        prefix, total = F(1), Z
        for i in range(self.m):
            row = self.clean(s, i)
            h = self.forcing(s, i, degree)
            h += sum((p*self.values(v, degree)[(i+1) % self.m]
                      for v, p in row[1:]), Z)
            rhs.append(h)
            stays.append(row[0][1])
            total += prefix*h
            prefix *= row[0][1]
        boundary = Z if s == self.target else total/(1-prefix)
        result = [boundary]*self.m
        following = boundary
        for i in range(self.n, 0, -1):
            following = rhs[i]+stays[i]*following
            result[i] = following
        return tuple(result)

    def centered(self, s, degree):
        return tuple(a-b for a, b in zip(self.values(s, degree),
                                         self.values(self.base(s[-1]), degree)))

    def restricted_absolute(self, s, i, degree):
        """Separate positive active/clean expectations of |D_degree|.
        These check the majorants, so signed cancellation cannot hide a
        missing acceptance factor or an omitted unchanged-state branch.
        """
        nxt = (i+1) % self.m
        baseline = self.values(self.base(s[-1]), degree)[nxt]
        def value(v):
            return abs(self.values(v, degree)[nxt]-baseline)
        active, clean = Z, Z
        active_stay, clean_stay = F(1), F(1)
        for k in self.recipients(i):
            if k == self.n:
                continue
            for x, mutation in enumerate(self.d[s[i]]):
                mass = mutation*self.d[x][k]
                active += mass*value(put(s, k, x))
                active_stay -= mass
            mass = self.d[s[i]][k]
            clean += mass*value(put(s, k, k))
            clean_stay -= mass
        assert active_stay >= 0 and clean_stay >= 0
        return active+active_stay*value(s), clean+clean_stay*value(s)

    @lru_cache(None)
    def flux(self, degree):
        return sum((self.forcing(self.target, i, degree) for i in range(self.m)), Z)

    @lru_cache(None)
    def boundary_reward(self, s):
        """Independent clean occupation of 1{phase=0, orphan correct},
        killed on regular completion at ANY phase. Used only for D0 audit.
        """
        if s[:-1] == self.target[:-1]:
            return (Z,)*self.m
        rhs, stays, prefix, total = [], [], F(1), Z
        for i in range(self.m):
            row = self.clean(s, i)
            h = F(i == 0 and s[-1] == self.n)
            h += sum((p*self.boundary_reward(v)[(i+1) % self.m]
                      for v, p in row[1:]), Z)
            rhs.append(h)
            stays.append(row[0][1])
            total += prefix*h
            prefix *= row[0][1]
        result = [total/(1-prefix)]*self.m
        following = result[0]
        for i in range(self.n, 0, -1):
            following = rhs[i]+stays[i]*following
            result[i] = following
        return tuple(result)

    def orphan_action(self, s):
        result = Z
        stay = self.values(s, 3)[0]
        assert s[-1] == self.n
        for y in range(self.n):
            result += self.d[self.n][y]*self.d[y][self.n]*(
                self.values(put(s, self.n, y), 3)[0]-stay)
        return result

    def orrr(self):
        return ((1-self.q)*self.orphan_action(self.corner)
                +self.q*self.orphan_action(self.target))/self.q

    def clear(self):
        for name in ('clean', 'forcing', 'values', 'flux', 'boundary_reward'):
            getattr(self, name).cache_clear()


def geometry():
    """All abstract surviving-overwrite patterns through budget three.
    0=correct, 1=generic wrong, 2=the surviving original corner (slot 0 only).
    Wrong values do not affect this combinatorial support property.
    """
    rows = []
    for n in (4, 6, 8, 12, 20, 32):
        counts = [0]*4
        clean_edges = active_edges = 0
        for first in (0, 1, 2):
            for b in range(4-int(first == 1)):
                for wrong in combinations(range(1, n), b):
                    s = [0]*n
                    s[0] = first
                    for k in wrong:
                        s[k] = 1
                    used = b+int(first == 1)
                    counts[used] += 1

                    def valid(t, budget):
                        errors = sum(x != 0 for x in t)
                        cost = sum(x == 1 for x in t)
                        bad = sum(bool(t[k] and t[k+1])
                                  and not (k == 0 and t[0] == 2)
                                  for k in range(0, n, 2))
                        assert cost <= budget and errors <= budget+1 and bad <= 1

                    valid(s, used)
                    for k in range(n):
                        if s[k]:
                            t = s.copy()
                            t[k] = 0
                            valid(t, used)
                            clean_edges += 1
                        if used <= 2:
                            for value in ((0, 1, 2) if k == 0 else (0, 1)):
                                t = s.copy()
                                t[k] = value
                                valid(t, used+1)
                                active_edges += 1
        rows.append(dict(n=n, budget0=counts[0], budget1=counts[1],
                         budget2=counts[2], budget3=counts[3],
                         clean_edges=clean_edges, overwrite_edges=active_edges))
    return rows


def inequalities():
    rows = []
    for n in (4, 6, 8, 10, 12, 20):
        c = Raw(n)
        count = 0
        worst = Z
        for k in range(0, n, 2):
            for x in range(n+1):
                if x == k:
                    continue
                a = c.d[x][k]
                for y in range(n+1):
                    if y == k+1:
                        continue
                    b = c.d[y][k+1]
                    M = c.L+2/(a+b)
                    assert 2*a/(a+b) <= 2
                    assert b*M*M <= 2*c.L*c.L+2/a
                    assert a*b*M*M <= (c.L+1)**2
                    worst = max(worst, b*M*M/(2*c.L*c.L+2/a))
                    count += 3
        rows.append(dict(n=n, exact_inequalities=count, max_marked_ratio=float(worst),
                         max_marked_ratio_exact=str(worst)))
        c.clear()
    return rows


def audit(repo, out, ns=(4, 6)):
    out.mkdir(parents=True, exist_ok=True)
    prior = repo/'research/reports/large-T-20261109/followup/round-0017'
    published = {(int(r['n']), r['word']): r for r in csv.DictReader((prior/'words.csv').open())}
    old_centered = list(csv.DictReader((prior/'centered.csv').open()))
    states_rows, flux_rows, words_rows, entrance_rows = [], [], [], []
    counters = dict(identities=0, inequalities=0, prior_centered_matches=0,
                    state_cases=0, phase_cases=0)
    for n in ns:
        c = Raw(n)
        def check_state(s, degree, cap, label, mark=F(1),
                        active_cap=None, clean_cap=None, forcing_cap=None):
            centered = c.centered(s, degree)
            base = c.base(s[-1])
            active_ratio = clean_ratio = forcing_ratio = Z
            for i in range(c.m):
                nxt = (i+1) % c.m
                raw_rhs = (c.forcing(s, i, degree)
                           +sum((p*c.values(v, degree)[nxt] for v, p in c.clean(s, i)), Z)
                           -c.flux(degree)*F(s == c.target and i == 0))
                assert c.values(s, degree)[i] == raw_rhs
                counters['identities'] += 1
                if s[:-1] != c.target[:-1]:
                    rhs = c.flux(degree)*F(i == 0 and s[-1] == n)
                    if degree:
                        rhs += c.forcing(s, i, degree)-c.forcing(base, i, degree)
                    rhs += sum((p*c.centered(v, degree)[nxt]
                                for v, p in c.clean(s, i)), Z)
                    assert centered[i] == rhs
                    counters['identities'] += 1
                else:
                    assert centered[i] == 0
                    counters['identities'] += 1
                assert abs(centered[i]) <= cap
                counters['inequalities'] += 1
                if degree == 0:
                    assert centered[i] == c.boundary_reward(s)[i]
                    assert centered[i] >= 0
                    counters['identities'] += 1
                    counters['inequalities'] += 1
                if active_cap is not None:
                    active, clean = c.restricted_absolute(s, i, degree-1)
                    assert active <= active_cap and clean <= clean_cap
                    active_ratio = max(active_ratio, active/active_cap)
                    clean_ratio = max(clean_ratio, clean/clean_cap)
                    counters['inequalities'] += 2
                if forcing_cap is not None:
                    ratio = abs(c.forcing(s, i, degree))/forcing_cap
                    assert ratio <= 1
                    forcing_ratio = max(forcing_ratio, ratio)
                    counters['inequalities'] += 1
            states_rows.append(dict(n=n, family=label, state=' '.join(map(str, s)),
                                    degree=degree, acceptance=str(mark), phases=c.m,
                                    max_ratio=float(max(map(abs, centered))/cap),
                                    active_ratio=float(active_ratio) if active_cap is not None else '',
                                    clean_ratio=float(clean_ratio) if clean_cap is not None else '',
                                    forcing_ratio=float(forcing_ratio) if forcing_cap is not None else '',
                                    centered_sha256=fingerprint(centered)))
            counters['state_cases'] += 1
            counters['phase_cases'] += c.m

        # Exhaust all n=4 states through two surviving overwrites, including
        # nonadjacent errors. At n=6 exhaust every bad-pair/orphan value plus
        # every marked value, rather than treating them as independent.
        if n == 4:
            double = [s for s in product(range(n+1), repeat=c.m) if c.budget(s) <= 2]
        else:
            double = {c.base(y) for y in range(n+1)}
            for base in (c.target, c.corner):
                for k in range(0, n, 2):
                    for x, z, y in product(range(n+1), repeat=3):
                        if x != k and z != k+1:
                            double.add(put(put(put(base, k, x), k+1, z), n, y))
            double = sorted(double)
        for s in double:
            M = c.cap(s)
            check_state(s, 0, M, 'two-overwrite')
            check_state(s, 1, 5*c.m*M*M, 'two-overwrite',
                        active_cap=M+4, clean_cap=M, forcing_cap=M+4)
        print(json.dumps(dict(n=n, stage='raw first responses checked', **counters)), flush=True)

        for base in (c.target, c.corner):
            for y in range(n+1):
                s0 = put(base, n, y)
                check_state(s0, 2, 64*c.m*c.m*c.L**3, 'unmarked',
                            active_cap=5*c.m*c.L*c.L, clean_cap=5*c.m*c.L*c.L,
                            forcing_cap=10*c.m*c.L*c.L)
                for k, x in product(range(n), range(n+1)):
                    s = put(s0, k, x)
                    a = c.d[x][k]
                    check_state(s, 2, 64*c.m*c.m*c.L*(c.L*c.L+1/a), 'marked', a,
                                active_cap=5*c.m*(5*c.L*c.L+4/a),
                                clean_cap=5*c.m*c.L*c.L,
                                forcing_cap=32*c.m*(c.L*c.L+1/a))

        # Every published centered fingerprint is checked from raw responses,
        # including the n=6 cases that had no independent oracle previously.
        for row in old_centered:
            if int(row['n']) == n:
                s = tuple(map(int, row['state'].split()))
                j = 1 if row['marked'] == '2' else 2
                assert fingerprint(c.centered(s, j)) == row['centered_sha256']
                counters['prior_centered_matches'] += 1

        for j in (0, 1, 2):
            value = c.flux(j)
            cap = (1, c.m*c.L, 10*c.m*c.m*c.L*c.L)[j]
            assert abs(value) <= cap
            counters['inequalities'] += 1
            s, i = c.corner, 0
            omitted = (sum((p*c.centered(v, j)[1] for v, p in c.clean(s, i)), Z)
                       +(c.forcing(s, i, j)-c.forcing(c.target, i, j) if j else 0))
            residual = c.centered(s, j)[0]-omitted
            assert residual == value and value != 0
            counters['identities'] += 1
            flux_rows.append(dict(n=n, degree=j, compensation_exact=str(value),
                                  compensation_decimal=float(value),
                                  uncompensated_residual_exact=str(residual)))

        B = 512*c.m*c.m*c.L**3
        for base in (c.target, c.corner):
            for y in range(n+1):
                s = put(base, n, y)
                for i in range(c.m):
                    assert abs(c.forcing(s, i, 3)) <= B
                    active, clean = c.restricted_absolute(s, i, 2)
                    assert active <= 320*c.m*c.m*c.L**3
                    assert clean <= 64*c.m*c.m*c.L**3
                    counters['inequalities'] += 3
                response = c.values(s, 3)[0]
                d = c.d[y][n]
                cap = c.m*B*(c.L+(1/d if y != n else 0))
                assert abs(response) <= cap
                counters['inequalities'] += 1
                entrance_rows.append(dict(n=n, corner_survives=int(base == c.corner),
                                          orphan=y, repair_exact=str(d),
                                          entrance_exact=str(c.d[n][y]*d if y != n else 0),
                                          response_sha256=fingerprint(response),
                                          response_decimal=float(response),
                                          bound_ratio=float(abs(response)/cap)))
        word = c.orrr()
        bound = 2048*c.m**3*c.L**4/c.q
        assert abs(word) <= bound
        assert fingerprint(word) == published[(n, 'ORRR')]['rational_sha256']
        counters['identities'] += 1
        counters['inequalities'] += 1
        words_rows.append(dict(n=n, word='ORRR', value_decimal=float(word),
                               rational_sha256=fingerprint(word),
                               bound_exact=str(bound), bound_ratio=float(abs(word)/bound),
                               independent_match=True))
        print(json.dumps(dict(n=n, stage='complete', orrr=float(word), **counters)), flush=True)
        c.clear()

    geo, algebra = geometry(), inequalities()
    for name, rows in [('responses.csv', states_rows), ('flux.csv', flux_rows),
                       ('words.csv', words_rows), ('entrance.csv', entrance_rows),
                       ('budget.csv', geo), ('inequalities.csv', algebra)]:
        write_csv(out/name, rows)
    result = dict(status='mechanically checked', **counters,
                  support_patterns=sum(sum(r['budget'+str(i)] for i in range(4)) for r in geo),
                  support_edges=sum(r['clean_edges']+r['overwrite_edges'] for r in geo),
                  algebra_inequalities=sum(r['exact_inequalities'] for r in algebra),
                  ns=list(ns), scientific_trajectories=0, scientific_seeds=[],
                  arithmetic='exact rational; decimal fields are presentation only',
                  independence='New raw uncentered Bellman implementation; no earlier solver imported',
                  scope='All n=4 populations of overwrite budget <=2; n=6 all bad-pair and marked values, all orphan values and phases; abstract support and acceptance inequalities on additional finite n.')
    (out/'verification.json').write_text(json.dumps(result, sort_keys=True, indent=2)+'\n')
    print(json.dumps(result), flush=True)


if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--repo', type=Path, default=Path('.'))
    p.add_argument('--out', type=Path, required=True)
    p.add_argument('--ns', type=int, nargs='+', default=[4, 6])
    a = p.parse_args()
    audit(a.repo.resolve(), a.out, tuple(a.ns))
