import contextlib
import fcntl
import io
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest import mock

from scripts import neighborhood_campaign as campaign


class FrozenDesignTests(unittest.TestCase):
    def test_plan_sizes_and_independent_seeds(self):
        all_seeds = set()
        expected = {"smoke": 62, "calibrate": 102, "main": 1080, "holdout": 240}
        for stage, count in expected.items():
            plan = campaign.make_plan(stage)
            self.assertEqual(campaign.make_plan(stage), plan)
            self.assertEqual(len(plan), count)
            seeds = {row["seed"] for row in plan}
            self.assertEqual(len(seeds), count)
            self.assertFalse(all_seeds & seeds)
            all_seeds.update(seeds)
            self.assertEqual(sorted(row["rep"] for row in plan), [row["rep"] for row in plan])
        primary = campaign.make_plan("main")
        self.assertEqual({r["factor"] for r in primary}, {0, 1 / 64, 1})
        for n in (64, 128, 256):
            for factor in (0, 1 / 64, 1):
                rows = [r for r in primary if (r["n"], r["factor"]) == (n, factor)]
                self.assertEqual(len(rows), 5 * 24)
                self.assertEqual(len({r["T"] for r in rows}), 5)
        self.assertEqual({r["n"] for r in campaign.make_plan("holdout")}, {512})

    def test_concurrent_writer_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            with (base / "campaign.lock").open("a") as lock:
                fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
                r = subprocess.run(
                    [sys.executable, campaign.__file__, "--stage", "smoke", "--out", tmp,
                     "--seconds", "0.5"], capture_output=True, text=True, timeout=5)
            self.assertEqual(r.returncode, 1)
            self.assertIn("another campaign process", r.stderr)


class CheckpointTests(unittest.TestCase):
    def setUp(self):
        self.stack = contextlib.ExitStack()
        self.addCleanup(self.stack.close)
        self.temp = Path(self.stack.enter_context(tempfile.TemporaryDirectory()))
        self.base = self.temp / "runs"
        root = self.temp / "repository"
        for name in campaign.SOURCES:
            file = root / name
            file.parent.mkdir(parents=True, exist_ok=True)
            file.write_text("test fixture")
        self.root = root
        original_plan = campaign.make_plan
        self.stack.enter_context(mock.patch.object(campaign, "ROOT", root))
        self.stack.enter_context(mock.patch.object(campaign, "make_plan",
                                                  side_effect=lambda s: original_plan(s)[:3]))
        self.stack.enter_context(mock.patch.object(campaign.shutil, "which", return_value="/fake/c++"))
        self.stack.enter_context(mock.patch.object(campaign, "git_metadata",
                                                  return_value={"commit": "example", "dirty": True}))
        self.stack.enter_context(mock.patch.object(campaign, "runtime_details", return_value={}))
        self.stack.enter_context(mock.patch.object(campaign, "command", side_effect=self.command))
        self.stack.enter_context(contextlib.redirect_stdout(io.StringIO()))
        self.stack.enter_context(contextlib.redirect_stderr(io.StringIO()))
        self.trials = []
        self.interrupt_at = None
        self.cap_exact = False
        self.cap_post = False

    def command(self, argv, deadline):
        if argv[1] == "--version":
            return "test compiler\n"
        if "-dM" in argv:
            return "#define _GLIBCXX_RELEASE 14\n"
        if "-o" in argv:
            return ""
        n, size, _, seed, cap = argv[1:6]
        self.trials.append(seed)
        if len(self.trials) == self.interrupt_at:
            raise campaign.BudgetExpired
        n, size, cap = int(n), int(size), int(cap)
        censored = self.cap_post or self.cap_exact
        t = cap if censored else 1
        return json.dumps(dict(attempts=t*(n+1), init_evals=0 if argv[8]=="corner" else n+1,
                               sweeps=t, archive_sweep=1, front_sweep=1,
                               exact_sweep=None if self.cap_exact else 1, U=0, S=1,
                               post_sweep=None if censored else 1, bad_at_U=1, bad_at_S=0,
                               max_error_at_S=0, comparisons=size*t*(n+1),
                               external_replacements=0))

    def run_stage(self, stage):
        return campaign.execute(self.base, stage, seconds=60)

    def test_interrupted_seed_retried_and_completed_rows_immutable(self):
        self.interrupt_at = 2
        self.assertEqual(self.run_stage("smoke"), 2)
        directory = self.base / "smoke"
        first, = (directory / "rows").glob("*.json")
        original = first.read_bytes()
        events = [json.loads(x) for x in (directory / "events.jsonl").read_text().splitlines()]
        self.assertEqual(events[-1]["event"], "wall_budget")
        self.assertEqual(events[-1]["unconfirmed_trial"], campaign.make_plan("smoke")[1]["id"])
        self.assertGreaterEqual(events[-1]["trial_seconds"], 0)
        self.assertEqual(self.run_stage("smoke"), 0)
        self.assertEqual(self.trials[1], self.trials[2])
        self.assertEqual(self.trials.count(self.trials[0]), 1)
        self.assertEqual(first.read_bytes(), original)
        self.assertEqual(self.run_stage("smoke"), 0)
        self.assertEqual(len(self.trials), 4)

    def test_receipt_corruption_and_source_change_rejected(self):
        self.assertEqual(self.run_stage("smoke"), 0)
        row_path = next((self.base / "smoke" / "rows").glob("*.json"))
        contents = row_path.read_bytes()
        row = json.loads(contents)
        row["sweeps"] += 1
        row_path.write_text(json.dumps(row))
        with self.assertRaisesRegex(ValueError, "receipt digest"):
            self.run_stage("smoke")
        row_path.write_bytes(contents)
        (self.root / campaign.PROTOCOL).write_text("amendment")
        with self.assertRaisesRegex(ValueError, "model, compiler or protocol changed"):
            self.run_stage("smoke")

    def test_stage_gate_blocks_missing_and_censored_smoke(self):
        self.assertEqual(self.run_stage("main"), 2)
        self.assertEqual(campaign.read_json(self.base / "main" / "status.json")["state"], "gate_blocked")
        self.assertFalse(self.trials)
        self.cap_post = True
        self.assertEqual(self.run_stage("smoke"), 0)
        self.assertEqual(self.run_stage("calibrate"), 2)
        self.assertIn("smoke contains", campaign.read_json(self.base/"calibrate"/"status.json")["reason"])

    def test_holdout_gate_uses_exact_event_not_post_s(self):
        for stage in ("smoke", "calibrate"):
            self.assertEqual(self.run_stage(stage), 0)
        self.cap_post = True
        self.assertEqual(self.run_stage("main"), 0)
        self.assertEqual(self.run_stage("holdout"), 0)

    def test_missing_primary_exact_blocks_holdout(self):
        for stage in ("smoke", "calibrate"):
            self.assertEqual(self.run_stage(stage), 0)
        self.cap_exact = True
        self.assertEqual(self.run_stage("main"), 0)
        self.assertEqual(self.run_stage("holdout"), 2)
        self.assertIn("primary exact", campaign.read_json(self.base/"holdout"/"status.json")["reason"])
