**The candidate bound survives independent audit. Proved within the supplied pinned model:**
\[
|B_n|\le1536n^5,\qquad n\ge3,
\]
where \(B_n\) is the \(p^2\) coefficient of the T=3 minus T=2 completion-time gap, in sweeps. The [analytic audit](audit.md) makes the predictable orphan-turn count explicit and checks both insertion orders and the separate orphan-only calculation.

**Mechanically checked exact results:**

| n | Mixed-insertion coefficient |
|---:|---:|
| 4 | 3.6617001469 |
| 6 | 6.3956184797 |

These decimals represent exact rationals, not sampled estimates. At n=6, the two different-sweep orders have opposite signs; both are retained.

The independent implementation checked **16,512 suffix cases**, 268 regular repair means with orphan help omitted, 268 mixed forcings, 20 mixed responses and five local/joint-chain identities. No bound violation was found. The complete n=4 reconstruction matches the published second coefficient exactly.

**Verification:** all **121 tests** passed, together with compilation and whitespace checks. Five new outputs reproduce byte for byte; all eight round-8 outputs and their recursive dependency checks also reproduce. All **312 protected tracked files and symlinks** remain unchanged. [Reproduction guide](README.md) and [check receipts](checks.json).

**Published measurements remain unchanged:** the n=256 ratio is **2.327639 [2.050148, 2.674642]**, with 24 complete observations per arm; the separate registered n=512 ratio is **2.339095 [2.085387, 2.596468]**, with 32 per arm. These retain their earlier approximate nominal 95% bootstrap intervals. No dependency repair or new trajectory sampling was needed. The original preregistration, capped main trial and **240 missing, blocked holdout trials** are preserved; its two-stage decision remains inconclusive.

**Assumptions and proof limits:** ideal extrema, pinned labels, the supplied corner, ascending own-parent standard-bit mutation, activated bitwise observation noise, filled cardinalities and simultaneous boundary stopping. The bound does **not** enlarge the noise window: a uniform third-and-higher-order remainder remains unresolved. A violated suffix inequality, failed predictable-count identity or exact \(|B_n|>1536n^5\) would falsify the corresponding argument.

Morning report: cumulative progress now includes audited empirical comparisons, the first-order asymptotic, exact quadratic response and an audited polynomial coefficient bound. STATUS and CLAIMS were updated; curated artifacts are in `deliverables/`. Packaging completed after **671.5 seconds—11 minutes 12 seconds**; full reproduction took **58.1 seconds**. A packaging symlink check was corrected without changing scientific results. One CPU; no network, paid resources, commit or push.

Next task: Determine whether an acceptance-weighted resolvent can bound third-and-higher terms uniformly on p=o(log n/n^4), including adjacent corrupted donors, because the audited quadratic bound now leaves those terms as the obstacle to enlarging the noise window.
