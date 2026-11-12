# Prospective n=512 low-noise cardinality comparison

**Preregistered specification; outcomes unmeasured.** Study ID:
`large-T-512-low-noise-prospective-20261109-r1-v1`. Prepared in follow-up round 1,
2026-11-09, from commit `4f0d9533e1e6fa30e2da9eae14cb75956762f2b5`.
Publication by the supervisor in a committed round-1 checkpoint must precede
every new smoke or main outcome. This round draws neither. The scientific
question is whether T=23 reduces the **fixed-horizon restricted mean** first
true exact-assignment evaluation cost relative to T=1 at n=512 and p=1/(64n).

The machine-readable [plan](plan.json), [seed table](seeds.csv), deterministic
[generator](plan.py), [reference analysis](analysis.py), and [synthetic tests](test_plan.py)
are part of this registration. [freeze.json](freeze.json) binds their bytes.
The measurement wrapper will be implemented and tested in the subsequent round;
it must obey the interface and gates below. No measurement command has been run.

**Empirically supported motivation, with a mechanically checked dependency.**
The [published interpretation](../../interpretation.md) reports n=256 low-noise
means 1,165,698.458 versus 500,807.333 evaluations for T=1 and T=16, respectively:
ratio 2.3276385563, pointwise nominal 95% interval [2.0501481748, 2.6746419965],
24 independent trajectories per arm. In both arms every recorded post-S delay
and pinned-endpoint repair count was zero; the observed difference was before S.
[audit.py](audit.py) checks the packet signatures, receipt invariants, original
plans and primary arithmetic; its reproducible result is [audit.json](audit.json).
No earlier follow-up checkpoint exists at the input commit. No missing-plan or
missing-receipt repair is required for this dependency.

The original n=64,T=1,f=1 capped receipt `67178d8d2471ba15457b` blocks all
240 original holdout trajectories. Those are **missing**, not capped outcomes.
The [original preregistration](../../../../LARGER_NEIGHBORHOODS_PREREG.md), gate,
seeds, receipts, cap and inconclusive two-stage decision remain unchanged.
This is a new prospectively registered comparison selected after seeing the
published campaign. It cannot retrospectively validate that campaign's blocked
replication or turn an unrestricted hypothesis into a confirmed restricted one.
Neither the old n=256 observations nor the old planned n=512 seeds enter the
new estimate. No unobserved n=512 result is assumed in choosing this design.

**Fixed design and stopping rules.** f denotes p*n. All numbers below are fixed;
there is no sample-size re-estimation, arm selection or cap extension.

| Stage | n | T | f | Repetitions per arm | Sweep cap | Purpose |
|---|---:|---|---:|---:|---:|---|
| Smoke | 32 | 1,23 | 1/64 | 2 | 10,742 | Local implementation/invariant gate only |
| Main | 512 | 1,23 | 1/64 | 32 | 38,341 | Sole inferential comparison |

The main cap is the original size-specific horizon ceil(12*n*ln(n+1)), fixed
numerically at 38,341 sweeps. It corresponds to 19,668,933 offspring attempts
and 19,669,446 evaluations including initialization. The smoke cap is
ceil(96*32*ln(33)). Thirty-two main trajectories per arm are a fixed precision
choice, twice the old holdout count; this is not a power guarantee or a fitted
sample-size calculation. Smoke is excluded from all main intervals.

Execution is serial on one local CPU, with no worker pool, GPU or cloud. After
implementation tests and the publication gate, allow **one measurement invocation
of at most 1,800 seconds**, timed monotonically from wrapper startup and including
compilation, smoke, main, and receipt writes. A shorter externally imposed
remaining-turn deadline wins. No per-trial wall cutoff, retries, resume, or
second measurement invocation is authorized by this plan. A cutoff, interrupt,
invalid receipt, or engine failure ends that invocation; preserve completed
receipts, mark unrecorded trials missing, and report partial work. Do not substitute
seeds. Further sampling would need a separately published prospective amendment.
This conservative failure policy avoids unrecorded restarts or changing the budget
after seeing outcomes. Analysis may be rerun without sampling.

Run smoke first. All four smoke receipts must pass validation and reach post-S
exact assignment by their cap. A failed/capped smoke blocks main; report it,
without adjusting parameters to rescue this registration. Main stops after all
64 receipts, the fixed wall deadline, or an integrity/technical failure. A valid
main cap is **not** a failure and does not block remaining trials. Early exact
assignment does not stop a trajectory: continue until its first exact boundary
at or after S, or its sweep cap. No efficacy/futility checks, confidence-interval
peeking, or completion-rate criteria may stop or enlarge main.

