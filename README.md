# MOEA/D under prior noise

**A reproducible research repository for OneMinMax, neighborhood exchange, and evaluation-efficient scheduling.**

The active implementation studies an explicitly specified **cyclic, self-parent, Tchebycheff MOEA/D** with one-bit mutation, optional one-bit prior noise, and no re-evaluation. It is not intended to represent every implementation called MOEA/D.

> **Research status:** the proposed full-population law
> `Theta(n² + (n²/T) log(1+n/T))` is **not certified by this repository**.
> The supplied arguments leave an interior/maximum-time dependency and a matching-lower-bound supply problem unresolved. Finite experiments, zero invariant violations, and fitted curves cannot close those gaps. See [the claim-by-claim audit](docs/theory-status.md).

## Evidence for larger neighborhoods

The [committed evidence report](evidence/neighborhoods/README.md) contains **2,144 seeded trials**: 32 replicates per configuration, `n = 32, 64, 128, 256, 512`, noiseless runs and one-bit prior noise `p = 0.1/n`. It includes a fixed-`n` radius sweep, endpoint occupation and jump diagnostics, and a separate noiseless frontier-scheduling baseline.

![Effect of radius](evidence/neighborhoods/figures/runtime_vs_radius.svg)

![Noiseless scaling diagnostic](evidence/neighborhoods/figures/scaling_noiseless.svg)

![One-bit prior noise diagnostic](evidence/neighborhoods/figures/scaling_alpha_0.1.svg)

These plots report **evaluations, including initialization**, with pointwise approximate 95% bootstrap intervals. The reference point is fixed at `(n,n)`. A global neighborhood is `r=n`; clipped radius neighborhoods have different sizes at the boundary and in the interior. We do not call `2r+1` the actual size of every neighborhood.

Every run, including a run that hits its evaluation cap, is retained. For censored configurations the reported statistic is the **mean capped runtime**, not a survivor-only mean or an estimate of the unrestricted mean. Censoring counts, all seeds, and complete reproducibility details are in the report and manifest. No asymptotic conclusion is inferred from the tested sizes alone.

[Raw trials](evidence/neighborhoods/runs.csv) · [Summaries](evidence/neighborhoods/summary.csv) · [Diagnostic arrays](evidence/neighborhoods/diagnostics.jsonl) · [Provenance](evidence/neighborhoods/manifest.json)

## Install and reproduce

Python 3.11 or newer is required. The following uses the tested direct dependency versions; the manifest records the actual environment.

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements-evidence.txt
python -m pip install -e . --no-deps
python -m pytest -q

# Small end-to-end check.
python -m moead.experiments --config experiments/smoke.json --out results-local/smoke
python -m moead.report --input results-local/smoke
python -m moead.verify --input results-local/smoke --check-source

# Reproduce the full protocol in a NEW directory.
python -m moead.experiments --config experiments/neighborhoods.json --out results-local/full --engine numba
python -m moead.report --input results-local/full
python -m moead.verify --input results-local/full --check-source

# Check the committed evidence without rerunning simulations.
python -m moead.verify --input evidence/neighborhoods
```

Use `--engine python` for the unaccelerated reference path. Numba is optional for the package, but recommended for the full experiment grid. The tests compare both paths against each other and against a separate literal-bitstring oracle. An existing nonempty output directory is refused unless `--overwrite` is explicitly supplied.

## Exact algorithm contract

For each index `j=0,...,n`, the incumbent stores its true weight `w[j]` and one persistent noisy observation `v[j]`. The integer scalarization is

```text
cost(j, v) = max(j*(n-v), (n-j)*v).
B(k)       = {j : 0 <= j <= n and |j-k| <= r}.
```

Initialization samples `n+1` independent uniform bit strings and evaluates each once. In each cyclic turn `k=0,...,n`, mutate **the current incumbent of k**, flip exactly one uniformly chosen bit, and evaluate the offspring once. With probability `p`, the evaluation flips one further uniformly chosen bit without changing the stored genotype. The **same observed offspring vector** is offered to every index in `B(k)`; ties are accepted. The ideal reference point is fixed, and stored parent observations are never refreshed.

The stopping instrument checks `w[j]=j` for every `j` after every offspring. It also records first full true-front coverage separately. True weights are not used by selection as an oracle. Runtime counts objective-vector evaluations, not scalar comparisons, CPU time, sweeps, or the number of neighbors updated. [Full specification and limitations](docs/methodology.md).

## What is proved here, and what is not

| Item | Status |
|---|---|
| Exact reduction from bit strings to the `(true weight, stored observation)` state | Proof in the model notes; exhaustive small transition-law tests and coupled oracle tests |
| Noiseless endpoint certification and invariant (J) after an actual endpoint acceptance | Short deterministic proof; instrumented checks use precisely this precondition |
| Noiseless endpoint upper bound | Proof supplied; **does not** establish the simultaneous full-population bound |
| Frontier variant, noiseless, single-solution initialization | Exact conditional mean `1+n(H_w+H_(n-w))`; proof and Bellman-identity tests |
| Larger-neighborhood cyclic full-population Theta-law | **Open in the available proof material**; experiments are evidence only |
| Constant jump bound, matching lower bound, general noise threshold, novelty priority | **Not claimed** |

The [frontier baseline](docs/frontier.md) uses different scheduling **and initialization** from cyclic MOEA/D. Its plot must not be interpreted as a neighborhood-only comparison or a noisy-runtime theorem.

## Repository map

```text
src/moead/                 validated simulator, kernels, runner, statistics, reporting
  model.py                 public API and configuration validation
  kernel.py                exact count-space transitions; optional acceleration
  frontier.py              separate noiseless scheduling baseline
  experiments.py           fixed protocols, deterministic seeds, raw records, provenance
  statistics.py            censoring-aware summaries and Monte Carlo intervals
  report.py / verify.py    regenerate plots; verify artifact integrity
experiments/               machine-readable full and smoke protocols
tests/                     mathematical identities, bitstring oracle, replay and regression tests
docs/                      model, proof-status audit, frontier proof, migration notes
evidence/neighborhoods/    committed raw data, summaries, diagnostics and SVG figures
legacy/                    original scripts and notebook, preserved verbatim but not endorsed
references/                PDFs already present in the original repository
.github/workflows/         tests plus branch-scoped evidence reproduction
```

## Contributing evidence

State the algorithm and initialization before comparing results. Change a versioned protocol rather than editing a plotted number. Keep every trial and its seed; record timeouts as censored, not `-1` runtimes. Distinguish a finite observation, a conjecture, a conditional theorem, and a fully supplied proof. Run the tests and regenerate the report after code changes. Increasing neighborhood size can reduce evaluations while increasing scalar-comparison work; this repository does not claim an equivalent wall-clock speed-up.

The original research artifacts are retained with their provenance in [the migration audit](docs/migration.md). No unsupported historical theorem or novelty assertion has been silently promoted into the active documentation.
