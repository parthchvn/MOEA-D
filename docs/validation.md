# Validation record

These are completed, revision-specific checks, not a guarantee that the software is bug-free or that an asymptotic runtime conjecture is true. Each evidence manifest identifies its own generating source and environment.

## Completed experiment protocols

| Protocol | Generating source | Trials | Completed | Budget-censored | Figures | Execution record |
|---|---|---:|---:|---:|---:|---|
| Corrected neighborhood/scheduling experiment | `ea3ce28fe25fa957d63e3c99dd21b2c4b4852375` | 2,144 | 2,144 | 0 | 8 | [Full reproduction](https://github.com/parthchvn/MOEA-D/actions/runs/41464295294) |
| Expanded scaled/fixed one-bit noise | `5f1f346973dacf08f7e3502d81076363dc4f9bcc` | 8,704 | 6,535 | 2,169 | 8 | [Full reproduction](https://github.com/parthchvn/MOEA-D/actions/runs/41465033304) |

Both workflows completed simulation, reporting, source/data verification, and the evidence commit. The protocols have different administrative caps and independently seeded controls. Their runtime observations are not pooled into a single mean. Both retain every trial, including all capped observations.

The [neighborhood manifest](../evidence/neighborhoods/manifest.json) and [noise manifest](../evidence/noise-grid/manifest.json) record clean generating source trees, source-file and data hashes, Python/dependency versions, RNG, and seed derivation. Neighborhood evidence was regenerated after the frontier correction described below. Later documentation-only commits do not change those source fingerprints.

## Automated validation completed on 2 November 2026

| Check | Observed result | Receipt |
|---|---|---|
| Corrected neighborhood suite | 154 tests passed on Python 3.13 | [Reproduction job](https://github.com/parthchvn/MOEA-D/actions/runs/41464295294/job/125340997198) |
| Expanded suite including noise-protocol regressions | **176 tests passed**, zero failures/skips, in the retained Python 3.13 receipt | [CI run](https://github.com/parthchvn/MOEA-D/actions/runs/41465039333) |
| Python version matrix at revision `5f1f346` | Python 3.11 and 3.13 jobs passed | [CI run](https://github.com/parthchvn/MOEA-D/actions/runs/41465039333) |
| Fresh smoke simulation, report, source/hash verification | Passed on both Python versions | Same CI run |
| Committed neighborhood summaries and README reconstructed from raw records | Exact agreement in CI | Same CI run |
| Full noise grid, report, source/hash verification | Passed; all 8,704 protocol entries retained | [Noise reproduction](https://github.com/parthchvn/MOEA-D/actions/runs/41465033304) |
| Eligible noiseless certificate observations in the neighborhood experiment | **468,983 checks, zero violations** | [Raw records](../evidence/neighborhoods/runs.csv) |

The Python 3.13 CI artifact includes JUnit XML, environment information, integrity-verification output, and an archive of the tested revision. Pull-request workflows may test GitHub's synthetic merge commit; the receipt's `source-commit.txt` identifies that exact checkout rather than silently equating it with the branch head. The quoted test counts apply to these receipts, not every future revision.

The current CI additionally verifies the expanded noise dataset when present and independently regenerates its summary and README from raw trials. The completed full-noise workflow verifies that dataset itself; the older CI receipt above must not be described as testing an evidence directory that had not yet been committed. Latest revision-specific results are available under [pull request #1's checks](https://github.com/parthchvn/MOEA-D/pull/1/checks).

Certificate observations are taken at eligible completed-sweep boundaries after an actual endpoint acceptance. They are correlated within runs, not 468,983 independent statistical trials. The deterministic proof and its precondition are in [the theory-status document](theory-status.md).

## Review-found correction: frontier singleton initialization

The original 131-test suite did not detect an initialization error in the separate frontier baseline. When L=R=w, both scheduler labels select the same parent; either mutation direction can expand the actual solved interval. Advancing only the selected boundary sometimes failed to recognize an already solved adjacent slot. The fix updates both boundaries from the actual post-replacement state.

Including the one shared initial evaluation, the corrected exact conditional expectation is

`1 + n H_w + n H_(n-w) - 1{0<w<n}`.

The formula without the indicator was not the exact expectation for this broadcast algorithm. For n=2,w=1 the expectation is 4, not 5. The corrected argument is in [frontier.md](frontier.md). Twenty-three added regression tests include exact-rational Bellman equations for every interval at n=1,...,12, an independent literal-bitstring implementation that recomputes the entire solved set, and censoring. The 154-test corrected suite and all neighborhood evidence were rerun. The expanded noise-protocol tests bring the later suite to 176. The cyclic neighborhood simulator itself was unchanged by the frontier fix.

## Scope of the tests

Tests include independent literal-bitstring oracles, exact rational enumeration of small mutation/noise laws, small-state certification checks, Python/Numba agreement, deterministic replay, evaluation accounting, censored-run handling, configuration/seed completeness, and end-to-end report-integrity checks. They check that the same noisy offspring observation is shared across replacements and that evaluation noise does not overwrite the genotype.

Passing these tests does not establish the cyclic full-population runtime law, a matching lower bound, a general noise threshold, or an n-uniform endpoint-jump bound. The [claim audit](theory-status.md) separates those unresolved statements from supplied proofs. The special p=1 obstruction in [noise-analysis.md](noise-analysis.md) has its own argument and is not extrapolated to p<1.

## Recheck a checkout

After installing the pinned dependencies:

```bash
python -m pytest -q
python -m moead.verify --input evidence/neighborhoods --check-source
python -m moead.noise --out evidence/noise-grid --verify --check-source

python -m moead.experiments --config experiments/smoke.json --out results-local/validation-smoke --engine numba
python -m moead.report --input results-local/validation-smoke
python -m moead.verify --input results-local/validation-smoke --check-source
```

Use a new output directory for each reproduction. The neighborhood runner supports explicit `--overwrite`; the expanded-noise runner requires a new or empty directory. Full commands and statistical qualifications are in the [README](../README.md) and [methodology](methodology.md). A source-changing commit can fail the committed-evidence check until the corresponding evidence is regenerated; do not disable that check to conceal stale results.
