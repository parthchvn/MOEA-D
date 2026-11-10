#!/usr/bin/env python3
"""Rational bounds and the isolated even-n orphan calculation; no sampling."""
from fractions import Fraction as F
from math import comb
from second import Response, kernel


def q_value(n):
    a1 = F((n-1)**(n-1), n**n)
    a2 = F((n-1)**(n-2), n**n)
    return 1-(1-a2)*(1-a1)


def polynomial(n):
    m, ell = n+1, 6*n
    q = q_value(n)
    r2 = 2*(ell+2)*(m*m*ell+comb(m, 2))
    r3 = 2*(ell+3)*(m*m*ell+comb(m, 2))
    mixed = m*(12*ell*ell+16*ell+2)
    odd = (r2+r3)/q
    even = (r2+r3+mixed)/q + 6/q**2
    assert even <= 1536*n**5
    return dict(T3=r3/q, T2_regular=r2/q, mixed=mixed/q,
                orphan=6/q**2, gap=even if n % 2 == 0 else odd,
                parity_free=F(1536*n**5))


def norm_parameters(n):
    m = n+1
    M = m*n**n
    return m, M, q_value(n)


def norm_second(n):
    m, M, q = norm_parameters(n)
    return 8*(comb(m, 2)*M+m*m*M*M)/q


def sign_window(n, first):
    m, M, q = norm_parameters(n)
    return min(F(1, 8*m*M), abs(first)*q/(64*m*m*M*M))


def dyadic_below(value):
    """Largest power of two not exceeding a positive value <=1."""
    if not 0 < value <= 1:
        raise ValueError('Requires 0<value<=1')
    exponent = max(0, value.denominator.bit_length()-value.numerator.bit_length())
    p = F(1, 1 << exponent)
    while p > value:
        p /= 2
    while 2*p <= value:
        p *= 2
    return p


def remainder(n, p, order=2):
    """Absolute remainder in the T3-T2 gap after order 1 or 2."""
    m, M, q = norm_parameters(n)
    d = (1+2*p)**m-1
    if not 0 <= M*d < 1:
        raise ValueError('Outside certified resolvent disk')
    g = M*d/(1-M*d)-2*m*M*p
    if order == 2:
        g -= (4*comb(m, 2)*M+4*m*m*M*M)*p*p
    elif order != 1:
        raise ValueError('order must be 1 or 2')
    assert g >= 0
    return 2*g/q


def orphan(n):
    """Noise restricted to recipient n, with endpoint geometric clock q.

    Exact coefficients of G_nn(1-q)/(1-p+p D(n,n)), obtained by a Schur
    complement of the autonomous local transition matrix. See derivation.md.
    """
    d = kernel(n)
    q, s = q_value(n), 1-q_value(n)
    b = 1-d[n][n]
    death = [d[y][n] for y in range(n)]
    c = [d[n][y]*death[y] for y in range(n)]
    a = sum(c)
    f = [q+s*death[y] for y in range(n)]
    # L is the p coefficient of the transient local (own-turn) matrix.
    L = []
    for y in range(n):
        row = [d[y][z]*d[z][n] if z != y else F(0) for z in range(n)]
        row[y] = b*death[y]-sum(row)
        L.append(row)
    C0 = sum(c[y]*death[y]/f[y] for y in range(n))
    C1 = sum(c[y]*L[y][z]*death[z]/(f[y]*f[z])
             for y in range(n) for z in range(n))
    first = sum(d[n][y]/f[y] for y in range(n))
    F2 = -b*s*a+2*b*s*s*C0-s**3*C1
    second = q*first*first-F2/q**2
    assert abs(second) <= 6/q**2
    return dict(first=first, second=second)


class Restricted(Response):
    def __init__(self, n, t, targets):
        super().__init__(n, t)
        self.targets = set(targets)

    def delta(self, e, i):
        return self.delta_targets(e, i, self.targets)


def local_reversibility(n):
    """Exact coefficient identities in detailed balance, at a rational p."""
    d, p = kernel(n), F(1, 7*n)
    nu = [(1-p)*int(y == n)+p*d[n][y] for y in range(n+1)]
    for x in range(n+1):
        for y in range(n+1):
            if x == y:
                continue
            nx = (1-p)*int(x == n)+p*d[x][n]
            ny = (1-p)*int(y == n)+p*d[y][n]
            assert nu[x]*d[x][y]*ny == nu[y]*d[y][x]*nx
    return (n+1)*n
