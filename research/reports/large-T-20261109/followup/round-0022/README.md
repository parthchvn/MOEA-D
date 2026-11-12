# Round 22: the cost of losing the last correct slot

**Proved for the actual noisy pinned process:** the time spent with no correct
slot has an acceptance-weighted bound that stays constant when T grows like
sqrt(n). Write m=n+1, d_max=max_k |{i:k in B_T(i)}| and

\[
\kappa=\frac{2mp(1-p)}{1-(d_{\max}+1)p}.
\]

If the denominator is positive, from any pinned state with at least one
correct slot,

\[
 E Z_H\le\kappa E V_H.
\]

Here Z_H counts actual pre-attempt states with no correct slot before the
simultaneous boundary endpoint or horizon H. V_H counts pre-attempt states
having exactly one correct slot reachable by the scheduled breeder. These
are dependent occupation counts, not simulated means or independent phases.
For p=c/n, fixed c>0, T=o(n), **kappa=2c+o(1)**. This includes fixed T,
logarithmic T and square-root T.

The [proof](proof.md) uses v_k(y)=1/D(y,k) and an explicit cyclic-phase
correction. The corruption entrance factor pD(x,y)D(y,k) cancels the large
reciprocal before summation. External overwrites, shared observations,
selection bias and within-sweep reinfection remain in the process.

An ordinary-initialization extension charges first entry into the fully pinned
phase to actual pin-ready opportunities R_H:

\[
 E Z_H\le B_{\rm init}+\kappa E(R_H+V_H),\qquad
 B_{\rm init}\le\frac{mp(1-2^{-n})}{1-(d_0+1)p}.
\]

This is unconditional; it does not assume that accepted observations or the
state at S have a fresh noise law. The first interior pinning time A is
distinguished from its first boundary S. Completion is the existing post-S
simultaneous exact boundary event, which can differ from first exactness.

For **full communication T=n+1**, a separate stronger argument gives
kappa_full=p/(1-p) for all p<1: every inactive gate creates a correct slot.
This auxiliary reseeding result does not assert full simultaneous completion.

**Proved obstruction:** ongoing noise does not make every supplied all-wrong
state repair quickly. The explicit polarized family has expected first
reseeding at least

\[
\frac{a!}{(1-p)+p2^a}\quad\text{attempts},\qquad
a=\left\lceil\frac{n+1-T}{2}\right\rceil.
\]

For sublinear T and p=c/n this lower bound is
exp((1/2+o(1)) n log n). Thus the entrance weights are essential. Neither
positive accessibility nor this supplied-state residence yields an
ordinary-initialization runtime lower bound.

## What the bound does and does not settle

This answers the previous checkpoint's last-correct-loss first-moment question
at square-root T. The remaining gap is **noisy seeded occupation** and its
exit distribution. The clean 3n-times-error-count repair bound cannot simply
be applied during those noisy intervals. There is no new total-runtime
polynomial bound, fixed-c comparison between T arms, pre-U/S speedup theorem,
Taylor calculation, or uniform remainder claim.

Assumptions: standard independent rate-1/n bit mutation; activated bitwise
observation noise with the same mask rate; ascending cyclic own-parent
updates; filled-cardinality neighborhoods; shared offspring evaluation;
stored-label max-Chebyshev replacement with ties accepted. Pinned theorems
require ideal reference and target labels; the initialization extension
handles their actual first attainment explicitly. Offspring attempts exclude
the m initialization evaluations. No scheduler or algorithm was modified.

## Deterministic illustrations

These values evaluate exact rational formulas; they are not empirical means
or fitted laws. [bounds.csv](bounds.csv) contains the general kappa formula.
Its failed full-T degree conditions concern that general formula; the sharper
full-communication argument above needs no such condition.

| n | T=ceil(sqrt n) | c in p=c/n | General kappa bound |
|---:|---:|---:|---:|
| 128 | 12 | 1 | 2.348481 |
| 512 | 23 | 1 | 2.146742 |
| 4096 | 64 | 1 | 2.048512 |
| 512 | 23 | 1/64 | 0.031344 |

[traps.csv](traps.csv) gives exact **first true-change** means from supplied
polarized states. First reseeding and completion can be later. The formula
stops at the first change, allowing the unchanged algorithm to return or
reinfect later in that sweep.

