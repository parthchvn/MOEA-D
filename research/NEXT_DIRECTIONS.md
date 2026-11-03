# Next research directions after the controlled radius study

Prepared 2026-11-02 from independent evaluator/literature reviews.
**The original sections below are proposals, not a preregistration or standing
authorization to launch experiments.** The execution update distinguishes the
later authorized study. Future runs need their own bounded goal and protocol.

## Execution update, 2026-11-03

The sections below preserve the independently reviewed original proposal.
A later user request authorized **two lazy ON/OFF arms only**, omitting its fresh
exact arm before outcomes. The new frozen `BROADCAST_PREREG.md` governs that
completed study, not the historical grid below. All 324 trajectories in 162 seed
blocks completed uncensored; inference uses 288 trajectories/144 blocks.
**Empirically supported:** useful r=1 broadcast and a positive radius interaction
at primary n=256 and validation n=512, with both preregistered primary intervals
positive. This supports finite broadcast contribution, not exclusive mediation
of the earlier mutation change. Passive observations find last endpoint target
hits determine all sampled completion times; known counterexamples remain.
See [the ablation report](reports/20261103T022831Z-broadcast-ablation.md).

Priority 1 below has therefore been executed in its authorized two-arm form;
the proposed three-arm decomposition has not. The next bounded proposal is the
standard-bit bridge detailed in [STANDARD_BIT_PROPOSAL.md](STANDARD_BIT_PROPOSAL.md):
two standard-bit ON/OFF arms, archive-primary, with explicit paired-kernel
validation and bounded gates. It is proposed only, not preregistered or launched.
The conditional dose/scheduler or finite-state questions below remain later
options; no further study is authorized.

## Evidence and priority

**Empirically supported:** the exact-to-lazy change better explained tested
radius sensitivity at n=256/512 than the stopping event. Lazy raw runtimes were
slower; smaller-n contrasts were inconclusive. Zero sampled positive-radius
gaps do not imply equality: C14 gives a positive-probability counterexample.
See [the completed report](reports/20261102T212758Z-radius-factorial.md).

**Conjectured:** direct same-weight neighbor broadcast mediates attenuation.
The previous intervention also changed moving frequency and cyclic timing.
Isolate broadcast before increasing n or fitting another runtime law.

| Priority | Bounded question | Limitation |
|---|---|---|
| 1 | Broadcast ablation, with passive phase diagnostics. | Interventional contrast, not identification of natural mediation. |
| 2 | Standard-bit mutation bridge to the paper. | Multi-bit jumps and self-loop probabilities change together. |
| 3 | Small self-loop probability study. | Fixed q does not settle a threshold for q(n). |
| Conditional | Uniform scheduler, small-state analysis, focused proof obligation. | Finite chains/grids do not establish asymptotics. |

Do not combine these into one large factorial. Negative or ambiguous ablation
results should redirect the next question, not automatically increase sampling.

## First proposed study: broadcast ablation

Use three fresh arms with identical canonical scalarization, initialization,
cyclic own-parent breeders, clipped radius and tie acceptance:

1. Exact one-bit, normal communication.
2. Lazy q=1/2, normal communication (ON).
3. Lazy q=1/2, suppressing only recipient updates j≠breeder when offspring
   weight equals parent weight (OFF).

OFF retains offspring evaluation, archive insertion, breeder self-comparison,
and every moving-offspring broadcast. It does not delete the cyclic visit.
**Proved controls:** r=0 and q=0 give ON/OFF pathwise identity under a shared
tape. OFF self-loop recipient changes/target acquisitions must be zero. These
are planned regression checks, not new experiments. OFF need not equal exact
or globally doubled exact runtime. OFF changes Algorithm 1's communication;
type-A mutation qualification alone does not transfer its bound to OFF.

### Provisional grid and budget

| Stage | n | Radii | Arms | Independent blocks per (n,r) | Trajectories |
|---|---|---|---:|---:|---:|
| Smoke | 8, 32 | 0, 1, ceil(log2 n) | 3 | 3 | 54 |
| Primary | 256 | 1, 8 | 3 | 48 | 288 |
| Timing-gated validation | 512 | 1, 9 | 3 | 24 | 144 |

Large r=0 cells are unnecessary: r=0 is principally a pathwise control and was
costly previously. The maximum is 486 trajectories in 162 independent blocks;
recording two endpoints does not double the independent sample count.

