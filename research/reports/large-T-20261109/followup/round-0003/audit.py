#!/usr/bin/env python3
"""Independent receipt audit. Reads published evidence; never runs a sampler.

From the checkout: python deliverables/audit.py --repo . --out /tmp/r3-audit
Only NumPy's registered PCG64 index generator is used for bootstrap randomness.
No previous analyzer, validator, wrapper or plan generator is imported.
"""
import argparse
import collections
import csv
import datetime as dt
import hashlib
import json
import math
import os
from pathlib import Path
import subprocess
import tarfile

for _key in ("OPENBLAS_NUM_THREADS", "OMP_NUM_THREADS", "MKL_NUM_THREADS",
             "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ[_key] = "1"
import numpy as np

BASE = Path("research/reports/large-T-20261109")
R1 = BASE / "followup/round-0001"
R2 = BASE / "followup/round-0002"
EVENTS = ("exact_sweep", "front_sweep", "archive_sweep", "U", "S", "post_sweep")
METRICS = ("exact_evaluations", "post_evaluations", "U_sweeps", "S_sweeps",
           "pre_U_sweeps", "U_to_S_sweeps", "post_S_sweeps", "post_exact_gap_sweeps")
WORK = ("attempts", "comparisons", "external_replacements", "external_changes",
        "endpoint_repairs_own", "endpoint_repairs_external", "wall_seconds")


def need(ok, message):
    if not ok:
        raise ValueError(message)


def sha(body):
    return hashlib.sha256(body).hexdigest()


def digest(value):
    return sha(json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False).encode())


def read(path):
    return json.loads(path.read_bytes())


def dump(path, value):
    path.write_text(json.dumps(value, indent=2, sort_keys=True, allow_nan=False)+"\n")


def table(path, rows):
    with path.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def percentile(values, p):
    """Independent linear order-statistic interpolation (not np.quantile)."""
    values = sorted(values)
    if not values:
        return None
    h = (len(values)-1)*p
    i = int(h)
    return float(values[i] + (h-i)*(values[min(i+1, len(values)-1)]-values[i]))


def interval(values):
    return [percentile(values, .025), percentile(values, .975)]


def mean(values):
    return sum(values)/len(values) if len(values) else None


def wilson(hits, total):
    z = 1.959963984540054
    # Count-scale equivalent of the Wilson score formula.
    midpoint = (hits+z*z/2)/(total+z*z)
    radius = z*math.sqrt(hits*(total-hits)/total+z*z/4)/(total+z*z)
    return [max(0., midpoint-radius), min(1., midpoint+radius)]


def restricted(row):
    h = row["max_sweeps"]
    x, u, s, p = [h if row[key] is None else row[key]
                  for key in ("exact_sweep", "U", "S", "post_sweep")]
    initial = row["init_evals"]
    need(0 <= u <= s <= p <= h and 0 <= x <= p, "Restricted event order")
    a, b, c, g = u, s-u, p-s, p-x
    result = dict(zip(METRICS, (initial+(row["n"]+1)*x, initial+(row["n"]+1)*p,
                               u, s, a, b, c, g)))
    need(a+b+c == p and initial+(row["n"]+1)*(a+b+c-g) == result[METRICS[0]],
         "Phase identity")
    return result


