# Round 24 synthesis: larger neighborhoods, recovery and the remaining runtime gap

**Finding — proved within the specified pinned process, from rounds 21–23:** a surviving correct slot gives uniformly polynomial **clean** repair, and the acceptance-weighted cost of losing the last correct slot is bounded under ongoing noise. At fixed \(c>0\), \(p=c/n\), and \(T=o(n)\), the latter charge tends to \(2c\). These statements remove an unweighted all-wrong residence obstruction; they do **not** bound noisy time spent with a surviving correct slot. No new polynomial total-runtime theorem for square-root \(T\), or ordinary-initialization transfer, is established by this activation. The older forest bound already gives a polynomial bound for logarithmic \(T\), as recorded below.

This round supplies a cumulative scientific checkpoint, not another experiment or a new theorem. [HISTORY.md](HISTORY.md) indexes every published follow-up pass 1–23, this pass, the two duplicate recovery copies, earlier campaigns, all identified counterexample families and unfinished routes. “Proved” describes an analytic result under its stated assumptions; finite checks corroborate it but do not certify all \(n\). Older proofs retain their published audit status rather than being silently re-reviewed here. The same-family fresh-context review is not formal certification or an independent-model endorsement. External novelty is **UNVERIFIED**; no current literature search was performed.

## Exact process and units

For the positive noisy structural result take \(n\ge2\), \(m=n+1\), and integer \(1\le T\le m\). At attempt \(t\), breeder \(a=t\bmod m\) mutates its own incumbent by independent per-bit flips of rate \(1/n\). Let \(D(x,y)\) be the resulting weight kernel. For a noise activation probability p in [0,1], a fresh independent Bernoulli(\(p\)) gate activates an independent observation mask at the same per-bit rate, giving one shared observation with law

\[
N(y,k)=(1-p)\mathbf1_{y=k}+pD(y,k).
\]

The filled-cardinality neighborhood is \(B_T(i)=[L_i,L_i+T-1]\), where

\[
L_i=\max\{0,\min(i-\lfloor(T-1)/2\rfloor-\mathbf1_{T\ {\rm even},\ i\ {\rm odd}},m-T)\}.
\]

This fills exactly \(T\) recipients, including at the endpoints. It is **not** the clipped symmetric radius in `large.py`, nor the neighborhood-parent/distance process in `sim.py`. Some boundary edges can be directed even for odd \(T\).

Supply ideal observed extrema \((0,n)\) and stored labels \(b_k=k\). Non-worsening max-Chebyshev comparisons, ties accepted, use \(C_k(b)=\max\{k(n-b),(n-k)b\}\). Its unique minimum is at \(b=k\). Consequently observation \(k\) can replace only slot \(k\), and only when \(k\in B_T(i)\); the true child weight \(y\) is stored there. Labels/reference remain pinned, while true correctness need not persist. Before pinning, this single-recipient property is false.

Let \(\mathcal F_t\) reveal the supplied state and consumed masks/gates through attempt \(t\), with no future randomness. All inequalities condition on this pre-proposal history, not on acceptance. Let \(C_t=|\{k:w_k(t)=k\}|\); a *seed* means \(C_t\ge1\). Let \(\tau\) be the number of attempts to the first fully aligned phase-zero sweep boundary, including zero when initially aligned there. Aligned interior states remain live, allowing reinfection. Rejections and unchanged proposals still consume attempts. These are neither historical nor archive coverage times.

At a boundary, attempts equal \(m\) times sweeps. Supplied-state initialization has zero charge. For ordinary initialization, add \(m\) initial noisy evaluations; each subsequent attempted offspring has one shared noisy evaluation, not \(T\) evaluations. Logical recipient comparisons and wall seconds are separate costs. Occupation counts below are attempts, not independent sweep durations. In recorded ordinary runs, U is the first ideal-reference boundary and S is the first boundary with both ideal reference and every stored target label; the attempt-time A defined below need not itself be a boundary.

## Strongest new activation result and its derivation

**Proved, rounds [22](../round-0022/proof.md) and [23](../round-0023/audit.md):** put

\[
d_k=|\{i:k\in B_T(i)\}|,\qquad
\delta_k=1-(d_k+1)p,\qquad
\delta_{\min}=1-(d_{\max}+1)p>0.
\]

