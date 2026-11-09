#!/usr/bin/env python3
"""Run the registered own-parent neighborhood experiment, one deterministic trial at a time."""
import argparse
import contextlib
import datetime as dt
import fcntl
import hashlib
import json
import math
import os
from pathlib import Path
import platform
import shutil
import signal
import subprocess
import sys
import tempfile
import time


ROOT = Path(__file__).resolve().parents[1]
ENGINE = "scripts/neighborhood_sweep.cpp"
RUNNER = "scripts/neighborhood_campaign.py"
PROTOCOL = "research/LARGER_NEIGHBORHOODS_PREREG.md"
SOURCES = (ENGINE, RUNNER, PROTOCOL)
VERSION = "own-parent-cardinality-v1"
STAGES = ("smoke", "calibrate", "main", "holdout")
FLAGS = ["-std=c++17", "-O3"]
EVENTS = ("exact_sweep", "front_sweep", "archive_sweep", "U", "S", "post_sweep")


def digest(value):
    data = json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False)
    return hashlib.sha256(data.encode("utf-8")).hexdigest()


def file_hash(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def utc():
    return dt.datetime.now(dt.timezone.utc).isoformat()


def atomic_bytes(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile("wb", dir=path.parent, suffix=".tmp", delete=False) as f:
        temp = Path(f.name)
        try:
            f.write(data)
            f.flush()
            os.fsync(f.fileno())
            f.close()
            os.replace(temp, path)
        finally:
            temp.unlink(missing_ok=True)


def atomic_json(path, obj):
    atomic_bytes(path, (json.dumps(obj, indent=2, allow_nan=False) + "\n").encode())


def log_event(stage_dir, event, **fields):
    with (stage_dir / "events.jsonl").open("a", encoding="utf-8") as f:
        f.write(json.dumps(dict(utc=utc(), event=event, **fields), allow_nan=False) + "\n")
        f.flush()
        os.fsync(f.fileno())


def make_plan(stage):
    """Hashes provide independent seed namespaces and a fixed balanced execution order."""
    if stage not in STAGES:
        raise ValueError(f"unknown stage {stage}")
    rows = []

    def cell(n, size, factor, reps, cap, cohort, mutation="bit", noise="bit",
             init="uniform", reference="observed"):
        for rep in range(reps):
            row = dict(n=n, T=size, factor=factor, max_sweeps=cap, mutation=mutation,
                       noise=noise, init=init, reference=reference, rep=rep, cohort=cohort)
            token = digest([VERSION, stage, row])
            seed = int(digest(["trial-seed", token])[:16], 16)
            rows.append(dict(id=token[:20], seed=seed, **row))

    if stage == "calibrate":
        for n in (128, 256, 512):
            for size in (1, n + 1):
                cell(n, size, 1 / 64, 1, 32, "calibration")
        for n in (8, 16):
            for size in (1, 2, 3, n + 1):
                cap = math.ceil(12 * n * n * math.log(n + 1))
                cell(n, size, 0, 12, cap, "corner", init="corner", reference="ideal")
    else:
        sizes = {"smoke": (8, 16), "main": (64, 128, 256), "holdout": (512,)}[stage]
        reps = {"smoke": 2, "main": 24, "holdout": 16}[stage]
        for n in sizes:
            cap = math.ceil((96 if stage == "smoke" else 12) * n * math.log(n + 1))
            cardinalities = {1, 3, math.ceil(math.sqrt(n)), math.ceil(n / 4), n + 1}
            if stage == "smoke":
                cardinalities.add(2)
            for size in sorted(cardinalities):
                for factor in (0, 1 / 64, 1):
                    cell(n, size, factor, reps, cap, "smoke" if stage == "smoke" else "primary")
            if stage == "smoke":
                for size in (1, 3):
                    cell(n, size, 1 / 64, reps, cap, "smoke", mutation="one", noise="one")

    rows.sort(key=lambda row: (row["rep"], digest(["order", row["id"]])))
    if len(set(row["seed"] for row in rows)) != len(rows):
        raise ValueError("seed collision in frozen plan")
    if len(set(row["id"] for row in rows)) != len(rows):
        raise ValueError("id collision in frozen plan")
    return rows


class BudgetExpired(Exception):
    pass


def command(argv, deadline, *, cwd=ROOT):
    """On cutoff/interrupt kill the complete child process group, including compiler children."""
    remaining = deadline - time.monotonic()
    if remaining <= 0:
        raise BudgetExpired
    proc = subprocess.Popen(argv, cwd=cwd, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                            text=True, start_new_session=True)
    try:
        stdout, stderr = proc.communicate(timeout=max(0, deadline - time.monotonic()))
    except BaseException as exc:
        with contextlib.suppress(ProcessLookupError):
            os.killpg(proc.pid, signal.SIGKILL)
        proc.communicate()
        if isinstance(exc, subprocess.TimeoutExpired):
            raise BudgetExpired from exc
        raise
    if time.monotonic() > deadline:
        raise BudgetExpired
    if proc.returncode:
        raise RuntimeError(f"{Path(argv[0]).name} exited {proc.returncode}: {stderr[-1500:]}")
    return stdout


def git_metadata(deadline):
    if not shutil.which("git"):
        return {"commit": None, "dirty": None}
    try:
        head = command(["git", "rev-parse", "HEAD"], deadline).strip()
        dirty = bool(command(["git", "status", "--porcelain"], deadline).strip())
    except RuntimeError:
        return {"commit": None, "dirty": None}
    return {"commit": head, "dirty": dirty}


def check_integer(row, key, low=0, high=None, nullable=False):
    x = row.get(key)
    if x is None and nullable and key in row:
        return
    if type(x) is not int or x < low or (high is not None and x > high):
        raise ValueError(f"{row.get('id', 'trial')}: invalid {key}={x}")


def validate_outcome(row):
    n, size, cap = row["n"], row["T"], row["max_sweeps"]
    check_integer(row, "sweeps", high=cap)
    t = row["sweeps"]
    for key in EVENTS:
        check_integer(row, key, high=t, nullable=True)
    for key in ("attempts", "init_evals", "comparisons", "external_replacements"):
        check_integer(row, key)
    if row["attempts"] != t * (n + 1) or row["comparisons"] != row["attempts"] * size:
        raise ValueError("engine sweep or comparison accounting mismatch")
    if row["init_evals"] != (0 if row["init"] == "corner" else n + 1):
        raise ValueError("initial evaluation cost mismatch")
    if row["external_replacements"] > row["attempts"] * (size - 1):
        raise ValueError("external replacement count exceeds eligible recipients")
    for early, late in (("archive_sweep", "front_sweep"), ("front_sweep", "exact_sweep"),
                        ("U", "S"), ("S", "post_sweep"), ("exact_sweep", "post_sweep")):
        if row[late] is not None and (row[early] is None or row[early] > row[late]):
            raise ValueError(f"first-hit ordering violated: {early}, {late}")
    for key, event, bound in (("bad_at_U", "U", n + 1), ("bad_at_S", "S", n + 1),
                              ("max_error_at_S", "S", n)):
        check_integer(row, key, high=bound, nullable=True)
        if (row[key] is None) != (row[event] is None):
            raise ValueError(f"{key} must be observed exactly when {event} is observed")
    if row["post_sweep"] is None:
        if t != cap:
            raise ValueError("partial engine output has no confirmed stop")
    elif row["post_sweep"] != t:
        raise ValueError("engine continued beyond first post-S exact boundary")


def validate_row(row, planned, manifest):
    if row.get("record_sha256") != digest({k: v for k, v in row.items() if k != "record_sha256"}):
        raise ValueError(f"receipt digest mismatch: {planned['id']}")
    if any(row.get(k) != v for k, v in planned.items()):
        raise ValueError(f"receipt parameters mismatch: {planned['id']}")
    if any(row.get(k) != manifest[k] for k in ("model_sha256", "plan_sha256")):
        raise ValueError(f"receipt belongs to different plan/model: {planned['id']}")
    validate_outcome(row)
    seconds = row["wall_seconds"]
    if type(seconds) not in (int, float) or not math.isfinite(seconds) or seconds < 0:
        raise ValueError("invalid elapsed time")
    if row["stop_reason"] != ("post_exact" if row["post_sweep"] is not None else "sweep_cap"):
        raise ValueError("receipt stop reason mismatch")


def read_json(path):
    with path.open(encoding="utf-8") as f:
        return json.load(f)


def verify_manifest(path, stage, plan, model_signature):
    manifest = read_json(path)
    if (manifest.get("stage") != stage or manifest.get("model_version") != VERSION or
            manifest.get("plan") != plan or manifest.get("plan_sha256") != digest(plan)):
        raise ValueError(f"frozen plan mismatch: {stage}")
    if manifest.get("model_sha256") != model_signature:
        raise ValueError(f"model, compiler or protocol changed for {stage}; use a new run directory")
    if digest([VERSION, manifest["sources"], manifest["toolchain"]]) != model_signature:
        raise ValueError(f"manifest provenance mismatch: {stage}")
    for filename, expected in manifest["sources"].items():
        if file_hash(path.parent / "source" / filename) != expected:
            raise ValueError(f"archived source changed: {filename}")
    return manifest


def read_rows(stage_dir, manifest, deadline):
    by_id = {r["id"]: r for r in manifest["plan"]}
    rows = {}
    for path in (stage_dir / "rows").glob("*.json"):
        if time.monotonic() >= deadline:
            raise BudgetExpired
        if path.stem not in by_id:
            raise ValueError(f"unexpected receipt {path.name}")
        row = read_json(path)
        validate_row(row, by_id[path.stem], manifest)
        rows[path.stem] = row
    return rows


def gate(base, stage, model_signature, deadline):
    """Sequential validation independently checks every prerequisite's immutable receipts."""
    for previous in STAGES[:STAGES.index(stage)]:
        directory = base / previous
        path = directory / "manifest.json"
        if not path.exists():
            return f"prerequisite {previous} has not run"
        manifest = verify_manifest(path, previous, make_plan(previous), model_signature)
        rows = read_rows(directory, manifest, deadline)
        if len(rows) != len(manifest["plan"]):
            return f"prerequisite {previous} has missing receipts"
        if previous == "smoke" and any(r["post_sweep"] is None for r in rows.values()):
            return "uniform smoke contains sweep-censored trials; scaling blocked"
        if previous == "main" and any(r["exact_sweep"] is None for r in rows.values()):
            return "main contains sweep-censored primary exact hits; holdout blocked"
    return None


def runtime_details(deadline):
    info = {"logical_cpus": os.cpu_count(), "system_release": platform.release()}
    if platform.system() == "Darwin" and shutil.which("sysctl"):
        try:
            info["cpu_model"] = command(["sysctl", "-n", "machdep.cpu.brand_string"], deadline).strip()
        except RuntimeError:
            pass
    elif Path("/proc/cpuinfo").is_file():
        for line in Path("/proc/cpuinfo").read_text().splitlines():
            if line.startswith("model name") and ":" in line:
                info["cpu_model"] = line.split(":", 1)[1].strip()
                break
    return info


def standard_library(compiler, deadline):
    # Binomial draws may differ across libstdc++ and libc++.
    macros = command([compiler, "-std=c++17", "-dM", "-E", "-x", "c++", "-include",
                      "random", os.devnull], deadline)
    wanted = {"__GLIBCXX__", "_GLIBCXX_RELEASE", "_LIBCPP_VERSION", "_MSVC_STL_VERSION"}
    result = {}
    for line in macros.splitlines():
        parts = line.split(maxsplit=2)
        if len(parts) == 3 and parts[0] == "#define" and parts[1] in wanted:
            result[parts[1]] = parts[2]
    if not result:
        raise ValueError("cannot identify the C++ standard library for a reproducible replay")
    return result


def make_manifest(directory, stage, plan, sources, toolchain, signature, deadline):
    path = directory / "manifest.json"
    if path.exists():
        return verify_manifest(path, stage, plan, signature)
    if any((directory / "rows").glob("*.json")):
        raise ValueError("missing manifest alongside existing receipts")
    for name, expected in sources.items():
        data = (ROOT / name).read_bytes()
        if hashlib.sha256(data).hexdigest() != expected:
            raise ValueError(f"source changed during freeze: {name}")
        atomic_bytes(directory / "source" / name, data)
    manifest = {"format": 1, "campaign": "large-T-20261109", "stage": stage, "model_version": VERSION, "created_utc": utc(),
                "model_sha256": signature, "plan_sha256": digest(plan), "plan": plan,
                "sources": sources, "toolchain": toolchain, "git": git_metadata(deadline),
                "runtime": runtime_details(deadline),
                "model": "ascending own-parent, cardinality filled at edges, one observed "
                         "offspring per attempt, moving reference includes rejected observations, "
                         "ungated non-worsening Tchebycheff broadcast; first boundary events"}
    atomic_json(path, manifest)
    return manifest


def summarize(directory, stage, plan, rows, state, reason):
    status = {"stage": stage, "state": state, "reason": reason, "planned": len(plan),
              "recorded": len(rows), "post_exact": sum(r["post_sweep"] is not None for r in rows.values()),
              "sweep_cap": sum(r["post_sweep"] is None for r in rows.values()),
              "exact_observed": sum(r["exact_sweep"] is not None for r in rows.values()),
              "updated_utc": utc()}
    atomic_json(directory / "status.json", status)
    return status


def execute(base, stage, seconds):
    invocation_start = time.monotonic()
    deadline = invocation_start + seconds
    directory = base / stage
    directory.mkdir(parents=True, exist_ok=True)
    compiler_option = os.environ.get("CXX", "c++")
    compiler = shutil.which(compiler_option)
    if not compiler:
        raise ValueError("CXX must name an available C++17 compiler executable")
    version = command([compiler, "--version"], deadline).splitlines()[0]
    toolchain = {"compiler": Path(compiler_option).name, "version": version, "flags": FLAGS,
                 "system": platform.system(), "machine": platform.machine(),
                 "python": platform.python_version(), "stdlib": standard_library(compiler, deadline)}
    sources = {name: file_hash(ROOT / name) for name in SOURCES}
    signature = digest([VERSION, sources, toolchain])
    plan = make_plan(stage)
    manifest = make_manifest(directory, stage, plan, sources, toolchain, signature, deadline)
    rows = read_rows(directory, manifest, deadline)
    log_event(directory, "start", seconds=seconds)
    item = None
    started = None
    try:
        reason = gate(base, stage, signature, deadline)
        if reason:
            summarize(directory, stage, plan, rows, "gate_blocked", reason)
            print(reason, file=sys.stderr)
            return 2
        if len(rows) < len(plan):
            summarize(directory, stage, plan, rows, "running", None)
            with tempfile.TemporaryDirectory(prefix="neighborhood-engine-") as temp:
                binary = str(Path(temp) / "engine")
                command([compiler, *FLAGS, str(directory / "source" / ENGINE), "-o", binary], deadline)
                for candidate in plan:
                    if candidate["id"] in rows:
                        continue
                    item = candidate
                    started = time.monotonic()
                    args = [str(item[k]) for k in ("n", "T", "factor", "seed", "max_sweeps",
                                                   "mutation", "noise", "init", "reference")]
                    result = json.loads(command([binary, *args], deadline))
                    if not isinstance(result, dict) or any(
                            k in item and item[k] != v for k, v in result.items()):
                        raise ValueError("engine returned conflicting plan parameters")
                    row = dict(result, **item)
                    row.update(wall_seconds=time.monotonic() - started, model_sha256=signature,
                               plan_sha256=manifest["plan_sha256"])
                    row["stop_reason"] = "post_exact" if row.get("post_sweep") is not None else "sweep_cap"
                    row["record_sha256"] = digest(row)
                    validate_row(row, item, manifest)
                    atomic_json(directory / "rows" / (item["id"] + ".json"), row)
                    rows[item["id"]] = row
                    summarize(directory, stage, plan, rows, "running", None)
                    item = None
        status = summarize(directory, stage, plan, rows, "complete", None)
        log_event(directory, "complete", recorded=len(rows))
        print(json.dumps(status, sort_keys=True))
        return 0
    except (BudgetExpired, KeyboardInterrupt) as exc:
        reason = "interrupt" if isinstance(exc, KeyboardInterrupt) else "wall_budget"
        trial_id = item["id"] if item else None
        log_event(directory, reason, unconfirmed_trial=trial_id,
                  elapsed_seconds=time.monotonic() - invocation_start,
                  trial_seconds=(time.monotonic() - started) if trial_id and started is not None else None)
        summarize(directory, stage, plan, rows, "incomplete", reason)
        print(f"{stage}: {reason}; {len(rows)}/{len(plan)} immutable receipts", file=sys.stderr)
        return 2
    except (OSError, ValueError, RuntimeError) as exc:
        log_event(directory, "failed", trial_id=item["id"] if item else None)
        summarize(directory, stage, plan, rows, "failed", type(exc).__name__)
        raise


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--stage", required=True, choices=STAGES)
    parser.add_argument("--out", required=True, type=Path, help="campaign base containing stage directories")
    parser.add_argument("--seconds", required=True, type=float, help="wall budget for this invocation")
    args = parser.parse_args()
    if not math.isfinite(args.seconds) or args.seconds <= 0:
        parser.error("--seconds must be positive and finite")
    base = args.out.resolve()
    base.mkdir(parents=True, exist_ok=True)

    def terminate(signum, frame):
        raise KeyboardInterrupt
    signal.signal(signal.SIGTERM, terminate)
    with (base / "campaign.lock").open("a") as lock:
        try:
            fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            print("another campaign process owns this run directory", file=sys.stderr)
            return 1
        try:
            return execute(base, args.stage, args.seconds)
        except (BudgetExpired, KeyboardInterrupt):
            print("interrupted before any new trial was confirmed", file=sys.stderr)
            return 2
        except (ValueError, RuntimeError, OSError) as exc:
            print(f"campaign stopped: {exc}", file=sys.stderr)
            return 1


if __name__ == "__main__":
    raise SystemExit(main())
