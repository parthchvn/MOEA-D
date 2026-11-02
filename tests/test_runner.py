from __future__ import annotations

import time
import unittest
from types import SimpleNamespace
from unittest import mock

from scripts import run_research


class ResearchRunnerTests(unittest.TestCase):
    def test_describe_includes_quartiles(self) -> None:
        summary = run_research.describe([1.0, 2.0, 3.0, 4.0])
        self.assertEqual(summary["count"], 4)
        self.assertEqual(summary["median"], 2.5)
        self.assertEqual(summary["q25"], 1.75)
        self.assertEqual(summary["q75"], 3.25)

    def test_large_grid_is_round_robin_and_checkpoints_every_trial(self) -> None:
        args = SimpleNamespace(
            n=[2],
            r=[0, 1],
            reps=2,
            seed=100,
            track=False,
            max_sweeps=100,
            max_trial_seconds=10,
        )
        checkpoint_sizes: list[int] = []

        rows, summary, budget_exhausted = run_research.large_grid(
            args,
            deadline=time.monotonic() + 10,
            checkpoint=lambda current, _summary: checkpoint_sizes.append(len(current)),
        )

        self.assertFalse(budget_exhausted)
        self.assertEqual(checkpoint_sizes, [1, 2, 3, 4])
        self.assertEqual(
            [(row["repetition"], row["radius"]) for row in rows],
            [(0, 0), (0, 1), (1, 0), (1, 1)],
        )
        self.assertEqual(summary["n=2,r=0"]["trials_started"], 2)
        self.assertEqual(summary["n=2,r=1"]["trials_started"], 2)

    def test_per_trial_deadline_does_not_abort_balanced_grid(self) -> None:
        args = SimpleNamespace(
            n=[2],
            r=[0, 1],
            reps=2,
            seed=100,
            track=False,
            max_sweeps=100,
            max_trial_seconds=0.001,
        )
        timed_out = {
            "sweeps": -1,
            "censored": True,
            "censor_reason": "wall_time",
            "J_checks": 0,
            "J_viol": 0,
        }

        with mock.patch.object(run_research.large, "run", return_value=timed_out):
            rows, _summary, budget_exhausted = run_research.large_grid(
                args,
                deadline=time.monotonic() + 10,
                checkpoint=lambda _current, _summary: None,
            )

        self.assertFalse(budget_exhausted)
        self.assertEqual(len(rows), 4)
        self.assertTrue(all(row["deadline_scope"] == "trial" for row in rows))


if __name__ == "__main__":
    unittest.main()
