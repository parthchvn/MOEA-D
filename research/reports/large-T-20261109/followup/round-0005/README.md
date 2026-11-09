# Round 5: proof audit and reproducible counterexamples

**Proved:** the round-4 fixed-T supplied-corner argument survives analytical
red-team review. **Contradicted:** universal expected monotonicity in T,
acceptance-conditioned error probability at most p, and interchangeability of
mid-sweep and boundary correctness. See [audit.md](audit.md) for assumptions,
complete review, proof details and scope; [memory.md](memory.md) is the durable
claim/status supplement.

The new exact finite-state result at n=3,p=1/192 is a T=2 to T=3 slowdown:
4.7659580192 to 4.7671266818 expected sweeps from the supplied corner, despite
identical endpoint-donor sets. [verification.json](verification.json) gives
rational witnesses. [expectations.csv](expectations.csv) contains certified
intervals for all 25 cells; [certificates.csv](certificates.csv) contains the
4,339 population-state certificates. These intervals are deterministic
mathematical enclosures, not confidence intervals or sampled averages.

From the repository root, the portable check requires only Python's standard
library; `-S` intentionally disables site packages:

```sh
python -S deliverables/verify.py --bundle deliverables
```

For complete regeneration and prior-dependency replay, choose a new directory.
NumPy is needed for proposing numerical certificates and replaying the old
registered bootstrap. All tasks are serial with one numerical thread:

```sh
PYTHONDONTWRITEBYTECODE=1 python deliverables/reproduce.py --repo . --out /tmp/round5-replay
PYTHONDONTWRITEBYTECODE=1 python deliverables/test_audit.py
python -m unittest discover -s tests -v
python -m py_compile sim.py large.py scripts/run_research.py
```

After publication replace `deliverables` with
`research/reports/large-T-20261109/followup/round-0005` in these commands.
Regeneration compares all five deterministic outputs byte for byte on the
recorded toolchain. If another numerical library rounds a proposed vector
differently, the saved exact certificates remain independently verifiable;
their mathematical validity does not rely on numerical-solver error estimates.

[audit.py](audit.py) constructs full-state transitions from literal bit masks
and scalarization comparisons. Floating linear solves propose values only;
integer/Fraction Bellman residuals certify their intervals.
[verify.py](verify.py) recomputes every certificate and witness without numerical
solves. [forest.py](forest.py) exhausts three sweeps at n=2 from two starts and
T=1,2,3, checking all encountered transitions but expanding only states with at
most two particles. [forest.json](forest.json) records its 242,064 transitions
and pruning. The general forest lemma is proved analytically in the audit.
[test_audit.py](test_audit.py) includes tampering, boundary semantics, family
bookkeeping, and 27 exact multisource renewal cases with random initial lifetimes.

**Published empirical evidence, reverified:** original n=256 T=1/T=16 ratio
2.327639 [2.050148,2.674642], 24 complete trajectories per arm; separate n=512
T=1/T=23 restricted ratio 2.339095 [2.085387,2.596468], 32 complete trajectories
per arm at horizon 38,341 sweeps. Intervals are the registered approximate
nominal 95% intervals. [dependency.json](dependency.json) preserves arm means,
quantiles and phase denominators and verifies the prior committed plan.
The original 240-trial holdout remains gate-blocked and entirely missing;
its original two-stage decision remains inconclusive. No new trajectories,
seeds, cap changes or holdout measurements were introduced.

[checks.json](checks.json) records tests, provenance, elapsed time and preservation.
Raw command logs remain outside this bundle. No source PDF, scientific engine,
original preregistration or published evidence changed; no commit, push, cloud
resource or network access was used. One CPU was used. Finite certificate
checks and the bounded forest enumeration do not replace the analytic proof.
