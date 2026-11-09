#!/usr/bin/env python3
"""Analyze first boundary hits for the own-parent, cardinality-T campaign."""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import re
import tempfile
from collections import defaultdict
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np


STAGES = ("smoke", "calibrate", "main", "holdout")
EVENTS = ("exact_sweep", "front_sweep", "archive_sweep", "U", "S", "post_sweep")
CONFIG = ("stage", "cohort", "n", "factor", "mutation", "noise", "init", "reference",
          "max_sweeps", "T")
FIELDS = ("id", "rep", "seed", *CONFIG[1:])


def digest(obj):
    raw = json.dumps(obj, sort_keys=True, separators=(",", ":"), allow_nan=False)
    return hashlib.sha256(raw.encode()).hexdigest()


def require(ok, message):
    if not ok:
        raise ValueError(message)


def integer(value, minimum=0):
    return type(value) is int and value >= minimum


def validate_receipt(row, trial, manifest):
    ident = trial["id"]
    require(all(row.get(k) == v for k, v in trial.items()), f"Plan/receipt mismatch in {ident}")
    for k in ("model_sha256", "plan_sha256"):
        require(row.get(k) == manifest[k], f"{k} mismatch in {ident}")
    unsigned = {k: v for k, v in row.items() if k != "record_sha256"}
    require(row.get("record_sha256") == digest(unsigned), f"Receipt hash mismatch in {ident}")
    n, T, cap = trial["n"], trial["T"], trial["max_sweeps"]
    sweeps = row["sweeps"]
    require(integer(sweeps) and sweeps <= cap, f"Sweep count outside horizon in {ident}")
    require(row["attempts"] == (n+1)*sweeps and integer(row["attempts"]),
            f"Attempt count mismatch in {ident}")
    require(row["init_evals"] == (0 if trial["init"] == "corner" else n+1),
            f"Initialization count mismatch in {ident}")
    for key in EVENTS:
        value = row[key]
        require(value is None or (integer(value) and value <= sweeps),
                f"{key} outside observed prefix in {ident}")
    # Every exact assignment covers the current front; every incumbent has
    # appeared in the passive true-weight archive. S and exact are unordered.
    for before, after in (("U", "S"), ("S", "post_sweep"), ("exact_sweep", "post_sweep"),
                          ("front_sweep", "exact_sweep"), ("archive_sweep", "front_sweep")):
        if row[after] is not None:
            require(row[before] is not None and row[before] <= row[after],
                    f"Invalid {before}, {after} order in {ident}")
    exact, pinned, post = row["exact_sweep"], row["S"], row["post_sweep"]
    if exact is not None and pinned is not None and exact >= pinned:
        require(post == exact, f"Post-S event missed in {ident}")
    if post is None:
        require(sweeps == cap and row["stop_reason"] == "sweep_cap", f"Incomplete cap in {ident}")
    else:
        require(post == sweeps and row["stop_reason"] == "post_exact", f"Invalid stop in {ident}")
    require(integer(row["comparisons"]) and row["comparisons"] == row["attempts"]*T,
            f"Recipient comparison mismatch in {ident}")
    require(integer(row["external_replacements"]) and
            row["external_replacements"] <= row["attempts"]*(T-1),
            f"External replacement count mismatch in {ident}")
    require(isinstance(row["wall_seconds"], (float, int)) and math.isfinite(row["wall_seconds"])
            and row["wall_seconds"] >= 0, f"Invalid wall duration in {ident}")
    if trial["reference"] == "ideal":
        require(row["U"] == 0, f"Supplied reference did not freeze at zero in {ident}")
    if trial["factor"] == 0 and trial["init"] == "uniform":
        require(exact == pinned == post, f"Noiseless natural assignment identity failed in {ident}")


