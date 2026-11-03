# Lazy same-weight neighbor-broadcast ablation

Activated **2026-11-03 02:28:31 UTC**. New-study experiment-start cutoff:
**03:58:31 UTC**; hard deadline **04:28:31 UTC**. All planned experiments
finished at **02:57:17.945 UTC**. Report completed after independent approval
at **2026-11-03 03:04:56 UTC**, 36 minutes 25 seconds after activation.
All computation is local, cloud
spend $0; model/API billing is unmeasured. No commits, pushes, PDF changes,
RunPod, new mutation operator, scheduler, q value, or noisy-proof work.

## Question and controlled change

At fixed lazy one-bit q=1/2, does broadcasting same-weight offspring to other
subproblems help r=1 and contribute to finite radius attenuation? ON broadcasts
normally. OFF suppresses only j≠breeder replacement when offspring weight equals
its current breeder's parent weight. Evaluation, archive processing, self-
comparison, moving-offspring communication, initialization, scalarization, ties,
radius and cyclic visits remain fixed. The new two-arm request refines the
earlier three-arm roadmap before outcomes; no fresh exact arm is run.

The [frozen preregistration](../BROADCAST_PREREG.md) specifies paired blocks,
phase observations, missing/censor rules, seeds, caps and statistical policy.
The [canonical source comparison](../PAPER_COMPARISON.md) remains applicable.
OFF changes Algorithm 1's replacement rule, so the paper's type-A conditions
alone do not transfer its upper bound to OFF. C16's uniform-scheduler identity
also does not apply. This estimates a finite broadcast-policy effect, not a
natural-mediation fraction of the earlier exact-to-lazy contrast.

## Baseline, implementation and independent gates

**Mechanically checked:** baseline HEAD
`7c4e8addcca6adf04d65f74fec05244bbb26ab5f` is unchanged, with prior-study dirty
files preserved. Before edits, all 37 tests passed (0.674 s) and four modules
compiled. Exact dirty source/patch/status/dependencies are archived under
`research/runs/20261103T022831Z-broadcast-baseline/` (28 files).

The initial baseline command used the configured base Python and encountered
an unwritable Matplotlib cache warning; explicit `.venv/bin/python` and workspace
cache paths resolved this. The first baseline-manifest helper invocation used
a relative output path and failed before writing its manifest; rerunning with
the absolute path succeeded before implementation. No trial data were involved.

The builder alone edits and launches grids. Coordinator and reviewers remain
read-only. Independent pre-change audits preceded implementation. Optional core
flags preserve the old default API/seeded results while adding the broadcast
mask and passive confirmed-prefix first-hit phases. A new runner mode declares
every planned block/arm before execution and checkpoints each arm, including
partial-block/interruption cases. The separate analyzer retains all planned
blocks and jointly resamples arm/endpoint pairs. Arm order alternates by
repetition parity within each radius, rather than global block parity.

**Mechanically checked:** all 54 tests passed (builder 0.886 s; independent
evaluator 0.921 s), five modules compiled, whitespace checks passed. Tests include
legacy golden output, ON/OFF r=0/moving-only identity, useful ON copies, suppressed
OFF effects, observer passivity, deadline-confirmed phase hits, persisted
checkpoint/plan/source hashes, and missing/censored-block inference.
The evaluator approved smoke after reviewing code and the preregistration frozen
at **02:40:40 UTC**.

## Commands, timing and integrity

All experiment commands use `MPLCONFIGDIR=.cache/matplotlib XDG_CACHE_HOME=.cache`.
The workspace cache directories are ignored and excluded from source snapshots.

```bash
MPLCONFIGDIR=.cache/matplotlib XDG_CACHE_HOME=.cache .venv/bin/python scripts/run_research.py broadcast-grid --n 8 32 --include-zero --blocks 3 --seed 2611031000 --max-evaluations 2000000 --max-trial-seconds 10 --max-seconds 300 --not-after-utc 2026-11-03T03:58:31Z --label broadcast-smoke
```

Smoke evidence: `research/runs/20261103T024139Z-broadcast-grid-broadcast-smoke/`.
**Mechanically checked:** 36 trajectories, all 18 planned blocks complete,
zero censoring, 31 source hashes verified; all phase/count/seed/order invariants
hold. All six radius-zero block pairs match exactly apart from execution/arm
metadata. OFF hold-induced recipient changes/target acquisitions are zero.
Elapsed 0.9915 s; max trial 0.05955 s. Positive-radius n=32 trial time was
0.192639 s, giving the frozen conservative main prediction 394.525 s, below
its 2,700-second cap. This is a compute-budget projection, not a complexity law.

The evaluator independently audited smoke and explicitly approved main.