For each stage, visit repetitions in ascending order. Even repetitions run T=1
then T=23; odd repetitions run T=23 then T=1. These are independent runs, not
paired observations despite alternating order. The complete 68-row manifest
must exist durably before the first smoke draw.

**Exact stochastic process and observation convention.** Retain the committed
`scripts/neighborhood_sweep.cpp` source with SHA-256
`11bdbd26facb39b22df911d063e1718dd03a2ae8fd01a18458d1c5e8f694df10`.
Use C++17 and `-O3`, `std::mt19937_64`, and the engine's existing binomial and
Bernoulli routines. Record actual compiler, standard-library macros, architecture,
binary hash, Python/NumPy versions and flags; different C++ libraries need not
produce bit-identical paths. The estimand is distributional under the specified
transition law, with pseudorandom adequacy and independence across distinct seeds
assumed. Distinct seeds are not a mathematical proof of independent RNG streams.

Initialize n+1 independent Binomial(n,1/2) true weights, observe each once, and
store its observed weight b[k]. Mutation flips each bit independently with
probability 1/n. Each observation, including initialization and zero-flip
mutation, has an independent activation gate of probability p=f/n; if activated,
each bit of the true candidate is flipped independently with probability 1/n
for observation only. Incumbents are never reevaluated. Use one observation
per proposal, shared among all recipients. At n=512, p=1/32768 exactly.

Visit breeders 0,...,n repeatedly and mutate the current breeder's **own**
incumbent. Update observed extrema lo,hi using every candidate, even one later
rejected. Compare candidate c and stored b at recipient k using the same updated
cost max{k*(hi-b),(n-k)*(b-lo)}. Replace on a non-worsening comparison, including
ties, regardless of the breeder's acceptance. The true candidate and stored
observed label move together. There is no supplied ideal point or corner state.

B_T(i) starts with i; at each increasing distance add in-range right then left
for even i, left then right for odd i, until exactly T recipients are included.
At edges fill inward rather than clipping cardinality. For these odd arms the
recipient interval is [clamp(i-floor((T-1)/2),0,n+1-T), start+T-1]. In particular
B_23(0)={0,...,22}; this is not the clipped-radius-11 process. No neighborhood
parent sampling, adaptation, reevaluation, or alternative scalarization is used.

Boundary 0 follows initialization; subsequent boundaries follow complete
n+1-attempt sweeps. Let X be the first boundary with every **true** slot weight
w[k]=k; U the first boundary with lo=0,hi=n; S the first boundary with this ideal
reference and every **stored** b[k]=k; and P the first truly exact boundary at or
after S. Absent events are infinity. X and S are not ordered. U<=S<=P and X<=P.
Also record first current-front coverage and passive all-initial/all-generated
true-weight archive coverage at boundaries; these are different from X and from
per-offspring historical first hits. No persistence of true assignment under
stored noisy selection is assumed. The natural filtration reveals initialization
and every consumed proposal/noise draw through each completed sweep; all four
events are stopping times for this boundary filtration. No drift theorem or
conditioning-on-acceptance argument enters this design.

**Fresh seeds, fully enumerated.** `plan.py` is the authoritative generator.
Canonical JSON means UTF-8, sorted keys, compact comma/colon separators and no
NaN. For a row's configuration c (stage,n,T,factor,mutation,noise,init,reference,
max_sweeps,rep), token=SHA256(JSON([study_id,"trial",c])); id is its first 20 hex
digits. The unsigned 64-bit seed is the first 16 hex digits of
SHA256(JSON([study_id,"seed",token])), interpreted in base 16. The JSON and CSV
store exact decimal integers; never round them through a spreadsheet float or
JavaScript Number. All 68 seeds are distinct and disjoint from the 2,420 unique
trial seeds in published packets, including all 1,484 planned cardinality seeds
and the blocked holdout. Pilot/campaign duplicate seeds are counted once in this
exclusion set. This audit covers published evidence, not inaccessible private runs.
There is no search for favorable seeds and no seed pairing between arms.

**Primary restricted-mean analysis and decision.** Let H=38,341 and
Z_T=513*(1+min(X_T,H)). The sole primary parameter is
R_H=E[Z_1]/E[Z_23]. Estimate it by the ratio of the two all-32 sample means.
This is a ratio of means, not a mean of per-run ratios. An event at H counts as
observed; no event through H counts as capped. Both have Z=513*(1+H), but their
completion indicators differ. A full capped receipt gives an exact restricted
observation, so retain it with the same weight as a success. Do not discard caps,
fit tail extrapolations or change H. With only common administrative censoring,
this equals integrating empirical survival through H, plus initialization; no
Kaplan–Meier extrapolation or independent-censoring assumption is needed.

