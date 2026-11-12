# Round 19: RORR with regular and orphan entrances

**Candidate proof:** in the supplied pinned T=2 model, for even n>=4,
\[
|\mathrm{RORR}|\le1024(n+1)^3(20n)^4/q<4\cdot10^9n^8,
\quad q=1-(1-d(2,0))(1-d(1,0)).
\]
Units are sweeps. [proof.md](proof.md) gives the complete assembly and the
specific steps needing independent analytic review. The audited round-18
marked two-R lemma is retained as a premise and verified through the
published dependency replay. This result does not certify the full fourth
coefficient, its sign, or a uniform higher-order remainder.

The first regular overwrite retains a=d(x,k); the orphan insertion retains
d_y=d(y,n) inside c_y=d(n,y)d_y. A baseline flux beta is bounded using d_y
before the marked estimate's 1/a is canceled. Deleting the baseline before
O is invalid: its contribution to the word is beta times the first regular
response. The exact implementation tests that identity separately.

**Mechanically checked artifacts:** finite rational results and their scope
are recorded below. The grid is designed in this round for mathematical
verification, not a preregistered stochastic experiment. There are no new
scientific trajectories or seeds, no sampling intervals, and no censoring
of these exact calculations. Finite coverage does not prove the all-n bound.

| Artifact | Purpose |
|---|---|
| [proof.md](proof.md) | Model, candidate bound, baseline correction, scope and falsifiers |
| [rorr.py](rorr.py) | New ordered sweep/suffix solver and exact finite checks |
| [test_rorr.py](test_rorr.py) | Literal-mask, shared-observation, boundary and entrance regressions |
| [words.csv](words.csv) | Exact RORR fingerprints, decimals and bound comparisons |
| [entrance.csv](entrance.csv) | Actual orphan entrance factors and baseline responses |
| [joint.csv](joint.csv) | Both entrance factors on the same absolute continuation envelope |
| [responses.csv](responses.csv) | Marked regular continuations at every phase |
| [branches.csv](branches.csv) | Separate positive active and clean absolute expectations |
| [shortcuts.csv](shortcuts.csv) | Nonzero baseline contribution and incorrect value if it is omitted |
| [verification.json](verification.json) | Exact finite scope and check counts |
| [dependency.json](dependency.json) | Replayed premises, registrations, receipts and seed separation |
| [reproduce.py](reproduce.py) | Serial reproduction with a hard deadline |
| [checks.json](checks.json), [provenance.json](provenance.json) | Verification, preservation, source hashes and timing |
| [memory.md](memory.md) | Durable claim/status supplement and cumulative progress |

The word solver imports no previous solver for its answers. It composes
unrestricted clean and signed recipient updates through each sweep, solves
boundary equations in clean-error deletion order, and recovers interior
phases by suffix products. It compares its exact values with the published
round-14 direct phase solver after verifying that source's manifest. A
separate custom-reward recurrence checks the orphan-turn and baseline
decomposition. Literal bit masks and max-Chebyshev comparisons test both
implementations' transition assumptions. This is one agent's candidate
argument and two numerical implementations, not a claim of a second agent's
independent analytic review.

The new grid includes every target k<n, child x in {0,...,n}, orphan y,
and phase at n=4,6, from both C and the aligned population. Cases with a
correct child or an unchanged marked weight are deliberately retained.
Clean descendants remain within this family. This is not an enumeration
of every population. Acceptance in responses.csv refers to the remembered
first regular factor, even after repair. The y=n entrance row has zero
positive orphan-birth weight and the killed boundary baseline value zero;
the actual negative unchanged O coefficient is minus the sum over y<n.
In joint.csv, `joint_weight` is a*d(n,y)*d(y,n); the first regular mutation
row is summed later, as in the proof, and is not included in that column.

Reproduce from the repository root using its configured Python (on this
host, `/Users/parth/miniforge3/bin/python`):

```sh
PYTHONDONTWRITEBYTECODE=1 OPENBLAS_NUM_THREADS=1 python deliverables/test_rorr.py
PYTHONDONTWRITEBYTECODE=1 OPENBLAS_NUM_THREADS=1 python deliverables/reproduce.py --repo . --out research/runs/round19/replay-new --seconds 11000
PYTHONDONTWRITEBYTECODE=1 OPENBLAS_NUM_THREADS=1 python -m unittest discover -s tests -v
PYTHONPYCACHEPREFIX=/tmp/round19-cache python -m py_compile sim.py large.py scripts/run_research.py deliverables/rorr.py deliverables/test_rorr.py deliverables/reproduce.py
```

Choose a fresh private replay destination. After publication, replace
`deliverables` in commands with `research/reports/large-T-20261109/followup/round-0019`.
The new code needs only the Python standard library. The recursive empirical
analysis replay also needs the repository's NumPy/Matplotlib environment.
Every heavy stage is serial, with one numerical thread. Logs, full execution
receipts and temporary caches stay outside the publication bundle.

`--verified-prior PATH` may reuse a completed full round-18 replay. This
option checks that replay's success receipt and all eight output bytes,
plus the published artifact manifest, before proceeding. It cannot accept
an incomplete replay or a directory containing only copied data. The
recorded run uses this option after completing the full dependency replay
earlier in the same turn; it does not represent a second execution of that
dependency stage. Scalar fingerprints hash `str(Fraction)`, not rounded
decimals. All result decisions use exact equality or rational inequalities.

**Empirical context, unchanged:** the original n=256 ratio remains
2.327639 [2.050148, 2.674642], with 24 complete observations per arm. The
separately registered n=512 restricted-mean ratio remains
2.339095 [2.085387, 2.596468], with 32 per arm and no censored or missing main
follow-up observations. These retain their approximate nominal 95%
bootstrap interpretation. At n=512 the cost q10/median/q90 values are
4.507/5.043/5.903 million evaluations at T=1 and
1.592/2.183/2.586 million at T=23. All phase denominators and original
campaign counts remain in dependency.json. These experiments concern
ordinary initialization, not the supplied-state Taylor word.

The original preregistration, capped high-noise main trial, 240 missing
gate-blocked holdout trials and inconclusive original two-stage decision
are preserved. The independent n=512 study does not unblock or replace that
holdout. Earlier private execution logs remain unavailable; chronology is
verified only as far as published receipts permit. No new stochastic measurement,
network use, paid resource, source-PDF edit, commit or push is part of this
checkpoint. The work makes no current-literature novelty claim.

## Recorded finite results

**Mechanically checked:** independent sweep and phase solvers agree exactly.
The values below are rounded exact rationals in sweep units, not sampled means.

| n | RORR | Incorrect result after baseline omission |
|---:|---:|---:|
| 4 | 0.158278329276 | -1.803253923193 |
| 6 | 0.270057708937 | -3.515361728199 |

The new verification passes 2,567 exact identities and 7,814 inequalities,
including 664 envelopes retaining both entrance factors. It includes
864 exact phase-oracle comparisons. The additional custom-reward
recurrence verifies the missing baseline contribution in each row. These
checks support the stated finite identities; the all-n bound remains a
candidate proof awaiting independent analytic audit.
