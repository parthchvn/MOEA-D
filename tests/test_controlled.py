from __future__ import annotations

import time
import unittest
from unittest import mock

import numpy as np

import large


class InitialState:
    def __init__(self, values):
        self.values = values

    def binomial(self, n, p, size):
        assert len(self.values) == size
        return np.array(self.values)


class UniformTape:
    def __init__(self, value):
        self.value = value
        self.draws = 0

    def random(self, size):
        self.draws += size
        return np.full(size, self.value)


class ControlledModelTests(unittest.TestCase):
    def fixture(self, initial, r=0, mutation="exact", cap=None, gate=0.0, direction=0.0):
        streams = InitialState(initial), UniformTape(gate), UniformTape(direction)
        with mock.patch.object(large, "controlled_streams", return_value=streams):
            result = large.run_controlled(len(initial) - 1, r, 0, mutation,
                                          max_evaluations=cap)
        return result, streams

    def test_rejected_offspring_completes_archive_and_is_counted(self):
        result, _ = self.fixture([0, 0, 2], cap=4)
        self.assertEqual(result["archive_evaluations"], 4)
        self.assertIsNone(result["alignment_evaluations"])
        self.assertEqual(result["evaluations"], 4)
        self.assertEqual(result["observation_evaluations"], 4)
        self.assertEqual(result["rejected_offspring"], 1)
        self.assertEqual(result["rejected_new_archive_weights"], 1)
        self.assertEqual(result["censor_reason"], "max_evaluations")

    def test_initialization_archive_is_not_alignment(self):
        result, _ = self.fixture([1, 0], cap=2)
        self.assertEqual(result["archive_evaluations"], 2)
        self.assertFalse(result["archive_censored"])
        self.assertTrue(result["alignment_censored"])
        self.assertEqual(result["evaluations"], 2)

    def test_initial_alignment_counts_all_initial_evaluations(self):
        result, _ = self.fixture([0, 1], cap=2)
        self.assertEqual(result["archive_evaluations"], 2)
        self.assertEqual(result["alignment_evaluations"], 2)
        self.assertEqual(result["offspring_evaluations"], 0)

    def test_alignment_is_checked_mid_sweep_and_at_exact_cap(self):
        result, _ = self.fixture([0, 0, 2], cap=5)
        self.assertEqual(result["archive_evaluations"], 4)
        self.assertEqual(result["alignment_evaluations"], 5)
        self.assertIsNone(result["censor_reason"])

    def test_lazy_copy_can_solve_a_different_recipient(self):
        result, _ = self.fixture([1, 0, 2], r=1, mutation="lazy", cap=4)
        self.assertEqual(result["self_loop_offspring"], 1)
        self.assertEqual(result["self_loop_recipient_changes"], 1)
        self.assertEqual(result["self_loop_target_acquisitions"], 1)
        self.assertEqual(result["aligned_count"], 2)

    def test_positive_radius_can_have_strict_gap_from_incomplete_archive(self):
        # Independent evaluator witness: offspring 0,0,0,3,1,2 from initial
        # [1,1,1,2] gives archive at eval8 and alignment at eval10. Every
        # transition is a feasible one-bit move; lazy gates choose moving calls.
        for mutation in ("exact", "lazy"):
            directions = mock.Mock()
            directions.random.side_effect = [np.array([0.99, 0.99, 0.99, 0.0]),
                                              np.zeros(4)]
            streams = InitialState([1, 1, 1, 2]), UniformTape(0.9), directions
            with mock.patch.object(large, "controlled_streams", return_value=streams):
                result = large.run_controlled(3, 1, 0, mutation, max_evaluations=10)
            self.assertEqual(result["archive_evaluations"], 8)
            self.assertEqual(result["alignment_evaluations"], 10)
            self.assertIsNone(result["censor_reason"])

    def test_rng_consumption_policy_does_not_depend_on_mutation_arm(self):
        for mutation in ("exact", "lazy"):
            _, streams = self.fixture([1, 0, 2], mutation=mutation, cap=4)
            self.assertEqual(streams[1].draws, 3)
            self.assertEqual(streams[2].draws, 3)

    def test_direction_probabilities_and_lazy_gate_boundary(self):
        for n in range(1, 12):
            for weight in range(n + 1):
                for direction in (0.0, 0.2, 0.5, 0.9):
                    expected = weight + 1 if direction < (n - weight) / n else weight - 1
                    self.assertEqual(large.controlled_offspring(n, weight, "exact", 0, direction), expected)
                    self.assertEqual(large.controlled_offspring(n, weight, "lazy", 0.5, direction), expected)
                    self.assertEqual(large.controlled_offspring(n, weight, "lazy", 0.499, direction), weight)

    def test_chebyshev_is_not_absolute_distance(self):
        costs = large.cost_table(3)
        self.assertEqual(abs(0 - 1), abs(2 - 1))
        self.assertGreater(costs[1, 2], costs[1, 0])

    def test_order_preserving_paper_complement_cost_identity(self):
        for n in range(1, 15):
            costs = large.cost_table(n)
            for k in range(n + 1):
                for zeros in range(n + 1):
                    paper_piecewise = k * (n - zeros) if zeros <= k else (n - k) * zeros
                    self.assertEqual(costs[k, zeros], paper_piecewise)
                    self.assertEqual(costs[n-k, n-zeros], paper_piecewise)

    def test_small_seeded_paths_preserve_endpoint_order(self):
        for n in (2, 4, 8):
            for r in (0, 1, n):
                for mutation in ("exact", "lazy"):
                    first = large.run_controlled(n, r, 123, mutation, max_evaluations=100_000)
                    second = large.run_controlled(n, r, 123, mutation, max_evaluations=100_000)
                    self.assertEqual(first, second)
                    self.assertFalse(first["alignment_censored"])
                    self.assertLessEqual(first["archive_evaluations"], first["alignment_evaluations"])
                    self.assertEqual(first["aligned_count"], n + 1)
                    if mutation == "exact":
                        self.assertEqual(first["self_loop_offspring"], 0)

    def test_expired_deadline_preserves_finite_observed_count(self):
        result = large.run_controlled(5, 1, 0, deadline=time.monotonic() - 1)
        self.assertEqual(result["evaluations"], 0)
        self.assertEqual(result["observation_evaluations"], 0)
        self.assertEqual(result["censor_reason"], "wall_time")

    def test_work_crossing_deadline_is_censored(self):
        original = large.controlled_offspring

        def slow(*args):
            time.sleep(0.03)
            return original(*args)

        streams = InitialState([0, 0, 2]), UniformTape(0), UniformTape(0)
        with mock.patch.object(large, "controlled_streams", return_value=streams), \
                mock.patch.object(large, "controlled_offspring", side_effect=slow):
            result = large.run_controlled(2, 0, 0, deadline=time.monotonic() + 0.01)
        self.assertEqual(result["censor_reason"], "wall_time")
        self.assertEqual(result["evaluations"], 4)
        self.assertEqual(result["observation_evaluations"], 3)
        self.assertTrue(result["archive_censored"])

    def test_late_initialization_has_zero_confirmed_observation_prefix(self):
        original = InitialState.binomial

        def slow(*args, **kwargs):
            time.sleep(0.03)
            return original(*args, **kwargs)

        streams = InitialState([0, 1]), UniformTape(0), UniformTape(0)
        with mock.patch.object(large, "controlled_streams", return_value=streams), \
                mock.patch.object(InitialState, "binomial", slow):
            result = large.run_controlled(1, 0, 0, deadline=time.monotonic() + 0.01)
        self.assertEqual(result["evaluations"], 2)
        self.assertEqual(result["observation_evaluations"], 0)
        self.assertTrue(result["archive_censored"])
        self.assertTrue(result["alignment_censored"])

    def test_earlier_archive_success_survives_late_alignment_work(self):
        original = large.controlled_offspring

        def slow(*args):
            time.sleep(0.03)
            return original(*args)

        streams = InitialState([1, 0]), UniformTape(0), UniformTape(0)
        with mock.patch.object(large, "controlled_streams", return_value=streams), \
                mock.patch.object(large, "controlled_offspring", side_effect=slow):
            result = large.run_controlled(1, 0, 0, deadline=time.monotonic() + 0.01)
        self.assertEqual(result["archive_evaluations"], 2)
        self.assertEqual(result["observation_evaluations"], 2)
        self.assertEqual(result["evaluations"], 3)
        self.assertFalse(result["archive_censored"])
        self.assertTrue(result["alignment_censored"])


if __name__ == "__main__":
    unittest.main()
