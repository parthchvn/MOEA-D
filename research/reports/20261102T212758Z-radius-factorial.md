# Finite-size communication-radius study

Activated **2026-11-02 21:27:58 UTC**. All experiments finished
**2026-11-02 21:51:21 UTC**. Final independent approval was delivered at
**2026-11-02 21:55:13 UTC**; report completed **2026-11-02 21:55:28 UTC**,
**27 minutes 30 seconds** after activation.
Experiment-start cutoff: **2026-11-03 01:42:58 UTC**. Hard deadline:
**2026-11-03 02:27:58 UTC**. All computation was local; cloud spend was $0.
Model/API billing was not measured. No commits, pushes, source-PDF changes,
RunPod jobs, or noisy-proof work occurred.

**Empirically supported conclusion:** the exact-to-lazy mutation change better
explains the tested radius sensitivity than the stopping event. The primary
n=256 comparison and the outcome-independent n=512 validation both meet the
preregistered decision rule. This is not an overall lazy-mutation speedup, a
universal equality of stopping times, or an asymptotic separation.

## Question and controlled model

Does same-Hamming-weight offspring availability or archive-versus-alignment
stopping better explain finite-size radius sensitivity? The frozen protocol is
[`FACTORIAL_PREREG.md`](../FACTORIAL_PREREG.md); the source-cited model table,
apparent printed min/max typo, order-preserving genotype-complement conjugacy,
and theorem-transfer limitations are in
[`PAPER_COMPARISON.md`](../PAPER_COMPARISON.md).

The 2×2 compares exact versus lazy one-bit mutation (self-loop probability 1/2)
and passive archive coverage versus simultaneous exact alignment. Both stopping
times are observed on each trajectory and analyzed as paired endpoints. All
other process conventions and random-stream policies are fixed. This comparator
also halves moving mutations and is not standard bit mutation; radius-zero
results and radius-sensitivity contrasts account for that interpretive limit.

## Audit and reproducibility record

**Mechanically checked:** baseline HEAD
`7c4e8addcca6adf04d65f74fec05244bbb26ab5f`, clean status, 16 unit tests and
required compilation passed. Both reviewers supplied independent constraints
before builder edits. The builder alone wrote code/notes and launched grids.
Coordinator, evaluator and literature reviewer remained read-only.

**Contradicted intermediate implementation:** the first deadline implementation
used executed evaluations as a right-censor observation bound after an offspring
crossed the wall deadline. The evaluator and coordinator independently identified
that an unrecorded event could already have happened within that count. Before
any grid, the builder separated executed work from the confirmed observation
prefix. Late initialization has confirmed count zero; late offspring retain the
previous confirmed prefix; an earlier archive event survives later alignment
censoring. Added regression tests passed. A new slow-initialization fixture first
failed because its mock did not accept a keyword argument; the fixture was fixed
without weakening its assertion. These are implementation corrections, not
failed scientific hypotheses.

**Mechanically checked:** 36 tests and compilation passed before smoke; the
independent evaluator reran all 36 and explicitly approved smoke. The source
snapshot includes untracked/dirty code and notes with SHA-256 hashes; manifests
include all installed distribution versions, command, seed base, Git state,
deadline, runtime, and full parameters. Atomic results checkpoint after every
completed trajectory. A persisted-file interruption regression test verifies
that an interrupted next trial preserves its predecessor.

## Commands and scale decisions

Smoke command:

```bash
python scripts/run_research.py factorial-grid --n 8 16 32 --reps 3 --seed 2611021000 --max-evaluations 2000000 --max-trial-seconds 10 --max-seconds 300 --not-after-utc 2026-11-03T01:42:58Z --label factorial-smoke
```

Local ignored raw evidence:
`research/runs/20261102T213431Z-factorial-grid-factorial-smoke/`.
**Mechanically checked:** 54/54 trajectories; 18 cells with three repetitions
each; no endpoint censoring; complete manifest; all 26 snapshot hashes match;
all seeds unique and sequential; initialization ≤ archive ≤ alignment = executed
= confirmed observations; final archive and aligned counts equal n+1.
Elapsed runner time 0.687 s, maximum trajectory time 0.0475 s.

Twice the n² extrapolation from the n=32 smoke trial time projects 321 seconds
for the full preregistered main grid, comfortably below its 5,400-second cap.
This is a runtime budgeting estimate, not a claim about optimization complexity.
Smoke is excluded from the main inferential estimates. The 36 positive-radius
smoke trajectories had equal endpoint times; this descriptive observation alone
does not prove event equality.

The independent evaluator then approved exactly the preregistered main grid.

```bash
python scripts/run_research.py factorial-grid --n 32 64 128 256 --reps 24 --seed 2611022000 --max-evaluations 20000000 --max-trial-seconds 60 --max-seconds 5400 --not-after-utc 2026-11-03T01:42:58Z --label factorial-main
```

