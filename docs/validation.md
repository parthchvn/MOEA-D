# Validation record

This records completed checks, not a guarantee that the software is bug-free or that an asymptotic runtime conjecture is true.

## Reproduced revision

The experiment-producing source revision is [`73ff50e`](https://github.com/parthchvn/MOEA-D/commit/73ff50e1b7c55dafeef1532dfac5366eb0ee0b6b). The generated evidence was committed in [`f25be5c`](https://github.com/parthchvn/MOEA-D/commit/f25be5cdc9bd17881318f45c13fc2fc91e16d06d). Its [manifest](../evidence/neighborhoods/manifest.json) records a clean source tree, source-file hashes, data hashes, Python and dependency versions, and the random-number generator and seed derivation. Later documentation-only commits do not change those source hashes.

## Checks completed on 2 November 2026

| Check | Observed result | Record |
|---|---|---|
| Automated tests, Python 3.13 | 131 passed; no failures or skips reported | [CI job](https://github.com/parthchvn/MOEA-D/actions/runs/41462824653/job/125335949709) |
| Automated tests and smoke reproduction, Python 3.11 | Job passed, including reporting and source/hash verification | [CI job](https://github.com/parthchvn/MOEA-D/actions/runs/41462824653/job/125335950090) |
| Full protocol, report generation, source/hash verification, and artifact commit | Every workflow step passed | [Reproduction workflow](https://github.com/parthchvn/MOEA-D/actions/runs/41462824643) |
| Recorded full-protocol trials | 2,144 completed; 0 reached their evaluation cap | [Evidence report](../evidence/neighborhoods/README.md) |
| Eligible noiseless endpoint-certificate checks | 468,983 checks; 0 violations | [Raw records](../evidence/neighborhoods/runs.csv) |

The certificate checks are observations at eligible completed-sweep boundaries, after an actual endpoint acceptance. They are not 468,983 independent statistical trials. The deterministic certification argument and its precondition are given in [the theory-status document](theory-status.md).

## What the tests cover

The suite contains an independently written literal-bitstring transition oracle, exact rational enumeration of small mutation/noise laws, small-state certification checks, Python/Numba execution agreement, deterministic replay, evaluation-accounting and censoring checks, and end-to-end experiment/report integrity checks. The oracle verifies that a single noisy offspring observation is shared across neighborhood replacements and that true genotypes are not overwritten by noise.

These tests check specified cases and implementation properties. They do not establish the proposed full-population runtime law, a matching lower bound, a noise threshold, or an n-uniform bound on endpoint jumps. Those distinctions remain explicit in [the claim audit](theory-status.md).

## Recheck a checkout

From the repository root after installing the dependencies:

```bash
python -m pytest -q
python -m moead.verify --input evidence/neighborhoods --check-source
python -m moead.experiments --config experiments/smoke.json --out results-local/validation-smoke --engine numba
python -m moead.report --input results-local/validation-smoke
python -m moead.verify --input results-local/validation-smoke --check-source
```

Use a new output directory for each reproduction, or explicitly request `--overwrite`. The full experiment commands and statistical caveats are in the [README](../README.md) and [methodology](methodology.md).
