"""Exact weight-space transitions, with optional (not fastmath) JIT acceleration.

The Python implementation is the reference execution path. No random-number
seed, population state, or experiment is created at import time.
"""

import numpy as np

try:
    from numba import njit
    from numba.extending import register_jitable
except ImportError:  # The package works without the optional accelerator.
    njit = None

    def register_jitable(function):
        return function


@register_jitable
def cost(n, j, weight):
    """n times ideal-reference Tchebycheff cost; all comparisons are integral."""
    return max(j * (n - weight), (n - j) * weight)


@register_jitable
def transition(n, radius, k, p, u_mut, u_gate, u_noise,
               weights, observed, counts, first_hit, evaluation):
    """Mutate x_k, evaluate once, broadcast the SAME observation to B(k).

    Arrays are updated in place. Uniforms belong to [0,1). Return changes to
    wrong-true, wrong-stored and distinct-weight counters, whether slot zero
    accepted, and the number of scalar comparisons. No stopping is done here.
    """
    parent = weights[k]
    child = parent - 1 if u_mut < parent / n else parent + 1
    value = child
    if u_gate < p:
        value += -1 if u_noise < child / n else 1
    wrong_delta = 0
    stored_delta = 0
    distinct_delta = 0
    accepted_zero = False
    lo, hi = max(0, k - radius), min(n, k + radius)
    for j in range(lo, hi + 1):
        if cost(n, j, value) <= cost(n, j, observed[j]):
            old = weights[j]
            wrong_delta += int(child != j) - int(old != j)
            stored_delta += int(value != j) - int(observed[j] != j)
            counts[old] -= 1
            if counts[old] == 0:
                distinct_delta -= 1
            if counts[child] == 0:
                distinct_delta += 1
            counts[child] += 1
            weights[j], observed[j] = child, value
            if child == j and first_hit[j] < 0:
                first_hit[j] = evaluation
            if j == 0:
                accepted_zero = True
    return wrong_delta, stored_delta, distinct_delta, accepted_zero, hi - lo + 1


def trajectory(n, radius, p, weights, observed, rng, budget, diagnostics):
    """Run cyclic self-parent MOEA/D; budget INCLUDES initial n+1 evaluations."""
    size = n + 1
    counts = np.zeros(size, dtype=np.int64)
    first_hit = np.full(size, -1, dtype=np.int64)
    wrong = stored_wrong = distinct = 0
    for j in range(size):
        counts[weights[j]] += 1
        wrong += int(weights[j] != j)
        stored_wrong += int(observed[j] != j)
        if weights[j] == j:
            first_hit[j] = size
    for count in counts:
        distinct += int(count > 0)
    front_hit = size if distinct == size else -1
    stored_hit = size if stored_wrong == 0 else -1
    evaluations = size
    comparisons = checks = violations = 0
    certified = False
    level_visits = np.zeros(size, dtype=np.int64)
    acceptance_jumps = np.zeros(size, dtype=np.int64)
    sweep_jumps = np.zeros(size, dtype=np.int64)
    sweep_start = weights[0]
    while evaluations < budget and wrong > 0:
        k = (evaluations - size) % size
        if k == 0:
            sweep_start = weights[0]
            if diagnostics:
                level_visits[sweep_start] += 1
        before = weights[0]
        evaluations += 1
        d1, d2, d3, accepted, comparisons_now = transition(
            n, radius, k, p, rng.random(), rng.random(), rng.random(),
            weights, observed, counts, first_hit, evaluations)
        wrong += d1
        stored_wrong += d2
        distinct += d3
        comparisons += comparisons_now
        if p == 0.0 and accepted:
            certified = True
        if diagnostics and p == 0.0 and weights[0] < before:
            acceptance_jumps[before - weights[0]] += 1
        if stored_hit < 0 and stored_wrong == 0:
            stored_hit = evaluations
        if front_hit < 0 and distinct == size:
            front_hit = evaluations
        if k == n:
            if diagnostics and p == 0.0:
                sweep_jumps[sweep_start - weights[0]] += 1
            # A deterministic skip of the first two sweeps is NOT a certificate.
            # Check only after an actual acceptance by endpoint zero, at p=0.
            if p == 0.0 and certified:
                checks += 1
                failed = False
                s = weights[0]
                for j in range(radius + 1):
                    if cost(n, j, observed[j]) > cost(n, j, s):
                        failed = True
                    if j >= s and weights[j] < s:
                        failed = True
                    if j <= s and weights[j] > s:
                        failed = True
                violations += int(failed)
    return (evaluations, wrong == 0, front_hit, stored_hit, comparisons,
            checks, violations, first_hit, level_visits,
            acceptance_jumps, sweep_jumps)


fast_trajectory = njit(cache=True)(trajectory) if njit is not None else None
