#!/usr/bin/env python3
"""Analysis-only reporting, plot and separate arithmetic audit of frozen receipts.

No engine calls. The published round-1 analysis is imported from the run snapshot.
"""
import argparse
import collections
import csv
import hashlib
import importlib
import json
import math
import os
from pathlib import Path
import sys
import tempfile
import time

for name in ("OPENBLAS_NUM_THREADS", "OMP_NUM_THREADS", "MKL_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ[name] = "1"
os.environ.setdefault("MPLCONFIGDIR", str(Path(tempfile.gettempdir()) / "round2-mpl"))
import numpy as np

ROUND1 = "research/reports/large-T-20261109/followup/round-0001"


def write_json(path, value):
    path.write_text(json.dumps(value, indent=2, sort_keys=True, allow_nan=False)+"\n")


def write_csv(path, rows, fields=None):
    fields = list(rows[0]) if fields is None else fields
    with path.open("w", newline="") as handle:
        writer=csv.DictWriter(handle, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def scalar_values(r):
    """Separate scalar arithmetic; deliberately does not call analysis.vector."""
    h=r["max_sweeps"]
    x,u,s,p=(h if r[k] is None else r[k] for k in ("exact_sweep","U","S","post_sweep"))
    return dict(exact_evaluations=(r["n"]+1)*(1+x), post_evaluations=(r["n"]+1)*(1+p),
                U_sweeps=u, S_sweeps=s, pre_U_sweeps=u, U_to_S_sweeps=s-u,
                post_S_sweeps=p-s, post_exact_gap_sweeps=p-x)


def audit_arithmetic(rows, summary, design):
    """Recompute the frozen mean/quantile/bootstrap calculation from raw scalars.

    This is a separate implementation by the same agent, not an independent review.
    """
    checks=0
    def equal(actual, expected):
        nonlocal checks
        np.testing.assert_allclose(actual, expected, rtol=0, atol=1e-8)
        checks+=int(np.size(actual))
    vectors={}
    residuals=[]
    for key,r in rows.items():
        v=scalar_values(r)
        h=r["max_sweeps"]
        p=h if r["post_sweep"] is None else r["post_sweep"]
        residuals.append(v["pre_U_sweeps"]+v["U_to_S_sweeps"]+v["post_S_sweeps"]-p)
        residuals.append((r["n"]+1)*(1+v["pre_U_sweeps"]+v["U_to_S_sweeps"]+v["post_S_sweeps"]-v["post_exact_gap_sweeps"])-v["exact_evaluations"])
        equal(residuals[-2:],[0,0])
        vectors[key]=v
    boot,means={},{}
    scalar_metrics=list(next(iter(vectors.values()))) if vectors else []
    for T in (1,23):
        items=sorted([r for r in design["plan"] if r["stage"]=="main" and r["T"]==T],key=lambda r:r["rep"])
        observed=[rows[r["id"]] for r in items if r["id"] in rows]
        arm=summary["arms"][str(T)]
        equal([len(observed),len(items)-len(observed)],[arm["receipts"],arm["missing"]])
        for event in ("exact_sweep","front_sweep","archive_sweep","U","S","post_sweep"):
            equal(sum(r[event] is not None for r in observed),arm["events"][event]["observed"])
        if len(observed)!=len(items):
            continue
        N=len(items)
        indices=np.random.Generator(np.random.PCG64(design["primary"]["inference_seeds"][str(T)])).integers(0,N,size=(10000,N))
        boot[T],means[T]={},{}
        for metric in scalar_metrics:
            data=np.asarray([vectors[r["id"]][metric] for r in observed],dtype=np.int64)
            means[T][metric]=sum(int(v) for v in data)/N
            boot[T][metric]=np.sum(data[indices],axis=1)/N
            equal(means[T][metric],arm["restricted_means"][metric])
            equal(np.quantile(data,[.1,.5,.9],method="linear"),arm["restricted_quantiles_10_50_90"][metric])
            equal(np.quantile(boot[T][metric],[.025,.975],method="linear"),arm["restricted_mean_pointwise_95"][metric])
    if len(boot)==2:
        equal(means[1]["exact_evaluations"]/means[23]["exact_evaluations"],summary["primary"]["ratio"])
        equal(np.quantile(boot[1]["exact_evaluations"]/boot[23]["exact_evaluations"],[.025,.975],method="linear"),summary["primary"]["nominal_95_ci"])
        for metric in scalar_metrics:
            d=summary["diagnostic_differences_T1_minus_T23"][metric]
            equal(means[1][metric]-means[23][metric],d["estimate"])
            equal(np.quantile(boot[1][metric]-boot[23][metric],[.025,.975],method="linear"),d["nominal_pointwise_95"])
    else:
        assert summary["primary"]["ratio"] is None and summary["primary"]["nominal_95_ci"] is None
    # Histograms retain rare values hidden by the 10th/50th/90th percentiles.
    distributions={}
    for T in (1,23):
        selected=[r for r in rows.values() if r["stage"]=="main" and r["T"]==T]
        distributions[str(T)]={key:dict(sorted(collections.Counter(str(r[key]) for r in selected).items()))
                              for key in ("bad_at_U","max_error_at_U","bad_at_S","max_error_at_S",
                                          "endpoint_repairs_own","endpoint_repairs_external")}
        distributions[str(T)]["post_S_occupancy"]=dict(sorted(collections.Counter(str(scalar_values(r)["post_S_sweeps"]) for r in selected).items()))
    return dict(status="mechanically checked", scalar_numeric_checks=checks,
                max_absolute_identity_residual=max(map(abs,residuals),default=0),
                arithmetic_implementation="separate scalar/integers implementation, same agent",
                histograms=distributions)


def make_plot(out, rows, summary, design):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    colors={1:"#2463a2",23:"#cb5b28"}
    plt.rcParams.update({"font.size":10,"axes.spines.top":False,"axes.spines.right":False,
                         "axes.titlesize":12,"axes.labelsize":10,"font.family":"DejaVu Sans"})
    fig, axes=plt.subplots(2,2,figsize=(12,8.3),layout="constrained")
    ax=axes[0,0]
    for T in (1,23):
        selected=[r for r in rows.values() if r["stage"]=="main" and r["T"]==T]
        vals=np.sort([scalar_values(r)["exact_evaluations"] for r in selected])/1e6
        arm=summary["arms"][str(T)]
        if len(vals):
            ax.step(np.r_[0,vals],np.r_[0,np.arange(1,len(vals)+1)/arm["planned"]],where="post",color=colors[T],label=f"T={T} ({len(vals)}/32 receipts)")
            caps=[scalar_values(r)["exact_evaluations"]/1e6 for r in selected if r["exact_sweep"] is None]
            if caps: ax.plot(caps,[len(vals)/32]*len(caps),"x",color=colors[T])
    ax.set(title="A  Restricted first-exact cost: empirical CDF",xlabel="Evaluations, including initialization (millions)",ylabel="Fraction of 32 planned trials",ylim=(0,1.04))
    ax.legend(loc="lower right",frameon=False)
    ax.grid(alpha=.18)
    ax=axes[0,1]
    for y,T in enumerate((23,1)):
        arm=summary["arms"][str(T)]
        if "restricted_means" in arm:
            m=arm["restricted_means"]["exact_evaluations"]/1e6
            lo,hi=np.array(arm["restricted_mean_pointwise_95"]["exact_evaluations"])/1e6
            ax.errorbar(m,y,xerr=[[m-lo],[hi-m]],fmt="o",color=colors[T],capsize=5,markersize=8)
            ax.annotate(f"{m:.3f} [{lo:.3f}, {hi:.3f}]",(m,y),xytext=(0,16),textcoords="offset points",ha="center",color=colors[T])
    ax.set(title="B  Restricted means and nominal 95% intervals",xlabel="Mean evaluations (millions)",yticks=[0,1],yticklabels=["T=23","T=1"],ylim=(-.6,1.6))
    ax.grid(axis="x",alpha=.18)
    primary=summary["primary"]
    if primary["ratio"] is not None:
        lo,hi=primary["nominal_95_ci"]
        ax.text(.5,.03,f"Ratio T=1 / T=23: {primary['ratio']:.3f} [{lo:.3f}, {hi:.3f}]",ha="center",transform=ax.transAxes,fontweight="bold")
    else:
        ax.text(.5,.03,"Partial work: primary estimate and CI suppressed",ha="center",transform=ax.transAxes)
    ax=axes[1,0]
    diffs=summary.get("diagnostic_differences_T1_minus_T23",{})
    for y,key in enumerate(("U_to_S_sweeps","pre_U_sweeps")):
        if key in diffs:
            d=diffs[key]; m=d["estimate"]; lo,hi=d["nominal_pointwise_95"]
            ax.errorbar(m,y,xerr=[[m-lo],[hi-m]],fmt="o",color="#3f6061",capsize=5,markersize=7)
            ax.annotate(f"{m:,.1f} [{lo:,.1f}, {hi:,.1f}]",(m,y),xytext=(0,17),textcoords="offset points",ha="center")
    ax.axvline(0,color=".6",lw=1)
    ax.set(title="C  Descriptive phase savings: T=1 minus T=23",xlabel="Difference in mean occupied sweeps",yticks=[0,1],yticklabels=["Between U and S","Before U"],ylim=(-.6,1.6),xlim=(-200,5800))
    ax.grid(axis="x",alpha=.18)
    ax.text(.5,.03,"U: ideal reference; S: ideal reference + all stored targets",ha="center",transform=ax.transAxes,fontsize=9)
    ax=axes[1,1]
    for y,T in enumerate((23,1)):
        selected=[r for r in rows.values() if r["stage"]=="main" and r["T"]==T]
        counts=collections.Counter(scalar_values(r)["post_S_sweeps"] for r in selected)
        for value,count in counts.items():
            ax.scatter([value],[y],s=60+count*6,color=colors[T])
            ax.annotate(f"{count}/32",(value,y),xytext=(0,14),textcoords="offset points",ha="center",color=colors[T])
        arm=summary["arms"][str(T)]
        if "restricted_means" in arm:
            m=arm["restricted_means"]["post_S_sweeps"]
            lo,hi=arm["restricted_mean_pointwise_95"]["post_S_sweeps"]
            ax.text(.4,y-.25,f"Mean {m:g}; 95% interval [{lo:g}, {hi:g}]",color=colors[T],fontsize=9)
    ax.set(title="D  Time after S: retain the rare delay",xlabel="Occupied post-S sweeps through P or H",yticks=[0,1],yticklabels=["T=23","T=1"],ylim=(-.6,1.6),xlim=(-.5,4.6),xticks=range(5))
    ax.grid(axis="x",alpha=.18)
    fig.suptitle("Independent n=512 low-noise study · 32 trajectories per arm",fontsize=15,fontweight="bold")
    fig.supxlabel("p=1/32,768; H=38,341 sweeps (19.669446 million evaluations).\nPointwise 95% percentile bootstrap, 10,000 resamples; no simultaneous coverage claim.",fontsize=10)
    fig.savefig(out/"results.png",dpi=180,metadata={"Software":"matplotlib"})
    plt.close(fig)


def summarize(run_dir,out):
    start=time.monotonic()
    out.mkdir(parents=True,exist_ok=True)
    sys.path.insert(0,str(run_dir/"source"/ROUND1))
    analysis=importlib.import_module("analysis")
    plan=importlib.import_module("plan")
    rows=analysis.load_run(run_dir)
    design=plan.build_plan()
    summary=analysis.analyze(rows,design)
    write_json(out/"summary.json",summary)
    audit=audit_arithmetic(rows,summary,design)
    write_json(out/"arithmetic.json",audit)
    table=[]
    derived=list(scalar_values(next(iter(rows.values())))) if rows else list(analysis.METRICS)
    for order,item in enumerate(design["plan"]):
        r=rows.get(item["id"])
        entry=dict(order=order,**(r if r else item),receipt_status="missing" if r is None else r["stop_reason"])
        entry.update({k:None for k in derived} if r is None else scalar_values(r))
        entry["logical_comparisons_through_first_exact"]=None if r is None or r["exact_sweep"] is None else (r["n"]+1)*r["T"]*r["exact_sweep"]
        table.append(entry)
    fields=list(dict.fromkeys(k for r in table for k in r))
    write_csv(out/"trials.csv",table,fields)
    cells=[]
    for T in (1,23):
        a=summary["arms"][str(T)]; e=a["events"]["exact_sweep"]
        m=a.get("restricted_means",{}); q=a.get("restricted_quantiles_10_50_90",{}).get("exact_evaluations",[None]*3)
        ci=a.get("restricted_mean_pointwise_95",{}).get("exact_evaluations",[None]*2)
        cells.append(dict(n=512,T=T,factor=1/64,planned=a["planned"],observed=e["observed"],capped=e["capped"],missing=e["missing"],
                          restricted_mean_evaluations=m.get("exact_evaluations"),mean_ci_low=ci[0],mean_ci_high=ci[1],q10=q[0],median=q[1],q90=q[2],
                          completion_wilson_low=(e["completion_wilson_95"] or [None,None])[0],completion_wilson_high=(e["completion_wilson_95"] or [None,None])[1]))
    write_csv(out/"cells.csv",cells)
    phases=[]
    for key in ("pre_U_sweeps","U_to_S_sweeps","post_S_sweeps","post_exact_gap_sweeps"):
        d=summary.get("diagnostic_differences_T1_minus_T23",{}).get(key,{})
        ci=d.get("nominal_pointwise_95",[None,None])
        phases.append(dict(metric=key,T1_mean=summary["arms"]["1"].get("restricted_means",{}).get(key),
                           T23_mean=summary["arms"]["23"].get("restricted_means",{}).get(key),difference=d.get("estimate"),difference_ci_low=ci[0],difference_ci_high=ci[1]))
    write_csv(out/"phases.csv",phases)
    make_plot(out,rows,summary,design)
    return dict(analysis_and_plot_seconds=time.monotonic()-start,receipt_count=len(rows),arithmetic_checks=audit["scalar_numeric_checks"])


if __name__=="__main__":
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run",required=True,type=Path)
    parser.add_argument("--out",required=True,type=Path)
    args=parser.parse_args()
    print(json.dumps(summarize(args.run.resolve(),args.out.resolve()),indent=2))
