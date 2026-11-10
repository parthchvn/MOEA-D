# Run the larger-neighborhood study on your Mac

This checkout runs an interactive Codex session and a single benchmark worker in tmux. The study varies recipient cardinality T under standard bit mutation and activated bitwise prior noise. The baseline uses T=1 with the same parent, reference, selection, initialization and endpoint definitions as every larger arm.

## Launch

From Terminal, use a separate checkout so you can keep working in your usual MOEA-D tree.

```bash
cd "$HOME" &&
git clone --single-branch --branch research/larger-neighborhoods-20261109 \
  https://github.com/parthchvn/MOEA-D.git MOEA-D-large-T &&
cd MOEA-D-large-T &&
bash scripts/start_neighborhood_tmux.sh --agent-now
```

For an existing campaign checkout, use `cd "$HOME/MOEA-D-large-T" && bash scripts/start_neighborhood_tmux.sh --agent-now`. A live session reattaches with its original deadline. Starting after that session ends gives a fresh time budget and resumes the frozen seed plan. Use the same checkout, scientific source and toolchain. The launcher defaults to **five hours per new activation**. Set a different budget at launch, e.g. `--seconds 28800` for eight hours. Add `--detach` for a background launch. With `--agent-now` Codex starts proof/counterexample work while the worker runs. Omitting it starts Codex after evidence preparation or a worker failure.

The machine needs Git, a configured Git author identity, tmux, a signed-in Codex CLI, a C++17 compiler, and Python 3.11+. On a Mac with Homebrew, `brew install tmux` supplies tmux and `xcode-select --install` supplies the compiler if needed. The wrapper finds Miniforge at `$HOME/miniforge3/bin/python` or accepts `MOEAD_PYTHON=/path/to/python`. A regular launch creates a local Python environment if NumPy or Matplotlib is missing. The push targets the named experiment branch of `parthchvn/MOEA-D` and needs Git credentials with write access. If using GitHub CLI for HTTPS credentials, run `gh auth login` and `gh auth setup-git` before leaving the run unattended. You can verify push credentials for this checkout using `git push --dry-run origin HEAD`. Sign into Codex with `codex login` if necessary.

An optional `bash scripts/start_neighborhood_tmux.sh --check` checks tools, existing Python dependencies, the dedicated checkout and a disposable tmux session. To use this check before the first normal launch, install requirements into your chosen Python environment first.

## During the session

| Action | Command or key |
|---|---|
| Detach; return to your terminal | Ctrl-b, release, then d |
| Return to Codex | `tmux attach -t moead-large-T` |
| Choose the worker, agent or clock window | Ctrl-b, then w |
| Read progress from another terminal in the checkout | `tail -f research/runs/larger-neighborhoods-20261109/worker.log` |
| Stop this activation | `tmux kill-session -t moead-large-T` |
| Recover a pending publication after fixing Git credentials | `bash scripts/start_neighborhood_tmux.sh --publish-only` |

The clock window keeps an awake Mac from idle system sleep with `caffeinate -i`. Keep the machine awake and available, including the lid position, for an unattended run. The sampling cutoff reserves time for reporting and review. The worker commits generated reports, plots, compressed raw receipts and the finished Codex interpretation to the experiment branch. Each interpretation names the exact campaign index by SHA-256. On resume an older interpretation only applies to its named packet. The publication retry verifies the packet and only publishes a new interpretation with a matching digest. A non-fast-forward push keeps evidence local; fetch and inspect the branch before retrying. On interruption, completed receipts survive, and the interrupted trajectory is retried with the same seed. If the holdout gate blocks, a partial report identifies the unobserved cells. Running out of time does not convert an unfinished proof into a theorem.

## Design and outputs

