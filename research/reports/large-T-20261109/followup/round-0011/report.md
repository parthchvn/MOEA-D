**Candidate proof: yes, for a closed \(T=2\) pair.** The real-\(p\) Schur complement eliminates the entire double-error block while preserving elapsed time and polynomial acceptance-weighted entry and exit bounds. The [proof](proof.md) also gives an exact one-block elimination inside the full pinned population, retaining other-coordinate evolution during omitted sweeps. Independent audit remains necessary.

Let \(D,S,A\) denote double-error, single-error and aligned pair states, and \(R_D=(I-P_{DD})^{-1}\). For \(0\le p<1/6\), the candidate bounds are
\[
P_{SD}R_D\mathbf1\le\frac{4p}{1-6p},
\qquad
P_{AD}R_D\mathbf1\le\frac{2p^2}{1-6p}.
\]
The corresponding entry-weighted exit masses are at most \(2p\) and \(p^2\). Acceptance probabilities cancel the large inverse repair weights; positivity of holding denominators alone would not establish these bounds.

**Mechanically checked:** nine exact Schur solves agree with direct boundary hitting equations. Representative results are:

| \(n\), pair | \(p\) | Maximum entry-weighted residence | Candidate bound |
|---|---:|---:|---:|
| 3, {2,3} | 1/81 | 0.007465593 | 0.053333333 |
| 5, {4,5} | 1/625 | 0.001755076 | 0.006462036 |

These are deterministic rational calculations in sweeps, not sampled estimates. Exact values are in [schur.csv](schur.csv). At \(n=33,p=n^{-4}\), the analytic residence bound is \(3.372923\times10^{-6}\), where the replayed absolute-majorant obstruction exceeds 1,314.

**Candidate negative result:** stronger residence-moment bounds fail. An explicit positive path gives
\[
\bigl(P'_{SD}(0)R_D(0)^2\mathbf1\bigr)_{(0,n)}
\ge \frac{n^{n-4}}{32}.
\]
At \(n=33\), the sharper exact path contribution exceeds \(1.0465\times10^{43}\). Thus first-moment elimination does not automatically control derivatives or the Taylor remainder. This does not refute a signed remainder bound. See [witnesses](moments.csv).

**Assumptions and gaps:** pinned ideal extrema and labels, ascending own-parent standard-bit mutation, activated bitwise observation noise, filled cardinality, and simultaneous boundary stopping. The autonomous calculation excludes the even-\(n\) orphan-fed last pair and overlapping \(T=3\) neighborhoods. The reduced global inverse, synchronization under reinfection, and full third-and-higher remainder remain unresolved. No enlarged full-process noise window is claimed. A failed phase identity, acceptance bound, boundary drift inequality, or Schur/direct equality would falsify the associated argument.

**Published measurements remain unchanged:**

| Comparison | Complete trials per arm | Ratio [approximate nominal 95% interval] |
|---|---:|---:|
| \(n=256,\ T=1/T=16\) | 24 | 2.327639 [2.050148, 2.674642] |
| Separate \(n=512,\ T=1/T=23\) | 32 | 2.339095 [2.085387, 2.596468] |

The recursive dependency replay passed; no plan or receipt repair was needed. The original preregistration, capped main trial and **240 missing blocked holdout trials** remain preserved. Its two-stage decision remains inconclusive. No new scientific trajectories or seeds were used.

**Verification:** 120 tests passed; compilation and whitespace checks passed. Six generated outputs reproduced byte for byte, and 341 protected tracked entries remained unchanged. Curated artifacts and reproduction instructions are in [README.md](README.md); STATUS and CLAIMS were updated.

Morning report: cumulative progress now includes audited empirical comparisons, linear and quadratic response results, the absolute-majorant obstruction, and this real-\(p\) elimination candidate with a higher-residence limitation. Packaging took **1,341.5 seconds—22 minutes 22 seconds**; full reproduction took **64.8 seconds**. One CPU, no scientific/test failures, paid resources, network, commit or push.

Next task: Does an independent audit validate the phase-potential Schur bound and its full-population tensor extension, since these now carry the proposed real-p control beyond the divergent absolute majorant?