Raw evidence: `research/runs/20261102T213520Z-factorial-grid-factorial-main/`.
**Mechanically checked:** all 576 trajectories completed, each of 24 cells has
24 repetitions, no endpoint censoring, all 27 snapshot hashes match, seeds are
unique `2611022000..2611022575`, and all endpoint/count invariants hold. Elapsed
206.143 s, maximum trial 5.389 s. The n=256 trials used 157.897 s and total
non-trial overhead was 3.415 s.

The preregistered optional n=512 timing estimate is
`2*4*157.897 + 3.415/4 = 1264.03 seconds`, below its 4,500-second cap and the
remaining experiment window. This eligibility decision uses only timing,
censoring, and integrity; no bootstrap mechanism estimates had been computed
when eligibility was submitted for independent approval.

The evaluator independently verified this gate and the coordinator approved the
single preregistered validation before any mechanism contrasts were inspected.

```bash
python scripts/run_research.py factorial-grid --n 512 --reps 24 --seed 2611023000 --max-evaluations 80000000 --max-trial-seconds 180 --max-seconds 4500 --not-after-utc 2026-11-03T01:42:58Z --label factorial-validation512
```

Raw evidence:
`research/runs/20261102T213945Z-factorial-grid-factorial-validation512/`.
**Mechanically checked:** 144/144 trajectories, six cells with 24 repetitions,
zero censoring, seeds `2611023000..2611023143`, all 27 snapshot hashes correct,
all event/count/order invariants correct. Elapsed 695.881 s, maximum trial
18.414 s. Core simulator, runner and analyzer hashes are identical between main
and validation. All sources stayed fixed during each grid. No further scaling,
extra repetitions, or standard-bit comparison was performed.

All three runs total **774 independent trajectories** (54 smoke plus 720 main
and validation), with no censoring. The 1,548 paired endpoint observations are
not 1,548 independent samples. Aggregate runner time was **902.711 seconds**
(15.05 minutes), excluding auditing, editing, tests and analysis. No experiment process
remained running after validation completed.

Recompute the curated distributions and contrasts:

```bash
python scripts/analyze_factorial.py research/runs/20261102T213520Z-factorial-grid-factorial-main research/runs/20261102T213945Z-factorial-grid-factorial-validation512 --output research/reports/20261102T212758Z-factorial-summary.json
```

The [curated JSON summary](20261102T212758Z-factorial-summary.json) contains
all 30 cells, both event distributions (mean, standard deviation, quartiles,
90th/95th percentiles, extrema), paired gaps, mechanism counters, intervals,
source-manifest/result hashes, and analysis parameters. Raw individual values
remain in the ignored run directories. Smoke is excluded from this summary.

## Empirically supported findings

Let `R=mean(T_r=1)/mean(T_r=ceil(log2(n)))`. The table reports R for exact/lazy
mutation and `M=log(R_exact)-log(R_lazy)`. Archive and alignment estimates are
identical in these positive-radius samples. Intervals are **pointwise 95%
percentile bootstrap**, 10,000 draws, seed `2611029000`; whole trajectory
records are independently resampled within cells, preserving paired endpoints.
They are not simultaneous familywise guarantees.

| n | Radius comparison | Exact R [95% interval] | Lazy R [95% interval] | M [95% interval] | Preregistered decision |
|---:|---|---|---|---|---|
| 32 | 1 versus 5 | 1.200 [0.917, 1.584] | 1.084 [0.888, 1.337] | 0.102 [-0.239, 0.447] | Ambiguous |
| 64 | 1 versus 6 | 1.337 [1.071, 1.675] | 1.042 [0.833, 1.308] | 0.250 [-0.072, 0.568] | Ambiguous |
| 128 | 1 versus 7 | 1.607 [1.330, 1.979] | 1.389 [1.116, 1.727] | 0.146 [-0.142, 0.438] | Ambiguous |
| **256, primary** | 1 versus 8 | **1.582 [1.316, 1.925]** | **1.162 [0.970, 1.381]** | **0.309 [0.057, 0.574]** | Same-weight mechanism favored |
| 512, validation | 1 versus 9 | 1.676 [1.373, 2.072] | 1.225 [0.988, 1.522] | 0.314 [0.026, 0.610] | Same-weight mechanism favored |

All **480/480 positive-radius main/validation trajectories** had equal archive
and alignment first times. Thus the sampled stopping attenuation S and factorial
interaction are zero. The bootstrap interval `[0,0]` is an empirical degeneracy:
resampling observed zero gaps cannot reveal rare unobserved gaps. It is **not**
a population bound excluding rare stopping differences. The counterexample
below explicitly rules out universal equality.

