# Round 10: limits of an acceptance-weighted resolvent

**Candidate proof:** positive diagonal reweighting cannot make the absolute
insertion resolvent polynomial, even after summing clean excursions first.
An accessible T=2 pair of adjacent corrupted donors gives an exponential
diagonal lower bound. Its corner-row positive majorant diverges at p=n^(-4),
which is inside p=o(log(n)/n^4). This does not refute a signed/resummed
resolvent or the desired real-p remainder itself.

**Proved restricted bound from the audited orphan identity:** the orphan-only
third-and-higher remainder is at most 128p^3/q^4<=10368p^3n^4 for p<=q/4.
The full mixed/adjacent remainder and full-process sign window are unchanged.

| Artifact | Purpose |
|---|---|
| [proof.md](proof.md) | Model, candidate no-go proof, restricted positive bound, limits and falsifiers |
| [obstruction.csv](obstruction.csv) | Exact rational norm lower bounds and their values at p=n^(-4) |
| [orphan.csv](orphan.csv) | Exact discounted orphan values, quadratic coefficients, remainders and bounds |
| [verification.json](verification.json) | Finite check counts and exact accessibility/diagonal receipts |
| [check.py](check.py) | Independent deterministic checker using the standard library |
| [test_check.py](test_check.py) | Twelve regression/falsification tests |
| [dependency.json](dependency.json) | Recursive earlier replay, registration/receipt checks and coefficient matches |
| [reproduce.py](reproduce.py) | Serial regeneration and byte comparison |
| [checks.json](checks.json) | Tests, timing and preservation accounting |
| [provenance.json](provenance.json) | Source revision, commands, toolchain and hashes |
| [memory.md](memory.md) | Durable claim/status supplement |

From the repository root, choose a new scratch output directory:

```sh
PYTHONDONTWRITEBYTECODE=1 python -S deliverables/test_check.py
PYTHONDONTWRITEBYTECODE=1 python -S deliverables/check.py --out /tmp/round10-math
PYTHONDONTWRITEBYTECODE=1 OPENBLAS_NUM_THREADS=1 python deliverables/reproduce.py --repo . --out /tmp/round10-replay
PYTHONDONTWRITEBYTECODE=1 OPENBLAS_NUM_THREADS=1 python -m unittest discover -s tests -v
PYTHONPYCACHEPREFIX=/tmp/round10-cache python -m py_compile sim.py large.py scripts/run_research.py deliverables/check.py deliverables/reproduce.py deliverables/test_check.py
```

After publication replace `deliverables` with
`research/reports/large-T-20261109/followup/round-0010`. The standalone new
checker needs only the Python standard library. Earlier-round reproduction
also requires the repository's NumPy/Matplotlib environment. No sampler is
invoked. `--reuse-prior` accepts an already completed round-9 replay and still
compares its five published outputs. Four new result files are byte-compared;
execution/provenance timings are invocation-specific.

**Mechanically checked examples**, not estimates or confidence intervals:

| n | State | Signed-resolvent absolute diagonal lower bound g | g/n^4 |
|---:|---|---:|---:|
| 17 | Adjacent pair | 23,557.636 | 0.2821 |
| 32 | Orphan | 1,555,015,625.338 | 1482.9785 |
| 33 | Adjacent pair | 1,558,773,154.389 | 1314.3988 |
| 65 | Adjacent pair | 6.7369011463e18 | 3.7740421673e11 |

Values above one in the last column falsify a contraction criterion at that
p. Values below one do not establish contraction: these are lower bounds.
The n=3 adjacent-pair signed lower bound is negative and hence vacuous; it
is retained in the CSV. The asymptotic statement uses the proof, not this grid.

**Published empirical measurements remain unchanged.** The original n=256
T=1/T=16 ratio is 2.327639 [2.050148,2.674642], 24 complete trials per arm.
The separately registered n=512 T=1/T=23 ratio is
2.339095 [2.085387,2.596468], 32 complete trials per arm. Intervals are the
earlier approximate nominal 95% independent-bootstrap intervals. Distribution
and phase information remains in the earlier evidence and dependency receipt.
The original high-noise cap and 240 missing, gate-blocked holdout trials
remain; the original two-stage decision is inconclusive. The separate n=512
study does not retroactively supply that holdout.

**Execution scope:** deterministic proof checks only, zero new scientific
trajectories or seeds. The prior-round plan-before-measurement rule is not
bypassed by launching an experiment here. Raw logs and intermediate outputs
are outside this bundle. No original preregistration, gate, receipt, source
PDF or simulator was changed. One CPU; no network, paid resources, commit
or push. The no-go proof still needs independent review, and the all-order
mixed response remains a distinct proof obligation.
