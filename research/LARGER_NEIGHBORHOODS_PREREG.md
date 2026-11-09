# Larger cardinalities under stored prior noise

Frozen 2026-11-09, before the campaign pilot. The unit is one independently seeded population trajectory. This is a new study of the manuscript model. It does not replace the earlier exact/lazy factorial, broadcast ablation or standard-bit bridge proposal. The campaign ID is `large-T-20261109`. A fresh scientific revision needs a new ID and a new plan before collecting its data.

## Model

The objective vector at Hamming weight w is (w,n−w). Initialize n+1 true weights as independent Binomial(n,1/2), evaluate once, and store each noisy weight. The observed extrema lo and hi include initialization and every proposal, including rejected ones. For breeder i in ascending cyclic order, mutate its **own** incumbent; generate a single observed weight c from the offspring of true weight y. Update the extrema, then minimize max{k(hi−b),(n−k)(b−lo)} at each recipient k, using the **updated** extrema for both c and the incumbent's stored b. On a tie, replace. Broadcast the same (y,c) regardless of the breeder's own decision. Mutation is either exactly one uniformly random bit, or independent per-bit rate 1/n. Noise is inactive with probability 1−p; when activated use the specified noise operator. Activation is a single Bernoulli draw, not independent activation for each bit. Draws start afresh on every proposal, including a mutation that flips zero bits. The primary campaign uses bitwise mutation and activated bitwise noise throughout.

B_T(i) has exactly T indices. Begin with i; for distance 1,2,… append in-range indices to reach T, preferring right then left for even i, left then right for odd i. Boundaries fill to cardinality T. This matches the ordering of sim.build_neighborhoods. Its absolute-distance objective and random neighborhood parent are different. In large.py, r is a clipped symmetric radius, and even an interior size 2r+1 does not determine the same endpoint neighborhoods. Keep numeric comparisons between these engines out of the primary analysis.

## Endpoints, units and mechanism

- Boundary 0 is just after initialization; one sweep is n+1 offspring attempts. The primary endpoint is first **true exact assignment** at a sweep boundary (slot k holds weight k for all k). It can precede S. For an observed event at sweep s, cost is init_evals+(n+1)s. Initialization costs n+1 for ordinary runs; supplied corner states cost zero initialization evaluations.
- Record the first current-front boundary (true weights cover every weight in any order) and the boundary by which the passive archive has seen all weights, including rejected offspring. Archive here is rounded to the boundary convention. It can differ from a per-offspring archive time in earlier evidence. Record U (reference ideal), S (also all stored labels at their targets), and first true exact boundary at or after S. Continue past an early exact hit to observe post-S repair or the fixed cap.
- Report U, S−U and post−S where observable. These sum to the post-S endpoint. Summaries restricted to trajectories that reached a phase must say so. Inspect the number and size of true/stored mismatches, endpoint repair donors, and external replacements. Comparisons, elapsed seconds and evaluations have distinct units: a broadcast is one evaluation even if T recipients compare it.

## Fixed design

Here f is the activation factor p=f/n. The lag limit is imposed in complete sweeps. At each size take distinct numeric cardinalities if rounding collides. No lazy mutation, adaptation, selective reuse, neighborhood mating, or supplied ideal reference in the primary cells.

| Stage | Sizes | Cardinalities | Factors | Repetitions per cell | Limit and use |
|---|---|---|---|---:|---|
| Smoke | 8,16 | 1,2,3,ceil(sqrt n),ceil(n/4),n+1 | 0,1/64,1 | 2 | ceil(96 n log(n+1)); bit/bit model and termination checks |
| Smoke controls | 8,16 | 1,3 | 1/64 | 2 | same cap; one-bit mutation and one-bit noise |
| Calibration | 128,256,512 | 1,n+1 | 1/64 | 1 | 32 sweeps; throughput only, an administrative stop is expected |
| Calibration, supplied corner | 8,16 | 1,2,3,n+1 | 0 | 12 | ceil(12 n² log(n+1)); ideal reference and one supplied endpoint error |
| Main | 64,128,256 | 1,3,ceil(sqrt n),ceil(n/4),n+1 | 0,1/64,1 | 24 | ceil(12 n log(n+1)); 1,080 planned trajectories |
| Holdout | 512 | 1,3,23,128,513 | 0,1/64,1 | 16 | same cap; 240 planned trajectories |

