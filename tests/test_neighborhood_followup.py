"""Regressions for continuing past a finished Codex turn."""
import argparse
import hashlib
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import time
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]/"scripts"))
import neighborhood_followup as follow


class FollowupTests(unittest.TestCase):
    def test_finished_turn_starts_next_and_research_resumes_after_publication(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            def git(*args):
                return subprocess.check_output(["git",*args], cwd=root, text=True).strip()
            git("init","-q","-b",follow.session.BRANCH)
            git("config","user.email","fixture@example.invalid")
            git("config","user.name","Fixture")
            mirror = root.parent / (root.name+"-mirror.git")
            git("init","--bare","-q",str(mirror))
            self.addCleanup(shutil.rmtree, mirror)
            git("remote","add","origin","https://github.com/parthchvn/MOEA-D.git")
            (root/".gitignore").write_text("research/runs/\nfig*.png\n")
            for path in (follow.session.PACKET/"INDEX.json",follow.session.NOTE):
                (root/path).parent.mkdir(parents=True,exist_ok=True)
                (root/path).write_text("fixture")
            (root/follow.session.NOTE).write_text("Evidence INDEX.json SHA-256: "+hashlib.sha256(b"fixture").hexdigest()+"\n")
            git("add",".")
            git("commit","-qm","fixture")
            git("update-ref","refs/remotes/origin/"+follow.session.BRANCH,"HEAD")
            base = root/"research/runs/follow"
            original = follow.run_child
            real_checked = follow.session.checked_run
            tasks = []
            def child(cmd,cwd,end,log=None):
                if cmd[0]=="codex":
                    tasks.append(cmd[-1])
                    Path(cmd[-2]).write_text("This synthetic checkpoint exercises completion and the queued obligation. "
                                             "See the fixture for reproducibility.\nNext task: EXHAUSTED\n")
                    (cwd/"deliverables"/"evidence.csv").write_text("n,result\n1,1\n")
                elif "verify" not in cmd:
                    original(cmd,cwd,end,log)
            def checked(cmd,end):
                if cmd[:3]==["git","push","origin"]:
                    cmd=["git","push",str(mirror),cmd[3]]
                real_checked(cmd,end)
            old=Path.cwd()
            self.addCleanup(os.chdir,old)
            with patch.multiple(follow.session,ROOT=root,BASE=base,LOG=base/"log"), \
                 patch.object(follow,"run_child",side_effect=child), \
                 patch.object(follow.session,"checked_run",side_effect=checked), \
                 patch.object(follow.signal,"signal"),patch.dict(os.environ), \
                 patch.object(follow,"TASKS",("First distinct task","Second distinct task")):
                follow.supervise(time.time()+60)
                follow.supervise(time.time()+60)
                self.assertEqual(len(tasks),2)
                self.assertIn("Second distinct task",tasks[1])
                self.assertEqual(git("rev-parse","HEAD"),git("--git-dir="+str(mirror),"rev-parse",follow.session.BRANCH))
                self.assertTrue((root/follow.DEST/"round-0002"/"evidence.csv").is_file())
                with patch.object(follow,"launch",return_value=0) as launch:
                    args=argparse.Namespace(publish_only=False,check=False,agent_now=True)
                    self.assertEqual(follow.session.launch(args),0)
                    launch.assert_called_once_with(args)

    def test_long_child_is_terminated_on_budget(self):
        with self.assertRaises(subprocess.TimeoutExpired):
            follow.run_child([sys.executable,"-c","import time; time.sleep(60)"],
                             Path.cwd(),time.time()+0.1)
