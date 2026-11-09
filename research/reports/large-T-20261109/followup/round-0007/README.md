# Round 7: independent asymptotic audit

**Proved after audit, for the supplied pinned corner:**
A_n=−(n/2)log n+O(n). The [analytic audit](audit.md) replaces the candidate's
uniformity assertions with explicit bounds and checks the exceptional sites,
ascending suffix order, both edge parities and the even-n orphan.
It establishes eventual negativity of the derivative. A Taylor remainder
uniform in n, and ordering at fixed positive c with p=c/n, remain unresolved.

**Mechanically checked:** the independent literal-mask full-population
calculation at n=4 gives A_4=−1.4923892474463167… exactly, matching the reduction.
It visits all 3,125 populations for each cardinality. All 120 published exact
recipient contributions at n=3,…,10 also match the separate evaluator.

| Exact finite check | Cases | Maximum checked quantity | Universal analytic bound |
|---|---:|---:|---:|
| Slow edge leading-term normalized error | 128 | 0.183801 | 64 |
| Opposite-direction residual at a slow edge | 128 | 0.259157 | 6 |
| Multiple-step residual at a slow edge | 128 | 0.694909 | 18 |
| Two-error clean mean divided by n | 1,348 | 3.828226 | 5 |
| Slot-2 phase delay, endpoint wrong, divided by q | 1,348 | 2.978391 | 98 |
| Slot-2 phase delay, endpoint already correct | 1,348 | 1.984960 | 7 |

Decimals display exact rational computations; they are not confidence
intervals or trajectory measurements. The normalized leading error is
|L−n/(2u)|/(1+n/u²). Every wrong weight is included in the finite checked
systems. The constants were derived analytically, not inferred from these
maxima. The universal proof is separate from finite verification.

| Artifact | Purpose |
|---|---|
| [audit.md](audit.md) | Complete independent argument with explicit bounds and scope |
| [audit.py](audit.py) | Exact polynomial kernels, exceptional-state oracle and edge checks |
| [edges.csv](edges.csv) | All 128 checked edge sites, including right/left order |
| [exceptions.csv](exceptions.csv) | All 95 exceptional recipient coefficients and bounds |
| [verification.json](verification.json) | Exact full-state derivatives, counts, maxima and grid |
| [dependency.json](dependency.json) | Replayed prior publication, receipts, registration and holdout |
| [test_audit.py](test_audit.py) | Fifteen deterministic regression and counterexample tests |
| [reproduce.py](reproduce.py) | Complete serial regeneration, including the published dependencies |
| [memory.md](memory.md) | Durable C25/C26 changes and unresolved questions |
| [checks.json](checks.json) | Tests, timing, toolchain, hashes and preservation accounting |

From the repository root, the new exact mathematical audit and tests require
only Python's standard library. Use a new output directory:

```sh
PYTHONDONTWRITEBYTECODE=1 python -S deliverables/audit.py --repo . --out /tmp/round7-audit
PYTHONDONTWRITEBYTECODE=1 python -S deliverables/test_audit.py
```

Complete regeneration also needs NumPy and Matplotlib for the **earlier**
published arithmetic/plot replay. It never invokes a scientific sampler:

```sh
PYTHONDONTWRITEBYTECODE=1 OPENBLAS_NUM_THREADS=1 python deliverables/reproduce.py --repo . --out /tmp/round7-replay
PYTHONDONTWRITEBYTECODE=1 OPENBLAS_NUM_THREADS=1 python -m unittest discover -s tests -v
PYTHONPYCACHEPREFIX=/tmp/round7-pycache python -m py_compile sim.py large.py scripts/run_research.py
```

After publication, replace `deliverables` in these commands with
`research/reports/large-T-20261109/followup/round-0007`. Earlier dependency paths
are resolved relative to `--repo`. All four generated new result files replay
byte for byte. The new arithmetic is exact; decimal displays use Python float
conversion. Earlier float/plot replay has its previously recorded toolchain
qualification. Raw logs and restored prior outputs remain outside this bundle.

**Published empirical evidence, unchanged and reverified:** at n=256 the
original restricted ratio is 2.327639 [2.050148,2.674642], with 24 complete
observations per arm. The separate registered n=512 ratio is
2.339095 [2.085387,2.596468], with 32 complete observations per arm. These are
the earlier approximate nominal 95% bootstrap intervals. They are not evidence
for the supplied-corner derivative theorem. The original campaign still has
one capped main trial and 240 missing gate-blocked holdout trials. Its two-stage
decision remains inconclusive. No prior evidence, plan, gate, seed or source
PDF changed; no dependency repair was needed.

**Limits and falsifiers:** the proof is specific to ideal extrema, pinned
labels, the supplied corner, standard-bit mutation/activated bitwise noise,
filled cardinalities and simultaneous boundary stopping. The parent-0
counterexample in the tests prevents extending the recipient-1 mass bound
outside its allowed insertion histories. The tests also detect a cyclic-order
swap and preserve the even-n orphan. A failed explicit uniform inequality or
independent derivative mismatch would falsify the relevant step. No claim of
global literature novelty, positive-c ordering, all-n negativity, ordinary-run
asymptotics or causal explanation of pre-S savings is made offline.
