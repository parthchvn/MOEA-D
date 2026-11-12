# Round 14 durable claim/status supplement

**C33: proved under the supplied pinned assumptions after independent audit.**
The round-13 candidate |C_n|<=10^10 n^7 holds for n>=3. C_n is the p^3
coefficient of the T=3 minus T=2 sweep-boundary completion-time gap from
(2,1,2,...,n), with ideal extrema, pinned labels, ascending own-parent
standard-bit mutation, activated bitwise observation noise and filled
cardinalities. The proof in [audit.md](audit.md) retains both bad-pair
acceptance factors and treats all six mixed R/O cubic words separately.
It does not imply a uniform fourth-and-higher remainder or a new noise window.

**C34: contradicted shortcut.** At an interior phase, subtract the local
first-future-boundary function F_v^(i), not the unshifted boundary function
f_v. For i>0, F_v^(i)(y)=f_v(y)-i/(n+1)+1{y=n}/nu_v(n). The n=4,
orphan-weight-zero, next-breeder-1 witness has the incorrect difference
-1/5 and the corrected excess zero. The earlier implementation already
subtracted phase values; this is an explicit repair of the written definition.
Stochastic split parameters also require a sufficiently small nonnegative
interval; a two-sided stochastic neighborhood would be false.

**Mechanically checked:** an independent phase-cycle solver, importing no
earlier response implementation, reproduces all 16 ordered cubic terms
at n=4,6 and their T=2 cubic sums. All 12 mixed terms match exact rational
hashes. The six mixed values retain their signs, including negative ORO.
The audit covers 238,166 two-birth support histories, 19,166 acceptance
inequalities, and 456 phase states including 100 with a bad pair. There
are 1,368 boundary excess identities, 8,856 phase-local identities, 8,856
R-annihilation identities, 11,808 excess upper/nonnegativity checks and
4,452 response/forcing inequalities. Literal genotype-mask tests also
verify the transition law and the n=3 exceptional cubics.

**Dependencies and empirical history preserved:** complete round-11 replay
recursively checks prior plans, published receipts, seed separation and
algebra. Round-12/13 manifests match. The large round-12 positive-p Schur
solve is not a premise and was not repeated. No dependency repair was needed.
The original n=256 ratio 2.327639 [2.050148,2.674642] and separate n=512
restricted-mean ratio 2.339095 [2.085387,2.596468] retain their earlier
approximate nominal 95% intervals. Original preregistration, capped main
trial, 240 missing blocked holdout trials and inconclusive two-stage decision
are unchanged. No new scientific trajectories or seeds were generated.

**Unresolved in this checkout:** the fourth-and-higher uniform remainder,
sharp cubic behavior, fixed-c ordering and ordinary initialization. The
exponential higher-residence obstruction remains valid. Next investigate
the fourth-order coefficient: two acceptance factors control M^2, but do
not by themselves control the M^3 residence factor appearing one order later.
