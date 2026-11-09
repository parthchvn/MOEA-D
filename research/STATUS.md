# Research status

## Larger neighborhoods with stored prior noise (2026-11-09)

The [local campaign](LARGE_T_LOCAL.md) is ready for main measurement. Model and inference were registered before the pilot. The frozen sampler at `9710dfff482d8e76c7b2269abd9c23985bd044d0` passed 70 tests. Its clean-checkout [pilot](reports/large-T-20261109/pilot/report.md) recorded 62/62 smoke trials and 102/102 calibrations, including six intentionally fixed-duration throughput runs. Re-running this setup on another machine measures its own throughput. The n=256 primary effect and n=512 validation are unmeasured in the pilot. C17–C19 record the proven corner law, the pathwise counterexample and the preregistered open comparison. The campaign interpretation, once available, is the dated status and claim supplement for this study.

At n=16 in the noiseless supplied-corner calibration, the mean costs over 12 trajectories per arm were 8,927.8 evaluations at T=1, 436.3 at T=2 and 830.2 at T=3. The model predicts the same capped mean, 672.4, for T=2 and T=3; finite samples of a geometric variable can differ substantially. All eight corner means fell within their pointwise model-predictive ranges. The six single-run timing cells quantify throughput on the recorded host only. The final setup passed all 92 tests, including mask-oracle, restart, packet integrity, statistical analysis and publication checks. Restoring the compressed pilot packet and rerunning the analyzer reproduced all nine report files byte for byte, including all four plots.

Previous structured audit: 2026-11-03.

## Broadcast ablation completed and approved (2026-11-03 03:04:56 UTC)

The user-authorized two-arm lazy q=1/2 ON/OFF study completed all planned grids
at 02:57:17.945 UTC, within the new 02:28:31–04:28:31 UTC ceiling. The former
three-arm roadmap was refined before outcomes. Baseline 37 tests/compilation
passed and the exact dirty source is preserved. Independent pre-change audits,
implementation/preregistration approval, smoke and timing/integrity gates all
preceded the relevant runs. Core source remained frozen during each grid.

**Mechanically checked:** 324 trajectories in 162 independent seed blocks,
all uncensored: smoke 36/18, main 192/96, validation 96/48. Inference excludes
smoke (288 trajectories/144 blocks). Total runner time 701.1943 s. All source,
phase, count, seed, paired-order and checkpoint invariants pass. The evaluator's
separate raw recomputation matches 860 numerical checks in the curated summary.
All 54 tests pass (final builder 0.932 s; independent pre-grid 0.921 s), five
modules compile, and whitespace/PDF/HEAD/preservation checks pass. The independent
evaluator approved the final model, evidence and claims at 03:04:23 UTC; the
literature reviewer approved source/scope at 03:03:24 UTC. Final completion is
03:04:56 UTC, 36 minutes 25 seconds after activation.

**Empirically supported (C15):** broadcast contributes to finite radius
attenuation at fixed q=1/2. Primary n=256 A1=0.3579 [0.2529,0.4682] and
Delta=0.3568 [0.2518,0.4673]; validation n=512 both=0.1976 [0.0979,0.3148].
Each interval is 97.5% two-sided paired bootstrap, an approximate nominal
Bonferroni 95% family per n. OFF uses about 43%/22% more evaluations at r=1;
the logarithmic-radius measured effect is small/uncertain. In all 288 inferential
trajectories archive=last endpoint target-hit=alignment, with interiors earlier.
These sample identities do not override C10/C14 counterexamples. Broadcast
advances both endpoint and interior progress at r=1; equal completion can mask
different interior progress at large radius. No exclusive mediation or asymptotic
claim is made; OFF is outside the paper's canonical replacement rule.

See `BROADCAST_PREREG.md`, `reports/20261103T022831Z-broadcast-ablation.md`, and
`reports/20261103T022831Z-broadcast-summary.json`. Prior factorial data/report/
preregistration remain unchanged. No additional experiment is needed or authorized.

## Controlled study completed (2026-11-02 21:55:28 UTC)

