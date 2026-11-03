# Project definition

## Core question

How does neighborhood sharing change the runtime and noise robustness of MOEA/D on the bi-objective OneMinMax benchmark under one-bit mutation?

## Benchmark

For a bit string `x` of length `n`, let `k = |x|_1`. The Pareto objective vector is `(k, n-k)`, so every Hamming weight in `{0, ..., n}` represents one Pareto-front point.

The project normally uses `n + 1` scalar subproblems indexed by `j in {0, ..., n}`.
The canonical noiseless scalarization is now frozen as
`C_j(w)=max{j(n-w),(n-j)w}`, minimized with ties accepted. Its unique optimum is
`w=j`. The exact paper/draft index and genotype transformations, ascending-order
qualification, and apparent source min/max typo are in `PAPER_COMPARISON.md`.
`sim.py` uses absolute distance and is not equivalent across the two branches.

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

### Controlled paired-event model (`large.run_controlled`)

- Same scalarization, uniform initialization, own-parent mutation, ascending
  cyclic breeder scan, clipped radius, and non-worsening replacement throughout.
- Exact one-bit or lazy one-bit with weight self-loop probability exactly `1/2`.
  Lazy copies are evaluated; neighbor communication is ON by default. The
  reviewed broadcast ablation can suppress only neighbor replacements on copies,
  preserving the breeder comparison and all moving-offspring broadcasts.
- Passive archive includes every initialized and generated weight, including
  rejected offspring. Both archive and alignment first times are checked per
  offspring and include the `n+1` initialization evaluations.
- Two endpoints are paired observations on one trajectory; distinct mutation,
  radius, n and repetition cells use independent seeds and the same split-stream
  random policy. `FACTORIAL_PREREG.md` fixes the design.
- Executed evaluations and confirmed observation prefixes are separate under
  wall deadlines. Endpoint-specific censoring preserves an earlier archive hit.
- `scripts/run_research.py factorial-grid` records grids, and
  `scripts/analyze_factorial.py` recomputes distributions and paired uncertainty.

The 2026-11-02 finite study favors the mutation-rule change as an explanation
of radius sensitivity at n=256 and its n=512 validation. It establishes no
asymptotic threshold, universal stopping equality, or overall lazy speedup.

The 2026-11-03 two-arm broadcast study holds lazy q=1/2 fixed and couples ON/OFF
by absolute offspring index within independent (n,r,repetition) blocks. Passive
confirmed target-hit times record endpoint and interior completion without RNG
changes. `broadcast-grid` and `analyze_broadcast.py` preserve each planned arm,
including missing/censored arms. The finite intervention supports useful
broadcast at r=1 and attenuation relative to logarithmic radius at n=256/512;
exclusive mediation and asymptotics remain open. See `BROADCAST_PREREG.md` and
`reports/20261103T022831Z-broadcast-ablation.md`.

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
