# Proposed claim and status updates — round 22

Proposals only: existing CLAIMS.md, STATUS.md, sources, plans and evidence
were not edited. No empirical claim is promoted to a theorem. Novelty is
UNVERIFIED, and this round has no independent reviewer verdict.

| Proposed claim | Status | Exact scope and limitation |
|---|---|---|
| Reciprocal phase potential tolerates ongoing external corruption | **Proved; mechanically checked** | Pinned ideal reference/labels, standard-bit own-parent cyclic mutation and shared activated bitwise noise. For delta_k=1-(d_k+1)p>0, first repair of slot k is bounded by m[1/D(w_k,k)+g_k(phase)]/delta_k attempts. Other slots evolve normally. |
| Last-correct-slot loss has a uniformly bounded acceptance-weighted first residence | **Proved; mechanically checked** | Before an eligible proposal from parent x to the unique correct k, expected subsequent unseeded attempts, multiplied by its entrance indicator, are at most J=mp[1-D(x,k)+g_k(i+1) sum_{y!=k}D(x,y)D(y,k)]/delta_k. This is not a bound conditional on acceptance. |
| Growing-T zero-seed occupation has constant overhead at p=c/n | **Proved; mechanically checked in finite kernels** | If delta_min>0, E Z_H<=kappa E V_H from any pinned seeded state, kappa=2mp(1-p)/[1-(d_max+1)p]. For fixed c and T=o(n), including ceil(sqrt n), kappa=2c+o(1). H is any deterministic attempt horizon; simultaneous completion remains a boundary event. No total runtime bound follows without controlling seeded time. |
| Full communication gives uniform fast reseeding | **Proved; mechanically checked** | T=n+1, p<1: every inactive gate creates a seed, so E L<=1/(1-p). The last-loss/final-pinning charge is at most p/(1-p), with no degree condition. This is only the reseeding event, not simultaneous completion. |
| Final-pinning entry can be charged without conditioning away selection | **Proved; mechanically checked** | The final pin can newly pin only one target. With R_H the pre-attempt pin-ready opportunities, E Z_H<=B_init+kappa E(R_H+V_H). For ordinary uniform-bit initialization B_init<=mp(1-2^-n)/delta_0. This is unconditional and does not bound typical entry states or pre-U/S runtime. |
| Ongoing noise makes every all-wrong state repair quickly | **Contradicted** | At T<m, the polarized supplied state has expected first reseeding >=a!/[(1-p)+p2^a] attempts, a=ceil((m-T)/2). For T=o(n), p=c/n this lower bound is exp((1/2+o(1))n log n). Positive entry mass does not make it an ordinary-initialization runtime lower bound. |

Proposed STATUS supplement: the previous round's proposed last-seed-loss
question now has an actual-real-p occupation answer, uniform over T=o(n).
The catastrophic all-wrong clean traps remain slow even with ongoing noise,
but their first-moment cost after an actual last-seed loss is controlled by
the acceptance factor. Their contribution cannot exceed a constant multiple
of vulnerable seeded occupation at p=c/n. The remaining total-runtime gap
is noisy seeded progress and its exit distribution, rather than an unweighted
bound over all supplied unseeded states.

Keep the fixed-T supplied-corner theorem, growing-T questions, ordinary
initialization, and noiseless radius literature distinct. Retain earlier
negative results: acceptance-conditioning bias, within-sweep reinfection,
nonmonotonic finite-n T comparisons, and exponential higher-residence/absolute-
majorant obstructions. This is a first-moment result, with no total-runtime tail theorem,
Taylor coefficient, remainder, or fixed-positive-c arm ordering.

No Monte Carlo study was registered in round 21, so none was run. Existing
empirical estimates and 240 blocked holdout observations were neither sampled
nor newly recertified. Reproduction and finite scope are in README.md,
verification.json and checks.json; the proof and explicit self-audit are
proof.md and audit.md.

Best next bounded question: control noisy **seeded** occupation from the
pinned corner at T=ceil(sqrt n), p=c/n using the geometry of consecutive
wrong slots and their actual entrance weights. This would supply the missing
quantity in the new constant-overhead decomposition and could turn it into
a total-runtime bound.
