# Lazy same-weight broadcast ON/OFF preregistration

Protocol draft recorded 2026-11-03 02:38:19 UTC, before any recorded grid.
Final pre-smoke protocol freeze: **2026-11-03 02:40:40 UTC**.
The final reviewed version and its SHA-256 will be frozen in the smoke source
snapshot before execution. Status: **conjectured** broadcast effect; no outcomes
exist for this study yet. Prior factorial evidence is not reused as new data.

## Authorization, baseline and scope refinement

This is a new two-hour authorized study, activated **2026-11-03 02:28:31 UTC**.
Stop starting experiments at **03:58:31 UTC**; hard stop **04:28:31 UTC**.
Reserve the final 30 minutes for independent recomputation, tests and reporting.
The completed earlier goal/deadline does not govern this study.

The latest request compares **two lazy q=1/2 arms**, ON and OFF. This refines
`NEXT_DIRECTIONS.md`'s three-arm proposal before any outcomes: omit its fresh
exact baseline. No new mutation operator, q value, scheduler, noise model,
asymptotic fit, or natural-mediation fraction is studied. The prior report,
preregistration and raw records remain unchanged.

Baseline HEAD `7c4e8addcca6adf04d65f74fec05244bbb26ab5f` has the expected
uncommitted preceding study/roadmap changes. Exact pre-edit dirty sources, patch,
Git status and dependencies are saved under
`research/runs/20261103T022831Z-broadcast-baseline/` (28 source files).
Before implementation, all 37 tests passed (0.674 s) and compilation of sim.py,
large.py, run_research.py and analyze_factorial.py passed. Baseline default
Python was `/Users/parth/miniforge3/bin/python`; runs explicitly use
`.venv/bin/python` (NumPy 2.4.3, Matplotlib 3.10.8), with workspace cache paths.
Only the builder writes or launches experiments. Independent evaluator and
literature constraints preceded implementation; smoke and main need explicit
evaluator approval of implemented semantics and safeguards.

## Frozen process and intervention

Keep independent binomial initialization, n+1 initialization evaluations,
`C_j(w)=max{j(n-w),(n-j)w}`, ascending cyclic own-parent breeders, clipped radius,
non-worsening ties, and passive archive insertion of every initialized/generated
weight, including rejected offspring. Check archive/alignment after each
offspring and continue to alignment or censoring. The source mapping and
apparent printed min/max issue remain in `PAPER_COMPARISON.md`.

Both arms use the same q=1/2 lazy kernel. A hold is defined by the offspring
weight equalling the current breeder's parent weight, not by recipient equality
or acceptance. ON offers it normally. OFF suppresses only replacement at
recipients j≠breeder on a hold. Retain its evaluation, archive processing,
breeder self-comparison, cyclic phase advancement, and all moving-offspring
offers. Different stopping times may produce different cumulative move/hold
counts; the per-call mechanism is fixed.

OFF changes the paper's replacement rule, so type-A membership alone transfers
no bound to OFF. The uniform-scheduler C16 identity does not apply to cyclic
OFF. No factor-two rescaling is assumed.

## Blocks, seeds, phases and safeguards

One block is one `(run,n,r,repetition)` with independent seed `seed_base+index`
in round-robin repetition/configuration order. ON/OFF instantiate separate,
identically seeded initialization/gate/direction generators using the existing
SeedSequence split. Both streams draw n+1 gate and direction uniforms each
sweep; coupling is by absolute offspring index, not accepted/moving update count.
Each arm keeps its own stopping time. Blocks across n/r and runs use distinct
seeds. Counterbalance arm order by **repetition parity within each (n,r)**:
even repetitions ON then OFF, odd OFF then ON. Global block parity is unsuitable
when two radius cells would lock each cell to one arm order.

Before work, manifest all planned blocks, seeds and arm orders, including
planned-but-unstarted blocks. Checkpoint atomically after every completed arm.
Retain missing partners, entire unstarted blocks, and endpoint-specific
censoring. A complete-case subset cannot support unconditional mean contrasts.
Primary decisions require the full planned run and no censored endpoints.