def validate(row, planned, manifest):
    need(all(type(row.get(k)) is type(v) and row[k] == v for k, v in planned.items()),
         "Receipt differs from plan")
    need(row["record_sha256"] == digest({k:v for k,v in row.items() if k != "record_sha256"}),
         "Receipt digest")
    need(all(row[k] == manifest[k] for k in ("plan_sha256", "model_sha256")), "Receipt provenance")
    h, t, n, size = (row[k] for k in ("max_sweeps", "sweeps", "n", "T"))
    need(type(t) is int and 0 <= t <= h, "Sweep prefix")
    for event in EVENTS:
        v = row[event]
        need(v is None or (type(v) is int and 0 <= v <= t), "Event prefix: "+event)
    for a,b in (("archive_sweep","front_sweep"),("front_sweep","exact_sweep"),
                ("U","S"),("S","post_sweep"),("exact_sweep","post_sweep")):
        need(row[b] is None or (row[a] is not None and row[a] <= row[b]), "Event ordering")
    x,s,p = (row[k] for k in ("exact_sweep","S","post_sweep"))
    need(not (x is not None and s is not None and x >= s) or p == x, "Post-S first hit")
    need((p == t and row["stop_reason"] == "post_exact") or
         (p is None and t == h and row["stop_reason"] == "sweep_cap"), "Termination")
    expected_initial = 0 if row["init"] == "corner" else n+1
    for key, expected in (("init_evals",expected_initial),("attempts",(n+1)*t),
                          ("comparisons",(n+1)*t*size)):
        need(type(row[key]) is int and row[key] == expected, "Accounting: "+key)
    for key in WORK[:-1]:
        need(type(row[key]) is int and row[key] >= 0, "Negative/noninteger work")
    need(0 <= row["external_changes"] <= row["external_replacements"] <= t*(n+1)*(size-1),
         "External replacements")
    need(size != 1 or row["endpoint_repairs_external"] == 0, "Impossible external repair")
    need(math.isfinite(row["wall_seconds"]) and row["wall_seconds"] >= 0, "Elapsed time")
    for event in ("U","S"):
        for prefix, bound in (("bad_at_",n+1),("max_error_at_",n)):
            value = row[prefix+event]
            need((row[event] is None and value is None) or
                 (row[event] is not None and type(value) is int and 0 <= value <= bound), "Mismatch diagnostic")
    restricted(row)


def archive_bytes(path):
    # Read only regular members into memory; no extraction or path execution.
    with tarfile.open(path, "r:gz") as archive:
        result = {}
        for member in archive:
            need(member.isfile() and member.name not in result, "Unsafe/duplicate archive member")
            result[member.name] = archive.extractfile(member).read()
        return result


def packet(root, name, inputs):
    directory = root / "research/evidence/large-T-20261109" / name
    index = read(directory / "INDEX.json")
    inputs[str((directory / "INDEX.json").relative_to(root))] = sha((directory / "INDEX.json").read_bytes())
    stages = {}
    for entry in index["stages"]:
        path = directory / entry["file"]
        body = path.read_bytes()
        need(sha(body) == entry["sha256"] and len(body) == entry["bytes"], "Packet digest")
        inputs[str(path.relative_to(root))] = sha(body)
        files = archive_bytes(path)
        m = json.loads(files["manifest.json"])
        need(digest(m["plan"]) == m["plan_sha256"] == entry["plan_sha256"], "Packet plan digest")
        need(digest([m["model_version"],m["sources"],m["toolchain"]]) == m["model_sha256"] == entry["model_sha256"],
             "Packet model digest")
        for item in m["plan"]:
            config = {k:v for k,v in item.items() if k not in ("id","seed")}
            token = digest([m["model_version"],entry["stage"],config])
            need(item["id"] == token[:20] and item["seed"] == int(digest(["trial-seed",token])[:16],16),
                 "Original planned seed rule")
        for name_, expected in m["sources"].items():
            need(sha(files["source/"+name_]) == expected == sha((root/name_).read_bytes()), "Frozen model source")
        byid = {p["id"]:p for p in m["plan"]}
        need(len(byid) == len(m["plan"]), "Duplicate planned id")
        rows = {}
        for name_, data in files.items():
            if name_.startswith("rows/"):
                key = Path(name_).stem
                need(key in byid and key not in rows, "Unplanned/duplicate receipt")
                rows[key] = json.loads(data)
                validate(rows[key], byid[key], m)
        need(len(rows) == entry["recorded"] and len(byid)-len(rows) == entry["missing"], "Packet counts")
        stages[entry["stage"]] = (m, rows, json.loads(files["status.json"]))
    return stages


