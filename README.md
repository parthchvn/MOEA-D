# MOEA/D runtime experiments on OneMinMax

This repository studies how MOEA/D behaves on the bi-objective OneMinMax benchmark under one-bit mutation, with particular attention to neighborhood sharing and one-bit prior noise without reevaluation.

The project currently contains two related, but not identical, models:

- `sim.py` simulates full bit strings under one-bit prior noise. Its neighborhood parameter `T` is the requested number of subproblems in each neighborhood.
- `large.py` uses an exact Hamming-weight state reduction for the noiseless model. Its parameter `r` is a symmetric neighborhood radius, so an unclipped interior neighborhood has size `2r + 1`; boundary neighborhoods are smaller.

Do not compare their `T` values or stopping times without first reconciling these conventions. The main noiseless runtime law in `large.py` is presently a research claim with empirical support, not a completed proof in this repository.

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

## Current research priorities

1. Compare the implemented process line by line with Doerr, Elmoutassim, Krejca, and Kibulu's October 2026 communication-radius preprint, which proves a quadratic runtime for every nonzero radius in a closely related model.
2. Fix a canonical MOEA/D definition and reconcile archive versus simultaneous coverage, mutation, update order, target orientation, ideal-point notation, and neighborhood size across the literature, draft, notebook, and scripts.
3. Audit the noisy `T=1` proof, particularly conditioning on accepted noisy values, tail bounds for the maximum over subproblems, and simultaneous versus historical Pareto-front coverage.
4. Establish what, if anything, remains novel about the noiseless runtime conjecture before extending it to noisy neighborhoods.
