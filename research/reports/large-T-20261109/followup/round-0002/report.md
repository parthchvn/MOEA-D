**Completed the frozen round-1 study:** 64/64 main trials and 4/4 smoke trials, with no censoring, missing receipts, or sampling failures. The original blocked holdout and preregistration remain unchanged.

**Empirically supported:** at n=512, p=1/32768, and H=38,341 sweeps, the restricted-mean evaluation ratio T=1/T=23 is **2.339095**, with approximate nominal 95% bootstrap interval **[2.085387, 2.596468]**. This satisfies the registered rule favoring T=23.

| Arm | Mean evaluations | q10 / median / q90, millions |
|---|---:|---:|
| T=1 | 5,139,185.91 | 4.507 / 5.043 / 5.903 |
| T=23 | 2,197,082.81 | 1.592 / 2.183 / 2.586 |

Each arm completed 32/32 trials; its Wilson 95% completion interval is **[0.892821, 1]**. Inference uses the registered 10,000 independent within-arm whole-trajectory bootstrap resamples. Smoke trials are excluded.

**Empirically supported diagnostics:** almost all observed savings occur before stored-label alignment S.

| Phase | Mean savings, sweeps: T=1 minus T=23 | Pointwise nominal 95% interval |
|---|---:|---:|
| Before ideal-reference discovery U | 4,462.406 | [3,787.054, 5,106.461] |
| Between U and S | 1,272.563 | [1,001.177, 1,594.568] |
| After S | 0.125 | [0, 0.375] |

One T=1 trajectory required **four post-S sweeps**; all others required zero. First-exact and post-S endpoints coincide in all 64 main observations. Both arms recorded zero pinned-endpoint repairs. These observations support a predominantly pre-S explanation descriptively; they do not establish causal mediation or universal endpoint equality.

T=23 used **57.25% fewer evaluations**, but **9.83 times as many logical recipient comparisons**. Host timings remain descriptive.

**Mechanically checked:** registration was committed in `a5449de` before measurement; the prior evidence audit reproduced exactly; all 68 seeds are disjoint from 2,420 published seeds. Kernel tests ran first. All **95 repository tests, 14 registered tests, and 15 synthetic wrapper tests** passed, alongside compilation checks. A separate arithmetic implementation matched **275 quantities**, with zero phase-identity residuals. Analysis replay reproduced all six result files—including the plot—byte for byte.

The [reproduction guide](README.md) links runnable source, exact source snapshots, [per-trial data](trials.csv), [plan](plan.json), [summary](summary.json), [plot](results.png), and [checks](checks.json). Full plan/model hashes and toolchain provenance are in the [manifest](manifest.json):

- Plan: `f64686335a457d16eb0f26a94eef9a8bd94e75e76aec3eeb6524f50d1e48441f`
- Model: `246cad3ef58d87ed25f981faf893eb33a85c9c1b3e30796d5873d20d9ac57691`

**Assumptions and proof gaps:** this is the unchanged cyclic own-parent, filled-cardinality process with standard-bit mutation, activated bitwise observation noise, stored labels, moving observed extrema, and sweep-boundary stopping. Independent pseudorandom streams are assumed. Rare tails, unrestricted expectation ordering, donor corruption, joint repair and asymptotics remain unresolved by this evidence. Degenerate diagnostic intervals do not prove equality. **No new candidate proof is advanced.** An interval wholly below one would oppose the registered directional conjecture; a lower endpoint ≤1 would fail its support criterion.

Cumulative morning report: earlier n=256 evidence was audited, round 1 published a separate plan, and round 2 completed its n=512 comparison. The direction agrees with earlier evidence; the original two-stage decision remains inconclusive. Curated outputs and local STATUS/CLAIMS updates are complete. Elapsed time was about **9 minutes**, including **16.613 seconds** for the single measurement invocation. No network, paid resources, commit, or push was used.

Next task: Preregister an independent n=512 comparison of T=3 versus T=23 to test whether three recipients retain the observed pre-S savings with substantially fewer logical comparisons.
