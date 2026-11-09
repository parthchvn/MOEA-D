"""Bounded local tmux campaign; the benchmark worker and research agent have separate clocks/windows."""
import argparse
import fcntl
import hashlib
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import shlex
import shutil
import signal
import subprocess
import sys
import tempfile
import time
import uuid


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "research/runs/larger-neighborhoods-20261109"
REPORT = Path("research/reports/large-T-20261109/campaign")
PACKET = Path("research/evidence/large-T-20261109/campaign")
NOTE = Path("research/reports/large-T-20261109/interpretation.md")
BRANCH = "research/larger-neighborhoods-20261109"
SESSION = "moead-large-T"
STAGES = ("smoke", "calibrate", "main", "holdout")
SCRIPTS = ROOT / "scripts"
STATUS = BASE / "worker-status.json"
LOG = BASE / "worker.log"


def output(*args):
    return subprocess.check_output(args, cwd=ROOT, text=True).strip()


def allowed_path(path):
    target = Path(path)
    return target == NOTE or any(target == p or p in target.parents for p in (REPORT, PACKET))


def guard_checkout():
    branch = output("git", "branch", "--show-current")
    if branch != BRANCH and not branch.startswith(BRANCH + "-"):
        raise RuntimeError(f"Use a dedicated checkout of {BRANCH} or a branch named {BRANCH}-…")
    urls = output("git", "remote", "get-url", "--push", "--all", "origin").splitlines()
    accepted = {
        "https://github.com/parthchvn/MOEA-D", "git@github.com:parthchvn/MOEA-D",
        "ssh://git@github.com/parthchvn/MOEA-D",
    }
    if len(urls) != 1 or urls[0].removesuffix(".git") not in accepted:
        raise RuntimeError("Expected a single GitHub push destination at parthchvn/MOEA-D.")
    # No reset/stash/checkout. A partially generated curated packet or note can be resumed.
    raw = subprocess.check_output(["git", "status", "--porcelain=v1", "-z", "--untracked-files=all"], cwd=ROOT)
    for entry in os.fsdecode(raw).split("\0"):
        if not entry:
            continue
        if "R" in entry[:2] or "C" in entry[:2] or not allowed_path(entry[3:]):
            raise RuntimeError("The worktree contains changes outside the three evidence paths. "
                               "Use a clean dedicated checkout; existing files were left in place.")
    return branch


def preflight():
    branch = guard_checkout()
    required = ("tmux", "codex", os.environ.get("CXX", "c++"))
    for program in required:
        if shutil.which(program) is None:
            raise RuntimeError(f"Missing {program}. Install it and run the launcher again.")
    for path in ("research/LARGE_T_AGENT.md", "scripts/neighborhood_campaign.py",
                 "scripts/analyze_neighborhood_campaign.py", "scripts/package_neighborhood_evidence.py",
                 "scripts/neighborhood_sweep.cpp"):
        if not (ROOT / path).is_file():
            raise RuntimeError(f"Required repository file missing: {path}")
    for variable in ("GIT_AUTHOR_IDENT", "GIT_COMMITTER_IDENT"):
        output("git", "var", variable)
    print(f"Dedicated branch {branch}. {output('codex', '--version')}. {output('tmux', '-V')}.", flush=True)


def choose_python(install):
    candidates = [ROOT / ".venv/bin/python", Path(sys.executable)]
    verify = ("import sys, numpy, matplotlib; assert sys.version_info >= (3,11); "
              "assert tuple(map(int,numpy.__version__.split('.')[:2])) >= (1,26); "
              "assert tuple(map(int,matplotlib.__version__.split('.')[:2])) >= (3,8)")
    for candidate in candidates:
        if candidate.is_file() and subprocess.run([str(candidate), "-c", verify], stdout=subprocess.DEVNULL,
                                                   stderr=subprocess.DEVNULL).returncode == 0:
            return str(candidate)
    venv = candidates[0]
    if not install:
        raise RuntimeError("Missing dependencies. A regular launch creates .venv and installs requirements.txt.")
    if not venv.exists():
        subprocess.run([sys.executable, "-m", "venv", str(venv.parents[1])], check=True)
    subprocess.run([str(venv), "-m", "pip", "install", "-r", str(ROOT / "requirements.txt")], check=True)
    subprocess.run([str(venv), "-c", verify], check=True)
    return str(venv)


def utc(timestamp):
    return datetime.fromtimestamp(timestamp, timezone.utc).isoformat(timespec="seconds")


