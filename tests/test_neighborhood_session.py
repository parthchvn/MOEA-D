import argparse
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import tempfile
import time
import unittest
from unittest.mock import Mock, patch


SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
spec = importlib.util.spec_from_file_location("neighborhood_session", SCRIPTS / "neighborhood_session.py")
session = importlib.util.module_from_spec(spec)
spec.loader.exec_module(session)


class SessionTests(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.base = Path(tmp.name)
        self.repo = self.base / "checkout with spaces"
        self.repo.mkdir()
        self.bare = self.base / "mirror.git"
        self.git("init", "-q", "--bare", str(self.bare))
        self.git("init", "-q", "-b", session.BRANCH)
        self.git("config", "user.name", "Fixture")
        self.git("config", "user.email", "fixture@example.invalid")
        self.git("config", "commit.gpgsign", "false")
        self.git("config", "core.hooksPath", "/dev/null")
        (self.repo / ".gitignore").write_text("research/runs/\n")
        self.git("add", ".gitignore")
        self.git("commit", "-qm", "Setup")
        self.git("remote", "add", "origin", "https://github.com/parthchvn/MOEA-D.git")
        self.git("update-ref", "refs/remotes/origin/" + session.BRANCH, "HEAD")
        runs = self.repo / "research/runs/campaign"
        runs.mkdir(parents=True)
        self.addCleanup(patch.stopall)
        patch.multiple(session, ROOT=self.repo, BASE=runs, LOG=runs / "worker.log",
                       STATUS=runs / "worker-status.json").start()

    def git(self, *args):
        return subprocess.check_output(["git", *args], text=True, cwd=self.repo).strip()

    def test_reject_wrong_branch_dirty_checkout_and_unrelated_ahead_history(self):
        self.assertEqual(session.guard_checkout(), session.BRANCH)
        unrelated = self.repo / "other.txt"
        unrelated.write_text("keep me unchanged")
        with self.assertRaisesRegex(RuntimeError, "outside"):
            session.guard_checkout()
        self.git("add", "other.txt")
        self.git("commit", "-qm", "Unrelated work")
        with self.assertRaisesRegex(RuntimeError, "outgoing commit"):
            session.publish(time.time() + 10)
        self.git("switch", "-qc", "main")
        with self.assertRaisesRegex(RuntimeError, "dedicated checkout"):
            session.guard_checkout()
        self.assertEqual(unrelated.read_text(), "keep me unchanged")

    def test_publish_verified_paths_and_separate_note_without_staging_other_work(self):
        for parent in (session.REPORT, session.PACKET):
            out = self.repo / parent / "evidence.json"
            out.parent.mkdir(parents=True)
            out.write_text("{}\n")
        index = self.repo / session.PACKET / "INDEX.json"
        index.write_text("{}\n")
        expected_hash = hashlib.sha256(index.read_bytes()).hexdigest()
        note = self.repo / session.NOTE
        note.write_text(f"A finite observation.\n\nEvidence INDEX.json SHA-256: {expected_hash}\n")
        real_run = session.checked_run

        def route_only_push_to_disposable_mirror(args, deadline):
            if args[:3] == ["git", "push", "origin"]:
                self.assertEqual(args[3:], [f"HEAD:refs/heads/{session.BRANCH}"])
                args = ["git", "push", str(self.bare), args[3]]
            return real_run(args, deadline)

        with patch.object(session, "checked_run", side_effect=route_only_push_to_disposable_mirror):
            session.publish(time.time() + 10, include_note=False)
            self.assertEqual(self.git("diff-tree", "--no-commit-id", "--name-only", "-r", "HEAD").splitlines(),
                             sorted([str(session.PACKET / "INDEX.json"), *(str(p / "evidence.json") for p in (session.PACKET, session.REPORT))]))
            self.assertTrue(self.git("status", "--short", "--", str(session.NOTE)))
            session.publish(time.time() + 10)
            self.assertEqual(self.git("diff-tree", "--no-commit-id", "--name-only", "-r", "HEAD"), str(session.NOTE))
            self.assertEqual(self.git("--git-dir=" + str(self.bare), "rev-parse", session.BRANCH),
                             self.git("rev-parse", "HEAD"))
            head = self.git("rev-parse", "HEAD")
            session.publish(time.time() + 10)
            self.assertEqual(head, self.git("rev-parse", "HEAD"))
            # Both a stale tracked note and a new note with the wrong digest
            # are excluded when a subsequent evidence packet is published.
            index.write_text('{"new": true}\n')
            self.assertFalse(session.publish(time.time() + 10))
            self.assertEqual(self.git("diff-tree", "--no-commit-id", "--name-only", "-r", "HEAD"),
                             str(session.PACKET / "INDEX.json"))
            note.write_text("Mismatched draft with previous digest " + expected_hash)
            self.assertFalse(session.publish(time.time() + 10))
            self.assertTrue(self.git("status", "--short", "--", str(session.NOTE)))
            new_hash = hashlib.sha256(index.read_bytes()).hexdigest()
            note.write_text(f"Evidence INDEX.json SHA-256: {new_hash}\n")
            self.assertTrue(session.publish(time.time() + 10))
            self.assertEqual(self.git("diff-tree", "--no-commit-id", "--name-only", "-r", "HEAD"),
                             str(session.NOTE))

    def test_budget_stop_promotes_partial_receipts_with_no_holdout_or_new_budget(self):
        calls = []
        def stage(args, deadline):
            name = args[args.index("--stage") + 1]
            calls.append(name)
            return 2 if name == "main" else 0
        with patch.object(session, "bounded_run", side_effect=stage), patch.object(session, "checked_run"), \
             patch.object(session, "promote") as promote, patch.object(session, "publish") as publish:
            self.assertEqual(session.worker("local-activation", time.time() + 25, 25), 0)
        self.assertEqual(calls, ["smoke", "calibrate", "main"])
        promote.assert_called_once()
        publish.assert_called_once()
        self.assertIn("Partial", session.STATUS.read_text())

    def test_missing_git_auth_preserves_local_evidence_as_reviewable(self):
        with patch.object(session, "bounded_run", return_value=0), patch.object(session, "checked_run"), \
             patch.object(session, "promote"), patch.object(session, "publish", side_effect=RuntimeError("push failed")):
            self.assertEqual(session.worker("local-activation", time.time() + 25, 25), 1)
        self.assertIn('"state": "push-pending"', session.STATUS.read_text())

    def test_agent_now_receives_scoped_prompt_without_waiting(self):
        with patch.object(os, "execvp") as execute, patch.object(os, "chdir"), \
             patch.object(session, "output", return_value="--sandbox <MODE>"):
            session.agent("test-run", time.time()+45, start_now=True)
        command, args = execute.call_args.args
        self.assertEqual(command, "codex")
        self.assertIn("workspace-write", args)
        self.assertIn("test-run", args[-1])
        self.assertIn(str(session.NOTE), args[-1])
        self.assertIn("LARGE_T_AGENT.md", args[-1])

    def test_optional_codex_options_follow_the_installed_cli(self):
        with patch.object(session, "output", return_value="  --sandbox <MODE>"), patch.object(subprocess, "run") as probe:
            self.assertEqual(session.codex_command("goal"), ["codex", "--sandbox", "workspace-write", "goal"])
            probe.assert_not_called()
        help_text = "  --no-daemon\n  --enable <FEATURE>\n  --no-alt-screen"
        with patch.object(session, "output", return_value=help_text), patch.object(subprocess, "run", return_value=Mock(returncode=0, stdout="goals    stable    false\n")):
            flags = session.codex_command("goal")
            self.assertIn("--no-daemon", flags)
            self.assertIn("goals", flags)
            self.assertIn("--no-alt-screen", flags)

    def test_promote_preserves_previous_files_in_ignored_tree(self):
        previous = self.repo / session.REPORT / "unfinished-notes"
        previous.parent.mkdir(parents=True)
        previous.write_text("mine")
        fresh = self.base / "fresh"
        fresh.mkdir()
        (fresh / "report.md").write_text("new")
        session.install_outputs(fresh, session.REPORT)
        self.assertEqual((self.repo / session.REPORT / "report.md").read_text(), "new")
        self.assertEqual(next(session.BASE.rglob("unfinished-notes")).read_text(), "mine")
        self.assertFalse(previous.exists())

    def test_publish_only_retains_expired_budget_and_refuses_unverified_current_run(self):
        args = argparse.Namespace(publish_only=True, seconds=18000)
        elapsed = time.time() - 1000
        session.update_status("same-activation", "push-pending", "Auth failed", elapsed)
        for path in (session.PACKET, session.REPORT):
            (self.repo / path).mkdir(parents=True)
        with patch.object(os, "chdir"), patch.object(session, "checked_run") as verify, \
             patch.object(session, "publish", return_value=False) as publish:
            self.assertEqual(session.launch(args), 0)
            self.assertIn("verify", verify.call_args.args[0])
            self.assertLessEqual(publish.call_args.args[0] - time.time(), 300)
            receipt = json.loads(session.STATUS.read_text())
            self.assertEqual(receipt["activation"], "same-activation")
            self.assertEqual(receipt["deadline"], session.utc(elapsed))
            self.assertIn("pending", receipt["message"])
            session.update_status("another-activation", "main", "In progress", time.time() + 500)
            with self.assertRaisesRegex(RuntimeError, "no verified publication receipt"):
                session.launch(args)
            publish.assert_called_once()

    def test_science_work_never_uses_the_analysis_or_review_reservations(self):
        now = time.time()
        end = now + 18000
        with patch.object(session, "bounded_run", return_value=2) as stage, \
             patch.object(session, "checked_run") as tests, patch.object(session, "promote") as promote, \
             patch.object(session, "publish", side_effect=RuntimeError("test stop")) as publish:
            self.assertEqual(session.worker("test", end, 18000), 1)
        self.assertEqual(tests.call_args.args[1], end - 2100)
        stage_command, stage_limit = stage.call_args.args
        self.assertEqual(stage_limit, end - 2100)
        self.assertLessEqual(int(stage_command[-1]), 15900 - 4)
        self.assertEqual(promote.call_args.args[0], end - 1500)
        self.assertEqual(publish.call_args.args[0], end - 1500)

    def test_existing_tmux_session_reattaches_without_changing_activation(self):
        args = argparse.Namespace(publish_only=False, check=False, detach=True, agent_now=True, seconds=40)
        with patch.object(os, "chdir"), patch.object(session.shutil, "which", return_value="/fake/tmux"), \
             patch.object(subprocess, "run", return_value=Mock(returncode=0)), \
             patch.object(session, "output", return_value=str(session.ROOT)), \
             patch.object(session, "attach") as attach, patch.object(session, "tmux") as create:
            self.assertEqual(session.launch(args), 0)
        create.assert_not_called()
        attach.assert_called_once_with("=" + session.SESSION, True)
