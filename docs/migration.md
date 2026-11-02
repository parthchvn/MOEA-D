# Migration and provenance audit

Base repository commit: `76df0006c3770106b41dca05914301b97cb2132a` (“larger neighborhoods”). The restructure preserves original research files verbatim by Git blob identity. It does not rewrite Git history.

| Original path | Preserved path | Original blob |
|---|---|---|
| `large.py` | `legacy/large.py` | `140cf2a4b26adb49cf2fbf0e36f9681238c1b41d` |
| `sim.py` | `legacy/sim.py` | `081362eb554298797655588ebd83b2b95e5ebfbf` |
| `plots/Untitled.ipynb` | `legacy/notebooks/Untitled.ipynb` | `69ce532d661f013040126a24fa2d3b0d3e040e17` |
| `doerr_antipov.pdf` | `references/doerr_antipov.pdf` | `84bf77c2b4319e50a7aff749aa050094412c70e6` |
| `moead_drift_v2.pdf` | `references/moead_drift_v2.pdf` | `c9bf4bcae321be390cee40bafa3537f70dad1b05` |
| `multiplicative_drift.pdf` | `references/multiplicative_drift.pdf` | `cba42df1901f5ad513974e2c820e41ec7074ab8b` |
| `rare_events.pdf` | `references/rare_events.pdf` | `b6c63da8ba2398a0eff7d6d80132cebd8433b5b5` |

The OS metadata `.DS_Store` and empty notebook checkpoint are removed from the new tree and ignored going forward; they remain recoverable in Git history. The original nine-byte README is replaced. The notebook is preserved as an archival artifact, not silently treated as a validated source of new raw trials. The PDFs are existing reference material; their presence does not certify this repository's claims.

## Why the old simulations are not pooled

`large.py` uses noiseless ideal-reference Tchebycheff cost, cyclic self-parent reproduction, and clipped symmetric radius neighborhoods. `sim.py` instead uses absolute distance `abs(noisy_weight-index)`, random neighborhood parents, and fixed-size/parity-tie-broken neighborhoods. These are **different algorithms**, not interchangeable noisy/noiseless implementations.

The legacy large-neighborhood script also omits initialization evaluations, tests completion only at sweep boundaries, uses `-1` for capped runs and includes those sentinels in its mean helper, and can miss a completion on the final allowed sweep. Its plot titles equate apparent flatness with Theta-laws and describe the interior as instantaneous. The active code removes those interpretations and records each trial explicitly.

The legacy noisy script averages completed runs only; its cap and success rate do not convert that survivor-only mean into an unconditional expected runtime. The active statistics retain capped times and show censoring counts.

## Source research notes

The supplied noiseless notes (“matching Theta-law” and “corrections”) motivate the certificate and diagnostics, but contain unresolved and disputed arguments. Their claims are audited in `theory-status.md`; they are not presented as completed papers. Historical simulation counts without the underlying per-trial artifacts are not combined with the freshly generated data. This repository does not claim to have independently verified every PDF or historical notebook output.

## Active replacement

The new `src/` package provides a single specified cyclic model, a separately labeled frontier baseline, an independent literal-bitstring test oracle, reproducible experiment protocols, censoring-aware tables, and evidence regenerated entirely from retained raw trials. No original numerical output is relabeled as a newly reproduced observation.
