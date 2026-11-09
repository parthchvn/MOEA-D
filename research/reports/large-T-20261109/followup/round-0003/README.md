**Independent audit passed.** The preceding n=512 study's receipts reproduce its
restricted-mean ratio **2.3390952207**, approximate nominal 95% percentile interval
**[2.0853866835, 2.5964682010]**. Both main arms have 32 observed exact endpoints,
zero capped trials and zero missing receipts. Four separate smoke trials also
complete and are excluded from inference. This is finite empirical support for
T=23 under the registered rule, with no upgrade to an unrestricted or asymptotic
claim. No new scientific trajectory was generated during this audit.

The [audit result](audit.json) contains the numerical findings, exact hashes,
phase denominators, exceptions, seed intersections and provenance checks.
[Cells](cells.csv) retain every original main/holdout arm and both follow-up
stages. [Trials](trials.csv) derive the follow-up values from all 68 terminal
JSON receipts. [Phases](phases.csv) give means, differences and intervals;
[seeds](seeds.csv) give exact-integer set intersections. Original receipts are
referenced by ID and remain in the committed prior checkpoints and evidence
archives; this bundle does not duplicate or alter them.

**Mechanically checked dependency and chronology.** The original registration
was committed in `88a67b4` at 20:24:32 UTC, before the pilot. The follow-up
registration was committed in `a5449de` at 21:26:18 UTC, before the round-2
manifest start at 21:29:55.393665 UTC. Full registration, freeze, plan, seed,
source and artifact bytes match their recorded hashes and Git ancestor.
The prior evidence has usable plans and receipts; no repair was needed.

**Mechanically checked seed separation.** The 68 follow-up seeds are unique
and disjoint from all 2,420 earlier published trial seeds, including 1,484
original campaign planned seeds and all 240 blocked holdout seeds. The two
follow-up arms and smoke/main stages are disjoint. An explicit qualification:
the original pilot and original campaign reuse 164 smoke/calibration seeds;
those are excluded from both primary effects and cannot be counted as fresh
replications. The pilot used GCC/libstdc++ on Linux; the campaign used
clang/libc++ on macOS. Different toolchains do not prove independent streams.
These checks cover published evidence, not inaccessible private trials.

**Mechanically checked censoring.** The original main has 1,080 receipts, 1,079
exact hits and one cap: n=64, T=1, f=1, ID `67178d8d2471ba15457b`. Its U=469,
but S and exact assignment are absent through H=3,206. The gate consequently
leaves all 240 original holdout trials missing, with no observed n=512 estimate.
Each holdout arm's restricted sample-mean identification bounds remain
[513, 19,669,446] evaluations, and the primary ratio bounds remain
[1/38342, 38342]; these are not confidence intervals. The original two-stage
decision remains inconclusive. The separate follow-up does not unblock it.
The earlier n=256 primary estimate also reproduces: 2.3276385563,
[2.0501481748, 2.6746419965], with 24 observed trajectories per arm.

**Empirically supported phase description.** At n=512 the T=1-minus-T=23 mean
differences are 4,462.40625 sweeps before U, 1,272.5625 from U to S, and 0.125
after S. All 32 observations per arm enter and complete each phase. U is the
first ideal observed-reference boundary; S additionally requires all stored
labels at their targets; P is the first true-exact boundary at or after S.
The first true-exact boundary X equals P in all 64 main receipts. Their total
mean evaluation difference is 2,942,103.09375, with joint-bootstrap interval
[2,607,666.77109, 3,260,761.05937]. Interval endpoints are not added across phases.

The one positive post-S delay is retained: T=1, repetition 20, receipt
`4e8a2113cf235be3cc1b`, U=6,951, S=11,204, X=P=11,208. It has one true/stored
mismatch of magnitude one at S. Both arms have zero recorded own/external
pinned-endpoint repairs. Thus savings are predominantly before S descriptively;
an assertion of literally zero post-S contribution would be false. These
observations do not identify causal mediation. T=23 saves 57.2484% of sampled
evaluations but uses 9.83155 times the logical recipient comparisons.

