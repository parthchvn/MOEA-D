from __future__ import annotations

import json
import tempfile
import time
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest import mock

import numpy as np

import large
from scripts import run_research, analyze_broadcast


class ConstantTape:
    def __init__(self, value):
        self.value = value

    def random(self, size):
        return np.full(size, self.value)


def streams(initial, gate=0.0, direction=0.0):
    initial_rng = mock.Mock()
    initial_rng.binomial.return_value = np.asarray(initial)
    return initial_rng, ConstantTape(gate), ConstantTape(direction)


class BroadcastModelTests(unittest.TestCase):
    def test_on_broadcast_solves_neighbor_off_suppresses_only_copy(self):
        results = []
        for enabled in (True, False):
            with mock.patch.object(large, "controlled_streams", return_value=streams([1, 0, 2])):
                results.append(large.run_controlled(2, 1, 0, "lazy", max_evaluations=4,
                                                    self_loop_broadcast=enabled, track_phases=True))
        on, off = results
        self.assertEqual(on["self_loop_recipient_changes"], 1)
        self.assertEqual(on["target_first_hit_evaluations"], [None, 4, 3])
        self.assertEqual(off["self_loop_recipient_changes"], 0)
        self.assertEqual(off["self_loop_target_acquisitions"], 0)
        self.assertEqual(off["target_first_hit_evaluations"], [None, None, 3])
        self.assertEqual(off["rejected_offspring"], 0)  # self comparison retained
        for result in results:
            self.assertEqual(result["evaluations"], 4)
            self.assertEqual(result["archive_evaluations"], 3)

    def test_radius_zero_is_pathwise_identity(self):
        for seed in (0, 123, 987):
            on = large.run_controlled(8, 0, seed, "lazy", max_evaluations=100_000,
                                      self_loop_broadcast=True, track_phases=True)
            off = large.run_controlled(8, 0, seed, "lazy", max_evaluations=100_000,
                                       self_loop_broadcast=False, track_phases=True)
            self.assertEqual(on, off)

    def test_no_self_loop_tape_preserves_moving_communication_and_phases(self):
        results = []
        for enabled in (True, False):
            initial, gates, _ = streams([1, 1, 1, 2], gate=.9)
            directions = mock.Mock()
            directions.random.side_effect = [np.array([.99, .99, .99, 0]), np.zeros(4)]
            with mock.patch.object(large, "controlled_streams", return_value=(initial, gates, directions)):
                results.append(large.run_controlled(3, 1, 0, "lazy", max_evaluations=10,
                                                    self_loop_broadcast=enabled, track_phases=True))
        self.assertEqual(*results)
        self.assertEqual(results[0]["target_first_hit_evaluations"], [5, 4, 10, 8])
        self.assertEqual(results[0]["last_endpoint_evaluations"], 8)
        self.assertEqual(results[0]["alignment_after_endpoints_evaluations"], 2)

    def test_exact_mutation_broadcast_flag_has_no_effect(self):
        self.assertEqual(large.run_controlled(8, 1, 123, "exact"),
                         large.run_controlled(8, 1, 123, "exact", self_loop_broadcast=False))

    def test_phase_observers_leave_all_legacy_fields_identical(self):
        for enabled in (True, False):
            plain = large.run_controlled(8, 1, 123, "lazy", self_loop_broadcast=enabled)
            observed = large.run_controlled(8, 1, 123, "lazy", self_loop_broadcast=enabled, track_phases=True)
            self.assertEqual(plain, {key: observed[key] for key in plain})
            self.assertEqual(max(observed["target_first_hit_evaluations"]), observed["alignment_evaluations"])

    def test_legacy_default_golden_record_from_prechange_source(self):
        # Captured mechanically from the pre-edit source snapshot; no dependency
        # on ignored run files is needed to execute this regression.
        expected = dict(aligned_count=9, alignment_censored=False, alignment_evaluations=127,
                        archive_censored=False, archive_count=9, archive_evaluations=127,
                        censor_reason=None, evaluations=127, initialization_evaluations=9,
                        observation_evaluations=127, offspring_evaluations=118,
                        rejected_new_archive_weights=1, rejected_offspring=11,
                        self_loop_offspring=59, self_loop_recipient_changes=6,
                        self_loop_target_acquisitions=2)
        self.assertEqual(large.run_controlled(8, 1, 123, "lazy", max_evaluations=100_000), expected)

    def test_late_initialization_does_not_confirm_phase_hits(self):
        initial, gate, direction = streams([0, 1, 2])
        def delayed(*args, **kwargs):
            time.sleep(.03)
            return np.array([0, 1, 2])
        initial.binomial.side_effect = delayed
        with mock.patch.object(large, "controlled_streams", return_value=(initial, gate, direction)):
            result = large.run_controlled(2, 1, 0, "lazy", track_phases=True,
                                          deadline=time.monotonic() + .01)
        self.assertEqual(result["observation_evaluations"], 0)
        self.assertEqual(result["target_first_hit_evaluations"], [None] * 3)
        self.assertIsNone(result["last_endpoint_evaluations"])

    def test_late_new_target_preserves_earlier_endpoint_hits(self):
        original = large.controlled_offspring
        def delayed(*args):
            time.sleep(.03)
            return original(*args)
        with mock.patch.object(large, "controlled_streams", return_value=streams([0, 0, 2], gate=.9)), \
                mock.patch.object(large, "controlled_offspring", side_effect=delayed):
            result = large.run_controlled(2, 1, 0, "lazy", track_phases=True,
                                          deadline=time.monotonic() + .01)
        self.assertEqual(result["observation_evaluations"], 3)
        self.assertEqual(result["target_first_hit_evaluations"], [3, None, 3])
        self.assertEqual(result["last_endpoint_evaluations"], 3)
        self.assertIsNone(result["alignment_after_endpoints_evaluations"])


