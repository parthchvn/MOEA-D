#!/usr/bin/env python3
"""Build the prospective design. This module never launches a simulation."""
import argparse
import csv
import hashlib
import io
import json
from pathlib import Path

STUDY = "large-T-512-low-noise-prospective-20261109-r1-v1"
BASE_COMMIT = "4f0d9533e1e6fa30e2da9eae14cb75956762f2b5"
ENGINE = "scripts/neighborhood_sweep.cpp"
ENGINE_SHA256 = "11bdbd26facb39b22df911d063e1718dd03a2ae8fd01a18458d1c5e8f694df10"
BOOTSTRAP = 10000


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":"),
                                   allow_nan=False).encode("utf-8")).hexdigest()


def file_hash(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def repo_root():
    for path in Path(__file__).resolve().parents:
        if (path / ENGINE).is_file() and (path / "AGENTS.md").is_file():
            return path
    raise ValueError("Place this bundle inside the research checkout")


def build_plan():
    rows = []
    for stage, n, reps, cap in (("smoke", 32, 2, 10742), ("main", 512, 32, 38341)):
        for rep in range(reps):
            for size in ((1, 23) if rep % 2 == 0 else (23, 1)):
                config = dict(stage=stage, n=n, T=size, factor=0.015625,
                              mutation="bit", noise="bit", init="uniform",
                              reference="observed", max_sweeps=cap, rep=rep)
                token = digest([STUDY, "trial", config])
                rows.append(dict(id=token[:20], seed=int(digest([STUDY, "seed", token])[:16], 16),
                                 **config))
    assert len({r["id"] for r in rows}) == len(rows)
    assert len({r["seed"] for r in rows}) == len(rows)
    return dict(format=1, study=STUDY, status="prospective-no-scientific-outcomes",
                base_commit=BASE_COMMIT, engine=ENGINE, engine_sha256=ENGINE_SHA256,
                model_version="own-parent-cardinality-v1", plan=rows,
                plan_sha256=digest(rows),
                resource_policy=dict(workers=1, measurement_seconds=1800,
                                     max_invocations=1, same_seed_retries_in_invocation=0),
                primary=dict(n=512, factor=0.015625, activation_probability=1/32768,
                             baseline_T=1, comparator_T=23, repetitions_per_arm=32,
                             cap_sweeps=38341, cap_evaluations=19669446,
                             event="exact_sweep", estimand="ratio_of_restricted_mean_evaluations",
                             bootstrap_replicates=BOOTSTRAP, interval=[0.025, 0.975],
                             quantile_method="linear", bit_generator="PCG64",
                             inference_seeds={str(T): int(digest([STUDY, "bootstrap", T])[:16], 16)
                                              for T in (1, 23)}))


def seed_csv(plan):
    out = io.StringIO(newline="")
    fields = ["order", "id", "stage", "n", "T", "factor", "rep", "seed", "max_sweeps",
              "mutation", "noise", "init", "reference"]
    writer = csv.DictWriter(out, fieldnames=fields, lineterminator="\n")
    writer.writeheader()
    for order, row in enumerate(plan["plan"]):
        writer.writerow(dict(order=order, **row))
    return out.getvalue()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, default=Path(__file__).resolve().parent)
    parser.add_argument("--check", action="store_true", help="verify, never overwrite")
    args = parser.parse_args()
    plan = build_plan()
    files = {"plan.json": json.dumps(plan, indent=2, sort_keys=True, allow_nan=False)+"\n",
             "seeds.csv": seed_csv(plan)}
    if args.check:
        for name, expected in files.items():
            if (args.out / name).read_text() != expected:
                raise ValueError(f"Frozen design differs: {name}")
        if file_hash(repo_root() / ENGINE) != ENGINE_SHA256:
            raise ValueError("Engine source differs from the registered model")
    else:
        args.out.mkdir(parents=True, exist_ok=True)
        for name, data in files.items():
            path = args.out / name
            if path.exists() and path.read_text() != data:
                raise ValueError(f"Refusing to replace a different design: {name}")
            path.write_text(data)
    print(json.dumps(dict(study=STUDY, planned=len(plan["plan"]),
                          plan_sha256=plan["plan_sha256"], sampling_performed=False), sort_keys=True))


if __name__ == "__main__":
    main()