**Audit method.** [audit.py](audit.py) imports none of the earlier analyzers,
validators, plan generators or wrappers. It reads the published tar members
without extracting them, verifies hashes, reconstructs seed rules, and checks
event order, accounting and terminal conditions. It recalculates means from
integer totals, linear quantiles with independent order-statistic code, Wilson
intervals, and the frozen 10,000 within-arm PCG64 bootstrap resamples. Bootstrap
row multiplicities preserve joint phase observations. It matches 6,914
scalar/structural comparisons, maximum absolute numerical discrepancy
2.28e-13, with zero phase-identity residual. These counts are checks, not
independent observations. It also checks every original published endpoint
cell and completed-phase denominator, plus the original primary bootstrap.

For common horizon H, the audited occupancies are A=min(U,H),
B=min(S,H)-min(U,H), C=min(P,H)-min(S,H), G=min(P,H)-min(X,H).
They obey A+B+C=min(P,H) and init+(n+1)(A+B+C-G)=restricted exact evaluations.
An unentered phase has zero occupancy. Completed-duration summaries retain
their own selection-conditioned denominators. A hit exactly at H is observed;
a missing receipt is not a cap. [Synthetic tests](test_audit.py) exercise these
distinctions and reject corrupted or semantically inconsistent receipts.

**Analysis-only reproduction.** From the repository root after publication:

```sh
PYTHONDONTWRITEBYTECODE=1 python research/reports/large-T-20261109/followup/round-0003/audit.py --repo . --out /tmp/round3-audit
PYTHONDONTWRITEBYTECODE=1 python research/reports/large-T-20261109/followup/round-0003/test_audit.py
python -m unittest discover -s tests -v
python -m py_compile sim.py large.py scripts/run_research.py
```

Before publication, substitute `deliverables/` for the round-0003 directory.
Python 3.13.12 and NumPy 2.4.3 were used with one CPU/thread. The six regenerated
files `audit.json`, `inputs.json`, `cells.csv`, `phases.csv`, `seeds.csv`, and
`trials.csv` are deterministic. [Inputs](inputs.json) pins the published evidence
bytes. [Checks](checks.json) records test commands, execution durations, exact
replay, preservation, output hashes and this round's elapsed time. Raw logs
and restored source snapshots remain outside deliverables.

**Checks and limits.** All 95 repository tests, 14 registered tests, 15 wrapper
tests and 16 new audit tests pass. The original dependency audit reruns exactly.
The prior round's six analysis files, including its plot, replay byte for byte.
An initial new synthetic fixture omitted `factor`; that fixture was repaired
and all 16 tests rerun. No published data or algorithm repair was needed.

The round-2 engine receipts sum to 14.224490 seconds (13.801595 main); its
recorded invocation is 16.612791 seconds, including 1.265618 seconds compilation.
The start/end UTC fields span 16.365010 seconds. The 0.247781-second difference
is consistent with source code recording monotonic START before imports and
registration, and started_utc afterward. Per-trial timestamps and the private
invocation log were not published. Thus raw receipts verify the scientific
phase arithmetic; code, manifest and reported checks support execution order,
but they cannot independently establish the absence of unreported invocations.
This is a provenance limit, not an observed contradiction.

**Assumptions, proof gaps and falsifiers.** The process remains ascending cyclic
own-parent standard-bit mutation, activated bitwise observation noise, shared
stored labels, moving observed extrema, exact filled cardinality and
sweep-boundary true exact assignment. T is not a clipped radius. Independent
pseudorandom streams are assumed; distinct seeds alone do not prove independence.
Bootstrap coverage is approximate and pointwise. Restricted means do not order
unrestricted expectations or exclude rare tails. P=X in this sample does not
prove stopping-event equality. Donor corruption, joint repair/reinfection and
acceptance-conditioned noisy selection remain proof gaps in the supplied
evidence. No new candidate proof or literature/novelty claim is made offline.
For the registered R_H>1 conjecture, a lower interval endpoint <=1 fails its
support rule; an interval entirely below one opposes its direction. A P>X
receipt falsifies sample endpoint equality; substantial post-S savings would
challenge the predominantly pre-S description. The existing pathwise
nonmonotonicity and reinfection counterexamples remain unchanged.

The durable [memory supplement](memory.md) records C19/C20 without changing
their inferential scope. No new experiment or plan is introduced here; a future
T=3-versus-T=23 comparison requires a separate plan published before measurement.
