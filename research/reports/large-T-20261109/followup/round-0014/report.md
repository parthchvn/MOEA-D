**Proved within the supplied pinned model:** the candidate cubic bound survives independent audit:
\[
E\tau_3-E\tau_2=pA_n+p^2B_n+p^3C_n+O_n(p^4),
\qquad |C_n|\le10^{10}n^7,\quad n\ge3.
\]
The [analytic audit](audit.md) retains both acceptance factors and checks all six mixed terms separately.

**Mechanically checked:** an independent phase-equation solver reproduces these signed T=2 cubic components exactly; decimals below are rounded.

| Term | n=4 | n=6 |
|---|---:|---:|
| RRO | 3.182273 | 6.434594 |
| ROR | 0.098767 | 0.133758 |
| ROO | 2.371062 | 4.189576 |
| ORR | 0.300182 | 0.283948 |
| ORO | −0.701751 | −1.226489 |
| OOR | 0.770812 | 1.096540 |

All 16 words, including RRR and OOO, match published rational hashes. Additional checks cover **238,166 two-birth histories**, **19,166 acceptance inequalities**, and **456 phase states**, including 100 bad-pair states.

**Contradicted shortcut:** subtracting the boundary orphan hitting function unchanged at an interior phase can produce a negative “excess.” An exact n=4 witness gives −1/5. Subtracting the corresponding phase hitting function gives zero and restores the cancellation. The earlier implementation already used phase-to-phase subtraction; this audit makes the written definition explicit.

**Assumptions:** supplied corner `(2,1,2,…,n)`, ideal extrema, pinned labels, ascending own-parent standard-bit mutation, activated bitwise observation noise, filled T=2/3 cardinalities, and simultaneous alignment at full sweep boundaries. Time is measured in sweeps.

**Verification:** 123 tests passed, compilation and whitespace checks passed, and six curated outputs reproduced byte for byte. All **385 protected tracked entries** remain unchanged. Earlier registrations, receipts and seed separation replayed successfully; no dependency repair was needed. [Reproduction bundle](README.md), [checks](checks.json).

**Published empirical evidence remains unchanged:** the original n=256 ratio is 2.327639 [2.050148, 2.674642], with 24 complete observations per arm; the separately registered n=512 restricted-mean ratio is 2.339095 [2.085387, 2.596468], with 32 per arm. These retain their earlier approximate nominal 95% intervals. The original capped trial, preregistration and **240 missing, blocked holdout trials** are preserved; its two-stage decision remains inconclusive. No new scientific trajectories or seeds were generated.

**Remaining proof gaps:** a uniform fourth-and-higher remainder, sharp cubic behavior, fixed-positive-c ordering, and ordinary-initialization behavior. No enlarged noise window follows. Missing acceptance factors, failed phase cancellation or stopped-reward identities, or an exact coefficient exceeding the bound would falsify the corresponding argument.

Morning report: cumulative progress now includes audited empirical evidence and polynomial response bounds through cubic order, while preserving the higher-residence counterexample. Curated outputs and STATUS/CLAIMS updates are complete. Packaging took **858 seconds—14 minutes 18 seconds**; full replay took 101.3 seconds. One CPU, no network, paid resources, commit or push.

Next task: Determine whether the fourth-order supplied-corner coefficient remains polynomial after signed cancellation, because the audited two-entry estimate controls M² but not the next M³ residence factor.
