"""A SEPARATE noiseless, single-initial-solution, frontier-scheduled variant.

This is a scheduling baseline, not evidence about cyclic MOEA/D under noise.
"""

import numpy as np
from .kernel import transition
from .model import Config


def simulate_frontier(config: Config) -> dict:
    if config.noise_probability != 0 or config.radius < 1:
        raise ValueError("frontier baseline requires p=0 and radius>=1")
    n = config.n
    rng = np.random.Generator(np.random.PCG64(config.seed))
    initial = int(rng.binomial(n, 0.5))
    weights = np.full(n + 1, initial, dtype=np.int64)
    observed = weights.copy()
    counts = np.zeros(n + 1, dtype=np.int64)
    counts[initial] = n + 1
    first_hit = np.full(n + 1, -1, dtype=np.int64)
    first_hit[initial] = 1
    left = right = initial
    evaluations, comparisons = 1, 0  # one evaluated solution, reused in all slots
    while (left > 0 or right < n) and evaluations < config.max_evaluations:
        choose_left = left > 0 and (right == n or rng.random() < 0.5)
        k = left if choose_left else right
        evaluations += 1
        result = transition(n, config.radius, k, 0.0, rng.random(), 1.0, 0.0,
                            weights, observed, counts, first_hit, evaluations)
        comparisons += result[-1]
        # Initially L=R, so BOTH scheduling choices mutate the SAME parent.
        # Even a nominally left-assigned trial can solve R+1 (and vice versa).
        # Track the actual certified interval, not the scheduled direction.
        if left > 0 and weights[left - 1] == left - 1:
            left -= 1
        if right < n and weights[right + 1] == right + 1:
            right += 1
    expected = 1.0 + n * (sum(1 / s for s in range(1, initial + 1))
                          + sum(1 / s for s in range(1, n - initial + 1)))
    # The first mutation of an interior singleton ALWAYS expands one side.
    # Its Bellman equation saves one evaluation relative to two independent
    # assigned-boundary coupon-collector sums. See docs/frontier.md.
    expected -= int(0 < initial < n)
    return dict(evaluations=evaluations, completed=left == 0 and right == n,
                comparisons=comparisons, initial_weight=initial,
                conditional_expected_evaluations=expected, weights=weights)
