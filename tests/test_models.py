from __future__ import annotations

import sys
import time
import unittest
from pathlib import Path
from unittest import mock

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import large  # noqa: E402
import sim  # noqa: E402


class NoiselessModelTests(unittest.TestCase):
    def test_cost_has_unique_target_minimum(self) -> None:
        for n in range(1, 31):
            costs = large.cost_table(n)
            for target in range(n + 1):
                minimizers = np.flatnonzero(costs[target] == costs[target].min())
                self.assertEqual(minimizers.tolist(), [target])

    def test_radius_neighborhoods_are_reciprocal(self) -> None:
        for n in range(1, 25):
            for radius in range(n + 1):
                intervals = large.neighbourhoods(n, radius)
                for left in range(n + 1):
                    a, b = intervals[left]
                    for right in range(n + 1):
                        c, d = intervals[right]
                        self.assertEqual(a <= right < b, c <= left < d)

    def test_seeded_run_is_deterministic(self) -> None:
        first = large.run(n=20, r=2, seed=123, track=True, max_sweeps=20_000)
        second = large.run(n=20, r=2, seed=123, track=True, max_sweeps=20_000)
        self.assertEqual(first["sweeps"], second["sweeps"])
        self.assertEqual(first["level_time"], second["level_time"])
        np.testing.assert_array_equal(first["solve"], second["solve"])
        self.assertEqual(first["J_checks"], second["J_checks"])
        self.assertEqual(first["J_viol"], second["J_viol"])
        self.assertEqual(first["censored"], second["censored"])
        self.assertFalse(first["censored"])

    def test_completion_on_last_allowed_sweep_is_not_censored(self) -> None:
        result = large.run(n=2, r=0, seed=0, max_sweeps=3)
        self.assertFalse(result["censored"])
        self.assertEqual(result["sweeps"], 3)

    def test_expired_deadline_censors_before_work(self) -> None:
        result = large.run(n=10, r=1, seed=0, deadline=time.monotonic() - 1)
        self.assertTrue(result["censored"])
        self.assertEqual(result["censor_reason"], "wall_time")

    def test_deadline_crossed_during_final_work_is_censored(self) -> None:
        original = large.np.flatnonzero

        def slow_flatnonzero(values):
            time.sleep(0.03)
            return original(values)

        with mock.patch.object(large.np, "flatnonzero", side_effect=slow_flatnonzero):
            result = large.run(
                n=1,
                r=0,
                seed=0,
                max_sweeps=5,
                deadline=time.monotonic() + 0.01,
            )
        self.assertTrue(result["censored"])
        self.assertEqual(result["censor_reason"], "wall_time")


class NoisyModelTests(unittest.TestCase):
    def test_requested_neighborhood_cardinality(self) -> None:
        for n in range(1, 20):
            for size in range(1, n + 2):
                neighborhoods = sim.build_neighborhoods(n, size)
                self.assertTrue(all(len(set(group)) == size for group in neighborhoods))

    def test_simplified_scalarization_targets_index(self) -> None:
        for target in range(20):
            values = [sim.g_from_k(weight, target) for weight in range(20)]
            self.assertEqual(int(np.argmin(values)), target)

    def test_front_coverage_is_simultaneous(self) -> None:
        population = [
            np.array([0, 0, 0], dtype=np.int8),
            np.array([1, 0, 0], dtype=np.int8),
            np.array([1, 1, 0], dtype=np.int8),
            np.array([1, 1, 1], dtype=np.int8),
        ]
        self.assertTrue(sim.front_covered(population))
        population[1] = np.array([0, 0, 0], dtype=np.int8)
        self.assertFalse(sim.front_covered(population))

    def test_small_noiseless_alignment_run(self) -> None:
        result = sim.simulate_moead(
            n=5,
            p=0.0,
            T=1,
            stop_rule="aligned",
            max_gens=20_000,
            rng=np.random.default_rng(321),
        )
        self.assertTrue(result["converged"])

    def test_invalid_stop_rule_fails_before_simulation(self) -> None:
        with self.assertRaises(ValueError):
            sim.simulate_moead(n=5, p=0.0, T=1, stop_rule="historical")

    def test_expired_deadline_censors_noisy_run(self) -> None:
        result = sim.simulate_moead(
            n=5,
            p=0.0,
            T=1,
            stop_rule="aligned",
            deadline=time.monotonic() - 1,
            rng=np.random.default_rng(7),
        )
        self.assertFalse(result["converged"])
        self.assertEqual(result["censor_reason"], "wall_time")

    def test_deadline_crossed_during_evaluation_is_censored(self) -> None:
        original = sim.noisy_k
        calls = 0

        def delayed_noisy_k(x, p, rng):
            nonlocal calls
            calls += 1
            if calls == 3:
                time.sleep(0.03)
            return original(x, p, rng)

        with mock.patch.object(sim, "noisy_k", side_effect=delayed_noisy_k):
            result = sim.simulate_moead(
                n=1,
                p=0.0,
                T=1,
                stop_rule="aligned",
                max_gens=5,
                rng=np.random.default_rng(1),
                deadline=time.monotonic() + 0.01,
            )
        self.assertFalse(result["converged"])
        self.assertEqual(result["censor_reason"], "wall_time")


if __name__ == "__main__":
    unittest.main()