The effect concerns **radius sensitivity**, not raw speed. At primary n=256,
lazy mutation is slower in raw evaluations at both positive radii:

| Mutation | r | Mean evaluations | Median | Interquartile range | 95th percentile |
|---|---:|---:|---:|---|---:|
| Exact | 1 | 141,500.4 | 128,885.5 | 115,585.0–155,998.5 | 233,188.8 |
| Lazy | 1 | 216,062.5 | 202,773.0 | 154,520.3–266,893.5 | 353,736.7 |
| Exact | 8 | 89,436.7 | 85,839.0 | 54,613.0–103,700.0 | 146,761.7 |
| Lazy | 8 | 186,004.4 | 181,571.5 | 159,662.5–213,503.0 | 270,866.2 |

At n=512 the corresponding raw means are exact 633,855.4 versus lazy 804,170.6
at r=1, and exact 378,145.5 versus lazy 656,618.9 at r=9. Lazy mutation incurs
evaluated self-loops and halves moving mutations; no global factor-two
normalization was imposed.

Stopping events matter at r=0. For n=256, the exact mean archive/alignment costs
are 345,901.6 / 416,404.8, with mean paired gap 70,503.2 evaluations (only 5/24
zero gaps). Lazy costs are 635,893.3 / 814,936.7, with mean gap 179,043.5 (4/24
zero gaps). The archive therefore genuinely implements a distinct event.

Descriptive mechanism counters also show that self-loops are not globally idle:
at n=256 they directly solve an average of 63 target recipients at r=1 and 54.0
at r=8, versus zero at r=0. This documents useful copy communication but does
not independently identify its causal contribution to the runtime contrast.

## Proved findings and source-based inferences

- The canonical scalarization has a unique target minimum, so target hits persist
  under the stated noiseless replacement rule.
- Complementing paper genotypes while retaining indices gives an exact
  weight-process conjugacy preserving ascending cyclic order. The unchanged-
  genotype index reversal instead reverses scan order.
- A passive all-generated archive contains every incumbent's origin, so
  `T_archive <= T_alignment` pathwise; equality need not hold.
- **Source-based inference, r>=1 only:** lazy one-bit with self-loop probability
  1/2 satisfies type A. The endpoint argument and midpoint-restricted solved-
  prefix/suffix fill in Lemmas 4–5 extend the paper's upper expectation argument
  to alignment. This is not its explicitly stated runtime event. The precise
  conditioning, fresh-draw filtration and stage bounds are in the comparison
  note. No tail or lazy lower bound is transferred, and no experiment is used
  to prove an asymptotic result.