**Mechanically checked:** baseline 16 tests and compilation passed on clean
HEAD `7c4e8addcca6adf04d65f74fec05244bbb26ab5f`. A five-hour study started at
21:27:58 UTC; experiment-start cutoff is 2026-11-03 01:42:58 UTC and final
deadline 02:27:58 UTC. Independent evaluator and literature audits preceded
builder edits. Independent evaluator approval gated smoke, main, and validation.
All 774 trajectories completed without censoring: 54 smoke (0.687 s), 576 main
(206.143 s), and 144 n=512 validation (695.881 s). Sources, seeds, balance and
endpoint invariants passed. The independent evaluator approved the finished
bundle at 21:55:13 UTC: all 37 tests passed independently, four modules compiled,
825 numerical checks matched separate raw-data recomputation, and core source/
snapshot/PDF/HEAD checks passed. The literature reviewer approved source/proof
scope, relying on the cited endpoint lemma externally. The report was completed
27 minutes 30 seconds after activation; no further experiment is needed for
this bounded goal. See `FACTORIAL_PREREG.md` and
`reports/20261102T212758Z-radius-factorial.md`.

**Empirically supported:** the preregistered decision favors the mutation-rule
change as the explanation of radius sensitivity. At primary n=256,
`R_exact=1.582`, `R_lazy=1.162`, mutation attenuation `M=0.309` with pointwise
95% bootstrap `[0.057,0.574]`; n=512 validation gives `M=0.314`,
`[0.026,0.610]`. Smaller n=32/64/128 remain inconclusive. Lazy mutation is slower
in raw evaluations at the primary positive radii; the finding concerns radius
sensitivity, not an overall speedup. All 480 main/validation positive-radius
trajectories had equal sampled endpoints, while r=0 had substantial gaps.

**Contradicted:** universal positive-radius event equality. A feasible n=3,r=1
path from `[1,1,1,2]` reaches archive coverage at evaluation 8 and alignment at
10. Zero-gap empirical bootstrap intervals therefore do not bound rare gaps.
The same path refutes a universal endpoint-last-hit/alignment identity (C10),
while leaving asymptotic endpoint dominance unresolved.

**Proved (source-based inference, not the printed theorem event):** the paper's
type-A upper-bound argument for r>=1 solves all subproblems, so the lack of alignment in
its stated archive stopping event does not itself prevent its expectation upper
argument from applying to the lazy controlled comparator. No tail or lazy
lower bound is transferred. Full source reconciliation is recorded in
`PAPER_COMPARISON.md`.

## Current state

- The repository has the legacy noisy and noiseless models, an exploratory
  notebook, and the canonical exact/lazy paired-event variant with a reviewed
  lazy broadcast ON/OFF intervention and passive target-hit phases.
- Basic noiseless properties pass small finite checks: unique scalarization minimizers, reciprocal radius neighborhoods, deterministic seeded runs, and convergence on a smoke set.
- The included noisy `T=1` draft is not yet a complete proof. The most important gap is conditioning on accepted stored noisy values.
- The larger-neighborhood runtime law is a well-formed conjecture with suggestive simulations, but no proof document is present.
- A preprint posted on 2026-10-26 directly studies MOEA/D solution exchange on OneMinMax. It proves `Theta(n^2)` evaluations for every communication radius `r >= 1` and `Theta(n^2 log n)` for `r = 0` in its model. This is in tension with the repository's claimed logarithmic threshold.
- The most important identified model difference is mutation: the preprint's quadratic upper-bound class requires a constant probability of producing a same-Hamming-weight offspring, while exact one-bit mutation always changes the Hamming weight by one. This is a sufficient-condition gap, not evidence by itself of a slower runtime. The preprint also measures archive coverage, while legacy `large.run` waits for simultaneous subproblem alignment.
- The whole-process invariant `(J)` is contradicted at initialization. The code's checks after sweep 2 concern only a possible post-burn-in property.
- The recorded-run harness now checkpoints after every trial, enforces separate per-trial and total deadlines, uses balanced round-robin configuration order, and snapshots source files and dependency versions.
- There was previously no environment specification, test suite, experiment manifest, claim ledger, or long-run protocol.

## Publication bundle (2026-11-03)

The user subsequently authorized committing the reviewed proposal and important
completed-study evidence to `parthchvn/MOEA-D` on `main`. Six compact packs in
`research/evidence/` preserve exact smoke/main/validation records, dirty sources,
patches and dependency manifests; the evidence README gives hash verification,
safe temporary extraction and analysis-only recomputation commands. Independent
publication audit approved all six packs (195 files; 1,098 trajectories) and exact
summary recomputation at 2026-11-03 04:07:36 UTC. Earlier
reports' no-commit/no-push statements remain historical. Local raw runs and PDFs
are preserved; publication does not authorize the proposed standard-bit study.

