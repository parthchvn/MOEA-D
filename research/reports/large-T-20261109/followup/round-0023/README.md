# Round 23: independent adversarial audit

**Result:** the precise larger-T claims from rounds 21 and 22 survive this
audit. The noisy occupation theorem now has a second, global-potential proof
and checks against complete tiny boundary-stopped processes. No noisy total
runtime bound follows yet. This is a same-family fresh-context review, not
formal proof certification. Novelty is UNVERIFIED.

Read [audit.md](audit.md) for the process, filtration, derivation, all-n constant
checks, negative branches, phase boundaries and remaining gap. Read
[memory.md](memory.md) for proposed claim/status updates. The source proofs
and empirical evidence remain unchanged.

The main counterexample to an incorrect interpretation is concrete: at
n=3,T=3,p=1/192, state (3,1,0,0), next breeder 1, the conditional mean future
reseeding delay after losing the last seed is at least **1.4185754517 attempts**.
The acceptance-weighted charge is only kappa=191/4488≈**0.0425579323**. The
entrance probability is 47/46656. Conditioning away that probability would
invalidate the result; the original theorem retains it. The bound is certified
with exact rational residuals, not estimated by simulation.

[witnesses.json](witnesses.json) also records a zero-drift phase-omission
witness, a complete positive-probability sweep with interior alignment followed
by reinfection, and the positive noisy error-count drift +385/139968. These
refute attempted shortcuts; they are not counterexamples to the source theorem.

## Deterministic coverage

| Check | Exact finite scope |
|---|---|
| Global W inequality and tracked-slot repair | n=2,3; all T=1,...,n+1; every population and breeder phase; p=0, 1/(64n), 99/[100(d_max+1)]; 13,017 global and 38,322 slot cases |
| Full boundary-runtime and occupation certificates | n=2,3; all T; p=1/(64n),1/(4n); 14 cells, 8,664 live phase states, 5,928 seeded-start occupation enclosures |
| Prior first-reseeding certificate verification | 14 prior cells, 2,736 rational residuals, independently reconstructed literal kernel |
| Clean seeded completion | n=2,3; all T>=3; 369 boundary states including aligned boundary zero |
| Signed Taylor coefficients | (n,T)=(2,3) through degree 1; (3,3),(3,4) through degree 2; eight exact coefficients matching the prior publication |
| Neighborhood and central-interval geometry | n=2,...,64; all T and breeders; 93,660 rows, including even-T parity and filled boundaries |
| Final full-pinning transitions | n=2,3; all stored-label vectors and enclosing references, all T/breeders/observations; 31,231 proposals, 232 final pins; one all-wrong true vector suffices because acceptance ignores true weight |

The global grid includes aligned phase zero to check the unrestricted one-step
inequality. Runtime equations instead kill **only** aligned phase zero and
retain every aligned interior state. Their maximum cell has 1,023 live phase
states. The exact clean and polynomial computations cover no larger n than
listed. Large-n analytic conclusions do not rest on extrapolating these checks.

`audit.py` is a new implementation, with no imports from older rounds. It
enumerates literal mutation masks and scalarization comparisons. Numerical
linear solves propose decimal rationals; exact Bellman residuals certify
enclosures. `verify.py` checks these without NumPy or numerical solves.
Regenerating the floating proposals can depend on the numerical library;
byte comparison is deliberately strict. The supplied rational certificates
can be verified without that dependency.
The signed sweep-polynomial expansion is independent of the earlier
phase-recurrence implementation and retains both branches of J-K.

## Reproduction

From this bundle, with REPO set to the repository root and OUTPUT a new scratch
directory outside the bundle:

```sh
/Users/parth/miniforge3/bin/python3 reproduce.py --repo REPO --out OUTPUT --check-published
```

The interpreter path is the one used here; on another machine substitute its
configured Python with NumPy. The script sets every relevant numerical thread
limit to one, runs the 95 repository tests and eight new tests, compiles the
required modules with a temporary pycache, rebuilds eight outputs, verifies
their rational certificates and checks exact byte identity. Every subprocess
has a 300-second cap. It never invokes an experiment runner. Existing fixed
test fixtures are not a new scientific experiment. A failed or interrupted
replay is not a completed finite grid.

Individual analysis-only commands are also available:

```sh
/Users/parth/miniforge3/bin/python3 audit.py --repo REPO --out OUTPUT
/Users/parth/miniforge3/bin/python3 receipts.py --repo REPO --out OUTPUT/empirical.json
/Users/parth/miniforge3/bin/python3 verify.py --bundle OUTPUT
```

Use the main wrapper to enforce numerical thread limits automatically.
No path to this checkout is embedded in the reproduction code. Prior-source
locations are resolved from the supplied repository root. The current exact
model/config/source hashes and execution receipts are in [checks.json](checks.json),
and the final bundle inventory is in [provenance.json](provenance.json).

The generated files are [global.csv](global.csv), [occupation.csv](occupation.csv),
[certificates.csv](certificates.csv), [clean.csv](clean.csv),
[coefficients.csv](coefficients.csv), [witnesses.json](witnesses.json),
[verification.json](verification.json) and [empirical.json](empirical.json).
Exact fractions are authoritative; decimals are display values. The largest
artifact is below 1 MB. No raw trajectory grid, private log, PDF, credential,
symlink or external-service data is included.

## Empirical estimands and limitations

The receipt audit independently checks all 68 separate follow-up receipts and
1,244 original campaign receipts. At n=512 the registered estimand is the
ratio of restricted mean first-exact evaluations through 38,341 sweeps,
including 513 initialization evaluations. The 32 main observations per arm
are complete. The four smoke observations are excluded from inference.

The independently replayed ratio is **2.3390952207223643**, with the original
approximate nominal 95% percentile interval
**[2.0853866835146455,2.5964682010315485]**. Registered whole-trajectory bootstrap
resamples retain within-run phase dependence and use independent arm streams.
The original n=256 mean ratio again equals **2.3276385562777966**; its old
bootstrap interval is not re-certified here.

The original campaign's single capped high-noise main trial and 240 missing
gate-blocked holdout observations remain visible and unchanged. Missing rows
are not administratively censored outcomes. The original two-stage conclusion
stays inconclusive. The separate study does not substitute for the blocked
holdout. Phase savings remain descriptive, not causal mediation; observed
completion of every trial does not convert restricted to unrestricted means.

Registration bytes and ancestry were checked in the local Git object database.
Published receipts and Git dates do not independently verify inaccessible
private execution chronology. Seed separation was rechecked against all
campaign plans, including the blocked holdout, not against unrelated historical
experiments. No new scientific samples or seeds were generated.

The next useful obligation is a signed noisy drift estimate for the
phase-dependent clean completion potential while a seed survives, with
last-seed losses charged to W. The existing error-count witness makes that
choice of potential a falsifiable issue, rather than an automatic transfer
of the clean theorem.
