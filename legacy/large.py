"""
MOEA/D on OneMinMax — NOISELESS (p = 0), one-bit mutation, large neighbourhoods.

Reproduces the law     sweeps = Theta( n + (n/T)·log(1 + n/T) )
                        evals = Theta( n² + (n²/T)·log(1 + n/T) )
i.e. Theta(n² log n) for T = O(1), and Theta(n²) for T = Omega(log n).

Model
-----
  OneMinMax(x) = (|x|_1, n-|x|_1); n+1 subproblems; Tchebycheff scalarisation
  w.r.t. the IDEAL reference point z* = (n,n).  Then the scalar value of a point
  of Hamming weight w for subproblem j is

      phi_j(w) = max{ (j/n)(n-w),  ((n-j)/n)·w }

  — V-shaped, strictly monotone on each branch, unique minimiser j.
  Stored unnormalised as cost[j,w] = max( j(n-w), (n-j)w ).

  One-bit mutation.  The offspring bred at k is offered to EVERY j in B(k)
  and accepted iff phi_j does not increase ("<=", ties accepted).

  p = 0  =>  evaluations are exact  =>  stored value == true value always
         =>  the ENTIRE state is the weight vector w[0..n].  This is exact,
             not an approximation: mutation and selection see x only through
             |x|_1.  It is also why there is no Phase II at p=0.

  Runtime in SWEEPS (one sweep = n+1 evaluations).

Neighbourhood caveat
--------------------
  Use ODD T = 2r+1 with genuine symmetric intervals.  A fixed-width *shifted*
  window (common in implementations) breaks j in B(k) <=> k in B(j), and at
  T=2 silently disconnects subproblem 0 from every breeder but itself — which
  destroys the entire speed-up.
"""

import math, time
from collections import Counter
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np


# ------------------------------------------------------------------ core
def cost_table(n):
    idx = np.arange(n + 1)
    return np.maximum(idx[:, None] * (n - idx)[None, :],
                      (n - idx)[:, None] * idx[None, :]).astype(np.int64)

def neighbourhoods(n, r):                      # B(k) = {j : |j-k| <= r}
    return [(max(0, k - r), min(n + 1, k + r + 1)) for k in range(n + 1)]

def run(n, r, seed, track=False, max_sweeps=None):
    rng  = np.random.default_rng(seed)
    idx  = np.arange(n + 1)
    cost = cost_table(n)
    iv   = neighbourhoods(n, r)
    if max_sweeps is None:
        max_sweeps = int(80 * n * math.log(n + 2)) + 1000

    w = rng.binomial(n, 0.5, size=n + 1).astype(np.int64)   # state = weights

    solve = np.full(n + 1, -1, dtype=np.int64); solve[w == idx] = 0
    level_time = Counter(); J_checks = J_viol = 0

    for sweep in range(1, max_sweeps + 1):
        if np.array_equal(w, idx):
            return dict(sweeps=sweep - 1, level_time=level_time, solve=solve,
                        J_checks=J_checks, J_viol=J_viol, censored=False)
        if track:
            S = int(w[0]); level_time[S] += 1
            if sweep >= 3:                                  # invariant (J)
                core = np.arange(0, min(r, n) + 1)
                bad  = core[(core >= S) & (w[core] < S)]    # (J) forbids this
                J_checks += 1; J_viol += int(bad.size > 0)

        rmut = rng.random(n + 1)
        for k in range(n + 1):                              # sweep: k = 0..n
            pw = int(w[k])
            ow = pw + 1 if rmut[k] < (n - pw) / n else pw - 1     # one-bit mutation
            a, b = iv[k]
            acc = cost[a:b, ow] <= cost[idx[a:b], w[a:b]]          # offer to B(k)
            if acc.any():
                pos = np.flatnonzero(acc) + a
                w[pos] = ow
                new = pos[(w[pos] == pos) & (solve[pos] < 0)]
                solve[new] = sweep

    return dict(sweeps=-1, level_time=level_time, solve=solve,
                J_checks=J_checks, J_viol=J_viol, censored=True)

def mean_sweeps(n, r, reps, seed0=0):
    v = [run(n, r, seed0 + i)["sweeps"] for i in range(reps)]
    return float(np.mean(v)), float(np.std(v))


# ------------------------------------------------------- 1. scaling in n
def exp_scaling():
    ns   = [50, 100, 200, 400, 800]
    reps = {50: 16, 100: 12, 200: 10, 400: 6, 800: 4}
    cfg  = [("T=1", lambda n: 0), ("T=3", lambda n: 1), ("T=9", lambda n: 4),
            ("T~2*sqrt(n)", lambda n: int(math.sqrt(n))), ("T=n+1", lambda n: n)]
    res = {}
    for i, (lab, rf) in enumerate(cfg):
        res[lab] = [mean_sweeps(n, rf(n), reps[n], 1000 + 137 * i)[0] for n in ns]
        print(f"  {lab:>12}: " + "  ".join(f"{v:8.0f}" for v in res[lab]), flush=True)

    fig, ax = plt.subplots(1, 2, figsize=(12, 4.6))
    for lab, ys in res.items():
        ax[0].plot(ns, [y / n for y, n in zip(ys, ns)], "o-", label=lab)
        ax[1].plot(ns, [y / (n * math.log(n)) for y, n in zip(ys, ns)], "o-", label=lab)
    ax[0].set_ylabel("sweeps / n");        ax[0].set_title(r"flat $\Rightarrow\ \Theta(n)$")
    ax[1].set_ylabel("sweeps / (n ln n)"); ax[1].set_title(r"flat $\Rightarrow\ \Theta(n\log n)$")
    for a in ax:
        a.set_xlabel("n"); a.set_xscale("log"); a.grid(alpha=.3); a.legend(fontsize=8)
    fig.suptitle("Noiseless MOEA/D: T=1 is Θ(n log n); large T is Θ(n)")
    fig.tight_layout(); fig.savefig("fig1_scaling.png", dpi=160); plt.close(fig)


