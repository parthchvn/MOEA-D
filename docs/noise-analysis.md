# Interpreting the expanded noise experiments

The [expanded report](../evidence/noise-grid/README.md) separates `p=alpha/n` from fixed `p`. It uses the same cyclic self-parent, ideal-reference Tchebycheff model, shared offspring observation, one-bit mutation, and no re-evaluation as the original neighborhood dataset. The new protocol is exploratory: it was selected after pilot runs, not preregistered as a confirmatory test.

## What the instruments mean

`event=1` means the **current true population** first achieved `w[j]=j` for every slot before or at its administrative evaluation cap. `stored_hit>=0` means that every stored observation had already achieved `v[j]=j` before the run stopped. These are different events under noise. The run ends at the earlier of true exact assignment and the cap; a missing stored hit is consequently not, by itself, an estimate of the unrestricted stored-optimum hitting time.

`stored_hit_but_exact_censored` counts a particularly informative failure mode: all stored scalar optima were reached, but the true population did not become simultaneously correct by the cap. Stored scalar optima are permanent because comparisons use non-increasing costs. A positive count therefore identifies unsuccessful time spent after stored optimization, rather than just slow optimization of stored fitness. It does not prove that all difficulty is in this phase.

The terminal incorrect-slot average is computed **only among capped runs**. It is subject to selection by failure and is not a stationary-distribution estimate. Runs, not sequential observations within a run, are the independent replication units.

## Comparisons that the data can support

For a fixed n, every noise/radius configuration has the same evaluation cap. The sample mean is an estimator of `E[min(tau,B)]`, where tau is the true-exact-assignment time and B is the cap. It is not an estimator of unrestricted runtime when censoring is material. The original dataset used budget factor 20; the expanded grid uses factor 4 and fresh noiseless controls. Do not pool their capped means.

Increasing alpha in `p=alpha/n` tests noise intensity on a shrinking-probability scale. Increasing n with fixed p tests a genuinely different regime. Finite success at one n does not establish robustness as n tends to infinity; likewise, failure within the cap does not establish exponential runtime. A curve at the cap is not runtime saturation.

The pointwise bootstrap and Wilson intervals are approximate and do not control simultaneous coverage across the grid. Noise and radius configurations use independent streams. A smaller sample mean for one noisy cell is not sufficient evidence that noise improves the algorithm. A quadratic normalization plot is a diagnostic, not a proof of a quadratic law. Comparisons measure evaluations, not wall-clock cost or scalar-comparison work.

## A rigorous special case: p=1

This is a mathematical consequence of the specified model, separate from simulation.

**Lemma (permanent incorrect slot).** Suppose noise always flips exactly one bit, no re-evaluation is used, and slot j has stored weight v[j]=j. Then the true weight of that slot differs from j at that time and at every later time.

**Proof.** Every evaluation at p=1 returns a weight differing by exactly one from the evaluated genotype's true weight. Thus an incumbent with stored weight j has true weight j-1 or j+1 (only the feasible alternative at an endpoint). The Tchebycheff scalarization has its unique weight optimum at j. Once the stored value is optimal, replacement is possible only by an offspring whose observed weight is also j. Such an offspring again has true weight differing from j. Rejection leaves the existing incorrect slot unchanged. Induction over turns proves the assertion, for every radius. QED.

**Corollary (infinite expected exact-assignment time at p=1).** With the independent uniform initialization used in this repository, the expected true-exact-assignment hitting time is infinite, for every n>=1 and every radius. This does not assert that every run fails.

**Proof.** A uniform bit string remains uniform after flipping a uniformly chosen bit. Initial observed weights are therefore independent Binomial(n,1/2) variables. Let q_j=binom(n,j)/2^n. Slot j initially has its stored optimum with probability q_j, and the preceding lemma makes that slot permanently truly incorrect. The probability that at least one slot has this obstruction at initialization is

`1-product_{j=0}^n(1-q_j) >= 1-exp(-sum_{j=0}^n q_j) = 1-exp(-1) > 0`.

On this event true exact assignment never occurs. Positive probability of an infinite hitting time implies infinite expectation. QED.

This boundary result relies on **exactly one noise bit at every evaluation**. It is not a threshold theorem for p<1, is not about archive coverage, and must not be transferred to bitwise noise or re-evaluation without a new proof.

## Reproducibility

The raw records, source hashes, protocol, and generated plots are under `evidence/noise-grid/`. The runner validates configuration/seed completeness and event accounting; the verifier recomputes the summary from the raw records. Existing neighborhood data remain in their own directory. The [general theory audit](theory-status.md) still lists the open cyclic full-population runtime arguments.
