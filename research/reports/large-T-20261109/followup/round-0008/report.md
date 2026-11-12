**Derived the second-order coefficient**, in sweep units:
\[
E\tau_3-E\tau_2=pA_n+p^2B_n+O_n(p^3).
\]
Here \(B_n\) is half the second derivative. The [derivation](derivation.md) retains both within-sweep and different-sweep insertions.

| n | \(B_n\) | Status |
|---:|---:|---|
| 3 | +0.4281536262 | Exact rational; independent implementation agrees |
| 4 | −1.8401743257 | Exact rational; independent implementation agrees |
| 12 | −22.49855751 | Deterministic float64; uncertified |

**Candidate proof:** \(|B_n|\le1536n^5\) for every \(n\ge3\). The argument handles the even-\(n\), \(T=2\) orphan separately through a reversible local chain and mixed-insertion bounds. Those new steps await independent audit.

**Proved conservative remainder:** an explicit bound controls all higher orders on a small, \(n\)-dependent window. For example, at \(n=4\), the gap is negative throughout \(0<p\le2^{-34}\). This window is extremely conservative; ordering at fixed positive \(c\), with \(p=c/n\), remains unresolved.

At the previously certified \(n=3,p=1/192\) point, the quadratic prediction reduces the discrepancy by **over 104-fold**, leaving a certified discrepancy between \(1.1094\times10^{-7}\) and \(1.1212\times10^{-7}\) sweeps.

**Checks passed:** 134 tests—95 repository, 12 new and 27 prior—plus compilation. The independent full-population calculation matched 20 rational components across 6,762 population/cardinality cases. Checks included 4,992 orphan suffix comparisons and 124 mixed-insertion bounds. Eight result files reproduce byte for byte; 282 protected tracked files remain unchanged. See [reproduction instructions](README.md) and [checks](checks.json).

**Published measurements reverified; no new sampling:** the original \(n=256\) ratio remains 2.327639 [2.050148, 2.674642], with 24 complete observations per arm. The separate registered \(n=512\) ratio remains 2.339095 [2.085387, 2.596468], with 32 per arm. These retain their approximate nominal 95% intervals. No dependency repair was needed. The original preregistration, capped main trial and **240 missing, gate-blocked holdout trials** remain unchanged.

Assumptions remain the supplied pinned corner, ascending own-parent standard-bit mutation, activated bitwise observation noise, filled cardinalities and simultaneous boundary stopping. Proof gaps include independent review of the polynomial bound and a useful uniform higher-order remainder. A violated suffix inequality or independent coefficient disagreement would falsify the associated step.

Morning report: cumulative progress now extends the audited first-order asymptotic to an exact quadratic response, a candidate polynomial bound and a conservative finite-noise window. STATUS and CLAIMS were updated. A larger deterministic grid was interrupted without retained results. Elapsed through packaging was **1,315 seconds—about 22 minutes**; successful new reproduction took 30.3 seconds. No paid resources, network access, commit or push occurred.

Next task: Independently audit the even-n orphan mixed-insertion bound, because it carries the new candidate |B_n|≤1536n^5 estimate needed before enlarging the noise window.
