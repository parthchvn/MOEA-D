# Round 15: fourth-order supplied-corner response

**The full polynomial question remains unresolved.** This checkpoint derives
exact fourth coefficients, proves a polynomial bound for the T=3 arm alone,
and supplies two candidate cancellation bounds for T=2. It also shows that
retaining actual mutation probabilities does not rescue the positive
two-entry third-residence majorant. The [derivations](proof.md) separate all
four statements and identify the remaining transfer obligations.

For the frozen pinned process and full-sweep simultaneous-alignment event,

\[
E\tau_3-E\tau_2=pA_n+p^2B_n+p^3C_n+p^4D_n+O_n(p^5).
\]

**Mechanically checked exact coefficients, rounded for display:**

| n | T=2 fourth coefficient | T=3 fourth coefficient | D_n |
|---:|---:|---:|---:|
| 3 | 7.558680030268 | 8.576265119673 | +1.017585089405 |
| 4 | 13.833568380548 | 12.633155088872 | -1.200413291676 |
| 5 | 17.253346446187 | 17.856099860554 | +0.602753414367 |

D is the fourth derivative divided by 24, in sweeps. Attempts multiply it
by n+1. There is no sampling error, confidence interval or censoring for
these rational calculations. Independent sweep and phase recurrences match
20 quantities through order four at n=3,4. Twenty-four lower-order values
match published exact hashes at n=3,4,5. At n=4 all sixteen ordered R/O words
sum exactly to the T=2 fourth coefficient. n=5 has no independent fourth
oracle; it has the published lower-order checks and a fresh exact replay.

**Proved:** |d_(T=3,n)|<=122880000 n^9, using clean frontier repair for at
most five errors and exact finite exceptions. This does not bound D_n.

**Proved negative result:** a two-corruption path from the actual supplied
corner, retaining mutation and acceptance probabilities, has third clean
residence contribution at least 2^n/[12288 n^4(n+1)] for odd n>=9. The exact
selected contribution is 2.5179029708e9 at n=65. This rejects an absolute
residence shortcut, not polynomiality of the signed coefficient.

**Candidate proof:** for an isolated closed pair, with
r(z)=d(z,k)+d(z,k+1), the second response v2 in local attempts obeys
r(x)r(y)|v2|<=2176(32n)^3 at both phases. The key new estimate is the
unconditional active-escape bound rho(z)^2<3r(z). Exact checks cover 42
adjacent isolated pairs at n=3,...,9, including 4,032 double-error and 1,120
single-error phase states and 16,030 inequalities/identities.

**Candidate proof:** the full T=2 ordered word RROO satisfies
|RROO|<=5000(n+1)^2(20n)^4/q. A correct-orphan stationary identity reduces
the second excess to O(M^2) for a closed bad pair. A separate stopped-reward
argument retains feedback from the orphan-fed last pair. Exact checks cover
254 states at n=4,6,8, 1,734 phases, 1,950 stopped-reward checks and 36
stationary identities. Exact RROO is 2.135753903581 at n=4 and
4.179111924897 at n=6. These two new all-n arguments await independent audit.

**Remaining gap:** RRRR and thirteen other mixed fourth words lack a complete
all-n bound here. A local pair result cannot freeze the remaining population
or replace simultaneous completion by a maximum of noisy first hits. No
uniform higher remainder, enlarged noise window or fixed-positive-c ordering
is established. [proof.md](proof.md) gives explicit falsifiers.

| File | Purpose |
|---|---|
| [proof.md](proof.md) | Exact process, identities, negative path, local candidate and RROO candidate |
| [fourth.py](fourth.py) | Order-four sweep-product response recursion |
| [verify.py](verify.py) | Independent phase oracle, published lower-order checks, compact curation |
| [pair.py](pair.py) | Isolated-pair coefficients, local inequalities and positive path witnesses |
| [excess.py](excess.py) | Phase-aware RROO and stationary/stopped-reward checks |
| [test_fourth.py](test_fourth.py) | Literal-mask, boundary, forcing and model-scope regressions |
| [coefficients.csv](coefficients.csv), [gaps.csv](gaps.csv) | Rational fingerprints and rounded arm/gap values |
| [words.csv](words.csv), [mixed.csv](mixed.csv) | Sixteen n=4 fourth words and the n=4,6 RROO checks |
| [pair.csv](pair.csv), [pair.json](pair.json) | Local pair checks and counts |
| [entrance.csv](entrance.csv), [obstruction.csv](obstruction.csv) | Exact positive-majorant witnesses, with their limited scope |
| [excess.csv](excess.csv), [stationary.csv](stationary.csv), [excess.json](excess.json) | Correct-orphan excess checks and counts |
| [verification.json](verification.json), [dependency.json](dependency.json) | Oracle and earlier-evidence receipts |
| [reproduce.py](reproduce.py) | Complete serial replay with a wall deadline |
| [checks.json](checks.json), [provenance.json](provenance.json) | Test, preservation, runtime and source-hash accounting |
| [memory.md](memory.md) | Durable C35-C40 claim/status supplement |

From the repository root, using the configured Python:

```sh
PYTHONDONTWRITEBYTECODE=1 OPENBLAS_NUM_THREADS=1 python deliverables/test_fourth.py
PYTHONDONTWRITEBYTECODE=1 OPENBLAS_NUM_THREADS=1 python deliverables/reproduce.py --repo . --out research/runs/round15/replay-new --seconds 3000
PYTHONDONTWRITEBYTECODE=1 OPENBLAS_NUM_THREADS=1 python -m unittest discover -s tests -v
PYTHONPYCACHEPREFIX=/tmp/round15-cache python -m py_compile sim.py large.py scripts/run_research.py deliverables/fourth.py deliverables/pair.py deliverables/excess.py deliverables/verify.py deliverables/reproduce.py deliverables/test_fourth.py
```

Use a fresh replay destination. After publication replace `deliverables` in
these commands with `research/reports/large-T-20261109/followup/round-0015`.
The reproducer enforces one numerical thread and serial execution. It first
replays round 14, including earlier registered plans, receipts and seeds,
then computes all new algebra and compares thirteen curated outputs byte for
byte. Large exact fractions and execution logs stay in the requested private
run directory. Hashes in the compact CSV files refer to the canonical string
of each exact Fraction; rounded decimals are not used for equality checks.

**Empirical history preserved:** the original n=256 ratio remains 2.327639
[2.050148,2.674642], with 24 complete observations per arm. The separately
registered n=512 restricted-mean ratio remains 2.339095
[2.085387,2.596468], with 32 per arm. These retain their earlier approximate
nominal 95% bootstrap intervals; [dependency.json](dependency.json) retains
distributions and phase denominators. No plan or receipt repair was needed.
The original cap, preregistration, 240 missing gate-blocked holdout trials
and inconclusive two-stage decision are unchanged. Private earlier trial
logs remain unavailable, so chronology is checked only from published
evidence. No new scientific trajectories or seeds were generated.

No network, paid resources, source-PDF changes, commit or push were used.
No literature novelty claim is made in this offline task.
