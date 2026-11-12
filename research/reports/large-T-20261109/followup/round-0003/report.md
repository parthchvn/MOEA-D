**Mechanically checked: the independent audit passes.** Raw receipts reproduce the preceding experiment’s estimates, censoring and phase timing. Its committed plan predates measurement; no dependency repair was needed. Reproducible code and curated results are in the [audit bundle](README.md).

**Empirically supported:** at n=512, p=1/32768 and H=38,341 sweeps, the restricted-mean evaluation ratio T=1/T=23 is **2.339095**, with approximate nominal 95% bootstrap interval **[2.085387, 2.596468]**.

| Arm | Exact / capped / missing | Mean evaluations | q10 / median / q90, millions |
|---|---:|---:|---:|
| T=1 | 32 / 0 / 0 | 5,139,185.91 | 4.507 / 5.043 / 5.903 |
| T=23 | 32 / 0 / 0 | 2,197,082.81 | 1.592 / 2.183 / 2.586 |

Four separate smoke trials also completed and remain excluded from inference. Each main arm’s Wilson 95% completion interval is [0.892821, 1].

**Empirically supported phase description:** savings occur predominantly before stored-label alignment S.

| Phase | Mean savings, sweeps | Pointwise nominal 95% interval |
|---|---:|---:|
| Before ideal-reference discovery U | 4,462.406 | [3,787.054, 5,106.461] |
| U to S | 1,272.563 | [1,001.177, 1,594.568] |
| After S | 0.125 | [0, 0.375] |

All phases have 32 completed observations per arm. One T=1 trajectory has a **four-sweep post-S delay**; all others have zero. First-exact and post-S endpoints coincide in all 64 main receipts. Both arms record zero pinned-endpoint repairs. The decomposition has zero arithmetic residual; it does not establish causal mediation.

**Mechanically checked seed separation:** all 68 follow-up seeds are unique and disjoint from **2,420 prior published seeds**, including every blocked holdout seed. The original pilot and campaign share 164 smoke/calibration seeds; these are excluded from both primary estimates and must not count as independent replications.

The earlier n=256 estimate also reproduces: **2.327639 [2.050148, 2.674642]**. Its original campaign still has one capped main trial and **240 missing, gate-blocked holdout trials**. The original preregistration, holdout and inconclusive two-stage decision remain unchanged.

**Checks:** the separate auditor matched **6,914 scalar/structural comparisons**, with maximum numerical discrepancy below 2.28×10⁻¹³. All **95 repository, 14 registered, 15 wrapper and 16 new audit tests** passed. Compilation passed; both the prior six analysis artifacts and the six new audit outputs reproduced byte for byte. A synthetic-fixture omission and a packaging-order error were corrected; neither affected published evidence. See [checks](checks.json), [phases](phases.csv) and [seed intersections](seeds.csv).

**Assumptions and proof gaps:** the unchanged process uses cyclic own-parent mutation, stored shared observation noise, moving extrema, filled-cardinality neighborhoods and sweep-boundary stopping. Independent pseudorandom streams and approximate bootstrap coverage remain assumptions. Rare tails, unrestricted expectation ordering, donor corruption, joint repair and asymptotics remain unresolved by this evidence. **No new candidate proof is advanced.** For the registered directional conjecture, a lower interval endpoint ≤1 fails its support rule; an interval entirely below one opposes it.

Published round-2 timing totals 16.613 seconds per invocation, including 14.224 seconds of engine calls. Private per-trial execution logs are unavailable, limiting independent verification of execution chronology.

Morning report: cumulative progress now includes the original evidence, a prior-round prospective registration, its completed experiment, and this independent audit. T=23 saves 57.25% of sampled evaluations while using 9.83 times the logical comparisons. This audit took approximately **7 minutes 33 seconds**. Curated outputs and STATUS/CLAIMS updates are complete; no new scientific sampling, network access, paid resources, commit or push occurred.

Next task: Preregister an independent n=512 T=3-versus-T=23 comparison to test whether three recipients retain the pre-S savings with fewer comparisons, because the audited T=23 benefit carries a 9.83-fold comparison overhead.
