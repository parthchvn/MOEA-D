**The first-order sign changes with \(n\).** For the supplied pinned corner, measured in sweeps,
\[
E\tau_3-E\tau_2=pA_n+O_n(p^2).
\]
The finite-\(n\) derivative formula is proved; exact arithmetic gives \(A_3>0\) but \(A_n<0\) for every \(n=4,\ldots,10\).

| \(n\) | \(A_n\), sweeps per unit \(p\) | Verification |
|---:|---:|---|
| 3 | +0.2221318472 | Exact; independent full-state check |
| 4 | −1.4923892474 | Exact |
| 10 | −9.5116810659 | Exact |
| 1024 | −3457.562158 | Deterministic float64 |
| 1025 | −2640.369475 | Deterministic float64 |

**Candidate asymptotic theorem:**
\[
A_n=-\tfrac12 n\log n+O(n).
\]
The [complete candidate argument](derivation.md) isolates slow interior repairs under \(T=2\): their contributions form harmonic sums near both endpoints. \(T=3\) supplies a fast repair donor at every interior site. Attempts multiply the coefficient by \(n+1\).

At \(n=3\), the direct endpoint contributions cancel exactly. The donor-1 contribution changes by \(+0.3131733141\), while recipient 2 contributes \(-0.09104146695\), producing the positive gap. Thus identical endpoint donors do not imply identical simultaneous-completion laws.

Assumptions remain ideal extrema, pinned labels, supplied state \((2,1,2,\ldots,n)\), ascending own-parent standard-bit mutation, activated bitwise observation noise, filled-cardinality neighborhoods, and boundary stopping.

**Checks passed:** 95 repository tests, 12 new tests, 17 prior-audit tests, compilation, and independent exact enumeration of 256 populations per \(T\) at \(n=3\). Six generated outputs reproduce byte for byte; all 189 preservation checks pass. [Code, data and reproduction instructions](README.md) and [verification accounting](checks.json) are included.

**No new scientific sampling occurred.** Published plans and receipts replay successfully; no dependency repair was needed. The original n=256 ratio remains 2.327639 [2.050148, 2.674642], and the separate n=512 ratio remains 2.339095 [2.085387, 2.596468]. These retain their approximate nominal 95% intervals. The original 240 holdout trials remain missing and gate-blocked; its two-stage decision remains inconclusive.

**Remaining gaps:** independent review of the asymptotic argument, negativity at every \(n\ge4\), and a Taylor remainder uniform in \(n\). The derivative alone does not establish ordering at fixed positive \(c\) with \(p=c/n\). A full-state derivative disagreement would falsify the reduction; a rigorous failure of \(A_n/(n\log n)\to-1/2\) would falsify the candidate asymptotic.

Morning report: cumulative progress now includes audited empirical evidence, the prior pinned-corner result, and an exact first-order sign reversal. STATUS and CLAIMS were updated. Elapsed time was approximately **13 minutes**, using one CPU, with no paid resources, commit or push.

Next task: Independently audit the candidate \(A_n=-(n/2)\log n+O(n)\) proof, especially its exceptional-site bounds and uniform edge estimates, because these steps now carry the large-n explanation of the exact sign reversal.
