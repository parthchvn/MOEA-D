import json
from pathlib import Path
import tempfile
import unittest

from scripts import analyze_neighborhood_campaign as campaign


def trial(index, T=1, n=4, stage="main"):
    return dict(id=f"{index:020x}", seed=index+1, rep=index, n=n, T=T,
                factor=1/64, max_sweeps=10, mutation="bit", noise="bit",
                reference="observed", init="uniform", cohort="primary" if stage=="main" else "smoke")


def freeze(root, plan, stage="main"):
    root.mkdir(exist_ok=True)
    (root/"rows").mkdir(exist_ok=True)
    manifest = dict(stage=stage, plan=plan, plan_sha256=campaign.digest(plan), model_sha256="a"*64)
    (root/"manifest.json").write_text(json.dumps(manifest))
    return manifest


def receipt(t, m, when):
    k=t["max_sweeps"] if when is None else when
    attempts=(t["n"]+1)*k
    row = dict(t, model_sha256=m["model_sha256"], plan_sha256=m["plan_sha256"],
               attempts=attempts, sweeps=k, init_evals=t["n"]+1, exact_sweep=when, front_sweep=0,
               archive_sweep=0, U=1, S=2, post_sweep=when, comparisons=attempts*t["T"],
               external_replacements=0, wall_seconds=.2, stop_reason="sweep_cap" if when is None else "post_exact")
    row["record_sha256"]=campaign.digest(row)
    return row


def save(root,row):
    (root/"rows"/(row["id"]+".json")).write_text(json.dumps(row))


