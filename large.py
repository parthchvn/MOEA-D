"""
MOEA/D on OneMinMax — NOISELESS (p = 0), one-bit mutation, large neighbourhoods.

Explores the conjectured scaling

    sweeps ~ n + (n/T)·log(1 + n/T),
    evals  ~ n² + (n²/T)·log(1 + n/T).

This relationship is an empirical research hypothesis, not a theorem established
by this repository. Here ``T = 2r+1`` is only the nominal, unclipped interior
cardinality; actual boundary neighborhoods have size ``r+1``.

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
             |x|_1.  With n+1 uniquely targeted subproblems, exact alignment
             itself covers all n+1 front weights; no extra archive phase is
             modeled here.

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


def controlled_streams(seed):
    """Independent initialization, lazy-gate, and direction PCG64 streams."""
    return tuple(np.random.default_rng(child)
                 for child in np.random.SeedSequence(seed).spawn(3))


def controlled_offspring(n, weight, mutation, gate, direction):
    """One-bit direction is drawn even when the lazy gate makes a weight copy."""
    if mutation == "lazy" and gate < 0.5:
        return weight
    return weight + 1 if direction < (n - weight) / n else weight - 1


def run_controlled(n, r, seed, mutation="exact", max_evaluations=None,
                   deadline=None, *, self_loop_broadcast=True, track_phases=False):
    """Canonical cyclic model; observe paired archive and alignment times.

    The archive is passive and contains every initialized/generated weight,
    including rejected offspring. Both first-passage times count initialization
    and are checked after each offspring. Continue past archive completion until
    alignment or censoring. Thus endpoints are paired, not independent trials.

    Paper correspondence: complement its genotype, retain subproblem index j,
    and let its number of zeros equal our number of ones. This preserves the
    ascending cyclic breeder order. Neighborhoods are clipped, not periodic.
    See research/PAPER_COMPARISON.md for the source's apparent min/max typo.
    ``self_loop_broadcast=False`` suppresses only other-recipient replacement
    when the offspring equals the breeder's parent weight. Optional phase
    observers record confirmed-prefix times without drawing randomness. Both
    defaults preserve the original controlled API and seeded return fields.
    """
    if not isinstance(n, (int, np.integer)) or n < 1:
        raise ValueError("n must be a positive integer")
    if not isinstance(r, (int, np.integer)) or not 0 <= r <= n:
        raise ValueError("r must be an integer in [0,n]")
    if mutation not in ("exact", "lazy"):
        raise ValueError("mutation must be exact or lazy")
    if max_evaluations is not None and max_evaluations < n + 1:
        raise ValueError("max_evaluations must include n+1 initialization evaluations")

    evaluations = observation_evaluations = 0
    archive_time = alignment_time = None
    first_hits = [None] * (n + 1) if track_phases else None
    archived = aligned = 0
    self_loops = self_loop_changes = self_loop_targets = 0
    rejected = rejected_new_archive = 0

    def expired():
        return deadline is not None and time.monotonic() >= deadline

    def result(reason):
        payload = dict(
            evaluations=evaluations,
            observation_evaluations=observation_evaluations,
            initialization_evaluations=min(evaluations, n + 1),
            offspring_evaluations=max(0, evaluations - n - 1),
            archive_evaluations=archive_time,
            alignment_evaluations=alignment_time,
            archive_censored=archive_time is None,
            alignment_censored=alignment_time is None,
            censor_reason=reason,
            archive_count=archived,
            aligned_count=aligned,
            self_loop_offspring=self_loops,
            self_loop_recipient_changes=self_loop_changes,
            self_loop_target_acquisitions=self_loop_targets,
            rejected_offspring=rejected,
            rejected_new_archive_weights=rejected_new_archive,
        )
        if track_phases:
            endpoint_time = (max(first_hits[0], first_hits[n])
                             if first_hits[0] is not None and first_hits[n] is not None
                             else None)
            interior = first_hits[1:n]
            interior_time = (max(interior, default=n + 1)
                             if observation_evaluations >= n + 1
                             and all(value is not None for value in interior) else None)
            payload.update(
                target_first_hit_evaluations=list(first_hits),
                last_endpoint_evaluations=endpoint_time,
                interior_completion_evaluations=interior_time,
                alignment_after_endpoints_evaluations=(alignment_time - endpoint_time
                    if alignment_time is not None and endpoint_time is not None else None),
            )
        return payload

    if expired():
        return result("wall_time")
    init_rng, gate_rng, direction_rng = controlled_streams(seed)
    idx = np.arange(n + 1)
    cost = cost_table(n)
    intervals = neighbourhoods(n, r)
    if expired():
        return result("wall_time")
    weights = init_rng.binomial(n, 0.5, size=n + 1).astype(np.int64)
    evaluations = n + 1
    archive = np.zeros(n + 1, dtype=bool)
    archive[weights] = True
    archived = int(archive.sum())
    aligned = int(np.count_nonzero(weights == idx))
    if expired():
        return result("wall_time")
    observation_evaluations = evaluations
    if track_phases:
        for target in np.flatnonzero(weights == idx):
            first_hits[int(target)] = evaluations
    if archived == n + 1:
        archive_time = evaluations
    if aligned == n + 1:
        alignment_time = evaluations
        return result(None)

    while True:
        # Both arrays are consumed for both mutation arms, including lazy copies.
        # Batching by a sweep only prefetches independent uniforms; each offspring
        # still mutates the current (possibly just replaced) incumbent.
        if expired():
            return result("wall_time")
        gates = gate_rng.random(n + 1)
        directions = direction_rng.random(n + 1)
        for breeder in range(n + 1):
            if expired():
                return result("wall_time")
            if max_evaluations is not None and evaluations >= max_evaluations:
                return result("max_evaluations")
            parent = int(weights[breeder])
            offspring = controlled_offspring(
                n, parent, mutation, gates[breeder], directions[breeder])
            evaluations += 1
            new_archive_weight = not archive[offspring]
            if new_archive_weight:
                archive[offspring] = True
                archived += 1
            a, b = intervals[breeder]
            accepted = cost[a:b, offspring] <= cost[idx[a:b], weights[a:b]]
            if offspring == parent and not self_loop_broadcast:
                # Preserve the breeder's comparison, evaluation, archive and
                # cyclic visit; only same-weight offers to other slots stop.
                accepted &= idx[a:b] == breeder
            positions = np.flatnonzero(accepted) + a
            new_target = None
            if offspring == parent:
                self_loops += 1
                self_loop_changes += int(np.count_nonzero(weights[positions] != offspring))
            if positions.size:
                # A weight can newly solve only its own uniquely targeted index.
                if a <= offspring < b and accepted[offspring - a] and weights[offspring] != offspring:
                    aligned += 1
                    new_target = offspring
                    self_loop_targets += int(offspring == parent)
                weights[positions] = offspring
            else:
                rejected += 1
                rejected_new_archive += int(new_archive_weight)
            # A crossing caused by work after the wall deadline remains censored.
            # Earlier observed archive success is retained if alignment censors.
            if expired():
                return result("wall_time")
            observation_evaluations = evaluations
            if track_phases and new_target is not None:
                first_hits[new_target] = evaluations
            if archive_time is None and archived == n + 1:
                archive_time = evaluations
            if aligned == n + 1:
                alignment_time = evaluations
                return result(None)

def run(n, r, seed, track=False, max_sweeps=None, deadline=None):
    level_time = Counter()
    solve = np.full(n + 1, -1, dtype=np.int64)
    J_checks = J_viol = 0

    def result(sweeps, censored, censor_reason):
        return dict(sweeps=sweeps, level_time=level_time, solve=solve,
                    J_checks=J_checks, J_viol=J_viol, censored=censored,
                    censor_reason=censor_reason)

    def deadline_reached():
        return deadline is not None and time.monotonic() >= deadline

    # The deadline covers setup as well as evolutionary updates. Checks after
    # vectorised operations prevent a trial that crosses its deadline during
    # its last operation from being reported as an uncensored success.
    if deadline_reached():
        return result(-1, True, "wall_time")
    rng = np.random.default_rng(seed)
    idx = np.arange(n + 1)
    cost = cost_table(n)
    if deadline_reached():
        return result(-1, True, "wall_time")
    iv = neighbourhoods(n, r)
    if max_sweeps is None:
        max_sweeps = int(80 * n * math.log(n + 2)) + 1000

    w = rng.binomial(n, 0.5, size=n + 1).astype(np.int64)   # state = weights
    if deadline_reached():
        return result(-1, True, "wall_time")
    solve[w == idx] = 0

    if np.array_equal(w, idx):
        if deadline_reached():
            return result(-1, True, "wall_time")
        return result(0, False, None)

    for sweep in range(1, max_sweeps + 1):
        if deadline_reached():
            return result(-1, True, "wall_time")
        if track:
            S = int(w[0]); level_time[S] += 1
            if sweep >= 3:                     # candidate post-burn-in property (J)
                core = np.arange(0, min(r, n) + 1)
                bad  = core[(core >= S) & (w[core] < S)]    # (J) forbids this
                J_checks += 1; J_viol += int(bad.size > 0)

        rmut = rng.random(n + 1)
        if deadline_reached():
            return result(-1, True, "wall_time")
        for k in range(n + 1):                              # sweep: k = 0..n
            if deadline_reached():
                return result(-1, True, "wall_time")
            pw = int(w[k])
            ow = pw + 1 if rmut[k] < (n - pw) / n else pw - 1     # one-bit mutation
            a, b = iv[k]
            acc = cost[a:b, ow] <= cost[idx[a:b], w[a:b]]          # offer to B(k)
            if acc.any():
                pos = np.flatnonzero(acc) + a
                w[pos] = ow
                new = pos[(w[pos] == pos) & (solve[pos] < 0)]
                solve[new] = sweep
            if deadline_reached():
                return result(-1, True, "wall_time")

        if np.array_equal(w, idx):
            if deadline_reached():
                return result(-1, True, "wall_time")
            return result(sweep, False, None)

    return result(-1, True, "max_sweeps")

def mean_sweeps(n, r, reps, seed0=0):
    results = [run(n, r, seed0 + i) for i in range(reps)]
    if any(result["censored"] for result in results):
        raise RuntimeError("mean_sweeps cannot average censored trials")
    v = [result["sweeps"] for result in results]
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
    ax[0].set_ylabel("sweeps / n");        ax[0].set_title(r"flat is consistent with linear sweeps")
    ax[1].set_ylabel("sweeps / (n ln n)"); ax[1].set_title(r"flat is consistent with $n\log n$ sweeps")
    for a in ax:
        a.set_xlabel("n"); a.set_xscale("log"); a.grid(alpha=.3); a.legend(fontsize=8)
    fig.suptitle("Noiseless MOEA/D: exploratory scaling diagnostics")
    fig.tight_layout(); fig.savefig("fig1_scaling.png", dpi=160); plt.close(fig)


# ------------------------------------- 2. T-dependence at fixed n vs the law
def exp_T(n=400, reps=6):
    rs = [0, 1, 2, 4, 8, 16, 32, 64, 128, n]
    meas, err = [], []
    for r in rs:
        m, s = mean_sweeps(n, r, reps, 5000 + 17 * r)
        meas.append(m); err.append(s / math.sqrt(reps))
        sizes = [b - a for a, b in neighbourhoods(n, r)]
        print(f"  r={r:>4}, |B|={min(sizes):>3}..{max(sizes):<3}: "
              f"{m:8.1f}   ({m/n:5.2f} n)", flush=True)
    meas = np.array(meas)

    Ts   = np.array([min(n + 1, 2 * r + 1) for r in rs], float)
    X    = np.column_stack([np.full_like(Ts, n), (n / Ts) * np.log1p(n / Ts)])
    coef, *_ = np.linalg.lstsq(X, meas, rcond=None)          # a·n + b·(n/T)log(1+n/T)
    print(f"  fit: sweeps = {coef[0]:.2f}*n + {coef[1]:.2f}*(n/T)*log(1+n/T)")

    fig, ax = plt.subplots(figsize=(7.2, 4.8))
    ax.errorbar(Ts, meas, yerr=err, fmt="o", ms=6, capsize=3, label="measured")
    ax.plot(Ts, X @ coef, "-", lw=2,
            label=rf"${coef[0]:.2f}n + {coef[1]:.2f}\frac{{n}}{{T}}\log(1+\frac{{n}}{{T}})$")
    ax.axhline(coef[0] * n, ls="--", c="gray", label="fitted linear term")
    ax.axvline(math.log(n), ls=":", c="red",  label=r"conjectured $T=\log n$ threshold")
    ax.set_xscale("log"); ax.set_yscale("log")
    ax.set_xlabel("nominal interior cardinality min(n+1, 2r+1)")
    ax.set_ylabel("sweeps"); ax.set_title(f"n={n}, p=0; diagnostic fit, not a theorem")
    ax.grid(alpha=.3, which="both"); ax.legend(fontsize=8)
    fig.tight_layout(); fig.savefig("fig2_T_dependence.png", dpi=160); plt.close(fig)


# -------------------------- 3. endpoint level profile vs. a heuristic
def exp_levels(n=400, rs=(1, 8, 64), reps=4):
    fig, ax = plt.subplots(figsize=(7.6, 4.8))
    for c, r in enumerate(rs):
        agg = Counter()
        for i in range(reps):
            agg.update(run(n, r, 9000 + 31 * r + i, track=True)["level_time"])
        S  = np.array(sorted(s for s in agg if 1 <= s <= n // 3))
        ts = np.array([agg[s] / reps for s in S])
        heuristic = np.array([max(1.0, n / ((min(r, s) + 1) * s)) for s in S])
        ax.plot(S, ts,  ".", ms=3, alpha=.45, color=f"C{c}", label=f"measured, r={r}")
        ax.plot(S, heuristic, "-", lw=2, color=f"C{c}",
                label=rf"heuristic $\max\{{1,\ n/((\min(r,S)+1)S)\}}$, r={r}")
    ax.set_xscale("log"); ax.set_yscale("log")
    ax.set_xlabel("endpoint level  S = w[0]"); ax.set_ylabel("sweeps spent at level S")
    ax.set_title(f"n={n}: endpoint level time versus a conjectured heuristic")
    ax.grid(alpha=.3, which="both"); ax.legend(fontsize=7, ncol=2)
    fig.tight_layout(); fig.savefig("fig3_levels.png", dpi=160); plt.close(fig)


# ---------------- 4. candidate post-burn-in property (J) and first-hit profile
def exp_invariant_and_profile(n=200, rs=(1, 4, 25), reps=4):
    print("  candidate post-burn-in property (J): l <= r and l >= S ==> w[l] >= S")
    fig, ax = plt.subplots(figsize=(7.6, 4.6))
    for r in rs:
        chk = vio = 0; prof = np.zeros(n + 1)
        for i in range(reps):
            R = run(n, r, 13000 + 7 * r + i, track=True)
            chk += R["J_checks"]; vio += R["J_viol"]; prof += R["solve"]
        prof /= reps
        print(f"    r={r:>3}:  {chk:6d} checks,  {vio} violations")
        ax.plot(np.arange(n + 1), prof, lw=1.4, label=f"r={r}")
    ax.set_xlabel("subproblem k"); ax.set_ylabel("first sweep with w[k] = k")
    ax.set_title(f"n={n}: exploratory first-hit profile by subproblem")
    ax.grid(alpha=.3); ax.legend()
    fig.tight_layout(); fig.savefig("fig4_solve_profile.png", dpi=160); plt.close(fig)


if __name__ == "__main__":
    t0 = time.time()
    print("=== 1. scaling in n ===");                  exp_scaling()
    print("=== 2. T-dependence, n=400 ===");           exp_T(400)
    print("=== 3. endpoint level profile, n=400 ==="); exp_levels(400)
    print("=== 4. candidate property (J) + profile, n=200 ==="); exp_invariant_and_profile(200)
    print(f"\ndone in {time.time()-t0:.0f}s -> fig1..fig4 .png")