class BroadcastRunnerTests(unittest.TestCase):
    def args(self, **changes):
        values = dict(n=[8], include_zero=False, blocks=2, seed=900,
                      max_trial_seconds=10, max_evaluations=100_000, run_id="unit-run")
        values.update(changes)
        return SimpleNamespace(**values)

    def test_counterbalance_within_each_radius_and_checkpoint_every_arm(self):
        args = self.args()
        checkpoints = []
        rows, summary, exhausted = run_research.broadcast_grid(
            args, time.monotonic() + 30, lambda rows, _: checkpoints.append(len(rows)))
        self.assertFalse(exhausted)
        self.assertEqual(checkpoints, list(range(1, 9)))
        self.assertEqual([r["arm"] for r in rows], ["on", "off", "on", "off", "off", "on", "off", "on"])
        self.assertEqual([r["seed"] for r in rows], [900, 900, 901, 901, 902, 902, 903, 903])
        self.assertEqual(summary["complete_blocks"], 4)
        self.assertEqual(summary["unstarted_blocks"], [])

    def test_total_cutoff_retains_partial_and_unstarted_blocks(self):
        result = large.run_controlled(8, 1, 900, "lazy", track_phases=True)
        stopped = False
        def clock():
            return 20 if stopped else 0
        def checkpoint(*_):
            nonlocal stopped
            stopped = True
        with mock.patch.object(run_research.time, "monotonic", side_effect=clock), \
                mock.patch.object(run_research.large, "run_controlled", return_value=result):
            rows, summary, exhausted = run_research.broadcast_grid(self.args(), 10, checkpoint)
        self.assertTrue(exhausted)
        self.assertEqual(len(rows), 1)
        self.assertEqual(len(summary["incomplete_started_blocks"]), 1)
        self.assertEqual(len(summary["unstarted_blocks"]), 3)

    def test_per_trial_cutoffs_do_not_omit_partner_or_later_blocks(self):
        result = large.run_controlled(8, 1, 0, "lazy", track_phases=True,
                                      deadline=time.monotonic() - 1)
        with mock.patch.object(run_research.large, "run_controlled", return_value=result):
            rows, summary, exhausted = run_research.broadcast_grid(
                self.args(max_trial_seconds=.001), time.monotonic() + 30, lambda *_: None)
        self.assertFalse(exhausted)
        self.assertEqual(summary["complete_blocks"], 4)
        self.assertTrue(all(row["deadline_scope"] == "trial" for row in rows))
        self.assertTrue(all(row["alignment_censored"] for row in rows))

    def test_persisted_interruption_preserves_full_plan_and_first_arm(self):
        result = large.run_controlled(8, 1, 900, "lazy", track_phases=True)
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            (root / "dirty.py").write_text("value=42\n")
            argv = ["run_research.py", "broadcast-grid", "--n", "8", "--blocks", "2",
                    "--seed", "900", "--max-seconds", "30"]
            with mock.patch.object(run_research, "ROOT", root), \
                    mock.patch.object(run_research.sys, "argv", argv), \
                    mock.patch.object(run_research.large, "run_controlled", side_effect=[result, KeyboardInterrupt()]):
                with self.assertRaises(KeyboardInterrupt):
                    run_research.main()
            destination, = (root / "research" / "runs").iterdir()
            manifest = json.loads((destination / "manifest.json").read_text())
            output = json.loads((destination / "results.json").read_text())
            self.assertEqual(manifest["requested_blocks"], 4)
            self.assertEqual(manifest["requested_trials"], 8)
            self.assertEqual(len(manifest["planned_blocks"]), 4)
            self.assertTrue(manifest["interrupted"])
            self.assertEqual(len(output["trials"]), 1)
            self.assertEqual(len(output["summary"]["unstarted_blocks"]), 3)
            snapshot = destination / "source_snapshot" / "dirty.py"
            self.assertEqual(manifest["source_sha256"]["dirty.py"], run_research.sha256(snapshot))


