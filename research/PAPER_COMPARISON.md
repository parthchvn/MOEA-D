# Comparison with the October 2026 communication-radius preprint

Primary source: Benjamin Doerr, Moaad Elmoutassim, Martin S. Krejca, and Guy Mushiata Kibulu, **Understanding the Co-evolutionary Solution Exchange of the MOEA/D: Already the Smallest Communication Radius Gives the Best-Possible Speed-Up**, [arXiv:2610.35373](https://arxiv.org/abs/2610.35373), posted 2026-10-26.

The independent primary-source audit was completed on 2026-11-02 against
[arXiv v1 HTML](https://arxiv.org/html/2610.35373v1) and the
[primary PDF](https://arxiv.org/pdf/2610.35373), DOI
[10.48550/arXiv.2610.35373](https://doi.org/10.48550/arXiv.2610.35373).
Source loci: Section 3, Equation (1) and Algorithm 1 (printed page 5), runtime
definition (pages 5–6), Theorem 1 (page 6), type A/Theorem 2 (page 7), Lemma 5
(page 8), and appendix Lemma 4 (pages 19–21).

Source descriptions were independently verified against the cited locations;
they are statements reported by the primary source, not mechanical checks.
The transformations below are **proved** algebraically and **mechanically
checked** in unit tests.

| Aspect | Legacy `large.run` | October 2026 preprint | Consequence |
|---|---|---|---|
| Benchmark | OneMinMax with `n+1` subproblems | Same | Directly comparable. |
| Decomposition | Chebyshev/Tchebycheff cost with target weight `j` | Chebyshev decomposition with one target per Pareto value | The piecewise costs agree after `k_paper=n-j_large` and `zeros=n-w`. The PDF appears to print `min` in both its general definition and Equation (1), although the unique-minimizer statement and later lemmas require `max`; record this as an apparent source typo, not a silent code change. |
| Initialization | Independent binomial Hamming weights induced by uniform bit strings | Independent uniformly random bit strings | Equivalent at the weight-state level. |
| Parent/subproblem selection | Cyclical sweep over every subproblem; mutate that breeder's own incumbent | Uniform or cyclical selection | Complement genotypes and retain indices to preserve ascending cyclic order. The same-genotype index reversal instead reverses order. This differs from `sim.py`, which chooses a random neighborhood parent. |
| Mutation | Flip exactly one bit; Hamming weight always changes by `+1` or `-1` | Main theorem uses standard bitwise mutation; upper proof covers type-A operators | Critical difference. Type-A requires constant probability of a same-Hamming-weight offspring, not necessarily a literal genotype copy. Exact one-bit mutation has probability zero. |
| Communication | Offer each offspring to every subproblem within symmetric radius `r`; accept on non-worsening cost | Same radius interval and non-worsening replacement | Checked: Algorithm 1 offers directly to all neighbors, without a breeder-acceptance gate. |
| Ties | Accepted | Accepted | Comparable. |
| Boundary neighborhoods | Clipped symmetric intervals | Clipped symmetric intervals | Comparable when both use radius `r`; do not rename this uniformly as size `T`. |
| Archive | None | Archives every initialized individual and every generated offspring, including offspring rejected by replacement | Critical difference for the runtime event and for a faithful controlled variant. |
| Runtime event | All current subproblem states simultaneously satisfy `w[j] = j` | Archive has witnessed every Pareto-front value | `large.py` uses a stronger event; archive coverage can occur earlier and persists. |
| Cost unit | Sweeps, with one evaluation per subproblem per completed sweep; initialization is not counted and stopping is checked at sweep boundaries | Function evaluations including initialization; archive completion can occur on an individual offspring | `sweeps*(n+1)` is not an exact paper-equivalent count. A controlled implementation must count the `n+1` initialization evaluations and check archive completion per generated offspring. |
| Claimed radius result | Conjectured `Theta(n + (n/T) log(1+n/T))` sweeps | Proved `Theta(n^2)` evaluations for all `r >= 1`; `Theta(n^2 log n)` for `r=0` | Potential conflict becomes a research question about the missing weight self-loop and stopping semantics. |

## Mechanistic difference

The preprint's type-A condition explicitly requires `Pr(|mutation(x)| = |x|) >= alpha` for a positive constant `alpha`. Standard bitwise mutation satisfies this, in particular through zero-bit flips. Exact one-bit mutation has no weight self-loop. This makes same-weight offspring a plausible mechanism to test, but violating a sufficient theorem assumption does not establish a different runtime.

## Minimal controlled study

Implement, test, and compare four variants while holding decomposition, cyclic order, initialization, and radius fixed:

1. exact one-bit mutation + simultaneous alignment (legacy `large.run` event);
2. exact one-bit mutation + archive coverage;
3. lazy one-bit mutation with preregistered weight self-loop probability `1/2` + simultaneous alignment;
4. lazy one-bit mutation with preregistered weight self-loop probability `1/2` + archive coverage.

For archive variants, archive all initialized weights and every generated offspring weight, even when replacement rejects it. Optionally add standard bitwise mutation as a fifth validation against the paper. Measure `r=0`, `r=1`, and `r=ceil(log2(n))` over increasing `n`, count initialization evaluations, and check archive completion per evaluation. This factorial design isolates whether the weight self-loop, stopping event, or their interaction drives the different empirical law.

Do not claim new asymptotics from this experiment alone. Its purpose is to select the correct conjecture and proof mechanism.

## Frozen canonical process and exact transformations

**Proved:** let `C_j(w)=max{j(n-w),(n-j)w}`. Below `w=j` the first
branch strictly decreases (unless the branch is empty at an endpoint); above
`j` the second strictly increases. Thus `j` uniquely minimizes `C_j` on
`{0,...,n}`. Non-worsening replacement makes a target hit permanent.

The paper measures zeros `q` and indexes targets by `k`. Its displayed
piecewise formula is `n*g_k(q)=max{k(n-q),(n-k)q}`. With unchanged genotypes,
`q=n-w` and `k=n-j` give `n*g_(n-j)(n-w)=C_j(w)`. This map preserves clipped
radius neighborhoods but reverses an ascending breeder scan. It alone does
not establish same-order sample-path identity.

The canonical order-preserving map is `x_paper=1-x_code`, `q_paper=w_code`,
and `k_paper=j_code`. It gives `n*g_j(w)=C_j(w)` and preserves the ascending
scan, uniform initialization, exact/lazy one-bit weight transition laws,
neighbors, ties and replacement. This is a distributional conjugacy, not an
assertion that the same random seed reproduces the paper's bit-level generator.
The controlled implementation uses this map. The graph remains a clipped path;
"cyclic" refers only to repeatedly scanning indices `0,...,n`.

**Contradicted (literal printed formula):** the paper prints `min` in the
general scalarization and Equation (1), inconsistent with its piecewise formula
and unique-minimizer statement. At `n=2,k=1,q=0`, normalized `min` gives zero
where the piecewise branch gives one. We explicitly use `max`, as required by
those branches and Lemma 3; the source itself is not edited.

**Proved:** the local draft at `N=n` uses
`D_i(w)=max{iw,(n-i)(n-w)}/n=C_(n-i)(w)/n`. In contrast `sim.py` implements
absolute distance: at `n=3,j=1`, weights zero and two tie in distance but have
Chebyshev costs three and four. That process is excluded from the controlled
study and cannot serve as its independent scalarization oracle.

**Proved:** every incumbent is an initialized or generated solution, so a
passive all-offspring archive covers every current incumbent. Hence pathwise
`T_archive <= T_alignment`. The inequality can be strict at initialization:
`n=1`, state `[1,0]` covers the archive but is misaligned. Recording both first
times on one trajectory does not change its population transitions.

## What the primary arguments transfer

**Proved (source-based inference, radius `r>=1`):** lazy one-bit mutation satisfies type A
with `C_A=alpha=1/2`; exact one-bit has zero probability of a same-weight
offspring and fails that sufficient condition. A same-weight offspring need
not copy its genotype, though this controlled comparator does copy at weight
level. Lemma 5's proof establishes every subproblem's optimum using Lemma 4.
Use the filtration generated by initial weights and the gate/direction uniforms
actually consumed by each completed offspring (prefetched but unused uniforms
are not revealed). Condition on this history after both endpoints are solved.
Grow a solved prefix only to `ceil(n/2)` and a solved suffix only down to
`floor(n/2)`. Each scheduled solved-frontier breeder then extends its half-front
with conditional probability at least `C_A/2` per visit using fresh randomness;
`r>=1` ensures communication to the adjacent target. Visits are at most `n+1`
evaluations apart. At most n such stages, each with expected delay at most
`2(n+1)/C_A` given the preceding history, give an `O(n^2)` fill expectation.
Combine this with Lemma 4's endpoint expectation. No drift theorem or tail
argument is added here.
Together with unique-minimum persistence, its upper expectation argument also
covers simultaneous alignment for the canonical lazy model. This is an
inference from the proof, not the paper's explicitly stated archive runtime
event. No tail bound follows automatically, and failure of type A gives no
lower bound for exact one-bit mutation.

The lazy comparator changes same-weight availability and active-mutation
frequency together. It does not reproduce standard bit mutation's multi-bit
jumps or state-dependent same-weight probabilities. Raw speedups at all radii
are not implied; the study uses radius-sensitivity contrasts to expose this
limitation, with radius zero as a contextual control.

**Contradicted universal stopping equality:** even positive radius and an
initially incomplete archive do not imply equal event times. With `n=3,r=1`,
initialize `[1,1,1,2]` and follow feasible cyclic offspring weights
`[0,0,0,3,1,2]`. After the fourth offspring (evaluation 8), the population is
`[0,1,3,3]` and the archive is complete. Alignment first occurs at evaluation 10,
with `[0,1,2,3]`. The path has positive probability under exact one-bit and under
lazy one-bit when these six calls use its moving branch. This was independently
checked by both reviewers and added as a deterministic regression test. Zero
sampled gaps in the recorded positive-radius cells therefore remain finite
empirical evidence, not an event-identity theorem.

**Open source ambiguity:** type B (page 8, Theorem 6) prints `C_B in (0,1)`,
while Lemma 7 (page 9) uses a constant greater than one. Exact/lazy one-bit
cannot satisfy the literal fixed-constant condition: from `q=1`, conditioning
on `q' != 1` gives `Pr(q' in [2,i])=1-1/n`; taking `i=n` forces
`C_B >= n/(n+1)`. Lemma 7 additionally mixes no-flip and same-weight
probabilities. The finite study neither repairs these apparent issues nor
transfers a `Theta` lower bound to lazy one-bit mutation. The paper's printed
main theorem for standard bit mutation is reported as its result.

The literature reviewer searched title/identifier and arXiv communication-radius
and OneMinMax queries on 2026-11-02, including work after 2026-10-26. No newer
directly relevant primary result was identified; v1 was the only version found.
This is a bounded search, not a comprehensive novelty claim.
