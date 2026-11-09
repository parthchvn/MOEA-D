"""Deterministic/synthetic checks only; prospective seeds never reach an engine."""
import json
import math
import tempfile
import unittest
from pathlib import Path

import numpy as np
import analysis
from plan import ENGINE, ENGINE_SHA256, STUDY, build_plan, digest, seed_csv, repo_root


def fixture(item, exact=3, U=1, S=2, post=3):
    row = dict(item)
    t = item["max_sweeps"] if post is None else post
    row.update(sweeps=t, init_evals=item["n"]+1, attempts=t*(item["n"]+1),
               comparisons=t*(item["n"]+1)*item["T"],
               exact_sweep=exact, front_sweep=exact, archive_sweep=exact,
               U=U, S=S, post_sweep=post, bad_at_U=None if U is None else 0,
               max_error_at_U=None if U is None else 0, bad_at_S=None if S is None else 0,
               max_error_at_S=None if S is None else 0, external_replacements=0, external_changes=0,
               endpoint_repairs_own=0, endpoint_repairs_external=0, wall_seconds=0.,
               stop_reason="post_exact" if post is not None else "sweep_cap",
               model_sha256="a"*64, plan_sha256=build_plan()["plan_sha256"])
    row["record_sha256"] = digest(row)
    return row


class DesignTests(unittest.TestCase):
    def test_frozen_arm_size_horizon_and_order(self):
        d = build_plan()
        self.assertEqual(d, build_plan())
        self.assertEqual(len(d["plan"]), 68)
        for stage, n, reps, H in (("smoke",32,2,10742),("main",512,32,38341)):
            rows = [r for r in d["plan"] if r["stage"] == stage]
            self.assertEqual(len(rows), 2*reps)
            self.assertEqual({r["n"] for r in rows}, {n})
            self.assertEqual({r["max_sweeps"] for r in rows}, {H})
            for rep in range(reps):
                self.assertEqual([r["T"] for r in rows if r["rep"] == rep],
                                 [1,23] if rep%2 == 0 else [23,1])
        self.assertEqual(d["primary"]["cap_evaluations"], 513*(1+38341))
        self.assertEqual(38341, math.ceil(12*512*math.log(513)))
        self.assertEqual(10742, math.ceil(96*32*math.log(33)))
        self.assertEqual(len({r["seed"] for r in d["plan"]}),68)
        self.assertEqual(len(seed_csv(d).splitlines()),69)

    def test_bundle_matches_generator(self):
        folder = Path(__file__).resolve().parent
        self.assertEqual(json.loads((folder/"plan.json").read_text()), build_plan())
        self.assertEqual((folder/"seeds.csv").read_text(), seed_csv(build_plan()))
        self.assertEqual(len(ENGINE_SHA256),64)


