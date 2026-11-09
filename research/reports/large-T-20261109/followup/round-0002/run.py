#!/usr/bin/env python3
"""One-shot execution of the published round-1 study; never resumes or retries.

Run from the research checkout. Use reproduce.py for analysis-only replay.
The native engine and registered analysis are loaded unchanged from that checkout.
"""
import time
START = time.monotonic()

import argparse
import contextlib
import datetime as dt
import hashlib
import importlib
import json
import os
from pathlib import Path
import platform
import shlex
import shutil
import signal
import subprocess
import sys
import tempfile

for _name in ("OPENBLAS_NUM_THREADS", "OMP_NUM_THREADS", "MKL_NUM_THREADS",
              "VECLIB_MAXIMUM_THREADS", "NUMEXPR_NUM_THREADS"):
    os.environ[_name] = "1"

ROUND1 = "research/reports/large-T-20261109/followup/round-0001"
FLAGS = ["-std=c++17", "-O3"]
OUTPUT_FIELDS = {
    "sweeps", "attempts", "init_evals", "comparisons", "external_replacements",
    "external_changes", "exact_sweep", "front_sweep", "archive_sweep", "U", "S",
    "post_sweep", "bad_at_U", "max_error_at_U", "bad_at_S", "max_error_at_S",
    "first_corner_donor", "endpoint_repairs_own", "endpoint_repairs_external",
}


class Cutoff(Exception):
    pass


