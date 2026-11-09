#!/usr/bin/env python3
"""Recheck only published evidence and prospective seed separation; no sampling."""
import argparse
import csv
import io
import json
import subprocess
import sys
import tarfile
from pathlib import Path

import numpy as np
from plan import BASE_COMMIT, ENGINE, ENGINE_SHA256, build_plan, digest, file_hash, repo_root


def seeds_in(value):
    result = set()
    if isinstance(value, dict):
        for key, val in value.items():
            if key == "seed" and type(val) is int:
                result.add(val)
            else:
                result.update(seeds_in(val))
    elif isinstance(value, list):
        for val in value:
            result.update(seeds_in(val))
    return result


def audit():
    root = repo_root()
    sys.path.insert(0, str(root / "scripts"))
    import package_neighborhood_evidence as packet
    existing, stages, packets = set(), {}, {}
    for name in ("pilot", "campaign"):
        directory = root / "research/evidence/large-T-20261109" / name
        packets[name] = file_hash(directory / "INDEX.json")
        for stage, files in packet.read_packet(directory):
            manifest = json.loads(files["manifest.json"])
            existing.update(seeds_in(manifest["plan"]))
            rows = {Path(k).stem: json.loads(v) for k, v in files.items() if k.startswith("rows/")}
            for source, expected in manifest["sources"].items():
                assert file_hash(root / source) == expected, (name, stage, source)
            if name == "campaign":
                stages[stage] = (manifest, rows, json.loads(files["status.json"]))
    cardinality_seeds = len(existing)
    legacy_index = json.loads((root / "research/evidence/INDEX.json").read_text())
    legacy = []
    for entry in legacy_index["archives"]:
        path = root / "research/evidence" / entry["archive"]
        assert file_hash(path) == entry["sha256"]
        with tarfile.open(path, "r:gz") as archive:
            for name, expected in entry["member_sha256"].items():
                body = archive.extractfile(name).read()
                assert packet.sha(body) == expected
                if name.endswith(("/manifest.json", "/results.json")):
                    existing.update(seeds_in(json.loads(body)))
        legacy.append(dict(archive=entry["archive"], sha256=entry["sha256"]))
    planned = build_plan()
    new_seeds = {r["seed"] for r in planned["plan"]}
    assert len(new_seeds) == 68 and not existing.intersection(new_seeds)
    assert not new_seeds.intersection(planned["primary"]["inference_seeds"].values())
    prior = subprocess.check_output(["git", "ls-tree", "-r", "--name-only", BASE_COMMIT,
                                     "research/reports/large-T-20261109/followup"],
                                    cwd=root, text=True).splitlines()
    assert not prior, "Unexpected earlier checkpoint at the input revision"
    assert file_hash(root / ENGINE) == ENGINE_SHA256
    manifest, rows, _ = stages["main"]
    arms = {}
    samples = {}
    for T in (1, 16):
        selected = [rows[p["id"]] for p in manifest["plan"]
                    if (p["n"], p["T"], p["factor"]) == (256, T, 1/64)]
        values = np.asarray([257*(1+r["exact_sweep"]) for r in selected])
        assert len(selected) == 24
        samples[T] = values
        arms[str(T)] = dict(count=len(selected), sum_evaluations=int(values.sum()),
                           mean_evaluations=float(values.mean()),
                           U_mean=float(np.mean([r["U"] for r in selected])),
                           S_minus_U_mean=float(np.mean([r["S"]-r["U"] for r in selected])),
                           post_minus_S_mean=float(np.mean([r["post_sweep"]-r["S"] for r in selected])),
                           own_endpoint_repairs=sum(r["endpoint_repairs_own"] for r in selected),
                           external_endpoint_repairs=sum(r["endpoint_repairs_external"] for r in selected))
    key = ["main", "primary", 256, 1/64, "bit", "bit", "uniform", "observed",
           next(p["max_sweeps"] for p in manifest["plan"] if p["n"] == 256), 1]
    rng = np.random.default_rng(int(digest(["large-T-independent-bootstrap-v1", key])[:16], 16))
    draws = rng.choice(samples[1], (10000, 24)).mean(axis=1) / rng.choice(samples[16], (10000, 24)).mean(axis=1)
    ci = np.quantile(draws, [.025, .975]).tolist()
    ratio = float(samples[1].mean()/samples[16].mean())
    with (root / "research/reports/large-T-20261109/campaign/contrasts.csv").open() as handle:
        published = next(r for r in csv.DictReader(handle) if r["stage"] == "main" and r["role"] == "primary")
    for actual, field in ((ratio, "mean_ratio"), (ci[0], "mean_ci_low"), (ci[1], "mean_ci_high")):
        assert abs(actual-float(published[field])) < 1e-12
    capped = [r for r in rows.values() if r["exact_sweep"] is None]
    assert len(capped) == 1
    c = capped[0]
    assert c["id"] == "67178d8d2471ba15457b"
    assert stages["holdout"][2]["state"] == "gate_blocked" and not stages["holdout"][1]
    return dict(status="mechanically checked", base_commit=BASE_COMMIT,
                prior_followup_checkpoints=prior, prerequisite_repair_needed=False,
                packet_index_sha256=packets, verified_legacy_archives=legacy,
                cardinality_unique_planned_seeds=cardinality_seeds,
                all_published_unique_trial_seeds=len(existing), new_planned_seeds=len(new_seeds),
                seed_intersection=[], scientific_outcomes_drawn=0,
                stage_counts={s:{k:v for k,v in triple[2].items() if k not in ("updated_utc",)}
                              for s,triple in stages.items()},
                old_primary=dict(arms=arms, ratio=ratio, nominal_95_ci=ci),
                original_blocking_receipt={k:c[k] for k in ("id", "seed", "n", "T", "factor", "rep", "max_sweeps", "U", "S", "exact_sweep")},
                original_decision="inconclusive; blocked holdout preserved",
                prospective_plan_sha256=planned["plan_sha256"])


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    result = audit()
    args.out.write_text(json.dumps(result, sort_keys=True, indent=2, allow_nan=False)+"\n")
    print("Published packets, primary arithmetic, and new seed separation verified; no sampling.")
