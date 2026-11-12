# Round 21: larger-cardinality donor structure

**Proved under supplied ideal reference and pinned target labels:** for every
filled T>=3, one correct slot protects clean repair. With m_e errors, the
expected simultaneous boundary completion time is at most 3n m_e sweeps.
T=2 closed pairs and the even-n orphan explain why its earlier local slow
traps do not satisfy that guarantee.

**Proved negative result:** strong connectivity alone is insufficient. With
no correct slot, an explicit polarized population has exact clean first-change
mean at least a!/(n+1), where a=ceil((n+1-T)/2). A matching-scale upper bound is

\[
 \sup_w E_w\tau\le4\,2^{a_*}a_*!+3n^2,\qquad
 a_*=a+1\{T\text{ even},\ n\equiv3\pmod4,\ T<n+1\}.
\]

Consequently clean worst-state means can be exp(Theta(n log n)) even at
T=ceil(ln n) or ceil(sqrt n); full communication creates a correct slot on
the first attempt. This is a worst-state result, not ordinary-initialization
or noisy-corner complexity. The explicit noisy entrance to the trap retains
its very small acceptance/mutation factors.

The [proof](proof.md) also gives a uniform O_j(n^(2j+1)) bound on supplied-corner
Taylor coefficients of fixed degree j<n for all T>=3. It gives no uniform
remainder or fixed-positive-c ordering. The old forest bound's exponential
factor is traced to simultaneous extinction of every artificial family.
[Self-audit](audit.md) records qualifications and falsifiers; it is not an
independent reviewer verdict.

## Comparisons

The requested set {2,3,4,5,7,ceil(ln n),ceil(sqrt n),n+1} is deduplicated, with
inadmissible cardinalities omitted. Natural log is explicit. [geometry.csv](geometry.csv)
contains 104 cells at n in {3,4,5,6,7,8,9,16,17,32,33,64,65,128,256,512,1024},
including source components, nonreciprocal edges, incoming degrees, endpoint
neighborhoods, and the even-T central-interval penalty.

**Mechanically checked exact means, rounded for display:** the following
repair rows compare the *same supplied state* across T. All other slots are
correct; p=0. They are total boundary completion means in sweeps.

| Supplied errors | T=2 | T=3 | Full T |
|---|---:|---:|---:|
| n=17, last pair both weight zero | 1.51509e18 | 65.62897 | 59.32694 |
| n=18, orphan weight zero | 3.93464e22 | 47.56346 | 44.82123 |

At n=32, the polarized trap first-change means are 1.03378e14 sweeps at T=3,
5.34453e13 at T=4=ceil(ln 32), 2.05014e12 at T=6=ceil(sqrt 32), and 1 at full
T=33. Those trap populations **vary with T** and do not prove same-state
monotonicity. Exact fractions and mask entrance factors are in [traps.csv](traps.csv).

## Reproduction and finite scope

From this bundle's directory, using the configured interpreter:

```sh
PYTHONDONTWRITEBYTECODE=1 OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 /Users/parth/miniforge3/bin/python3 reproduce.py --repo "$(git rev-parse --show-toplevel)" --out /tmp/moead-round21-replay --check-published
```

Use a fresh scratch output directory. No code writes to the repository's
existing sources or evidence. The wrapper runs serially with one numerical
thread, checks all tracked files and HEAD before/after, and reproduces six
deterministic data files byte for byte. `BUNDLE` and `OUTPUT` in the saved
command receipt are portable placeholders. Source and configuration hashes,
Git state, timings, test counts and interpreter version are in [checks.json](checks.json).

| Artifact | Scope |
|---|---|
| [structure.py](structure.py), [test_structure.py](test_structure.py) | Exact graph, mutation, clean subset recurrence, trap, parity, entrance and reinfection checks. Hard clean closure cap: 256 states. |
| [response.py](response.py) | Exact sparse phase recurrence at (n,T)=(2,3),(3,3),(3,4), degrees through n-1. Hard cap: 1024 phase states. No population matrix. |
| [verification.json](verification.json) | 91,518 neighborhood rows; 11,408 central seed rates; 369 seeded boundary means and 1,088 phase means; 48 larger repair cells; 48 trap cells, 23 direct sweep checks. |
| [repair.csv](repair.csv) | Pair/orphan states at n={5,6,9,10,17,18,33,34}; at most four clean subset states each. |
| [traps.csv](traps.csv) | Exact product law at n={3,4,5,6,7,8,16,24,32}; direct subset-sweep comparison only for n<=7. |
| [coefficients.csv](coefficients.csv) | Eight exact coefficients; three n=3,T=3 values match published round-8 fractions. |
| [forest.csv](forest.csv) | 56 formula cells, n={32,128,512,1024}, c={1/64,1}; exact rational conditions/exponents and illustrative floating log10 upper bounds. |
| [memory.md](memory.md), [PROGRESS.md](PROGRESS.md) | Proposed claim/status changes and checkpoints. Existing memory files were not edited. |
| [provenance.json](provenance.json) | Final artifact inventory, work accounting and integrity metadata. |

The seeded population checks are exhaustive only at n=2,3 and T>=3. The
all-n results rely on the written proofs, not the grid. New tests plus the
repository suite comprise 105 passing tests; seven Python modules compile.
Exact coefficient recurrences additionally verify 6,298 live-phase Bellman
equations across the three configurations and requested orders.

No scientific Monte Carlo study, new research seed set, paid resources,
delegation, commits or pushes occurred. Censoring is inapplicable to the exact
calculations. A first development run exceeded Python's default integer
printing limit; the documented higher ceiling and complete rerun resolved it.
The 240 original blocked holdout observations remain untouched. No newer-work
search was performed, so novelty is UNVERIFIED. The next mathematical gap is
the acceptance-weighted cost of losing the last correct slot under ongoing
noise, not another inference from clean means to noisy synchronization.
