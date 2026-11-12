# Round 20 recovery and RORR audit

**Proved, restricted model:** the baseline and both entrance factors justify the candidate RORR bound, in sweeps, for even n≥4 and supplied pinned T=2. [audit.md](audit.md) contains the assumptions and derivation. The complete fourth-order gap and a uniform finite-noise remainder remain unresolved in this project.

| File | Role |
|---|---|
| [audit.md](audit.md) | Fresh-context analytic audit, contradictions, missing inputs and scope |
| [HISTORY.md](HISTORY.md) | Index of every published follow-up round 1–19, including negative results |
| [memory.md](memory.md) | Proposed claim/status updates; existing project files were not edited |
| [PROGRESS.md](PROGRESS.md) | Durable checkpoints, including unfinished stages |
| [recovery.json](recovery.json) | Inventory hash/length verification, duplicate copies and missing WIP receipts |
| [audit.py](audit.py), [test_recovered.py](test_recovered.py) | Byte-identical recovered solver/test sources, explicitly reused |
| [check.py](check.py), [targeted.json](targeted.json) | New independent source/schema/geometry checks, exact finite scope |
| [verification.json](verification.json) | Fresh bounded exact-run counts, distinct from missing WIP receipts |
| [words.csv](words.csv), [baseline.csv](baseline.csv) | Fresh exact word/baseline fingerprints and rounded presentation values |
| [phases.csv](phases.csv), [entrances.csv](entrances.csv), [branches.csv](branches.csv) | Fresh phase, joint-entrance and separate positive-kernel checks |
| [reproduce.py](reproduce.py) | Future serial bounded reproduction; no recursive earlier-grid replay |
| [checks.json](checks.json), [provenance.json](provenance.json), [preservation.json](preservation.json) | Actual verification receipts, hashes, timing and unchanged-source record |

**Recovery attribution.** The six original files are preserved under [the activation's recovery folder](../activation-20261112T181239Z-84cbf5/recovery/round-0020-cb372b60/README.md). The audit.py source SHA-256 is `2f2e5f84d5b6c69f9043bf23ab1f8a3396ee826b4f96e5aad0debbadef78e36a`; test_recovered.py is the original test_audit.py, SHA-256 `0ef9dd3136662a02d94baefe3853d9f8241e5cd6c30b9d3dbe14214bee23eed7`. Neither was newly authored for this activation. The original reproduction wrapper was not run: it would replay empirical dependencies unnecessarily. Its claims of completed outputs were not treated as evidence.

The code uses exact Fraction arithmetic for decisions; decimals are presentation only. Fraction fingerprints hash str(Fraction); tuple fingerprints use the corresponding tuple string. Published n=4,6 round-19 results were reused after 30 round-18/19 artifact hash checks and explicit table key/coverage/schema checks. Fresh response verification uses every phase, regular target, child and orphan value from both corner/aligned origins at n=4. The n=6 published exact result is reused after manifest/schema verification; a fresh n=6 run was deliberately interrupted before completion to bound redundant work, and supplies no new certified grid. This is not a full population-state enumeration. Independent support checks enumerate 55,939 regular configurations at n=4,6,8 through three generic overwrites, plus marked descendants and second births. No finite grid proves the all-n theorem.

**Reproduce after publication**, starting in this bundle's directory (the commands also work in its staging directory):

```sh
REPO_ROOT=$(git rev-parse --show-toplevel)
PYTHONDONTWRITEBYTECODE=1 OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 VECLIB_MAXIMUM_THREADS=1 NUMEXPR_NUM_THREADS=1 /Users/parth/miniforge3/bin/python3 reproduce.py --repo "$REPO_ROOT" --out "$REPO_ROOT/research/runs/round20-audit-replay-new" --seconds 1800
```

Choose a fresh scratch output name. The wrapper verifies recovery hashes/manifests and schema/support, runs the 17 recovered tests and repository suite, compiles relevant modules into scratch cache, then executes only the bounded n=4 response grid. It compares all seven deterministic output files to this bundle when present. Logs/caches stay in scratch. Tests and scientific computations run serially with one numerical thread; no Monte Carlo samples or seeds are created. The special exact harness is needed because run_research.py generates trajectories, not signed phase-response equations.

**Units and exclusions.** Initialization is free in this supplied-state analysis. Reward 1/(n+1) per attempt defines sweep units, and stopping is simultaneous true alignment at phase zero. This is not archive coverage, first interior alignment, or ordinary random initialization. The word bound supplies neither a tail nor a fixed-positive-c ordering. Earlier finite experiments and the blocked original holdout are cited in HISTORY.md and were not sampled or fully replayed again. Novelty is UNVERIFIED; no external search or theorem transfer is claimed. The next lane is larger T.

Relative links to earlier rounds are designed for publication beside their original round directories; they intentionally refer to those reports rather than copying their artifacts.