```bash
MPLCONFIGDIR=.cache/matplotlib XDG_CACHE_HOME=.cache .venv/bin/python scripts/run_research.py broadcast-grid --n 256 --blocks 48 --seed 2611032000 --max-evaluations 20000000 --max-trial-seconds 60 --max-seconds 2700 --not-after-utc 2026-11-03T03:58:31Z --label broadcast-main
```

Main evidence: `research/runs/20261103T024310Z-broadcast-grid-broadcast-main/`.
**Mechanically checked:** 192/192 trajectories, all 96 planned blocks complete,
zero censoring; 32 snapshot hashes and all event/confirmed-phase/final-count/
seed/arm-order invariants pass. OFF self-loop recipient changes/target
acquisitions are zero. Elapsed 235.6517 s, trial time 233.7861 s, overhead
1.8656 s, maximum trial 2.9843 s. Finished 2026-11-03 02:47:06.629 UTC.

The frozen validation projection is `4*233.7861+1.8656/2=936.077 seconds`,
below its 1,800-second cap and fitting the remaining cutoff with 120 s slack.
Eligibility was submitted for independent review without computing or inspecting
mechanism contrasts. The evaluator independently verified main and explicitly
approved validation; the coordinator authorized its exact frozen parameters.
This gate passed before validation launch and before mechanism analysis.

```bash
MPLCONFIGDIR=.cache/matplotlib XDG_CACHE_HOME=.cache .venv/bin/python scripts/run_research.py broadcast-grid --n 512 --blocks 24 --seed 2611033000 --max-evaluations 80000000 --max-trial-seconds 180 --max-seconds 1800 --not-after-utc 2026-11-03T03:58:31Z --label broadcast-validation512
```

Validation evidence: `research/runs/20261103T024933Z-broadcast-grid-broadcast-validation512/`.
**Mechanically checked:** 96 trajectories in all 48 planned blocks completed,
zero censoring, 32 source hashes verified. Elapsed 464.5511 s; maximum trial
10.1019 s. Finished 2026-11-03 02:57:17.945 UTC. All phase/event/seed/order
invariants pass, including zero OFF hold-induced changes. Computational source,
tests and frozen preregistration match the main snapshot. Only the report/status
notes changed between the main and validation snapshots; no source changed
while a grid ran.

Totals: **324 trajectories in 162 independent seed blocks**, including 36 smoke
trajectories/18 blocks. Inference uses 288 trajectories/144 blocks; neither the
paired arms nor two stopping observations create additional independent samples.
There are no missing arms, unstarted planned blocks or censored endpoints.
Runner elapsed time totals **701.1943 s (11 min 41 s)**. Setup, implementation,
review and reporting time are separate. No experiment process remains running;
no further grid is authorized. Local cloud spend is $0.

Seeds are 2611031000–2611031017 (smoke), 2611032000–2611032095 (main), and
2611033000–2611033047 (validation). Each block shares a seed across two separate
identically initialized generators, with unconditional gate/direction consumption
by absolute offspring index. Distinct blocks have independent seed assignments.
Every manifest records dirty Git state, exact source hashes/snapshots, command,
full planned blocks, Python/dependency versions, deadlines, order and timing.

```bash
MPLCONFIGDIR=.cache/matplotlib XDG_CACHE_HOME=.cache .venv/bin/python scripts/analyze_broadcast.py research/runs/20261103T024310Z-broadcast-grid-broadcast-main research/runs/20261103T024933Z-broadcast-grid-broadcast-validation512 --output research/reports/20261103T022831Z-broadcast-summary.json
```

The [curated summary](20261103T022831Z-broadcast-summary.json) records raw and
manifest hashes, distributions, censoring, paired phase effects and uncertainty.
Smoke is excluded. The independent evaluator recomputed from raw data without
importing the analyzer and matched **860 numerical checks**, including all
contrasts, intervals, means, distribution statistics, phase summaries and counts.

## Empirically supported: broadcast contributes at the tested sizes

The primary alignment estimands are
`A1=log(mean(T_OFF,r1)/mean(T_ON,r1))` and
`Delta=A1-Alog=D_OFF-D_ON`, where `D=log(mean(T_r1)/mean(T_rlog))`.
Whole ON/OFF × archive/alignment blocks are resampled jointly within each radius,
with independent resampling across radii. The frozen 20,000 bootstrap draws use
seed 2611039000. Each of the two primary contrasts uses a 97.5% two-sided
percentile interval: an approximate nominal Bonferroni 95% family at each n,
not exact bootstrap coverage. Validation is a separate family; other intervals
below are pointwise descriptive 95% intervals.

| Study | A1 [97.5% interval] | Delta [97.5% interval] | OFF/ON mean at r=1 | R_ON; R_OFF |
|---|---|---|---|---|
| Primary n=256, 48 blocks/radius | 0.3579 [0.2529, 0.4682] | 0.3568 [0.2518, 0.4673] | 1.4303 | 1.1381; 1.6261 |
| Validation n=512, 24 blocks/radius | 0.1976 [0.0979, 0.3148] | 0.1976 [0.0979, 0.3148] | 1.2185 | 1.2647; 1.5410 |

