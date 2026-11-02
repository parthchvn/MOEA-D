# Research agent instructions

## Mission

Advance the mathematical and empirical understanding of MOEA/D on OneMinMax. Optimize for correctness, reproducibility, and useful negative results. A plausible plot is not a proof, and a proof sketch is not an implemented experiment.

## Durable project memory

Read these files before substantive work:

1. `research/PROJECT.md` for the model and terminology.
2. `research/CLAIMS.md` for what is established and what remains open.
3. `research/STATUS.md` for the current frontier.
4. `research/EXPERIMENTS.md` before running or changing experiments.
5. `research/LITERATURE.md` before claiming novelty or transferring a theorem.
6. `research/PAPER_COMPARISON.md` before working on communication-radius claims.

Update `research/STATUS.md` after a meaningful work unit. Update `research/CLAIMS.md` whenever evidence changes a claim's status. Never silently upgrade an empirical claim into a theorem.

## Agent roles

For explicitly requested parallel work, use independent roles with one coordinator:

- The builder may edit code, tests, and research notes.
- The evaluator is read-only until it has written an independent critique of the builder's result.
- The literature reviewer searches for primary sources, records exact theorem assumptions, and explains whether they transfer to this model.
- The coordinator reconciles disagreements and decides the next bounded step.

Only one agent may edit a given checkout at a time. Give simultaneous implementation agents separate Git worktrees. Evaluators should not share the builder's unstated assumptions.

## Research integrity rules

- Label every substantive statement as proved, mechanically checked, empirically supported, conjectured, contradicted, or open.
- State the exact stochastic process, filtration, conditioning event, potential, and stopping time before applying a drift theorem.
- Do not infer a tail bound from an expectation bound.
- Do not infer a bound on a maximum of random variables from their individual means without a justified tail or dependence argument.
- Distinguish first hitting, eventual historical coverage, archive coverage, and simultaneous coverage by the current population.
- Treat conditioning on acceptance or on a stored noisy value as selection-biased unless proved otherwise.
- Search for counterexamples at small `n` before attempting a general proof.
- Preserve failed hypotheses and counterexamples in the claim ledger.
- Cite primary literature with authors, title, year, and DOI/arXiv identifier when available.
- Search for work newer than the repository before calling a question open. The October 2026 communication-radius preprint is directly relevant and must be compared against the implemented process.
- Do not modify the source PDFs.

## Model conventions that must not be conflated

- In `sim.py`, `T` is a requested neighborhood cardinality constructed by alternating left and right choices. Even `T` can produce non-reciprocal choices.
- In `large.py`, `r` is a symmetric radius. Interior cardinality is `2r + 1`, while endpoint cardinality is `r + 1` after clipping.
- The draft and scripts use different ideal-point and weight orientations. Prove equivalence or document the transformation before transferring a result.
- `front_covered(pop)` means simultaneous coverage by the current population. Earlier notebook cells also use historical coverage; these are different stopping events.
- In noiseless `large.py`, a target hit is absorbing because the target is the
  unique scalarization minimum. Do not transfer that persistence claim to the
  noisy stored-fitness process or to a different replacement rule.

## Experiment protocol

- Use `scripts/run_research.py` for recorded grids unless a different harness is justified.
- Record the Git commit, dirty state, command, seeds, censoring, elapsed time, and model conventions.
- Start with a smoke grid, inspect censoring and invariants, then scale.
- Use independent seeds across configurations. Use paired seeds only when the analysis explicitly uses pairing.
- Report distributions, censoring, and uncertainty; do not report only means.
- Do not tune a law and evaluate it on the same grid without saying so.
- Generated results belong in `research/runs/` and are ignored by Git. Commit only curated summaries that are needed for a paper or decision.

## Overnight boundaries

- Work from one explicit `/goal` with a measurable finish condition and a time or token budget.
- Prefer a sequence of small falsifiable questions over broad "improve the research" prompts.
- Do not push to GitHub, create paid cloud resources, or start RunPod jobs without explicit authorization and a spend/time ceiling.
- If RunPod is authorized, cap concurrent pods, set a hard termination time, persist checkpoints/results before shutdown, and stop on repeated infrastructure failures.
- Never loop merely because improvement is possible. Continue only when the latest evidence identifies a distinct next experiment or proof obligation.
- End with a morning report covering results, failures, changed files, costs/runtime, unresolved risks, and the best next action.

## Verification commands

```bash
python -m unittest discover -s tests -v
python -m py_compile sim.py large.py scripts/run_research.py
```

Use the environment's configured Python if the default interpreter lacks NumPy or Matplotlib.
