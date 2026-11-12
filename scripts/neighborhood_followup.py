"""Run successive evidence and proof tasks after the frozen campaign has finished."""
import fcntl
import hashlib
import json
import os
from pathlib import Path
import re
import shlex
import shutil
import signal
import subprocess
import sys
import tempfile
import time
import uuid

import neighborhood_session as session

DEST = session.FOLLOWUP
NAME = "moead-large-T-research"
TASKS = (
    "Preregister a separate prospective n=512 low-noise comparison of T=1 and T=23. "
    "Use fresh deterministic seeds and fixed arms, cap, replication count, CI and stopping rule. "
    "Specify a restricted-mean analysis for censored outcomes and U, S-U, post-S diagnostics. "
    "Publish the exact implementable plan before drawing any new outcome.",
    "Implement and execute the published round-1 plan on one local CPU. Run kernel tests first. "
    "Include runnable source, per-trial receipts, plan and model hashes, a plot and uncertainty. "
    "Keep completed rows and label partial work on cutoff. This is a new study, distinct from the blocked holdout.",
    "Independently audit the preceding experiment. Recompute the estimates and censoring directly "
    "from raw receipts. Check phase timing and whether the two experiments use disjoint seeds.",
    "Attempt the fixed-T noisy corner theorem. Start from the T=3 and T=1 hypotheses and the "
    "observed reinfection path. Bound time donor 1 spends at an incorrect weight. State exact gaps.",
    "Red-team the previous argument. Search small-n transitions for counterexamples, and audit "
    "each conditioning, boundary-time and simultaneous-repair step. Supply a reproducible witness or lemma.",
)


def next_task(root):
    rounds = sorted(root.glob("round-[0-9][0-9][0-9][0-9]"))
    for i, path in enumerate(rounds, 1):
        if path.name != f"round-{i:04d}" or not (path / "report.md").is_file():
            raise RuntimeError(f"Incomplete round history at {path}")
    if len(rounds) < len(TASKS):
        return len(rounds) + 1, TASKS[len(rounds)]
    lines = (rounds[-1] / "report.md").read_text().splitlines()
    pending = [line.removeprefix("Next task: ").strip() for line in lines if line.startswith("Next task: ")]
    if len(pending) != 1 or not pending[0]:
        raise ValueError("Latest checkpoint lacks one explicit Next task line")
    for path in rounds:
        metadata = path/".checkpoint.json"
        if not metadata.exists():
            metadata = path/"provenance.json"  # Old supervisor format.
        prior = json.loads(metadata.read_text())
        if prior["task"].strip().casefold() == pending[0].casefold():
            raise RuntimeError("Next task repeats a completed task; inspect the last research checkpoint")
    return len(rounds) + 1, pending[0]


def run_child(cmd, cwd, deadline, log=None):
    proc = subprocess.Popen(cmd, cwd=cwd, stdin=subprocess.DEVNULL, stdout=log,
                            stderr=subprocess.STDOUT, start_new_session=True)
    try:
        if proc.wait(timeout=max(.01, deadline-time.time())):
            raise RuntimeError(f"{cmd[0]} failed; inspect the round log")
    finally:
        if proc.poll() is None:
            os.killpg(proc.pid, signal.SIGTERM)
            try:
                proc.wait(timeout=2)
            except subprocess.TimeoutExpired:
                os.killpg(proc.pid, signal.SIGKILL)
                proc.wait()


