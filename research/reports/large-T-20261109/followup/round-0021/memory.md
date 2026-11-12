# Proposed claim and status updates — round 21

These are proposals only. Existing CLAIMS.md, STATUS.md, reports, registrations,
and evidence were not edited. Status labels below distinguish analytic proof,
finite exact checks, and unresolved implications. Novelty is UNVERIFIED.

| Proposed entry | Status | Precise scope / evidence |
|---|---|---|
| Filled donor graph transition at T=3 | **Proved; mechanically checked** | T=2 consists of pairs, with a source orphan at even n; T>=3 contains the bidirectional adjacent path. Odd T can still have nonreciprocal filled-boundary edges. Formula and 91,518 independent row checks in proof.md / verification.json. |
| Surviving correct slot protects clean repair | **Proved; mechanically checked** | Pinned ideal reference/labels, p=0, cyclic own-parent standard-bit mutation, T>=3: from m_e<=n errors, boundary mean <=3n m_e sweeps, plus one from an interior phase. Does not give noisy persistence. |
| Large-T all-wrong clean trap family | **Proved; mechanically checked** | For a=ceil((n+1-T)/2), the explicit polarized state has exact first-change mean 1/q >=a!/(n+1). Accessible from the corner by a prescribed p^(n+1) path with mask factors retained. Not a lower bound for noisy corner runtime or ordinary initialization. |
| Uniform clean worst-state bound and parity effect | **Proved; mechanically checked** | For T>=3, sup_w E tau <=4*2^a_star*a_star!+3n^2, a_star=a+1{even T, n=3 mod 4, T<n+1}. Polynomial if b log(b+1)=O(log n), superpolynomial if b log(b+1)=omega(log n), b=n+1-T. All-n derivation in proof.md, not grid extrapolation. |
| Uniform fixed-order supplied-corner response for T>=3 | **Proved; mechanically checked in eight tiny coefficients** | For 1<=j<n, |h_j(C)| <=2^j(n+1)^j[3n(j+1)+1]^j/q_T =O_j(n^(2j+1)). Each pinned insertion creates at most one error. No uniform higher-order remainder, noise window, fixed-positive-c ordering, or T=2 fourth-gap theorem. |
| Growing-T consequence of the published donor/forest argument | **Proved algebraic consequence of cited round-5 bound** | At p=c/n, natural-log T gives O_c(n^(2+c)log n) attempts; sqrt T gives O_c(n^(5/2)exp(c sqrt n)); full T gives O_c(n^3 exp(cn/(1-c))) for fixed 0<c<1. Artificial-family simultaneous emptiness is the step causing the exponential factor. This round does not independently recertify the entire old forest construction. |
| Strong connectivity alone excludes slow clean states | **Contradicted** | Polarized all-wrong states at T>=3, including logarithmic and square-root T, have factorial first-change residence. Strong connectivity helps after a correct seed exists. |

Proposed STATUS supplement: the useful distinction is now surviving-correct-slot
repair versus total loss of correct slots, rather than more isolated T=2 words.
Both a positive uniform lemma and an explicit slow family are available for
larger cardinalities. Exact checks use capped clean subsets (<=256 states) and
a tiny phase solver (<=1024 phase states), with no full population matrix.

Retain earlier negative evidence: acceptance conditioning can be biased;
within-sweep alignment can be reinfected; T=2 higher-residence moments and
absolute majorants can be exponential; small-n noisy T-monotonicity fails.
Nothing here converts clean hitting into noisy persistence or entrance mass
into typical frequency. Ordinary initialization and fixed-positive-c
growing-T noisy completion remain unresolved in this checkout.

The original 240 gate-blocked holdout observations remain blocked. No new
Monte Carlo plan was needed or executed, no seeds were generated, and no
empirical estimates were changed or re-certified in this round.

Best next bounded question: bound the acceptance-weighted cost of losing the
last correct slot before completion at T=ceil(sqrt(n)), p=c/n, from the pinned
corner. This targets the gap between the new clean protection and the old
artificial-family synchronization bound; entrance factors and subsequent
noisy escape must both be retained.