**Mechanically calculated timing proxy:** prior positive-radius exact/lazy trial
totals were 18.38/36.61 s at n=256 and 83.60/140.46 s at n=512 (24 repetitions
per radius). Substituting ON time for unmeasured OFF, adjusting repetitions,
and doubling gives about 1,095 s before overhead, roughly 19 minutes. OFF and
instrumentation costs are unmeasured; this is not a guarantee. A suggested
future ceiling is two elapsed hours, 60/180 s per trial at n=256/512, operation
caps, and a reserved analysis period. **No runtime or spend is authorized here.**

Before launch freeze disjoint seeds, exact caps, cutoff, interval/multiplicity
policy, and timing/censoring validation gates. Do not select validation because
results look favorable, scale censored cells, or add repetitions for significance.

### Coupling and runner requirements

**Mechanically checked by inspection:** the current analyzer rejects duplicate
seeds and groups only (n,r,mutation); it cannot handle the proposed block design.

- Define a block by (n,r,repetition), independent across radii/n. Each arm gets
  separate identically initialized initialization/gate/direction generators;
  never pass one shared mutable generator through arms. Exact ignores but
  consumes its gate. Couple by absolute offspring index, not accepted updates.
- Each arm retains its own stopping/censoring time. Jointly bootstrap the whole
  three-arm/two-endpoint block within a radius; radius blocks are independent.
  Add explicit arm/block identifiers and valid deliberate-pairing seed checks.
- Counterbalance arm order within round-robin blocks; checkpoint each completed
  arm. Preserve missing/censored arms and incomplete blocks. Do not use silent
  complete-case deletion for unconditional means. Censored required cells make
  those contrasts inconclusive unless another estimand was preregistered.
- Retain confirmed-prefix censoring, initialization cost, passive all-offspring
  archive, dirty-source snapshots and dependency versions. Review new semantics
  independently before the main grid; prior approval does not cover new code.

### Estimands and outcomes

Propose alignment as primary and archive as paired secondary; freeze event and
interval/multiplicity choices before launch. For either event define

`A_r = log(mean(T_OFF,r) / mean(T_ON,r))`,

`Delta = A_1 - A_log = D_OFF - D_ON`, with
`D_arm = log(mean(T_arm,1) / mean(T_arm,ceil(log2 n)))`.

Require positive predeclared lower uncertainty limits for **both A_1 and Delta**
to support useful small-radius broadcast explaining attenuation. Delta alone
could reflect broadcast harming the larger radius. Distinguish uniform benefit
(positive A at both radii without a resolved interaction), large-radius harm,
and ambiguous/censored evidence. Nonsignificance is not evidence of zero.

The fresh exact reference gives the algebraic contrast decomposition
`D_exact-D_ON = (D_OFF-D_ON)+(D_exact-D_OFF)`.
This is not natural mediation or an assumption that OFF must reproduce exact.
Report raw distributions and paired differences without global factor-two scaling.

### Passive phase diagnostics in the first study

**Open:** is the effect before endpoint discovery, during interior completion,
or both? Current records cannot recover these times. Legacy tracking uses
different streams/sweep counts and is not a substitute.

Record per-target first hit F_j (initialized hits at n+1), last endpoint hit
`H=max(F_0,F_n)`, `T_alignment-H`, and the last interior hit, with censoring.
Optional diagnostics: solved prefix/suffix, endpoint level dwell times, nearby
breeders at the current endpoint weight, and 90%/99% archive completion times
with a fixed rounding rule. Endpoint level/occupancy records connect directly
to the paper's spread/improvement argument.

Observers must consume no randomness or change selection; test seeded identity
with them enabled/disabled. Avoid full traces without a separate storage need.
Level-conditioned/copy-count analyses are descriptive and selection-biased for
causal or drift inference; they do not themselves establish a drift theorem.

## Later studies, selected by the first result

**Standard-bit bridge — proved kernel, unimplemented:** independent bit flips
with probability 1/n give `w'=w-X+Y`, independently `X~Bin(w,1/n)` and
`Y~Bin(n-w,1/n)`. The weight reduction remains exact for canonical selection.
Test small-n bit-mask enumeration, support, complement symmetry and mean
`w+(n-2w)/n`. Record X,Y: zero flips `(1-1/n)^n` are only part of same-weight
mutation; balanced changes also contribute. Use independent operator seeds
unless a valid coupling is preregistered. sim.py's absolute-distance selection
is not an oracle. This bridge changes jumps and self-loop probabilities together.

