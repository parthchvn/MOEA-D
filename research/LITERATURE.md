# Literature map

This is a relevance map, not a comprehensive bibliography. Verify theorem assumptions in the primary source before transferring a result.

## Directly overlapping work

### Doerr, Elmoutassim, Krejca, and Kibulu (2026)

**Understanding the Co-evolutionary Solution Exchange of the MOEA/D: Already the Smallest Communication Radius Gives the Best-Possible Speed-Up.** [arXiv:2610.35373](https://arxiv.org/abs/2610.35373), posted 2026-10-26.

This is the highest-priority source. It studies mutation-only MOEA/D with Chebyshev decomposition into `n+1` uniformly weighted subproblems on OneMinMax. Its stated result is expected `Theta(n^2)` function evaluations for every communication radius `r >= 1` and `Theta(n^2 log n)` for `r = 0`, with standard bit mutation and archive coverage as the runtime event. Its proof predicts faster partial progress at larger radii without changing the full-front asymptotic order. This communication paper reports no experiments; the partial-progress statement is not empirical evidence.

Its quadratic upper-bound proof generalizes to a type-A mutation class that must produce a same-Hamming-weight offspring with probability at least a positive constant; this need not be a literal genotype copy. Standard bitwise mutation qualifies, in particular through zero-bit flips, while the repository's exact one-bit mutation does not. The repository must also compare archive coverage, update order, communication/acceptance semantics, and simultaneous alignment. The current conjecture is therefore not automatically contradicted, but failure of a sufficient proof condition is not evidence that the conjecture is true.

The independent 2026-11-02 source audit and controlled study are now recorded in
`PAPER_COMPARISON.md` and `reports/20261102T212758Z-radius-factorial.md`. The
canonical ascending-cycle map complements genotypes while retaining indices;
the unchanged-genotype index map reverses scan order. The printed min/max
inconsistency is explicit. Lazy one-bit with probability 1/2 satisfies type A.
For `r>=1`, a **proved source-based inference** from Lemmas 4–5 extends the
upper expectation argument to simultaneous alignment; it gives no automatic
tail bound. Apparent type-B constant/proof inconsistencies prevent silently
transferring a lazy lower bound. No finite experiment is used to establish
these source-based statements or any new asymptotic result.

A bounded search on 2026-11-02 found no newer directly relevant primary result
after the October 26 preprint, whose available history showed v1 only. This
does not assert comprehensive novelty. The 2×2 finite study supports a mutation
mechanism for radius sensitivity, while leaving exact one-bit asymptotics open.

**Source-reported proof structure, not a separately numbered partial-progress
theorem:** Section 4, Theorem 2 and Lemma 4 balance spread `O(n*ell/r)` against
improvement `O(n^2/(k*ell))`, choosing
`ell_k=min{ceil(sqrt(n*r/k)),k}`. The proof's early levels contribute
`O(n^2/sqrt(r))` and late levels contribute `O(n^2)`; its constants depend on the
fixed positive type-A parameters. These orders are proof ingredients, not a
tight finite level-time law or a fitted regression. Useful future diagnostics
include endpoint weight-level dwell times and how many neighboring breeders
share that endpoint value. See the [primary manuscript, Section 4](https://arxiv.org/html/2610.35373v1).
`NEXT_DIRECTIONS.md` preserves the original proposals and the independent
uniform-scheduler time-change argument. The later authorized two-arm lazy
broadcast ablation is completed in `reports/20261103T022831Z-broadcast-ablation.md`;
it supports finite broadcast contribution at fixed q=1/2, with exclusive mediation
still open. The next standard-bit two-arm/archive-primary design is saved in
`STANDARD_BIT_PROPOSAL.md`; it is proposed, not preregistered or launched. The
uniform-scheduler process remains unimplemented, and its identity does not
transfer to the cyclic studies.

### Zhang, Zhong, Zheng, and Doerr (2026)

**Superior Runtime Guarantees for the MOEA/D Multi-Objective Optimizer via Weighted-Sum Decomposition.** AAAI 2026. [DOI:10.1609/aaai.v40i43.41049](https://doi.org/10.1609/aaai.v40i43.41049).

**Source-reported conditional theorem:** Theorem 6 assumes `n>=8`, `c>500/3`,
`a>1`, and `c ln(n)<=H<=n^(a-1)-1`. Conditional on an event of probability at
least `1-3*n^(-(3*c/500-1))`, expected evaluations are at most
`e*(H+1)*(1+a ln(n))*n`. Thus the `O(n log^2 n)` statement for `H=Theta(log n)`
has a probability/conditioning qualification; it is not an unconditional
expectation bound. See the [primary paper, Theorem 6](https://ojs.aaai.org/index.php/AAAI/article/download/41049/45010).

The algorithm uses `H+1` evenly weighted weighted-sum maximization subproblems,
uniform initialization, sequential own-parent standard-bit mutation, no exchange,
and an all-offspring archive. Its scalar objective is
`(2i/H-1)w+(1-i/H)n`: subproblems favor endpoints, with a neutral middle when H
is even, rather than distinct target weights. This is a different decomposition
project, not a theorem transferable to the current communication radius.

### Doerr, Krejca, and Weeks (2024)

**Proven Runtime Guarantees for How the MOEA/D Computes the Pareto Front From the Subproblem Solutions.** PPSN 2024. [arXiv:2405.01014](https://arxiv.org/abs/2405.01014).

This work studies the phase in which subproblem optima do not already cover
the full front. Its `N+1` equidistant Chebyshev subproblems use own-parent
sequential updates without exchange and an all-offspring archive; the generic
algorithm updates its reference point, which requires reconciliation before a
local implementation. **Source-reported bounds:** standard-bit mutation gives
total `O(n*N*log n+n^(n/(2N))*N*log n)`; a stated lower bound concerns the phase
starting from all subproblem optima, under its divisibility assumptions, and
must not be relabeled a full-run lower bound. Power-law exact-K-bit mutation
with exponent `beta in (1,2)` gives total `O(n*N*log n+n^beta*log n)`.
[Primary manuscript, v2](https://arxiv.org/html/2405.01014v2).
This is relevant if N<n leaves missing archive points, but does not settle the
current `N=n` communication/alignment model.

### Doerr, Krejca, and Weeks (2026): dynamic decomposition

Benjamin Doerr, Martin S. Krejca, and Noé Weeks, **A Dynamic Decomposition
Strategy for the MOEA/D With Proven Performance Guarantees**,
[arXiv:2610.35334v1](https://arxiv.org/html/2610.35334v1), posted 2026-10-26.

**Source-reported theorem:** Theorem 2 gives expected `O(n^4)` evaluations for
distorted LOTZ objectives `(u(LeadingOnes),v(TrailingZeros))` with arbitrary
monotonically increasing u,v. The stated setting permits standard-bit and exact
one-bit mutation. Algorithm 2 starts with two endpoint weights, uses dynamic
max-Chebyshev weights/reference, sequential own-parent mutation and full
communication, and inserts/deletes subproblems using objective-space gaps and
redundancy. Its archive processes both initialized solutions and every offspring,
retaining nondominated objective values, and helps initialize inserted
subproblems; runtime is checked at main-loop boundaries.
These assumptions differ from fixed `n+1` subproblems on OneMinMax, so this
same-day result does not settle the current mechanism. It is context for a
later separate project, not an immediate extra factor in the ablation. Appendix B
contains experiments despite a stale no-experiments checklist in that manuscript.

## Noise and no-reevaluation foundations

### Dinot, Doerr, Hennebelle, and Will (2023)

**Runtime Analyses of Multi-Objective Evolutionary Algorithms in the Presence of Noise.** IJCAI 2023. [DOI:10.24963/ijcai.2023/616](https://doi.org/10.24963/ijcai.2023/616).

They prove that SEMO without reevaluation covers the OneMinMax front in `O(n^2 log n)` expected iterations for one-bit prior noise `p <= alpha/n`. Their population, dominance rule, and historical/current coverage mechanics differ from MOEA/D. The proof is a source of techniques and warnings, not a theorem that automatically transfers.

### Antipov and Doerr (2025)

**Evolutionary Algorithms Are Significantly More Robust to Noise When They Ignore It.** IJCAI 2025; [arXiv:2409.00306](https://arxiv.org/abs/2409.00306).

They analyze the `(1+1)` EA on LeadingOnes without reevaluation and prove robustness to constant noise rates in that setting. The paper supports the broad possibility that stored noisy fitness can be robust, but the objective, potential, and selection process differ from this project.

### Doerr, Johannsen, and Winzen (2012)

**Multiplicative Drift Analysis.** Algorithmica 64, 673-697. [DOI:10.1007/s00453-012-9622-x](https://doi.org/10.1007/s00453-012-9622-x).

This supplies the drift theorem used by the local draft. Applying it requires a valid state potential and conditional drift for every relevant nonzero state; it does not justify conditioning shortcuts or an unproved tail bound for a maximum over subproblems.

## Literature-review protocol

For each candidate source, record:

- exact algorithm and mutation operator;
- decomposition and reference point;
- population/archive semantics;
- neighborhood/communication rule;
- runtime event and cost unit;
- theorem assumptions and bound;
- which local claim it supports, challenges, or leaves untouched.

Search by citations in the newest directly overlapping paper before broad keyword search. Prefer proceedings, journal pages, DOI records, and arXiv manuscripts over secondary summaries.
