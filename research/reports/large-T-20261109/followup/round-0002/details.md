**Empirically supported, finite restricted comparison.** At n=512 and
p=1/(64n)=1/32768, the registered primary ratio is
R_H=E[513(1+min(X_1,H))]/E[513(1+min(X_23,H))], with H=38,341 sweeps.
X is first simultaneous true slot-to-target assignment at a sweep boundary.
The estimate is **2.3390952207**, nominal 95% percentile bootstrap interval
**[2.0853866835, 2.5964682010]**. Its lower endpoint exceeds one, so the frozen
directional rule favors T=23. The observed evaluation reduction is 57.2484%.
This does not establish an unrestricted expectation ordering or an asymptotic law.

| Main arm | Planned / exact / capped / missing | Restricted mean evaluations [nominal 95% interval] | q10 / median / q90 evaluations |
|---|---|---|---|
| T=1 | 32 / 32 / 0 / 0 | 5,139,185.906 [4,900,990.788, 5,388,055.833] | 4,506,858.9 / 5,042,790 / 5,903,142.3 |
| T=23 | 32 / 32 / 0 / 0 | 2,197,082.813 [2,002,718.334, 2,439,676.104] | 1,591,839 / 2,182,815 / 2,585,776.5 |

Both arms' completion fraction is 32/32; Wilson 95% interval **[0.892821, 1]**.
The four separately seeded n=32 smoke trials also finish uncensored and are
excluded from inference. Main exact times range from 7,651 to 14,311 sweeps at
T=1 and 2,749 to 9,589 at T=23. Every main U, S, archive, current-front,
first-exact and post-S event is observed. No missing-data bound substitutes
for a confidence interval in this complete dataset.

The frozen analysis sorts each arm by repetition, uses independent PCG64
streams and 10,000 whole-trajectory resamples per arm, and computes linear
2.5%/97.5% quantiles. The same within-arm resampling indices apply to all phase
diagnostics. These are **approximate pointwise nominal** intervals, with no
simultaneous coverage or small-sample coverage theorem. Thirty-two trajectories
per arm do not rule out rare long runs. The raw [receipts](trials.csv),
[summary](summary.json), [phase table](phases.csv), and [plot](results.png) retain
both distributional and censoring information.

**Empirically supported phase decomposition.** U is the first boundary with
observed extrema (0,n); S additionally requires every stored label to equal its
target; P is the first true-exact boundary at or after S. All 32 trajectories
per arm enter and complete each phase: entered/completed/censored/not-entered
is 32/32/0/0 for each phase. The table uses all-trial restricted occupancies;
in this sample they also equal observed completed durations.

| Occupied phase, sweeps | T=1 mean | T=23 mean | Difference T=1−T=23 [pointwise 95%] |
|---|---:|---:|---:|
| Before U | 8,737.6875 | 4,275.28125 | 4,462.40625 [3,787.05391, 5,106.46094] |
| U to S | 1,279.09375 | 6.53125 | 1,272.5625 [1,001.17656, 1,594.56797] |
| After S through P | 0.125 | 0 | 0.125 [0, 0.375] |
| P minus X | 0 | 0 | 0 [0, 0] |

U's q10/median/q90 are 6,990.7/8,687/10,830.7 at T=1 and
3,096/4,246.5/5,034.5 at T=23. For S−U they are
510.8/985/2,484.3 and 5/6/8. Every post-S quantile at these probabilities is
zero, which hides the single nonzero observation; the plot and histograms
explicitly retain it. Conditional completed-phase summaries carry their
denominators and selection-conditioning labels in the summary.

**Mechanically checked algebra, not a new runtime theorem.** With
u=min(U,H), s=min(S,H), q=min(P,H), x=min(X,H), the phase occupancies
A=u, B=s−u, C=q−s, G=q−x satisfy A+B+C=q and
513(1+A+B+C−G)=513(1+x). The separate arithmetic audit checks these identities
for all 68 receipts with zero residual. Here P=X in all 64 main trajectories.
The observed evaluation difference **2,942,103.09375** therefore decomposes into
**2,289,214.40625 before U**, **652,824.5625 from U to S**, and **64.125 after S**.
Its joint-bootstrap interval is [2,607,666.77109, 3,260,761.05937]; it is not
obtained by adding marginal interval endpoints. Descriptively, 77.8088% of the
sample difference occurs before U, 22.1890% between U and S, and 0.00218% after S.
These percentages are not causal mediation fractions.

