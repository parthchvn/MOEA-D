# Start the five-hour local Codex research run

This workflow uses one Codex Goal as the coordinator and three project-scoped subagents: a sole-writing builder, an independent evaluator, and a read-only literature reviewer. Keep all agents in the same orchestrated session; do not open several writing sessions on this checkout.

## 1. Prepare and verify the local environment

From Terminal:

```bash
cd /Users/parth/Documents/ChatGPT/Transfer/MOEA-D
/Users/parth/miniforge3/bin/python -m venv --system-site-packages .venv
source .venv/bin/activate
codex --version
codex doctor --summary
python -m unittest discover -s tests -v
python -m py_compile sim.py large.py scripts/run_research.py
```

The `.venv` command is idempotent for this prepared checkout. It reuses the already installed NumPy and Matplotlib packages and does not need a network download.

## 2. Create a clean baseline

The prepared research harness is currently an uncommitted change. Put it on its own branch and commit it before the autonomous run so the morning diff contains only the agents' work:

```bash
git switch -c codex/moead-five-hour-audit
git add README.md large.py sim.py .gitignore AGENTS.md requirements.txt research scripts tests .codex
git commit -m "Add reproducible MOEA-D research harness"
git status --short
```

The final command should print nothing. Review the staged diff before committing if desired.

## 3. Start a detachable, sleep-resistant session

The Mac includes `screen` and `caffeinate`, so no additional terminal package is required:

```bash
cd /Users/parth/Documents/ChatGPT/Transfer/MOEA-D
pbcopy < research/FIVE_HOUR_GOAL.txt
screen -S moead-research
./scripts/start_local_codex.sh
```

When Codex opens, paste the clipboard contents and press Return. The `/goal` command starts the persistent five-hour objective. Use `/subagents` inside Codex to inspect the builder, evaluator, and literature-reviewer threads.

The launch script uses an isolated non-daemon Codex process with automatic approval review inside Codex's `workspace-write` sandbox. It starts an independent watchdog inside the `screen` session. At five hours it first sends an interrupt, gives active work 60 seconds to flush its atomic manifest, and then closes the session if Codex is still active. If Codex exits or fails to launch, the script cancels the watchdog so it cannot interrupt a later session. This is the hard wall-clock boundary; the Goal's own five-hour instruction is the graceful boundary.

Detach without stopping the run by pressing `Control-A`, releasing the keys, then pressing `D`. You may close the Terminal window after detaching, but keep the Mac connected to power and network with its lid open. `caffeinate` prevents idle sleep; it does not override normal lid-closed sleep.

## 4. Check, resume, or stop

Reattach later:

```bash
screen -r moead-research
```

If the Codex process exited but the task was saved, restart Codex from the repository and use `codex resume --last`. Inside Codex, `/goal` shows status, `/goal pause` pauses, `/goal resume` continues, and `/goal clear` removes the goal.

For an emergency stop from another terminal:

```bash
screen -S moead-research -X quit
```

After the run, inspect `git status`, the timestamped report under `research/reports/`, all recorded manifests under `research/runs/`, and the full diff before committing anything.