**Dose response — conjectured finite tradeoff:** later consider a small grid
such as q in {0,1/8,1/4,1/2,3/4}, preferably ON/OFF within q, at one n first.
The kernel is q, `(1-q)(n-w)/n`, `(1-q)w/n` for hold/up/down. Helper, manifest
and row schema currently hardcode 1/2 and must change together; call the new
parameter self_loop_probability, not the noisy model's p. q=0/1 are boundary
tests; q=1 generally cannot complete. Fixed q in (0,1), independent of n, has
type-A alpha=q and C_A=1-q under original communication. This gives no uniform
claim as q approaches 0/1, no optimal q(n), and no paper-bound transfer to OFF.

## Proved alternate-process time-change control (C16)

This is a **proposed, unimplemented uniform-scheduler process**, not the cyclic
model. Fix n≥1, r and constant q in [0,1). Independently each evaluation draws
an iid uniform breeder, a moving gate with probability 1-q, and an independent
U[0,1] direction mark compared with (n-w)/n at the current parent weight w.
Use own-parent mutation, canonical noiseless selection, passive all-generated
archive, and OFF communication on holds. Independent initialization costs n+1.

State is the full weight vector plus archive mask. The filtration reveals
initialization and executed marks, not future marks. A hold leaves this state
unchanged: the incumbent was already archived, and self-comparison changes
nothing. Deleting holds gives the exact uniform-breeder chain, equivalently
`P_q=q I+(1-q)P_exact` on the augmented state.

For either true uncensored stopping event let K count active one-bit mutation
attempts through its hit, including rejected offspring, not just accepted changes.
Waiting lengths are iid Geom(1-q) on {1,2,...}, independent of initialization
and retained marks, hence of K. Conditional on K the offspring count is their
sum, with mean K/(1-q). K=0 handles initial completion; Tonelli permits extended
infinite expectations. Therefore

`E[T_OFF-(n+1)] = E[T_exact-(n+1)]/(1-q)`.

Both reviewers checked the argument. It is a distributional coupling, not an
identity for arbitrary common per-evaluation seeds, wall-censored means, ON,
adaptive q, noise, random permutations per sweep, or cyclic scheduling. A cyclic
hold advances breeder phase; deleting holds changes active breeder order.
No global factor-two correction or new asymptotic result for current runs follows.

## Small-state analysis and proof obligations

**Open finite question:** quantify gap probabilities/sizes, rather than only
find more witnesses. Cyclic state must include population, archive bitset and
next breeder. Naive size is `(n+1)^(n+1)*2^(n+1)*(n+1)`; start n≤3, then n=4
only if reachable-state counts and timing permit. Include binomial initialization
and its n+1 cost. Rational finite chains can mechanically establish finite
hitting probabilities/expectations, not general-n asymptotics.

For a fixed cell with 0 gaps in 24 independent trials, the one-sided exact-binomial
95% gap-probability upper bound is `1-0.05^(1/24)≈11.7%`: not zero, not a bound
on expected gap size, and not simultaneous across cells. Preserve C5's failed
invariant and C10's pathwise counterexample. Any later drift proof must state
process, filtration, conditioning, potential and stopping time. Noise remains
its own unresolved stored-fitness project.

## Source boundaries

Doerr et al. (2026), [arXiv:2610.35373v1](https://arxiv.org/html/2610.35373v1),
is direct. Its proof predicts partial-progress radius benefits; it reports no
experiments. Section 4's `ell_k=min{ceil(sqrt(n*r/k)),k}` balance motivates an
`O(n²/sqrt r)` early term plus `O(n²)` late term for fixed positive type-A
constants, not a numbered partial-progress theorem or a finite fitted law.
Keep the min/max and type-B caveats in [PAPER_COMPARISON](PAPER_COMPARISON.md).

[LITERATURE.md](LITERATURE.md) records exact boundaries of alternative projects:
[weighted-sum AAAI 2026](https://doi.org/10.1609/aaai.v40i43.41049) has a
high-probability conditioning event; [sparse decomposition (2024)](https://arxiv.org/html/2405.01014v2)
separates missing archive points; [dynamic decomposition (2026)](https://arxiv.org/html/2610.35334v1)
changes weights/population on distorted LOTZ, with an O(n⁴) expected bound and
both exact-one-bit/standard-bit operators. These do not settle fixed-decomposition
OneMinMax or establish novelty of the proposed ablation.

## Review record

The independent evaluator approved the proposed design, pairing, censoring,
estimands and C16 proof; the literature reviewer approved source assumptions
and citations. The original three-arm proposal remains unexecuted; the
authorized two-arm refinement is completed as recorded above. C16 remains
unimplemented.