Sort each arm by repetition. Generate 10,000 independent bootstrap samples per
arm, each comprising 32 whole-trajectory row indices with replacement, using
NumPy `Generator(PCG64(seed_T)).integers(0,32,size=(10000,32))`. The seed for arm T
is the first 16 hex digits of SHA256(JSON([study_id,"bootstrap",T])); both seeds
are in `plan.json`. Reuse each arm's index matrix for all its diagnostics to
preserve within-trajectory dependence; the two arms use different streams.
Each bootstrap ratio divides the two resampled means. The fixed interval is
the two-sided, pointwise, **approximate nominal 95% percentile interval**, with
quantiles 0.025 and 0.975 and NumPy `method="linear"`.

If all 64 main receipts are valid and the interval's lower endpoint is >1,
report finite prospective evidence favoring T=23 for R_H. If its upper endpoint
is <1, report evidence in the opposite direction. Otherwise the directional
comparison is inconclusive; equality at 1 fails the directional rule. Missing
receipts suppress the primary estimate, interval and directional decision.
This is one primary comparison; diagnostic intervals have no simultaneous
coverage claim. Percentile intervals can be unstable with 32 observations,
rare tails or mass at the cap; even a degenerate bootstrap interval is not proof
of equality. Report raw per-trial values and censor indicators, empirical CDFs
of Z, q10/median/q90 of Z, and completion fractions with Wilson 95% intervals
(z=1.959963984540054), separately by arm. Restricted quantiles at the cap are
not uncensored runtime quantiles. No unrestricted mean conclusion is primary,
even if every sampled trajectory finishes before H.

**Missing data and integrity failures.** The unchanged engine prints only a final
boundary receipt. A killed trial has no durable event prefix; label it missing,
not capped at its kill time. For an arm with m missing among N=32, observed
restricted sum A gives sample-mean identification bounds
[(A+m*513)/32,(A+m*19,669,446)/32]. Combine arm bounds as
[L_1/U_23,U_1/L_23] for the restricted sample ratio. These are deterministic
missing-data bounds, not confidence intervals for population expectations.
With no receipts the ratio bounds are [1/38342,38342]. Report completed/capped/
missing separately; never use a complete-case bootstrap for the primary result.
Per-arm phase summaries from partial work must say they describe recorded
trajectories only, and carry the missing denominator; no all-trial phase inference.
A corrupt receipt causes an integrity stop and quarantined evidence, not silent
deletion. Determine validity before producing a scientific inference.

**Phase diagnostics that remain defined under censoring.** Define
u=min(U,H), s=min(S,H), q=min(P,H), x=min(X,H), and the per-trajectory occupancies
A=u, B=s-u, C=q-s, G=q-x. All are observed from a valid terminal receipt,
including a cap; set an unobserved event to H for these transformations only.
Analyze all-32 means of A (before U), B (between U and S), C (after S), and G
(post-S endpoint minus first exact). These are time spent before the common
horizon, **not** E[min(S-U,H)] or E[min(P-S,H)] among all eventual entrants.
An unentered phase has zero occupancy, not a missing or completed duration.

**Proved algebraic identities, not new runtime theorems:** A+B+C=q and
513*(1+A+B+C-G)=Z. Thus the T=1-minus-T=23 mean difference in post endpoint
evaluations decomposes as 513*(Delta A+Delta B+Delta C); the first-exact
difference subtracts 513*Delta G. The observed phase sum must not be called the
first-exact time when G>0. Report both differences and these identity residuals.
Use the same independent whole-row bootstrap matrices for pointwise nominal
95% intervals on means and differences; avoid percentages of a near-zero total
difference. Mechanistic attribution from phase differences remains descriptive.

Also report restricted event means for U, S and P; for each of U, S-U and P-S
give numbers entered/completed/censored-after-entry/not-entered, and observed
completed-duration mean and q10/median/q90. These conditional completed-phase
summaries are explicitly selection-conditioned and cannot be added across
different denominators. A phase completed exactly at the cap is completed.
Report the distribution of `bad_at_U`, `max_error_at_U`, `bad_at_S`,
`max_error_at_S` with their observed denominators. At U these describe
true/stored mismatch, not necessarily distance from target; at S labels equal
targets. Report own/external pinned-endpoint repairs, external replacements and
actual state changes. The repair counters start at each endpoint's individual
pinning, potentially before S, and stop at P or H; they are not post-S-only
counts. Replacements need not change a state or constitute useful repairs.
No kernel changes or new instrumentation are required to obtain these fields.

Keep work units separate: first-exact evaluation cost is 513*(1+X) when seen;
logical comparisons through that boundary are 513*T*X. The engine's cumulative
attempts, comparisons and elapsed seconds end at P or H, potentially later.
Report those cumulative fields under that endpoint label, and report wrapper,
compile and analysis time separately. Timing is descriptive on this host, with
no timing hypothesis or speed claim inferred from evaluation savings.