Keep per-trial and total deadlines, operation caps, source/dependency snapshots,
and executed-versus-confirmed observation counts. Phase observations commit
only after the post-operation deadline check. Record per-target first hits F_j,
last endpoint hit H=max(F_0,F_n), interior completion and T_alignment-H, without
drawing randomness. Initialization hits are at n+1, but late initialization
confirms none. A later censored operation cannot erase earlier confirmed hits.
Use only H≤T_alignment and T_archive≤T_alignment; archive and H have no universal
ordering. Target hits persist, so completed T_alignment=max_j F_j.

Tests must cover r=0 path identity, moving-only/no-hold identity, useful ON copy
versus suppressed OFF recipient changes, old-default seeded equivalence,
observer passivity, confirmed phase censoring, counterbalanced ordering,
persisted checkpoints/plan/snapshots and missing/censored block inference.

## Preregistered grids and gates

| Stage | n | Radii | Blocks per (n,r) | Seed base | Trajectories |
|---|---|---|---:|---:|---:|
| Smoke | 8,32 | 0,1,ceil(log2 n) | 3 | 2611031000 | 36 |
| Primary | 256 | 1,8 | 48 | 2611032000 | 192 |
| Validation | 512 | 1,9 | 24 | 2611033000 | 96 |

Maximum 324 trajectories/162 independent blocks; two paired endpoints do not
double sample size. Smoke is excluded from inferential summaries. Radius-zero
smoke validates pathwise ON/OFF identity; no large r=0 grid is needed.

- Smoke caps: 2,000,000 evaluations, 10 s/trial, 300 s total.
- Primary caps: 20,000,000 evaluations, 60 s/trial, 2,700 s total.
- Validation caps: 80,000,000 evaluations, 180 s/trial, 1,800 s total.
- Every command uses `--not-after-utc 2026-11-03T03:58:31Z`.

Main requires uncensored smoke, all semantic/integrity checks, evaluator approval,
and a conservative timing projection below its cap and remaining experiment
window. Project from positive-radius n=32 smoke time, multiplied by
`(256/32)^2*(48/3)*2`. This is a compute-budget proxy, not a runtime law.
Validation requires complete uncensored main and integrity approval. Predict
validation time as `2*(512/256)^2*(24/48)` times main trial time plus half its
observed overhead. Require that estimate below 1,800 s and fitting before the
cutoff with 120 s slack. Decide validation from timing/censoring/integrity before
inspecting mechanism contrasts. If a gate fails, retain partial evidence and
report the failed gate; do not silently alter n/repetitions or chase significance.

## Analysis frozen before outcomes

Alignment is primary; archive and phases are paired secondary/descriptive
outcomes. Use raw evaluation counts and their full observed distributions.
Let `A_r=log(mean(T_OFF,r)/mean(T_ON,r))` and
`Delta=A_1-A_log = D_OFF-D_ON`, where
`D_arm=log(mean(T_arm,1)/mean(T_arm,ceil(log2 n)))`.

Use 20,000 percentile-bootstrap draws, seed **2611039000**. Resample whole
ON/OFF × archive/alignment blocks jointly within each radius, independently
across radii; retain the paired phase values in those same blocks. For primary
alignment A_1 and Delta use **97.5% two-sided percentile intervals each**
(quantiles 0.0125,0.9875), a nominal Bonferroni-95 family within a given n.
Bootstrap coverage is approximate, not an exact finite-sample guarantee. The
n=512 validation is a separate family, not pooled with n=256. All archive/phase
and other interval summaries are 95% pointwise descriptive intervals.

Require both primary lower limits >0 to support useful r=1 broadcast
contributing to the finite attenuation. Delta alone could reflect large-radius
harm. Report all outcomes, including uniform benefit without resolved radius
interaction, large-radius harm, opposite signs, and ambiguity. Nonsignificance
does not prove zero. If any planned arm/block is missing or required endpoint
is censored, the unconditional primary conclusion is inconclusive; do not drop
records or impute unobserved runtimes.

Report means, standard deviations, median/quartiles, upper quantiles/extrema,
paired endpoint gaps, observed limits/censoring, ON/OFF phase distributions and
paired mean phase differences. Phase and level-conditioned/copy-count findings
are descriptive and cannot establish a selection-conditioned drift bound.
The two-arm intervention estimates a broadcast-policy effect at fixed lazy
mutation; it does not identify the entire earlier exact-to-lazy effect, natural
mediation, or an asymptotic result. C15's exclusive wording must not be silently
upgraded to a proof or sole-explanation claim.
