# Proposed next experiment: standard-bit same-weight broadcast

Prepared 2026-11-03. **PROPOSED — not preregistered, implemented, or launched.**
This document authorizes no computation or spend. It records the next bounded
question after the completed [lazy broadcast ablation](reports/20261103T022831Z-broadcast-ablation.md).

## Question and reason to prioritize it

**Empirically supported:** at lazy q=1/2, suppressing same-weight neighbor
broadcast increased r=1 mean evaluations by about 43% at n=256 and 22% at n=512,
and increased the r=1 versus logarithmic-radius contrast. The previous study
supports finite broadcast contribution; exclusive mediation remains open (C15).

**Open next question:** does that beneficial broadcast-policy effect persist
under the primary paper's standard-bit mutation, which permits both multi-bit
jumps and state-dependent same-weight probabilities? A two-arm ON/OFF study
isolates broadcast within that operator. It is more informative than adding
sizes to the completed lazy study or introducing a broad operator factorial.

## Process and exact intervention

Keep canonical `C_j(w)=max{j(n-w),(n-j)w}`, n+1 independent uniform initial
strings, ascending cyclic own-parent breeders, clipped radius, non-worsening
ties and sequential replacement. Count n+1 initialization evaluations and every
offspring. Archive every initial/generated weight, including rejected offspring;
observe its first completion after each offspring, while continuing the same
passive-archive trajectory to alignment for secondary measurements.

**Proved mathematical kernel, implementation still required:** standard-bit
mutation flips each bit independently with probability p=1/n. Given parent
weight w, draw independent `X~Bin(w,p)`, `Y~Bin(n-w,p)`, then `w'=w-X+Y`.
Canonical selection and future mutation depend only on weight, so this remains
an exact weight-state description. The ON arm broadcasts every offspring.
The OFF arm suppresses only recipient replacements j≠breeder when **X=Y**,
retaining the breeder comparison, evaluation, archive processing, cyclic
advancement and every moving-offspring offer. Suppress both no-flip X=Y=0 and
balanced-flip X=Y>0 offspring; suppressing only zero flips would test a different
question. Separate these two categories in passive diagnostic counters.

The two arms have the same mutation law, but after states diverge their
realized hold probabilities and trajectories may differ. This is part of the
policy effect, not a reason to force common offspring values.

## Coupling and tests required before a grid

Within each (n,r,repetition) block, use identical initialization and two
independent uniform streams indexed by absolute offspring attempt: one for X,
one for Y. Map each mark through the inverse CDF of the appropriate binomial
at that arm's current w. Consume exactly two marks even at boundary weights or
on holds, using separate identically seeded generator instances across arms.
Blocks are independent across n, r and repetition. Identically seeding native
binomial calls is insufficient to assert this coupling: implementations may
consume state-dependent amounts of randomness.

**Required mechanical checks, not yet performed:** compare the full weight
kernel with small-n enumeration of all bit-flip masks for every parent weight;
check support, normalization, complement symmetry, mean `w+(n-2w)/n`, variance
`1-1/n`, degenerate boundaries and numerical CDF tails/thresholds. Do not deliberately
truncate support or silently renormalize the kernel. Document numerical error
and precision handling, including underflow of tiny probabilities and the finite
resolution of random marks. Freeze the numerical inverse-CDF construction and
tolerances before data collection.

Add deterministic zero-flip and balanced-flip X=Y>0 fixtures: ON can update a
neighbor, OFF cannot, while self-comparison and archive/evaluation counts remain.
Check r=0 paired path identity, moving-offspring identity, fixed mark consumption,
passive observer identity, old lazy defaults, and late-hit confirmed-prefix
censoring. Existing paired runner/analyzer assumptions must be reviewed for the
new operator and the event-specific eligibility below; prior approval is not
implementation approval for standard-bit mutation.

## Proposed bounded grid and gates

| Stage | n | Radii | Independent blocks per (n,r) | Trajectories |
|---|---|---|---:|---:|
| Smoke | 8, 32 | 0, 1, ceil(log2 n) | 3 | 36 |
| Primary | 256 | 1, 8 | 48 | 192 |
| Timing-gated validation | 512 | 1, 9 | 24 | 96 |

There are two arms per block: at most 324 trajectories in 162 independent
blocks; primary/validation inference excludes the 36 smoke trajectories.
Two stopping observations do not multiply the sample count. Large r=0 cells
are omitted because smoke already tests the pathwise identity control.

