#!/usr/bin/env python3
"""Run bounded, reproducible MOEA/D experiment grids.

This records raw independent trials and enough metadata to reproduce a run. It is
deliberately an experiment runner, not an autonomous hypothesis generator.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import platform
import shutil
import statistics
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable

import matplotlib
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import large  # noqa: E402
import sim  # noqa: E402

SOURCE_SUFFIXES = {".md", ".py", ".toml", ".txt"}
SOURCE_EXCLUDED_PARTS = {".cache", ".git", ".venv", "__pycache__", "runs"}


def git_value(*args: str) -> str | None:
    try:
        return subprocess.check_output(
            ["git", *args], cwd=ROOT, text=True, stderr=subprocess.DEVNULL
        ).strip()
    except (OSError, subprocess.CalledProcessError):
        return None


def atomic_json(path: Path, payload: Any) -> None:
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    os.replace(temporary, path)


def experiment_sources() -> list[Path]:
    sources = []
    for path in ROOT.rglob("*"):
        if not path.is_file():
            continue
        relative = path.relative_to(ROOT)
        if any(part in SOURCE_EXCLUDED_PARTS for part in relative.parts):
            continue
        if path.suffix in SOURCE_SUFFIXES or relative == Path("requirements.txt"):
            sources.append(path)
    return sorted(sources)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for chunk in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def snapshot_sources(destination: Path) -> dict[str, str]:
    snapshot = destination / "source_snapshot"
    hashes: dict[str, str] = {}
    for source in experiment_sources():
        relative = source.relative_to(ROOT)
        target = snapshot / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, target)
        hashes[str(relative)] = sha256(source)

    try:
        patch = subprocess.check_output(
            ["git", "diff", "--binary", "--no-ext-diff", "HEAD", "--", "."],
            cwd=ROOT,
            text=True,
            stderr=subprocess.DEVNULL,
        )
    except (OSError, subprocess.CalledProcessError):
        patch = ""
    (destination / "working_tree.patch").write_text(patch)
    return hashes


def run_directory(mode: str, label: str | None) -> Path:
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    safe_label = "" if not label else "-" + "".join(
        ch if ch.isalnum() or ch in "-_" else "-" for ch in label
    ).strip("-")
    destination = ROOT / "research" / "runs" / f"{stamp}-{mode}{safe_label}"
    destination.mkdir(parents=True, exist_ok=False)
    return destination


def describe(values: list[float]) -> dict[str, float | int | None]:
    if not values:
        return {
            "count": 0,
            "mean": None,
            "median": None,
            "q25": None,
            "q75": None,
            "min": None,
            "max": None,
        }
    ordered = sorted(values)
    return {
        "count": len(ordered),
        "mean": statistics.fmean(ordered),
        "median": statistics.median(ordered),
        "q25": float(np.quantile(ordered, 0.25)),
        "q75": float(np.quantile(ordered, 0.75)),
        "min": ordered[0],
        "max": ordered[-1],
    }


def base_manifest(
    args: argparse.Namespace, destination: Path, source_hashes: dict[str, str]
) -> dict[str, Any]:
    dirty = git_value("status", "--porcelain")
    return {
        "schema_version": 2,
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "mode": args.mode,
        "command": [sys.executable, *sys.argv],
        "output_directory": str(destination.relative_to(ROOT)),
        "git_commit": git_value("rev-parse", "HEAD"),
        "git_dirty": bool(dirty) if dirty is not None else None,
        "python": sys.version,
        "numpy": np.__version__,
        "matplotlib": matplotlib.__version__,
        "platform": platform.platform(),
        "wall_time_budget_seconds": args.max_seconds,
        "seed_base": args.seed,
        "complete": False,
        "budget_exhausted": False,
        "source_sha256": source_hashes,
        "source_snapshot_directory": "source_snapshot",
        "working_tree_patch": "working_tree.patch",
        "parameters": vars(args),
    }


def summarize_large(
    args: argparse.Namespace, rows: list[dict[str, Any]]
) -> dict[str, Any]:
    summary: dict[str, Any] = {}
    for n in args.n:
        for radius in args.r:
            group = [row for row in rows if row["n"] == n and row["radius"] == radius]
            if not group:
                continue
            uncensored = [float(row["sweeps"]) for row in group if not row["censored"]]
            summary[f"n={n},r={radius}"] = {
                "trials_started": len(group),
                "censored": sum(bool(row["censored"]) for row in group),
                "sweeps_uncensored_only": describe(uncensored),
                "candidate_invariant_violations": sum(
                    int(row["invariant_violations"]) for row in group
                ),
            }
    return summary


def summarize_noise(
    args: argparse.Namespace, rows: list[dict[str, Any]]
) -> dict[str, Any]:
    summary: dict[str, Any] = {}
    for n in args.n:
        for neighborhood_size in args.T:
            group = [row for row in rows if row["n"] == n and row["T"] == neighborhood_size]
            if not group:
                continue
            converged = [float(row["evaluations"]) for row in group if row["converged"]]
            summary[f"n={n},T={neighborhood_size}"] = {
                "trials_started": len(group),
                "converged": sum(bool(row["converged"]) for row in group),
                "evaluations_converged_only": describe(converged),
            }
    return summary


def large_grid(
    args: argparse.Namespace,
    deadline: float,
    checkpoint: Callable[[list[dict[str, Any]], dict[str, Any]], None],
) -> tuple[list[dict[str, Any]], dict[str, Any], bool]:
    rows: list[dict[str, Any]] = []
    budget_exhausted = False
    trial_index = 0
    configurations = []
    for n in args.n:
        if n < 1:
            raise ValueError("n must be positive")
        for radius in args.r:
            if radius < 0 or radius > n:
                raise ValueError(f"radius r={radius} must be in [0, n={n}]")
            intervals = large.neighbourhoods(n, radius)
            sizes = [end - begin for begin, end in intervals]
            configurations.append((n, radius, min(sizes), max(sizes)))

    for repetition in range(args.reps):
        for n, radius, minimum_size, maximum_size in configurations:
            if time.monotonic() >= deadline:
                budget_exhausted = True
                break
            seed = args.seed + trial_index
            trial_index += 1
            trial_started = time.monotonic()
            per_trial_deadline = trial_started + args.max_trial_seconds
            trial_deadline = min(deadline, per_trial_deadline)
            deadline_scope = (
                "total" if deadline <= per_trial_deadline else "trial"
            )
            result = large.run(
                n=n,
                r=radius,
                seed=seed,
                track=args.track,
                max_sweeps=args.max_sweeps,
                deadline=trial_deadline,
            )
            rows.append(
                {
                    "n": n,
                    "radius": radius,
                    "nominal_unclipped_interior_size": 2 * radius + 1,
                    "nominal_interior_size": min(n + 1, 2 * radius + 1),
                    "minimum_actual_size": minimum_size,
                    "maximum_actual_size": maximum_size,
                    "repetition": repetition,
                    "seed": seed,
                    "sweeps": result["sweeps"],
                    "censored": result["censored"],
                    "censor_reason": result["censor_reason"],
                    "deadline_scope": (
                        deadline_scope
                        if result["censor_reason"] == "wall_time"
                        else None
                    ),
                    "max_trial_seconds": args.max_trial_seconds,
                    "candidate_invariant_checks": result["J_checks"],
                    "invariant_checks": result["J_checks"],
                    "invariant_violations": result["J_viol"],
                    "elapsed_seconds": time.monotonic() - trial_started,
                }
            )
            checkpoint(rows, summarize_large(args, rows))
            if (result["censor_reason"] == "wall_time"
                    and deadline_scope == "total"):
                budget_exhausted = True
                break
        if budget_exhausted:
            break
    return rows, summarize_large(args, rows), budget_exhausted


def noise_grid(
    args: argparse.Namespace,
    deadline: float,
    checkpoint: Callable[[list[dict[str, Any]], dict[str, Any]], None],
) -> tuple[list[dict[str, Any]], dict[str, Any], bool]:
    rows: list[dict[str, Any]] = []
    budget_exhausted = False
    trial_index = 0
    configurations = []
    for n in args.n:
        if n < 1:
            raise ValueError("n must be positive")
        probability = args.p_factor / n
        for neighborhood_size in args.T:
            if not 1 <= neighborhood_size <= n + 1:
                raise ValueError(f"T={neighborhood_size} must be in [1, n+1={n+1}]")
            configurations.append((n, neighborhood_size, probability))

    for repetition in range(args.trials):
        for n, neighborhood_size, probability in configurations:
            if time.monotonic() >= deadline:
                budget_exhausted = True
                break
            seed = args.seed + trial_index
            trial_index += 1
            rng = np.random.default_rng(seed)
            trial_started = time.monotonic()
            per_trial_deadline = trial_started + args.max_trial_seconds
            trial_deadline = min(deadline, per_trial_deadline)
            deadline_scope = (
                "total" if deadline <= per_trial_deadline else "trial"
            )
            result = sim.simulate_moead(
                n=n,
                p=probability,
                T=neighborhood_size,
                stop_rule=args.stop_rule,
                max_gens=args.max_gens,
                rng=rng,
                deadline=trial_deadline,
            )
            rows.append(
                {
                    "n": n,
                    "T": neighborhood_size,
                    "p": probability,
                    "p_factor": args.p_factor,
                    "stop_rule": args.stop_rule,
                    "repetition": repetition,
                    "seed": seed,
                    "generations": result["total_gens"],
                    "evaluations": result["total_evals"],
                    "converged": result["converged"],
                    "censor_reason": result["censor_reason"],
                    "deadline_scope": (
                        deadline_scope
                        if result["censor_reason"] == "wall_time"
                        else None
                    ),
                    "max_trial_seconds": args.max_trial_seconds,
                    "elapsed_seconds": time.monotonic() - trial_started,
                }
            )
            checkpoint(rows, summarize_noise(args, rows))
            if (result["censor_reason"] == "wall_time"
                    and deadline_scope == "total"):
                budget_exhausted = True
                break
        if budget_exhausted:
            break
    return rows, summarize_noise(args, rows), budget_exhausted


def parser() -> argparse.ArgumentParser:
    common = argparse.ArgumentParser(add_help=False)
    common.add_argument("--seed", type=int, default=20261102)
    common.add_argument("--max-seconds", type=float, default=5 * 60 * 60)
    common.add_argument("--max-trial-seconds", type=float, default=10 * 60)
    common.add_argument("--label")

    root = argparse.ArgumentParser(description=__doc__)
    subparsers = root.add_subparsers(dest="mode", required=True)

    noiseless = subparsers.add_parser("large-grid", parents=[common])
    noiseless.add_argument("--n", type=int, nargs="+", required=True)
    noiseless.add_argument("--r", type=int, nargs="+", required=True)
    noiseless.add_argument("--reps", type=int, default=10)
    noiseless.add_argument("--max-sweeps", type=int, default=None)
    noiseless.add_argument("--track", action="store_true")

    noisy = subparsers.add_parser("noise-grid", parents=[common])
    noisy.add_argument("--n", type=int, nargs="+", required=True)
    noisy.add_argument("--T", type=int, nargs="+", required=True)
    noisy.add_argument("--p-factor", type=float, required=True)
    noisy.add_argument("--trials", type=int, default=20)
    noisy.add_argument("--stop-rule", choices=("front", "aligned"), default="aligned")
    noisy.add_argument("--max-gens", type=int, default=None)
    return root


def main() -> int:
    args = parser().parse_args()
    if args.max_seconds <= 0:
        raise ValueError("--max-seconds must be positive")
    if args.max_trial_seconds <= 0:
        raise ValueError("--max-trial-seconds must be positive")
    destination = run_directory(args.mode, args.label)
    started = time.monotonic()
    deadline = started + args.max_seconds
    source_hashes = snapshot_sources(destination)
    manifest = base_manifest(args, destination, source_hashes)
    atomic_json(destination / "manifest.json", manifest)

    def checkpoint(rows: list[dict[str, Any]], summary: dict[str, Any]) -> None:
        atomic_json(
            destination / "results.json",
            {"schema_version": 2, "trials": rows, "summary": summary},
        )
        manifest["updated_at_utc"] = datetime.now(timezone.utc).isoformat()
        manifest["elapsed_seconds"] = time.monotonic() - started
        manifest["trials_recorded"] = len(rows)
        atomic_json(destination / "manifest.json", manifest)

    checkpoint([], {})
    try:
        if args.mode == "large-grid":
            rows, summary, budget_exhausted = large_grid(args, deadline, checkpoint)
            requested_trials = len(args.n) * len(args.r) * args.reps
        else:
            rows, summary, budget_exhausted = noise_grid(args, deadline, checkpoint)
            requested_trials = len(args.n) * len(args.T) * args.trials
        checkpoint(rows, summary)
        manifest["complete"] = not budget_exhausted and len(rows) == requested_trials
        manifest["budget_exhausted"] = budget_exhausted
        manifest["requested_trials"] = requested_trials
        manifest["elapsed_seconds"] = time.monotonic() - started
        manifest["trials_recorded"] = len(rows)
        manifest["finished_at_utc"] = datetime.now(timezone.utc).isoformat()
        atomic_json(destination / "manifest.json", manifest)
        print(destination.relative_to(ROOT))
        print(json.dumps(summary, indent=2, sort_keys=True))
        return 0
    except BaseException as error:
        manifest["elapsed_seconds"] = time.monotonic() - started
        manifest["error"] = f"{type(error).__name__}: {error}"
        manifest["interrupted"] = isinstance(error, KeyboardInterrupt)
        atomic_json(destination / "manifest.json", manifest)
        raise


if __name__ == "__main__":
    raise SystemExit(main())