def package(work, tag, task):
    checkout = session.ROOT
    clone = work/"worktree"
    output = clone/"deliverables"
    last = work/"last.md"
    if any(p.is_symlink() for p in (work, clone, last, output)) or not output.is_dir():
        raise ValueError("Invalid saved round workspace")
    source_head = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=clone, text=True).strip()
    # A recovery may run on a newer launcher commit. Its research inputs
    # and the already-published preceding rounds must match the saved clone.
    subprocess.run(["git","merge-base","--is-ancestor",source_head,"HEAD"],cwd=checkout,check=True)
    subprocess.run(["git","diff","--quiet",source_head,"HEAD","--",str(DEST),
                    str(session.NOTE),str(session.PACKET),str(session.REPORT)],cwd=checkout,check=True)
    body = last.read_text().strip()
    if len(body) < 80 or len(re.findall(r"^Next task: \S.*$",body,re.M)) != 1:
        raise RuntimeError(f"Invalid or empty checkpoint; full turn preserved at {work}")
    with tempfile.TemporaryDirectory(dir=work) as staging:
        stage = Path(staging)/"checkpoint"
        stage.mkdir()
        for source in sorted(output.rglob("*")):
            if source.is_symlink() or not source.resolve().is_relative_to(output.resolve()) or output.is_symlink():
                raise ValueError("Unexpected artifact link")
            if source.is_dir():
                continue
            rel = source.relative_to(output)
            if (not source.is_file() or source.suffix not in {".md",".py",".csv",".json",".png"}
                or any(not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._-]*", part) for part in rel.parts)
                or source.stat().st_size > 25_000_000 or rel.as_posix() == "report.md"):
                raise ValueError(f"Unexpected artifact: {rel}")
            (stage/rel).parent.mkdir(parents=True,exist_ok=True)
            shutil.copyfile(source,stage/rel)
        (stage/"report.md").write_text(body+"\n")
        (stage/".checkpoint.json").write_text(json.dumps({
            "task":task, "started_from":source_head, "work_id": work.name,
            "packet_sha256": hashlib.sha256((checkout/session.PACKET/"INDEX.json").read_bytes()).hexdigest(),
            "completed_utc":session.utc(time.time())},indent=2)+"\n")
        target = checkout/DEST/tag
        target.parent.mkdir(parents=True,exist_ok=True)
        stage.rename(target)


def recover(work_id, end):
    if not re.fullmatch(r"round-[0-9]{4}-[0-9a-f]{8}", work_id):
        raise ValueError("Specify the saved round directory name")
    session.guard_checkout()
    root = session.ROOT/DEST
    tag = work_id.rsplit("-",1)[0]
    work = session.BASE/"followup"/work_id
    with (session.BASE/"followup.lock").open("a") as lock:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        existing = root/tag
        if existing.exists():
            metadata = existing/".checkpoint.json"
            if not metadata.exists() or json.loads(metadata.read_text()).get("work_id") != work_id:
                raise RuntimeError(f"A different checkpoint already exists at {existing}")
        else:
            n, task = next_task(root)
            if tag != f"round-{n:04d}" or not (work/"last.md").is_file():
                raise RuntimeError("Expected the next unpublished round and its saved final response")
            package(work, tag, task)
        os.environ["GIT_TERMINAL_PROMPT"] = "0"
        session.publish(end, followup=True)
        print(f"Published saved checkpoint {DEST/tag}", flush=True)


