**Proved within the supplied pinned model:** Round 4’s candidate proof survives the audit. The family coupling, renewal calculation and restart establish expected **Θ(n²) attempts for fixed c>0 and T≥2**, versus **Θ(n³) for T=1**, with p=c/n. The [analytic audit](audit.md) explicitly checks conditioning, boundary timing and simultaneous repair.

This requires ideal extrema, pinned labels, the supplied corner, cyclic own-parent standard-bit mutation and activated bitwise noise.

**Contradicted: expected runtime is universally nonincreasing in T.** Exact transition certificates give this counterexample at n=3, p=1/192:

| T | Expected simultaneous boundary time, sweeps |
|---:|---:|
| 2 | 4.7659580192 |
| 3 | 4.7671266818 |

Both have endpoint-donor set `{0,1}`. The difference is rigorously positive, approximately **0.001168662645 sweeps**. These are deterministic enclosures, not sampled means or confidence intervals. [Certificates and reproduction](README.md).

Two additional witnesses refute shortcuts:

- Conditioning on accepted observation 0 gives true-error probability **32/5197 > p** from parent weight 2.
- A population can become fully correct during a sweep and finish that sweep incorrect.

Neither invalidates the audited proof. Its bounds condition before proposals, preserve boundary stopping, and restart with a fresh comparison forest.

**Mechanically checked:** 25 full-state cells, 4,339 population/cell combinations and 242,064 bounded forest transitions. The forest search expands at most two particles; general validity rests on the analytic proof. All **95 repository tests, 17 new audit tests and 15 prior-proof tests** pass, alongside compilation. Five new outputs reproduce byte for byte; certificates verify without NumPy.

Published plans and receipts reproduce; **no dependency repair was needed**. Existing empirical results remain:

| Comparison | Complete observations per arm | Restricted-mean ratio, nominal 95% interval |
|---|---:|---:|
| n=256, T=1/T=16 | 24 | 2.327639 [2.050148, 2.674642] |
| Separate n=512, T=1/T=23 | 32 | 2.339095 [2.085387, 2.596468] |

The original campaign still has one capped main trial and **240 missing, gate-blocked holdout trials**. Its two-stage decision remains inconclusive. No new scientific sampling occurred.

**Remaining gaps:** ordinary initialization, growing T, tail bounds and explanations of the observed pre-S savings remain unresolved here. A lost particle tag, failed family independence or certified expectation exceeding an applicable bound would falsify the proof.

Morning report: cumulative progress now includes audited empirical evidence, a validated conditional corner theorem and an expectation-monotonicity counterexample. Curated outputs and STATUS/CLAIMS updates are complete. Verification corrections concerned equality handling, an asymmetry fixture and packaging order; details are in [checks.json](checks.json). Elapsed time was approximately **13 minutes**, using one CPU, with no paid resources, network access, commit or push. All 166 preservation checks passed.

Next task: Derive the first-order small-noise coefficient of the T=3 minus T=2 supplied-corner completion-time gap and determine its dependence on n, because the certified n=3 slowdown breaks their noiseless equality despite identical endpoint donors.
