"""Pre-draw wrapper tests. Synthetic outputs/mocked commands; no prospective RNG."""
import copy
import json
import os
from pathlib import Path
import sys
import tempfile
import time
import unittest
from unittest.mock import patch

import run

ROOT = next(p for p in Path(__file__).resolve().parents if (p / "AGENTS.md").is_file())
plan, analysis = run.load_registered(ROOT)


def outcome(item, capped=False, early=False):
    n, T = item["n"], item["T"]
    t = item["max_sweeps"] if capped else 4
    return dict(sweeps=t, attempts=t*(n+1), init_evals=n+1, comparisons=t*(n+1)*T,
                external_replacements=0, external_changes=0,
                exact_sweep=None if capped else 1 if early else 4,
                front_sweep=None if capped else 1 if early else 4,
                archive_sweep=None if capped else 1 if early else 4,
                U=1, S=2, post_sweep=None if capped else 4,
                bad_at_U=0, bad_at_S=0, max_error_at_U=0, max_error_at_S=0,
                first_corner_donor=None, endpoint_repairs_own=0, endpoint_repairs_external=0)


class WrapperTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.out = Path(self.tmp.name) / "run"
        self.private = Path(self.tmp.name) / "private"
        self.private.mkdir()
        self.design = plan.build_plan()
        self.manifest = dict(plan=self.design["plan"], plan_sha256=self.design["plan_sha256"],
                             model_sha256="a"*64)

    def perform(self, **kwargs):
        return run.measure(plan, analysis, self.manifest, self.out, self.private,
                           Path("mock-engine"), time.monotonic()+30, ROOT, **kwargs)

    def test_full_order_exact_seed_strings_and_receipts(self):
        calls = []
        def execute(argv, deadline, root):
            item = self.design["plan"][len(calls)]
            self.assertEqual(argv[1:], [str(item[k]) for k in
                             ("n", "T", "factor", "seed", "max_sweeps", "mutation", "noise", "init", "reference")])
            calls.append(item["id"])
            return json.dumps(outcome(item))
        status = self.perform(execute=execute)
        self.assertEqual(status["state"], "complete")
        self.assertEqual(calls, [p["id"] for p in self.design["plan"]])
        self.assertEqual(status["recorded"], 68)
        for item in self.design["plan"]:
            row = json.loads((self.out / "rows" / (item["id"]+".json")).read_text())
            analysis.validate(row, item, self.manifest)

    def test_capped_smoke_preserved_and_blocks_main(self):
        calls = []
        def execute(*args):
            item = self.design["plan"][len(calls)]
            calls.append(item)
            return json.dumps(outcome(item, capped=True))
        status = self.perform(execute=execute)
        self.assertEqual((status["state"], status["recorded"], len(calls)), ("smoke_blocked",1,1))
        self.assertEqual(len(status["missing_ids"]),67)

    def test_capped_main_does_not_stop_and_early_exact_preserved(self):
        calls = []
        def execute(*args):
            item = self.design["plan"][len(calls)]
            calls.append(item)
            return json.dumps(outcome(item, capped=len(calls)==5, early=len(calls)==6))
        status = self.perform(execute=execute)
        self.assertEqual(status["state"], "complete")
        rows = [json.loads((self.out / "rows" / (i["id"]+".json")).read_text()) for i in calls]
        self.assertEqual(rows[4]["stop_reason"],"sweep_cap")
        self.assertEqual((rows[5]["exact_sweep"],rows[5]["S"],rows[5]["post_sweep"]),(1,2,4))
        self.assertEqual(analysis.analyze({r["id"]:r for r in rows})["arms"]["1"]["events"]["exact_sweep"]["capped"],1)

    def test_cutoff_keeps_rows_without_censoring_killed_trial(self):
        calls = []
        def execute(*args):
            item = self.design["plan"][len(calls)]
            calls.append(item)
            if len(calls)==6:
                raise run.Cutoff("synthetic cutoff")
            return json.dumps(outcome(item))
        status = self.perform(execute=execute)
        self.assertEqual((status["state"],status["recorded"]),("wall_cutoff",5))
        self.assertEqual(len(calls),6)  # No retry or replacement seed.
        rows = {p.stem:json.loads(p.read_text()) for p in (self.out/"rows").glob("*.json")}
        self.assertNotIn(calls[-1]["id"],rows)
        report=analysis.analyze(rows)
        self.assertIsNone(report["primary"]["nominal_95_ci"])
        self.assertIsNone(report["primary"]["ratio"])
        self.assertEqual(report["arms"]["1"]["missing"],31)

    def test_unknown_fields_or_invalid_accounting_stop_no_retry(self):
        for mode in ("extra", "accounting", "corner"):
            with self.subTest(mode=mode):
                result = outcome(self.design["plan"][0])
                if mode=="extra": result["unregistered"]=1
                if mode=="accounting": result["attempts"]+=1
                if mode=="corner": result["first_corner_donor"]=0
                calls=[]
                def execute(*args):
                    calls.append(args)
                    return json.dumps(result)
                status=self.perform(execute=execute)
                self.assertEqual(status["state"],"integrity_or_technical_failure")
                self.assertEqual((status["recorded"],len(calls)),(0,1))

    def test_source_change_after_child_quarantines_output(self):
        count=0
        def check():
            nonlocal count
            count+=1
            if count==2: raise ValueError("source changed")
        status=self.perform(execute=lambda *args:json.dumps(outcome(self.design["plan"][0])),check=check)
        self.assertEqual(status["recorded"],0)
        self.assertEqual(status["state"],"integrity_or_technical_failure")

    def test_engine_failure_and_interrupt_are_terminal(self):
        for failure, expected in ((RuntimeError("bad child"),"integrity_or_technical_failure"),
                                  (KeyboardInterrupt(),"interrupted")):
            with self.subTest(expected=expected):
                def execute(*args): raise failure
                status=self.perform(execute=execute)
                self.assertEqual(status["state"],expected)
                self.assertEqual(status["recorded"],0)

    def test_receipts_never_overwritten(self):
        item=self.design["plan"][0]
        args=(self.out,item,outcome(item),.01,self.manifest,plan,analysis)
        row=run.store_receipt(*args)
        with self.assertRaisesRegex(ValueError,"duplicate"):
            run.store_receipt(*args)
        self.assertEqual(json.loads((self.out/"rows"/(item["id"]+".json")).read_text()),row)

    def test_persistent_invocation_marker(self):
        path=Path(self.tmp.name)/"invocation.json"
        run.claim_invocation(path,{"run":1})
        with self.assertRaises(FileExistsError): run.claim_invocation(path,{"run":2})
        self.assertEqual(json.loads(path.read_text()),{"run":1})

    def test_json_duplicate_and_missing_fields_rejected(self):
        with self.assertRaisesRegex(ValueError,"Duplicate"):
            run.parse_output('{"sweeps":1,"sweeps":2}')
        with self.assertRaisesRegex(ValueError,"fields"):
            run.parse_output('{}')

    def test_deadline_no_child_started_if_expired(self):
        with patch.object(run.subprocess,"Popen") as child:
            with self.assertRaises(run.Cutoff):
                run.command(["never-called"],time.monotonic()-1,ROOT)
            child.assert_not_called()

    def test_deadline_kills_child_process_group(self):
        with patch.object(run.subprocess,"Popen") as popen, patch.object(run.os,"killpg") as kill:
            child=popen.return_value
            child.pid=7654
            child.communicate.side_effect=[run.subprocess.TimeoutExpired("mock",.1),("","")]
            with self.assertRaises(run.Cutoff): run.command(["mock"],time.monotonic()+1,ROOT)
            kill.assert_called_once_with(7654,run.signal.SIGKILL)
            self.assertTrue(popen.call_args.kwargs["start_new_session"])

    def test_published_registration_and_modified_file_rejected(self):
        result=run.registration(ROOT,time.monotonic()+30)
        self.assertEqual(result["files"]["plan.json"],run.sha(ROOT/run.ROUND1/"plan.json"))
        real_command=run.command
        def altered(argv,*args,**kwargs):
            value=real_command(argv,*args,**kwargs)
            return value+"tampered" if len(argv)>2 and argv[1]=="show" and argv[2].endswith("/plan.json") else value
        with patch.object(run,"command",side_effect=altered):
            with self.assertRaisesRegex(ValueError,"registration differs"):
                run.registration(ROOT,time.monotonic()+30)

    def test_uncommitted_registration_rejected(self):
        def fake(argv,*args):
            if argv[1]=="rev-parse": return "head"
            if argv[1]=="log": return ""
            self.fail("Should reject before reading/sampling")
        with patch.object(run,"command",side_effect=fake):
            with self.assertRaisesRegex(ValueError,"not been committed"):
                run.registration(ROOT,time.monotonic()+30)

    def test_source_and_snapshot_tampering_detected(self):
        root=Path(self.tmp.name)/"repo"
        root.mkdir()
        (root/"x.py").write_text("frozen\n")
        run.atomic(self.out/"source/x.py",(root/"x.py").read_bytes())
        hashes={"x.py":run.sha(root/"x.py")}
        run.verify_sources(root,self.out,hashes)
        (self.out/"source/x.py").write_text("modified\n")
        with self.assertRaisesRegex(ValueError,"source changed"):
            run.verify_sources(root,self.out,hashes)


if __name__ == "__main__":
    unittest.main(verbosity=2)