**Implementation contract and pre-draw gates for round 2.**

1. Locate the committed round-1 checkpoint at
   `research/reports/large-T-20261109/followup/round-0001/`. Require its report,
   provenance, `preregistration.md`, `freeze.json`, and every frozen artifact in
   Git at an ancestor of the current HEAD. Compare `git show COMMIT:path` bytes
   with local files and `freeze.json`; record that registration commit and
   directory. A locally written but uncommitted plan does not pass. The supervisor,
   not this agent, commits it after this round returns.
2. Re-run `plan.py --check`, `audit.py`, `test_plan.py`, the repository suite
   `python -m unittest discover -s tests -v`, and the prescribed compilation
   checks. Implement the measurement wrapper and test its deadline/receipt/gate
   behavior with mocks or existing independent test fixtures, **never prospective
   seeds**. Require no sampling code invocation before registration verification.
3. Use the existing cardinality kernel, not `run_research.py`'s different
   radius/noise model. A separate wrapper is justified because the frozen
   `neighborhood_campaign.py` neither defines this study nor permits its main
   arm/censoring policy. Do not edit that runner or bypass its holdout gate.
4. Freeze all executed sources before the first draw. Write `manifest.json`
   containing `study`, the entire `plan` array, `plan_sha256`, registration
   commit/directory/file hashes, exact command and deadlines, Git commit/dirty
   status, `sources` (relative path to SHA-256), `toolchain`, host/runtime and
   model conventions. Store exact bytes under `source/<relative path>`.
   Set `model_sha256=digest([study,sources,toolchain])`, where digest uses the
   canonical JSON above. Include the engine, wrapper and registered analysis
   sources. The row-plan digest is
   `f64686335a457d16eb0f26a94eef9a8bd94e75e76aec3eeb6524f50d1e48441f`.
5. Compile the frozen engine once. For each planned row invoke the binary with
   positional arguments `n T factor seed max_sweeps bit bit uniform observed`.
   Example structure for main: `engine 512 T 0.015625 SEED 38341 bit bit uniform observed`.
   T and SEED must come from the row, without rounding. Propagate the remaining
   monotonic deadline to the subprocess; kill its process group on cutoff.
6. Merge the returned fields with all planned row fields; add `wall_seconds`
   (engine process time), `model_sha256`, `plan_sha256`, and `stop_reason`
   (`post_exact` or `sweep_cap`). Set `record_sha256` to digest of the entire
   row without that field. Validate with `analysis.validate`, then atomically
   persist `rows/<id>.json` with fsync. Accept only expected fields/parameters,
   no duplicate or conflicting receipt, and no source change during execution.
   Emit per-invocation start/stop and per-trial failure elapsed-time records
   privately, even when no receipt survives. Preserve successful receipts.
7. The reference analyzer accepts `python ROUND1/analysis.py --run RUN_DIR
   --out SUMMARY.json`. Its source/plan/receipt checks are necessary but do not
   replace the wrapper's prior-commit/deadline gates. Verify the decomposition
   directly against raw records. Publish runnable wrapper source, exact source
   snapshots, manifest, all per-trial JSON receipts (small), compact CSV, summary,
   censor-aware ECDF/phase figure and checks in the next deliverables. Keep
   private logs outside deliverables. Use relative links and simple filenames.

Paths `ROUND1` and `RUN_DIR` above are placeholders resolved in the subsequent
checkout; the engine argument order, all numerical choices, seed order,
statistics and failure policy are already executable or explicit. To check this
round without any sampling, from the repository root after publication:

```sh
python research/reports/large-T-20261109/followup/round-0001/plan.py --check
python research/reports/large-T-20261109/followup/round-0001/test_plan.py
python research/reports/large-T-20261109/followup/round-0001/audit.py --out research/runs/round1-audit.json
```

**Conjectures, limitations and falsifiers.** The prospective conjecture is R_H>1;
an interval wholly below 1 is directional evidence against it, and any lower
endpoint <=1 fails the new support criterion. A CI crossing 1 does not prove
equality. The descriptive working hypothesis is that most savings occur before
S, motivated by the old primary phases; material positive post-S savings would
oppose an exclusively pre-S account, and G>0 forbids equating the two endpoints.
No causal mediation claim is registered. The existing reinfection and pathwise
nonmonotonicity counterexamples remain live. No candidate noisy proof is advanced.
Single-n restricted means establish neither unrestricted expectation ordering,
asymptotic growth, nor a general benefit from larger T. Selection-biased stored
noise, donor corruption, joint repair and rare tails remain proof obligations.
The supplied-corner law is not an assumption for this experiment. The supplied
literature/theory notes were read for model scope; this offline round makes no
new literature search, novelty claim or theorem transfer.