## Best next bounded question

The broadcast study now supports a finite contribution from same-weight
communication. `STANDARD_BIT_PROPOSAL.md` specifies the next proposed two-arm
standard-bit ON/OFF comparison: archive-primary A1 and Delta, alignment/phases
secondary, requiring validation of fixed-consumption paired binomial-quantile
streams, and a
bounded smoke/main/timing-gated validation plan. It is not preregistered,
implemented or launched; independent evaluator and literature reviewers approved
its design/source scope on 2026-11-03. No implementation, trial or spend is authorized. `NEXT_DIRECTIONS.md` preserves the earlier three-arm proposal
and records its later two-arm execution; its conditional dose/scheduler and
finite-state questions remain later options, not one large factorial.

**Proved alternate-process control (C16):** independent uniform breeders with
lazy broadcast OFF permit deletion of inert holds, giving the exact embedded
chain and a 1/(1-q) expected offspring-count factor. This process remains
unimplemented and the identity does not transfer to the current cyclic ablation.
**Open:** exclusive/natural mediation of the earlier exact-to-lazy contrast,
rare event gaps, exact-one-bit asymptotics and noisy selection conditioning.

## Resolved model-comparison checklist

The completed comparison with Doerr, Elmoutassim, Krejca, and Kibulu (2026)
records these distinctions in `PAPER_COMPARISON.md`:

1. archive coverage versus simultaneous exact subproblem alignment;
2. one-bit versus standard-bit or general mutation;
3. uniform versus cyclical breeder selection and the repository's sweep update order;
4. whether offspring are communicated after acceptance only or offered independently to all neighbors;
5. radius and boundary conventions;
6. tie acceptance, reference point, scalarization orientation, and initialization.
7. self-parent mutation in `large.py` versus neighborhood-parent selection in `sim.py`.

The models differ. The controlled study isolates mutation and stopping as two
factors; it supports C13 in the tested finite range without retiring or proving
the exact-one-bit asymptotic conjectures. The study remains noiseless.

## Exploratory radius diagnostic

An uncommitted, machine-recorded smoke grid used `n in {50,100,200}`, `r in {0,1,4}`, and eight independent repetitions per configuration. It had no censoring. Mean sweeps for `r=1` were `94.6`, `175.3`, and `526.1`; for `r=4` they were `65.4`, `131.8`, and `382.6`. This confirms a finite-size benefit from communication and from increasing the radius, but the range and variance are far too small to distinguish linear from `n log n` behavior. The run is stored locally under `research/runs/20261102T204129Z-large-grid-radius-diagnostic/` and is intentionally ignored by Git.

## Suggested bounded work packages

### A. Canonical-model reconciliation — completed

The source-cited comparison, model conventions, index/complement transformations,
clipped endpoint neighborhoods and both event definitions are recorded in
`PAPER_COMPARISON.md`, `PROJECT.md`, and `FACTORIAL_PREREG.md`. The controlled
implementation and tests match this freeze. The self-loop broadcast ablation is now completed; the proposed next empirical
step is the standard-bit bridge above, subject to separate authorization.

### B. Noisy drift audit

- Enumerate the augmented state `(true weight, stored value)` for one extreme subproblem.
- Derive exact transition probabilities including acceptance.
- Compute conditional drift for every reachable state for small `n` and symbolic `p` where feasible.
- Test whether a one-dimensional potential can work; otherwise design a phase or two-dimensional potential.

### C. Noiseless neighborhood theorem

- If useful, formulate and test a new post-burn-in replacement for the contradicted whole-process invariant `(J)`.
- Separate endpoint hitting time, interior alignment, and simultaneous completion.
- Define effective neighborhood size by radius or minimum cardinality before stating asymptotics.
- Preregister scaling grids that discriminate candidate laws.

## Decision rule

Do not begin the noisy `T > 1` theorem until A is complete and the overlap with the October 2026 result is understood. Exploratory experiments are allowed when they directly distinguish the two processes or choose between proof strategies.

## Morning-report template

- Question attempted:
- Result and status label:
- Evidence produced:
- Counterexamples or failed approaches:
- Files changed:
- Commands/runs and elapsed time:
- Cloud cost, if any:
- Remaining uncertainty:
- Best next action:
