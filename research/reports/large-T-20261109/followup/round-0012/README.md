# Round 12: independent phase-potential and tensor audit

**Proved within the supplied pinned model:** the real-p phase-potential
Schur bound and its exact one-block tensor extension survive independent
audit. The polynomial strengthening to higher residence moments is
contradicted by the audited explicit family. Full-population Taylor
control remains unresolved in this checkout. See [audit.md](audit.md).

| File | Role |
|---|---|
| [audit.md](audit.md) | Independent proof review, assumptions, limits and falsifiers |
| [audit.py](audit.py) | Separate exact transition, interval, pair and joint-state implementation |
| [test_audit.py](test_audit.py) | Focused regression and falsification tests |
| [phase.csv](phase.csv) | Exact Bernstein certificates on 0<=p<=1/6 for n=3,...,8 |
| [pair.csv](pair.csv) | Nine independent Schur/direct pair solves |
| [tensor.csv](tensor.csv) | Exact full-population transition comparisons |
| [moments.csv](moments.csv) | Six exact higher-residence witnesses |
| [verification.json](verification.json) | Counts, full Schur equations and shortcut counterexamples |
| [dependency.json](dependency.json) | Recursive replay, published measurements and preserved holdout |
| [reproduce.py](reproduce.py) | Serial deterministic reproduction, never a scientific sampler |
| [checks.json](checks.json) | Test, timing and preservation receipt |
| [provenance.json](provenance.json) | Source revision, commands, versions and artifact hashes |
| [memory.md](memory.md) | Durable STATUS/CLAIMS supplement |

From the repository root, use its configured Python with NumPy, Matplotlib,
and SymPy (no new packages are needed on the audited host):

```sh
PYTHONDONTWRITEBYTECODE=1 OPENBLAS_NUM_THREADS=1 python deliverables/test_audit.py
PYTHONDONTWRITEBYTECODE=1 OPENBLAS_NUM_THREADS=1 python deliverables/reproduce.py --repo . --out /tmp/round12-replay
PYTHONDONTWRITEBYTECODE=1 OPENBLAS_NUM_THREADS=1 python -m unittest discover -s tests -v
PYTHONPYCACHEPREFIX=/tmp/round12-cache python -m py_compile sim.py large.py scripts/run_research.py deliverables/audit.py deliverables/test_audit.py deliverables/reproduce.py
```

Use a fresh replay directory. After publication replace `deliverables` in
commands with `research/reports/large-T-20261109/followup/round-0012`.
The reproducer sets the standard numerical thread limits to one. It checks
all six published round-11 outputs byte for byte and recursively validates
earlier plans and receipts before running the new checker. The new six
scientific outputs are byte-compared to this bundle on subsequent replays. Execution logs and
variable timing receipts go to the requested replay directory, outside the
curated bundle. `--reuse-prior` may point to a completed round-11 replay;
the same six prior-output comparisons still apply. The main checker needs
SymPy only as an exact integer linear-system engine. It imports no earlier
transition or Schur solver. It verifies exact integer residuals of all solves.

The completed independent audit took 2,010.0 seconds on the audited host;
recursive round-11 reproduction took another 64.7 seconds. The full joint
solve dominates this cost. Four CSVs also match the completed stages of
the earlier development invocation byte for byte. The joint solve was
performed once to completion, with exact direct and Schur residual checks;
its full output was not generated a second time solely for byte comparison.

**Evidence interpretation:** deterministic exact values have no sampling
confidence intervals or censoring. Every finite inequality is labelled
mechanically checked. The general statements rely on the proof in
[audit.md](audit.md). The full tensor check includes the rest's evolution
during omitted sweeps and the actual population boundary stopping event.

**Empirically supported, unchanged:** n=256,T=1/T=16 gives
2.327639 [2.050148,2.674642] from 24 complete observations per arm;
the separately registered n=512,T=1/T=23 comparison gives
2.339095 [2.085387,2.596468] from 32 per arm. These retain their earlier
approximate nominal 95% independent-bootstrap intervals. Distributions,
phase denominators and receipts are retained in the dependency replay.
The original campaign still has one capped main trial and 240 missing,
gate-blocked holdout rows. Its original two-stage decision is inconclusive.

**Execution scope:** one CPU; zero new scientific trajectories or seeds;
no network, paid resources, commit or push. No original registration,
receipt, gate, seed, source PDF or simulator was changed. This is a
deterministic mathematical audit, not a newly sampled experiment.
