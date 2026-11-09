# Round 4: fixed-T noisy corner

**Result: a donor-occupation bound and a complete candidate proof of the
fixed-cardinality corner theorem.** The proposed theorem gives
\(\Theta_{c,T}(n^2)\) expected attempts for every fixed (c>0,T\ge2), versus
\(\Theta_c(n^3)\) at (T=1), from the supplied ideal-reference, pinned-label
single-corner state. The full result is **candidate**, pending independent
review of the error-family coupling. The local occupation and endpoint bounds
have direct proofs in [proof.md](proof.md).

For donor 1, (d_1=|\{i:1\in B_T(i)\}|\le2T-1). Starting it correct and
writing (a=p/(1-2p)), the proved occupation estimates are

\[
 E B_1(\sigma)\le d_1a E\sigma,\qquad
 E[O_1(\sigma)/(n+1)]\le d_1(a+p)E\sigma.
\]

(B_1) counts incorrect pre-own-turn states; (O_1) counts incorrect states
before all attempts. They hold at integrable boundary stopping times, with
finite truncation used first. Thus an (O(n))-sweep interval has only
(O_{c,T}(1)) expected incorrect sweep-equivalents for this donor. This does
not assume that a retained observation has an unbiased noise distribution.

**Analytic illustration, not a measurement.** At (n=512,T=3,c=1/64), the
first endpoint boundary repair is bounded above by **1,390.571 sweeps**.
Before that event, donor 1 has at most **0.127319 expected incorrect own turns**
and **0.254629 expected incorrect sweep-equivalents**. The proposed simultaneous
upper bound is 1,458.942 sweeps. [bounds.csv](bounds.csv) gives the rounded
analytic constants, including much looser high-noise bounds; it contains no
sampled trajectories or fitted laws.

The new proof represents each error by a local repair particle. An erroneous
external replacement creates a child; a clean external repair can erase the
actual tag while leaving an unused comparison particle. Expected child repair
work per active turn is at most \((T-1)p/(1-2p)\). Independent base families
represent fresh corruption from correct parents. A derived empty-state renewal
identity controls joint completion even when (cT) is large. This avoids the
small-noise restriction of a direct union/drift bound, but introduces the main
new proof obligation: validate that comparison construction for whole cyclic
trajectories, including births later in the same sweep.

**Mechanically checked dependencies.** The round-3 independent auditor was
rerun before using prior measurements. All six outputs reproduce byte for
byte, including 6,914 scalar/structural checks and the prior registration,
receipt, source, and seed checks. The old experiment has usable plans and
receipts; no repair was needed. Details are in [dependency.json](dependency.json).
The local 20-page manuscript contains the repair-potential lemmas, but the
revised fixed-(c), (T=3) proof described in the theory note was not present.
The new argument does not assume it. [sources.json](sources.json) records
the source audit and exact hashes. No source PDF was changed.

**Existing empirical measurements, reverified; no new sampling.** All entries
below use ordinary initialization, (p=1/(64n)), and include initialization
evaluations. They do not observe the supplied corner theorem.

| Published study | T | Exact / planned | Mean evaluations | q10 / median / q90 |
|---|---:|---:|---:|---:|
| Original n=256 | 1 | 24 / 24 | 1,165,698.458 | 837,357.4 / 1,108,569.5 / 1,505,942.9 |
| Original n=256 | 3 | 24 / 24 | 606,177.333 | 391,308.2 / 519,140.0 / 949,717.8 |
| Original n=256 | 16 | 24 / 24 | 500,807.333 | 355,122.6 / 490,356.0 / 645,018.6 |
| Separate n=512 | 1 | 32 / 32 | 5,139,185.906 | 4,506,858.9 / 5,042,790.0 / 5,903,142.3 |
| Separate n=512 | 23 | 32 / 32 | 2,197,082.813 | 1,591,839.0 / 2,182,815.0 / 2,585,776.5 |