def supervise(end):
    os.chdir(session.ROOT)
    def stop(signum, frame):
        raise InterruptedError("Research session interrupted")
    for sig in (signal.SIGHUP, signal.SIGTERM):
        signal.signal(sig, stop)
    os.environ.update(GIT_TERMINAL_PROMPT="0", MPLBACKEND="Agg", OMP_NUM_THREADS="1",
                      OPENBLAS_NUM_THREADS="1", PATH=str(Path(sys.executable).parent)+os.pathsep+os.environ["PATH"])
    checkout = session.ROOT
    base = session.BASE / "followup"
    base.mkdir(parents=True, exist_ok=True)
    # Retry a local checkpoint or non-fast-forward/auth failure before spending another turn.
    if (checkout / DEST).exists():
        session.publish(end, followup=True)
    run_child([sys.executable, "scripts/package_neighborhood_evidence.py", "verify",
               "--packet", str(session.PACKET)], checkout, end)
    while time.time() < end-15:
        n, task = next_task(checkout / DEST)
        if task == "EXHAUSTED":
            print("Research agenda exhausted; see the last round for the blocking evidence.", flush=True)
            return
        tag = f"round-{n:04d}"
        work = base / (tag+"-"+uuid.uuid4().hex[:8])
        work.mkdir()
        clone = work / "worktree"
        run_child(["git","clone","--quiet","--no-hardlinks","--no-local",str(checkout),str(clone)], checkout, end)
        run_child(["git","remote","remove","origin"], clone, end)
        output = clone / "deliverables"
        output.mkdir()
        remaining = int(end-time.time())
        prompt = f"""Read AGENTS.md, its research references, research/LARGE_T_THEORY.md, the committed
{session.NOTE}, and prior checkpoints under {DEST}. You have a local offline checkout and one CPU.
This is follow-up round {n}. Task: {task}
Base conclusions on the published evidence. Preserve the original preregistration and blocked holdout.
Verify any dependency on an earlier round before using it. If a prior experiment lacks a usable plan
or receipts, repair that obligation first. Use independent seeds for new experiments and commit the
plan in a prior round before measuring. Spend at most {max(1,remaining-25)} seconds on this turn.
Run relevant tests. Put only curated new reproducible outputs (markdown, python, csv, json, png)
under deliverables/ using relative links and simple filenames. The supervisor publishes them and your
final response as report.md. Keep raw private notes and logs outside deliverables. Do not push or commit.
Your final response is the research checkpoint: report measurements, assumptions, elapsed time,
checks, proof gaps and falsifiers. Label conjectures and candidate proofs. Give a short morning-report
summary of cumulative progress. End with exactly one standalone line 'Next task: <distinct concrete
question and why the latest evidence warrants it>'. Use 'Next task: EXHAUSTED' only if no actionable
question remains and explain the blocker. Do substantive work now, then return for the next turn."""
        last = work / "last.md"
        print(f"{tag}: {task}\nLocal log: {work/'codex.log'}", flush=True)
        with (work/"codex.log").open("ab") as log:
            for attempt in range(2):
                try:
                    run_child(["codex","exec","--sandbox","workspace-write","-o",str(last),prompt],
                              clone, end-10, log)
                    break
                except RuntimeError:
                    if attempt or end-time.time() < 60:
                        raise
                    print("Codex execution failed. Retrying once from the existing round files.",flush=True)
                    prompt += " This turn is a retry. Inspect your partial artifacts before continuing."
                    time.sleep(5)
        package(work, tag, task)
        session.publish(end, followup=True)
        print(f"Published {DEST/tag}",flush=True)
    print("Time budget reached; completed rounds are on the campaign branch.",flush=True)


def attach(ident, detached):
    if detached:
        print(f"Attach using tmux attach -t {NAME}")
    else:
        session.attach(ident, False)


def launch(args):
    session.preflight()
    existing = subprocess.run(["tmux","list-sessions","-F","#{session_id} #{session_name}"],
                              capture_output=True,text=True)
    reuse = None
    for entry in existing.stdout.splitlines():
        ident, _, name = entry.partition(" ")
        if name == NAME:
            if session.output("tmux","show-options","-qv","-t",ident,"@moead_root") != str(session.ROOT):
                raise RuntimeError("Follow-up tmux session belongs to another checkout")
            panes = session.output("tmux","list-panes","-s","-t",ident,"-F","#{window_name} #{pane_dead}")
            if "research 0" in panes.splitlines():
                attach(ident,args.detach)
                return 0
            reuse = ident
            break
    python = session.choose_python(install=True)
    end = int(time.time())+args.seconds
    cmd = [python,str(Path(__file__).resolve()),str(end)]
    if sys.platform=="darwin" and shutil.which("caffeinate"):
        cmd = ["caffeinate","-i",*cmd]
    base = session.BASE/"followup"
    base.mkdir(parents=True,exist_ok=True)
    log = shlex.quote(str(base/"supervisor.log"))
    line = f"set -o pipefail; {shlex.join(cmd)} 2>&1 | tee -a {log}"
    if reuse:
        ident = reuse
        session.tmux("new-window","-t",ident+":","-n","research","-c",str(session.ROOT),
                     "exec bash -c "+shlex.quote(line))
    else:
        ident = session.output("tmux","new-session","-dP","-F","#{session_id}","-s",NAME,"-n","research",
                               "-e","PATH="+os.environ["PATH"],"-c",str(session.ROOT),
                               "exec bash -c "+shlex.quote(line))
        session.tmux("set-option","-t",ident,"@moead_root",str(session.ROOT))
    print(f"Research deadline {session.utc(end)}. Log: {base/'supervisor.log'}",flush=True)
    attach(ident,args.detach)
    return 0


if __name__ == "__main__":
    session.BASE.mkdir(parents=True,exist_ok=True)
    with (session.BASE/"followup.lock").open("a") as lock:
        fcntl.flock(lock,fcntl.LOCK_EX | fcntl.LOCK_NB)
        supervise(int(sys.argv[1]))