Propose a two-hour elapsed ceiling with the final 30 minutes reserved for
independent recomputation, full tests/compilation and reporting. Standard-bit
implementation cost and OFF runtime are unmeasured; previous lazy timings are
not a guarantee. Before any run, preregister exact seed ranges, mark/CDF policy,
operation/per-trial/total caps, absolute cutoff, bootstrap draws/seed and a
numerical conservative timing gate. Main requires implementation approval and
smoke integrity/censoring/timing checks. Validation eligibility uses timing,
censoring and integrity only, before inspecting mechanism contrasts, and may
conservatively require both endpoints uncensored. No outcome-driven enlargement.

Use `scripts/run_research.py` with explicit planned blocks, alternating arm order
by repetition parity within each (n,r), and a checkpoint after every arm.
Preserve missing/unstarted blocks, censored arms, confirmed observation prefixes,
commands, exact dirty snapshots, dependency versions and seeds. Full source
freeze applies during execution. These are proposed safeguards, not a launch.

## Primary estimands and decision

**Prospective change:** make archive coverage primary to match the paper's
runtime event; alignment and target-hit phases are paired secondary observations.
This choice is explicit before standard-bit outcomes and does not relabel the
previous alignment-primary study.

For archive evaluations define
`A_r=log(mean(T_OFF,r)/mean(T_ON,r))` and
`Delta=A_1-A_log=D_OFF-D_ON`, with
`D_arm=log(mean(T_arm,1)/mean(T_arm,ceil(log2 n)))`.
Resample whole planned ON/OFF block records, carrying both endpoint observations
and censor flags, within radius and independently across radii. Propose two 97.5% two-sided percentile intervals for archive A1
and Delta: approximate nominal Bonferroni 95% family per n, with validation a
separate family. Alignment/phase intervals are pointwise 95% descriptive.
Bootstrap coverage is approximate; freeze all details in the later preregistration.

Primary archive inference requires every planned archive time observed, even
if some later alignment times censor. Keep those earlier archive successes and
every planned arm/block; do not discard them as incomplete trajectories.
Alignment inference requires its own full-observation gate. Any required
missing/censored archive observation makes unconditional primary mean contrasts
inconclusive; no complete-case deletion or substitution of executed late counts.

Require positive lower intervals for **both A1 and Delta** to support useful
r=1 broadcast contributing to finite radius attenuation. Delta alone can arise
from larger-radius harm. Report uniform benefit without a resolved interaction,
large-radius harm, negative effects and ambiguous/censored evidence separately;
nonsignificance is not zero or equivalence. Report distributions, paired
differences and censoring, not only means. Retain confirmed F_j, endpoint H,
interior completion and alignment−H without additional RNG draws. Never presume
the lazy study's sampled archive/alignment equality transfers to this operator.

## Interpretation and source boundary

A positive result would support finite transport of the broadcast contribution
to standard-bit mutation. A negative or unresolved result would expose limits
of the lazy proxy or precision, not contradict the paper's asymptotic theorem.
Do not estimate a cross-operator interaction or compare effect sizes inferentially
using the old lazy data; such a comparison would require its own design.
No natural-mediation fraction, exclusive explanation, asymptotic law, or global
time-change factor follows. Zero-flip/balanced-flip counters and passive phase correlations are descriptive,
not estimates of separate causal mechanisms.

Primary source: Doerr, Elmoutassim, Krejca and Kibulu (2026), *Understanding the
Co-evolutionary Solution Exchange of the MOEA/D: Already the Smallest
Communication Radius Gives the Best-Possible Speed-Up*,
[arXiv:2610.35373v1](https://arxiv.org/html/2610.35373v1), §3 Algorithm 1 and
§4 Theorems 1–2. ON uses the paper's standard-bit operator and canonical
communication; OFF changes its replacement rule, so the theorem is not
transferred to OFF. Preserve the source min/max and lower-class caveats in
[PAPER_COMPARISON.md](PAPER_COMPARISON.md). C16's constant-q iid-uniform
scheduler identity does not apply to this cyclic, state-dependent-hold process.
This proposal asserts no comprehensive novelty claim.

**Reviewed proposal:** independent evaluator approval at 2026-11-03 04:03:49
UTC; independent literature/source-scope approval at 04:03:48 UTC. No blocking
design issue remains. These approvals cover the proposal only; implementation,
full preregistration and experiment launch remain future work. No code, tests,
trials, earlier preregistration/report, source PDF, or claim status is changed
by this document.
