#!/usr/bin/env python3
"""Recompute preregistered finite-size contrasts from raw paired trajectories."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np

try:
    from scripts.run_research import atomic_json, describe, sha256
except ModuleNotFoundError:
    from run_research import atomic_json, describe, sha256


EVENTS = ("archive", "alignment")


def interval(point, samples):
    return {"estimate": float(point),
            "ci95": np.quantile(samples, [0.025, 0.975]).tolist()}


def analyze(rows, bootstrap=10_000, seed=2611029000):
    if bootstrap < 1:
        raise ValueError("bootstrap must be positive")
    seeds = [row["seed"] for row in rows]
    if len(set(seeds)) != len(seeds):
        raise ValueError("Duplicate trajectory seeds: endpoints must not be counted as separate trials")
    rng = np.random.default_rng(seed)
    groups = {}
    for row in rows:
        key = row["n"], row["radius"], row["mutation"]
        groups.setdefault(key, []).append(row)
        for event in EVENTS:
            observed = row[f"{event}_evaluations"]
            if row[f"{event}_censored"] != (observed is None):
                raise ValueError("Endpoint censoring flag disagrees with recorded time")
            if observed is not None and not row["n"] + 1 <= observed <= row["observation_evaluations"]:
                raise ValueError("Endpoint time lies outside observation interval")
        if row["alignment_evaluations"] is not None:
            if row["archive_evaluations"] is None or row["archive_evaluations"] > row["alignment_evaluations"]:
                raise ValueError("Archive must complete by alignment")
    cells, means, samples = {}, {}, {}
    for key, group in sorted(groups.items()):
        indices = rng.integers(len(group), size=(bootstrap, len(group)))
        cell = {"trajectories": len(group), "events": {},
                "observation_evaluations": describe([row["observation_evaluations"] for row in group]),
                "executed_evaluations": describe([row["evaluations"] for row in group]),
                "elapsed_seconds": sum(row.get("elapsed_seconds", 0) for row in group)}
        means[key] = {}
        samples[key] = {}
        for event in EVENTS:
            censored = sum(row[f"{event}_censored"] for row in group)
            values = [row[f"{event}_evaluations"] for row in group
                      if not row[f"{event}_censored"]]
            stats = describe(values)
            stats.update({"std": float(np.std(values, ddof=1)) if len(values) > 1 else None,
                          "q90": float(np.quantile(values, 0.9)) if values else None,
                          "q95": float(np.quantile(values, 0.95)) if values else None})
            cell["events"][event] = {"censored": censored, "evaluations_uncensored_only": stats,
                                       "mean_ci95": None}
            if not censored:
                array = np.asarray(values, dtype=float)
                means[key][event] = float(array.mean())
                samples[key][event] = array[indices].mean(axis=1)
                cell["events"][event]["mean_ci95"] = np.quantile(samples[key][event], [0.025, 0.975]).tolist()
        complete_pairs = [row for row in group if not row["alignment_censored"]]
        gaps = [row["alignment_evaluations"] - row["archive_evaluations"] for row in complete_pairs]
        cell["paired_gap_uncensored_only"] = describe(gaps)
        cell["paired_gap_uncensored_only"]["zero_gap_count"] = sum(gap == 0 for gap in gaps)
        if len(complete_pairs) == len(group):
            gaps_array = np.asarray(gaps, dtype=float)
            cell["paired_gap_mean_ci95"] = np.quantile(gaps_array[indices].mean(axis=1), [0.025, 0.975]).tolist()
        for name in ("self_loop_offspring", "self_loop_recipient_changes", "self_loop_target_acquisitions",
                     "rejected_offspring", "rejected_new_archive_weights"):
            cell[name] = describe([row.get(name, 0) for row in group])
        cells[f"n={key[0]},r={key[1]},mutation={key[2]}"] = cell

    contrasts = {}
    for n in sorted({key[0] for key in groups}):
        rlog = int(np.ceil(np.log2(n)))
        required = [(n, r, m) for r in (1, rlog) for m in ("exact", "lazy")]
        if any(key not in means or len(means[key]) != 2 for key in required):
            contrasts[str(n)] = {"status": "inconclusive: missing or censored requisite endpoint"}
            continue
        d, ds = {}, {}
        out = {"status": "empirically supported finite-size estimates", "radius_log": rlog,
               "R": {}, "D": {}, "contrasts": {}}
        for mutation in ("exact", "lazy"):
            for event in EVENTS:
                name = f"{mutation}_{event}"
                ratio = means[n, 1, mutation][event] / means[n, rlog, mutation][event]
                ratio_samples = samples[n, 1, mutation][event] / samples[n, rlog, mutation][event]
                d[name], ds[name] = np.log(ratio), np.log(ratio_samples)
                out["R"][name] = interval(ratio, ratio_samples)
                out["D"][name] = interval(d[name], ds[name])

        def calculate(values):
            ma = values["exact_archive"] - values["lazy_archive"]
            ml = values["exact_alignment"] - values["lazy_alignment"]
            se = values["exact_alignment"] - values["exact_archive"]
            sl = values["lazy_alignment"] - values["lazy_archive"]
            m, s = (ma + ml) / 2, (se + sl) / 2
            return {"M_archive": ma, "M_alignment": ml, "S_exact": se, "S_lazy": sl,
                    "interaction": ml - ma, "M_average": m, "S_average": s,
                    "mutation_dominance": m - np.abs(s), "stopping_dominance": s - np.abs(m)}

        points, boot = calculate(d), calculate(ds)
        for name in points:
            out["contrasts"][name] = interval(points[name], boot[name])
        positive = lambda name: out["contrasts"][name]["ci95"][0] > 0
        if all(positive(name) for name in ("M_archive", "M_alignment", "mutation_dominance")):
            out["decision"] = "same-weight mechanism favored"
        elif all(positive(name) for name in ("S_exact", "S_lazy", "stopping_dominance")):
            out["decision"] = "stopping mechanism favored"
        elif any(positive(name) for name in ("M_archive", "M_alignment")) and any(positive(name) for name in ("S_exact", "S_lazy")):
            out["decision"] = "both contribute; dominance unresolved"
        else:
            out["decision"] = "ambiguous under preregistered decision rule"
        contrasts[str(n)] = out
    return {"schema_version": 1, "method": "independent cell bootstrap; paired endpoints resampled together",
            "bootstrap_draws": bootstrap, "analysis_seed": seed,
            "interval_scope": "pointwise percentile 95%, not simultaneous",
            "trajectory_count": len(rows), "cells": cells, "contrasts": contrasts}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("runs", type=Path, nargs="+")
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--bootstrap", type=int, default=10_000)
    parser.add_argument("--seed", type=int, default=2611029000)
    args = parser.parse_args()
    rows, sources = [], []
    for directory in args.runs:
        result_path = directory / "results.json"
        manifest_path = directory / "manifest.json"
        result = json.loads(result_path.read_text())
        manifest = json.loads(manifest_path.read_text())
        if manifest["mode"] != "factorial-grid":
            raise ValueError("Only factorial-grid trajectories are supported")
        rows.extend(result["trials"])
        sources.append({"directory": str(directory), "results_sha256": sha256(result_path),
                        "manifest_sha256": sha256(manifest_path), "complete": manifest["complete"]})
    output = analyze(rows, args.bootstrap, args.seed)
    output["sources"] = sources
    args.output.parent.mkdir(parents=True, exist_ok=True)
    atomic_json(args.output, output)
    print(args.output)
    print(json.dumps(output["contrasts"], indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