class BroadcastAnalysisTests(unittest.TestCase):
    def dataset(self):
        args = SimpleNamespace(n=[8], include_zero=False, blocks=3, seed=900)
        plan = run_research.broadcast_plan(args)
        rows = []
        for block in plan:
            for position, arm in enumerate(block["arm_order"]):
                alignment = 100 * (block["repetition"] + 1)
                if arm == "off" and block["radius"] == 1:
                    alignment *= 2
                h = alignment // 2
                hits = [h] * 9
                hits[1] = alignment
                rows.append(dict(**block, run_id="synthetic", arm=arm, execution_position=position,
                                 mutation="lazy", weight_self_loop_probability=.5,
                                 self_loop_neighbor_broadcast=arm == "on", evaluations=alignment,
                                 observation_evaluations=alignment, archive_evaluations=alignment-10,
                                 alignment_evaluations=alignment, archive_censored=False, alignment_censored=False,
                                 target_first_hit_evaluations=hits, last_endpoint_evaluations=h,
                                 interior_completion_evaluations=alignment,
                                 alignment_after_endpoints_evaluations=alignment-h,
                                 self_loop_offspring=0, self_loop_recipient_changes=0,
                                 self_loop_target_acquisitions=0))
        return dict(manifest=dict(mode="broadcast-grid", parameters=dict(run_id="synthetic"),
                                 complete=True, planned_blocks=plan), trials=rows)

    def test_whole_block_bootstrap_preserves_proportional_arm_coupling(self):
        result = analyze_broadcast.analyze([self.dataset()], bootstrap=1000)
        primary = result["contrasts"]["8"]["primary"]
        for name in ("A1", "Delta"):
            self.assertAlmostEqual(primary[name]["estimate"], np.log(2))
            np.testing.assert_allclose(primary[name]["interval"], [np.log(2)] * 2)
            self.assertEqual(primary[name]["coverage"], .975)

    def test_planned_but_unstarted_block_makes_primary_inconclusive(self):
        data = self.dataset()
        data["trials"] = data["trials"][:-2]
        data["manifest"]["complete"] = False
        result = analyze_broadcast.analyze([data], bootstrap=100)
        self.assertEqual(result["planned_blocks"], 6)
        self.assertEqual(result["recorded_trajectories"], 10)
        self.assertEqual(result["contrasts"]["8"]["primary_decision"], "inconclusive")

    def test_censoring_not_removed_as_complete_case(self):
        data = self.dataset()
        row = data["trials"][0]
        row.update(alignment_evaluations=None, alignment_censored=True,
                   interior_completion_evaluations=None, alignment_after_endpoints_evaluations=None)
        row["target_first_hit_evaluations"][1] = None
        result = analyze_broadcast.analyze([data], bootstrap=100)
        self.assertEqual(result["recorded_trajectories"], 12)
        self.assertEqual(result["contrasts"]["8"]["primary_decision"], "inconclusive")

    def test_duplicate_arm_rejected(self):
        data = self.dataset()
        data["trials"].append(dict(data["trials"][0]))
        with self.assertRaises(ValueError):
            analyze_broadcast.analyze([data], bootstrap=100)

    def test_late_phase_hit_beyond_observation_is_rejected(self):
        data = self.dataset()
        data["trials"][0]["target_first_hit_evaluations"][0] = 101
        with self.assertRaises(ValueError):
            analyze_broadcast.analyze([data], bootstrap=100)


if __name__ == "__main__":
    unittest.main()
