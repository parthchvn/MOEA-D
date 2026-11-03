# MOEA/D runtime experiments on OneMinMax

This repository studies how MOEA/D behaves on the bi-objective OneMinMax benchmark under one-bit mutation, with particular attention to neighborhood sharing and one-bit prior noise without reevaluation.

The project contains legacy models and a controlled noiseless variant:

- `sim.py` simulates full bit strings under one-bit prior noise. Its neighborhood parameter `T` is the requested number of subproblems in each neighborhood.
- `large.py` uses an exact Hamming-weight state reduction for the noiseless model. Its parameter `r` is a symmetric neighborhood radius, so an unclipped interior neighborhood has size `2r + 1`; boundary neighborhoods are smaller.
- `large.run_controlled` supports exact/lazy one-bit mutation, paired archive/alignment stopping observations, and the reviewed lazy same-weight broadcast ON/OFF intervention with passive target-hit phases.

Do not compare their `T` values or stopping times without first reconciling these conventions. The main noiseless runtime law in `large.py` remains conjectured; the finite studies below do not establish it.

## Quick start

Use Python 3.11 or newer.

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python -m unittest discover -s tests -v
```

Run a small, reproducible noiseless grid:

```bash
python scripts/run_research.py large-grid \
  --n 50 100 200 \
  --r 0 1 4 8 \
  --reps 10 \
  --max-seconds 3600
```

Run a noisy grid:

```bash
python scripts/run_research.py noise-grid \
  --n 20 40 80 \
  --T 1 2 3 \
  --p-factor 0.05 \
  --trials 20 \
  --stop-rule aligned \
  --max-seconds 3600
```

Each command writes a timestamped, machine-readable run under `research/runs/`. Results checkpoint after every completed trial and include an exact source snapshot, dependency versions, seeds, censoring, and a dirty-tree patch. Generated runs and figures are ignored by Git by default.

## Research workflow

- `AGENTS.md` defines the operating rules for human and AI research work.
- `research/PROJECT.md` fixes the model definitions and scope.
- `research/CLAIMS.md` separates proved, checked, empirical, and open claims.
- `research/STATUS.md` records the current research frontier and next decisions.
- `research/EXPERIMENTS.md` defines the experiment and evidence protocol.
- `research/OVERNIGHT.md` contains a bounded long-horizon Codex runbook.
- `research/START_LOCAL.md` gives the exact local five-hour launch and recovery steps.

The PDFs in the repository are source material. They should be cited and audited, not modified in place.

## Completed controlled studies and next proposal

**Empirically supported:** the exact-to-lazy mutation change better explained
finite communication-radius sensitivity than archive/alignment stopping at
n=256/512. The subsequent fixed-lazy broadcast ablation found that suppressing
same-weight neighbor communication increased r=1 mean evaluations by about
43% and 22%, respectively, and increased the radius contrast. These findings
support finite broadcast contribution, not exclusive mediation or asymptotics.
Universal archive/alignment and endpoint/completion identities have explicit
counterexamples despite equality in the reported positive-radius samples.

- [Canonical model and source comparison](research/PAPER_COMPARISON.md).
- [Exact/lazy factorial report](research/reports/20261102T212758Z-radius-factorial.md)
  and [frozen protocol](research/FACTORIAL_PREREG.md).
- [Lazy broadcast report](research/reports/20261103T022831Z-broadcast-ablation.md)
  and [frozen protocol](research/BROADCAST_PREREG.md).
- [Published evidence packs and recomputation instructions](research/evidence/README.md)
  preserve raw records, seeds, manifests, exact executed source and dependency versions.
- [Next standard-bit ON/OFF proposal](research/STANDARD_BIT_PROPOSAL.md) is reviewed
  but not preregistered, implemented or launched. Archive coverage is its prospective
  primary endpoint; a validated fixed-consumption standard-bit kernel is required.

The noisy stored-fitness proof, exact-one-bit asymptotics, exclusive mediation,
and rare event gaps remain separate open questions in the
[claim ledger](research/CLAIMS.md). No new experiments are authorized by these
proposals or by publishing this repository.
