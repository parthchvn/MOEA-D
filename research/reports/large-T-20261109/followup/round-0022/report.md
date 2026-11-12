**Proved:** losing the last correct slot has bounded acceptance-weighted repair cost. With
\[
\kappa=\frac{2(n+1)p(1-p)}{1-(d_{\max}+1)p},
\]
expected all-wrong occupation is at most \(\kappa\) times vulnerable seeded occupation, when the denominator is positive. For \(T=\lceil\sqrt n\rceil\), \(p=c/n\), **\(\kappa\to2c\)**.

The proof retains corruption’s acceptance factor, which cancels the reciprocal repair potential. It includes cyclic timing, external overwrites, shared observations and reinfection. An extension charges initial full-pinning entrances under ordinary initialization without assuming fresh noise conditional on acceptance.

**Also proved:** supplied all-wrong states can remain superpolynomially slow under ongoing noise. Thus entrance weighting is essential. **Total runtime remains unresolved:** noisy progress while a correct slot survives still needs control.

Assumptions are standard-bit own-parent mutation, activated bitwise observation noise, filled-cardinality neighborhoods and stored-label replacement. Completion remains simultaneous exact alignment at sweep boundaries.

Checks passed: **106 tests**, compilation, **2,736 certified phase states**, and six byte-identical reproduced outputs. A packaging-order error was corrected without changing scientific results.

Saved the [proof](proof.md), [self-audit](audit.md), [reproduction bundle](README.md), [proposed memory updates](memory.md), and [checkpoint](PROGRESS.md). Existing sources and evidence are unchanged. Elapsed: **16 minutes 6 seconds**, one CPU, no paid resources, sampling, commits or pushes. Novelty remains unverified.

Strongest falsifier: an admissible exact phase state violating the claimed unit-drift supersolution or its acceptance-weighted entrance bound.

Next task: Bound noisy seeded occupation from the pinned corner at square-root T, because this is the missing quantity needed to turn the constant-overhead decomposition into a total-runtime bound.
