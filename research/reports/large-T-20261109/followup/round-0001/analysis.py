#!/usr/bin/env python3
"""Frozen reference analysis for the prospective study; never runs the engine."""
import argparse
import json
import math
from pathlib import Path

import numpy as np
from plan import BOOTSTRAP, ENGINE, ENGINE_SHA256, STUDY, build_plan, digest, file_hash

EVENTS = ("exact_sweep", "front_sweep", "archive_sweep", "U", "S", "post_sweep")
METRICS = ("exact_evaluations", "post_evaluations", "U_sweeps", "S_sweeps",
           "pre_U_sweeps", "U_to_S_sweeps", "post_S_sweeps", "post_exact_gap_sweeps")


def require(ok, text):
    if not ok:
        raise ValueError(text)


def integer(x, low=0, high=None):
    return type(x) is int and x >= low and (high is None or x <= high)


def validate(row, item, manifest):
    require(all(row.get(k) == v for k, v in item.items()), "Receipt differs from plan")
    require(row.get("record_sha256") == digest({k:v for k,v in row.items() if k != "record_sha256"}),
            "Receipt hash mismatch")
    for k in ("model_sha256", "plan_sha256"):
        require(row.get(k) == manifest[k], f"Receipt {k} mismatch")
    n, T, H = item["n"], item["T"], item["max_sweeps"]
    t = row.get("sweeps")
    require(integer(t, high=H), "Invalid sweep count")
    for key in EVENTS:
        require(key in row and (row[key] is None or integer(row[key], high=t)), "Invalid event: "+key)
    for early, late in (("archive_sweep", "front_sweep"), ("front_sweep", "exact_sweep"),
                        ("U", "S"), ("S", "post_sweep"), ("exact_sweep", "post_sweep")):
        if row[late] is not None:
            require(row[early] is not None and row[early] <= row[late], "Event order violated")
    X, S, P = (row[k] for k in ("exact_sweep", "S", "post_sweep"))
    if X is not None and S is not None and X >= S:
        require(P == X, "Missed first post-S exact boundary")
    require((P is None and t == H and row.get("stop_reason") == "sweep_cap") or
            (P == t and row.get("stop_reason") == "post_exact"), "Invalid termination")
    for k, expected in (("init_evals", n+1), ("attempts", t*(n+1)), ("comparisons", t*(n+1)*T)):
        require(integer(row.get(k)) and row[k] == expected, "Invalid accounting: "+k)
    for k, event, bound in (("bad_at_U", "U", n+1), ("max_error_at_U", "U", n),
                             ("bad_at_S", "S", n+1), ("max_error_at_S", "S", n)):
        require(k in row and ((row[k] is None and row[event] is None) or
                (row[event] is not None and integer(row[k], high=bound))), "Invalid diagnostic: "+k)
    for k in ("external_replacements", "external_changes", "endpoint_repairs_own", "endpoint_repairs_external"):
        require(integer(row.get(k)), "Invalid count: "+k)
    require(row["external_changes"] <= row["external_replacements"] <= t*(n+1)*(T-1),
            "Invalid replacement accounting")
    if T == 1:
        require(row["endpoint_repairs_external"] == 0, "T=1 cannot repair via other donors")
    require(type(row.get("wall_seconds")) in (int, float) and math.isfinite(row["wall_seconds"])
            and row["wall_seconds"] >= 0, "Invalid elapsed time")


def vector(row):
    """All entries known even at an administrative cap; no completed-phase deletion."""
    H, n = row["max_sweeps"], row["n"]
    X, U, S, P = (H if row[k] is None else row[k] for k in ("exact_sweep", "U", "S", "post_sweep"))
    require(0 <= U <= S <= P <= H and X <= P, "Invalid restricted phase order")
    return np.array([(n+1)*(1+X), (n+1)*(1+P), U, S, U, S-U, P-S, P-X], dtype=float)


def wilson(k, n):
    z = 1.959963984540054
    p = k/n
    denom = 1+z*z/n
    center = (p+z*z/(2*n))/denom
    half = z*math.sqrt(p*(1-p)/n+z*z/(4*n*n))/denom
    return [max(0., center-half), min(1., center+half)]


def quantiles(values):
    return np.quantile(values, [.1, .5, .9], method="linear").tolist() if len(values) else None


def phase_diagnostics(rows):
    result = {}
    for name, start, end in (("U", None, "U"), ("S_minus_U", "U", "S"),
                             ("post_minus_S", "S", "post_sweep")):
        entered = len(rows) if start is None else sum(r[start] is not None for r in rows)
        values = [r[end]-(0 if start is None else r[start]) for r in rows if r[end] is not None]
        result[name] = dict(entered=entered, completed=len(values), right_censored_after_entry=entered-len(values),
                            not_entered=len(rows)-entered, completed_only_mean=float(np.mean(values)) if values else None,
                            completed_only_quantiles=quantiles(values), selection_conditioned=True)
    for key in ("bad_at_U", "max_error_at_U", "bad_at_S", "max_error_at_S"):
        values = [r[key] for r in rows if r[key] is not None]
        result[key] = dict(denominator=len(values), mean=float(np.mean(values)) if values else None,
                           quantiles=quantiles(values))
    result["cumulative_work_to_post_or_cap"] = {
        k:sum(r[k] for r in rows) for k in ("attempts", "comparisons", "external_replacements", "external_changes",
                                           "endpoint_repairs_own", "endpoint_repairs_external", "wall_seconds")}
    return result


