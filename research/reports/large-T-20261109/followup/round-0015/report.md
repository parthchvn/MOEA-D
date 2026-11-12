**Polynomiality of the full fourth-order gap remains unresolved.** This round establishes partial bounds and a stronger counterexample to the absolute-residence approach. [Derivations and falsifiers](proof.md).

Writing
\[
E\tau_3-E\tau_2=pA_n+p^2B_n+p^3C_n+p^4D_n+O_n(p^5),
\]
the **mechanically checked exact coefficients**, rounded below, are:

| n | \(D_n\), sweeps per \(p^4\) |
|---:|---:|
| 3 | +1.017585089405 |
| 4 | −1.200413291676 |
| 5 | +0.602753414367 |

Independent sweep and phase recurrences agree at \(n=3,4\). All sixteen fourth-order R/O terms sum exactly at \(n=4\). The \(n=5\) result reproduced exactly but lacks an independent fourth-order oracle.

The mathematical progress is:

- **Proved:** the T=3 arm alone satisfies \(\lvert d_{3,n}\rvert\le122880000n^9\). This does not bound the gap.
- **Proved negative result:** an actual two-corruption entrance from the supplied corner, retaining mutation and acceptance probabilities, has a positive third-residence contribution at least \(2^n/[12288n^4(n+1)]\) for odd \(n\ge9\). Thus retaining mutation factors does not rescue that absolute-value bound. This is not a lower bound on the signed coefficient.
- **Candidate proofs, awaiting independent audit:** polynomial bounds for the isolated-pair second response and the full-process RROO term. The latter replaces the problematic \(M^3\) estimate with an \(M^2\) bound for closed pairs and separately handles the orphan-fed last pair.

The assumptions remain supplied corner \((2,1,2,\ldots,n)\), ideal extrema, pinned labels, ascending own-parent standard-bit mutation, activated bitwise observation noise, filled T=2/3 neighborhoods, and simultaneous alignment at full sweep boundaries.

**Remaining gaps:** RRRR and thirteen other mixed fourth-order terms still lack complete bounds here. The isolated-pair estimate cannot freeze the remaining population. No uniform higher-order remainder or enlarged noise window follows. Kernel disagreement, failure of the active-escape inequality, or a phase/stopped-reward counterexample would falsify the corresponding new argument.

**Verification:** 119 tests, compilation, whitespace, artifact hashes and relative links passed. Thirteen curated outputs reproduced byte for byte; 410 protected tracked entries remained unchanged. The new checks include 42 isolated pairs and 254 orphan-excess states. [Reproduction bundle](README.md), [checks](checks.json).

Earlier plans, receipts and seed separation replayed successfully; no repair was needed. Published ratios remain 2.327639 [2.050148, 2.674642] at n=256 and 2.339095 [2.085387, 2.596468] in the separate registered n=512 study, retaining their approximate nominal 95% intervals. The original cap, preregistration, **240 missing blocked holdout trials**, and inconclusive two-stage decision are preserved. No new scientific trajectories or seeds were generated.

Morning report: cumulative progress now extends audited cubic control with exact fourth-order values, a T=3 bound, two candidate cancellation bounds, and a stronger failed-method witness. Curated deliverables and STATUS/CLAIMS updates are complete. Elapsed: **2,070 seconds—34 minutes 30 seconds**; full replay: 608 seconds. One CPU, no network, paid resources, commit or push.

Next task: Independently audit the phase-aware RROO bound, especially the orphan-fed last pair, because its new stationary and stopped-reward cancellations remove the explicit M³ obstruction.
