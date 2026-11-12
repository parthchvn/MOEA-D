**Acceptance weighting alone does not close the full remainder bound.** The [candidate proof](proof.md) identifies an obstruction to absolute resolvent bounds, including those that sum clean excursions before taking absolute values.

For accessible adjacent corrupted donors under T=2, every positive diagonal state weighting retains an exponential norm lower bound. At n=33 and p=n⁻⁴, the exact lower bound multiplied by p exceeds **1314**. The corresponding positive corner-row majorant diverges. This rules out that approach; it does **not** refute a signed resolvent or the desired real-positive-p remainder bound.

**Proved restricted progress:** using the audited discounted orphan identity, the orphan-only remainder after order two satisfies
\[
|R_O(p)|\le128p^3/q^4\le10368p^3n^4,\qquad p\le q/4.
\]
This is negligible relative to the linear term on the requested scale. Mixed insertions and adjacent-error contributions remain unresolved, so the full-process noise window is unchanged.

**Mechanically checked:**

- 121 tests passed; compilation and whitespace checks passed.
- Four new outputs reproduced byte for byte.
- Checks include seven signed-resolvent diagonals, six positive accessibility entries, ten exact orphan remainders and ten matches to published orphan coefficients.
- All 327 protected tracked files and symlinks remain unchanged.

The [reproduction bundle](README.md) contains exact fractions, code, receipts and falsifiers. Earlier plans and receipts replayed successfully; no dependency repair was needed. No new scientific trajectories or seeds were used.

**Published measurements remain unchanged:**

| Comparison | Complete trials per arm | Ratio [approximate nominal 95% interval] |
|---|---:|---:|
| n=256, T=1/T=16 | 24 | 2.327639 [2.050148, 2.674642] |
| Separate n=512, T=1/T=23 | 32 | 2.339095 [2.085387, 2.596468] |

The original preregistration, capped trial and **240 missing blocked holdout trials** are preserved. Its two-stage decision remains inconclusive.

**Assumptions and gaps:** supplied pinned corner, ideal extrema, ascending own-parent standard-bit mutation, activated bitwise observation noise, filled cardinalities and simultaneous boundary stopping. The general no-go application awaits independent audit. A transition-row discrepancy, failed clean-descendant bound or discounted-identity violation would invalidate the corresponding argument.

Morning report: cumulative progress now includes audited empirical comparisons, linear and quadratic response bounds, a restricted all-order orphan bound, and a concrete obstruction for the absolute resolvent approach. STATUS and CLAIMS were updated. Packaging finished after **729.9 seconds—12 minutes 10 seconds**; full reproduction took **59.8 seconds**. One CPU, no scientific/test failures, paid resources, network, commit or push.

Next task: Can a real-p Schur complement eliminate the T=2 double-error pair block while preserving polynomial acceptance-weighted entry and exit bounds, since its exact holding denominator stays positive where the absolute majorant diverges?