class AnalysisTests(unittest.TestCase):
    def setUp(self):
        self.design = build_plan()
        self.item = next(r for r in self.design["plan"] if r["stage"] == "main")
        self.manifest = dict(model_sha256="a"*64, plan_sha256=self.design["plan_sha256"])

    def check(self, row):
        analysis.validate(row, self.item, self.manifest)
        return analysis.vector(row)

    def test_complete_decomposition(self):
        v = self.check(fixture(self.item, exact=7, U=2, S=4, post=7))
        np.testing.assert_array_equal(v, [4104,4104,2,4,2,2,3,0])
        self.assertEqual(sum(v[4:7]),7)

    def test_censor_before_U(self):
        v = self.check(fixture(self.item, exact=None, U=None, S=None, post=None))
        np.testing.assert_array_equal(v, [19669446,19669446,38341,38341,38341,0,0,0])

    def test_censor_between_U_S(self):
        row = fixture(self.item, exact=None, U=100, S=None, post=None)
        v = self.check(row)
        self.assertEqual(list(v[4:7]),[100,38241,0])
        d = analysis.phase_diagnostics([row])
        self.assertEqual(d["S_minus_U"]["right_censored_after_entry"],1)
        self.assertEqual(d["post_minus_S"]["not_entered"],1)

    def test_censor_after_S_preserves_early_exact(self):
        v = self.check(fixture(self.item, exact=3, U=1, S=5, post=None))
        self.assertEqual(v[0],2052)
        self.assertEqual(v[1],19669446)
        self.assertEqual(list(v[4:]),[1,4,38336,38338])
        self.assertEqual(513*(1+sum(v[4:7])-v[7]),v[0])

    def test_early_exact_is_not_post(self):
        v = self.check(fixture(self.item, exact=1, U=2, S=5, post=9))
        self.assertEqual(v[0],1026)
        self.assertEqual(v[1],5130)
        self.assertEqual(sum(v[4:7]),9)
        self.assertEqual(v[7],8)

    def test_hit_at_cap_and_boundary_zero(self):
        for t in (0,38341):
            row = fixture(self.item, exact=t,U=t,S=t,post=t)
            self.check(row)
            self.assertEqual(analysis.phase_diagnostics([row])["post_minus_S"]["completed"],1)

    def test_reject_broken_event_and_receipt(self):
        row = fixture(self.item)
        row["U"] = 4
        with self.assertRaises(ValueError):
            self.check(row)
        row["record_sha256"] = digest({k:v for k,v in row.items() if k != "record_sha256"})
        with self.assertRaises(ValueError):
            self.check(row)
        row = fixture(self.item,exact=4,U=1,S=2,post=5)
        with self.assertRaises(ValueError):
            self.check(row)

    def test_primary_keeps_caps_in_denominator(self):
        rows = {}
        for item in self.design["plan"]:
            if item["stage"] != "main":
                continue
            row = fixture(item,exact=None,U=1,S=2,post=None) if item["T"] == 1 else fixture(item)
            analysis.validate(row,item,self.manifest)
            rows[item["id"]] = row
        result = analysis.analyze(rows)
        self.assertEqual(result["primary"]["ratio"],19669446/2052)
        self.assertEqual(result["arms"]["1"]["events"]["exact_sweep"]["capped"],32)
        self.assertEqual(result["arms"]["1"]["restricted_means"]["post_S_sweeps"],38339)
        self.assertEqual(result,analysis.analyze(rows))

    def test_missing_is_not_administrative_censoring(self):
        result = analysis.analyze({})
        self.assertIsNone(result["primary"]["nominal_95_ci"])
        self.assertEqual(result["primary"]["identification_bounds"],[1/38342,38342])
        self.assertEqual(result["arms"]["1"]["events"]["exact_sweep"]["capped"],0)
        rows = {r["id"]:fixture(r) for r in self.design["plan"] if r["stage"] == "main"}
        del rows[self.item["id"]]
        result = analysis.analyze(rows)
        bounds = result["arms"]["1"]["exact_restricted_mean_identification_bounds"]
        self.assertEqual(bounds,[(31*2052+513)/32,(31*2052+19669446)/32])
        self.assertEqual(result["primary"]["decision"],"incomplete_no_directional_decision")

    def test_zero_success_interval_has_nonzero_width(self):
        lo, hi = analysis.wilson(0,32)
        self.assertAlmostEqual(lo,0)
        self.assertGreater(hi,0.1)
        self.assertAlmostEqual(analysis.wilson(32,32)[0],1-hi)

    def test_phase_difference_identity_for_bootstraps(self):
        rows = {}
        for item in self.design["plan"]:
            if item["stage"] == "main":
                x = 1+item["rep"]%3
                rows[item["id"]] = fixture(item,exact=x,U=1,S=5,post=8+item["rep"]%4)
        result = analysis.analyze(rows)
        for arm in result["arms"].values():
            m = arm["restricted_means"]
            self.assertAlmostEqual(m["exact_evaluations"],
                513*(1+m["pre_U_sweeps"]+m["U_to_S_sweeps"]+m["post_S_sweeps"]-m["post_exact_gap_sweeps"]))

    def test_receipt_loader_and_smoke_gate(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source = root/"source"/ENGINE
            source.parent.mkdir(parents=True)
            source.write_bytes((repo_root()/ENGINE).read_bytes())
            manifest = dict(study=STUDY, plan=self.design["plan"],
                            plan_sha256=self.design["plan_sha256"],
                            sources={ENGINE:ENGINE_SHA256}, toolchain={"test_fixture":True})
            manifest["model_sha256"] = digest([STUDY,manifest["sources"],manifest["toolchain"]])
            (root/"manifest.json").write_text(json.dumps(manifest))
            (root/"rows").mkdir()
            def save(item):
                row = fixture(item)
                row["model_sha256"] = manifest["model_sha256"]
                row["record_sha256"] = digest({k:v for k,v in row.items() if k != "record_sha256"})
                (root/"rows"/(item["id"]+".json")).write_text(json.dumps(row))
            save(self.item)
            with self.assertRaisesRegex(ValueError,"passing smoke"):
                analysis.load_run(root)
            for item in self.design["plan"]:
                if item["stage"] == "smoke":
                    save(item)
            self.assertEqual(len(analysis.load_run(root)),5)
            source.write_text("tampered source")
            with self.assertRaisesRegex(ValueError,"source mismatch"):
                analysis.load_run(root)


if __name__ == "__main__":
    unittest.main(verbosity=2)
