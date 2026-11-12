Prepared the [preregistration](preregistration.md) and executable analysis for supervisor publication. **No prospective outcomes were drawn.** Measurement requires the committed round-1 checkpoint first.

**Mechanically checked:** the prior experiment has usable plans and receipts; no dependency repair was needed. No earlier follow-up checkpoint exists at the input revision. The [audit](audit.json) reproduced the published n=256 low-noise ratio **2.327639**, nominal 95% interval **[2.050148, 2.674642]**, from 24 trajectories per arm. The original holdout remains **0/240 observed**, blocked by the original high-noise cap. Its preregistration and inconclusive decision are preserved.

The separate prospective design fixes:

- **Arms:** n=512, p=1/32768, T=1 versus T=23; **32 independent trajectories per arm**.
- **Horizon:** 38,341 sweeps, or 19,669,446 evaluations including initialization.
- **Primary analysis:** ratio of restricted mean evaluation costs; 10,000 independent within-arm whole-trajectory bootstrap resamples; two-sided nominal 95% percentile interval.
- **Stopping:** four separately seeded smoke trials first, then one serial measurement invocation capped at 1,800 seconds. No adaptive stopping, additional replications, cap extensions, or replacement seeds.
- **Censoring:** retain administrative caps; distinguish missing receipts and report identification bounds without a primary confidence interval.
- **Diagnostics:** bounded time before U, between U and S, and after S, plus the first-exact/post-S gap. Completed-phase summaries retain their conditional denominators.

All **68 planned seeds** are distinct and disjoint from **2,420 published trial seeds**, including the blocked holdout. [plan.json](plan.json), [seeds.csv](seeds.csv), [analysis.py](analysis.py), and [freeze.json](freeze.json) make the choices reproducible.

**Checks passed:** 95 repository tests, 14 new synthetic analysis/design tests, Python compilation, receipt verification, artifact hashes, and preservation checks on 52 original files. Tests cover censoring in each phase, missing receipts, early exact assignment, boundary-zero events, and receipt/source tampering. Details are in [checks.json](checks.json). Local STATUS and CLAIMS were updated.

**Conjectured, unmeasured:** the new restricted-mean ratio exceeds one. An interval wholly below one opposes it; a lower endpoint ≤1 fails the support criterion. Assumptions include adequate independent pseudorandom streams and the frozen transition law. Bootstrap coverage is approximate. No new noisy proof is proposed: unrestricted tails, donor corruption, joint repair, and causal mechanism attribution remain unresolved.

Cumulative morning-report progress: published evidence audited, blocked validation preserved, and a separate prospective comparison fully specified. Elapsed time was approximately **7 minutes 12 seconds**; no paid resources, network access, research-repository commit, or push.

Next task: After verifying committed round-1 publication, implement and execute the frozen comparison to determine whether T=23 lowers the n=512 restricted mean and which phases account for the difference, since the original validation remains unmeasured.
