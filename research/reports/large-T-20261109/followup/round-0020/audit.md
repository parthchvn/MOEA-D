# Round 20: fresh-context recovery audit of RORR

## Verdict and evidence boundary

**Proved under the assumptions below:** the [round-19 candidate](../round-0019/proof.md) has a valid baseline decomposition and retains both required entrance factors. With m=n+1, L=20n and q=1−(1−d(2,0))(1−d(1,0)),

\[
|\mathrm{RORR}|\le1024m^3L^4/q
\le3{,}932{,}160{,}000n^8<4\cdot10^9n^8
\]

in **sweep units**, for even n≥4. This is one ordered fourth response, not a runtime bound at positive p and not the complete fourth-order coefficient. Multiplying by m changes this coefficient bound to attempt units.

This verdict follows from the analytic audit below, independently reconsidered in a fresh context by the sole writer. It does not inherit the recovered WIP's “proved” label. There is no second model/agent review. The recovered solver and tests are explicitly reused, not misrepresented as newly authored independent software. Fresh exact checks are separate evidence.

**Mechanically checked recovery:** twelve inventory entries (two identical copies of six files) match their SHA-256 and lengths. Both published round-18/19 manifests match, 15 artifacts apiece. The WIP has **no** preserved verification.json, dependency.json, checks.json, provenance.json, words.csv, baseline.csv, phases.csv, entrances.csv or branches.csv. Consequently its claims of completed finite grids, dependency replays and preservation checks are unsupported by recovered receipts. The present run supplies new, bounded receipts. Details: [recovery.json](recovery.json), [targeted.json](targeted.json).

## Exact process and response

**Definitions.** Supply C=(2,1,2,…,n), reference (0,n), and stored labels b_k=k, without initialization charge. In ascending repeated cycles 0,…,n, breeder i mutates its own incumbent using independent per-bit probability 1/n. A fresh Bernoulli(p) gate activates an independent observation mask with the same bit probability. One shared observed weight is offered to the filled-cardinality T=2 neighborhood: even breeders prefer right, odd breeders left; fill from the valid side at endpoints. For even n the pairs are {0,1},…,{n−2,n−1}; breeder n also offers to n−1. Only breeder n can change orphan slot n. This matches first_recipient and cost in the repository's neighborhood_sweep.cpp at the pinned reference, not sim.py's parent/fitness rules or large.py's radius parameter.

At ideal reference the cost is max{k(n−w),(n−k)w}, uniquely minimized by w=k. Pinned recipient k therefore accepts exactly observation k and stores the child's true weight. Clean updates only delete errors. With noise, correct true weights need not persist. Mutation and observation weights use the same kernel d, because each independent mask's conditional weight law depends only on the input weight, not genotype identity.

Let F_t reveal the supplied state, next breeder phase I_t and consumed masks/gates through completed attempt t. Condition before proposals; fresh masks retain their unconditional law. No distribution of retained noise or accepted labels is assumed. Let τ be the number of attempts until the first fully aligned **phase-zero boundary**. Fully aligned interior states are live. The reward is 1/m per live attempt. No drift theorem or tail bound is used.

Let a*=(A_n,0), A_y=(0,1,…,n−1,y), P the unrestricted clean population/phase kernel, K its live restriction killed at a*, and G=(I−K)⁻¹. For each fixed n, own-repair probabilities are positive and clean errors never increase. Successive stages give finite mean absorption, so G exists. Extend response functions by zero at a*, not at aligned interiors.

Write the unrestricted activated-minus-clean difference as R+O, split by regular/orphan recipient. These are differences of stochastic recipient-restricted kernels, not separate noise gates. A shared observation can equal at most one pinned target, so the split is exact, including breeder n. At successor phase j=(i+1) mod m,

\[
R_i f(s)=\sum_{k\in B_2(i),k<n}
\left[\sum_x d(s_i,x)d(x,k)\{f(s^{k\leftarrow x},j)-f(s,j)\}
-d(s_i,k)\{f(s^{k\leftarrow k},j)-f(s,j)\}\right].
\]

