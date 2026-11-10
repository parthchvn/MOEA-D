# Round 17 durable claim/status supplement

**C42 — conjectured, complete candidate proof pending independent audit:**
for even n>=4, the supplied pinned T=2 ordered response ORRR satisfies
`|ORRR| <= 2048 (n+1)^3 (20n)^4/q = O(n^8)` in sweep units, where
`q=1-(1-d(2,0))(1-d(1,0))`. [proof.md](proof.md) gives the argument.

The new device subtracts the regular-correct population response at the
same orphan value and breeder phase. Its stopped equation includes an
aligned-boundary compensation. This yields a polynomial bound for the
acceptance-weighted marked second response. The initial orphan birth keeps
`d(n,y)d(y,n)` until after the clean occupation bound, so the latter factor
cancels the inverse orphan repair rate. Negative unchanged branches and
last-pair/orphan dependence remain included. Neither the isolated-pair
second-response candidate nor a new independence assumption is used.

**Mechanically checked C42:** 622 state cases, 3,734 phase cases, 3,053
identities and 7,708 inequalities at n=4,6. Exact ORRR values are
0.3049490187292804 and 0.3979640378737074 (rounded). The n=4 calculation
matches two separate published implementations and the published rational
hash. The n=6 value is newly calculated and lacks an independent fourth-order
oracle in this round. Finite checks do not supply the all-n proof.

**C43 — contradicted shortcut, exact finite witness:** the centered equation
cannot omit its aligned-boundary compensation. At n=4 the first two
compensations are approximately 2.071469580410 and 2.835341435438;
[flux.csv](flux.csv) preserves exact fractions. The incorrectly omitted
equation's residual equals this compensation. The actual runtime still
kills only at aligned phase zero, not at an interior aligned state.

**C40 — conjectured, unresolved here:** full fourth-order polynomiality does
not follow from the ORRR candidate. RRRR and the other untreated ordered
words, uniform higher remainders, fixed-positive-c ordering and ordinary
initialization remain separate obligations. The previously audited RROO
bound and positive exponential residence counterexamples are unchanged.

**Mechanically checked empirical dependencies:** the complete relevant
round-16 replay and its earlier recursive dependencies reproduce the plans,
receipts and seed separation; no repair was needed. The n=256 ratio remains
2.327639 [2.050148,2.674642], with 24 complete observations per arm. The
separately registered n=512 restricted-mean ratio remains
2.339095 [2.085387,2.596468], with 32 per arm. These retain their earlier
approximate nominal 95% bootstrap interpretation. The original cap,
preregistration, 240 missing blocked holdout trials and inconclusive original
two-stage decision are unchanged. No new scientific trajectories or seeds
were generated; no novelty claim or current-literature search is made.

The next bounded obligation is an independent audit of the new compensated
centering identity, surviving-overwrite budget and marked-response bound.
See [checks.json](checks.json) and [provenance.json](provenance.json) for final
verification and elapsed-time accounting.
