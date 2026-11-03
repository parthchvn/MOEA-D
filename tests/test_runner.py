from __future__ import annotations

import time
import json
import tempfile
import unittest
from pathlib import Path
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

    def factorial_args(self, **changes):
        values = dict(n=[4], reps=2, seed=100, max_evaluations=10_000,
                      max_trial_seconds=10)
        values.update(changes)
        return SimpleNamespace(**values)

    def test_factorial_round_robin_seed_policy_and_checkpoint(self):
        checkpoints = []
        rows, summary, exhausted = run_research.factorial_grid(
            self.factorial_args(), time.monotonic() + 30,
            lambda current, _: checkpoints.append(len(current)))
        self.assertFalse(exhausted)
        self.assertEqual(checkpoints, list(range(1, 13)))
        self.assertEqual([row["seed"] for row in rows], list(range(100, 112)))
        expected = [(r, m) for r in (0, 1, 2) for m in ("exact", "lazy")]
        for start in (0, 6):
            self.assertEqual([(row["radius"], row["mutation"]) for row in rows[start:start+6]], expected)
        self.assertTrue(all(cell["trajectories"] == 2 for cell in summary.values()))

    def test_factorial_trial_deadline_continues_total_deadline_stops(self):
        timed_out = large_result = run_research.large.run_controlled(
            4, 1, 0, deadline=time.monotonic() - 1)
        with mock.patch.object(run_research.large, "run_controlled", return_value=timed_out):
            rows, _, exhausted = run_research.factorial_grid(
                self.factorial_args(max_trial_seconds=0.001), time.monotonic() + 30,
                lambda *_: None)
            self.assertEqual(len(rows), 12)
            self.assertFalse(exhausted)
            self.assertTrue(all(row["deadline_scope"] == "trial" for row in rows))
            rows, _, exhausted = run_research.factorial_grid(
                self.factorial_args(max_trial_seconds=100), time.monotonic() + 30,
                lambda *_: None)
            self.assertEqual(len(rows), 1)
            self.assertTrue(exhausted)
            self.assertEqual(rows[0]["deadline_scope"], "total")
        self.assertEqual(large_result["evaluations"], 0)

    def test_disk_checkpoint_survives_interrupted_next_trial_and_snapshot_matches(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            source = root / "untracked_dirty_source.py"
            source.write_text("VALUE = 'exact dirty source'\n")
            completed = run_research.large.run_controlled(4, 0, 123, max_evaluations=10_000)
            argv = ["run_research.py", "factorial-grid", "--n", "4", "--reps", "2",
                    "--max-seconds", "30", "--max-trial-seconds", "10"]
            with mock.patch.object(run_research, "ROOT", root), \
                    mock.patch.object(run_research.sys, "argv", argv), \
                    mock.patch.object(run_research.large, "run_controlled",
                                      side_effect=[completed, KeyboardInterrupt()]):
                with self.assertRaises(KeyboardInterrupt):
                    run_research.main()
            destination, = (root / "research" / "runs").iterdir()
            manifest = json.loads((destination / "manifest.json").read_text())
            results = json.loads((destination / "results.json").read_text())
            self.assertEqual(len(results["trials"]), 1)
            self.assertTrue(manifest["interrupted"])
            self.assertFalse(manifest["complete"])
            self.assertIn("numpy", manifest["installed_distributions"])
            snapshot = destination / "source_snapshot" / source.name
            self.assertEqual(snapshot.read_bytes(), source.read_bytes())
            self.assertEqual(manifest["source_sha256"][source.name], run_research.sha256(snapshot))
            self.assertFalse((destination / "results.json.tmp").exists())


if __name__ == "__main__":
    unittest.main()