def utc():
    return dt.datetime.now(dt.timezone.utc).isoformat()


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def atomic(path, data):
    """Durably replace one metadata file; receipts additionally reject overwrites."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(dir=path.parent, delete=False) as handle:
        tmp = Path(handle.name)
        try:
            handle.write(data)
            handle.flush()
            os.fsync(handle.fileno())
            handle.close()
            os.replace(tmp, path)
            fd = os.open(path.parent, os.O_RDONLY)
            try:
                os.fsync(fd)
            finally:
                os.close(fd)
        finally:
            tmp.unlink(missing_ok=True)


def save(path, value):
    atomic(path, (json.dumps(value, indent=2, sort_keys=True, allow_nan=False)+"\n").encode())


def log(private, event, **fields):
    with (private / "events.jsonl").open("a") as handle:
        handle.write(json.dumps(dict(utc=utc(), event=event, **fields), allow_nan=False)+"\n")
        handle.flush()
        os.fsync(handle.fileno())


def command(argv, deadline, cwd, input_text=None):
    """One child at a time; kill its full process group on cutoff or interrupt."""
    if time.monotonic() >= deadline:
        raise Cutoff("deadline before child start")
    child = subprocess.Popen(argv, cwd=cwd, stdin=subprocess.PIPE if input_text is not None else None,
                             stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                             text=True, start_new_session=True)
    try:
        stdout, stderr = child.communicate(input=input_text,
                                          timeout=max(0, deadline-time.monotonic()))
    except BaseException as exc:
        with contextlib.suppress(ProcessLookupError):
            os.killpg(child.pid, signal.SIGKILL)
        child.communicate()
        if isinstance(exc, subprocess.TimeoutExpired):
            raise Cutoff("child exceeded remaining invocation budget") from exc
        raise
    if time.monotonic() >= deadline:
        raise Cutoff("deadline after child exit")
    if child.returncode:
        raise RuntimeError(f"{Path(argv[0]).name} exited {child.returncode}: {stderr[-2000:]}")
    return stdout


def load_registered(root):
    sys.path.insert(0, str(root / ROUND1))
    return importlib.import_module("plan"), importlib.import_module("analysis")


def registration(root, deadline):
    """Check publication in an ancestor, local bytes and every frozen artifact."""
    git = lambda *args: command(["git", *args], deadline, root).strip()
    head = git("rev-parse", "HEAD")
    commit = git("log", "-1", "--format=%H", "--", ROUND1+"/freeze.json")
    if not commit:
        raise ValueError("Round-1 freeze has not been committed")
    git("merge-base", "--is-ancestor", commit, head)
    directory = root / ROUND1
    freeze = json.loads((directory / "freeze.json").read_text())
    names = sorted(set(freeze["files"]) | {"report.md", "provenance.json", "freeze.json"})
    hashes = {}
    for name in names:
        if Path(name).name != name:
            raise ValueError("Unsafe registration filename")
        path = directory / name
        # Text encoding is lossless for these UTF-8 artifacts, including final newlines.
        committed = command(["git", "show", f"{commit}:{ROUND1}/{name}"], deadline, root)
        if committed.encode() != path.read_bytes():
            raise ValueError("Local or committed registration differs: "+name)
        hashes[name] = sha(path)
        if name in freeze["files"] and hashes[name] != freeze["files"][name]:
            raise ValueError("Registration freeze mismatch: "+name)
    return dict(commit=commit, directory=ROUND1, files=hashes, ancestor_of_head=head)


def verify_sources(root, out, sources):
    for name, expected in sources.items():
        if sha(root / name) != expected or sha(out / "source" / name) != expected:
            raise ValueError("Executed source changed: "+name)


def parse_output(text):
    def pairs(items):
        result = {}
        for key, val in items:
            if key in result:
                raise ValueError("Duplicate JSON field: "+key)
            result[key] = val
        return result
    result = json.loads(text, object_pairs_hook=pairs)
    if type(result) is not dict or set(result) != OUTPUT_FIELDS:
        raise ValueError("Unexpected or missing engine fields")
    if result["first_corner_donor"] is not None:
        raise ValueError("Uniform initialization cannot report a supplied-corner donor")
    return result


def store_receipt(out, item, result, wall, manifest, plan, analysis):
    row = dict(item, **result, wall_seconds=wall,
               model_sha256=manifest["model_sha256"], plan_sha256=manifest["plan_sha256"],
               stop_reason="post_exact" if result["post_sweep"] is not None else "sweep_cap")
    row["record_sha256"] = plan.digest(row)
    analysis.validate(row, item, manifest)
    path = out / "rows" / (item["id"]+".json")
    if path.exists():
        raise ValueError("Refusing duplicate/conflicting receipt: "+item["id"])
    save(path, row)
    return row


def measure(plan, analysis, manifest, out, private, engine, deadline, root,
            execute=command, check=lambda: None):
    """Returns a terminal status. Mocks test every failure branch without sampling."""
    started = time.monotonic()
    records = []
    state, error, active, trial_start = "complete", None, None, None
    try:
        for item in manifest["plan"]:
            if item["stage"] == "main":
                smoke = [p for p in manifest["plan"] if p["stage"] == "smoke"]
                seen = {r["id"]: r for r in records}
                if not all(p["id"] in seen and seen[p["id"]]["post_sweep"] is not None for p in smoke):
                    raise ValueError("Main without complete passing smoke")
            active = item["id"]
            trial_start = time.monotonic()
            check()
            log(private, "trial_start", id=active, stage=item["stage"])
            argv = [str(engine), *(str(item[k]) for k in
                    ("n", "T", "factor", "seed", "max_sweeps", "mutation", "noise", "init", "reference"))]
            engine_start = time.monotonic()
            stdout = execute(argv, deadline, root)
            wall = time.monotonic()-engine_start
            # Preserve even invalid output privately for an integrity investigation.
            atomic(private / "engine-output" / (active+".json"), stdout.encode())
            result = parse_output(stdout)
            check()
            row = store_receipt(out, item, result, wall, manifest, plan, analysis)
            records.append(row)
            log(private, "trial_receipt", id=active, wall_seconds=wall, record_sha256=row["record_sha256"])
            if item["stage"] == "smoke" and row["post_sweep"] is None:
                state = "smoke_blocked"
                break
            if time.monotonic() >= deadline:
                raise Cutoff("deadline after durable receipt")
            active, trial_start = None, None
    except BaseException as exc:
        state = "wall_cutoff" if isinstance(exc, Cutoff) else "interrupted" if isinstance(exc, KeyboardInterrupt) else "integrity_or_technical_failure"
        error = f"{type(exc).__name__}: {exc}"
        log(private, "trial_failure", id=active, reason=error,
            elapsed_seconds=None if trial_start is None else time.monotonic()-trial_start)
    present = {r["id"] for r in records}
    return dict(state=state, error=error, failed_or_last_id=active, recorded=len(records),
                missing_ids=[p["id"] for p in manifest["plan"] if p["id"] not in present],
                measurement_loop_seconds=time.monotonic()-started,
                stages={stage:dict(planned=sum(p["stage"] == stage for p in manifest["plan"]),
                                   recorded=sum(r["stage"] == stage for r in records),
                                   exact_observed=sum(r["stage"] == stage and r["exact_sweep"] is not None for r in records),
                                   post_observed=sum(r["stage"] == stage and r["post_sweep"] is not None for r in records))
                        for stage in ("smoke", "main")})


def claim_invocation(path, info):
    """Persistent, exclusive marker: changing the output path cannot authorize a retry."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("x") as handle:
        json.dump(info, handle, indent=2, sort_keys=True)
        handle.write("\n")
        handle.flush()
        os.fsync(handle.fileno())