def load_runs(directories):
    seeds, stages, groups, sources = set(), set(), defaultdict(list), []
    for root in directories:
        raw = (root / "manifest.json").read_bytes()
        manifest = json.loads(raw)
        stage, plan = manifest["stage"], manifest["plan"]
        require(stage in STAGES and stage not in stages, f"Unknown or repeated stage: {stage}")
        stages.add(stage)
        require(plan and manifest["plan_sha256"] == digest(plan), f"Invalid frozen plan for {stage}")
        require(re.fullmatch(r"[0-9a-f]{64}", manifest["model_sha256"]),
                f"Invalid model digest for {stage}")
        ids, reps, row_hashes = set(), set(), []
        for trial in plan:
            require(all(k in trial for k in FIELDS), f"Missing plan field in {stage}")
            ident = trial["id"]
            require(isinstance(ident, str) and re.fullmatch(r"[0-9a-f]{20}", ident)
                    and ident not in ids, f"Invalid or duplicate trial id: {ident}")
            ids.add(ident)
            require(integer(trial["seed"]) and trial["seed"] not in seeds, f"Invalid or reused seed: {ident}")
            seeds.add(trial["seed"])
            require(integer(trial["n"], 2) and integer(trial["T"], 1)
                    and trial["T"] <= trial["n"]+1 and integer(trial["max_sweeps"], 1)
                    and integer(trial["rep"]) and isinstance(trial["factor"], (float, int))
                    and 0 <= trial["factor"] <= trial["n"] and trial["mutation"] in ("one", "bit")
                    and trial["noise"] in ("one", "bit") and trial["init"] in ("corner", "uniform")
                    and trial["reference"] in ("observed", "ideal"), f"Invalid trial config: {ident}")
            key = (stage, *(trial[k] for k in CONFIG[1:]))
            require((key, trial["rep"]) not in reps, f"Repeated repetition in {stage} {ident}")
            reps.add((key, trial["rep"]))
            receipt = root / "rows" / (ident + ".json")
            row = None
            if receipt.exists():
                row = json.loads(receipt.read_text())
                validate_receipt(row, trial, manifest)
                row_hashes.append((ident, row["record_sha256"]))
            groups[key].append(row)
        extra = {p.stem for p in (root / "rows").glob("*.json")} - ids
        require(not extra, f"Unplanned receipts in {stage}: {sorted(extra)}")
        sources.append({"stage": stage, "model_sha256": manifest["model_sha256"],
                        "manifest_sha256": hashlib.sha256(raw).hexdigest(),
                        "plan_sha256": manifest["plan_sha256"], "planned": len(ids),
                        "receipts": len(row_hashes), "receipts_sha256": digest(sorted(row_hashes))})
    require(len({s["model_sha256"] for s in sources}) <= 1, "Cannot combine different model versions")
    return groups, sorted(sources, key=lambda s: STAGES.index(s["stage"]))


def event_summary(cfg, rows, event):
    n, cap = cfg["n"], cfg["max_sweeps"]
    initial = 0 if cfg["init"] == "corner" else n + 1
    seen = [r for r in rows if r is not None]
    observed = [initial+(n+1)*r[event] for r in seen if r[event] is not None]
    horizon = initial + (n+1)*cap
    missing = len(rows)-len(seen)
    censored = len(seen)-len(observed)
    restricted = observed + [horizon]*censored
    # A missing row has no confirmed prefix. A post-S exact hit implies all
    # other first hits, hence every null event in a valid receipt ran to cap.
    lower = (sum(restricted) + missing*initial)/len(rows)
    upper = (sum(restricted) + missing*horizon)/len(rows)
    complete = len(observed) == len(rows)
    stats = np.quantile(observed, [0.1, 0.5, 0.9]) if complete else (None,)*3
    summary = dict(cfg, event=event, planned=len(rows), observed=len(observed), at_cap=censored,
                   missing=missing, horizon_evaluations=horizon, completion_lower=len(observed)/len(rows),
                   completion_upper=(len(observed)+missing)/len(rows), restricted_mean_lower=lower,
                   restricted_mean_upper=upper,
                   restricted_mean_comparisons_lower=(lower-initial)*cfg["T"],
                   restricted_mean_comparisons_upper=(upper-initial)*cfg["T"],
                   mean_evaluations=float(np.mean(observed)) if complete else None,
                   q10=stats[0], median=stats[1], q90=stats[2])
    return summary, np.asarray(restricted, dtype=float) if not missing else None