def update_status(token, state, message, deadline):
    BASE.mkdir(parents=True, exist_ok=True)
    tmp = BASE / ("worker-status-" + uuid.uuid4().hex + ".tmp")
    tmp.write_text(json.dumps(dict(activation=token, state=state, message=message,
                                   updated=utc(time.time()), deadline=utc(deadline)), indent=2) + "\n")
    tmp.replace(STATUS)
    line = f"{utc(time.time())}  {state}: {message}"
    with LOG.open("a") as log:
        print(line, file=log)
    print(line, flush=True)


def bounded_run(args, deadline):
    seconds = deadline - time.time()
    if seconds <= 0:
        raise TimeoutError("wall ceiling reached")
    print("$ " + shlex.join(map(str, args)), flush=True)
    with LOG.open("a") as log:
        print("$ " + shlex.join(map(str, args)), file=log, flush=True)
        child = subprocess.Popen(list(map(str, args)), cwd=ROOT, stdout=log,
                                 stderr=subprocess.STDOUT, start_new_session=True)
        try:
            return child.wait(timeout=seconds)
        finally:
            if child.poll() is None:
                os.killpg(child.pid, signal.SIGTERM)
                try:
                    child.wait(timeout=2)
                except subprocess.TimeoutExpired:
                    os.killpg(child.pid, signal.SIGKILL)
                    child.wait()


def checked_run(args, deadline):
    code = bounded_run(args, deadline)
    if code:
        raise RuntimeError(f"{Path(str(args[0])).name} exited {code}; see {LOG.relative_to(ROOT)}")


def collect_runs():
    return [BASE / stage for stage in STAGES if (BASE / stage / "manifest.json").is_file()]


def install_outputs(src, target):
    dest = ROOT / target
    if not src.is_dir() or not any(p.is_file() for p in src.rglob("*")):
        raise RuntimeError(f"Expected a nonempty generated directory at {src}")
    if any(p.is_symlink() for p in (dest, *dest.parents) if p != ROOT and ROOT in p.parents):
        raise RuntimeError(f"Refusing to replace a symlinked output path: {target}")
    if any(p.is_symlink() for p in (*src.rglob("*"), *dest.rglob("*"))):
        raise RuntimeError("Curated evidence directories must contain regular files.")
    dest.parent.mkdir(parents=True, exist_ok=True)
    # Keep previous generated or pending work in the ignored run tree. Both renames
    # happen on the checkout's filesystem; an interrupted promotion is recoverable.
    backup = BASE / "previous-publications" / uuid.uuid4().hex / target
    if dest.exists():
        backup.parent.mkdir(parents=True)
        os.replace(dest, backup)
    try:
        os.replace(src, dest)
    except OSError:
        if backup.exists() and not dest.exists():
            os.replace(backup, dest)
        raise


def promote(deadline):
    runs = collect_runs()
    if not any(next((r / "rows").glob("*.json"), None) for r in runs):
        raise RuntimeError("No recorded trajectories to publish.")
    with tempfile.TemporaryDirectory(dir=BASE, prefix="promote-") as tmp:
        report, packet = Path(tmp) / "report", Path(tmp) / "packet"
        checked_run([sys.executable, SCRIPTS / "analyze_neighborhood_campaign.py",
                     "--runs", *runs, "--out", report], deadline)
        checked_run([sys.executable, SCRIPTS / "package_neighborhood_evidence.py",
                     "pack", "--runs", *runs, "--out", packet], deadline)
        checked_run([sys.executable, SCRIPTS / "package_neighborhood_evidence.py",
                     "verify", "--packet", packet], deadline)
        install_outputs(packet, PACKET)
        install_outputs(report, REPORT)


def note_matches_packet():
    note, index = ROOT / NOTE, ROOT / PACKET / "INDEX.json"
    if not note.is_file() or not index.is_file() or note.is_symlink() or index.is_symlink():
        return False
    marker = "Evidence INDEX.json SHA-256: "
    digest = hashlib.sha256(index.read_bytes()).hexdigest()
    try:
        lines = note.read_text(encoding="utf-8").splitlines()
    except UnicodeDecodeError:
        return False
    bindings = [line for line in lines if line.startswith(marker)]
    return bindings == [marker + digest]


def publish(deadline, include_note=True):
    BASE.mkdir(parents=True, exist_ok=True)
    with (BASE / ".publish.lock").open("a") as lock:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        return publish_locked(deadline, include_note)


