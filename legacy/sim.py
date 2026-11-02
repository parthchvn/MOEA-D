#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Feb 23 18:16:27 2026

@author: parth
"""

import numpy as np
import matplotlib.pyplot as plt
import time


# ---------- One-bit prior noise on k = sum(x) ----------
def noisy_k(x: np.ndarray, p: float, rng: np.random.Generator) -> int:
    k = int(x.sum())
    n = x.size
    if rng.random() < p:
        j = rng.integers(n)
        return k - 1 if x[j] == 1 else k + 1
    return k


# ---------- Scalarization: optimum for subproblem i at k=i ----------
def g_from_k(k_noisy: int, i: int) -> int:
    return abs(k_noisy - i)


# ---------- Neighborhoods ----------
def build_neighborhoods(N: int, T: int):
    """
    1D weights => natural neighbors are adjacent indices.
    We build B(i) of size T including i, then add neighbors outward.
    For ties (left/right), we alternate order based on parity of i for balance.
    """
    assert 1 <= T <= N + 1
    neigh = []
    for i in range(N + 1):
        B = [i]
        step = 1
        while len(B) < T:
            cand = [(i + step), (i - step)] if (i % 2 == 0) else [(i - step), (i + step)]
            for j in cand:
                if 0 <= j <= N and j not in B:
                    B.append(j)
                    if len(B) == T:
                        break
            step += 1
        neigh.append(B)
    return neigh


# ---------- Stopping conditions (on TRUE values) ----------
def front_covered(pop) -> bool:
    n = pop[0].size
    weights = {int(ind.sum()) for ind in pop}
    return weights == set(range(n + 1))


def aligned_optima(pop) -> bool:
    # requires N=n, i.e., pop has length n+1, and target for i is weight i
    return all(int(pop[i].sum()) == i for i in range(len(pop)))


# ---------- Simulation: MOEA/D with neighborhood size T ----------
def simulate_moead(
    n: int,
    p: float,
    T: int,
    stop_rule: str,            # "front" or "aligned"
    max_gens: int | None = None,
    rng: np.random.Generator | None = None,
):
    if rng is None:
        rng = np.random.default_rng()

    N = n
    B = build_neighborhoods(N, T)

    if max_gens is None:
        max_gens = int(50 * n * n * np.log(n + 2)) + 1

    pop = [rng.integers(0, 2, size=n, dtype=np.int8) for _ in range(N + 1)]

    # store last accepted noisy scalar value per subproblem
    stored_g = np.empty(N + 1, dtype=int)
    total_evals = 0

    # initial evaluation: each subproblem evaluates its own incumbent once
    for i in range(N + 1):
        kN = noisy_k(pop[i], p, rng)
        stored_g[i] = g_from_k(kN, i)
        total_evals += 1

    # initial stop check
    if stop_rule == "front" and front_covered(pop):
        return {"converged": True, "total_gens": 0, "total_evals": total_evals}
    if stop_rule == "aligned" and aligned_optima(pop):
        return {"converged": True, "total_gens": 0, "total_evals": total_evals}

    for gen in range(1, max_gens + 1):
        for i in range(N + 1):
            # mating selection in neighborhood
            parent_idx = rng.choice(B[i])
            y = pop[parent_idx].copy()
            y[rng.integers(n)] ^= 1  # 1-bit mutation

            # evaluate ONCE (one noisy k), then reuse for all neighborhood comparisons
            kN = noisy_k(y, p, rng)
            total_evals += 1

            # neighborhood replacement
            for ell in B[i]:
                gy = g_from_k(kN, ell)
                if gy <= stored_g[ell]:
                    pop[ell] = y.copy()   # avoid aliasing across subproblems
                    stored_g[ell] = gy

        if stop_rule == "front":
            if front_covered(pop):
                return {"converged": True, "total_gens": gen, "total_evals": total_evals}
        elif stop_rule == "aligned":
            if aligned_optima(pop):
                return {"converged": True, "total_gens": gen, "total_evals": total_evals}
        else:
            raise ValueError("stop_rule must be 'front' or 'aligned'")

    return {"converged": False, "total_gens": max_gens, "total_evals": total_evals}


# ---------- Run experiments for T=1 and T=2 ----------
def run_compare_T(ns, p_factor=0.05, trials=30, seed=0):
    base = np.random.default_rng(seed)
    out = {}

    for n in ns:
        p = p_factor / n
        out[n] = {"p": p, "T1": {"front": [], "aligned": [], "front_ok": 0, "aligned_ok": 0},
                        "T2": {"front": [], "aligned": [], "front_ok": 0, "aligned_ok": 0}}

        print(f"n={n:>3}, p={p:.5f} ... ", end="", flush=True)
        t0 = time.time()

        for _ in range(trials):
            # independent streams for each run
            rng1 = np.random.default_rng(base.integers(2**32))
            r1f = simulate_moead(n, p, T=1, stop_rule="front", rng=rng1)
            if r1f["converged"]:
                out[n]["T1"]["front"].append(r1f["total_evals"])
                out[n]["T1"]["front_ok"] += 1

            rng2 = np.random.default_rng(base.integers(2**32))
            r1a = simulate_moead(n, p, T=1, stop_rule="aligned", rng=rng2)
            if r1a["converged"]:
                out[n]["T1"]["aligned"].append(r1a["total_evals"])
                out[n]["T1"]["aligned_ok"] += 1

            rng3 = np.random.default_rng(base.integers(2**32))
            r2f = simulate_moead(n, p, T=2, stop_rule="front", rng=rng3)
            if r2f["converged"]:
                out[n]["T2"]["front"].append(r2f["total_evals"])
                out[n]["T2"]["front_ok"] += 1

            rng4 = np.random.default_rng(base.integers(2**32))
            r2a = simulate_moead(n, p, T=2, stop_rule="aligned", rng=rng4)
            if r2a["converged"]:
                out[n]["T2"]["aligned"].append(r2a["total_evals"])
                out[n]["T2"]["aligned_ok"] += 1

        dt = time.time() - t0
        def m(arr): return np.mean(arr) if arr else float("nan")
        print(
            f"T1 front {out[n]['T1']['front_ok']}/{trials} (mean {m(out[n]['T1']['front']):.0f}), "
            f"T2 front {out[n]['T2']['front_ok']}/{trials} (mean {m(out[n]['T2']['front']):.0f}) | "
            f"T1 aligned {out[n]['T1']['aligned_ok']}/{trials} (mean {m(out[n]['T1']['aligned']):.0f}), "
            f"T2 aligned {out[n]['T2']['aligned_ok']}/{trials} (mean {m(out[n]['T2']['aligned']):.0f}) "
            f"[{dt:.1f}s]"
        )

    out["trials"] = trials
    out["p_factor"] = p_factor
    return out


# ---------- Plot: two panels (front vs aligned), overlay T=1 and T=2 ----------
def plot_compare_T(results):
    trials = results["trials"]
    p_factor = results["p_factor"]

    ns = np.array(sorted([k for k in results.keys() if isinstance(k, int)]), dtype=float)

    def stats(Tkey, rule):
        means, stds, rates = [], [], []
        for n in ns.astype(int):
            arr = results[n][Tkey][rule]
            means.append(np.mean(arr) if arr else np.nan)
            stds.append(np.std(arr) if arr else 0.0)
            ok = results[n][Tkey][f"{rule}_ok"] / trials
            rates.append(ok)
        return np.array(means), np.array(stds), np.array(rates)

    fig, axes = plt.subplots(1, 2, figsize=(14, 5))

    for ax, rule, title in [
        (axes[0], "front", "Stop when current population covers full Pareto front"),
        (axes[1], "aligned", "Stop when all subproblems are aligned: sum(pop[i]) == i"),
    ]:
        m1, s1, r1 = stats("T1", rule)
        m2, s2, r2 = stats("T2", rule)

        ax.errorbar(ns, m1, yerr=s1, fmt="o-", capsize=3, label="T=1 (evals)")
        ax.errorbar(ns, m2, yerr=s2, fmt="s-", capsize=3, label="T=2 (evals)")
        ax.set_xlabel("n")
        ax.set_ylabel("Total evaluations")
        ax.set_title(f"{title}\n(p = {p_factor}/n)")
        ax.grid(True, alpha=0.3)

        axb = ax.twinx()
        axb.plot(ns, r1, "o--", alpha=0.6, label="T=1 (success rate)")
        axb.plot(ns, r2, "s--", alpha=0.6, label="T=2 (success rate)")
        axb.set_ylabel("Convergence rate")

        # combine legends
        h1, l1 = ax.get_legend_handles_labels()
        h2, l2 = axb.get_legend_handles_labels()
        ax.legend(h1 + h2, l1 + l2, loc="upper left", fontsize=9)

    plt.tight_layout()
    plt.show()


if __name__ == "__main__":
    p_factor = 0.05
    ns = [10, 15, 20, 30, 40, 50, 60, 80]
    results = run_compare_T(ns, p_factor=p_factor, trials=30, seed=42)
    plot_compare_T(results)