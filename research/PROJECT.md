# Project definition

## Core question

How does neighborhood sharing change the runtime and noise robustness of MOEA/D on the bi-objective OneMinMax benchmark under one-bit mutation?

## Benchmark

For a bit string `x` of length `n`, let `k = |x|_1`. The Pareto objective vector is `(k, n-k)`, so every Hamming weight in `{0, ..., n}` represents one Pareto-front point.

The project normally uses `n + 1` scalar subproblems indexed by `j in {0, ..., n}`. A canonical statement of the scalarization and weight orientation is still required because the draft, notebook, and scripts use different but potentially transformable conventions.

## Algorithms presently implemented

### Noisy full-bit model (`sim.py`)

- State: one bit string per subproblem plus one stored noisy scalar value per subproblem.
- Variation: flip exactly one uniformly random bit.
- Noise: with probability `p`, flip one uniformly random bit immediately before evaluation; incumbents are not reevaluated.
- Parent choice: for breeder index `i`, choose a parent uniformly from `B(i)`.
- Replacement: one noisy offspring evaluation is reused for comparisons across the breeder's neighborhood.
- Stopping events: either simultaneous front coverage or exact alignment of every subproblem with its target weight.
- Neighborhood parameter: requested cardinality `T`; construction can be asymmetric for even `T`.

### Noiseless reduced model (`large.py`)

- State: one Hamming weight per subproblem. This reduction is intended to be exact because mutation probabilities and scalarized selection depend only on Hamming weight when `p = 0`.
- Variation: the weight increases with probability `(n-w)/n` and decreases with probability `w/n`.
- Parent choice: mutate the incumbent of the current breeder subproblem itself.
- Replacement: the offspring weight is offered to every subproblem within symmetric radius `r`.
- Stopping event: simultaneous exact alignment `w[j] = j` for every subproblem.
- Neighborhood parameter: radius `r`; actual neighborhood sizes are clipped at the boundaries.

## Evidence hierarchy

From strongest to weakest:

1. A complete proof whose assumptions match the implemented process.
2. A mechanically checked finite-state or algebraic property.
3. A preregistered experiment with reproducible seeds and uncertainty.
4. An exploratory experiment.
5. An intuition, analogy, or unverified proof sketch.

The claim ledger records the current level for each result.

## Out of scope until explicitly introduced

- General objective functions beyond OneMinMax.
- Standard bitwise or lazy one-bit mutation except as an explicitly labeled controlled comparator to the exact one-bit baseline.
- Reevaluation, resampling, or explicit noise-handling mechanisms.
- Unbounded cloud experimentation.
- Claims about practical MOEA/D performance on real applications.
