# Round 16: independent phase-aware RROO audit

**Proved under the supplied pinned assumptions:** the round-15 RROO
candidate survives independent audit, including the orphan-fed last pair:

\[
 |\mathrm{RROO}|\le5000(n+1)^2(20n)^4/q,\qquad
 q=1-(1-d(2,0))(1-d(1,0)),\quad n\ge4\text{ even}.
\]

Units are full-population sweeps. This is one ordered fourth-order response,
not the full fourth coefficient. [audit.md](audit.md) supplies the complete
proof and falsifiers. The proof retains the initial correct orphan, phase
subtraction, linear invariant law and actual accepted-birth factors. Its
last-pair argument does not assume independent completion times.

**Mechanically checked exact results, rounded for display:**

| n | RROO | Independent agreement |
|---:|---:|---|
| 4 | 2.135753903581 | Exact rational hash matches round 15 |
| 6 | 4.179111924897 | Exact rational hash matches round 15 |

The new sweep-product solver also matches all 254 published excess fractions
in the overlapping grid. It checks 408 states, 3,188 phases and 31,552
inequalities/identities, including 240 orphan-fed states. Every wrong-value
pair is checked through n=6, every orphan-fed wrong-value pair at n=8, and
endpoint stress states elsewhere through n=10. Twenty-four stationary
horizons at n=4,6,8,12 pass. These are rational calculations with no sampling
uncertainty or censoring, not a finite-grid proof of asymptotics.

**Contradicted shortcut:** at n=4, state (0,1,2,0,0), next breeder 4,
the next clean turn completes the regular slots with probability 3/64 and
repairs the orphan with probability 1/256. The intersection is zero, versus
product 3/16384. [witness.json](witness.json) records this dependence.

**Limits:** polynomiality of the full fourth gap remains conjectured in
this checkout. RRRR and thirteen other mixed words remain unresolved.
The round-15 isolated-pair second-response estimate remains a candidate
proof and is not used here. No uniform higher remainder, enlarged noise
window, fixed-positive-c ordering, or ordinary-initialization result follows.

| File | Purpose |
|---|---|
| [audit.md](audit.md) | Analytic audit, exact assumptions, proof and falsifiers |
| [audit.py](audit.py) | Independent rational sweep-product solver; no prior solver imports |
| [test_audit.py](test_audit.py) | Literal-mask, scalarization, timing, signed-branch and dependence regressions |
| [rewards.csv](rewards.csv) | Per-state reward/excess fingerprints and bound-check ratios |
| [stationary.csv](stationary.csv) | Stationary identity checks at finite horizons |
| [words.csv](words.csv) | Independent RROO coefficients and bound values |
| [witness.json](witness.json) | Exact dependence witness |
| [verification.json](verification.json) | Mechanical check counts and scope |
| [dependency.json](dependency.json) | Relevant prior replay, registration, receipts and seed separation |
| [reproduce.py](reproduce.py) | Serial reproduction, exact output comparison and wall deadline |
| [checks.json](checks.json), [provenance.json](provenance.json) | Verification, preservation, hashes and elapsed-time accounting |
| [memory.md](memory.md) | Durable C39-C41 updates and unchanged C38/C40 limits |

From the repository root, with the configured Python:

```sh
PYTHONDONTWRITEBYTECODE=1 OPENBLAS_NUM_THREADS=1 python deliverables/test_audit.py
PYTHONDONTWRITEBYTECODE=1 OPENBLAS_NUM_THREADS=1 python deliverables/reproduce.py --repo . --out research/runs/round16/replay-new --seconds 1800
PYTHONDONTWRITEBYTECODE=1 OPENBLAS_NUM_THREADS=1 python -m unittest discover -s tests -v
PYTHONPYCACHEPREFIX=/tmp/round16-cache python -m py_compile sim.py large.py scripts/run_research.py deliverables/audit.py deliverables/reproduce.py deliverables/test_audit.py
```

Use a fresh replay destination. After publication, replace `deliverables`
in commands with `research/reports/large-T-20261109/followup/round-0016`.
The reproducer enforces one numerical thread and serial execution. It first
replays round 14 and its earlier plans/receipts; it verifies round-14/15
artifact manifests and replays the four relevant round-15 excess outputs.
It then recomputes this audit and compares all six curated generated files
byte for byte. It does not rerun the unrelated full fourth-order grid or
positive-p global Schur solve. Logs stay in the requested private directory.
Exact fraction hashes use the canonical `str(Fraction)` representation;
rounded decimals are never used to test equality.

**Empirical context, unchanged:** the n=256 primary ratio remains 2.327639
[2.050148,2.674642], with 24 complete observations per arm. The separate
registered n=512 restricted-mean ratio remains 2.339095
[2.085387,2.596468], with 32 per arm. These retain the earlier approximate
nominal 95% bootstrap intervals. The latter arms' q10/median/q90 costs are
4.507/5.043/5.903 million evaluations for T=1 and 1.592/2.183/2.586 million
for T=23. Full distributions and phase denominators remain in
[dependency.json](dependency.json). Registration and receipts are usable;
no repair was needed. Private earlier trial logs remain unavailable, so
chronology is verified only from published evidence.

The original preregistration, original capped main trial, 240 missing
blocked holdout trials and inconclusive original two-stage decision remain
unchanged. No new scientific trajectories or seeds were generated. No
network, paid resources, source-PDF edits, commit or push were used.
