# Comparison with the October 2026 communication-radius preprint

Primary source: Benjamin Doerr, Moaad Elmoutassim, Martin S. Krejca, and Guy Mushiata Kibulu, **Understanding the Co-evolutionary Solution Exchange of the MOEA/D: Already the Smallest Communication Radius Gives the Best-Possible Speed-Up**, [arXiv:2610.35373](https://arxiv.org/abs/2610.35373), posted 2026-10-26.

This is an initial audit to be verified against the full paper and implementation variants.

| Aspect | `large.py` | October 2026 preprint | Consequence |
|---|---|---|---|
| Benchmark | OneMinMax with `n+1` subproblems | Same | Directly comparable. |
| Decomposition | Chebyshev/Tchebycheff cost with target weight `j` | Chebyshev decomposition with one target per Pareto value | The piecewise costs agree after `k_paper=n-j_large` and `zeros=n-w`. The PDF appears to print `min` in both its general definition and Equation (1), although the unique-minimizer statement and later lemmas require `max`; record this as an apparent source typo, not a silent code change. |
| Initialization | Independent binomial Hamming weights induced by uniform bit strings | Independent uniformly random bit strings | Equivalent at the weight-state level. |
| Parent/subproblem selection | Cyclical sweep over every subproblem; mutate that breeder's own incumbent | Uniform or cyclical selection | Cyclical mode is directly comparable in order, modulo stopping and mutation. This differs from `sim.py`, which chooses a random parent from the breeder's neighborhood. |
| Mutation | Flip exactly one bit; Hamming weight always changes by `+1` or `-1` | Main theorem uses standard bitwise mutation; upper proof covers type-A operators | Critical difference. Type-A requires constant probability of a same-Hamming-weight offspring, not necessarily a literal genotype copy. Exact one-bit mutation has probability zero. |
| Communication | Offer each offspring to every subproblem within symmetric radius `r`; accept on non-worsening cost | Same radius interval and non-worsening replacement | Structurally close. Verify whether any parent-acceptance gate exists; displayed Algorithm 1 offers directly to all neighbors. |
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

1. exact one-bit mutation + simultaneous alignment (current `large.py`);
2. exact one-bit mutation + archive coverage;
3. lazy one-bit mutation with preregistered weight self-loop probability `1/2` + simultaneous alignment;
4. lazy one-bit mutation with preregistered weight self-loop probability `1/2` + archive coverage.

For archive variants, archive all initialized weights and every generated offspring weight, even when replacement rejects it. Optionally add standard bitwise mutation as a fifth validation against the paper. Measure `r=0`, `r=1`, and `r=ceil(log2(n))` over increasing `n`, count initialization evaluations, and check archive completion per evaluation. This factorial design isolates whether the weight self-loop, stopping event, or their interaction drives the different empirical law.

Do not claim new asymptotics from this experiment alone. Its purpose is to select the correct conjecture and proof mechanism.