def analyze(rows, design=None):
    design = build_plan() if design is None else design
    planned = [r for r in design["plan"] if r["stage"] == "main"]
    output = dict(study=STUDY, estimand="fixed-horizon restricted means", arms={}, primary={})
    matrices, resamples = {}, {}
    complete = all(r["id"] in rows for r in planned)
    for T in (1, 23):
        items = sorted((r for r in planned if r["T"] == T), key=lambda r:r["rep"])
        observed = [rows[p["id"]] for p in items if p["id"] in rows]
        N, missing = len(items), len(items)-len(observed)
        initial, horizon = items[0]["n"]+1, (items[0]["n"]+1)*(1+items[0]["max_sweeps"])
        matrix = np.stack([vector(r) for r in observed]) if observed else np.empty((0, len(METRICS)))
        bound = [(float(matrix[:,0].sum())+missing*initial)/N,
                 (float(matrix[:,0].sum())+missing*horizon)/N]
        arm = dict(planned=N, receipts=len(observed), missing=missing,
                   exact_restricted_mean_identification_bounds=bound,
                   diagnostics_observed_receipts_only=phase_diagnostics(observed), events={})
        for event in EVENTS:
            hits = sum(r[event] is not None for r in observed)
            arm["events"][event] = dict(observed=hits, capped=len(observed)-hits, missing=missing,
                                        completion_fraction_bounds=[hits/N, (hits+missing)/N],
                                        completion_wilson_95=wilson(hits,N) if missing == 0 else None)
        if missing == 0:
            matrices[T] = matrix
            arm["restricted_means"] = dict(zip(METRICS, matrix.mean(axis=0).tolist()))
            arm["restricted_quantiles_10_50_90"] = {k:quantiles(matrix[:,i]) for i,k in enumerate(METRICS)}
            rng = np.random.Generator(np.random.PCG64(design["primary"]["inference_seeds"][str(T)]))
            indices = rng.integers(0, N, size=(BOOTSTRAP, N))
            resamples[T] = matrix[indices].mean(axis=1)
            arm["restricted_mean_pointwise_95"] = {
                k:np.quantile(resamples[T][:,i], [.025, .975], method="linear").tolist()
                for i,k in enumerate(METRICS)}
        output["arms"][str(T)] = arm
    a, b = (output["arms"][str(T)]["exact_restricted_mean_identification_bounds"] for T in (1,23))
    output["primary"]["identification_bounds"] = [a[0]/b[1], a[1]/b[0]]
    if complete:
        means = {T:m.mean(axis=0) for T,m in matrices.items()}
        ratio = means[1][0]/means[23][0]
        interval = np.quantile(resamples[1][:,0]/resamples[23][:,0], [.025, .975], method="linear").tolist()
        decision = "favors_T23" if interval[0] > 1 else "favors_T1" if interval[1] < 1 else "inconclusive"
        output["primary"].update(ratio=float(ratio), nominal_95_ci=interval, decision=decision)
        output["diagnostic_differences_T1_minus_T23"] = {
            k:dict(estimate=float(means[1][i]-means[23][i]),
                   nominal_pointwise_95=np.quantile(resamples[1][:,i]-resamples[23][:,i],
                                                   [.025,.975], method="linear").tolist())
            for i,k in enumerate(METRICS)}
    else:
        output["primary"].update(ratio=None, nominal_95_ci=None, decision="incomplete_no_directional_decision")
    return output


def load_run(directory):
    design = build_plan()
    manifest = json.loads((directory / "manifest.json").read_text())
    require(manifest["study"] == STUDY and manifest["plan"] == design["plan"] and
            manifest["plan_sha256"] == design["plan_sha256"], "Manifest design differs")
    require(manifest["sources"].get(ENGINE) == ENGINE_SHA256, "Wrong model source")
    require(manifest["model_sha256"] == digest([STUDY, manifest["sources"], manifest["toolchain"]]),
            "Model signature mismatch")
    for name, expected in manifest["sources"].items():
        require(not Path(name).is_absolute() and ".." not in Path(name).parts, "Unsafe source path")
        require(file_hash(directory / "source" / name) == expected, "Archived source mismatch")
    by_id = {r["id"]:r for r in design["plan"]}
    rows = {}
    for path in sorted((directory / "rows").glob("*.json")):
        require(path.stem in by_id, "Unplanned receipt")
        row = json.loads(path.read_text())
        validate(row, by_id[path.stem], manifest)
        rows[path.stem] = row
    smoke = [r for r in design["plan"] if r["stage"] == "smoke"]
    if any(r["stage"] == "main" for r in rows.values()):
        require(all(r["id"] in rows and rows[r["id"]]["post_sweep"] is not None for r in smoke),
                "Main outcomes without passing smoke")
    return rows


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    summary = analyze(load_run(args.run))
    args.out.write_text(json.dumps(summary, indent=2, sort_keys=True, allow_nan=False)+"\n")
