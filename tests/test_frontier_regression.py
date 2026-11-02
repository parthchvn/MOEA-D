"""Independent frontier tests, including the shared-parent singleton state."""
from fractions import Fraction
import numpy as np
import pytest
from moead.model import Config
from moead.frontier import simulate_frontier


def harmonic(k):
    return sum((Fraction(1, s) for s in range(1, k + 1)), Fraction(0))


def remaining(n, left, right):
    return n * (harmonic(left) + harmonic(n - right)) - int(0 < left == right < n)


@pytest.mark.parametrize('n', range(1, 13))
def test_exact_bellman_including_singleton(n):
    for left in range(n + 1):
        for right in range(left, n + 1):
            value = remaining(n, left, right)
            if left == 0 and right == n:
                assert value == 0
                continue
            rhs = Fraction(1)
            if left == right:
                # Both scheduler labels refer to one parent; no self-loop.
                if left:
                    rhs += Fraction(left, n) * remaining(n, left - 1, right)
                if right < n:
                    rhs += Fraction(n - right, n) * remaining(n, left, right + 1)
            else:
                choices = int(left > 0) + int(right < n)
                if left:
                    rhs += (Fraction(left, n) * remaining(n, left - 1, right)
                            + Fraction(n - left, n) * value) / choices
                if right < n:
                    rhs += (Fraction(n - right, n) * remaining(n, left, right + 1)
                            + Fraction(right, n) * value) / choices
            assert value == rhs


def literal_frontier(config):
    """Bitstrings; full solved-set recomputation; no production transition call."""
    n = config.n
    rng = np.random.Generator(np.random.PCG64(config.seed))
    initial = int(rng.binomial(n, 0.5))
    # A canonical representative is enough: bit positions are exchangeable.
    x = np.concatenate((np.ones(initial, dtype=np.int8), np.zeros(n-initial, dtype=np.int8)))
    population = np.tile(x, (n + 1, 1))
    evaluations, comparisons = 1, 0
    while evaluations < config.max_evaluations:
        weights = population.sum(axis=1)
        solved = np.flatnonzero(weights == np.arange(n + 1))
        left, right = int(solved[0]), int(solved[-1])
        np.testing.assert_array_equal(solved, np.arange(left, right + 1))
        if left == 0 and right == n:
            break
        choose_left = left > 0 and (right == n or rng.random() < 0.5)
        k = left if choose_left else right
        child = population[k].copy()
        # Uniform permutation of positions, ordered ones first, couples exactly
        # to the production weight threshold without using its transition code.
        positions = np.concatenate((np.flatnonzero(child), np.flatnonzero(child == 0)))
        child[positions[int(rng.random() * n)]] ^= 1
        evaluations += 1
        value = int(child.sum())
        for j in range(max(0, k-config.radius), min(n, k+config.radius)+1):
            comparisons += 1
            current = int(population[j].sum())
            if max(j*(n-value), (n-j)*value) <= max(j*(n-current), (n-j)*current):
                population[j] = child
    weights = population.sum(axis=1)
    return evaluations, comparisons, weights


@pytest.mark.parametrize('n', [1, 2, 3, 5, 8])
@pytest.mark.parametrize('global_radius', [False, True])
def test_frontier_matches_literal_oracle_and_actual_interval(n, global_radius):
    for seed in range(16):
        config = Config(n, n if global_radius else 1, seed=seed, max_evaluations=10000)
        result = simulate_frontier(config)
        evaluations, comparisons, weights = literal_frontier(config)
        assert result['evaluations'] == evaluations
        assert result['comparisons'] == comparisons
        np.testing.assert_array_equal(result['weights'], weights)
        assert result['completed']
        w = result['initial_weight']
        assert result['conditional_expected_evaluations'] == pytest.approx(float(1 + remaining(n, w, w)))


def test_frontier_censoring_stops_at_budget():
    config = Config(20, 1, seed=7, max_evaluations=21)
    result = simulate_frontier(config)
    assert result['evaluations'] == 21
    assert not result['completed']