# ------------------------------------- 2. T-dependence at fixed n vs the law
def exp_T(n=400, reps=6):
    rs = [0, 1, 2, 4, 8, 16, 32, 64, 128, n]
    meas, err = [], []
    for r in rs:
        m, s = mean_sweeps(n, r, reps, 5000 + 17 * r)
        meas.append(m); err.append(s / math.sqrt(reps))
        print(f"  T={2*r+1:>4}: {m:8.1f}   ({m/n:5.2f} n)", flush=True)
    meas = np.array(meas)

    Ts   = np.array([2 * r + 1 for r in rs], float)
    X    = np.column_stack([np.full_like(Ts, n), (n / Ts) * np.log1p(n / Ts)])
    coef, *_ = np.linalg.lstsq(X, meas, rcond=None)          # a·n + b·(n/T)log(1+n/T)
    print(f"  fit: sweeps = {coef[0]:.2f}*n + {coef[1]:.2f}*(n/T)*log(1+n/T)")

    fig, ax = plt.subplots(figsize=(7.2, 4.8))
    ax.errorbar(Ts, meas, yerr=err, fmt="o", ms=6, capsize=3, label="measured")
    ax.plot(Ts, X @ coef, "-", lw=2,
            label=rf"${coef[0]:.2f}n + {coef[1]:.2f}\frac{{n}}{{T}}\log(1+\frac{{n}}{{T}})$")
    ax.axhline(coef[0] * n, ls="--", c="gray", label=r"$\Theta(n)$ floor")
    ax.axvline(math.log(n), ls=":", c="red",  label=r"$T=\log n$ (saturation)")
    ax.set_xscale("log"); ax.set_yscale("log")
    ax.set_xlabel("neighbourhood size T"); ax.set_ylabel("sweeps"); ax.set_title(f"n={n}, p=0")
    ax.grid(alpha=.3, which="both"); ax.legend(fontsize=8)
    fig.tight_layout(); fig.savefig("fig2_T_dependence.png", dpi=160); plt.close(fig)


# --------------------------------- 3. endpoint level profile vs. theory
def exp_levels(n=400, rs=(1, 8, 64), reps=4):
    fig, ax = plt.subplots(figsize=(7.6, 4.8))
    for c, r in enumerate(rs):
        agg = Counter()
        for i in range(reps):
            agg.update(run(n, r, 9000 + 31 * r + i, track=True)["level_time"])
        S  = np.array(sorted(s for s in agg if 1 <= s <= n // 3))
        ts = np.array([agg[s] / reps for s in S])
        pred = np.array([max(1.0, n / ((min(r, s) + 1) * s)) for s in S])   # theory
        ax.plot(S, ts,  ".", ms=3, alpha=.45, color=f"C{c}", label=f"measured, T={2*r+1}")
        ax.plot(S, pred, "-", lw=2, color=f"C{c}",
                label=rf"$\max\{{1,\ n/(\min(r,S)S)\}}$, T={2*r+1}")
    ax.set_xscale("log"); ax.set_yscale("log")
    ax.set_xlabel("endpoint level  S = w[0]"); ax.set_ylabel("sweeps spent at level S")
    ax.set_title(f"n={n}: time at each endpoint level vs. theory\n"
                 "the Ω(n) term lives at S=O(1); the log term at S > r")
    ax.grid(alpha=.3, which="both"); ax.legend(fontsize=7, ncol=2)
    fig.tight_layout(); fig.savefig("fig3_levels.png", dpi=160); plt.close(fig)


# ----------------------------- 4. invariant (J), and where the time goes
def exp_invariant_and_profile(n=200, rs=(1, 4, 25), reps=4):
    print("  invariant (J):   l <= r  and  l >= S   ==>   w[l] >= S")
    fig, ax = plt.subplots(figsize=(7.6, 4.6))
    for r in rs:
        chk = vio = 0; prof = np.zeros(n + 1)
        for i in range(reps):
            R = run(n, r, 13000 + 7 * r + i, track=True)
            chk += R["J_checks"]; vio += R["J_viol"]; prof += R["solve"]
        prof /= reps
        print(f"    T={2*r+1:>3}:  {chk:6d} checks,  {vio} violations")
        ax.plot(np.arange(n + 1), prof, lw=1.4, label=f"T={2*r+1}")
    ax.set_xlabel("subproblem k"); ax.set_ylabel("first sweep with w[k] = k")
    ax.set_title(f"n={n}: where the time goes — the interior is instant, "
                 "the runtime is the two endpoints")
    ax.grid(alpha=.3); ax.legend()
    fig.tight_layout(); fig.savefig("fig4_solve_profile.png", dpi=160); plt.close(fig)


if __name__ == "__main__":
    t0 = time.time()
    print("=== 1. scaling in n ===");                  exp_scaling()
    print("=== 2. T-dependence, n=400 ===");           exp_T(400)
    print("=== 3. endpoint level profile, n=400 ==="); exp_levels(400)
    print("=== 4. invariant (J) + profile, n=200 ==="); exp_invariant_and_profile(200)
    print(f"\ndone in {time.time()-t0:.0f}s -> fig1..fig4 .png")
