"""Independent literal-bitstring oracle and exhaustive small transition laws."""

from collections import defaultdict
from fractions import Fraction
import itertools
import numpy as np
import pytest

from moead.kernel import transition, cost


def flip_by_rank(bits, uniform):
    # Order ones first, then zeros. Uniform rank still picks a UNIFORM bit,
    # and couples its weight effect to the count-space uniform exactly.
    ordered = np.r_[np.flatnonzero(bits == 1), np.flatnonzero(bits == 0)]
    output = bits.copy()
    output[ordered[min(int(uniform * len(bits)), len(bits) - 1)]] ^= 1
    return output


def oracle_turn(population, stored, k, r, p, um, ug, un):
    n = population.shape[1]
    child = flip_by_rank(population[k], um)
    evaluation_copy = flip_by_rank(child, un) if ug < p else child.copy()
    vector = (int(evaluation_copy.sum()), int((1 - evaluation_copy).sum()))
    accepted_zero = False
    for j in range(n + 1):
        if abs(j - k) > r:
            continue
        proposed = max(j * vector[1], (n - j) * vector[0])
        previous = max(j * (n - stored[j]), (n - j) * stored[j])
        if proposed <= previous:
            population[j] = child.copy()
            stored[j] = vector[0]
            accepted_zero |= j == 0
    return accepted_zero


@pytest.mark.parametrize('n', [1, 2, 3, 7])
@pytest.mark.parametrize('p', [0.0, 0.2, 1.0])
def test_trajectories_against_bitstring_oracle(n, p):
    for r in sorted({0, 1, n}):
        rng = np.random.default_rng(500 + n + r)
        pop = rng.integers(0, 2, (n + 1, n), dtype=np.int64)
        weights = pop.sum(axis=1)
        observed = weights.copy()
        for j in range(n + 1):
            if rng.random() < p:
                observed[j] = flip_by_rank(pop[j], rng.random()).sum()
        stored_ref = observed.copy()
        counts = np.bincount(weights, minlength=n + 1)
        first_hit = np.where(weights == np.arange(n + 1), n + 1, -1)
        wrong = int(np.sum(weights != np.arange(n + 1)))
        stored_wrong = int(np.sum(observed != np.arange(n + 1)))
        distinct = int(np.count_nonzero(counts))
        certified = False
        for t in range(100):
            k = t % (n + 1)
            um, ug, un = rng.random(3)
            before = np.array([cost(n, j, observed[j]) for j in range(n + 1)])
            previous_true = weights.copy()
            delta = transition(n, r, k, p, um, ug, un, weights, observed,
                               counts, first_hit, n + 2 + t)
            accepted = oracle_turn(pop, stored_ref, k, r, p, um, ug, un)
            np.testing.assert_array_equal(weights, pop.sum(axis=1))
            np.testing.assert_array_equal(observed, stored_ref)
            np.testing.assert_array_equal(counts, np.bincount(weights, minlength=n + 1))
            assert accepted == delta[3]
            wrong, stored_wrong, distinct = wrong + delta[0], stored_wrong + delta[1], distinct + delta[2]
            assert wrong == np.sum(weights != np.arange(n + 1))
            assert stored_wrong == np.sum(observed != np.arange(n + 1))
            assert distinct == np.count_nonzero(counts)
            assert np.all(np.abs(weights - observed) <= 1)
            assert np.all([cost(n, j, observed[j]) <= before[j] for j in range(n + 1)])
            if p == 0:
                assert np.all(weights[previous_true == np.arange(n + 1)] ==
                              previous_true[previous_true == np.arange(n + 1)])
                certified |= accepted
                if certified:
                    s = weights[0]
                    for j in range(r + 1):
                        assert cost(n, j, observed[j]) <= cost(n, j, s)
                        if j >= s:
                            assert weights[j] >= s
                        if j <= s:
                            assert weights[j] <= s


@pytest.mark.parametrize('n', range(1, 7))
def test_enumerated_mutation_and_noise_laws(n):
    # Enumerate actual uniform mutation/noise bit choices using Fractions.
    for weight in range(n + 1):
        bits = np.array([1] * weight + [0] * (n - weight))
        for p in [Fraction(0), Fraction(1, 3), Fraction(1)]:
            literal = defaultdict(Fraction)
            formula = defaultdict(Fraction)
            for m in range(n):
                child = bits.copy()
                child[m] ^= 1
                w = int(child.sum())
                literal[w, w] += (1 - p) / n
                for b in range(n):
                    noisy = child.copy()
                    noisy[b] ^= 1
                    literal[w, int(noisy.sum())] += p / (n * n)
            for child, prob in [(weight - 1, Fraction(weight, n)),
                                (weight + 1, Fraction(n - weight, n))]:
                if not prob:
                    continue
                formula[child, child] += prob * (1 - p)
                if child:
                    formula[child, child - 1] += prob * p * Fraction(child, n)
                if child < n:
                    formula[child, child + 1] += prob * p * Fraction(n - child, n)
            assert {k: v for k, v in literal.items() if v} == {k: v for k, v in formula.items() if v}
            assert sum(literal.values()) == 1


def test_exhaustive_small_noiseless_certification_after_acceptance():
    n = 2
    for initial in itertools.product(range(n + 1), repeat=n + 1):
        for r in range(n + 1):
            for k in range(r + 1):
                for u in (0.01, 0.49, 0.99):
                    weights = np.array(initial, dtype=np.int64)
                    observed = weights.copy()
                    counts = np.bincount(weights, minlength=n + 1)
                    first = np.full(n + 1, -1, dtype=np.int64)
                    accepted = transition(n, r, k, 0.0, u, 0.5, 0.5,
                                          weights, observed, counts, first, 4)[3]
                    if accepted:
                        for j in range(r + 1):
                            assert cost(n, j, weights[j]) <= cost(n, j, weights[0])
