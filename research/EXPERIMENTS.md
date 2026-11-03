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
- `results.json`: one record per trajectory plus an aggregate summary; paired
  broadcast arms share a block and are not independent trials.
- `source_snapshot/`: the exact text/code/config inputs used by the run, including untracked experiment code.
- `working_tree.patch`: the tracked working-tree patch at run start.

The runner checkpoints JSON atomically after every completed trial, marks interrupted runs incomplete, and schedules configurations round-robin so a cutoff does not systematically finish one grid cell while omitting all others. It passes the earlier of the total deadline and `--max-trial-seconds` into each simulator, records which deadline caused wall-time censoring, and also supports sweep or generation limits as independent operation-count bounds.

## Exact/lazy factorial mode

`factorial-grid` uses the frozen protocol in `FACTORIAL_PREREG.md`. One raw trial
is one population trajectory with paired archive/alignment first-passage times;
two endpoints do not double the independent sample count. The passive archive
does not change transitions. Seeds are independent across mutation, radius, n,
and repetition. The full main command and exact sources are saved in each
manifest; the runner also accepts `--not-after-utc` as an absolute UTC deadline.

The raw `evaluations` field counts executed initialization/offspring evaluations.
`observation_evaluations` is the prefix confirmed before the wall deadline and
is the lower observation bound for a censored endpoint. A work unit that crosses
the deadline can make executed state counters advance without confirming an
endpoint event; it must not enlarge the right-censoring prefix. A completed
archive time stays valid if alignment later censors. `scripts/analyze_factorial.py`
preserves this distinction, rejects duplicate seeds, and resamples the two
endpoints together. Censored prerequisite cells yield inconclusive unconditional
mean contrasts rather than means based only on successes.

## Paired broadcast mode

`broadcast-grid` follows `BROADCAST_PREREG.md`: lazy q=1/2 ON/OFF only, with
separate identically seeded initialization/gate/direction generators within a
block, unconditional draws by absolute offspring index, and independent seeds
across (n,r,repetition) blocks. The manifest declares every planned block, seed
and arm order before execution. Round-robin blocks alternate arm order by
repetition parity within each n,r; every arm is checkpointed. Missing entire
blocks and partial/censored arms remain visible.

`scripts/analyze_broadcast.py` jointly resamples both arms and endpoints within
a block, independently across radii. Primary unconditional contrasts require
every planned arm complete and uncensored; no complete-case deletion. Primary
A1 and Delta use the frozen approximate nominal Bonferroni policy; secondary
phase/archive summaries remain pointwise. Target first hits are recorded only
within confirmed observation prefixes, including initialization. Observers draw
no random numbers. The completed 2026-11-03 study records 324 trajectories in
162 independent blocks (36/18 smoke; 288/144 inference), all uncensored; see
`reports/20261103T022831Z-broadcast-ablation.md` and its curated summary.

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
