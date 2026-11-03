# Controlled radius study preregistration

Initial design recorded: **2026-11-02 21:31 UTC**. Reviewed revision 2, final
pre-smoke freeze: **2026-11-02 21:33:47 UTC**. The exact version and SHA-256 are
preserved in the smoke source snapshot; no grid outcomes preceded this freeze. Status:
**conjectured** competing mechanisms; protocol and finite checks are
**mechanically checked** only after implementation review. This is a bounded
finite-size study, with no fitted scaling law or asymptotic inference.

## Activation and gates

- UTC activation: 2026-11-02 21:27:58; new-experiment cutoff:
  2026-11-03 01:42:58; hard deadline: 2026-11-03 02:27:58.
- Baseline HEAD: `7c4e8addcca6adf04d65f74fec05244bbb26ab5f`; clean Git status.
- Baseline coordinator command `PYTHONDONTWRITEBYTECODE=1 python -m unittest
  discover -s tests -v`: all 16 tests passed (0.118 s test runtime).
- Baseline builder command `python -m py_compile sim.py large.py
  scripts/run_research.py`: passed before edits.
- Python: `.venv/bin/python`, 3.13.12; NumPy 2.4.3; Matplotlib 3.10.8.
- Builder is the only writer and experiment launcher. Both independent audits
  were relayed before substantive edits. Main grid requires evaluator approval
  of implemented semantics and runner safeguards. Sources stay fixed during a run.

## Fixed process and pairing

Use `large.run_controlled`, independently initialized `Bin(n,1/2)` weights,
`C_j(w)=max(j(n-w),(n-j)w)`, ascending cyclic breeders, each breeder's own
incumbent, clipped symmetric radius, unconditional communication to all
neighbors, and non-worsening acceptance including ties. Cyclic means scan order,
not a ring. The paper's order-preserving genotype-complement map and apparent
min/max typo are documented in `PAPER_COMPARISON.md`.

Only mutation and stopping event vary. Exact mutation changes one uniformly
chosen bit. Lazy mutation returns the parent weight with probability exactly
`1/2`, otherwise performs that same one-bit mutation. A lazy copy is offered to
all neighbors and can change their incumbents. All evaluations count, including
lazy copies and the `n+1` initializations. A passive archive records every initial
weight and every generated weight, including universally rejected offspring.
Archive and simultaneous exact alignment are checked after every offspring.

Observe both first-passage times on each trajectory, continuing after archive
completion to alignment or a cap. This implements the 2×2 comparison with paired
stopping endpoints; two endpoints are **not** two independent trajectories.
Archive success remains observed if alignment later censors. A censored endpoint
retains its finite confirmed-prefix `observation_evaluations` and censoring reason.
`evaluations` separately counts executed work, including an operation crossing
the wall deadline. Such late work does not extend the confirmed censoring prefix;
late initialization has a zero confirmed prefix. State counters describe executed
work and are not substituted for confirmed endpoint observations.

For trajectory index `i`, seed is `seed_base+i`. Distinct `(n,r,mutation)` cells
and repetitions have distinct seeds; no mutation or radius pairing is used.
`SeedSequence(seed).spawn(3)` creates separate PCG64 initialization, gate, and
direction streams. Every sweep prefetches `n+1` gate and direction uniforms in
both mutation arms, including for lazy copies. Initialization and random-stream
policy are therefore unchanged between arms. Endpoints share the same path.

## Grid and adaptation rule

All grids use radii `{0,1,ceil(log2(n))}`, exact and lazy mutation, and paired
archive/alignment observations. Configurations are traversed round-robin within
each repetition. Each completed trajectory is atomically checkpointed before
the next begins. The earlier total/per-trial deadline is enforced inside the
simulator. Manifests preserve commands, seeds, dependency versions, Git state,
the dirty source snapshot and its SHA-256 hashes, timing, and censoring.

1. Smoke: `n={8,16,32}`, 3 repetitions, seed base `2611021000`, 54 trajectories;
   2,000,000 evaluation cap, 10 s trial cap, 300 s total cap. Smoke establishes
   timing, absence of censoring, source/checkpoint completeness, and invariants;
   its outcomes are excluded from the main inferential table.
2. Bounded main: `n={32,64,128,256}`, 24 repetitions, seed base `2611022000`,
   576 trajectories; 20,000,000 evaluation cap, 60 s trial cap, 5,400 s total cap.
   Start only after smoke is uncensored and passes invariants and evaluator
   approval. Reduce the largest n before launch only if conservative smoke
   extrapolation predicts exceeding the budget; record any such deviation.
3. One optional larger-n validation: `n=512`, 24 repetitions, seed base
   `2611023000`, 144 trajectories; 80,000,000 evaluation cap, 180 s trial cap,
   at most 4,500 s total. Run only if main is uncensored, all safeguards pass,
   and twice the n² timing extrapolation from main n=256, plus observed checkpoint
   overhead and the 45-minute verification
   reserve fits the cutoff. It is an adaptive finite-size validation, not a
   held-out test of an asymptotic law. No standard-bit mutation is planned.

Each command includes `--not-after-utc 2026-11-03T01:42:58Z`. Stop earlier after
three materially distinct failed approaches without new information or an
unresolved human research choice. Do not increase a censored configuration.

## Analysis and decision rule (fixed before smoke)

Primary costs are **raw evaluation counts**. No global factor-two correction is
assumed for lazy mutation. Radius zero is a contextual mutation-rate control.
For each uncensored cell report the full observations, mean, standard deviation,
median, quartiles, 90th and 95th percentiles, extrema, and paired endpoint gaps.
For every cell report censoring counts and observation limits.

Let `R_(m,e)(n)=mean(T_(n,r=1,m,e))/mean(T_(n,r=ceil(log2(n)),m,e))`
and `D_(m,e)=log(R_(m,e))`. Primary contrasts are:

- Mutation attenuation `M_e=D_(exact,e)-D_(lazy,e)` for each endpoint.
- Stopping attenuation `S_m=D_(m,alignment)-D_(m,archive)` for each mutation.
- Interaction `I=M_alignment-M_archive=S_exact-S_lazy`.
- Average attenuations `M=(M_archive+M_alignment)/2`,
  `S=(S_exact+S_lazy)/2`, and dominance `M-abs(S)` / `S-abs(M)`.

Use 10,000 percentile-bootstrap draws with analysis seed `2611029000`, resampling
whole trajectory records independently within `(n,r,mutation)` cells and retaining
both paired endpoints. Report pointwise 95% intervals, explicitly not simultaneous
familywise guarantees. If any requisite endpoint is censored, the unconditional
mean contrast is inconclusive; do not drop censored records or rank mechanisms
from successful trials alone. No post-hoc distributional imputation is planned.

The largest main n is primary; smaller n and optional n=512 show finite-size
consistency or reversals. A same-weight mechanism is favored when both `M_e`
intervals are positive and the interval for `M-abs(S)` is positive. A stopping
mechanism is favored when both `S_m` intervals are positive and `S-abs(M)` is
positive. If both contribute without a clear dominance, report both; if intervals,
censoring, or size reversals prevent a ranking, report an ambiguous result.
Regardless of the ranking, record negative results and the magnitude of the
paired archive/alignment gap. Self-loop recipient changes and target acquisitions
are descriptive mechanistic evidence, not independent causal estimands.

No noisy proof, tail theorem, lower-bound transfer, or asymptotic conclusion is
part of this study.
