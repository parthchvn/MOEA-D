# Round 9: independent orphan audit

**Proved after audit:** in the supplied pinned model, the candidate
|B_n|<=1536n^5 holds for n>=3, with B the p^2 coefficient in the T=3 minus
T=2 simultaneous boundary-time gap, measured in sweeps. The
[analytic audit](audit.md) makes the predictable-count argument explicit,
checks both temporal insertion orders, and separately verifies the reversible
orphan calculation. The conservative higher-order noise window is unchanged.

**Mechanically checked exact arithmetic:**

| n | R then O, different sweeps | O then R, different sweeps | Same-sweep mixed | Mixed sum |
|---:|---:|---:|---:|---:|
| 4 | 3.8117060980 | 0.1188888346 | -0.2688947857 | 3.6617001469 |
| 6 | 6.7707331029 | -0.1077884782 | -0.2673261450 | 6.3956184797 |

O denotes an insertion at the even-n orphan recipient n; R denotes an
insertion at any other recipient. These are signed coefficient components,
not observed causal effects. The impossible within-sweep O-then-R order is
exactly zero. At n=4 the complete reconstructed T=2 second coefficient is
12.3558009571 sweeps per p^2. It matches the published full-state value exactly.
Decimals here are displays of exact rationals, not sampled means or intervals.

| Artifact | Contents |
|---|---|
| [audit.md](audit.md) | Complete analytic audit, assumptions, constants and falsifiers |
| [audit.py](audit.py) | Independent literal-mask, full-population-tuple rational checker |
| [test_audit.py](test_audit.py) | 14 adversarial deterministic tests |
| [suffix.csv](suffix.csv) | Maxima by phase for every checked overwrite at n=4,6,8 |
| [mixed.csv](mixed.csv) | Exact temporal decomposition at n=4,6 and n=4 full reconstruction |
| [local.csv](local.csv) | Independent local-resolvent coefficients and finite-p joint-chain identities |
| [verification.json](verification.json) | Scope, arithmetic, grids and comparison counts |
| [dependency.json](dependency.json) | Prior-round replay, registration, receipt and seed checks |
| [checks.json](checks.json) | Tests, preservation, timing and reproduction accounting |
| [provenance.json](provenance.json) | Input revision, commands and source/output hashes |
| [memory.md](memory.md) | Durable status and claim supplement |

The 16,512 exact suffix cases include every y<n, possible original-corner
status, nonorphan overwrite (k,z), and phase at n=4,6,8. They verify both the
suffix difference bound and the residual-reward identity behind the proof.
Cases with no effective overwrite and some repeated resulting populations
are deliberately included; this count is not a count of distinct states.
The maximum difference/bound ratios are 0.136030, 0.167194 and 0.176453,
respectively. The separate single-process excess/bound maxima are 0.136030,
0.183586 and 0.218124. No bound violation was found. Further checks cover
268 regular means with orphan help omitted, 268 mixed forcings, 20 mixed
responses, 445 local balance equalities and five finite-p joint-chain identities.

The new checker needs only Python's standard library. From the repository root:

```sh
PYTHONDONTWRITEBYTECODE=1 python -S deliverables/test_audit.py
PYTHONDONTWRITEBYTECODE=1 python -S deliverables/audit.py --repo . --out /tmp/round9-exact
```

For a complete serial replay, including all published dependencies, use a new
output directory. NumPy and Matplotlib are needed only by the earlier replay.
This calls no scientific sampler:

```sh
PYTHONDONTWRITEBYTECODE=1 OPENBLAS_NUM_THREADS=1 python deliverables/reproduce.py --repo . --out /tmp/round9-replay
PYTHONDONTWRITEBYTECODE=1 OPENBLAS_NUM_THREADS=1 python -m unittest discover -s tests -v
PYTHONDONTWRITEBYTECODE=1 python -S research/reports/large-T-20261109/followup/round-0008/test_second.py
PYTHONPYCACHEPREFIX=/tmp/round9-pycache python -m py_compile sim.py large.py scripts/run_research.py deliverables/audit.py deliverables/reproduce.py deliverables/test_audit.py
```

After publication replace `deliverables` in commands by
`research/reports/large-T-20261109/followup/round-0009`. The checker resolves
earlier inputs through `--repo`; links within this bundle remain relative.
The five generated CSV/JSON outputs are compared byte for byte. Execution
timings and provenance describe the recorded invocation and are not expected
to reproduce bytewise. Raw logs and restored prior outputs stay outside this
bundle. No source PDF, scientific kernel or earlier evidence was edited.

**Published empirical measurements, reverified and unchanged:** the original
n=256 T=1/T=16 ratio is 2.327639 [2.050148,2.674642], 24 complete observations
per arm. The separate registered n=512 T=1/T=23 ratio is
2.339095 [2.085387,2.596468], 32 complete observations per arm. Intervals are
the earlier approximate nominal 95% bootstrap intervals. The prior reports
and dependency receipt retain distributions and all phase denominators.
The original campaign retains its single capped main trial and 240 missing,
gate-blocked holdout trials; its two-stage decision remains inconclusive.
This round generated no empirical trajectories, seeds, censoring or confidence
intervals. No paid resources, network access, commit or push was used.

**Remaining proof obligation:** a uniform third-and-higher-order remainder
on a polynomial noise scale. The audited bound on B alone does not establish
ordering at p=c/n or enlarge the existing conservative sign window. Further
insertions can corrupt adjacent donors simultaneously, beyond the regular
states controlled in this proof.
