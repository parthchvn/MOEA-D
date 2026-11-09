**The candidate proof survives the independent audit. Proved within the supplied pinned model:**
\[
A_n=-\frac n2\log n+O(n).
\]
The [analytic audit](audit.md) supplies explicit uniform bounds for the exceptional sites and both edges. The conclusion rests on that argument, separately from the finite numerical checks.

For every \(n\ge8\), the audit establishes:

| Contribution | Uniform bound |
|---|---:|
| Endpoint recipient 0 | \(|\gamma_{T,0}|\le36n\) |
| Recipient 1 | \(|\gamma_{T,1}|\le225n\) |
| Recipient 2 under \(T=3\) | \(0\le\gamma_{3,2}\le420\) |
| Slow-edge leading term \(L\) | \(\left|L-n/(2u)\right|\le64(1+n/u^2)\) |
| Other wrong values at each slow site | At most 24 |

The two parity-spaced \(T=2\) edges each contribute \((n/4)\log n\). All exceptional terms, including the even-\(n\) orphan, total \(O(n)\); the \(T=3\) contributions total \(O(n)\).

A necessary qualification is now explicit: recipient 1’s insertion parents have weights 1 or 2. Extending its erroneous-observation bound to weight-0 parents would be false. The actual insertion histories satisfy the restriction. Recipient 2’s shared breeder is handled using predictable attempt counts and fresh randomness after stopping, without assuming independent repair times.

**Mechanically checked:** all 120 published exact recipient coefficients at \(n=3,\ldots,10\) match the independent evaluator. Extending the literal-mask full-population calculation to all **3,125 states per cardinality at \(n=4\)** gives
\[
A_4=-1.4923892474463167\ldots
\]
exactly, matching the reduction. The previously verified \(A_3=+0.22213184717778317\ldots\) remains unchanged.

Exact checks also cover 128 edge sites, 95 exceptional contributions, 1,348 two-error means and 2,696 exceptional phase delays. No bound violation was found. [Results and reproduction instructions](README.md).

**Published empirical evidence reverified; no new trajectory measurements:**

| Comparison | Complete observations per arm | Restricted-mean ratio, nominal 95% interval |
|---|---:|---:|
| Original \(n=256\), \(T=1/T=16\) | 24 | 2.327639 [2.050148, 2.674642] |
| Separate \(n=512\), \(T=1/T=23\) | 32 | 2.339095 [2.085387, 2.596468] |

Prior registrations, receipts and seed separation replay successfully; **no dependency repair was needed**. The original preregistration and **240 missing, gate-blocked holdout trials** remain unchanged. Its two-stage decision remains inconclusive.

**Checks passed:** 95 repository tests, 15 new audit tests, 12 prior coefficient tests and compilation. Four new result files reproduce byte for byte. All 269 protected tracked files remain unchanged; STATUS and CLAIMS received the intended updates. Curated artifacts are in `deliverables/`; raw logs remain outside it.

**Assumptions and remaining gaps:** ideal extrema, pinned labels, the supplied corner, ascending own-parent standard-bit mutation, activated bitwise observation noise, filled cardinalities and simultaneous boundary stopping. The theorem establishes eventual derivative negativity. It does **not** establish negativity for every \(n\ge4\), a uniform Taylor remainder, fixed-positive-\(c\) ordering at \(p=c/n\), or ordinary-initialization behavior. A failed stated uniform inequality or independent transition/derivative disagreement would falsify the relevant proof step.

Morning report: cumulative progress now includes audited empirical evidence, the earlier conditional corner theorem and monotonicity counterexample, and an audited asymptotic explanation of the first-order sign reversal. Elapsed through packaging was **814.3 seconds—13 minutes 34 seconds**, using one CPU. No paid resources, network access, commit or push occurred.

Next task: Derive and bound the second-order coefficient in the T=3 minus T=2 corner-time expansion, because the audited negative first-order term still lacks a uniform noise window.