def work_summary(cfg, rows):
    seen = [r for r in rows if r is not None]
    work = dict(cfg, planned=len(rows), receipts=len(seen))
    for name in ("attempts", "comparisons", "external_replacements", "wall_seconds"):
        work["total_"+name] = sum(r[name] for r in seen)
    duration = work["total_wall_seconds"]
    work["attempts_per_second"] = work["total_attempts"]/duration if duration > 0 else None
    work["comparisons_per_second"] = work["total_comparisons"]/duration if duration > 0 else None
    for name in ("endpoint_repairs_own", "endpoint_repairs_external"):
        if all(r.get(name) is not None for r in seen):
            work["total_"+name] = sum(r[name] for r in seen)
        else:
            work["total_"+name] = None
    for name in ("bad_at_U", "max_error_at_U", "bad_at_S", "max_error_at_S"):
        vals = [r[name] for r in seen if r.get(name) is not None]
        work["observed_"+name] = len(vals)
        work["mean_observed_"+name] = float(np.mean(vals)) if vals else None
    for name, start, end in (("U", None, "U"), ("S_minus_U", "U", "S"),
                             ("phase_II", "S", "post_sweep")):
        durations = [r[end] - (r[start] if start else 0) for r in seen if r[end] is not None]
        work["observed_"+name] = len(durations)
        work["mean_observed_"+name+"_sweeps"] = float(np.mean(durations)) if durations else None
    if cfg["init"] == "corner":
        donors = [r["first_corner_donor"] for r in seen if r.get("first_corner_donor") is not None]
        work["observed_first_corner_donor"] = len(donors)
        work["first_corner_donor_own"] = donors.count(0)
        work["first_corner_donor_external"] = len(donors) - donors.count(0)
    else:
        work.update(observed_first_corner_donor=None, first_corner_donor_own=None,
                    first_corner_donor_external=None)
    return work


def contrasts(exact_cells, bootstrap):
    records = []
    for key, (a, values_a) in exact_cells.items():
        if (a["T"] != 1 or a["stage"] not in ("main", "holdout") or a["cohort"] != "primary"
                or a["init"] != "uniform" or a["reference"] != "observed"
                or a["mutation"] != "bit" or a["noise"] != "bit"):
            continue
        target = math.ceil(math.sqrt(a["n"]))
        other = key[:-1]+(target,)
        require(other in exact_cells, f"Missing prespecified comparison cell for {key}")
        b, values_b = exact_cells[other]
        rr = {k: a[k] for k in CONFIG if k != "T"}
        primary_n = 256 if a["stage"] == "main" else 512
        role = ("primary" if a["n"] == primary_n and a["factor"] == 1/64 else "exploratory")
        rr.update(role=role,T_baseline=1, T_comparator=target, baseline_observed=a["observed"],
                  comparator_observed=b["observed"], baseline_planned=a["planned"],
                  comparator_planned=b["planned"], restricted_ratio_lower=a["restricted_mean_lower"]/b["restricted_mean_upper"],
                  restricted_ratio_upper=a["restricted_mean_upper"]/b["restricted_mean_lower"],
                  restricted_ratio=None, restricted_ci_low=None, restricted_ci_high=None,
                  mean_ratio=None, mean_ci_low=None, mean_ci_high=None)
        if values_a is None or values_b is None:
            rr["status"] = "missing_receipts"
        else:
            ratio = float(values_a.mean()/values_b.mean())
            seed = int(digest(["large-T-independent-bootstrap-v1",list(key)])[:16], 16)
            rng = np.random.default_rng(seed)
            draws = (rng.choice(values_a, size=(bootstrap,len(values_a))).mean(axis=1) /
                     rng.choice(values_b, size=(bootstrap,len(values_b))).mean(axis=1))
            lo, hi = np.quantile(draws,[0.025,0.975])
            rr.update(restricted_ratio=ratio, restricted_ci_low=float(lo), restricted_ci_high=float(hi))
            if a["at_cap"]+b["at_cap"]:
                rr["status"] = "cap_censored"
            else:
                rr.update(mean_ratio=ratio, mean_ci_low=float(lo), mean_ci_high=float(hi))
                rr["status"] = "all_exact_observed"
        records.append(rr)
    return records


