# Literature map

This is a relevance map, not a comprehensive bibliography. Verify theorem assumptions in the primary source before transferring a result.

## Directly overlapping work

### Doerr, Elmoutassim, Krejca, and Kibulu (2026)

**Understanding the Co-evolutionary Solution Exchange of the MOEA/D: Already the Smallest Communication Radius Gives the Best-Possible Speed-Up.** [arXiv:2610.35373](https://arxiv.org/abs/2610.35373), posted 2026-10-26.

This is the highest-priority source. It studies mutation-only MOEA/D with Chebyshev decomposition into `n+1` uniformly weighted subproblems on OneMinMax. It proves `Theta(n^2)` function evaluations for every communication radius `r >= 1` and `Theta(n^2 log n)` for `r = 0`, with archive coverage as the runtime event. It also reports that larger radii can accelerate partial progress without changing the full-front asymptotic runtime.

Its quadratic upper-bound proof generalizes to a type-A mutation class that must produce a same-Hamming-weight offspring with probability at least a positive constant; this need not be a literal genotype copy. Standard bitwise mutation qualifies, in particular through zero-bit flips, while the repository's exact one-bit mutation does not. The repository must also compare archive coverage, update order, communication/acceptance semantics, and simultaneous alignment. The current conjecture is therefore not automatically contradicted, but failure of a sufficient proof condition is not evidence that the conjecture is true.

### Zhang, Zhong, Zheng, and Doerr (2026)

**Superior Runtime Guarantees for the MOEA/D Multi-Objective Optimizer via Weighted-Sum Decomposition.** AAAI 2026. [DOI:10.1609/aaai.v40i43.41049](https://doi.org/10.1609/aaai.v40i43.41049).

This paper proves that weighted-sum MOEA/D can cover the OneMinMax front with only a logarithmic number of subproblems, typically in `O(n log^2 n)` evaluations. It concerns a different decomposition and primarily informs alternative project directions and comparative framing.

### Doerr, Krejca, and Weeks (2024)

**Proven Runtime Guarantees for How the MOEA/D Computes the Pareto Front From the Subproblem Solutions.** PPSN 2024. [arXiv:2405.01014](https://arxiv.org/abs/2405.01014).

This work studies the second phase in which subproblem optima do not already cover the full front. It is relevant if the project changes the number of subproblems or uses an archive, but it does not by itself settle the current `N=n` simultaneous-alignment model.

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
