# Validation record

This records completed checks, not a guarantee that the software is bug-free or that an asymptotic runtime conjecture is true. Validation receipts are tied to specific source revisions, not to an unspecified future version of the repository.

## Reproduced neighborhood revision

The corrected neighborhood experiment was generated from source revision [`ea3ce28`](https://github.com/parthchvn/MOEA-D/commit/ea3ce28fe25fa957d63e3c99dd21b2c4b4852375). Its regenerated evidence was committed in [`31ec66e`](https://github.com/parthchvn/MOEA-D/commit/31ec66eee87ffe115d1a1ef7919cfad1e8ce32b0). The [manifest](../evidence/neighborhoods/manifest.json) records a clean generating source tree, source-file hashes, data hashes, Python/dependency versions, RNG, and seed derivation. Later documentation-only changes do not alter those generating-source hashes. The manifest in each evidence directory identifies its own experiment; this record does not claim that all additional modules or future protocols were part of this run.

## Checks completed on 2 November 2026

| Check | Observed result | Record |
|---|---|---|
| Corrected automated suite, Python 3.13 | **154 passed**; no failures or skips reported | [Reproduction job](https://github.com/parthchvn/MOEA-D/actions/runs/41464295294/job/125340997198) |
| Full neighborhood protocol, report generation, source/hash verification, and artifact commit | Every workflow step passed | [Reproduction workflow](https://github.com/parthchvn/MOEA-D/actions/runs/41464295294) |
| Recorded neighborhood trials | **2,144 completed; 0 reached their evaluation cap** | [Evidence report](../evidence/neighborhoods/README.md) |
| Generated neighborhood figures | **8 SVG figures**, with raw CSV/JSONL inputs retained | [Figures](../evidence/neighborhoods/figures) |
| Artifact integrity and generating-source consistency | 14 artifact files verified; source hashes matched | [Reproduction job](https://github.com/parthchvn/MOEA-D/actions/runs/41464295294/job/125340997198) |
| Eligible noiseless endpoint-certificate checks | **468,983 checks; 0 violations** | [Raw records](../evidence/neighborhoods/runs.csv) |

The certificate checks occur at eligible completed-sweep boundaries, after an actual endpoint acceptance. They are not 468,983 independent statistical trials. The deterministic certification argument and its precondition are given in [the theory-status document](theory-status.md).

The CI matrix separately runs Python 3.11 and 3.13, fresh smoke simulations, source/hash checks on both fresh and committed evidence, and reconstruction of committed summary tables and the evidence README from raw trials. Revision-specific results and retained test/environment receipts are available in [pull request #1's checks](https://github.com/parthchvn/MOEA-D/pull/1/checks). A source-changing commit can intentionally fail the committed-evidence check until its corresponding regenerated evidence is committed; that check must not be disabled to conceal stale results.

## Review-found correction: frontier singleton initialization

The original 131-test suite did not detect a shared-parent initialization error in the separate frontier baseline. When L=R=w, either scheduler label mutates the same parent, so the first mutation can expand either side. Tracking only the selected side did not always track the actual solved interval. The fix updates both boundaries from the post-replacement state.

The exact conditional expectation, including the one shared initial evaluation, is

`1 + n H_w + n H_(n-w) - 1{0<w<n}`.

The formula without the indicator was not the exact expectation for this broadcast algorithm. The corrected proof is in [frontier.md](frontier.md). Twenty-three new regression tests cover exact-rational Bellman equations for every interval at n=1,...,12, an independent literal-bitstring implementation that recomputes the entire solved set, and censoring. The full 154-test suite and full evidence generation were rerun after this fix. The cyclic larger-neighborhood simulator was unchanged by this correction.

## What the tests cover

The suite contains independently written literal-bitstring oracles, exact rational enumeration of small mutation/noise laws, small-state certification checks, Python/Numba execution agreement, deterministic replay, evaluation-accounting and censoring checks, and end-to-end experiment/report integrity checks. It checks that one noisy offspring observation is shared across replacements and that noise does not overwrite the true genotype.

These tests check specified cases and implementation properties. They do not establish the proposed full-population runtime law, a matching lower bound, a noise threshold, or an n-uniform bound on endpoint jumps. Those distinctions remain explicit in [the claim audit](theory-status.md). A passing test suite is not a replacement for a complete proof.

## Recheck a checkout

From the repository root after installing the dependencies:

```bash
python -m pytest -q
python -m moead.verify --input evidence/neighborhoods --check-source
python -m moead.experiments --config experiments/smoke.json --out results-local/validation-smoke --engine numba
python -m moead.report --input results-local/validation-smoke
python -m moead.verify --input results-local/validation-smoke --check-source
```

Use a new output directory for each reproduction, or explicitly request `--overwrite`. Full experiment commands and statistical caveats are in the [README](../README.md) and [methodology](methodology.md).