class NeighborhoodAnalysisTest(unittest.TestCase):
    def test_restricted_bounds_and_suppressed_mean(self):
        a,b,c=trial(0),trial(1),trial(2)
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp)/"run"
            m=freeze(root,[a,b,c])
            save(root,receipt(a,m,3))
            save(root,receipt(b,m,None))
            groups,_=campaign.load_runs([root])
            key,rows=next(iter(groups.items()))
            cell, samples=campaign.event_summary(dict(zip(campaign.CONFIG,key)),rows,"exact_sweep")
            self.assertEqual((cell["observed"],cell["at_cap"],cell["missing"]),(1,1,1))
            self.assertEqual(cell["restricted_mean_lower"],(20+55+5)/3)
            self.assertEqual(cell["restricted_mean_upper"],(20+55+55)/3)
            self.assertAlmostEqual(cell["restricted_mean_comparisons_lower"], (15+50)/3)
            self.assertAlmostEqual(cell["restricted_mean_comparisons_upper"], (15+50+50)/3)
            self.assertIsNone(cell["mean_evaluations"])
            self.assertIsNone(samples)
            self.assertAlmostEqual(cell["completion_upper"],2/3)

    def test_phase_durations_are_conditional_on_their_own_endpoints(self):
        a = trial(0)
        m = dict(model_sha256="a"*64, plan_sha256="b"*64)
        complete = dict(receipt(a,m,9), U=2, S=5, max_error_at_U=0)
        pinned = dict(receipt(a,m,None), U=4, S=4, max_error_at_U=2)
        early = dict(receipt(a,m,None), U=3, S=None, max_error_at_U=1)
        before_U = dict(receipt(a,m,None), U=None, S=None, max_error_at_U=None)
        work = campaign.work_summary(a,[complete,pinned,early,before_U,None])
        self.assertEqual((work["observed_U"],work["mean_observed_U_sweeps"]), (3,3))
        self.assertEqual((work["observed_S_minus_U"],work["mean_observed_S_minus_U_sweeps"]), (2,1.5))
        self.assertEqual((work["observed_phase_II"],work["mean_observed_phase_II_sweeps"]), (1,4))
        self.assertEqual((work["observed_max_error_at_U"],work["mean_observed_max_error_at_U"]), (3,1))
        self.assertEqual((work["planned"],work["receipts"]), (5,4))
        self.assertIsNone(campaign.work_summary(a,[early,None])["mean_observed_phase_II_sweeps"])

    def test_signed_receipt_invariants_and_early_exact(self):
        a=trial(0)
        with tempfile.TemporaryDirectory() as tmp:
            m=freeze(Path(tmp),[a])
            r=receipt(a,m,3)
            r.update(exact_sweep=0)
            r["record_sha256"]=campaign.digest({k:v for k,v in r.items() if k!="record_sha256"})
            campaign.validate_receipt(r,a,m)
            r.update(archive_sweep=1)
            r["record_sha256"]=campaign.digest({k:v for k,v in r.items() if k!="record_sha256"})
            with self.assertRaisesRegex(ValueError,"order"): campaign.validate_receipt(r,a,m)
            r.update(archive_sweep=0)
            with self.assertRaisesRegex(ValueError,"Receipt hash"): campaign.validate_receipt(r,a,m)

    def test_missing_duplicate_and_mismatched_plan(self):
        a=trial(0)
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp)/"run"
            m=freeze(root,[a,dict(trial(1), seed=a["seed"])])
            with self.assertRaisesRegex(ValueError,"seed"): campaign.load_runs([root])
            m["plan"][0]["n"]=7
            (root/"manifest.json").write_text(json.dumps(m))
            with self.assertRaisesRegex(ValueError,"frozen plan"): campaign.load_runs([root])

    def test_censor_blocks_unrestricted_comparison_only(self):
        raw=[trial(0),trial(1),trial(2,T=2),trial(3,T=2)]
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp)/"run"; m=freeze(root,raw)
            for t,k in zip(raw,[4,None,3,3]): save(root,receipt(t,m,k))
            cells, ratios=campaign.analyze([root],Path(tmp)/"out",100)
            self.assertEqual(len(cells),12)
            self.assertIsNone(ratios[0]["mean_ratio"])
            self.assertAlmostEqual(ratios[0]["restricted_ratio"],(25+55)/40)
            self.assertEqual(ratios[0]["status"],"cap_censored")
            self.assertEqual(ratios[0]["role"],"exploratory")
            for name in ("report.md","runtime-main.png","completion-main.png","work.csv","provenance.json"):
                self.assertGreater((Path(tmp)/"out"/name).stat().st_size,0)

    def test_endpoint_specific_censoring_preserves_early_exact_and_reproducibility(self):
        raw=[trial(0),trial(1),trial(2,T=2),trial(3,T=2)]
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp)/"run"; m=freeze(root,raw)
            for t,k in zip(raw,[4,5,3,3]):
                row=receipt(t,m,k)
                if t==raw[0]:
                    row.update(S=None,post_sweep=None,sweeps=10,attempts=50,comparisons=50,stop_reason="sweep_cap")
                    row["record_sha256"]=campaign.digest({k:v for k,v in row.items() if k!="record_sha256"})
                save(root,row)
            groups,_=campaign.load_runs([root]); data={}
            for key,rows in groups.items():
                data[key]=campaign.event_summary(dict(zip(campaign.CONFIG,key)),rows,"exact_sweep")
            comparisons=campaign.contrasts(data,500)
            self.assertEqual(comparisons,campaign.contrasts(data,500))
            self.assertAlmostEqual(comparisons[0]["mean_ratio"],27.5/20)

    def test_two_stage_decision_requires_uncensored_support_from_both(self):
        r = {"stage":"main","role":"primary","status":"all_exact_observed","mean_ci_low":1.01}
        h = dict(r,stage="holdout")
        self.assertIn("Pending",campaign.primary_decision([r]))
        self.assertIn("Empirically supported",campaign.primary_decision([r,h]))
        self.assertIn("Inconclusive",campaign.primary_decision([r,dict(h,mean_ci_low=.95)]))
        self.assertIn("Inconclusive",campaign.primary_decision([r,dict(h,status="cap_censored")]))

    def test_geometric_corner_closed_form_and_donor_boundary(self):
        n=8
        cfg=dict(n=n,T=3,max_sweeps=100)
        mean,low,high=campaign.corner_prediction(cfg,12,1000)
        a=n**-2*(1-1/n)**(n-2); b=n**-1*(1-1/n)**(n-1); q=a+b-a*b
        self.assertAlmostEqual(mean,(n+1)*(1-(1-q)**100)/q)
        self.assertLess(low,high)
        self.assertAlmostEqual(campaign.corner_prediction(dict(cfg,T=1,max_sweeps=1),12,100)[0],n+1)


if __name__ == "__main__":
    unittest.main()