These cells have no caps or missing receipts. The original primary T=1/T=16
ratio remains **2.327639 [2.050148, 2.674642]**. The separate n=512 T=1/T=23
restricted-mean ratio remains **2.339095 [2.085387, 2.596468]**, with approximate
nominal pointwise 95% bootstrap intervals. The latter has horizon 38,341
sweeps and 32 independent observations per arm; four smoke trials are excluded.
The original campaign still has one capped high-noise main row and **240
missing, gate-blocked holdout rows**. Its two-stage decision stays inconclusive.
No seed, cap, gate, original preregistration, or prior artifact was altered.

The existing phase evidence still places the sampled n=512 mean savings
predominantly before S: 4,462.40625 sweeps before U, 1,272.5625 between U and S,
and 0.125 after S. All phase denominators are 32 per arm; one T=1 row has a
four-sweep post-S delay. Both arms have zero recorded pinned-endpoint repairs.
Thus the corner proof is a conditional mechanism result, not an explanation
established for those empirical savings.

**Mechanically checked new mathematics.** [check.py](check.py) uses exact
fractions for 202 local kernels at (2\le n\le8), 6,628 kernel comparisons,
and 1,366 published state rows. It checks the uniform injection inequality,
first-step repair equations, stationary identities and composed mutation.
It checks 2,142 neighborhood cells through n=64, exhausts 263,169 single-step
tagged-particle couplings at n=2, and matches 24 renewal identities to exact
finite Markov-chain solutions. The old reinfection path and a donor-corruption
witness are retained in [verification.json](verification.json).
[kernels.csv](kernels.csv) contains exact rational values.

**Tests and reproduction.** All 95 repository tests, 15 new proof tests and 16
dependency-audit tests pass. Python compilation passes. Unit checks include
literal bit masks, independent transition enumeration, within-sweep children,
unused base immigrants, persistent untagged particles, and distinct birth IDs.
While extending the checker beyond one step, temporary birth IDs were replaced
with unique live IDs; this was a checker implementation correction, not a
change to prior evidence or to the mathematical process. No scientific
sampling failure occurred, because no new experiment was launched.

From the repository root, before publication:

```sh
PYTHONDONTWRITEBYTECODE=1 python deliverables/reproduce.py --repo . --out /tmp/corner-replay
PYTHONDONTWRITEBYTECODE=1 python deliverables/test_proof.py
python -m unittest discover -s tests -v
python -m py_compile sim.py large.py scripts/run_research.py
```

After publication replace `deliverables` with
`research/reports/large-T-20261109/followup/round-0004`.
The reproduction command creates fresh deterministic outputs and replays the
earlier auditor; it invokes no sampler. Python's standard library suffices
for the new proof checker. NumPy is used only by the old registered bootstrap
replay. [checks.json](checks.json) records commands, durations, byte comparisons,
preservation and final output hashes. Raw logs are outside this bundle.

**Assumptions, gaps, falsifiers.** The theorem requires standard bit mutation
and activated bitwise prior noise, independent fresh randomness, pinned ideal
labels, the supplied state, own parents, filled cardinalities, and the stated
cyclic order. For finite n the upper bound also requires
(p<1/2,(T-1)a<1,d_1a<1). These hold eventually for fixed (c,T).
Independent review must check the multi-sweep tag coupling, generation-work
bound, independent-family product and empty-state renewal, and restart at
the endpoint stopping time. A valid update that loses a tag for a wrong slot,
an exact violation of the injection bound, or an exact hitting expectation
exceeding the displayed finite bounds would falsify the corresponding argument.
No bound is transferred to growing T, ordinary initialization, one-bit mutation,
archive coverage, or runtime monotonicity. No literature search or novelty
claim is made in this offline turn.

**Morning report.** Cumulative progress consists of the original campaign,
the separately preregistered n=512 study, its independent audit, and now a
candidate fixed-T noisy corner proof with an explicit donor-occupation bound.
The empirical decision is unchanged. New files are this curated proof/check
bundle and its [claim supplement](memory.md); local STATUS/CLAIMS are updated.
One CPU was used, with no paid resources, network, commit, push, or new
scientific sampling. The next useful work is independent adversarial review
of the candidate coupling and renewal argument, before promoting the theorem.