The integer ceil(sqrt n) is the ceiling of the square root, not the nearest odd number. Smoke and time calibration do not enter scientific intervals. Each cell and repetition uses a distinct, deterministic SHA-256-derived seed; generator/compiler identity and binary source are recorded. Paired outcomes on one trajectory, such as archive and alignment, are never counted as separate independent runs. Repeatability across standard-library implementations is assessed at the distributional level; a bit-identical C++ trajectory requires the recorded toolchain. Plan order rotates cells across repetitions before sampling. The manifest enumerates all planned IDs before the first draw.

**Scaling gates.** Primary measurement requires the test suite and successful smoke. The runner requires complete smoke records and post-S completion across the smoke cells, then all calibration receipts. Intentionally capped calibration is a valid timing observation. Holdout requires every planned main receipt and every primary main exact endpoint observed. If a gate fails, report the affected cells and the missing holdout. Retain capped trials. Never replace a long trajectory with a new seed or fit on the held-out sizes.

## Inference fixed before sampling

**Primary finite-size hypothesis.** At n=256 and f=1/64, the mean first exact-assignment evaluation cost is smaller at T=16 than at T=1. Replication uses n=512, f=1/64, T=23 versus T=1 with independent seeds. The estimand is mean(T=1)/mean(T=ceil sqrt(n)); a value above one favors sharing. Use independent within-cell bootstrap resampling of whole trajectories, deterministic inference seeds and a two-sided nominal pointwise 95% interval. Call the directional effect replicated only when both lower endpoints exceed one and both stages are fully eligible. Intervals crossing one give an inconclusive directional comparison. No across-grid simultaneous coverage is claimed.

**Secondary hypotheses.** Examine the gain from sqrt(n) to n/4 to full broadcast, possible reversals and the change in recipient comparisons and time to solution. Report every predeclared arm, including negative effects. Report rates and times for the stage transitions before interpreting an exact-time difference. A reduction in post-S delay is a candidate mechanism; an observed correlation is insufficient to identify a cause. All other contrasts, curves at f=1, phase patterns, and fitted slopes are exploratory. No equality or plateau follows from an interval crossing one. No finite plot proves a Theta or big-O law.

**Censoring and interrupted work.** A finished run with no hit by sweep H supplies an exact restricted observation min(time,H)=H, and an unknown unrestricted time. Estimate an unrestricted mean ratio only if all planned trajectories for both cells have observed the chosen endpoint. Report fixed-horizon restricted means, completions, denominators, missing trials, and partial identification bounds if any planned path lacks a confirmed prefix. A killed trial without a durable boundary receipt is missing; record the time spent and retry its original seed on resume. Censoring of post-S completion never erases an earlier confirmed exact hit. Do not pool smoke, timing, main, or holdout. Interpret an uncensored finite sample as finite evidence, with uncertainty about unobserved rare tails.

## Validation and proof obligations

The independent small-n oracle uses bit masks rather than the optimized comparison code, and exercises even-T orientation, ties, shared observations and ideal-reference updates on rejected offspring. Additional fixtures cover the noiseless supplied-state geometric law and a failure of pathwise monotonicity. The existing repository suite must still pass. Publish fresh test counts, compiler/library details, elapsed seconds, seeds and the exact source used for each stage. Benchmark one and full recipient sets at the same sizes. Report both attempts/s and logical comparisons/s; implementation shortcuts at a pinned population are permitted only if all state transitions and logical counters are preserved.

Candidates for formal work, with their assumptions and falsifiers, are in [LARGE_T_THEORY.md](LARGE_T_THEORY.md). A proposed theorem must state the stochastic process, the stopping event, the initial law, the range of p,T,n, and provide a proof plus an independent adversarial review. Record “conjectured”, “contradicted” or “open” when that standard is unmet.
