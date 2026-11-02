"""Validated public simulation API for one-bit mutation and one-bit prior noise."""

from dataclasses import dataclass
import math
import numbers
import numpy as np

from .kernel import fast_trajectory, trajectory


@dataclass(frozen=True)
class Config:
    n: int
    radius: int
    noise_probability: float = 0.0
    seed: int = 0
    max_evaluations: int = 1_000_000
    diagnostics: bool = False

    def __post_init__(self):
        for name in ("n", "radius", "seed", "max_evaluations"):
            value = getattr(self, name)
            if isinstance(value, bool) or not isinstance(value, numbers.Integral):
                raise ValueError(f"{name} must be an integer")
        if not 1 <= self.n <= 1_000_000:
            raise ValueError("n must be in [1, 1000000] (int64 cost safety limit)")
        if not 0 <= self.radius <= self.n:
            raise ValueError("radius must be in [0, n]; radius=n is global")
        if self.seed < 0:
            raise ValueError("seed must be nonnegative")
        if not math.isfinite(self.noise_probability) or not 0 <= self.noise_probability <= 1:
            raise ValueError("noise_probability must be finite and in [0, 1]")
        if self.max_evaluations < self.n + 1:
            raise ValueError("budget must pay for all n+1 initial evaluations")

    @property
    def nominal_width(self):
        return 2 * self.radius + 1

    @property
    def max_neighborhood_size(self):
        return min(self.n + 1, self.nominal_width)


def neighborhood(n: int, radius: int, k: int) -> range:
    """Clipped symmetric radius neighborhood, not a shifted fixed-size window."""
    if n < 1 or not 0 <= radius <= n or not 0 <= k <= n:
        raise ValueError("invalid n, radius, or index")
    return range(max(0, k - radius), min(n, k + radius) + 1)


@dataclass
class Result:
    evaluations: int
    completed: bool
    front_hit: int
    stored_hit: int
    comparisons: int
    certificate_checks: int
    certificate_violations: int
    first_hit: np.ndarray
    level_visits: np.ndarray
    acceptance_jumps: np.ndarray
    sweep_jumps: np.ndarray
    weights: np.ndarray
    observed: np.ndarray
    engine: str


def simulate(config: Config, engine: str = "auto") -> Result:
    """Return observed runtime and an explicit completion flag (never a -1 runtime).

    Each initial individual is iid uniform on {0,1}^n, sampled exactly through
    its binomial weight. Parent fitness is not re-evaluated. The ideal reference
    (n,n) is fixed, not estimated. Check the true current population after each
    offspring evaluation; stopping is an instrumentation oracle, NOT feedback
    to parent selection or replacement.
    """
    if engine not in {"auto", "python", "numba"}:
        raise ValueError("engine must be auto, python, or numba")
    use_fast = engine == "numba" or (engine == "auto" and fast_trajectory is not None)
    if use_fast and fast_trajectory is None:
        raise RuntimeError("numba is not installed; use engine='python'")
    n, size = config.n, config.n + 1
    rng = np.random.Generator(np.random.PCG64(config.seed))
    weights = rng.binomial(n, 0.5, size=size).astype(np.int64)
    gates, directions = rng.random(size), rng.random(size)
    observed = weights.copy()
    noisy = gates < config.noise_probability
    observed[noisy] += np.where(directions[noisy] < weights[noisy] / n, -1, 1)
    function = fast_trajectory if use_fast else trajectory
    values = function(n, config.radius, float(config.noise_probability), weights,
                      observed, rng, config.max_evaluations, config.diagnostics)
    return Result(*values, weights, observed, "numba" if use_fast else "python")