def seeds_inside(value):
    result = set()
    if isinstance(value, dict):
        for key, val in value.items():
            if key == "seed" and type(val) is int:
                result.add(val)
            else:
                result.update(seeds_inside(val))
    elif isinstance(value, list):
        for val in value:
            result.update(seeds_inside(val))
    return result


class Comparator:
    def __init__(self):
        self.count = 0
        self.max_difference = 0.

    def equal(self, actual, published, label):
        self.count += 1
        if actual is None or published is None:
            need(actual is published, label)
        elif isinstance(actual, (list,tuple)):
            need(len(actual) == len(published), label)
            for a,b in zip(actual,published):
                self.equal(a,b,label)
        elif isinstance(actual, (int,float)) and not isinstance(actual,bool):
            delta = abs(actual-published)
            self.max_difference = max(self.max_difference, delta)
            need(delta <= 1e-8, f"{label}: {actual} != {published}")
        else:
            need(actual == published, label)


def cell_summary(items, rows, experiment, stage):
    recorded = [rows[p["id"]] for p in items if p["id"] in rows]
    missing = len(items)-len(recorded)
    p = items[0]
    low = 0 if p["init"] == "corner" else p["n"]+1
    high = low+(p["n"]+1)*p["max_sweeps"]
    values = [restricted(r)["exact_evaluations"] for r in recorded]
    return dict(experiment=experiment, stage=stage, n=p["n"], T=p["T"], factor=p["factor"],
                planned=len(items), observed=sum(r["exact_sweep"] is not None for r in recorded),
                capped=sum(r["exact_sweep"] is None for r in recorded), missing=missing,
                restricted_mean=mean(values) if not missing else None,
                sample_mean_bound_low=(sum(values)+missing*low)/len(items),
                sample_mean_bound_high=(sum(values)+missing*high)/len(items),
                q10=percentile(values,.1) if not missing else None,
                median=percentile(values,.5) if not missing else None,
                q90=percentile(values,.9) if not missing else None)


def phase_summary(records, start, end):
    entered = len(records) if start is None else sum(r[start] is not None for r in records)
    completed = [r[end]-(0 if start is None else r[start]) for r in records if r[end] is not None]
    return dict(entered=entered, completed=len(completed), right_censored_after_entry=entered-len(completed),
                not_entered=len(records)-entered, completed_only_mean=mean(completed),
                completed_only_quantiles=[percentile(completed,p) for p in (.1,.5,.9)] if completed else None,
                selection_conditioned=True)


def bootstrap(records, seed):
    # Count each resampled row's multiplicity, then dot integer metric totals.
    # This differs from the registered analyzer's indexed matrix averaging.
    data = [restricted(r) for r in records]
    n = len(data)
    indices = np.random.Generator(np.random.PCG64(seed)).integers(0,n,size=(10000,n))
    counts = np.asarray([np.bincount(row, minlength=n) for row in indices], dtype=np.int64)
    return {key:(counts @ np.asarray([r[key] for r in data],dtype=np.int64)/n).tolist() for key in METRICS}


