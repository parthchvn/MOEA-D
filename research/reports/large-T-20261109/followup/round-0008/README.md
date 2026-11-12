# Round 8: second-order supplied-corner response

The expansion in sweeps is m_3-m_2=p A_n+p^2 B_n+O_n(p^3).
The factor 1/2 is already included in B. Offspring attempts multiply every
time coefficient by n+1. No initialization evaluations are charged.

**Proved finite-n identity:** [derivation.md](derivation.md), equations (2)–(5),
give a signed two-insertion recurrence requiring at most three wrong slots.
**Candidate proof:** equations (6)–(13) give |B_n|<=1536n^5, including the
even-n T=2 orphan. Its mixed-insertion argument needs independent review.
**Proved conservative bound:** equations (14)–(15) control all higher orders
on an explicit, extremely small n-dependent noise window. This does not
establish fixed-positive-c ordering at p=c/n.

| Artifact | Purpose |
|---|---|
| [coefficients.csv](coefficients.csv) | Exact rational coefficients per arm, n=3,4; separate within/different-sweep contributions |
| [gaps.csv](gaps.csv) | Exact T=3 minus T=2 coefficients, n=3,4 |
| [numeric.csv](numeric.csv) | Deterministic float64 gap evaluations, n=3,...,12; not certified intervals |
| [oracle.json](oracle.json) | Independent literal-mask full-population rational results |
| [bounds.csv](bounds.csv) | Polynomial bounds and proved sign windows for the published exact A_n, n=3,...,10 |
| [comparison.json](comparison.json) | Quadratic prediction versus the previously certified n=3,p=1/192 gap |
| [verification.json](verification.json) | Exact inequality searches, orphan identity, mixed-term and arithmetic comparisons |
| [dependency.json](dependency.json) | Full prior-round replay and registration/receipt preservation |
| [checks.json](checks.json) | Tests, timings, limitations and preservation accounting |
| [provenance.json](provenance.json) | Source revision, commands, toolchain and artifact hashes |
| [memory.md](memory.md) | Durable claim/status supplement |

**Mechanically checked exact values**, displayed as decimals:

| n | A_n | B_n | Different-sweep part of B | Same-sweep part of B |
|---:|---:|---:|---:|---:|
| 3 | +0.2221318472 | +0.4281536262 | +0.9252013465 | -0.4970477202 |
| 4 | -1.4923892474 | -1.8401743257 | -1.1483549410 | -0.6918193846 |

The literal-mask oracle agrees on all 20 rational component comparisons over
6,762 population/cardinality cases. Exact searches check 1,904 regular means,
4,992 orphan suffix differences, 124 mixed forcings, eight mixed responses,
ten orphan coefficient identities and 400 local balance identities. No
violation was found. These are finite checks of the candidate proof's steps.
At n=12 the deterministic float64 evaluation gives B=-22.49855751; the larger
grid supplies no certified asymptotic law.

At the previously certified n=3,p=1/192 point, the quadratic prediction is
0.001168551114485052 sweeps. The certified discrepancy is between
1.10944950e-7 and 1.12116260e-7 sweeps, over 104 times smaller than the linear
discrepancy. This comparison uses a prior certificate and is not a new sampled
measurement. In [bounds.csv](bounds.csv), `window` is the largest dyadic value
below the exact formula window, keeping the certificate compact. At n=4,
0<p<=2^(-34) certifies a negative gap; the window is deliberately conservative.

All new arithmetic uses Python's standard library. From the repository root:

```sh
PYTHONDONTWRITEBYTECODE=1 python -S deliverables/test_second.py
PYTHONDONTWRITEBYTECODE=1 python -S deliverables/second.py --out /tmp/round8-exact --n 3 4
PYTHONDONTWRITEBYTECODE=1 python -S deliverables/oracle.py --out /tmp/round8-oracle.json --n 3 4
```

Full serial regeneration, including the earlier published evidence and output
comparisons, is provided by [reproduce.py](reproduce.py). It needs NumPy and
Matplotlib only for the earlier-round replay; it invokes no scientific sampler.
Choose a new output directory:

```sh
PYTHONDONTWRITEBYTECODE=1 OPENBLAS_NUM_THREADS=1 python deliverables/reproduce.py --repo . --out /tmp/round8-replay
PYTHONDONTWRITEBYTECODE=1 OPENBLAS_NUM_THREADS=1 python -m unittest discover -s tests -v
PYTHONPYCACHEPREFIX=/tmp/round8-pycache python -m py_compile sim.py large.py scripts/run_research.py
```

After publication replace `deliverables` in commands with
`research/reports/large-T-20261109/followup/round-0008`. Code resolves earlier
dependencies using `--repo`; links inside this bundle stay relative.
Exact rational results and generated JSON/CSV artifacts are compared byte for
byte. Float64 rows have the usual toolchain qualification. Timing and provenance
receipts describe this invocation and are not expected to reproduce bytewise.

**Published empirical evidence, unchanged:** the original n=256 ratio is
2.327639 [2.050148,2.674642], with 24 complete observations per arm. The separate,
previously registered n=512 ratio is 2.339095 [2.085387,2.596468], with 32 complete
observations per arm. Intervals are the earlier approximate nominal 95%
bootstrap intervals. Their phase denominators and distributions remain in the
prior reports and the replayed dependency receipt. The original campaign still
has one capped main trial and 240 missing, gate-blocked holdout trials. Its
two-stage decision remains inconclusive. No new trajectories, seeds or empirical
confidence intervals are generated here; censoring is inapplicable to the new
deterministic coefficients.

The attempted larger float64 calculation was interrupted without retaining
results; it is outside the reproduced grid and supports no claim. Raw logs and
restored prior outputs are outside this publication bundle. No prior plan,
receipt, source PDF, kernel or gate was changed. No commit, push, network access,
paid resource or cloud job was used.