def publish_locked(deadline, include_note):
    branch = guard_checkout()
    # An unrelated local commit must never hitch a ride with an evidence push.
    branch_ref = "refs/remotes/origin/" + branch
    if subprocess.run(["git", "show-ref", "--verify", "--quiet", branch_ref], cwd=ROOT).returncode:
        branch_ref = "refs/remotes/origin/" + BRANCH
    if subprocess.run(["git", "merge-base", "--is-ancestor", branch_ref, "HEAD"], cwd=ROOT).returncode:
        raise RuntimeError("Branch diverged or lacks the setup tracking ref. Fetch and inspect before publishing.")
    commits = output("git", "rev-list", f"{branch_ref}..HEAD").splitlines()
    for commit in commits:
        touched = output("git", "diff-tree", "--root", "-m", "--no-commit-id", "--name-only", "-r", commit)
        if any(not allowed_path(file) for file in touched.splitlines()):
            raise RuntimeError("An outgoing commit includes non-evidence files. Inspect it before pushing.")
    has_note = include_note and note_matches_packet()
    if include_note and (ROOT / NOTE).exists() and not has_note:
        print("The interpretation does not identify the current packet digest; publishing evidence only.", flush=True)
    targets = (REPORT, PACKET, NOTE) if has_note else (REPORT, PACKET)
    paths = [str(p) for p in targets if (ROOT / p).exists()]
    if not paths:
        raise RuntimeError("No curated output exists.")
    checked_run(["git", "add", "--", *paths], deadline)
    changed = subprocess.run(["git", "diff", "--cached", "--quiet", "--", *paths], cwd=ROOT).returncode
    if changed == 1:
        checked_run(["git", "commit", "--only", "-m", "Record larger-neighborhood campaign evidence",
                     "--", *paths], deadline)
    elif changed != 0:
        raise RuntimeError("Could not inspect staged evidence.")
    checked_run(["git", "push", "origin", f"HEAD:refs/heads/{branch}"], deadline)
    return has_note


