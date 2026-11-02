# Research status

Last structured audit: 2026-11-02.

## Current state

- The repository has two executable models and an exploratory notebook.
- Basic noiseless properties pass small finite checks: unique scalarization minimizers, reciprocal radius neighborhoods, deterministic seeded runs, and convergence on a smoke set.
- The included noisy `T=1` draft is not yet a complete proof. The most important gap is conditioning on accepted stored noisy values.
- The larger-neighborhood runtime law is a well-formed conjecture with suggestive simulations, but no proof document is present.
- A preprint posted on 2026-10-26 directly studies MOEA/D solution exchange on OneMinMax. It proves `Theta(n^2)` evaluations for every communication radius `r >= 1` and `Theta(n^2 log n)` for `r = 0` in its model. This is in tension with the repository's claimed logarithmic threshold.
- The most important identified model difference is mutation: the preprint's quadratic upper-bound class requires a constant probability of producing a same-Hamming-weight offspring, while exact one-bit mutation always changes the Hamming weight by one. This is a sufficient-condition gap, not evidence by itself of a slower runtime. The preprint also measures archive coverage, while `large.py` waits for simultaneous subproblem alignment.
- The whole-process invariant `(J)` is contradicted at initialization. The code's checks after sweep 2 concern only a possible post-burn-in property.
- The recorded-run harness now checkpoints after every trial, enforces separate per-trial and total deadlines, uses balanced round-robin configuration order, and snapshots source files and dependency versions.
- There was previously no environment specification, test suite, experiment manifest, claim ledger, or long-run protocol.

## Highest-value next question

Determine whether `large.py` implements the same stochastic process and runtime event as Doerr, Elmoutassim, Krejca, and Kibulu (2026). Compare, at minimum:

1. archive coverage versus simultaneous exact subproblem alignment;
2. one-bit versus standard-bit or general mutation;
3. uniform versus cyclical breeder selection and the repository's sweep update order;
4. whether offspring are communicated after acceptance only or offered independently to all neighbors;
5. radius and boundary conventions;
6. tie acceptance, reference point, scalarization orientation, and initialization.
7. self-parent mutation in `large.py` versus neighborhood-parent selection in `sim.py`.

If the models coincide, reproduce the paper's `r = 1` behavior and retire C3/C4. If they differ, isolate the smallest difference that produces the apparent threshold and state a genuinely novel question.

An initial comparison is recorded in `research/PAPER_COMPARISON.md`. Current evidence says the models do differ, so the immediate objective is to distinguish the effect of the missing weight self-loop from the effect of archive versus simultaneous-alignment stopping. The five-hour study must remain noiseless and controlled.

## Exploratory radius diagnostic

An uncommitted, machine-recorded smoke grid used `n in {50,100,200}`, `r in {0,1,4}`, and eight independent repetitions per configuration. It had no censoring. Mean sweeps for `r=1` were `94.6`, `175.3`, and `526.1`; for `r=4` they were `65.4`, `131.8`, and `382.6`. This confirms a finite-size benefit from communication and from increasing the radius, but the range and variance are far too small to distinguish linear from `n log n` behavior. The run is stored locally under `research/runs/20261102T204129Z-large-grid-radius-diagnostic/` and is intentionally ignored by Git.

## Suggested bounded work packages

### A. Canonical-model reconciliation

- Produce the line-by-line comparison with the October 2026 preprint.
- Write one mathematical algorithm matching one implementation line by line.
- Map ideal-point and weight orientations across the draft, notebook, and scripts.
- Define the neighborhood parameter at endpoints.
- Choose one primary stopping event and explicitly label all alternatives.

### B. Noisy drift audit

- Enumerate the augmented state `(true weight, stored value)` for one extreme subproblem.
- Derive exact transition probabilities including acceptance.
- Compute conditional drift for every reachable state for small `n` and symbolic `p` where feasible.
- Test whether a one-dimensional potential can work; otherwise design a phase or two-dimensional potential.

### C. Noiseless neighborhood theorem

- If useful, formulate and test a new post-burn-in replacement for the contradicted whole-process invariant `(J)`.
- Separate endpoint hitting time, interior alignment, and simultaneous completion.
- Define effective neighborhood size by radius or minimum cardinality before stating asymptotics.
- Preregister scaling grids that discriminate candidate laws.

## Decision rule

Do not begin the noisy `T > 1` theorem until A is complete and the overlap with the October 2026 result is understood. Exploratory experiments are allowed when they directly distinguish the two processes or choose between proof strategies.

## Morning-report template

- Question attempted:
- Result and status label:
- Evidence produced:
- Counterexamples or failed approaches:
- Files changed:
- Commands/runs and elapsed time:
- Cloud cost, if any:
- Remaining uncertainty:
- Best next action:
