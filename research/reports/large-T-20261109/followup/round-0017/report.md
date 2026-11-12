**Candidate proof:** ORRR has the polynomial bound
\[
|\mathrm{ORRR}|\le \frac{2048(n+1)^3(20n)^4}{q}=O(n^8),
\qquad q=1-(1-d(2,0))(1-d(1,0)),
\]
for even \(n\ge4\), in sweep units. Here \(d\) is the standard-bit mutation weight kernel. The [argument](proof.md) retains the wrong-orphan entrance factor \(d(n,y)d(y,n)\).

The new step centers responses against the regular-correct population at the same orphan value and breeder phase. An explicit boundary compensation makes the stopped equation valid. This accommodates dependence between the orphan and the last pair.

**Mechanically checked exact results**, rounded:

| n | ORRR | Verification |
|---:|---:|---|
| 4 | 0.3049490187292804 | Two independent solver comparisons; published exact hash matches |
| 6 | 0.3979640378737074 | New exact calculation and replay; no independent fourth-order oracle |

Checks cover **622 state cases, 3,734 phase cases, 3,053 identities and 7,708 inequalities**. These are deterministic calculations, without sampling uncertainty or censoring.

**Contradicted shortcut:** omitting the boundary compensation fails. At \(n=4\), the first two omitted-equation residuals are approximately **2.071469580410** and **2.835341435438**; [exact fractions](flux.csv) are preserved.

**Assumptions and proof gaps:** supplied corner `(2,1,2,…,n)`, ideal extrema, pinned labels, ascending own-parent standard-bit mutation, activated bitwise observation noise, filled cardinality \(T=2\), and simultaneous alignment at full sweep boundaries. Independent audit must validate the compensated centering identity, overwrite budget and marked-response bound. A failed phase identity, missing acceptance factor or independent coefficient mismatch would falsify the corresponding step. Polynomiality of the **full fourth-order gap remains conjectured**; no uniform remainder or enlarged noise window follows.

Earlier plans and receipts replayed successfully; **no dependency repair was needed**. Published empirical ratios remain **2.327639 [2.050148, 2.674642]** at \(n=256\), with 24 complete observations per arm, and **2.339095 [2.085387, 2.596468]** in the separate \(n=512\) study, with 32 per arm. These retain their approximate nominal 95% bootstrap interpretation. The original preregistration, capped trial, **240 missing blocked holdout trials**, and inconclusive two-stage decision are unchanged. No new scientific trajectories or seeds were generated.

**Verification and accounting:** 131 tests and compilation passed. Six generated outputs reproduced byte for byte; all 443 protected tracked files remained unchanged. The [14-file bundle](README.md) and local STATUS/CLAIMS updates are complete. Packaging took **1,464 seconds—24 minutes 24 seconds**; full replay took **612.6 seconds**. One CPU, no scientific/test failures, network, paid resources, commit or push.

Morning report: cumulative progress now includes audited empirical comparisons, polynomial response control through cubic order, audited RROO control, and this new ORRR proof candidate.

Next task: Does an independent audit validate the compensated centering identity and marked-response bound, since these new steps carry the candidate polynomial ORRR estimate?
