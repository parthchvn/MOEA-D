#!/usr/bin/env python3
"""Analyze paired broadcast ON/OFF blocks without dropping missing/censored arms."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np

try:
    from scripts.run_research import atomic_json, describe, sha256
except ModuleNotFoundError:
    from run_research import atomic_json, describe, sha256

ARMS = ("on", "off")
EVENTS = ("archive", "alignment")
PHASES = ("last_endpoint_evaluations", "interior_completion_evaluations",
          "alignment_after_endpoints_evaluations")


def distribution(values):
    result = describe(values)
    result.update(std=float(np.std(values, ddof=1)) if len(values) > 1 else None,
                  q90=float(np.quantile(values, .9)) if values else None,
                  q95=float(np.quantile(values, .95)) if values else None)
    return result


def interval(point, samples, coverage=.95):
    tail = (1 - coverage) / 2
    return {"estimate": float(point), "coverage": coverage,
            "interval": np.quantile(samples, [tail, 1 - tail]).tolist()}


def validate_row(row):
    n, observation = row["n"], row["observation_evaluations"]
    if not 0 <= observation <= row["evaluations"]:
        raise ValueError("Invalid confirmed/executed observation counts")
    for event in EVENTS:
        value = row[f"{event}_evaluations"]
        if row[f"{event}_censored"] != (value is None):
            raise ValueError("Endpoint censor flag disagrees with time")
        if value is not None and not n + 1 <= value <= observation:
            raise ValueError("Event outside confirmed observation prefix")
    hits = row["target_first_hit_evaluations"]
    if len(hits) != n + 1 or any(value is not None and not n + 1 <= value <= observation for value in hits):
        raise ValueError("Invalid confirmed target first-hit times")
    h = max(hits[0], hits[n]) if hits[0] is not None and hits[n] is not None else None
    interior = (max(hits[1:n], default=n + 1) if observation >= n + 1
                and all(value is not None for value in hits[1:n]) else None)
    alignment = row["alignment_evaluations"]
    expected_alignment = max(hits) if all(value is not None for value in hits) else None
    if alignment != expected_alignment or row["last_endpoint_evaluations"] != h:
        raise ValueError("Phase times disagree with target first hits")
    if row["interior_completion_evaluations"] != interior:
        raise ValueError("Interior time disagrees with target first hits")
    residual = alignment - h if alignment is not None and h is not None else None
    if row["alignment_after_endpoints_evaluations"] != residual:
        raise ValueError("Invalid post-endpoint residual")
    if alignment is not None and (row["archive_evaluations"] is None
                                  or row["archive_evaluations"] > alignment):
        raise ValueError("Archive must complete by alignment")
    if row["arm"] == "off" and (row["self_loop_recipient_changes"]
                                 or row["self_loop_target_acquisitions"]):
        raise ValueError("OFF cannot change recipients on self-loops")


def analyze(datasets, bootstrap=20_000, seed=2611039000):
    if bootstrap < 1:
        raise ValueError("bootstrap must be positive")
    plan, records, used_seeds, run_complete = {}, {}, {}, {}
    for dataset in datasets:
        manifest, rows = dataset["manifest"], dataset["trials"]
        if manifest["mode"] != "broadcast-grid":
            raise ValueError("Only broadcast-grid data are supported")
        run_id = manifest["parameters"]["run_id"]
        if run_id in run_complete:
            raise ValueError("Duplicate input run")
        run_complete[run_id] = manifest["complete"]
        for block in manifest["planned_blocks"]:
            key = run_id, block["block_id"]
            if key in plan or block["seed"] in used_seeds:
                raise ValueError("Planned blocks and their seeds must be unique")
            expected_order = ["on", "off"] if block["repetition"] % 2 == 0 else ["off", "on"]
            if block["arm_order"] != expected_order:
                raise ValueError("Arm order is not counterbalanced within cell")
            plan[key], records[key] = block, {}
            used_seeds[block["seed"]] = key
        for row in rows:
            key = row["run_id"], row["block_id"]
            if key not in plan or key[0] != run_id or row["arm"] not in ARMS:
                raise ValueError("Unplanned run/block/arm")
            if row["arm"] in records[key]:
                raise ValueError("Duplicate block arm")
            if any(row[name] != plan[key][name] for name in ("n", "radius", "repetition", "seed")):
                raise ValueError("Row differs from predeclared block")
            if (row["arm_order"] != plan[key]["arm_order"]
                    or row["execution_position"] != plan[key]["arm_order"].index(row["arm"])):
                raise ValueError("Recorded arm execution order differs from plan")
            if row["mutation"] != "lazy" or row["weight_self_loop_probability"] != .5:
                raise ValueError("Mutation differs from frozen lazy kernel")
            if row["self_loop_neighbor_broadcast"] != (row["arm"] == "on"):
                raise ValueError("Arm label differs from intervention")
            validate_row(row)
            records[key][row["arm"]] = row

    rng = np.random.default_rng(seed)
    cells, means, draws = {}, {}, {}
    grouped = {}
    for key, block in plan.items():
        grouped.setdefault((block["n"], block["radius"]), []).append(key)
    for cell_key, keys in sorted(grouped.items()):
        n, radius = cell_key
        missing = [{"run_id": key[0], "block_id": key[1],
                    "missing_arms": [arm for arm in ARMS if arm not in records[key]]}
                   for key in keys if len(records[key]) != 2]
        cell = {"planned_blocks": len(keys), "complete_blocks": len(keys) - len(missing),
                "missing_blocks_or_arms": missing, "arms": {}, "paired_phase_differences": {}}
        means[cell_key], draws[cell_key] = {}, {}
        indices = rng.integers(len(keys), size=(bootstrap, len(keys)))
        for arm in ARMS:
            available = [records[key][arm] for key in keys if arm in records[key]]
            stats = {"trajectories": len(available), "events": {}, "phases": {},
                     "observation_evaluations": distribution([r["observation_evaluations"] for r in available])}
            for event in EVENTS:
                values = [row[f"{event}_evaluations"] for row in available
                          if not row[f"{event}_censored"]]
                entry = {"censored": len(available) - len(values),
                         "evaluations_uncensored_only": distribution(values), "mean_ci95": None}
                if not missing and len(values) == len(keys):
                    array = np.asarray([records[key][arm][f"{event}_evaluations"] for key in keys], float)
                    means[cell_key][arm, event] = array.mean()
                    draws[cell_key][arm, event] = array[indices].mean(axis=1)
                    entry["mean_ci95"] = interval(array.mean(), draws[cell_key][arm, event])
                stats["events"][event] = entry
            for phase in PHASES:
                values = [row[phase] for row in available if row[phase] is not None]
                stats["phases"][phase] = {"unobserved": len(available) - len(values),
                                          "confirmed_values_only": distribution(values)}
            for name in ("self_loop_offspring", "self_loop_recipient_changes", "self_loop_target_acquisitions"):
                stats[name] = distribution([row[name] for row in available])
            gaps = [row["alignment_evaluations"] - row["archive_evaluations"] for row in available
                    if not row["alignment_censored"]]
            stats["paired_endpoint_gap_uncensored_only"] = distribution(gaps)
            stats["paired_endpoint_gap_uncensored_only"]["zero_gap_count"] = sum(value == 0 for value in gaps)
            cell["arms"][arm] = stats
        if not missing:
            for phase in PHASES:
                if all(records[key][arm][phase] is not None for key in keys for arm in ARMS):
                    differences = np.asarray([records[key]["off"][phase] - records[key]["on"][phase] for key in keys], float)
                    cell["paired_phase_differences"][phase] = interval(
                        differences.mean(), differences[indices].mean(axis=1))
        cells[f"n={n},r={radius}"] = cell

    contrasts = {}
    for n in sorted({key[0] for key in grouped}):
        rlog = int(np.ceil(np.log2(n)))
        keys = [key for key, block in plan.items() if block["n"] == n]
        full = all(run_complete[key[0]] and len(records[key]) == 2
                   and all(not records[key][arm][f"{event}_censored"] for arm in ARMS for event in EVENTS)
                   for key in keys)
        required = [(n, 1), (n, rlog)]
        if not full or any(key not in means or len(means[key]) != 4 for key in required):
            contrasts[str(n)] = {"status": "inconclusive: planned run/block missing or censored",
                                  "primary_decision": "inconclusive"}
            continue
        result = {"status": "empirical finite-size estimates", "rlog": rlog,
                  "events": {}, "primary": {}}
        for event in EVENTS:
            a, ad = {}, {}
            for radius in (1, rlog):
                a[radius] = np.log(means[n, radius]["off", event] / means[n, radius]["on", event])
                ad[radius] = np.log(draws[n, radius]["off", event] / draws[n, radius]["on", event])
            delta, delta_draw = a[1] - a[rlog], ad[1] - ad[rlog]
            result["events"][event] = {
                "A1": interval(a[1], ad[1]), "Alog": interval(a[rlog], ad[rlog]),
                "Delta": interval(delta, delta_draw),
                "R_on": interval(means[n, 1]["on", event] / means[n, rlog]["on", event],
                                 draws[n, 1]["on", event] / draws[n, rlog]["on", event]),
                "R_off": interval(means[n, 1]["off", event] / means[n, rlog]["off", event],
                                  draws[n, 1]["off", event] / draws[n, rlog]["off", event]),
            }
            if event == "alignment":
                result["primary"] = {"A1": interval(a[1], ad[1], .975),
                                     "Delta": interval(delta, delta_draw, .975)}
        supported = all(result["primary"][name]["interval"][0] > 0 for name in ("A1", "Delta"))
        result["primary_decision"] = ("broadcast helps at r=1 and contributes to attenuation"
                                      if supported else "joint mechanism criterion not established")
        contrasts[str(n)] = result
    return {"schema_version": 1, "bootstrap_draws": bootstrap, "seed": seed,
            "method": "whole ON/OFF x archive/alignment blocks, independent radius cells",
            "primary_interval_policy": "97.5% two-sided percentile per A1/Delta; nominal Bonferroni95 within n, approximate bootstrap",
            "secondary_interval_policy": "95% pointwise, descriptive",
            "planned_blocks": len(plan), "recorded_trajectories": sum(len(value) for value in records.values()),
            "cells": cells, "contrasts": contrasts}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("runs", type=Path, nargs="+")
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--bootstrap", type=int, default=20_000)
    parser.add_argument("--seed", type=int, default=2611039000)
    args = parser.parse_args()
    datasets, sources = [], []
    for directory in args.runs:
        manifest_path, results_path = directory / "manifest.json", directory / "results.json"
        datasets.append({"manifest": json.loads(manifest_path.read_text()),
                         "trials": json.loads(results_path.read_text())["trials"]})
        sources.append({"directory": str(directory), "manifest_sha256": sha256(manifest_path),
                        "results_sha256": sha256(results_path)})
    result = analyze(datasets, args.bootstrap, args.seed)
    result["sources"] = sources
    args.output.parent.mkdir(parents=True, exist_ok=True)
    atomic_json(args.output, result)
    print(args.output)
    print(json.dumps(result["contrasts"], indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