Both preregistered lower bounds are positive at each size. Suppressing only
same-weight neighbor broadcast increases mean evaluations at r=1 by about 43%
(n=256) and 22% (n=512), and increases the tested r=1 versus logarithmic-radius
contrast. This supports a beneficial finite broadcast-policy contribution to
radius attenuation. The two sizes agree in direction, with different effect
magnitudes; this is not a scaling trend or asymptotic statement. Archive effects
coincide numerically in this sample, as detailed below.

Alignment evaluations include all n+1 initial evaluations. Values are rounded
to the nearest evaluation; full precision, minima, maxima, standard deviations,
quantiles and mean intervals are in the curated JSON.

| n | r | Arm | Blocks | Mean | Median | IQR | 95th percentile |
|---|---|---|---:|---:|---:|---|---:|
| 256 | 1 | ON | 48 | 199,427 | 176,560 | 151,245–249,034 | 343,802 |
| 256 | 1 | OFF | 48 | 285,233 | 278,716 | 239,140–320,285 | 407,306 |
| 256 | 8 | ON | 48 | 175,221 | 160,754 | 127,474–210,741 | 313,991 |
| 256 | 8 | OFF | 48 | 175,408 | 161,911 | 127,474–210,741 | 313,991 |
| 512 | 1 | ON | 24 | 859,938 | 783,609 | 736,798–981,113 | 1,432,528 |
| 512 | 1 | OFF | 24 | 1,047,803 | 1,011,894 | 848,374–1,227,097 | 1,445,455 |
| 512 | 9 | ON | 24 | 679,939 | 660,744 | 466,575–801,562 | 1,184,158 |
| 512 | 9 | OFF | 24 | 679,939 | 660,744 | 466,575–801,562 | 1,184,158 |

**Negative/limited finding:** the measured high-radius completion effect is
small or unresolved. At n=256,r=8, 47/48 paired alignment times tie and one OFF
trajectory takes 8,997 additional evaluations; `Alog=0.001069`, pointwise 95%
interval `[0,0.003479]`. At n=512,r=9 all 24 paired completion times tie.
The resulting bootstrap `[0,0]` is empirical degeneracy, not proof of structural
zero, equivalence, or absence of rare effects. At r=1 the OFF−ON differences are
positive/tied/negative in 40/8/0 primary pairs and 16/8/0 validation pairs.
No negative difference was observed; no pathwise monotonicity is proved.

## Empirically supported: passive phase findings

Let `F_j` be the confirmed first evaluation at which subproblem j holds its
unique target, `H=max(F_0,F_n)` the last endpoint subproblem target-hit time,
and `I=max(F_1,...,F_(n-1))` the interior completion time. No RNG is consumed by
these observers. Hits crossing a wall deadline are excluded from confirmed
phase times. In all **288 main/validation trajectories**, `T_archive=H=T_alignment`
and `I<H`; the observed post-endpoint residual is zero.

| n,r | Mean paired OFF−ON H [95% interval] | Mean paired OFF−ON I [95% interval] |
|---|---|---|
| 256,1 | 85,805.73 [64,678.05,107,587.06] | 64,046.15 [54,798.87,73,512.51] |
| 256,8 | 187.44 [0,562.31] | 176.77 [0,530.31] |
| 512,1 | 187,865.25 [105,806.33,276,615.16] | 291,639.71 [237,346.73,352,152.17] |
| 512,9 | 0 [0,0] | 2,116.29 [0,5,643.50] |

At r=1 broadcasting advances both endpoint and interior target-hit times on
average; the last endpoint determines sampled completion. Equal completion
at n=512,r=9 masks different interior progress in two of 24 pairs (OFF is later
by 16,929 and 33,862 evaluations). These are passive
descriptions, not conditional-drift proofs or causal conditioning on copy counts.
Endpoint target hits should not be conflated with discovery of those weights
in the global archive. There is no universal ordering of H and archive time.

## Proved facts and source-transfer boundary

The noiseless scalarization's unique target is absorbing, so
`T_alignment=max_j F_j`. Every incumbent weight has been archived; consequently
`T_archive<=T_alignment`. These deterministic facts apply to both current arms.
In OFF, self-loop offspring change no population weight or archive state,
but still consume an evaluation
and advance the cyclic breeder phase. This is why the separate iid-uniform
scheduler identity C16 does not justify a factor-two conversion here.