def primary_decision(ratios):
    primary = {r["stage"]:r for r in ratios if r["role"] == "primary"}
    if set(primary) != {"main", "holdout"}:
        return "Pending — both the n=256 primary and independent n=512 confirmation are required."
    if any(r["status"] != "all_exact_observed" for r in primary.values()):
        return "Inconclusive — a primary or confirmation arm has cap-censored or missing exact times."
    if all(r["mean_ci_low"] > 1 for r in primary.values()):
        return ("Empirically supported at the two specified sizes: both pointwise 95% "
                "intervals for the baseline/comparator mean ratio lie above one.")
    return "Inconclusive — the prespecified two-stage criterion for a finite-size reduction was not met."


def corner_prediction(cfg, repetitions, draws):
    """Exact restricted mean and simulated central 95% range for a mean of this many trials."""
    n, k, cap = cfg["n"], cfg["T"], cfg["max_sweeps"]
    # Until the first weight 0 broadcast to slot 0, all other slots remain
    # correct, slot 0 stays at weight 2, and individual mutation draws are fresh.
    log_survival = 0.0
    for breeder in range(n+1):
        recipients = sorted(range(n+1), key=lambda j: (abs(j-breeder), j if breeder%2 else -j))[:k]
        if 0 not in recipients:
            continue
        weight = 2 if breeder == 0 else breeder
        hit = (1/n)**weight * (1-1/n)**(n-weight)
        log_survival += math.log1p(-hit)
    q = -math.expm1(log_survival)
    mean = (n+1)*(-math.expm1(cap*log_survival))/q
    rng = np.random.default_rng(int(digest(["corner-prediction-v1", cfg])[:16], 16))
    replicas = rng.geometric(q, size=(draws, repetitions))
    bounds = np.quantile((n+1)*np.minimum(replicas, cap).mean(axis=1), [.025, .975])
    return mean, float(bounds[0]), float(bounds[1])


def write_table(path, data, fields):
    with path.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields, lineterminator='\n')
        writer.writeheader()
        writer.writerows(data)