Both unchanged and suppressed-clean terms remain. Set H₀=G(1/m), H₁=GRH₀, H₂=GRH₁, J=GOH₂. Chronological order gives RORR=e_C GRJ. At fixed n this is the ordinary p⁴ ordered-word contribution to the finite killed resolvent; there are no factorials. It is signed, not the probability of four activations. Fixed-n analyticity supplies no uniform-in-n remainder.

## Reaudit of the marked premise

**Proved.** Here is the needed content of [round 18](../round-0018/audit.md), rederived rather than assumed from its status label. Define B_j(y,i)=H_j(A_y,i), D_j(s,i)=H_j(s,i)−B_j(s_n,i), g₀=1/m, g_j=RH_{j−1} and λ_j=Σ_i g_j(A_n,i). Then λ₀=1 and the zero extension satisfies

\[
H_j=g_j+PH_j-\lambda_j1_{a^*}.
\]

At aligned interior phases this is the remaining suffix sum of g_j; at phase zero the subtracted λ_j makes the zero extension valid. P here is **unrestricted**. R preserves the orphan and has row sum zero, hence RB_j=0 at each matched successor phase, also across the wrap to phase zero.

Couple the actual clean population and A_y using their common autonomous orphan trajectory Y_t. At breeder n use the same child, preserving last-pair/orphan dependence. Let ρ be the first regular-complete phase-zero boundary (zero if already such a boundary). Subtraction and stopped telescoping give

\[
D_j(s,i)=E\sum_{t<\rho}\left[g_j(S_t,I_t)-g_j(A_{Y_t},I_t)
+\lambda_j1_{\{Y_t=n,I_t=0\}}\right]. \tag{A}
\]

Before regular completion the actual chain cannot visit a*. After mid-sweep regular completion both population terms coincide and there is no further phase-zero instant before ρ, so no spurious compensation is paid. Fixed-n functions are bounded; finite mean regular completion justifies truncation and passage to the limit. In particular D₀≥0 is the expected number of correct-orphan phase-zero instants before regular completion.

Count surviving generic regular overwrites, excluding the original slot-0 value 2. Through three overwrites there are at most four regular errors and at most one slow pair: a slow pair means both members wrong, except the first pair with its original 2. Two slow pairs require four generic overwrites. This budget is used only through three; it is not extended to RRRR.

A correct adjacent donor gives its neighbor's target with probability at least 1/(3n) per scheduled visit, using the one-bit component and (1−1/n)^(n−1)>1/3. In the exceptional first pair, slot 0 at weight 2 proposes target 1 at rate at least 2/(3n); if slot 0 repairs earlier, its now-correct weight 0 still supplies target 1 at rate at least 1/(3n). Clean successes persist. At most four successive extensions, plus phase/boundary slack, fit in L=20n expected sweeps. This argument bounds conditional delays directly; it does not presume a pathwise monotonic coupling after deleting orphan help.

For a slow pair with own-repair rates a,b, values remain fixed until the first repair. Complete-sweep failure is at most (1−a)(1−b); any external repair already constitutes escape. Its escape rate is at least (a+b)/2. After escape at most three fast extensions remain. Thus both expected attempts/m and phase-zero counts, uniformly along clean descendants and in orphan value, are bounded by

\[
M=L+2/(a+b).
\]

A good state uses M=L. With at most two previous generic overwrites, a new birth cannot create a second slow pair. If it changes/creates the slow pair, its acceptance b multiplies the new inverse rate: 2b/(a+b)≤2. Events outside a preexisting slow pair retain the old bound. Summing at most two recipient mutation rows gives active E[D₀]≤M+4 and clean E[D₀]≤M. Nonnegativity therefore gives |g₁|≤2M; at a regular-correct baseline |g₁|≤L and |λ₁|≤mL. Equation (A), using attempts≤mM and boundary counts≤M, implies

\[
|D_1|\le4mM^2\le5mM^2. \tag{B}
\]

A corner/aligned origin with one marked regular overwrite k←x is good. If a subsequent birth creates a slow pair, it must corrupt the marked value's partner; a birth replacing the mark itself leaves a good state. With a=d(x,k)>0 and second acceptance b,