def worker(token, end, duration):
    # Reserve time for analysis, packaging, a push, and interpretation even after a partial run.
    evidence_end = end - min(1500, max(6, duration // 8))
    sample_end = evidence_end - min(600, max(4, duration // 10))
    phase = "tests"
    os.environ.update(OMP_NUM_THREADS="1", OPENBLAS_NUM_THREADS="1", MKL_NUM_THREADS="1",
                      VECLIB_MAXIMUM_THREADS="1", MPLBACKEND="Agg",
                      MPLCONFIGDIR=str(ROOT / ".cache/matplotlib"), GIT_TERMINAL_PROMPT="0")
    try:
        update_status(token, phase, "Running the entire test suite.", end)
        checked_run([sys.executable, "-m", "unittest", "discover", "-s", "tests", "-v"], sample_end)
        partial = False
        for stage in STAGES:
            remaining = int(sample_end - time.time()) - 4
            if remaining < 1:
                partial = True
                break
            phase = stage
            update_status(token, phase, "Running frozen plan; completed receipts are reused.", end)
            try:
                rc = bounded_run([sys.executable, SCRIPTS / "neighborhood_campaign.py", "--stage", stage,
                                  "--out", BASE, "--seconds", remaining], sample_end)
            except (TimeoutError, subprocess.TimeoutExpired):
                partial = True
                break
            if rc == 2:
                partial = True
                break
            if rc != 0:
                raise RuntimeError(f"{stage} failed (exit {rc}); scaling stopped.")
        phase = "evidence"
        update_status(token, phase, "Validating trajectories and preparing reports and plots.", end)
        promote(evidence_end)
        phase = "push"
        try:
            publish(evidence_end, include_note=False)
        except (OSError, RuntimeError, subprocess.SubprocessError) as exc:
            update_status(token, "push-pending",
                          f"Evidence verified locally. Git publication failed: {exc}. Once Git is ready, use --publish-only.", end)
            return 1
        update_status(token, "review", ("Partial" if partial else "Complete") +
                      " campaign evidence published. Codex can now interpret the receipts.", end)
        # The agent writes its finished interpretation by atomic rename. No turn is required to publish it.
        while time.time() < end - 30:
            if note_matches_packet() and output("git", "status", "--porcelain", "--", str(NOTE)):
                try:
                    if not publish(end - 4):
                        continue
                except (OSError, RuntimeError, subprocess.SubprocessError) as exc:
                    update_status(token, "push-pending", f"Interpretation ready, Git publication pending: {exc}", end)
                    return 1
                update_status(token, "done", "Interpretation and empirical evidence published.", end)
                return 0
            time.sleep(min(5, max(0.1, end - 30 - time.time())))
        return 0
    except (KeyboardInterrupt, InterruptedError):
        update_status(token, "interrupted", f"{phase} stopped. Completed trajectory receipts are preserved.", end)
        return 130
    except (OSError, RuntimeError, subprocess.SubprocessError) as exc:
        update_status(token, "failed", f"{phase}: {exc}", end)
        return 1


def tmux(*args):
    subprocess.run(["tmux", *args], cwd=ROOT, check=True)


def codex_command(prompt):
    # Probe the installed TUI, not a guessed version threshold. Older clients
    # have no shared daemon, and feature flags have changed between releases.
    help_text = output("codex", "--help")
    flags = [line.lstrip() for line in help_text.splitlines()]
    cmd = ["codex", "--sandbox", "workspace-write"]
    if any(line.startswith("--no-daemon") for line in flags):
        cmd.append("--no-daemon")
    if any(line.startswith("--enable ") for line in flags):
        features = subprocess.run(["codex", "features", "list"], text=True,
                                  capture_output=True, cwd=ROOT)
        if features.returncode == 0 and any(line.split()[:1] == ["goals"] for line in features.stdout.splitlines()):
            cmd.extend(["--enable", "goals"])
    if any(line.startswith("--no-alt-screen") for line in flags):
        cmd.append("--no-alt-screen")
    cmd.append(prompt)
    return cmd


def agent(token, end, start_now=False):
    print(f"Worker is running. Receipts and log: {BASE}. Research deadline: {utc(end)}.", flush=True)
    while not start_now and time.time() < end - 3:
        if STATUS.exists():
            record = json.loads(STATUS.read_text())
            if record["activation"] == token:
                if record["state"] == "interrupted":
                    print("Worker interrupted. Resume in a new activation when ready.")
                    return
                if record["state"] in ("review", "push-pending", "published", "failed", "done"):
                    break
        time.sleep(1)
    if time.time() >= end - 3:
        return
    print("Opening interactive Codex in the campaign checkout.", flush=True)
    prompt = (f"Use a persistent Codex goal if available. Your objective for this bounded activation follows. Read and execute research/LARGE_T_AGENT.md. The worker status is {STATUS.relative_to(ROOT)}. "
              f"Use only the remaining time until {utc(end)}. The worker already owns all sampling and "
              "publication. If receipts failed validation, diagnose the failure without making a runtime claim. "
              f"Write your finished interpretation by atomic rename to {NOTE} only after verified local evidence exists. "
              f"Bind the note to {PACKET}/INDEX.json: include exactly one standalone line "
              "'Evidence INDEX.json SHA-256: <digest>' with the 64 lowercase hex characters of its bytewise SHA-256. ")
    if start_now:
        prompt += (f"Begin now with a proof or counterexample task while the worker runs. Keep interim work in "
                   f"{BASE.relative_to(ROOT)}/agent-work/{token}/. Do not change the frozen harness or Git history. "
                   f"Monitor worker-status.json for this activation ({token}); before finalizing your note read the "
                   "actual verified report and the held-out or partial status. A push-pending state has valid local evidence. "
                   "Do not treat a previous activation's report as results for this one.")
    os.chdir(ROOT)
    os.execvp("codex", codex_command(prompt))


def clock(end):
    # ID rather than the reusable human-readable name, so an old activation cannot kill another.
    session_id = output("tmux", "display-message", "-p", "-t", os.environ["TMUX_PANE"], "#{session_id}")
    print(f"This activation ends at {utc(end)}. Checkpoints are kept under {BASE}.", flush=True)
    while time.time() < end:
        time.sleep(min(10, max(0, end - time.time())))
    tmux("kill-session", "-t", session_id)


def attach(target, detached):
    if detached:
        print(f"Attach using tmux attach -t {SESSION}. Detach with Ctrl-b, then d.")
    elif os.environ.get("TMUX"):
        tmux("switch-client", "-t", target)
    else:
        os.execvp("tmux", ["tmux", "attach-session", "-t", target])


def launch(args):
    os.chdir(ROOT)
    if args.publish_only:
        guard_checkout()
        deadline = time.time() + min(args.seconds, 300)
        previous = json.loads(STATUS.read_text()) if STATUS.is_file() else {}
        if previous and previous.get("state") not in {"review", "done", "push-pending", "published"}:
            raise RuntimeError("The current activation has no verified publication receipt. Resume the worker "
                               "to validate and prepare its evidence before using --publish-only.")
        os.environ["GIT_TERMINAL_PROMPT"] = "0"
        if not (ROOT / REPORT).is_dir() or not (ROOT / PACKET).is_dir():
            raise RuntimeError("No curated packet and report yet. Resume the worker to generate them.")
        BASE.mkdir(parents=True, exist_ok=True)
        checked_run([sys.executable, SCRIPTS / "package_neighborhood_evidence.py",
                     "verify", "--packet", ROOT / PACKET], deadline)
        has_note = publish(deadline)
        if previous:
            end = datetime.fromisoformat(previous["deadline"]).timestamp()
            message = "Explicit retry verified and published the current evidence"
            message += " and its digest-bound interpretation." if has_note else ". A digest-bound interpretation is pending."
            update_status(previous["activation"], "published", message, end)
        return 0
    if shutil.which("tmux") and not args.check:
        live = subprocess.run(["tmux", "has-session", "-t", "="+SESSION],
                              stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL).returncode == 0
        if live:
            if output("tmux", "show-options", "-qv", "-t", "="+SESSION, "@moead_root") != str(ROOT):
                raise RuntimeError("This tmux name belongs to another checkout. Attach to it directly.")
            attach("="+SESSION, args.detach)
            return 0
    preflight()
    interpreter = choose_python(install=not args.check)
    if args.check:
        socket = "moead-check-" + uuid.uuid4().hex[:10]
        try:
            tmux("-L", socket, "new-session", "-d", "-s", "probe", "sleep 30")
            tmux("-L", socket, "has-session", "-t", "=probe")
        finally:
            subprocess.run(["tmux", "-L", socket, "kill-server"], stderr=subprocess.DEVNULL)
        print("Preflight passed, including a disposable tmux socket check. No benchmark was started.")
        return 0
    token = uuid.uuid4().hex[:12]
    end = int(time.time()) + args.seconds
    BASE.mkdir(parents=True, exist_ok=True)

    def command(mode):
        cmd = [interpreter, str(Path(__file__).resolve()), "--internal", mode, token, str(end), str(args.seconds)]
        if mode == "clock" and sys.platform == "darwin" and shutil.which("caffeinate"):
            cmd = ["caffeinate", "-i", *cmd]
        return "exec " + shlex.join(cmd)

    tmux("new-session", "-d", "-s", SESSION, "-n", "clock", "-c", str(ROOT), command("clock"))
    try:
        tmux("set-option", "-t", "="+SESSION, "@moead_root", str(ROOT))
        for window in ("worker", "agent"):
            mode = "agent-now" if window == "agent" and args.agent_now else window
            tmux("new-window", "-d", "-t", SESSION+":", "-n", window, "-c", str(ROOT), command(mode))
        tmux("select-window", "-t", SESSION+":agent")
    except BaseException:
        tmux("kill-session", "-t", "="+SESSION)
        raise
    print(f"Local run ends at {utc(end)}. Follow {LOG.relative_to(ROOT)}. "
          "Rerun the same launcher to reattach; this preserves the deadline.", flush=True)
    attach("="+SESSION, args.detach)
    return 0


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--check", action="store_true", help="Check dependencies and Git target without sampling")
    group.add_argument("--publish-only", action="store_true", help="Commit/push already prepared evidence and interpretation")
    parser.add_argument("--agent-now", action="store_true", help="Start the interactive research agent alongside sampling; default waits for verified evidence or a failure")
    parser.add_argument("--detach", action="store_true", help="Leave the session detached after launch")
    parser.add_argument("--seconds", type=int, default=18_000, help="Total wall ceiling per new activation (default 18000)")
    parser.add_argument("--internal", nargs=4, help=argparse.SUPPRESS)
    args = parser.parse_args()
    if args.internal:
        mode, token, end, duration = args.internal
        if mode == "worker":
            def stop_worker(sig, frame):
                raise InterruptedError("terminal closed or worker interrupted")
            for sig in (signal.SIGHUP, signal.SIGTERM):
                signal.signal(sig, stop_worker)
            tmux("set-window-option", "-t", os.environ["TMUX_PANE"], "remain-on-exit", "on")
            return worker(token, int(end), int(duration))
        if mode in ("agent", "agent-now"):
            tmux("set-window-option", "-t", os.environ["TMUX_PANE"], "remain-on-exit", "on")
            return agent(token, int(end), start_now=mode == "agent-now")
        if mode == "clock":
            return clock(int(end))
        parser.error("Unknown internal mode")
    if args.seconds < 30:
        parser.error("--seconds must be at least 30")
    return launch(args)


if __name__ == "__main__":
    try:
        sys.exit(main())
    except (OSError, RuntimeError, subprocess.SubprocessError, KeyboardInterrupt) as exc:
        print(f"Local campaign stopped: {exc}", file=sys.stderr)
        sys.exit(1)