def plot_stage(out, stage, cells):
    # Display matched model/reference/init settings; controls remain in the CSV.
    chosen = [c for c in cells if c["stage"] == stage and c["mutation"] == c["noise"] == "bit"
              and c["init"] == "uniform" and c["reference"] == "observed"]
    if not chosen:
        return []
    sizes = sorted({c["n"] for c in chosen})
    factors = sorted({c["factor"] for c in chosen})
    names = []
    for which in ("runtime", "completion"):
        fig, axs = plt.subplots(len(sizes), len(factors), squeeze=False,
                                figsize=(max(5.5,len(factors)*3.3),1.3+2.5*len(sizes)))
        fig.suptitle(f"{stage.title()} · " + ("First exact assignment" if which == "runtime"
                                              else "Confirmed boundary hits"))
        for i,n in enumerate(sizes):
            for j,f in enumerate(factors):
                ax = axs[i,j]
                group = sorted((c for c in chosen if c["n"] == n and c["factor"] == f),
                               key=lambda x:x["T"])
                if not group:
                    ax.set_axis_off()
                    continue
                ax.set_title(f"n = {n}   ·   p = {f:g}/n", fontsize=10)
                if which == "runtime":
                    x = [r["T"] for r in group if r["event"]=="exact_sweep"]
                    vals = [r for r in group if r["event"]=="exact_sweep"]
                    low = np.array([r["restricted_mean_lower"] for r in vals])/n**2
                    high = np.array([r["restricted_mean_upper"] for r in vals])/n**2
                    ax.plot(x,low,"o-",color="#225b8d",label="Restricted mean / lower bound")
                    if any(r["missing"] for r in vals):
                        ax.fill_between(x,low,high,color="#9dbede",alpha=.5)
                        ax.plot(x,high,"x--",color="#617b9a",label="Missing-row upper bound")
                    if j == 0:
                        ax.set_ylabel("Restricted mean evals / n²",fontsize=9)
                else:
                    for event,label,marker in (("exact_sweep","Exact","o"),("front_sweep","Front","^"),
                                              ("archive_sweep","Archive","x"),("post_sweep","Post-S","s")):
                        vals = [r for r in group if r["event"]==event]
                        x = [r["T"] for r in vals]
                        ax.plot(x,[r["completion_lower"] for r in vals],marker=marker,
                                fillstyle="none",alpha=.85,label=label)
                    ax.set_ylim(-.05,1.05)
                    if j==0: ax.set_ylabel("Hits / planned trials",fontsize=9)
                ax.set_xscale("log",base=2)
                ax.set_xticks(x,labels=[str(t) for t in x],fontsize=8)
                ax.minorticks_off()
                if i == len(sizes)-1: ax.set_xlabel("Neighborhood cardinality T")
                ax.grid(axis="y",alpha=.2)
        legend = {}
        for ax in axs.flat:
            lines, labels = ax.get_legend_handles_labels()
            legend.update(zip(labels,lines))
        fig.legend(legend.values(),legend.keys(),loc="upper center",bbox_to_anchor=(.5,.94),
                   ncol=min(4,len(legend)),fontsize=8,frameon=False)
        fig.tight_layout(rect=(0,0,1,.88 if len(sizes)==1 else .92))
        name=f"{which}-{stage}.png"
        fig.savefig(out/name,dpi=145)
        plt.close(fig)
        names.append(name)
    return names


def plot_calibration(out, cells, work):
    names = []
    corner = [r for r in cells if r["stage"] == "calibrate"
              and r["theoretical_corner_restricted_evaluations"] is not None]
    if corner:
        sizes = sorted({r["n"] for r in corner})
        fig, axs = plt.subplots(1, len(sizes), squeeze=False, sharey=True,
                                figsize=(max(6, 4 * len(sizes)), 4.3))
        for n, ax in zip(sizes, axs.flat):
            rows = sorted((r for r in corner if r["n"] == n), key=lambda r: r["T"])
            x = [r["T"] for r in rows]
            ax.fill_between(x, [r["corner_prediction_low"] for r in rows],
                            [r["corner_prediction_high"] for r in rows],
                            color="#dae6ef", label="95% predictive range")
            ax.plot(x, [r["theoretical_corner_restricted_evaluations"] for r in rows],
                    color="#2d5774", label="Geometric expectation")
            observed = [r for r in rows if not r["missing"]]
            ax.scatter([r["T"] for r in observed],
                       [r["restricted_mean_lower"] for r in observed], color="#bc592b",
                       zorder=3, label="Observed mean")
            ax.set_title(f"n = {n}")
            ax.set(xscale="log", yscale="log", xlabel="Neighborhood cardinality T")
            ax.set_xticks(x, labels=[str(t) for t in x])
            ax.minorticks_off()
            ax.grid(axis="y", alpha=.2)
        axs[0,0].set_ylabel("Mean capped evaluations")
        fig.suptitle("Calibration · supplied-corner repair")
        fig.legend(*axs[0,0].get_legend_handles_labels(), loc="upper center",
                   bbox_to_anchor=(.5,.92), ncol=3, frameon=False, fontsize=8)
        fig.tight_layout(rect=(0,0,1,.84))
        name = "corner-calibrate.png"
        fig.savefig(out/name,dpi=145)
        plt.close(fig)
        names.append(name)
    benchmark = [r for r in work if r["stage"] == "calibrate" and r["cohort"] == "calibration"]
    if benchmark:
        fig, axs = plt.subplots(1,2,figsize=(8,4.3))
        sizes = sorted({r["n"] for r in benchmark})
        for ax, metric, title in zip(axs, ("attempts_per_second","comparisons_per_second"),
                                    ("Offspring evaluations / second","Recipient comparisons / second")):
            for single, label, color in ((True,"T = 1","#2d5774"),(False,"T = n + 1","#bc592b")):
                rows = sorted((r for r in benchmark if r["T"] == (1 if single else r["n"] + 1)
                               and r[metric] is not None), key=lambda r:r["n"])
                ax.plot([r["n"] for r in rows], [r[metric] for r in rows], "o-",
                        color=color, label=label)
            ax.set(xlabel="Dimension n", title=title, yscale="log")
            ax.set_xticks(sizes, labels=[str(n) for n in sizes])
            ax.grid(axis="y",alpha=.2)
        fig.suptitle("Calibration · local process throughput")
        fig.legend(*axs[0].get_legend_handles_labels(), loc="upper center",
                   bbox_to_anchor=(.5,.92), ncol=2, frameon=False, fontsize=8)
        fig.tight_layout(rect=(0,0,1,.84))
        name = "throughput-calibrate.png"
        fig.savefig(out/name,dpi=145)
        plt.close(fig)
        names.append(name)
    return names


