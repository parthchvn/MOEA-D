**The phase-potential Schur bound and its exact one-block tensor extension survive the independent audit.** They are **proved under the stated pinned, closed-pair assumptions**. The full-population Taylor remainder remains unresolved. See the [analytic audit](audit.md).

For \(R_D=(I-P_{DD})^{-1}\) and \(0\le p<1/6\),
\[
P_{SD}R_D\mathbf1\le\frac{4p}{1-6p},
\qquad
P_{AD}R_D\mathbf1\le\frac{2p^2}{1-6p}.
\]
The full-population elimination preserves these bounds by retaining the rest’s evolution during omitted sweeps and charging their elapsed time.

**Mechanically checked:** the independent implementation verified 5,154 Bernstein coefficients covering the entire finite-check interval \(0\le p\le1/6\), reproduced nine published pair solves exactly, and checked 260 population transition rows. The complete \(n=3\) calculation verified 144 joint exit/residence identities and 111 reduced hitting equations against the direct solution.

At \(n=3,p=1/81\), rounded exact calculations give:

| Quantity | Result |
|---|---:|
| Supplied-corner population mean | 4.810704306 sweeps |
| Underestimate when excursion time is omitted | 0.026355723 sweeps |
| Frozen-rest exit-law error from \((3,3,0,0)\) | 0.202776754 total variation |

These quantify failures of the shortcuts, not failures of the audited construction. Exact fractions are in [verification.json](verification.json).

**Contradicted strengthening:** polynomial control of all entrance-weighted higher residence moments fails. The audited family satisfies
\[
\bigl(P'_{SD}(0)R_D(0)^2\mathbf1\bigr)_{(0,n)}
\ge n^{n-4}/32.
\]
The explicit \(n=33\) path contribution exceeds \(1.0465\times10^{43}\). This does not determine the corresponding signed Taylor coefficient.

**Assumptions and gaps:** ideal extrema, pinned labels, ascending own-parent standard-bit mutation, activated bitwise observation noise, filled cardinality \(T=2\), and simultaneous boundary stopping. The selected pair must be closed; the orphan-fed last even-\(n\) pair and overlapping \(T=3\) neighborhoods are excluded. The remaining global inverse, synchronization under reinfection, and uniform higher-order remainder still need control. No enlarged noise window is established. A failed phase identity, acceptance bound, tensor factorization, or exact Schur equation would falsify the associated argument.

**Published measurements remain unchanged:**

| Comparison | Complete observations per arm | Ratio [approximate nominal 95% interval] |
|---|---:|---:|
| Original \(n=256,\ T=1/T=16\) | 24 | 2.327639 [2.050148, 2.674642] |
| Separate restricted-mean \(n=512,\ T=1/T=23\) | 32 | 2.339095 [2.085387, 2.596468] |

Recursive replay verified earlier registration and receipts; **no dependency repair was needed**. The original preregistration, capped main trial, **240 missing blocked holdout trials**, and inconclusive two-stage decision are preserved. No new scientific sampling or seeds were used.

**Checks and accounting:** 120 tests passed, compilation and whitespace checks passed, and 348 protected tracked entries remained unchanged. Packaging finished after **3,256 seconds—54 minutes 16 seconds**, including 2,010 seconds for the completed exact audit. One development solve was interrupted for arithmetic cost; the revised exact verification passed. One CPU, no network, paid resources, commit or push. Curated artifacts are linked in [README.md](README.md); local STATUS and CLAIMS were updated.

Morning report: this checkpoint adds an audited real-\(p\) elimination to the earlier empirical and small-noise results, while preserving the higher-residence obstruction and the unresolved remainder.

Next task: Does the supplied-corner cubic coefficient for the T=3 minus T=2 runtime gap remain polynomial after signed cancellation, since the audited first-moment bound does not control higher residence moments?
