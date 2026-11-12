# Round 16 durable claim/status supplement

**C39 — proved within the supplied pinned model, upgraded from candidate:**
the phase-aware ordered full-T=2 word RROO satisfies
|RROO|<=5000(n+1)^2(20n)^4/q for even n>=4, where
q=1-(1-d(2,0))(1-d(1,0)). Time is in sweeps. An independent analytic
audit validates the closed-pair stationary cancellation and the separate
orphan-fed stopped-reward argument, including all phases and the negative
unchanged branch. See [audit.md](audit.md).

**Mechanically checked C39:** a separately written sweep-product/triangular
solver reproduces both published RROO fractions at n=4,6 and all 254
overlapping excess fractions. The expanded grid covers 408 states and
3,188 phases at n=4,6,8,10, including 240 orphan-fed states, with 31,552
checks. Twenty-four stationary horizons at n=4,6,8,12 also pass. These
finite checks support reproducibility; the all-n bound rests on the proof.

**C41 — contradicted shortcut, proved finite witness:** regular completion
and orphan repair need not be independent. At n=4, state (0,1,2,0,0), next
breeder 4, the next clean turn completes regular slots with probability
3/64 and repairs the orphan with probability 1/256, with zero intersection.
The product is 3/16384. The audited stopped-reward proof permits this
dependence. This witness refutes no previous properly qualified bound.

**C38 — candidate proof unchanged:** the isolated-pair second-response
estimate from round 15 has not been independently audited in this round
and is not used to prove C39.

**C40 — conjectured, unresolved here:** polynomiality of the full fourth
gap D_n remains unproved in this checkout. RRRR and thirteen other mixed
fourth words still need bounds. The opposite ordering ORRR is a concrete
remaining problem: an orphan birth precedes three regular insertions.
Neither a uniform higher remainder nor a new noise window, fixed-c
ordering, or ordinary-initialization theorem follows from C39.

**Mechanically checked empirical dependencies:** the earlier registered
plans, receipts, seed separation and blocked holdout replay successfully;
no repair was needed. The n=256 ratio remains 2.327639
[2.050148,2.674642] with 24 complete observations per arm; the separate
registered n=512 restricted-mean ratio remains 2.339095
[2.085387,2.596468] with 32 per arm. Intervals retain their earlier
approximate nominal 95% interpretation. The original capped trial,
preregistration, 240 missing blocked holdout rows and inconclusive
two-stage decision remain unchanged. No new scientific seeds or trajectories
were generated. This offline audit makes no novelty claim.