**Observed exception retained.** T=1 repetition 20, receipt
[4e8a2113cf235be3cc1b](rows/4e8a2113cf235be3cc1b.json), has U=6,951,
S=11,204 and X=P=11,208. At S there is one true/stored mismatch of magnitude
one. Every other main trajectory has zero mismatch at S and zero post-S delay.
All 64 have zero true/stored mismatch at U. Thus an assertion that the entire
new sample difference occurs before S would be false. The working hypothesis
that most observed savings occur there is supported descriptively.

Both arms record zero own and external pinned-endpoint repairs. These counters
start at each endpoint's individual pinning, potentially before S, and end at P;
they are not post-S-only counters. T=23 records 67,946,563 external replacements
but only 14,415,540 actual true/stored changes across 32 trials. Replacement
counts cannot be interpreted as useful repair counts. Zero sampled repairs and
degenerate post-S or gap intervals do not establish zero population probability
or stopping-event identity.

**Empirical work tradeoff.** Work below ends at P; here P=X in every main trial.
Initialization contributes 513 evaluations but no recipient comparisons.

| T | Mean attempts | Mean logical comparisons | Mean engine-process seconds |
|---:|---:|---:|---:|
| 1 | 5,138,672.90625 | 5,138,672.90625 | 0.240098 |
| 23 | 2,196,569.8125 | 50,521,105.6875 | 0.191202 |

T=23 uses **9.83155 times** the logical comparisons while reducing evaluations.
The observed aggregate engine-time ratio is only 1.25573 in its favor. These
single-host timings are descriptive, include process startup and have no timing
uncertainty study. Logical comparisons include optimized pinned-state
accounting and are not literal CPU-operation counts.

**Assumptions and model scope.** The unchanged kernel initializes n+1
independent Binomial(n,1/2) true weights and observes each once. Ascending cyclic
breeders mutate their own incumbent with independent bit-flip probability 1/n.
One activation gate of probability p precedes independent 1/n observation
flips, shared across all T recipients; incumbents are never reevaluated.
Observed extrema include rejected proposals and update before both
Tchebycheff comparisons; ties replace. T is filled cardinality, including at
edges, not a clipped radius: B_23(0)={0,…,22}. All endpoints are checked at
complete sweep boundaries. The boundary filtration reveals initialization and
all consumed proposal/noise draws through that boundary. No drift theorem or
acceptance-conditioned noise bound is used.

The transition law is a weight-space reduction; adequate independent
pseudorandom streams are assumed, not proved by distinct seeds. Compiler and
standard-library details matter for exact seed replay. This run used clang
20.1.8, libc++ 200100, C++17/O3, std::mt19937_64 on arm64. The archived source,
binary hash, runtime and compiler macros are in the manifest. The radius/archive
literature and the supplied-corner law do not directly establish this noisy,
moving-reference, uniformly initialized result. This offline round makes no
new literature or novelty claim.

**Conjectures, proof gaps and falsifiers.** The registered finite R_H>1
conjecture receives empirical support under its interval rule. A lower endpoint
at or below one would fail that rule; an interval wholly below one would oppose
the direction. Material post-S savings would oppose a predominantly pre-S
description; any P>X sample would prevent equating the endpoints in the
decomposition. Neither failure occurred materially here, but rare gaps and tails
remain possible. Donor corruption, joint repair with reinfection, stored-noise
selection bias and unrestricted tails remain proof obligations in the supplied
project evidence. Existing nonmonotonicity and reinfection counterexamples are
unchanged. **No new candidate proof or noisy theorem is advanced.**

**Cumulative checkpoint.** Earlier n=256 evidence gave ratio 2.327639
[2.050148, 2.674642] with 24 trajectories per arm. Round 1 audited that evidence
and published a separate prospective plan without drawing outcomes. This round
implemented and executed it, producing the n=512 result above. The direction
agrees with the earlier evidence, but the old 240-row holdout remains entirely
unobserved and blocked; its original two-stage replication decision remains
inconclusive. No old seed, gate, cap or preregistration was changed.

The measurement invocation took 16.612791 seconds, including 1.265618 seconds
of compilation. All 68 engine calls sum to 14.224490 seconds; main calls sum to
13.801595 seconds. Initial analysis/plot packaging took 0.846576 seconds. See
checks.json for total turn accounting and verification. No paid resource,
network access, commit or push was used. Sampling failures and cutoffs: none.
The most useful next empirical question is whether T=3 retains the observed
pre-S benefit at lower comparison cost; it requires a new prospective plan
published before measurement.