The source is Benjamin Doerr, Moaad Elmoutassim, Martin S. Krejca, and Guy
Mushiata Kibulu (2026), *Understanding the Co-evolutionary Solution Exchange
of the MOEA/D: Already the Smallest Communication Radius Gives the Best-Possible
Speed-Up*, [arXiv:2610.35373v1](https://arxiv.org/html/2610.35373v1),
[DOI:10.48550/arXiv.2610.35373](https://doi.org/10.48550/arXiv.2610.35373).
Equation (1)/Algorithm 1, Theorem 2, Lemmas 4–5, and the type-B caveats are
located precisely in the source-cited model table. No source PDF was modified.

## Mechanically checked findings

- Initialization counting, archive inclusion of universally rejected offspring,
  per-offspring stopping, lazy neighbor propagation, scalarization ordering,
  index transformation, and deterministic seeded paths have regression tests.
- Checkpoints persist to disk after each completed trajectory; a subsequent
  interruption preserves them. Separate trial/total deadlines, confirmed
  censoring prefixes, round-robin balance, source hashes, and paired-bootstrap
  censor handling are tested.
- The evaluator independently recomputed all 720 main/validation raw records
  without importing the analysis functions. **825 numerical summary checks**
  matched, including every cell distribution and all radius/interaction
  bootstrap contrasts. Optional snapshot/code-identity checks also passed.
- Final full-suite and compilation results are recorded in the final verdict
  section below; its approval is not assumed in advance.

## Contradicted claims and negative results

**Universal equality at positive radius is contradicted.** Set n=3, r=1,
initial weights `[1,1,1,2]` (archive initially incomplete). The feasible cyclic
offspring sequence `[0,0,0,3,1,2]` completes the archive at evaluation 8 while
the population is `[0,1,3,3]`; alignment first occurs at evaluation 10. The
path has positive probability for exact one-bit, and for lazy one-bit when
its six gates choose moving mutation. Both reviewers independently checked
the witness; the builder added it as a regression for both mutation arms.

The same witness corrects C10: both endpoint targets are solved by evaluation 8,
but alignment occurs at 10. Thus a universal pathwise identity between alignment
time and the last endpoint hit is contradicted. This small witness does not
disprove the separate conjecture of asymptotic or typical endpoint dominance;
that bottleneck question remains unresolved.

The data do not support an overall lazy speedup. The smaller-n mechanism
contrasts remain inconclusive. The finite study neither establishes the
legacy logarithmic-radius necessity conjecture nor refutes it asymptotically.
The apparent printed min/max and type-B constant/proof issues are preserved,
not silently repaired. Earlier whole-process invariant C5 remains contradicted.

## Conjectured mechanism and open questions

**Conjectured:** direct neighbor broadcast of same-weight offspring is a plausible mediator of
the attenuation. The present mutation factor simultaneously changes same-weight
availability, moving frequency, and cyclic timing; it does not isolate those
three pathways. Standard bit mutation's multi-bit jumps and state-dependent
same-weight probabilities were not reproduced.

**Open:** exact-one-bit asymptotics, a logarithmic threshold or its absence, the probability
and magnitude of rare positive-radius stopping gaps, and a justified lower-bound
transfer remain open. No noise claim changed. No log-log law was fitted, and
pointwise intervals should not be read as simultaneous certainty.

**Best next action:** preregister a lazy-1/2 ablation suppressing only neighbor
broadcast on self-loop offspring. Preserve generation/evaluation, archive,
breeder self-comparison, moving-offspring broadcasts, cyclic order, and paired
random streams. This directly tests broadcast against reduced moves/cyclic
retiming. It is a new study and was not launched here.

## Final validation and independent verdict

**Mechanically checked at 2026-11-02 21:53 UTC:**

```bash
python -m unittest discover -s tests -v
python -m py_compile sim.py large.py scripts/run_research.py scripts/analyze_factorial.py
git diff --check
git diff --exit-code -- '*.pdf'
```

All **37 tests passed** (0.494 s); compilation, whitespace checks, and the
no-PDF-change check passed. No test was weakened. The original 16 tests remain.

Changed code/tests: `large.py`, `scripts/run_research.py`,
`scripts/analyze_factorial.py`, `tests/test_controlled.py`,
`tests/test_factorial_analysis.py`, `tests/test_runner.py`.
Changed research notes: `PROJECT.md`, `CLAIMS.md`, `STATUS.md`, `EXPERIMENTS.md`,
`LITERATURE.md`, `PAPER_COMPARISON.md`, new `FACTORIAL_PREREG.md`, this report,
and its curated JSON summary. Raw runs are ignored by Git. No commit was made.

The evaluator's independent final verdict is reproduced below. Both reviewers
remained read-only; this verdict was written by the evaluator and persisted by
the sole-writing builder.

> FINAL INDEPENDENT EVALUATOR VERDICT — APPROVED, 2026-11-02 21:55:13 UTC. No blocking issue remains in the final model implementation, runner safeguards, numerical summaries, or bounded empirical claims. I reviewed canonical cyclic semantics before the main grid, required the confirmed-prefix censoring correction before any grid, and independently approved each scale gate. Independent audits verified all 774 recorded trajectories and snapshot/seed/order/censoring invariants. Separate raw-data recomputation of the 720 main/validation trajectories, without importing the builder's analysis functions, matched 825 numerical checks. Final independent validation: all 37 unit tests passed (0.472 s), four modules compiled in memory, core code hashes match the executed snapshots, summary input hashes match raw evidence, and whitespace/PDF/HEAD checks passed. The preregistered primary n=256 result and n=512 validation support the exact-to-lazy mutation change as the better explanation of tested radius sensitivity. This does not establish direct broadcast mediation, an overall lazy speedup, universal stopping-time equality, or any exact-one-bit asymptotic result. C10 now correctly separates a contradicted pathwise identity from unresolved asymptotic endpoint dominance. Best next bounded action: a separately preregistered lazy self-loop neighbor-broadcast ablation. Please persist this verdict and final completion timestamp; no further experiments or code changes are needed.

The independent literature reviewer also approved the final source/proof scope:

> Final source/proof-scope approval: PAPER_COMPARISON, CLAIMS C11–C15, report proof/scope sections, PROJECT and LITERATURE now correctly distinguish cited source results, algebraic/model facts, the alignment expectation inference, finite empirical mutation-rule evidence, and conjectured direct broadcast mediation. The midpoint, r>=1, filtration/conditional-delay corrections are sound; no tail/lazy-lower transfer or universal stopping equality is claimed. No further required source/proof wording corrections. You may record this independent literature verdict, with scope: it uses cited Lemma4 as an external result and does not certify/reprove every preprint argument. Read-only throughout; no experiments launched.

The study stopped after its planned controlled comparison and validation met the
finish conditions. The exact-one-bit asymptotic and direct-mediation questions
remain open; no additional experiment was started merely because more time was
available.
