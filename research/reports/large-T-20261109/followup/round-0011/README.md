# Round 11: real-p Schur elimination

**Candidate proof:** the complete double-error block of a closed T=2 pair
can be eliminated with polynomial acceptance-weighted entry, residence and
exit bounds. The proof handles within-sweep repair and reinfection, retains
the omitted time, and extends the one-pair elimination to the full pinned
chain while retaining other-coordinate evolution. Independent audit is still
needed. A full-population Taylor remainder is not established.

For 0<=p<1/6, the single-error entry reward is at most 4p/(1-6p).
At n=33,p=n^-4 this bound is about 0.000003373, even though the replayed
round-10 absolute-series obstruction at the same parameters exceeds 1,314.
The new bound is an analytic candidate bound, not a measured runtime.

**Mechanically checked examples**, exact rational calculations in sweeps:

| n | Pair targets | p | Maximum entry-weighted double-error residence | Bound |
|---:|---|---|---:|---:|
| 3 | {2,3} | 1/81 | 0.007465593 | 0.053333333 |
| 5 | {4,5} | 1/625 | 0.001755076 | 0.006462036 |
| 5 | {2,3} | 1/12 | 0.039783925 | 0.666666667 |

**Contradicted strengthening:** entry weighting does not make all higher
residence moments polynomial. An explicit positive contribution to
P_SD'(0) R_D(0)^2 1 is at least n^(n-4)/32. At n=33 the sharper exact path
lower bound is 1.0465002071e43. This preserves a concrete obstacle for
derivative-based continuations; it does not refute a signed remainder bound.

| Artifact | Purpose |
|---|---|
| [proof.md](proof.md) | Complete candidate argument, model, limitations and falsifiers |
| [check.py](check.py) | Independent standard-library exact checker |
| [test_check.py](test_check.py) | Thirteen focused regression/falsification tests |
| [inequalities.csv](inequalities.csv) | All-state phase/sweep bounds at n=3,5,7,9 |
| [schur.csv](schur.csv) | Nine exact Schur/direct solves with rational values |
| [moments.csv](moments.csv) | Higher-residence obstruction witnesses |
| [bounds.csv](bounds.csv) | Analytic bounds on the n^-4 scale |
| [verification.json](verification.json) | Finite check counts and scope |
| [dependency.json](dependency.json) | Recursive evidence audit and unchanged measurements |
| [reproduce.py](reproduce.py) | Serial regeneration and byte comparison |
| [checks.json](checks.json) | Tests, timing and preservation receipt |
| [provenance.json](provenance.json) | Source revision, commands, hashes and resource use |
| [memory.md](memory.md) | Durable claim/status supplement |

From the repository root, with its configured NumPy/Matplotlib Python:

~~~sh
PYTHONDONTWRITEBYTECODE=1 python -S deliverables/test_check.py
PYTHONDONTWRITEBYTECODE=1 OPENBLAS_NUM_THREADS=1 python deliverables/reproduce.py --repo . --out /tmp/round11-replay
PYTHONDONTWRITEBYTECODE=1 OPENBLAS_NUM_THREADS=1 python -m unittest discover -s tests -v
PYTHONPYCACHEPREFIX=/tmp/round11-cache python -m py_compile sim.py large.py scripts/run_research.py deliverables/check.py deliverables/test_check.py deliverables/reproduce.py
~~~

Use a fresh replay directory. After publication replace the script directory
with research/reports/large-T-20261109/followup/round-0011. The new checker
itself needs only the Python standard library. Full replay also invokes prior
deterministic analyses and receipt verification, never a scientific sampler.
Six generated outputs are compared byte for byte. Timing receipts vary by
invocation. Raw logs and scratch calculations are kept outside this bundle.

**Published empirical results, unchanged:** n=256,T=1/T=16 gives
2.327639 [2.050148,2.674642], 24 complete trials per arm; separately
registered n=512,T=1/T=23 gives 2.339095 [2.085387,2.596468], 32 per arm.
Intervals are the earlier approximate nominal 95% independent-bootstrap
intervals. Their distributions, phase denominators and source receipts are
retained by the dependency replay. The original campaign still has its capped
main trial and 240 missing, gate-blocked holdout rows. The original two-stage
decision remains inconclusive.

**Execution scope:** deterministic algebra and tests, one CPU, zero new
scientific trajectories/seeds, no network, paid resources, commit or push.
No prior registration, receipt, gate, source PDF or simulator is modified.
The original prior-round-plan requirement is respected by doing no new
sampling experiment.