Read [the model and statistical plan](LARGER_NEIGHBORHOODS_PREREG.md), [the T=1 and corner theory](LARGE_T_THEORY.md) and [the agent brief](LARGE_T_AGENT.md). The main grid requests 1,080 independent trajectories over n=64,128,256. A further 240 trajectories at n=512 are reserved for independent validation. The primary ratio compares mean first true exact-assignment evaluations at T=1 with the mean at ceiling(sqrt(n)), with p=1/(64n). Both directional intervals must clear 1 to call the effect replicated. Full broadcast adds n+1 recipient comparisons per evaluation. Stopping times for front coverage, archive, reference and true assignment are recorded separately.

The [published pilot](reports/large-T-20261109/pilot/report.md) contains a smoke grid, a fixed-sweep timing calibration and a check against the exact noiseless corner law. The local worker repeats smoke and calibration on your hardware. New plots, summary CSVs and report are written to `research/reports/large-T-20261109/campaign/`, raw archives to `research/evidence/large-T-20261109/campaign/`, and the mathematical interpretation to `research/reports/large-T-20261109/interpretation.md`. Each trial records the frozen seed, event times, units and a model signature. Each stage archives scientific source and toolchain information. Raw elapsed times depend on hardware.

## Reproduce the published pilot

From the checkout, use a Python interpreter with the repo requirements installed. The destination for unpacking must be new.

```bash
packet=research/evidence/large-T-20261109/pilot
replay_dir=$(mktemp -d)
python3 scripts/package_neighborhood_evidence.py verify --packet "$packet" &&
python3 scripts/package_neighborhood_evidence.py unpack --packet "$packet" --out "$replay_dir/raw" &&
python3 scripts/analyze_neighborhood_campaign.py \
  --runs "$replay_dir/raw/smoke" "$replay_dir/raw/calibrate" --out "$replay_dir/report"
```

Use `.venv/bin/python` instead of `python3` if the launcher created that environment. The same commands work for `campaign/` with whichever stages its index records. Read the [compact raw-data index](evidence/large-T-20261109/pilot/INDEX.json) to verify stage totals and SHA-256 digests. Use the version of the analysis script identified by the index when reproducing an earlier report.

## Continue researching after the first interpretation

Once the campaign packet and its matching interpretation are committed, the same `--agent-now` command starts a five-hour follow-up in a separate tmux session named `moead-large-T-research`. Re-launching while that session is active reattaches with its original deadline. The original experiment has one censored main trial and its frozen holdout is blocked. The follow-up uses a new study design and seeds. The first round publishes its plan before any new measurement. Later rounds execute the plan, audit the receipts, work on the fixed-T noisy corner theorem and try to falsify the argument. Following rounds take a concrete open question from the preceding checkpoint.

Each round uses a fresh noninteractive Codex process in an isolated local clone. Completed outputs are pushed to `research/reports/large-T-20261109/followup/round-NNNN/` on the same branch. `report.md` records the observations, gaps and next task. Candidate proofs require independent scrutiny. A completed turn automatically starts the next task. The supervisor stops at the deadline, on a documented exhausted agenda after the initial tasks, or on an unresolved execution, validation or publication error. A failed Codex execution receives one retry when time permits. Completed local checkpoints are republished on restart. The most recent unfinished clone, model log and drafts remain under `research/runs/larger-neighborhoods-20261109/followup/`. If a turn times out before completing its checkpoint, that round starts again on a new activation.

To monitor outside tmux, use `tail -f research/runs/larger-neighborhoods-20261109/followup/supervisor.log`; each round prints the path to its detailed Codex log. To stop the follow-up, use `tmux kill-session -t moead-large-T-research`.

If Codex produced its final response but packaging failed, use the round directory printed in its log:
`bash scripts/start_neighborhood_tmux.sh --recover-round round-0008-52118af1` (substitute your round ID).
This rebuilds the checkpoint from the saved deliverables and final response and pushes it. It does not invoke Codex.
Research-supplied `provenance.json` keeps its original contents. Supervisor metadata for new checkpoints is in
`.checkpoint.json`. Repeating recovery after a successful push is idempotent. A subsequent `--agent-now`
activation takes the next task with a fresh time budget.