| n | T | p | First-change mean, attempts | Analytic lower bound, attempts |
|---:|---:|---:|---:|---:|
| 16 | 4 | 1/16 | 69,671.0983 | 563.9161 |
| 32 | 6 | 1/32 | 329,016,959,869.1064 | 169,948,542.0896 |

## Checks and exact coverage

All finite calculations completed without truncation. Censoring and sampling
uncertainty are inapplicable. The analytic proofs, not these finite grids,
support the all-n claims.

| Check | Exact finite scope |
|---|---|
| Literal mutation masks | 33 rows: all parent weights at n=2,...,7. |
| Local reciprocal drifts | 24,816 cases: n=2,...,12; p=0,1/(64n),1/(4n); every target, parent and incumbent. |
| Cyclic compensation | 629,424 identities: n=2,...,32; every T, target and phase; two positive p values. |
| Actual noisy unseeded kernel | 14 cells: n=2,3; all T; p=1/(64n),1/(4n); 2,736 phase states total, at most 324 per cell. |
| Repair and entrance bounds | 10,800 exact supersolution inequalities; 2,304 last-correct entrance inequalities. |
| Independent arithmetic | Fraction Gaussian solves for all 144 n=2 states; separate literal-mask/scalarization verifier for all 2,736 residuals, without NumPy. |
| First full pinning | 31,231 label/reference/recipient proposals at n=2,3; all 232 decisive transitions satisfy the unique-final-target condition. Acceptance is independent of the true weights used in this check. |
| Full communication, including high p | 1,044 exact seed hazards: n=2,3; p=1/8,1/2,3/4; every unseeded phase state. |
| Noisy trap calculation | 36 exact formula cells: n in {3,4,6,8,16,24,32}; admissible deduplicated T in {3,ceil(ln n),ceil(sqrt n)}; p=0,1/(64n),1/n. Natural logarithm. |
| Formula illustrations | 93 cells: n in {16,32,64,128,256,512,1024,4096}; deduplicated T in {3,ceil(ln n),ceil(sqrt n),n+1}; c=1/64,1,2. |

Floating linear algebra only proposes decimal rational vectors. Exact Bellman
residuals give certified enclosing intervals in [cells.csv](cells.csv);
[certificates.csv](certificates.csv) preserves every vector entry. The
[literal verifier](verify.py) reconstructs the transition rows independently
from bit masks and scalarized comparisons. The [self-audit](audit.md) is not
an independent reviewer verdict.

The repository's 95 tests and 11 new tests pass; seven Python modules compile.
The suite retains acceptance-conditioning and reinfection counterexamples.
Research sampling is zero; existing seeded test fixtures are tests, not a new
Monte Carlo study. The original 240 blocked holdout observations are untouched.

## Reproduction

From this bundle's directory, with a fresh scratch output path:

```sh
PYTHONDONTWRITEBYTECODE=1 OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 /Users/parth/miniforge3/bin/python3 reproduce.py --repo "$(git rev-parse --show-toplevel)" --out /tmp/moead-round22-replay --check-published
```

The wrapper runs serially, sets one numerical thread, enforces a 300-second
cap per command, checks tracked cleanliness and relevant source hashes before
and after, and compares all six generated scientific files byte for byte.
It writes compilation caches only to temporary storage. Code uses relative
bundle paths and an explicit repository argument, so publication does not
depend on this isolated checkout's location. `PYTHON`, `BUNDLE` and `OUTPUT`
in command receipts are portable placeholders.

The standard-library-only certificate check can also run separately:

```sh
/Users/parth/miniforge3/bin/python3 verify.py --bundle .
```

See [checks.json](checks.json) for commit, source/config-in-code hashes,
timings and receipts; [verification.json](verification.json) for exact counts;
[memory.md](memory.md) for proposed ledger/status updates; and
[PROGRESS.md](PROGRESS.md) for checkpoints. Existing memory/evidence was not
edited. [provenance.json](provenance.json) inventories the final bundle.

No new empirical plan or trajectories, Taylor calculations, paid resources,
parallel agents, commits, pushes, remote changes, or external literature
search occurred. Novelty remains **UNVERIFIED**. The strongest falsifier is
an exact permitted phase state violating Phi-K_D Phi>=1, or an entrance
violating its acceptance-weighted continuation bound.