def run(args):
    root, out, private = args.repo.resolve(), args.out.resolve(), args.private.resolve()
    deadline = START+1800
    if args.not_after_utc:
        ceiling = dt.datetime.fromisoformat(args.not_after_utc)
        if ceiling.tzinfo is None:
            raise ValueError("UTC ceiling requires timezone")
        deadline = min(deadline, time.monotonic()+(ceiling-dt.datetime.now(dt.timezone.utc)).total_seconds())
    reg = registration(root, deadline)  # Always before sampling or compiler execution.
    plan, analysis = load_registered(root)
    design = plan.build_plan()
    if json.loads((root / ROUND1 / "plan.json").read_text()) != design:
        raise ValueError("Published plan differs from generator")
    if sha(root / plan.ENGINE) != plan.ENGINE_SHA256:
        raise ValueError("Engine differs from registered source")
    checks = json.loads(args.checks.read_text())
    for name in ("kernel-tests", "plan", "audit", "plan-tests", "baseline-tests", "compile", "wrapper-tests"):
        if checks.get(name, {}).get("exit_code") != 0:
            raise ValueError("Missing successful pre-draw check: "+name)
    if checks["wrapper-tests"].get("wrapper_sha256") != sha(__file__):
        raise ValueError("Wrapper changed after its tests")
    if out.exists():
        raise ValueError("Output already exists: no resume or second invocation")
    out.mkdir(parents=True)
    private.mkdir(parents=True, exist_ok=True)
    started_utc = utc()
    claim_invocation(root / "research/runs" / (plan.STUDY+"-invocation.json"),
                     dict(study=plan.STUDY, started_utc=started_utc, out=str(out), registration=reg))
    log(private, "invocation_start", started_utc=started_utc, total_budget_seconds=deadline-START)
    status = None
    compile_seconds = 0.
    try:
        names = [plan.ENGINE, str(Path(__file__).resolve().relative_to(root)),
                 str(Path(__file__).resolve().with_name("test_run.py").relative_to(root)),
                 "tests/test_neighborhood_kernel.py"]
        names += [ROUND1+"/"+name for name in reg["files"]]
        sources = {name:sha(root / name) for name in sorted(set(names))}
        for name in sources:
            atomic(out / "source" / name, (root / name).read_bytes())
        verify_sources(root, out, sources)
        compiler = shlex.split(os.environ.get("CXX", "c++"))
        compiler[0] = shutil.which(compiler[0]) or compiler[0]
        version = command([*compiler, "--version"], deadline, root)
        macros = command([*compiler, *FLAGS, "-dM", "-E", "-x", "c++", "-"], deadline, root,
                         "#include <random>\n")
        selected_macros = {line.split()[1]:" ".join(line.split()[2:]) for line in macros.splitlines()
                           if line.startswith("#define ") and line.split()[1] in
                           ("_LIBCPP_VERSION", "__GLIBCXX__", "_GLIBCXX_RELEASE", "__cplusplus", "__clang_major__", "__clang_minor__")}
        engine = private / "engine"
        compile_argv = [*compiler, *FLAGS, str(out / "source" / plan.ENGINE), "-o", str(engine)]
        begin = time.monotonic()
        command(compile_argv, deadline, root)
        compile_seconds = time.monotonic()-begin
        toolchain = dict(compiler=compiler, version=version, macros=selected_macros, flags=FLAGS,
                         architecture=platform.machine(), binary_sha256=sha(engine),
                         random_engine="std::mt19937_64", distribution="standard-library binomial/Bernoulli")
        git_status = command(["git", "status", "--porcelain"], deadline, root).splitlines()
        import numpy as np
        manifest = dict(format=1, study=plan.STUDY, plan=design["plan"], plan_sha256=design["plan_sha256"],
                        registration=reg, sources=sources, toolchain=toolchain,
                        model_sha256=plan.digest([plan.STUDY, sources, toolchain]),
                        command=[sys.executable, *sys.argv], compile_command=compile_argv,
                        started_utc=started_utc, monotonic_start=START, monotonic_deadline=deadline,
                        measurement_budget_seconds=1800, effective_budget_seconds=deadline-START,
                        not_after_utc=args.not_after_utc, workers=1, pre_draw_checks=checks,
                        git=dict(commit=reg["ancestor_of_head"], dirty=bool(git_status), status=git_status),
                        runtime=dict(python=sys.version, numpy=np.__version__, platform=platform.platform(),
                                     single_thread_environment={k:os.environ[k] for k in
                                     ("OPENBLAS_NUM_THREADS", "OMP_NUM_THREADS", "MKL_NUM_THREADS", "VECLIB_MAXIMUM_THREADS", "NUMEXPR_NUM_THREADS")}),
                        conventions=dict(initialization="independent Bin(n,1/2), observed once",
                            mutation="independent bit flips, probability 1/n", noise="gate p=f/n then independent bit flips 1/n; stored/shared",
                            parent="ascending cyclic own-parent", neighborhood="exact filled cardinality; parity ties",
                            reference="moving observed extrema, including rejected proposals", selection="updated Tchebycheff; ties accepted",
                            primary="first true exact boundary X", terminal="first exact boundary P at/after stored alignment S, or H",
                            cap="administrative sweep cap; killed trials missing, never fabricated prefixes",
                            protocol=ROUND1+"/preregistration.md"))
        save(out / "manifest.json", manifest)
        def check():
            verify_sources(root, out, sources)
            if sha(engine) != toolchain["binary_sha256"]:
                raise ValueError("Engine binary changed")
        status = measure(plan, analysis, manifest, out, private, engine, deadline, root, check=check)
    except BaseException as exc:
        status = dict(state="wall_cutoff" if isinstance(exc, Cutoff) else "setup_failure",
                      error=f"{type(exc).__name__}: {exc}", recorded=0,
                      missing_ids=[r["id"] for r in design["plan"]])
        log(private, "setup_failure", reason=status["error"], elapsed_seconds=time.monotonic()-START)
    finally:
        status.update(ended_utc=utc(), invocation_seconds=time.monotonic()-START,
                      compile_seconds=compile_seconds, no_resume=True)
        save(out / "status.json", status)
        log(private, "invocation_stop", **status)
    print(json.dumps(status, indent=2))
    return 0 if status["state"] == "complete" else 2


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", type=Path, default=Path.cwd())
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--private", type=Path, required=True)
    parser.add_argument("--checks", type=Path, required=True)
    parser.add_argument("--not-after-utc")
    args = parser.parse_args()
    def interrupted(signum, frame):
        raise KeyboardInterrupt(f"signal {signum}")
    signal.signal(signal.SIGTERM, interrupted)
    raise SystemExit(run(args))