\[
b\{L+2/(a+b)\}^2\le2L^2+2/a,
\]

because b/(a+b)²≤1/(4a). Keep b before summing the fresh mutation rows in (B). The active and clean absolute D₁ expectations are bounded by 5m(5L²+4/a) and 5mL². Hence |g₂|≤32m(L²+1/a). For an unmarked corner/subset or A_y all one-birth successors are good, giving |g₂|≤10mL² and |λ₂|≤10m²L². The once-marked clean duration is ≤L, so (A) gives

\[
|D_2(s,i)|\le52m^2L^3+32m^2L/a
\le C(a):=64m^2L(L^2+1/a). \tag{C}
\]

Unmarked states satisfy |D₂|≤64m²L³. All phases and orphan values are covered. If the marked error has repaired, use the unmarked estimate and retain the old positive a harmlessly. No isolated-pair second-response conjecture is needed.

## Baseline and both entrance factors

**Proved.** At A_y, y<n, clean regular slots remain correct; orphan repair occurs only at its final turn with rate d_y=d(y,n). Its phase-zero mean life is 1/d_y sweeps. Since H₂=Gg₂ and baseline |g₂|≤10mL²,

\[
|B_2(y,0)|\le10m^2L^2/d_y,
\quad B_2(n,0)=0.
\]

This uses a first occupation moment, not a higher residence moment. Before O in RORR the orphan is correct. A wrong child y observed as n has actual entrance c_y=d(n,y)d_y. Its negative unchanged coefficient is −Σ_{y<n}c_y. Define

\[
\beta=\sum_{y<n}c_yB_2(y,0),\qquad
\Gamma(s)=\sum_{y<n}c_y\{D_2(s^{n\leftarrow y},0)-D_2(s,0)\}.
\]

The exact final-turn decomposition is OH₂(s,n)=β+Γ(s). Multiplying before summing cancels the orphan inverse:

\[
|\beta|\le10m^2L^2\sum_{y<n}d(n,y)\le10m^2L^2.
\]

Taking a supremum over y first would discard the factor that makes this polynomial. Equation (C) gives |Γ|≤2C(a), or 128m²L³ unmarked. If regular slots are all correct then Γ=0, including the orphan-fed last pair.

After the first R only one generic regular overwrite exists and the orphan stays correct. There are at most two regular errors and no slow pair. Two successive fast extensions, partial-phase and boundary slack give N(s,i)≤6n+2≤L, where N is expected visits to breeder n before τ. Integrating the decomposition therefore gives

\[
J(s,i)=\beta N(s,i)+E\sum_{t<\tau}1_{\{I_t=n\}}\Gamma(S_t),
\qquad |J(s,i)|\le V(a):=138m^2L^2(L^2+1/a).
\]

Unmarked states have |J|≤U:=138m²L⁴. The final breeder turn is counted even if alignment occurred earlier in the sweep. Pathwise τ=mN_path−i, hence N=H₀+i/m. R kills the successor-phase constant (zero at the killed wrap), so the baseline contributes exactly βH₁(C,0) to RORR. It is not generally zero.

For the first R use the positive stochastic kernels P_R⁺ and P_R⁰. Each accepted mark has probability d(s_i,x)a; unaccepted observations leave an unmarked state. Accepted diagonal events are counted within these probabilities, not added twice. Retaining a until after applying V(a), and using at most two recipient rows,

\[
P_R^+|J|\le U+138m^2L^2\sum_{k,x}d(s_i,x)(aL^2+1)
\le690m^2L^4.
\]

The clean branch stays unmarked, P_R⁰|J|≤U, so |RJ|≤828m²L⁴≤1024m²L⁴. The parent can depend on previous repairs; only its fresh conditional mutation row sum is used. No selection-biased parent distribution is assumed.

Both entrances can also be retained pointwise:

\[
a c_y\bigl(|H_2(s^{n\leftarrow y},0)|+|H_2(s,0)|\bigr)
\le d(n,y)\{10a m^2L^2+128m^2L d_y(aL^2+1)\}.
\]

