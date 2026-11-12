This bundle records the **completed, separate prospective n=512 study** specified
in the published round-1 checkpoint. It preserves the original preregistration and
blocked holdout. No original holdout seed was run. The original two-stage decision
remains inconclusive.

The main result is **empirically supported**: the fixed-horizon restricted-mean
evaluation ratio T=1/T=23 is **2.339095**, nominal 95% percentile bootstrap
**[2.085387, 2.596468]**. All 64 main trials and four separate smoke trials have
valid receipts; none is capped or missing. See [details](details.md),
[summary](summary.json), [cells](cells.csv), and the [figure](results.png).

The [plan](plan.json) and [seed table](seeds.csv) are unchanged copies of the
registered artifacts. The registration commit is
`a5449deed0c45f4ff0538fe49d0fa6285a77b809`, already present before measurement.
Its checkpoint directory is
`research/reports/large-T-20261109/followup/round-0001`.
[Registration verification](registration.json) binds every published file to
that commit. The [dependency audit](dependency.json) exactly reproduces the
round-1 audit of the earlier evidence and seed separation. No prerequisite
repair was needed.

The [manifest](manifest.json) binds the complete 68-row plan, source bytes,
compiler, standard-library macros, binary hash, command, deadlines, Git dirty
state, pre-draw tests, one-worker policy, and model conventions. The
[terminal status](status.json) records completion in 16.612791 seconds.
[trials.csv](trials.csv) contains all planned rows and their receipt hashes,
observations, work counters, and derived restricted values. The corresponding
full JSON receipts are in `rows/`, named by their `id` column. Read seed integers
as decimal strings or arbitrary-precision integers; a spreadsheet float can
round these 64-bit values.

**Analysis-only reproduction, with no sampling.** Python 3.13.12, NumPy 2.4.3,
and Matplotlib 3.10.8 were used. From this bundle directory, choose a fresh
temporary directory:

```sh
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 python reproduce.py --out /tmp/round2-replay
```

[reproduce.py](reproduce.py) checks [artifact hashes](checksums.json), restores
the exact source snapshots, revalidates all receipts using the unchanged
registered analyzer, and regenerates summary, CSVs, numerical audit and plot.
It never invokes an engine. On this host all six regenerated result files are
byte-identical. Numeric replay is checked separately from PNG replay because
font/Matplotlib versions may change pixels. [checks.json](checks.json) records
the observed validation, timing and scope.

To obey the requested artifact-extension restriction, the exact UTF-8 C++ and
Python source snapshots are stored losslessly as a path-to-text map in
[sources.json](sources.json). Each decoded byte sequence must match its SHA-256
in the manifest. Reproduction materializes the C++ file at
`/tmp/round2-replay/run/source/scripts/neighborhood_sweep.cpp`; it also restores
the registered `plan.py`, `analysis.py`, tests, preregistration, freeze and report
at their original relative paths. Thus no model source is omitted, and no
source PDF is included or modified.

**Runnable measurement implementation.** [run.py](run.py) is the exact wrapper
used, with [test_run.py](test_run.py) covering gates, capped smoke, valid capped
main trials, early exact assignment, cutoff, interrupts, source tampering,
unknown fields and duplicate receipts. It requires a research checkout with
the committed registration, passing pre-draw checks, unchanged frozen model,
a new output directory and a persistent unused invocation marker. It uses one
serial C++ process with C++17/O3; no worker pool or cloud resources. Its exact
executed command is in the manifest. **This registration's one sampling
invocation is consumed. Do not remove its marker or resume sampling.** Further
scientific trials need a separately published prospective plan.

The wrapper writes complete receipts atomically with fsync. A terminated child
has no durable event prefix and is missing, never a fabricated capped result.
Completed receipts survive failures; main is blocked unless all four smoke
receipts finish at their post-S endpoint. A valid administrative main cap would
be retained without stopping other trials. Missing main receipts suppress the
primary estimate/CI and produce the registered sample identification bounds.
These behaviors were tested with synthetic outputs, not prospective seeds.

[package.py](package.py) exports a raw completed or partial run into the
permitted formats. [summarize.py](summarize.py) calls the unchanged registered
analysis, produces presentation artifacts and performs a separately coded
arithmetic audit. These two presentation scripts were written after sampling;
they are covered by artifact hashes rather than retroactively added to the
frozen measurement-model hash. No raw private log is included.

All links within this bundle are relative. [memory.md](memory.md) is the durable
claim/status supplement; local `research/STATUS.md` and `research/CLAIMS.md`
were also updated. No commit or push was performed.
