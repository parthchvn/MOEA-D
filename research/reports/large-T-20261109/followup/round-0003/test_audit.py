#!/usr/bin/env python3
"""Synthetic failure/edge tests; no simulation or scientific seed is used."""
import unittest

import audit as a


def fixture(**updates):
    plan = dict(id="synthetic",seed=42,n=4,T=1,factor=.015625,max_sweeps=10,init="uniform")
    manifest = dict(plan_sha256="plan",model_sha256="model")
    row = dict(plan,**manifest,sweeps=10,attempts=50,comparisons=50,init_evals=5,
               exact_sweep=None,front_sweep=None,archive_sweep=None,U=None,S=None,post_sweep=None,
               bad_at_U=None,max_error_at_U=None,bad_at_S=None,max_error_at_S=None,
               external_changes=0,external_replacements=0,endpoint_repairs_own=0,endpoint_repairs_external=0,
               wall_seconds=0.,stop_reason="sweep_cap")
    row.update(updates)
    row["record_sha256"] = a.digest(row)
    return row,plan,manifest


def resign(row):
    row["record_sha256"] = a.digest({k:v for k,v in row.items() if k != "record_sha256"})


class AuditTests(unittest.TestCase):
    def test_cap_before_U_is_not_missing(self):
        r,p,m = fixture()
        a.validate(r,p,m)
        v = a.restricted(r)
        self.assertEqual([v[k] for k in ("pre_U_sweeps","U_to_S_sweeps","post_S_sweeps")],[10,0,0])
        s = a.cell_summary([p],{p["id"]:r},"synthetic","main")
        self.assertEqual((s["capped"],s["missing"],s["restricted_mean"]),(1,0,55))

    def test_cap_between_U_and_S(self):
        r,p,m = fixture(U=3,bad_at_U=0,max_error_at_U=0)
        a.validate(r,p,m)
        v = a.restricted(r)
        self.assertEqual((v["pre_U_sweeps"],v["U_to_S_sweeps"],v["post_S_sweeps"]),(3,7,0))

    def test_cap_after_S(self):
        r,p,m = fixture(U=2,S=4,bad_at_U=0,max_error_at_U=0,bad_at_S=1,max_error_at_S=1)
        a.validate(r,p,m)
        self.assertEqual(a.restricted(r)["post_S_sweeps"],6)
        stats = a.phase_summary([r],"S","post_sweep")
        self.assertEqual((stats["entered"],stats["completed"],stats["right_censored_after_entry"]),(1,0,1))

    def test_early_exact_survives_post_cap(self):
        r,p,m = fixture(archive_sweep=2,front_sweep=3,exact_sweep=3,U=5,S=6,
                        bad_at_U=0,max_error_at_U=0,bad_at_S=1,max_error_at_S=1)
        a.validate(r,p,m)
        v = a.restricted(r)
        self.assertEqual((v["exact_evaluations"],v["post_evaluations"],v["post_exact_gap_sweeps"]),(20,55,7))
        s = a.cell_summary([p],{p["id"]:r},"synthetic","main")
        self.assertEqual((s["observed"],s["capped"]),(1,0))

    def test_early_exact_phase_identity(self):
        r,p,m = fixture(sweeps=8,attempts=40,comparisons=40,archive_sweep=2,front_sweep=3,
                       exact_sweep=3,U=4,S=6,post_sweep=8,bad_at_U=0,max_error_at_U=0,
                       bad_at_S=1,max_error_at_S=1,stop_reason="post_exact")
        a.validate(r,p,m)
        v = a.restricted(r)
        self.assertEqual(v["post_exact_gap_sweeps"],5)
        self.assertEqual(v["exact_evaluations"],20)

    def test_hit_at_horizon_is_observed(self):
        r,p,m = fixture(archive_sweep=2,front_sweep=10,exact_sweep=10,U=2,S=9,post_sweep=10,
                       bad_at_U=0,max_error_at_U=0,bad_at_S=1,max_error_at_S=1,stop_reason="post_exact")
        a.validate(r,p,m)
        s = a.cell_summary([p],{p["id"]:r},"synthetic","main")
        self.assertEqual((s["observed"],s["capped"],s["restricted_mean"]),(1,0,55))

    def test_zero_boundary_is_not_absent(self):
        r,p,m = fixture(sweeps=0,attempts=0,comparisons=0,archive_sweep=0,front_sweep=0,exact_sweep=0,
                       U=0,S=0,post_sweep=0,bad_at_U=0,max_error_at_U=0,bad_at_S=0,max_error_at_S=0,
                       stop_reason="post_exact")
        a.validate(r,p,m)
        self.assertEqual(a.restricted(r)["exact_evaluations"],5)

    def test_missing_is_not_cap(self):
        _,p,_ = fixture()
        s = a.cell_summary([p],{},"synthetic","main")
        self.assertEqual((s["observed"],s["capped"],s["missing"]),(0,0,1))
        self.assertIsNone(s["restricted_mean"])
        self.assertEqual((s["sample_mean_bound_low"],s["sample_mean_bound_high"]),(5,55))

    def test_conditional_phase_denominators(self):
        r1,_,_ = fixture(U=2,bad_at_U=0,max_error_at_U=0)
        r2,_,_ = fixture()
        stats = a.phase_summary([r1,r2],"U","S")
        self.assertEqual((stats["entered"],stats["completed"],stats["not_entered"]),(1,0,1))
        self.assertIsNone(stats["completed_only_mean"])

    def test_hash_tampering_rejected(self):
        r,p,m = fixture()
        r["wall_seconds"] = 1
        with self.assertRaisesRegex(ValueError,"digest"):
            a.validate(r,p,m)

    def test_resigned_wrong_seed_rejected(self):
        r,p,m = fixture()
        r["seed"] += 1
        resign(r)
        with self.assertRaisesRegex(ValueError,"plan"):
            a.validate(r,p,m)

    def test_resigned_incorrect_work_rejected(self):
        r,p,m = fixture(attempts=49)
        with self.assertRaisesRegex(ValueError,"Accounting"):
            a.validate(r,p,m)

    def test_resigned_inverted_event_order_rejected(self):
        r,p,m = fixture(U=5,S=3,bad_at_U=0,max_error_at_U=0,bad_at_S=0,max_error_at_S=0)
        with self.assertRaisesRegex(ValueError,"ordering"):
            a.validate(r,p,m)

    def test_resigned_missed_post_hit_rejected(self):
        r,p,m = fixture(U=2,S=3,archive_sweep=2,front_sweep=5,exact_sweep=5,
                       bad_at_U=0,max_error_at_U=0,bad_at_S=1,max_error_at_S=1)
        with self.assertRaisesRegex(ValueError,"Post-S"):
            a.validate(r,p,m)

    def test_linear_quantiles(self):
        self.assertEqual(a.percentile([1,2,4,8],.5),3)
        self.assertEqual(a.percentile([1,2,4,8],.25),1.75)
        self.assertIsNone(a.percentile([],.5))

    def test_whole_row_bootstrap_keeps_phase_identity(self):
        r1,_,_ = fixture()
        r2,_,_ = fixture(archive_sweep=2,front_sweep=3,exact_sweep=3,U=5,S=6)
        b = a.bootstrap([r1,r2],123)
        for i in range(10000):
            self.assertEqual(b["exact_evaluations"][i],5+5*(b["pre_U_sweeps"][i]+b["U_to_S_sweeps"][i]
                              +b["post_S_sweeps"][i]-b["post_exact_gap_sweeps"][i]))


if __name__ == "__main__":
    unittest.main(verbosity=2)