The second absolute value pays the negative unchanged O branch. There is no surviving 1/a or 1/d_y. Before the first insertion the clean corner lives for exactly 1/q sweeps, so e_C G1=m/q. Multiplying the phasewise RJ bound by this occupation mass proves the verdict. Finally m≤2n and q≥d(1,0)≥1/(3n) give the displayed numerical constant.

## Contradictions, missing inputs and scope

**Contradicted shortcut:** setting B₂ to zero inside O loses βH₁(C). At n=4 the correct RORR is approximately 0.158278329276, whereas omission gives −1.803253923193; the missing term is 1.961532252469. At n=6 the corresponding values are 0.270057708937, −3.515361728199 and 3.785419437136. The n=4 fresh exact fingerprint is in [words.csv](words.csv); n=6 is reused after published hash/schema verification, not claimed as a completed new calculation. Both original witnesses are in the [published shortcuts](../round-0019/shortcuts.csv). This is the strongest direct falsifier of an oversimplified baseline argument.

**Mechanically checked scope obstruction:** state (3,0,0,0,4) has two slow pairs and needs four generic overwrites, outside the lemma's three-overwrite budget. The [published positive path](../round-0018/audit.md) realizes it. Last-pair/orphan independence is also false; the recovered literal-mask test retains marginals 3/64,1/256 and intersection zero at (0,1,2,0,0), breeder 4.

**Missing inputs:** WIP completion receipts and its claimed nine outputs are absent. The revised external manuscript appendix mentioned by early rounds and earlier private trial logs are not supplied. Neither is needed for this self-contained RORR argument; neither is silently certified. The base STATUS/CLAIMS files lag the published round supplements. All proposed updates are in [memory.md](memory.md); existing evidence is unchanged.

**Unresolved in this project, not newly surveyed literature:** the complete fourth-order gap, a useful uniform remainder, positive-fixed-c ordering at p=c/n, larger T and ordinary initialization. No Taylor coefficient sign is promoted to a finite-noise result. No noisy theorem is imported from the noiseless radius/archive paper; [PAPER_COMPARISON.md](../../../../PAPER_COMPARISON.md) records those model differences. Novelty is **UNVERIFIED** because no current external search was conducted. The old blocked holdout remains blocked, and no new stochastic samples were taken.

A failed marked-state support claim, compensated phase equation, positive-kernel bound, retained entrance factor or exact word match would falsify the associated step. The finite checks below cannot prove the all-n result; the preceding argument supplies it.

## Completed verification and reproduction

**Mechanically checked in this activation:** 95 repository tests and 17 recovered tests passed; seven Python modules compiled. The final bounded wrapper completed in 22.987 seconds, including a 3.870-second exact n=4 grid. That grid checks 200 marked cases, 1,000 marked phases, 160 joint entrance envelopes, 25 baseline phases and 10 positive-kernel rows: 460 exact equalities and 1,738 inequalities, with one published word and five baseline fingerprints matched. Additional states are solved recursively but not reported as exhaustive tested coverage.

The new independent support check covers 55,939 unique regular configurations across n=4,6,8, 711 marked descendant cases and 2,170 slow-pair-producing second-birth cases. The published schemas retain 664 joint entrance rows, 788 marked phase rows, 12 baseline rows, 24 branch rows and two word/shortcut rows; 1,464 entrance/mark fields are checked as exact fractions. Both recovered source copies and 30 published manifest artifacts match.

**Unfinished preliminary computation:** a combined n=4,6 run was deliberately interrupted during n=6 arithmetic with no completed output files; there was no assertion failure. Its partial stdout is not used as a certificate. The final n=4 run above is separate. Published n=6 exact results are reused after hash/schema checks, with no claim of a fresh n=6 response grid. The generic scope string emitted by the recovered solver describes its supported grids; the actual ns=[4] field and these counts specify this run.

[checks.json](checks.json) records actual stages and interruption; [provenance.json](provenance.json) records source/config hashes and preservation. [README.md](README.md) and [reproduce.py](reproduce.py) give a bounded serial rerun. No historical theoretical grids or empirical bootstrap studies were recursively replayed.
