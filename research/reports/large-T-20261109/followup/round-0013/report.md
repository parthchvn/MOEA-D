**Candidate proof: the cubic coefficient remains polynomial for both parities.** The [argument](proof.md) gives
\[
E\tau_3-E\tau_2=pA_n+p^2B_n+p^3C_n+O_n(p^4),
\qquad |C_n|\le10^{10}n^7.
\]
This bound awaits independent audit. Units are sweeps; attempts multiply coefficients by \(n+1\).

**Mechanically checked exact coefficients**, displayed rounded:

| \(n\) | \(C_n\) |
|---:|---:|
| 3 | +0.783396071426 |
| 4 | −1.549977057315 |
| 5 | −0.023834241014 |
| 6 | −5.367760391772 |

A separate full-population implementation matches **28 rational quantities at \(n=3,4\)**. These are deterministic calculations, without sampling intervals or censoring. [Results and reproduction](README.md).

The candidate proof retains both acceptance factors when two insertions create a corrupted pair. For even \(n\), it subtracts the autonomous orphan hitting function before bounding mixed terms. **Mechanically checked:** 16 ordered cubic terms, 996 excess identities and 1,608 inequalities. At \(n=32\), two auxiliary first-order quantities of magnitude \(2.27\times10^{57}\) cancel exactly to leave \(6.12\times10^{-44}\).

**Assumptions:** supplied corner \((2,1,2,\ldots,n)\), pinned ideal extrema and labels, ascending own-parent standard-bit mutation, activated bitwise observation noise, filled-cardinality neighborhoods, and simultaneous alignment at sweep boundaries.

**Proof gaps:** independent review of the two-entry weighting, phase extension of the orphan identity, and mixed-term bounds. The exponential higher-residence counterexample remains valid. A uniform fourth-and-higher remainder is unresolved, so no enlarged noise window or fixed-positive-\(c\) ordering is claimed. A failed phase identity, missing acceptance factor, or exact coefficient exceeding the proposed bound would falsify the corresponding step.

**Prior evidence remains unchanged:** the published ratios are 2.327639 [2.050148, 2.674642] at \(n=256\), with 24 complete observations per arm, and 2.339095 [2.085387, 2.596468] for the separately registered \(n=512\) study, with 32 per arm. These retain their earlier approximate nominal 95% intervals. Registration and receipt replay passed; no repair was needed. The original capped trial, **240 missing blocked holdout trials**, preregistration and inconclusive two-stage decision are preserved. No new trajectories or seeds were generated.

**Checks and accounting:** 123 tests, compilation, whitespace, artifact hashes and relative links pass. Eight curated outputs regenerate byte for byte from completed calculations; 364 protected tracked entries remain unchanged. One accidentally overlapping development check was interrupted and discarded; final calculations were serial. Elapsed through packaging: approximately **80 minutes 26 seconds**, within budget. No network, paid resources, commit or push.

Morning report: cumulative progress now includes audited empirical comparisons, linear and quadratic bounds, the higher-residence obstruction, and exact cubic calculations with a polynomial proof candidate. Curated artifacts and STATUS/CLAIMS updates are complete.

Next task: Independently audit the two-entry acceptance estimate and phase-aware orphan cancellation across all six mixed cubic terms, because these new steps carry the candidate polynomial bound.