For every deterministic attempt horizon \(H\), let \(Z_H\) count unseeded pre-attempt states before \(\tau\wedge H\), and let \(V_H\) count states with exactly one correct slot \(k\) eligible for the next breeder. From **any supplied pinned seeded state**, including the usual corner \(C=(2,1,2,\ldots,n)\),

\[
\boxed{\mathbb E Z_H\le\kappa\mathbb E V_H,\qquad
\kappa=\frac{2(n+1)p(1-p)}{1-(d_{\max}+1)p}.}
\]

This is a workload bound weighted by entrance probability. It is not a bound of \(\kappa\) on the conditional delay after a seed is lost.

The following dependency chain is sufficient; it does not use the earlier artificial-family forest or Taylor-word arguments.

1. For a wrong slot \(k\), set \(v_k(y)=1/D(y,k)\), with \(v_k(k)=0\). On its own turn the expected change is at most \(-(1-2p)\). On an eligible external turn it is at most \(p\), uniformly over that turn's history-dependent parent. The positive wrong-child terms cancel \(D(y,k)\) before summation.
2. At next-breeder phase \(a\), let \(r=(k-a)\bmod m\) and let \(e_k(a)\) count eligible external turns before the next own turn. Set \(g_k(a)=r\delta_k/m+p e_k(a)\). Direct cyclic subtraction gives the phase correction, with \(0\le g_k\le1-2p\). Thus \(\Phi_k=m[v_k(w_k)+g_k(a)]/\delta_k\), killed on repair of \(k\), has expected decrease at least one per live attempt.
3. Put \(W=\min_k\Phi_k\) when \(C=0\), and \(W=0\) otherwise. Choose a minimizer before the fresh draw. Then unseeded states have \(\mathbb E[W_{t+1}-W_t\mid\mathcal F_t]\le-1\). No minimum is exchanged with an expectation.
4. From a vulnerable seeded state with sole correct slot \(k\), parent weight \(x\), and next phase \(a'\), last-seed loss to \(y\ne k\) has probability \(pD(x,y)D(y,k)\). Keeping it attached to \(\Phi_k\) gives

\[
J_t=\frac{mp}{\delta_k}\left[1-D(x,k)+g_k(a')\sum_{y\ne k}D(x,y)D(y,k)\right]\le\kappa.
\]

5. Therefore \(\mathbb E[\Delta W\mid\mathcal F_t]\le-\mathbf1_{C_t=0}+J_t\mathbf1_{\rm vulnerable}\). Summing to a bounded horizon and dropping nonnegative terminal \(W\) proves the boxed bound. Monotone convergence handles increasing horizons; no unproved integrability, tail bound or excursion independence is used.

**Parameter consequence, proved:** \(d_{\max}\le\min(m,2T-1)\). For every fixed \(c>0\), \(p=c/n\) and \(T=o(n)\), the condition holds eventually and \(\kappa=2c+O_c(T/n+1/n)\). In particular it covers \(T=\lceil\sqrt n\rceil\) and \(T=\lceil\ln n\rceil\). The finite sufficient condition \(2Tp<1\) is convenient but not necessary. At full \(T=m\), every inactive gate creates a seed immediately, giving the stronger charge \(p/(1-p)\) for all \(p<1\), without the degree condition. This too concerns reseeding, not simultaneous completion.

**Ordinary-initialization extension, proved with restricted scope:** let \(A\) be the first attempt with ideal reference and all labels pinned, and let \(\tau\) now be the first aligned boundary at or after \(A\). At the decisive pinning transition only one previously missing target can be newly pinned. Let \(R_H\) count pre-\(A\) histories with one missing target eligible for the next breeder. Then

\[
\mathbb E Z_H\le B_{\rm init}+\kappa\mathbb E(R_H+V_H),\qquad
B_{\rm init}\le\frac{mp(1-2^{-n})}{\delta_0}
\]

for independent uniform bit-string initialization with one evaluation each. The initial and final-pinning entrance likelihoods are retained, not conditioned away. This does **not** bound time to \(A\), and this post-pinning endpoint need not equal the first true-exact endpoint.

## The single remaining pinned-runtime obligation

Define seeded work \(Q_H=(\tau\wedge H)-Z_H\). Since \(V_H\le Q_H\), the proved result gives

\[
\mathbb E[\tau\wedge H]\le(1+\kappa)\mathbb E Q_H.
\]

**Open in this checkout:** from the pinned corner, prove a bound \(\sup_H\mathbb E Q_H\le B(n,c,T)\) polynomial in \(n\), with the desired uniformity at square-root \(T\). This one bound would imply \(\mathbb E\tau\le(1+\kappa)B\) attempts. For example, an \(O_c(n^2)\) seeded-work estimate at square-root \(T\) would imply an \(O_c(n^2)\) total attempt bound; that premise is **not proved**. Under ordinary initialization, pre-pinning progress is an additional obligation, so the same statement cannot be advertised as an ordinary-run theorem.

**Proved clean ingredient, not the missing noisy estimate:** for \(n\ge3\), \(T\ge3\), a seeded boundary state with \(e\) errors has clean completion expectation at most \(3ne\) sweeps, or \(m(3ne+1)\) attempts from an arbitrary phase. Bidirectional adjacent edges supply a persistent correct donor; its prescribed one-bit component succeeds with probability \(>1/(3n)\) per visit. Summing conditional stage means proves the bound. Ongoing noise can destroy that donor and introduce errors.

A proposed clean-completion potential must therefore retain signed noisy changes, rejection branches, return states after all-wrong excursions, and the final boundary wait. The positive error-count drift witness in [HISTORY.md](HISTORY.md) rules out an automatic one-step error-count argument. The occupation theorem supplies only the \(W\) part of a possible combined argument; it does not supply the missing drift by itself.

## What the rest of the evidence establishes

| Result | Defensible status and scope |
|---|---|
| Noiseless supplied corner | **Proved:** sweep time is geometric with \(q_T=1-\prod_{i:0\in B_T(i)}(1-D(w_i,0))\). Mean attempts \(m/q_T\sim en^2\) uniformly over \(2\le T\le m\), versus \(en^3\) at \(T=1\), as \(n\to\infty\). Exact equality of \(T=2,3\) at \(p=0\) does not persist universally at \(p>0\). [Theory](../../../../LARGE_T_THEORY.md). |
| Fixed-\(T\) noisy corner | **Proved in the published round-5 audit:** fixed \(c>0\), fixed integer \(T\ge2\), \(p=c/n\), sufficiently large \(n\), expected simultaneous boundary cost \(\Theta_{c,T}(n^2)\) attempts; \(T=1\) gives \(\Theta_c(n^3)\). Supplied corner, ideal reference and pinned labels are essential. This synthesis retains that dependency, not a new full forest audit. [Audit](../round-0005/audit.md). |
| Old forest bound for growing \(T\) | **Proved algebraic consequence conditional on that forest bound:** for \(T=o(n)\), \(O_c(n^2[1+T\exp\{cT+O_c(T^2/n+T/n)\}])\) attempts. Natural-log \(T\) gives \(O_c(n^{2+c}\log n)\); square-root \(T\) gives \(O_c(n^{5/2}e^{c\sqrt n})\). Artificial simultaneous family extinction causes the exponential factor. The new occupation bound does not yet replace the full runtime estimate. [Derivation](../round-0021/proof.md). |
| Clean worst supplied states | **Proved:** for \(n\ge3,3\le T\le m\), with \(a=\lceil(m-T)/2\rceil\), polarized all-wrong states have mean first repair at least \(a!/m\) sweeps. The uniform upper bound is \(4\,2^{a_*}a_*!+3n^2\), where \(a_*=a+\mathbf1_{T\text{ even},\ n\equiv3\ (4),\ T<m}\). Thus logarithmic/square-root neighborhoods still have \(\exp(\Theta(n\log n))\) worst clean means. At full communication the first attempt supplies a seed. This is not a corner/ordinary-initialization lower bound. |
| Ongoing-noise trap | **Proved:** the same polarized supplied family has first-reseeding mean at least \(a!/[(1-p)+p2^a]\) **attempts**. For \(T=o(n),p=c/n\), this lower-bound expression grows as \(\exp((1/2+o(1))n\log n)\). Positive accessibility alone does not yield a lower bound from the corner or uniform initialization; entrance mass matters. [Proof](../round-0022/proof.md). |
| Small-noise \(T=3\) minus \(T=2\) gap | **Proved in earlier audits:** \(pA_n+p^2B_n+p^3C_n+O_n(p^4)\) in sweeps; \(A_n=-(n/2)\log n+O(n)\), \(\lvert B_n\rvert\le1536n^5\), \(\lvert C_n\rvert\le10^{10}n^7\) for \(n\ge3\). Exact \(A_3>0\), \(A_n<0\) checked only for \(4\le n\le10\). No uniform remainder at fixed positive \(c\) follows. [Rounds 7](../round-0007/audit.md), [9](../round-0009/audit.md), [14](../round-0014/audit.md). |
| Fourth-order work | **Partially proved:** RROO, ORRR and RORR have audited polynomial bounds for even \(n\ge4\), \(T=2\); the last was recovered/audited in round 20. These are signed ordered coefficients, not activation-event probabilities. Full fourth gap and isolated-pair second-response candidate remain unresolved. [Round 20](../round-0020/audit.md). |
| Finite-order \(T\ge3\) result | **Proved:** for the corner expansion \(\mathbb E_C\tau_{\rm sweeps}(p)=\sum h_j(C)p^j\), \(1\le j<n\), \(\lvert h_j(C)\rvert\le2^jm^j[3n(j+1)+1]^j/q_T=O_j(n^{2j+1})\), uniformly in \(T\ge3\). At most \(j+1\le n\) errors preserve a seed in intervening clean states. Protection fails at order \(j\ge n\); this is not a uniform remainder or a bound on the \(T=2\) gap. [Round 21](../round-0021/proof.md), [audit](../round-0023/audit.md). |

**Empirically supported, separate ordinary-initialization evidence:** the original \(n=256\), \(p=1/(64n)\), \(T=1\) versus \(T=16\) cost ratio is 2.327639, approximate nominal pointwise 95% bootstrap interval [2.050148, 2.674642], with 24 complete trajectories per primary arm. The separately registered \(n=512\), \(p=1/32768\), \(T=1\) versus \(T=23\) restricted-mean ratio is 2.339095 [2.085387, 2.596468], 32 complete trajectories per arm, horizon 38,341 sweeps. Four separate smoke trials are excluded. All 68 follow-up seeds are distinct and disjoint from the 2,420 seeds checked in the earlier audit. No new outcomes were generated here.

At \(n=512\), mean evaluations were 5,139,185.91 versus 2,197,082.81; q10/median/q90 were 4.507/5.043/5.903 versus 1.592/2.183/2.586 million. Both arms completed 32/32 (Wilson 95% completion interval [0.892821,1]); this does not exclude rare tails. The registered restricted estimand is not an unrestricted expectation merely because this sample was uncensored.

The observed mean phase savings were 4,462.406 sweeps before \(U\), 1,272.563 between \(U\) and \(S\), and 0.125 after \(S\), each based on 32 completed phases per arm. One \(T=1\) path had four post-\(S\) sweeps; all others had zero. Both arms recorded no pinned-endpoint repairs. Thus savings were predominantly pre-\(S\) descriptively, with no causal mediation claim. \(T=23\) saved 57.25% of evaluations but used 9.83 times the logical comparisons. [Round 2](../round-0002/report.md), [receipt audit](../round-0003/report.md), [latest receipt summary](../round-0023/empirical.json).

**Blocked, unchanged:** the original campaign has one valid capped high-noise main trial and 240 missing gate-blocked holdout rows. Missing observations are not censored trajectories. Its original two-stage conclusion remains inconclusive; the separate study does not replace that holdout. The pilot/campaign share 164 smoke/calibration seeds, so they are not independent replications. Campaign \(n=16,T=3\) corner calibration exceeded its pointwise predictive range, whereas the pilot's corresponding sample did not. Both observations and all exploratory reversals remain preserved. [Original interpretation](../../interpretation.md).

## Recovery, verification and changes

**Mechanically checked provenance:** activation [GOAL](../activation-20261112T181239Z-84cbf5/GOAL.md) and [RECOVERY](../activation-20261112T181239Z-84cbf5/RECOVERY.json) supplied context only. The local and GitHub-WIP directories contain byte-identical six-file copies of one interrupted round-20 audit. Their claimed outputs are not independent receipts. Nine advertised files are missing in each copy. Published round 20 supplies a later analytic audit and completed fresh \(n=4\) check; its fresh \(n=6\) recomputation was interrupted and remains unfinished. Published round-19 \(n=6\) evidence is distinct from that incomplete computation. See [HISTORY.md](HISTORY.md).

Round 24 changes only this new bundle: SYNTHESIS, HISTORY, proposed [memory](memory.md), [PROGRESS](PROGRESS.md), [verification code](verify_checkpoint.py), [source inventory](sources.json), and verification/provenance receipts. Existing CLAIMS/STATUS and all evidence are unchanged. No simulator was copied or modified. Source/config fingerprints include the frozen C++ kernel SHA-256 `11bdbd26facb39b22df911d063e1718dd03a2ae8fd01a18458d1c5e8f694df10` and round-1 plan file hashes in the complete inventory. Input HEAD is `eb682871d3d29e7c9373159ecf9605390cd7b8e9`.

Verification commands, run serially using `/Users/parth/miniforge3/bin/python3`, are recorded in [checks.json](checks.json). From this bundle, use a new scratch directory:

```sh
/Users/parth/miniforge3/bin/python3 verify_checkpoint.py --repo REPO --out NEW_SCRATCH
```

The wrapper sets numerical threads to one and runs the required repository unit tests, compilation of `sim.py`, `large.py`, `scripts/run_research.py` and this verifier, and round-23's exact rational certificate verifier. It also verifies recovery hashes, protected entries and publication-relative links. It does not run an experiment, draw new bootstrap samples, solve new numerical systems, or rerun all historical grids. Existing deterministic/stochastic unit-test fixtures are regression tests, not new scientific samples.

The certificate replay's exact scope is \(n=2,3\), every \(T=1,\ldots,n+1\), \(p=1/(64n),1/(4n)\): 14 cells, all 8,664 live phase states, and 5,928 seeded-start occupation enclosures. It kills only aligned phase zero, leaving aligned interior states live. Exact residuals certify pre-existing rational proposals without NumPy or a new floating solve. The larger geometry, global \(W\), Taylor and receipt grids quoted in HISTORY are earlier checks, **not newly rerun** here. The fresh replay passed 95 repository tests and compilation, then certified all 14 cells and 8,664 phase states in 18.347 seconds total wrapper time (0.892 seconds for certificate verification). All 602 protected tracked entries remained unchanged. Final work elapsed time and command outcomes appear in [PROGRESS.md](PROGRESS.md) and checks.json; no unexecuted check is called passed.

No paid resources, cloud jobs, parallel agents, commits, pushes, remote modifications or scientific samples were used. A preliminary inventory guard stopped on an existing tracked skill symlink; the corrected inventory hashes link text without following it. Draft Markdown equation escaping was also corrected before final document checks. No evidence was altered. Private execution logs and the revised manuscript appendix remain unavailable; neither is treated as a premise. The comparison with Benjamin Doerr, Moaad Elmoutassim, Martin S. Krejca and Guy Mushiata Kibulu, *Understanding the Co-evolutionary Solution Exchange of the MOEA/D: Already the Smallest Communication Radius Gives the Best-Possible Speed-Up* (2026), arXiv:2610.35373, DOI:10.48550/arXiv.2610.35373, remains the repository's [prior source comparison](../../../../PAPER_COMPARISON.md). No fresh external claim or theorem transfer is made here.

## Handoff and strongest falsifier

**Strongest falsifier of the retained positive result:** an admissible pinned phase state with \(\delta_{\min}>0\) violating
\(W-\mathbb E W_{\rm next}\ge\mathbf1_{C=0}-J\mathbf1_{\rm vulnerable}\), or a valid final-pinning entrance newly pinning multiple targets. No such witness is present in the audited finite coverage; this is not an all-state proof by enumeration.

**Strongest existing interpretation falsifier:** at \(n=3,T=3,p=1/192\), weights \((3,1,0,0)\), next breeder 1, the conditional reseeding delay after last-seed loss is at least 1.4185754517 attempts, whereas \(\kappa=191/4488\approx0.0425579323\). The entrance probability is \(47/46656\). This disproves deleting the entrance weight, not the occupation theorem. The all-wrong trap family separately refutes uniform polynomial conditional reseeding at growing \(T\).

**Proposed next bounded question, not executed or preregistered Monte Carlo:** for the exact pinned \(n=3,T=3,p=1/192\) process, test all 1,023 live population/phase states for a scalar \(\lambda\ge0\) making \(F=H_{\rm clean}\mathbf1_{C\ge1}+\lambda W\) have strictly negative noisy drift. \(H_{\rm clean}\) must be in attempts and stop only at aligned phase zero. Solve the resulting rational interval constraints on \(\lambda\); save a feasible certificate or incompatible-state witnesses. This tests a specific bridge to seeded work before spending another activation on an all-\(n\) argument. Failure would reject this potential family only. No new samples or resumption of the blocked holdout are needed.
