# Round 18: independent ORRR audit

**Proved in the supplied pinned model:** the compensated centering identity
and marked-response argument validate the round-17 bound

\[
|\mathrm{ORRR}|\le2048(n+1)^3(20n)^4/q=O(n^8),\qquad
q=1-(1-d(2,0))(1-d(1,0)),\quad n\ge4\text{ even}.
\]

Time is in full-population sweeps. The [analytic audit](audit.md) explicitly
distinguishes the unrestricted clean kernel from its killed occupation
kernel. It retains the boundary compensation, all signed branches, the
three-overwrite support budget, the accepted mark and the actual wrong-orphan
entrance factor. Last-pair and orphan repair are allowed to be dependent.

**Mechanically checked:** the new raw, uncentered solver reproduces both
published ORRR exact fingerprints, at n=4 and n=6. The n=6 comparison adds the
independent fourth-order oracle missing from round 17. Exact finite-check
counts are in [verification.json](verification.json); finite checks do not
establish the all-n result. No new experimental trajectories were generated.

The new grid checks 4,956 response cases and 31,052 phase cases, with
75,006 exact identities, 98,896 response inequalities and 17,280 additional
scalar acceptance inequalities. Abstract support checks cover 13,771
patterns and 134,517 clean/overwrite edges through n=32. All 622 published
centered fingerprints agree; separate comparisons also match four published
flux fractions and all 24 orphan-entrance response records. These counts
describe deterministic checks, not independent statistical observations.

At n=4 the degree-zero and degree-one checks exhaust every population with
surviving-overwrite budget at most two. At n=6 they cover every wrong-value
pair in the stated corner/subset families and every orphan value. The
marked degree-two checks include every slot, child value, orphan value and
phase at both n=4 and n=6. The finite grid is not an all-population check at n=6.

In `responses.csv`, `acceptance` is the remembered factor only on marked
rows; the value 1 elsewhere is a neutral placeholder. In `entrance.csv`,
`entrance_exact` records positive wrong-orphan births. The y=n row stores
the unchanged reference response and has zero positive-birth weight; its
negative O coefficient is minus the sum of the wrong-orphan birth weights,
as retained explicitly in the solver and proof.

| n | ORRR, rounded | Check |
|---:|---:|---|
| 4 | 0.3049490187292804 | Independent raw response matches published rational fingerprint |
| 6 | 0.3979640378737074 | Independent raw response matches published rational fingerprint |

**Contradicted shortcut:** omitting the boundary compensation leaves the
nonzero exact residuals in [flux.csv](flux.csv). The positive higher-residence
counterexamples from earlier rounds remain valid. The full fourth-order gap
remains conjectured polynomial; no uniform remainder or enlarged noise window
follows. No ordinary-initialization theorem is inferred.

| File | Purpose |
|---|---|
| [audit.md](audit.md) | Complete model, analytic audit, scope and falsifiers |
| [audit.py](audit.py) | Independent exact uncentered response and support audit |
| [test_audit.py](test_audit.py) | Literal masks, shared acceptance, killing, compensation and coefficient regressions |
| [responses.csv](responses.csv) | State/phase identities, fingerprints and centered bound ratios |
| [flux.csv](flux.csv) | Exact compensations and failed uncompensated residuals |
| [words.csv](words.csv) | Exact ORRR fingerprints and polynomial bounds |
| [entrance.csv](entrance.csv) | Actual orphan entrance factors and raw responses |
| [budget.csv](budget.csv) | Exhaustive finite abstract overwrite-support checks |
| [inequalities.csv](inequalities.csv) | Acceptance-weighted exact inequalities |
| [verification.json](verification.json) | Finite scope and exact check counts |
| [dependency.json](dependency.json) | Earlier publication, plans, receipts and seed audit |
| [reproduce.py](reproduce.py) | Serial dependency and new-output replay with a hard deadline |
| [checks.json](checks.json), [provenance.json](provenance.json) | Tests, preservation, commands, timing and source hashes |
| [memory.md](memory.md) | Durable C42/C43 update and cumulative checkpoint |

From the repository root, using the configured Python (the recorded host
uses `/Users/parth/miniforge3/bin/python`):

```sh
PYTHONDONTWRITEBYTECODE=1 OPENBLAS_NUM_THREADS=1 python deliverables/test_audit.py
PYTHONDONTWRITEBYTECODE=1 OPENBLAS_NUM_THREADS=1 python deliverables/reproduce.py --repo . --out research/runs/round18/replay-new --seconds 7200
PYTHONDONTWRITEBYTECODE=1 OPENBLAS_NUM_THREADS=1 python -m unittest discover -s tests -v
PYTHONPYCACHEPREFIX=/tmp/round18-cache python -m py_compile sim.py large.py scripts/run_research.py deliverables/audit.py deliverables/test_audit.py deliverables/reproduce.py
```

Use a fresh replay destination. After publication, replace `deliverables`
with `research/reports/large-T-20261109/followup/round-0018`. The new solver
uses only the Python standard library; the inherited empirical replay also
needs the repository's NumPy and Matplotlib environment. Every stage runs
serially with one numerical thread. The deadline terminates the subprocess
group. Logs and execution receipts remain in the selected private run
directory. Eight generated outputs are compared byte for byte. Scalar hashes
use `str(Fraction)` and centered-vector hashes use `str(tuple_of_Fraction)`;
decimals never decide equality.

**Empirical context, unchanged:** the earlier n=256 ratio remains
2.327639 [2.050148, 2.674642], with 24 complete observations per arm. The
separately registered n=512 restricted-mean ratio remains
2.339095 [2.085387, 2.596468], with 32 per arm. These retain their approximate
nominal 95% bootstrap interpretation. The latter cost q10/median/q90 values
are 4.507/5.043/5.903 million evaluations for T=1 and 1.592/2.183/2.586
million for T=23. Full phase denominators are in [dependency.json](dependency.json).

Usable prior plans and receipts replayed; no repair was needed. Earlier
private trial logs are unavailable, limiting chronology to published
evidence. The original preregistration, capped main trial, 240 missing
gate-blocked holdout trials and inconclusive original two-stage decision
remain unchanged. There was no new scientific sampling, seed generation,
network use, paid resource, source-PDF edit, commit or push.