Doerr, Elmoutassim, Krejca and Kibulu, *Understanding the Co-evolutionary Solution
Exchange of the MOEA/D: Already the Smallest Communication Radius Gives the
Best-Possible Speed-Up* (2026), [arXiv:2610.35373v1](https://arxiv.org/html/2610.35373v1),
§3 Algorithm 1 offers every offspring to all clipped neighbors. ON follows
that communication rule. OFF deliberately changes it; keeping type-A mutation
constants `C_A=alpha=1/2` does not transfer Theorem 2 to OFF. The previously
recorded source-based alignment expectation inference C12 remains restricted
to canonical ON, with its existing no-tail/no-lazy-lower-bound caveats.
No new asymptotic result is claimed.

## Contradicted universal statements

The existing C14 witness remains decisive: n=3,r=1, initial `[1,1,1,2]`,
feasible offspring tape `[0,0,0,3,1,2]` reaches archive coverage and both endpoint
targets by evaluation 8, but alignment only at 10. It contradicts universal
archive/alignment equality and universal last-endpoint/alignment equality.
The present zero residuals do not repair those statements or establish a
population upper bound on rare gaps. The witness does not refute asymptotic
endpoint dominance, which remains open.

## Conjectured mechanism and open findings

**Conjectured:** particular local copy-spread/frontier dynamics explain why the
broadcast benefit is concentrated at small radius. The intervention estimates
the finite total effect of the broadcast policy; it does not isolate every
intermediate mechanism or justify conditioning on observed copy counts.

**Open:** how much of the earlier exact-to-lazy contrast is attributable to
broadcast versus moving frequency/cyclic retiming. This two-arm study holds
q fixed and runs no fresh exact arm; it proves neither exclusive mediation nor
a natural-mediation fraction. Standard-bit mutation has multi-bit jumps and
state-dependent same-weight probabilities absent here. Exact-one-bit asymptotics,
rare completion gaps, and the noisy proof remain unresolved. No law was fitted.

## Changed files, verification and best next action

This study changes `large.py` and `scripts/run_research.py`, adds
`scripts/analyze_broadcast.py`, `tests/test_broadcast.py`, and the frozen
`research/BROADCAST_PREREG.md`, and updates this report/summary plus the durable
CLAIMS, STATUS, PROJECT, EXPERIMENTS and NEXT_DIRECTIONS notes. Existing tests,
the previous report/preregistration/curated data and source PDFs are preserved.
No code changes followed the preregistered grids.

```bash
MPLCONFIGDIR=.cache/matplotlib XDG_CACHE_HOME=.cache .venv/bin/python -m unittest discover -s tests -v
.venv/bin/python -m py_compile sim.py large.py scripts/run_research.py scripts/analyze_factorial.py scripts/analyze_broadcast.py
git diff --check
```

**Mechanically checked:** final builder validation passed all 54 tests (0.932 s),
five modules compiled, and `git diff --check` passed. Current core code, new tests
and preregistration hashes match both executed main/validation snapshots; all
32 hashes in each snapshot verify. Original test files, the previous report and
preregistration, HEAD and tracked PDFs remain unchanged. The previous curated
summary still verifies its raw inputs. A read-only preservation helper initially
requested the old JSON summary from a text-source snapshot that excludes JSON;
the corrected check verifies its recorded raw/manifest hashes instead. No files
or trial data were changed by that failed check.

**Independent source/scope review — APPROVED, 2026-11-03 03:03:24 UTC.**
The literature reviewer found no source/proof overstatement: C15 preserves
exclusive mediation as open; C12 is restricted to canonical ON; OFF theorem
transfer and cyclic use of C16 are excluded; C10/C14 counterexamples remain;
and high-radius completion ties are distinguished from interior/path effects.
This is a source/scope review, not a reproof of every external paper argument.

**Final independent evaluator verdict:**

> Approved by the independent evaluator at 2026-11-03 03:04:23 UTC; no blocking
> issue remains. The implemented process, paired/censor-aware runner and analysis,
> final claims/report, and all 324 recorded trajectories (288 inferential) were
> reviewed. Separate raw-data recomputation matched 860 numeric checks and all
> input hashes. Snapshot integrity and frozen computational sources/tests/
> preregistration were verified; independent in-memory compilation, whitespace,
> PDF and HEAD checks passed. The unchanged 54-test implementation passed
> independently before the grids and passed the final builder suite. The evidence
> supports a finite beneficial broadcast-policy contribution at fixed q=1/2 and
> n=256/512. Exclusive mediation, structural zero at high radius, universal
> stopping/endpoint identities, cyclic time-change and asymptotic conclusions
> remain open or unestablished as explicitly recorded.

The report and durable status were completed at **2026-11-03 03:04:56 UTC**,
36 minutes 25 seconds after activation and well before the cutoff/deadline.
All authorized work is complete; no experiment was started after validation.
The best next bounded action is a separately preregistered standard-bit bridge
to the source paper, retaining the canonical process and paired stopping/phase
observers, after independent review of its exact weight kernel. It is a proposal;
no additional implementation, trial or spend is authorized by this report.
