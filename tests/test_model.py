import math
import numpy as np
import pytest

from moead import Config, simulate
from moead.kernel import cost, fast_trajectory, transition
from moead.model import neighborhood
from moead.frontier import simulate_frontier


@pytest.mark.parametrize('n', range(1, 13))
def test_scalarization_exact_unique_optima(n):
    for j in range(n + 1):
        values = [cost(n, j, w) for w in range(n + 1)]
        assert values.index(min(values)) == j
        assert values.count(min(values)) == 1
        for w in range(n + 1):
            gap = j * (j - w) if w < j else (n - j) * (w - j)
            assert cost(n, j, w) == j * (n - j) + gap


@pytest.mark.parametrize('n', range(1, 13))
def test_neighborhood_symmetry_and_clipping(n):
    for r in range(n + 1):
        sizes = []
        for k in range(n + 1):
            neighbors = list(neighborhood(n, r, k))
            assert k in neighbors
            assert len(neighbors) == min(n, k + r) - max(0, k - r) + 1
            sizes.append(len(neighbors))
            for j in neighbors:
                assert k in neighborhood(n, r, j)
        config = Config(n, r)
        assert max(sizes) == config.max_neighborhood_size
        assert len(neighborhood(n, r, 0)) == r + 1
        if r == n:
            assert set(sizes) == {n + 1}
            assert config.nominal_width == 2 * n + 1  # NOT actual size!


@pytest.mark.parametrize('kwargs', [
    dict(n=0), dict(n=True), dict(radius=-1), dict(radius=11),
    dict(noise_probability=-0.1), dict(noise_probability=1.01),
    dict(noise_probability=float('nan')), dict(noise_probability=float('inf')),
    dict(seed=-1), dict(seed=1.5), dict(max_evaluations=10)])
def test_reject_invalid_configuration(kwargs):
    arguments = dict(n=10, radius=1)
    arguments.update(kwargs)
    with pytest.raises(ValueError):
        Config(**arguments)


@pytest.mark.parametrize('n', [1, 3, 8, 20])
@pytest.mark.parametrize('p', [0.0, 0.1, 0.7, 1.0])
@pytest.mark.parametrize('radius_kind', ['self', 'local', 'global'])
def test_python_numba_replay(n, p, radius_kind):
    if fast_trajectory is None:
        pytest.skip('optional accelerator not installed')
    radius = {'self': 0, 'local': 1, 'global': n}[radius_kind]
    config = Config(n, radius, p, seed=1234, max_evaluations=1500, diagnostics=True)
    a, b = simulate(config, 'python'), simulate(config, 'numba')
    for field in a.__dataclass_fields__:
        if field == 'engine':
            continue
        left, right = getattr(a, field), getattr(b, field)
        if isinstance(left, np.ndarray):
            np.testing.assert_array_equal(left, right)
        else:
            assert left == right


def test_budget_and_final_evaluation_are_not_lost():
    tiny = simulate(Config(10, 0, seed=7, max_evaluations=11), 'python')
    assert not tiny.completed and tiny.evaluations == 11
    result = simulate(Config(10, 1, seed=7, max_evaluations=10000), 'python')
    assert result.completed and result.evaluations > 11
    on_budget = simulate(Config(10, 1, seed=7, max_evaluations=result.evaluations), 'python')
    below = simulate(Config(10, 1, seed=7, max_evaluations=result.evaluations - 1), 'python')
    assert on_budget.completed and not below.completed
    assert result.front_hit <= result.evaluations
    assert result.stored_hit == result.evaluations  # p=0, exact assignment
    np.testing.assert_array_equal(result.weights, np.arange(11))


def test_absolute_distance_is_not_tchebycheff():
    assert abs(0 - 1) == abs(2 - 1)
    assert cost(10, 1, 0) < cost(10, 1, 2)


@pytest.mark.parametrize('n', [1, 2, 7, 20])
@pytest.mark.parametrize('seed', range(5))
def test_frontier_exact_assignment_and_formula(n, seed):
    result = simulate_frontier(Config(n, 1, seed=seed, max_evaluations=100000))
    assert result['completed']
    np.testing.assert_array_equal(result['weights'], np.arange(n + 1))
    w = result['initial_weight']
    expected = 1 + n * sum(1 / s for s in range(1, w + 1))
    expected += n * sum(1 / s for s in range(1, n - w + 1))
    expected -= int(0 < w < n)  # Shared initial parent: either mutation extends.
    assert result['conditional_expected_evaluations'] == pytest.approx(expected)


def test_frontier_rejects_noise_and_disconnected_neighborhood():
    for config in [Config(10, 0), Config(10, 1, 0.01)]:
        with pytest.raises(ValueError):
            simulate_frontier(config)


def test_frontier_harmonic_formula_for_distinct_boundaries():
    # Singleton states have a different equation; test_frontier_regression.py
    # covers those as well, using exact rational arithmetic and a bitstring oracle.
    for n in range(1, 12):
        h = [0.0] + [sum(1 / i for i in range(1, k + 1)) for k in range(1, n + 1)]
        for left in range(n + 1):
            for right in range(left + 1, n + 1):
                value = n * (h[left] + h[n - right])
                choices = int(left > 0) + int(right < n)
                if not choices:
                    assert value == 0
                    continue
                rhs = 1.0
                if left > 0:
                    rhs += ((left / n) * n * (h[left - 1] + h[n - right])
                            + (1 - left / n) * value) / choices
                if right < n:
                    rhs += (((n - right) / n) * n * (h[left] + h[n - right - 1])
                            + (right / n) * value) / choices
                assert math.isclose(value, rhs, abs_tol=1e-12)
