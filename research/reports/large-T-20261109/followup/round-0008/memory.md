# Round 8 claim and status supplement

**C27: proved finite-n identity; mechanically checked coefficients.**
For the supplied pinned corner and T in {2,3}, in sweep units,
m_3-m_2=p A_n+p^2 B_n+O_n(p^3). B is half the second derivative.
Writing P_j for the coefficient of p^j in the full, cyclic sweep kernel,
h_0 for the clean hitting mean and h_1=(I-Q_0)^(-1)Q_1h_0,
b_T=q^(-1) (P_1h_1+P_2h_0)(C), B_n=b_3-b_2. Clean boundary states with at
most three wrong coordinates suffice. Aligned intermediate states must be
retained. Attempts multiply these coefficients by n+1.
Exact rational arithmetic gives B_3=+0.4281536262425913 and
B_4=-1.8401743256595924. Deterministic float64 values through n=12 are
descriptive mathematical evaluations, not certified enclosures or experiments.

**C28: candidate proof, not independently audited.**
The complete proposed argument in [derivation.md](derivation.md) bounds
|B_n|<=1536n^5 for every n>=3. Regular clean states have mean at most 6n;
inverse own-repair probabilities cancel against the accepted-noise mass.
The even-n T=2 orphan requires a separate argument. Its autonomous own-turn
chain has invariant law (1-p)delta_n+pD(n,.); a discounted resolvent controls
the orphan-only coefficient. A predictable orphan-repair count controls the
mixed insertion terms. The mixed bound and ordering are the priority for
independent audit; finite successful checks do not prove them for all n.

**C29: proved conservative remainder/sign window.**
For m=n+1, M=m n^n, d(p)=(1+2p)^m-1, the Neumann-series majorant gives
an explicit cubic-and-higher remainder whenever Md(p)<1. If the exact A_n<0,
then the gap is negative for
0<p<=min{1/(8mM), |A_n|q/(64m^2M^2)}.
For all sufficiently large n, the audited first-order result implies at least
the window p<=log(n)/[768(n+1)^4 n^(2n)]. The eventual n threshold is not
made explicit. This is an extremely small n-dependent window, not a
fixed-positive-c result at p=c/n. The candidate polynomial bound makes only
the quadratic term negligible at p=o(log(n)/n^4); higher orders on that scale
remain unresolved by this evidence.

**Contradicted shortcut, preserved:** at even n and T=2 the last slot has no
external donor. A sole true-weight-0 error there has clean mean n^n, so a
uniform O(n) bound for every one-error state is false. This is why a generic
regular-state argument cannot simply include that endpoint. A larger attempted
float64 grid was interrupted without retained outputs; no conclusion uses it.

**C19/C20 and published evidence unchanged.**
The original n=256 ratio remains 2.327639 [2.050148,2.674642], with 24 complete
observations per arm. The separate previously registered n=512 ratio remains
2.339095 [2.085387,2.596468], with 32 complete observations per arm. These are
the existing approximate nominal 95% bootstrap intervals. The original main
still contains one capped trajectory, and all 240 original holdout trajectories
remain missing and gate-blocked; its two-stage decision is inconclusive.
Prior registrations, receipts, seed separation and all required earlier
outputs replayed successfully. No dependency repair, new trajectory, new seed,
network access, paid resource, commit or push occurred.

**Remaining obligations:** independently audit C28, then establish a useful
uniform third-and-higher-order remainder. All-n signs of A from n=4 and of B,
ordinary initialization, pre-S mechanisms and growing cardinality are outside
this checkpoint. A failed literal transition, exact response comparison,
regular/suffix inequality, or |B_n|>1536n^5 would falsify the corresponding
step. C25/C26's audited first-order status and C21–C24's earlier scoped results
remain unchanged. Their details reside in the prior published supplements.
