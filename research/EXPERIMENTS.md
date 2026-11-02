# Experiment protocol

## Before a run

Record:

- The claim ID being tested.
- The competing hypotheses and what observation distinguishes them.
- The exact algorithm variant and stopping event.
- The parameter grid, seeds or seed-generation rule, repetitions, timeout, and censoring rule.
- Whether the run is exploratory, tuning, or confirmatory.

Start with a smoke run. Do not scale a configuration that is censored, fails a declared semantic check, or writes incomplete output.

## Recorded-run format

`scripts/run_research.py` creates one directory containing:

- `manifest.json`: command, Git state, interpreter and dependency versions, timing, budget, source hashes, and model conventions.
- `results.json`: one record per independent trial plus an aggregate summary.
- `source_snapshot/`: the exact text/code/config inputs used by the run, including untracked experiment code.
- `working_tree.patch`: the tracked working-tree patch at run start.

The runner checkpoints JSON atomically after every completed trial, marks interrupted runs incomplete, and schedules configurations round-robin so a cutoff does not systematically finish one grid cell while omitting all others. It passes the earlier of the total deadline and `--max-trial-seconds` into each simulator, records which deadline caused wall-time censoring, and also supports sweep or generation limits as independent operation-count bounds.

## Analysis rules

- Report successful and censored trials separately.
- Include median and quantiles or the empirical distribution, not only mean and standard deviation.
- If censoring is nonzero, do not compute an unconditional runtime mean by dropping censored trials.
- Use log-log slopes only as exploratory diagnostics unless the tested range and uncertainty justify asymptotic language.
- If coefficients are fitted, evaluate predictive error on held-out configurations.
- When using paired seeds, analyze paired differences and say why pairing is valid.
- Preserve unexpected and negative results.

## Cloud execution

The runner is platform-neutral and can execute on RunPod after the repository and Python environment are installed. Cloud launch and termination are intentionally not automated yet because the repository contains no approved RunPod template, secret strategy, storage path, or spend ceiling.

Before enabling RunPod, add and verify:

- maximum concurrent pods;
- maximum dollars and maximum wall time;
- a persistent output/checkpoint volume;
- a watchdog that terminates stalled or completed pods;
- idempotent result download;
- cleanup behavior that never deletes the only result copy;
- a test using the cheapest suitable hardware.
