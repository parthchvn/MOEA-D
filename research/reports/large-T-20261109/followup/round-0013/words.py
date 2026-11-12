#!/usr/bin/env python3
"""Recipient-word cubic decomposition and orphan cancellation certificates.

Deterministic rational identities; no RNG, fitting, or positive-noise samples.
R changes nonorphan recipients and O changes only the even-n T=2 orphan.
"""
import argparse
import csv
from fractions import Fraction as F
from functools import lru_cache
from itertools import product
import json
import hashlib
from pathlib import Path
import sys
import cubic


class Words(cubic.Response):
    def __init__(self, n):
        if n % 2 or n < 4:
            raise ValueError('even n>=4, T=2 only')
        super().__init__(n, 2, True)

    @lru_cache(None)
    def insertion(self, e, i, letter):
        if letter not in 'RO':
            raise ValueError(letter)
        targets = (self.n,) if letter == 'O' else range(self.n)
        return self.delta_targets(e, i, targets)

    @lru_cache(None)
    def value(self, e, word):
        if not e:
            return F(0)
        if not word:
            return self.h(e)
        row = self.sweep(e)
        escape = sum(p for v, p in row if v != e)
        rhs = sum(self.suffix(e, 0, word[:r], word[r:])
                  for r in range(1, len(word)+1))
        rhs += sum(p*self.value(v, word) for v, p in row if v != e)
        return rhs/escape

    @lru_cache(None)
    def suffix(self, e, i, pending, word):
        if len(pending) > self.n+1-i:
            return F(0)
        if i == self.n+1:
            return self.value(e, word) if not pending else F(0)
        answer = sum(p*self.suffix(v, i+1, pending, word)
                     for v, p in self.clean(e, i))
        if pending:
            answer += sum(p*self.suffix(v, i+1, pending[1:], word)
                          for v, p in self.insertion(e, i, pending[0]))
        return answer

    def phase(self, e, i, word):
        """Remaining-sweep coefficient, excluding the common partial time cost."""
        return sum(self.suffix(e, i, word[:r], word[r:])
                   for r in range(len(word)+1))

    @lru_cache(None)
    def occupancy(self, e, order):
        """Separate Poisson solve killed at NONORPHAN completion.

        Reward is one iff the orphan is correct at the current boundary.
        Only O noise is present. There is at most one O per sweep.
        """
        if not any(k != self.n for k, _ in e):
            return F(0)
        row = self.sweep(e)
        escape = sum(p for v, p in row if v != e)
        rhs = F(self.n not in dict(e)) if order == 0 else self.occupancy_suffix(e, 0, 1, order-1)
        rhs += sum(p*self.occupancy(v, order) for v, p in row if v != e)
        return rhs/escape

    @lru_cache(None)
    def occupancy_suffix(self, e, i, count, order):
        if i == self.n+1:
            return self.occupancy(e, order) if not count else F(0)
        out = sum(p*self.occupancy_suffix(v, i+1, count, order)
                  for v, p in self.clean(e, i))
        if count:
            out += sum(p*self.occupancy_suffix(v, i+1, count-1, order)
                       for v, p in self.insertion(e, i, 'O'))
        return out

    def clear_words(self):
        for f in (self.insertion, self.value, self.suffix,
                  self.occupancy, self.occupancy_suffix):
            f.cache_clear()
        self.clear()


def local_coefficients(n, d):
    """Orphan-only hitting coefficients by a separate dense n-state solve.

    At zero noise the transient local kernel is diagonal, so each Poisson
    solution divides by d(y,n). No full-population recursion is used.
    """
    h0 = tuple(1/d[y][n] if y != n else F(0) for y in range(n+1))
    delta = []
    for x in range(n+1):
        row = [F(0)]*(n+1)
        for y in range(n+1):
            if x != y:
                a = d[x][y]*(d[y][n]-F(y == n))
                row[y] += a
                row[x] -= a
        delta.append(row)
    out = [h0]
    for _ in range(2):
        out.append(tuple(sum(delta[x][y]*out[-1][y] for y in range(n+1))/d[x][n]
                         if x != n else F(0) for x in range(n+1)))
    return out


def excess_checks(n):
    s = Words(n)
    L, m = F(20*n), n+1
    f = local_coefficients(n, s.d)
    rows = []
    # Single additional arbitrary nonorphan error. Include the last pair,
    # which receives clean proposals from the possibly corrupted orphan.
    for k in range(n):
        for x in range(n+1):
            if x == k:
                continue
            regular = s.put(s.corner, k, x)
            a = s.d[x][k]
            for y in range(n+1):
                e = s.put(regular, n, y)
                h0 = s.h(e)
                excess = h0-f[0][y]
                assert 0 <= excess <= L
                if y != n:
                    assert excess <= s.d[y][n]*L*L
                # O response minus the local O response. This is the signed
                # cancellation needed before bounding the R-O interactions.
                h1o = s.value(e, 'O')
                excess1 = h1o-f[1][y]
                assert abs(excess1) <= 64*L*L
                h2o = s.value(e, 'OO')
                excess2 = h2o-f[2][y]
                b = 1-s.d[n][n]
                gs = [s.occupancy(e, r) for r in range(3)]
                assert excess == gs[0]
                assert excess1 == gs[1]+b*gs[0]
                assert excess2 == gs[2]+b*gs[1]+b*b*gs[0]
                assert abs(excess2) <= 512*L**3
                h1r = s.value(e, 'R')
                assert abs(h1r) <= 32*m*(L*L+1/a)
                rows.append(dict(n=n, slot=k, wrong=x, orphan=y,
                                 rational_sha256=hashlib.sha256('|'.join(map(str, (excess, excess1, excess2, h1r))).encode()).hexdigest(),
                                 excess_decimal=float(excess),
                                 excess1_decimal=float(excess1),
                                 excess2_decimal=float(excess2),
                                 first_R_decimal=float(h1r),
                                 first_R_bound_ratio=float(abs(h1r)/(32*m*(L*L+1/a))),
                                 exact_identities=True, exact_bounds=True))
    s.clear_words()
    return rows


def decompose(n):
    s = Words(n)
    rows = []
    for letters in product('RO', repeat=3):
        word = ''.join(letters)
        v = s.value(s.corner, word)
        rows.append(dict(n=n, word=word, coefficient=str(v), decimal=float(v)))
        print(json.dumps(dict(n=n, word=word, decimal=float(v))), flush=True)
    total = sum(F(row['coefficient']) for row in rows)
    assert total == s.h(s.corner, 3)
    for row in rows:
        row['rational_sha256'] = hashlib.sha256(row['coefficient'].encode()).hexdigest()
        if n > 4:
            row['coefficient'] = ''
    s.clear_words()
    return rows


def witnesses():
    rows = []
    for n in (4, 8, 16, 32):
        s = Words(n)
        # Last pair depends on orphan proposals: this is not a product-chain
        # simplification. Only the autonomous orphan hitting part is removed.
        e = s.put(s.corner, n-1, n)
        e = s.put(e, n, 0)
        f = local_coefficients(n, s.d)
        h1 = s.value(e, 'O')
        difference = h1-f[1][0]
        b = 1-s.d[n][n]
        independent = s.occupancy(e, 1)+b*s.occupancy(e, 0)
        assert difference == independent
        assert abs(difference) <= 64*(20*n)**2
        rows.append(dict(n=n, local_first=float(f[1][0]),
                         population_first=float(h1), excess_first=float(difference),
                         exact_identity=True,
                         rational_sha256=hashlib.sha256('|'.join(map(str, (f[1][0], h1, difference))).encode()).hexdigest()))
        s.clear_words()
    return rows


def write_csv(path, rows):
    with path.open('w', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def main(out, ns):
    out.mkdir(parents=True, exist_ok=True)
    rows, checks = [], []
    for n in ns:
        rows.extend(decompose(n))
        checks.extend(excess_checks(n))
    write_csv(out/'words.csv', rows)
    write_csv(out/'excess.csv', checks)
    write_csv(out/'cancellation.csv', witnesses())
    print(json.dumps(dict(status='mechanically checked', word_coefficients=len(rows),
                          excess_states=len(checks), scientific_trajectories=0)))


if __name__ == '__main__':
    if hasattr(sys, 'set_int_max_str_digits'):
        sys.set_int_max_str_digits(0)
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out', type=Path, required=True)
    parser.add_argument('--n', type=int, nargs='+', default=[4])
    args = parser.parse_args()
    main(args.out, args.n)
