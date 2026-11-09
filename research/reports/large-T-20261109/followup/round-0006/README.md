# Round 6: small-noise coefficient

**Proved finite-n identity; mechanically checked values:** for the pinned
supplied corner, with τ in sweeps,

`Eτ(T=3) − Eτ(T=2) = p A_n + O_n(p²)`.

The exact n=3 coefficient is positive, **0.22213184717778317…**. The exact
coefficients at every n=4,…,10 are negative. Identical direct endpoint donors
therefore give neither equal noisy laws nor the same sign of the small-noise
gap at different n.

**Candidate asymptotic theorem:** `A_n = −(n/2) log n + O(n)`, with a complete
argument in [derivation.md](derivation.md), awaiting independent review.
T=2's slow-directed interior pairs supply the logarithm; T=3 has a fast clean
donor for every interior site. The coefficient in attempts is `(n+1)A_n`.
No uniform Taylor remainder or ordering at fixed positive c in p=c/n is claimed.

| File | Purpose |
|---|---|
| [derivation.md](derivation.md) | Model, finite-n identity, candidate asymptotic argument, limits and falsifiers |
| [coefficients.csv](coefficients.csv) | Eight exact rational and fourteen deterministic float64 size calculations |
| [components.csv](components.csv) | Exact recipient contributions, including the n=3 mechanism |
| [scaling.png](scaling.png) | Sign reversal and parity-separated size dependence; no fitted law |
| [coefficient.py](coefficient.py) | Rational two-error recurrence and fast disjoint-donor formula |
| [verify.py](verify.py) | Independent n=3 full-state, literal-mask exact derivative |
| [verification.json](verification.json) | Exact agreement for both 256-state systems and small-n signs |
| [comparison.json](comparison.json) | Linear prediction against the prior certified finite-p slowdown |
| [dependency.json](dependency.json) | Replayed published receipts, prior plans, certificates and holdout status |
| [test_coefficient.py](test_coefficient.py) | Twelve deterministic regression tests |
| [reproduce.py](reproduce.py) | Full serial regeneration and dependency replay |
| [plot.py](plot.py) | Scientific figure generation |
| [memory.md](memory.md) | Durable claim/status supplement |
| [checks.json](checks.json) | Verification, toolchain, preservation and time accounting |

From the repository root, the portable exact n=3 verifier needs only the
standard library. `-S` disables site packages:

```sh
PYTHONDONTWRITEBYTECODE=1 python -S deliverables/verify.py --bundle deliverables
```

Complete regeneration needs NumPy and Matplotlib and an unused output
directory. It replays the earlier recorded evidence but never calls a sampler:

```sh
PYTHONDONTWRITEBYTECODE=1 python deliverables/reproduce.py --repo . --out /tmp/round6-replay
PYTHONDONTWRITEBYTECODE=1 OPENBLAS_NUM_THREADS=1 python deliverables/test_coefficient.py
PYTHONDONTWRITEBYTECODE=1 python -m unittest discover -s tests -v
PYTHONPYCACHEPREFIX=/tmp/round6-pycache python -m py_compile sim.py large.py scripts/run_research.py
```

After publication, replace `deliverables` in these commands with
`research/reports/large-T-20261109/followup/round-0006`. No absolute paths are
embedded in the calculation. Exact rational outputs are portable; float64 rows
and the PNG are byte-reproducible on the recorded toolchain, while other
numerical/plotting libraries may round or render differently. The full-state
exact verifier is independent of such numerical output.

**Published empirical evidence, reverified:** the original n=256 ratio is
2.327639 [2.050148,2.674642], with 24 complete observations per arm. The separate
preregistered n=512 ratio is 2.339095 [2.085387,2.596468], with 32 complete
observations per arm. These are the original approximate nominal 95% intervals,
not results of a new experiment. The original campaign still has one capped
main trajectory and 240 missing, gate-blocked holdout trajectories; its two-stage
decision remains inconclusive. The committed round-1 plan predates the separate
n=512 measurement. No dependency repair was necessary.

There are **zero new scientific trajectories or seeds**. All new numbers are
deterministic mathematical evaluations, so no prospective empirical plan was
needed. Original caps, seeds, gates, preregistration, receipts and source PDFs
remain unchanged. Raw work logs are outside the bundle. No network, paid
resource, Git commit or push was used.