CONTRAST_FIELDS = [k for k in CONFIG if k != "T"] + [
    "role","T_baseline","T_comparator","baseline_observed","comparator_observed","baseline_planned",
    "comparator_planned","restricted_ratio_lower","restricted_ratio_upper","restricted_ratio",
    "restricted_ci_low","restricted_ci_high","mean_ratio","mean_ci_low","mean_ci_high","status"]


def analyze(roots, out, bootstrap=10_000):
    require(bootstrap >= 100, "Use at least 100 independent bootstrap draws")
    groups, sources = load_runs(roots)
    cells, work, exact = [], [], {}
    for key, rows in sorted(groups.items(), key=lambda z:(STAGES.index(z[0][0]),*z[0][1:])):
        cfg = dict(zip(CONFIG,key))
        for event in EVENTS:
            cell, values = event_summary(cfg,rows,event)
            predicted = (None, None, None)
            if (event == "exact_sweep" and cfg["init"] == "corner" and cfg["reference"] == "ideal"
                    and cfg["mutation"] == "bit" and cfg["factor"] == 0):
                predicted = corner_prediction(cfg, len(rows), bootstrap)
            (cell["theoretical_corner_restricted_evaluations"], cell["corner_prediction_low"],
             cell["corner_prediction_high"]) = predicted
            cells.append(cell)
            if event=="exact_sweep":
                exact[key] = cell, values
        work.append(work_summary(cfg,rows))
    ratios = contrasts(exact,bootstrap)
    out.mkdir(parents=True,exist_ok=True)
    # A failed JSON/plot build leaves the previous report readable. Commit output
    # only after this command exits successfully; the report is published last.
    with tempfile.TemporaryDirectory(dir=out.parent) as tmp:
        publish = Path(tmp)
        write_table(publish/"cells.csv",cells,list(cells[0]))
        write_table(publish/"work.csv",work,list(work[0]))
        write_table(publish/"contrasts.csv",ratios,CONTRAST_FIELDS)
        images=[]
        for s in sources:
            if s["stage"] == "calibrate":
                images.extend(plot_calibration(publish, cells, work))
            else:
                images.extend(plot_stage(publish,s["stage"],cells))
        provenance = {"analysis_version":1, "bootstrap_draws":bootstrap, "numpy":np.__version__,
                      "matplotlib":matplotlib.__version__, "sources":sources,
                      "analyzer_sha256":hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}
        (publish/"provenance.json").write_text(json.dumps(provenance,indent=2,sort_keys=True)+"\n")
        report = ["# Larger-neighborhood campaign", "",
                  "The primary endpoint is first exact assignment at a sweep boundary. "
                  "Evaluations include n + 1 initial observations for uniform starts. "
                  "Each subsequent sweep costs n + 1 evaluations. All cohorts and stopping "
                  "events are retained in cells.csv.","",
                  "| Stage | Planned | Verified receipts | Missing | Role |",
                  "|---|---:|---:|---:|---|"]
        for s in sources:
            role = {"smoke":"mechanics only","calibrate":"timing and corner controls","main":"main grid",
                    "holdout":"predeclared validation"}[s["stage"]]
            report.append(f"| {s['stage']} | {s['planned']} | {s['receipts']} | "
                          f"{s['planned']-s['receipts']} | {role} |")
        report.extend(["","## Finite-size contrasts","",
                       "Ratio = mean exact evaluations at T=1 divided by the mean at T=ceil(sqrt(n)). "
                       "Values above one favor the larger neighborhood. Each arm uses independent trials. "
                       "Intervals are deterministic, pointwise 95% percentile bootstraps with "
                       f"{bootstrap:,} independent-arm resamples; no multiplicity correction. "
                       "The primary contrast is n=256, factor=1/64, T=1 vs 16. Independent confirmation "
                       "is n=512, factor=1/64, T=1 vs 23. Other intervals are exploratory. "
                       "Repeated seeds are rejected.","",primary_decision(ratios),""])
        if ratios:
            report.extend(["| Stage | n | Noise factor | T | Mean ratio [95% interval] | Restricted ratio |",
                           "|---|---:|---:|---:|---|---|"])
            for row in ratios:
                ratio = (f"{row['mean_ratio']:.3f} [{row['mean_ci_low']:.3f}, {row['mean_ci_high']:.3f}]"
                         if row['mean_ratio'] is not None else row['status'].replace("_"," "))
                restricted = (f"{row['restricted_ratio']:.3f}" if row["restricted_ratio"] is not None
                              else f"[{row['restricted_ratio_lower']:.3f}, {row['restricted_ratio_upper']:.3f}]")
                report.append(f"| {row['stage']} | {row['n']} | {row['factor']:g} | "
                              f"{row['T_comparator']} | {ratio} | {restricted} |")
        else:
            report.append("Only control or timing stages are present. These samples support "
                          "execution and instrumentation checks; the primary contrasts await main/holdout.")
        benchmarks = [w for w in work if w["stage"] == "calibrate" and w["cohort"] == "calibration"]
        if benchmarks:
            report.extend(["","## Local throughput benchmark","",
                           "Aggregated over received timing trials; elapsed cost includes engine process start. "
                           "Comparisons count recipient tests.","",
                           "| n | T | Receipts | Attempts/s | Recipient comparisons/s |",
                           "|---:|---:|---:|---:|---:|"])
            for w in benchmarks:
                fmt = lambda x: "—" if x is None else f"{x:,.0f}"
                report.append(f"| {w['n']} | {w['T']} | {w['receipts']}/{w['planned']} | "
                              f"{fmt(w['attempts_per_second'])} | {fmt(w['comparisons_per_second'])} |")
        corner = [c for c in cells if c["theoretical_corner_restricted_evaluations"] is not None]
        if corner:
            report.extend(["","## Supplied-corner benchmark","",
                           "With inactive noise and all stored labels pinned, only slot zero needs repair. "
                           "Each sweep has independent success opportunities from its eligible donors. "
                           "The analytical restricted expectation uses the resulting geometric law and "
                           "each cell's actual cap. The last column is a central model-predictive 95% range for "
                           f"the planned sample mean, using {bootstrap:,} deterministic Monte Carlo draws "
                           "of independent capped geometric samples of that size. No initialization "
                           "evaluations are charged. See research/LARGE_T_THEORY.md for the derivation.","",
                           "| Stage | n | T | Receipts / planned | Restricted mean evals [lower, upper] | Analytic | Prediction range |",
                           "|---|---:|---:|---:|---:|---:|---:|"])
            for c in corner:
                report.append(f"| {c['stage']} | {c['n']} | {c['T']} | {c['planned']-c['missing']}/{c['planned']} "
                              f"| [{c['restricted_mean_lower']:.1f}, {c['restricted_mean_upper']:.1f}] "
                              f"| {c['theoretical_corner_restricted_evaluations']:.1f} "
                              f"| [{c['corner_prediction_low']:.1f}, {c['corner_prediction_high']:.1f}] |")
        report.extend(["","## Observation horizon and computational work","",
                       "At cap K, the restricted cost is initialization + (n+1) min(first-hit sweep,K). "
                       "A missing receipt supplies no confirmed trajectory prefix. For that planned trial "
                       "the restricted cost is bounded by initialization and initialization + (n+1)K. "
                       "First exact assignment can occur before S, when stored labels have not all reached their targets. "
                       "The shaded range in a runtime plot (when present) is a missing-data identification "
                       "range, not a sampling interval. Completion plots count confirmed hits divided by "
                       "all planned trials. Unrestricted means and quantiles are withheld if any required "
                       "trial is missing or the event is cap-censored. Even fully observed finite samples "
                       "cannot exclude rare longer trajectories.","",
                       "For each event, cells.csv gives lower and upper restricted-mean logical comparison "
                       "counts. At boundary s these equal T(n+1)s. Initialization contributes zero recipient "
                       "comparisons. Wall time in work.csv covers each entire receipted run through the "
                       "post-S endpoint or cap. An earlier exact boundary has no separate elapsed timestamp.","",
                       "The phase columns in work.csv are mean_observed_U_sweeps (first ideal reference), "
                       "mean_observed_S_minus_U_sweeps (from U to stored alignment), and "
                       "mean_observed_phase_II_sweeps (from S to first post-S exact assignment). "
                       "Each includes only trajectories that reached its end boundary. Its observed_* "
                       "count gives the denominator and planned gives the total scheduled. The three durations "
                       "sum to the post-S hitting sweep on a single completed trajectory. Cell means using "
                       "different observed sets need not add. True/stored mismatch counts and maximum "
                       "absolute errors at U and S use the same boundary-conditional convention. First corner "
                       "donor counts classify the first observed endpoint-zero repair as own or external.","",
                       "## Plots","","Runtime and completion plots show uniform, moving-reference bitwise/bitwise cells. "
                       "Each panel holds dimension and noise factor fixed. Calibration figures compare capped corner means "
                       "with the geometric model and show measured throughput. Observed corner means are plotted "
                       "only when all receipts are present. All trial types appear in the CSVs.",""])
        report.extend(f"![{name.removesuffix('.png')}]({name})" for name in images)
        (publish/"report.md").write_text("\n".join(report)+"\n")
        for pattern in ("runtime-*.png","completion-*.png","corner-calibrate.png","throughput-calibrate.png"):
            for old in out.glob(pattern):
                if old.name not in images and old.stem.split("-")[-1] in STAGES: old.unlink()
        for name in ["cells.csv","work.csv","contrasts.csv","provenance.json",*images,"report.md"]:
            (publish/name).replace(out/name)
    return cells, ratios


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--runs",type=Path,nargs="+",required=True)
    parser.add_argument("--out",type=Path,required=True)
    parser.add_argument("--bootstrap",type=int,default=10_000)
    args=parser.parse_args()
    analyze(args.runs,args.out,args.bootstrap)
    print(args.out/"report.md")


if __name__=="__main__":
    main()
