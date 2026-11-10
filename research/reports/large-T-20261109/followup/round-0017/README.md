# Round 17: ORRR and regular-state centering

**Candidate proof, pending independent analytic audit:** for even n>=4,
the supplied pinned T=2 model satisfies the proposed one-word bound

\[
|\mathrm{ORRR}|\le2048(n+1)^3(20n)^4/q=O(n^8),\qquad
q=1-(1-d(2,0))(1-d(1,0)).
\]

Time is measured in full-population sweeps. The argument centers responses
against the population with all regular slots correct and the same orphan
value, at the same phase. It retains the aligned-boundary compensation and
the wrong-orphan entrance d(n,y)d(y,n). It allows dependence between the
last pair and orphan. The isolated-pair second-response candidate is not
used. [proof.md](proof.md) gives the complete argument and falsifiers.

**Mechanically checked:** the new centered Poisson implementation reproduces
the published n=4 ORRR value, 0.3049490187292804 (rounded), exactly, and
compares with two separate published implementations. Finite checks of
the new centering and acceptance bounds cover 622 state cases and 3,734
phase cases, with 3,053 exact identities and 7,708 inequalities, as recorded in
[verification.json](verification.json). Nonzero boundary compensations
in [flux.csv](flux.csv) refute the shortcut that omits them.

| n | ORRR, rounded | Verification |
|---:|---:|---|
| 4 | 0.3049490187292804 | Two independent solver comparisons; published exact hash matches |
| 6 | 0.3979640378737074 | New exact centered calculation; no independent fourth-order oracle here |

At n=4 the first two boundary compensations are approximately 2.071469580410
and 2.835341435438. The residual in the incorrectly uncompensated equation
equals the corresponding exact compensation.

**Limits:** this is a candidate all-n bound with finite exact checks, not an
independently audited theorem. The full fourth-order gap, its uniform
remainder, fixed-positive-c ordering and ordinary initialization remain
unresolved in this checkout. No stochastic experiment was conducted.
The deterministic checks were designed in this round and are not presented
as preregistered empirical evidence.

| File | Purpose |
|---|---|
| [proof.md](proof.md) | Model, centered identity, candidate bound and falsifiers |
| [centered.py](centered.py) | Exact centered Poisson solver and finite checks |
| [test_centered.py](test_centered.py) | Literal masks, boundary correction, signed birth and independent oracle tests |
| [centered.csv](centered.csv) | State/phase check scope, exact fingerprints and bound ratios |
| [words.csv](words.csv) | Exact ORRR fingerprints, rounded values and proposed bounds |
| [flux.csv](flux.csv) | Exact nonzero aligned-boundary compensations |
| [entrance.csv](entrance.csv) | Actual wrong-orphan factors and weighted responses |
| [verification.json](verification.json) | Exact check counts and finite scope |
| [dependency.json](dependency.json) | Prior replay, registration, receipts and seed checks |
| [reproduce.py](reproduce.py) | Serial replay, hard wall deadline and byte comparisons |
| [checks.json](checks.json), [provenance.json](provenance.json) | Tests, preservation, source hashes and accounting |
| [memory.md](memory.md) | Durable C42/C43 supplement and cumulative status |

From the repository root, using the configured Python:

```sh
PYTHONDONTWRITEBYTECODE=1 OPENBLAS_NUM_THREADS=1 python deliverables/test_centered.py
PYTHONDONTWRITEBYTECODE=1 OPENBLAS_NUM_THREADS=1 python deliverables/reproduce.py --repo . --out research/runs/round17/replay-new --seconds 1800
PYTHONDONTWRITEBYTECODE=1 OPENBLAS_NUM_THREADS=1 python -m unittest discover -s tests -v
PYTHONPYCACHEPREFIX=/tmp/round17-cache python -m py_compile sim.py large.py scripts/run_research.py deliverables/centered.py deliverables/test_centered.py deliverables/reproduce.py
```

Use a fresh replay destination. After publication, replace `deliverables`
in these commands with `research/reports/large-T-20261109/followup/round-0017`.
The reproducer verifies and replays the round-16 dependency chain, then
recomputes all six generated outputs. It uses one numerical thread, runs
stages serially, kills the process group on deadline, and leaves logs and
execution receipts in the requested private output directory. Exact hashes
use canonical `str(Fraction)` strings; decimals never decide equality.

**Empirical context, unchanged:** the earlier n=256 ratio remains
2.327639 [2.050148,2.674642], with 24 complete observations per arm. The
separately registered n=512 restricted-mean ratio remains
2.339095 [2.085387,2.596468], with 32 per arm. These retain their earlier
approximate nominal 95% bootstrap interpretation. The n=512 cost
q10/median/q90 values are 4.507/5.043/5.903 million evaluations for T=1
and 1.592/2.183/2.586 million for T=23; full phase denominators remain
in [dependency.json](dependency.json).

The dependency replay found usable plans and receipts; no repair was needed.
Earlier private execution logs remain unavailable, limiting chronology to
published evidence. The original preregistration, capped main trial,
240 missing blocked holdout trials and inconclusive two-stage decision
remain unchanged. No new random trajectories, seeds, paid resources,
network use, source-PDF edits, commit or push occurred.