def main(root, out):
    out.mkdir(parents=True, exist_ok=True)
    inputs, compare = {}, Comparator()
    git = lambda *args: subprocess.check_output(["git", *args],cwd=root).decode().strip()
    r1, r2 = root/R1, root/R2
    design, manifest = read(r1/"plan.json"), read(r2/"manifest.json")
    for directory in (r1,r2):
        for path in directory.rglob("*"):
            if path.is_file() and "__pycache__" not in path.parts:
                inputs[str(path.relative_to(root))] = sha(path.read_bytes())
    commit = manifest["registration"]["commit"]
    subprocess.run(["git","merge-base","--is-ancestor",commit,"HEAD"],cwd=root,check=True)
    registration_names = set(read(r1/"freeze.json")["files"]) | {"freeze.json","report.md","provenance.json"}
    for name in registration_names:
        body = subprocess.check_output(["git","show",f"{commit}:{R1/name}"],cwd=root)
        need(body == (r1/name).read_bytes(), "Committed registration bytes")
        need(sha(body) == manifest["registration"]["files"][name], "Registered source digest")
    for name, expected in read(r1/"freeze.json")["files"].items():
        need(sha((r1/name).read_bytes()) == expected,"Freeze integrity")
    for name, expected in read(r2/"checksums.json")["files"].items():
        need(sha((r2/name).read_bytes()) == expected,"Round-2 artifact integrity: "+name)
    snapshots = read(r2/"sources.json")
    need(set(snapshots) == set(manifest["sources"]), "Source inventory")
    for name, expected in manifest["sources"].items():
        need(sha(snapshots[name].encode()) == expected,"Snapshot integrity")
    need(manifest["plan"] == design["plan"] and read(r2/"plan.json") == design,"Frozen design copy")
    need(manifest["plan_sha256"] == design["plan_sha256"] == digest(design["plan"]),"Design digest")
    need(manifest["model_sha256"] == digest([manifest["study"],manifest["sources"],manifest["toolchain"]]),
         "Model digest")
    need(sha((root/"scripts/neighborhood_sweep.cpp").read_bytes()) == design["engine_sha256"], "Model preservation")
    # Independently reconstruct the published seed rule and complete serial schedule.
    expected_plan = []
    for stage,n,reps,h in (("smoke",32,2,10742),("main",512,32,38341)):
        for rep in range(reps):
            for t in ((1,23) if rep%2 == 0 else (23,1)):
                config = dict(stage=stage,n=n,T=t,factor=.015625,mutation="bit",noise="bit",init="uniform",
                              reference="observed",max_sweeps=h,rep=rep)
                token = digest([design["study"],"trial",config])
                expected_plan.append(dict(config,id=token[:20],seed=int(digest([design["study"],"seed",token])[:16],16)))
    need(expected_plan == design["plan"],"Reconstructed schedule/seeds")
    planned = {p["id"]:p for p in design["plan"]}
    rows = {}
    for path in sorted((r2/"rows").glob("*.json")):
        need(path.stem in planned,"Unplanned row")
        row = read(path)
        validate(row,planned[path.stem],manifest)
        rows[path.stem] = row
    need(len(rows) == 68,"Published complete run missing receipts")
    smoke = [rows[p["id"]] for p in design["plan"] if p["stage"] == "smoke"]
    need(len(smoke) == 4 and all(r["post_sweep"] is not None for r in smoke),"Smoke gate")
    status = read(r2/"status.json")
    need(status["recorded"] == len(rows) and status["missing_ids"] == [] and status["state"] == "complete",
         "Published terminal status")
    registration_time = git("show","-s","--format=%cI",commit)
    need(dt.datetime.fromisoformat(registration_time) < dt.datetime.fromisoformat(manifest["started_utc"]),
         "Registration timestamp follows sampling")
    campaign, pilot = packet(root,"campaign",inputs), packet(root,"pilot",inputs)
    original_protocol = "research/LARGER_NEIGHBORHOODS_PREREG.md"
    original_commit = git("log","--reverse","--format=%H","--",original_protocol).splitlines()[0]
    original_commit_time = git("show","-s","--format=%cI",original_commit)
    need(subprocess.check_output(["git","show",f"{original_commit}:{original_protocol}"],cwd=root)
         == (root/original_protocol).read_bytes(),"Original registration preserved")
    need(dt.datetime.fromisoformat(original_commit_time) < dt.datetime.fromisoformat(pilot["smoke"][0]["created_utc"]),
         "Original registration chronology")
    old_seeds = {p["seed"] for m,_,_ in campaign.values() for p in m["plan"]}
    pilot_seeds = {p["seed"] for m,_,_ in pilot.values() for p in m["plan"]}
    legacy = set()
    index_path = root/"research/evidence/INDEX.json"
    inputs[str(index_path.relative_to(root))] = sha(index_path.read_bytes())
    for entry in read(index_path)["archives"]:
        path = index_path.parent/entry["archive"]
        need(sha(path.read_bytes()) == entry["sha256"],"Legacy packet hash")
        inputs[str(path.relative_to(root))] = entry["sha256"]
        files = archive_bytes(path)
        for name,expected in entry["member_sha256"].items():
            need(sha(files[name]) == expected,"Legacy member hash")
            if name.endswith(("/manifest.json","/results.json")):
                legacy.update(seeds_inside(json.loads(files[name])))
    new_seeds = {p["seed"] for p in design["plan"]}
    new_main = {p["seed"] for p in design["plan"] if p["stage"] == "main"}
    new_smoke = new_seeds-new_main
    old_main = {p["seed"] for p in campaign["main"][0]["plan"]}
    holdout = {p["seed"] for p in campaign["holdout"][0]["plan"]}
    published_old = old_seeds | pilot_seeds | legacy
    need(pilot_seeds == {p["seed"] for stage in ("smoke","calibrate") for p in campaign[stage][0]["plan"]},
         "Pilot overlap scope")
    need(not (pilot_seeds & (old_main | holdout)),"Pilot inferential overlap")
    groups = [("followup_all","original_all",new_seeds,old_seeds),
              ("followup_main","original_main",new_main,old_main),
              ("followup_all","blocked_holdout",new_seeds,holdout),
              ("followup_all","all_prior_published",new_seeds,published_old),
              ("followup_smoke","followup_main",new_smoke,new_main),
              ("followup_T1","followup_T23",{r["seed"] for r in rows.values() if r["T"]==1},
               {r["seed"] for r in rows.values() if r["T"]==23}),
              ("original_pilot","original_campaign",pilot_seeds,old_seeds)]
    overlaps = [dict(group_a=a,group_b=b,seeds_a=len(x),seeds_b=len(y),intersection=len(x&y),
                     intersection_sha256=digest(sorted(x&y))) for a,b,x,y in groups]
    need(len(new_seeds) == 68 and not (new_seeds & published_old),"Seed reuse")
    need(len(old_seeds) == sum(len(m["plan"]) for m,_,_ in campaign.values()),"Within-campaign seed reuse")
    table(out/"seeds.csv",overlaps)
    stage_counts = {}
    cells = []
    for stage,(m,records,_) in campaign.items():
        stage_counts[stage] = dict(planned=len(m["plan"]),receipts=len(records),
                                  exact=sum(r["exact_sweep"] is not None for r in records.values()),
                                  capped=sum(r["exact_sweep"] is None for r in records.values()),
                                  missing=len(m["plan"])-len(records))
        if stage in ("main","holdout"):
            grouped = collections.defaultdict(list)
            for p in m["plan"]:
                grouped[p["n"],p["T"],p["factor"]].append(p)
            cells.extend(cell_summary(items,records,"original",stage) for _,items in sorted(grouped.items()))
    for stage in ("smoke","main"):
        for t in (1,23):
            items = [p for p in design["plan"] if p["stage"] == stage and p["T"] == t]
            cells.append(cell_summary(items,rows,"followup",stage))
    table(out/"cells.csv",cells)
    old_main_rows = campaign["main"][1]
    cap_rows = [r for r in old_main_rows.values() if r["exact_sweep"] is None]
    need(len(cap_rows) == 1 and cap_rows[0]["id"] == "67178d8d2471ba15457b", "Original cap")
    need(not campaign["holdout"][1] and campaign["holdout"][2]["state"] == "gate_blocked", "Blocked holdout")
    # Recompute every original endpoint row directly, including missing/capped rows.
    config_keys = ("cohort","n","factor","mutation","noise","init","reference","max_sweeps","T")
    with (root/BASE/"campaign/cells.csv").open() as f:
        for pub in csv.DictReader(f):
            m, records, _ = campaign[pub["stage"]]
            items = [p for p in m["plan"] if all(str(p[k]) == pub[k] for k in config_keys)]
            need(bool(items),"Original cell lookup")
            event = {"exact":"exact_sweep","post":"post_sweep","front":"front_sweep","archive":"archive_sweep"}.get(pub["event"],pub["event"])
            chosen = [records[p["id"]] for p in items if p["id"] in records]
            initial = 0 if items[0]["init"] == "corner" else items[0]["n"]+1
            step = items[0]["n"]+1
            h = items[0]["max_sweeps"]
            observed = [initial+step*r[event] for r in chosen if r[event] is not None]
            capped = len(chosen)-len(observed)
            missing = len(items)-len(chosen)
            total = sum(observed)+capped*(initial+step*h)
            actual = dict(planned=len(items),observed=len(observed),at_cap=capped,missing=missing,
                          restricted_mean_lower=(total+missing*initial)/len(items),
                          restricted_mean_upper=(total+missing*(initial+step*h))/len(items))
            if not capped and not missing:
                actual.update(mean_evaluations=mean(observed),q10=percentile(observed,.1),median=percentile(observed,.5),q90=percentile(observed,.9))
            for key,val in actual.items():
                compare.equal(val,float(pub[key]),"Original cells "+key)
    # Audit original phase durations with their actual completed denominators.
    with (root/BASE/"campaign/work.csv").open() as f:
        for pub in csv.DictReader(f):
            m, records, _ = campaign[pub["stage"]]
            items = [p for p in m["plan"] if all(str(p[k]) == pub[k] for k in config_keys)]
            chosen = [records[p["id"]] for p in items if p["id"] in records]
            compare.equal(len(chosen),float(pub["receipts"]),"Original phase receipts")
            for end,start,label in (("U",None,"U"),("S","U","S_minus_U"),("post_sweep","S","phase_II")):
                values = [r[end]-(r[start] if start else 0) for r in chosen if r[end] is not None]
                compare.equal(len(values),float(pub["observed_"+label]),"Original phase denominator")
                expected = pub["mean_observed_"+label+"_sweeps"]
                compare.equal(mean(values),float(expected) if expected else None,"Original phase mean")
    old_arms, old_phase_means = {}, {}
    for t in (1,16):
        selected = [old_main_rows[p["id"]] for p in campaign["main"][0]["plan"]
                    if (p["n"],p["T"],p["factor"]) == (256,t,1/64)]
        old_arms[t] = [restricted(r)["exact_evaluations"] for r in selected]
        old_phase_means[str(t)] = {key:mean([restricted(r)[key] for r in selected]) for key in
                                  ("pre_U_sweeps","U_to_S_sweeps","post_S_sweeps","post_exact_gap_sweeps")}
    old_key = ["main","primary",256,1/64,"bit","bit","uniform","observed",17047,1]
    old_rng = np.random.Generator(np.random.PCG64(int(digest(["large-T-independent-bootstrap-v1",old_key])[:16],16)))
    old_boot = []
    for t in (1,16):
        indices = old_rng.integers(0,24,size=(10000,24))
        old_boot.append([sum(old_arms[t][i] for i in row)/24 for row in indices])
    old_primary = dict(ratio=mean(old_arms[1])/mean(old_arms[16]),
                       nominal_95_ci=interval([a/b for a,b in zip(*old_boot)]))
    with (root/BASE/"campaign/contrasts.csv").open() as f:
        old_pub = next(row for row in csv.DictReader(f) if row["stage"] == "main" and row["role"] == "primary")
    compare.equal(old_primary["ratio"],float(old_pub["mean_ratio"]),"Original ratio")
    compare.equal(old_primary["nominal_95_ci"],[float(old_pub["mean_ci_low"]),float(old_pub["mean_ci_high"])],"Original CI")
    summary = read(r2/"summary.json")
    arms, boots, phase_rows = {}, {}, []
    for t in (1,23):
        records = sorted((r for r in rows.values() if r["stage"] == "main" and r["T"] == t),key=lambda r:r["rep"])
        values = [restricted(r) for r in records]
        expected_seed = int(digest([design["study"],"bootstrap",t])[:16],16)
        need(design["primary"]["inference_seeds"][str(t)] == expected_seed,"Bootstrap seed")
        boots[t] = bootstrap(records,expected_seed)
        arm = dict(planned=32,receipts=len(records),missing=32-len(records),events={},means={},quantiles={},mean_intervals={})
        published = summary["arms"][str(t)]
        for event in EVENTS:
            hits = sum(r[event] is not None for r in records)
            arm["events"][event] = dict(observed=hits,capped=len(records)-hits,missing=32-len(records),
                completion_fraction_bounds=[hits/32,(hits+32-len(records))/32],completion_wilson_95=wilson(hits,32))
            for key,v in arm["events"][event].items():
                compare.equal(v,published["events"][event][key],"Followup event "+key)
        for key in METRICS:
            data = [v[key] for v in values]
            arm["means"][key] = mean(data)
            arm["quantiles"][key] = [percentile(data,p) for p in (.1,.5,.9)]
            arm["mean_intervals"][key] = interval(boots[t][key])
            compare.equal(arm["means"][key],published["restricted_means"][key],"Followup mean "+key)
            compare.equal(arm["quantiles"][key],published["restricted_quantiles_10_50_90"][key],"Followup quantiles "+key)
            compare.equal(arm["mean_intervals"][key],published["restricted_mean_pointwise_95"][key],"Followup mean CI "+key)
        arm["phases"] = {}
        for name,start,end in (("U",None,"U"),("S_minus_U","U","S"),("post_minus_S","S","post_sweep")):
            stats = phase_summary(records,start,end)
            arm["phases"][name] = stats
            for key,v in stats.items():
                compare.equal(v,published["diagnostics_observed_receipts_only"][name][key],"Phase "+name+key)
        arm["work"] = {key:sum(r[key] for r in records) for key in WORK}
        for key,v in arm["work"].items():
            compare.equal(v,published["diagnostics_observed_receipts_only"]["cumulative_work_to_post_or_cap"][key],"Work "+key)
        for key in ("bad_at_U","bad_at_S","max_error_at_U","max_error_at_S"):
            data = [r[key] for r in records if r[key] is not None]
            for k,v in dict(denominator=len(data),mean=mean(data),quantiles=[percentile(data,p) for p in (.1,.5,.9)]).items():
                compare.equal(v,published["diagnostics_observed_receipts_only"][key][k],"Mismatch "+key+k)
        arms[str(t)] = arm
    differences = {}
    for key in METRICS:
        est = arms["1"]["means"][key]-arms["23"]["means"][key]
        ci = interval([a-b for a,b in zip(boots[1][key],boots[23][key])])
        differences[key] = dict(estimate=est,nominal_pointwise_95=ci)
        for field,v in differences[key].items():
            compare.equal(v,summary["diagnostic_differences_T1_minus_T23"][key][field],"Difference "+key)
        phase_rows.append(dict(metric=key,T1_mean=arms["1"]["means"][key],T23_mean=arms["23"]["means"][key],
                               difference=est,ci_low=ci[0],ci_high=ci[1]))
    table(out/"phases.csv",phase_rows)
    primary = dict(ratio=arms["1"]["means"]["exact_evaluations"]/arms["23"]["means"]["exact_evaluations"],
                   nominal_95_ci=interval([a/b for a,b in zip(boots[1]["exact_evaluations"],boots[23]["exact_evaluations"])]))
    primary["decision"] = "favors_T23" if primary["nominal_95_ci"][0] > 1 else "favors_T1" if primary["nominal_95_ci"][1] < 1 else "inconclusive"
    for key,v in primary.items():
        compare.equal(v,summary["primary"][key],"Primary "+key)
    trials = []
    for p in design["plan"]:
        r = rows[p["id"]]
        trials.append({**{k:r[k] for k in ("id","stage","n","T","rep","seed","max_sweeps",*EVENTS)},
                       **restricted(r),"exact_observed":r["exact_sweep"] is not None,"post_observed":r["post_sweep"] is not None,
                       "record_sha256":r["record_sha256"]})
    table(out/"trials.csv",trials)
    exceptions = {"post_S_positive":[r for r in rows.values() if r["stage"] == "main" and restricted(r)["post_S_sweeps"] > 0],
                  "post_exact_gap_positive":[r["id"] for r in rows.values() if r["stage"] == "main" and restricted(r)["post_exact_gap_sweeps"] > 0]}
    for key in ("post_S_positive",):
        exceptions[key] = [{k:r[k] for k in ("id","T","rep","U","S","exact_sweep","post_sweep","bad_at_S","max_error_at_S")} for r in exceptions[key]]
    elapsed_utc = (dt.datetime.fromisoformat(status["ended_utc"])-dt.datetime.fromisoformat(manifest["started_utc"])).total_seconds()
    timing = dict(registration_commit_utc=registration_time,manifest_started_utc=manifest["started_utc"],
                  status_ended_utc=status["ended_utc"],manifest_to_status_seconds=elapsed_utc,
                  invocation_seconds=status["invocation_seconds"],compile_seconds=status["compile_seconds"],
                  loop_seconds=status["measurement_loop_seconds"],engine_seconds_all=sum(r["wall_seconds"] for r in rows.values()),
                  engine_seconds_main=sum(r["wall_seconds"] for r in rows.values() if r["stage"] == "main"),
                  utc_vs_monotonic_start_offset_seconds=status["invocation_seconds"]-elapsed_utc,
                  explanation="START is recorded before imports/registration; started_utc is recorded after those checks. Per-trial timestamps/private invocation log are not published in round 2.")
    result = dict(status="mechanically checked; empirical interpretation remains finite",new_scientific_outcomes=0,
                  dependency_repair_needed=False,registration_commit=commit,plan_sha256=manifest["plan_sha256"],
                  original_registration_commit=original_commit,original_registration_commit_utc=original_commit_time,
                  model_sha256=manifest["model_sha256"],original_stage_counts=stage_counts,original_primary=old_primary,
                  original_primary_phase_means=old_phase_means,
                  original_blocking_receipt={k:cap_rows[0][k] for k in ("id","seed","n","T","factor","max_sweeps","U","S","exact_sweep","post_sweep")},
                  blocked_holdout_mean_bounds=[513,19669446],blocked_holdout_ratio_bounds=[1/38342,38342],
                  original_decision="inconclusive; original holdout remains blocked",followup_primary=primary,
                  followup_arms=arms,followup_differences=differences,phase_identity_max_residual=0,
                  seed_audit=dict(prior_unique=len(published_old),new_unique=len(new_seeds),pairs=overlaps,
                      pilot_overlap_scope="164 reused smoke/calibration seeds only; excluded from both primary effects. Different toolchains do not establish independent streams.",
                      pilot_toolchain=pilot["calibrate"][0]["toolchain"],campaign_toolchain=campaign["calibrate"][0]["toolchain"]),
                  exceptions=exceptions,published_timing=timing,
                  comparison_checks=compare.count,max_absolute_numeric_discrepancy=compare.max_difference,
                  limitations=["Distinct seeds do not prove independent PRNG streams.",
                               "Terminal receipts permit arithmetic/event-order audit, not reconstruction of every transition or unreported execution.",
                               "No new sampling, literature search, asymptotic claim or candidate proof.",
                               "Bootstrap intervals are approximate pointwise; no guarantee against rare tails."])
    dump(out/"audit.json",result)
    dump(out/"inputs.json",dict(files=inputs,format=1,hash_algorithm="sha256 of bytes"))
    print(json.dumps(dict(checks=compare.count,primary=primary,prior_seeds=len(published_old),new_seeds=len(new_seeds),new_outcomes=0)))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo",type=Path,required=True)
    parser.add_argument("--out",type=Path,required=True)
    args = parser.parse_args()
    main(args.repo.resolve(),args.out.resolve())
