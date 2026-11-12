# Independent audit of the cubic acceptance and orphan arguments

**Verdict: proved under the supplied pinned-model assumptions, with the
interior-phase local hitting function specified explicitly below.** The
round-13 candidate polynomial estimate survives this independent analytic
audit:

\[
 m_3(n,p)-m_2(n,p)=pA_n+p^2B_n+p^3C_n+O_n(p^4),
 \qquad |C_n|\le10^{10}n^7\quad(n\ge3).
\]

The conclusion follows from the argument here, not extrapolation of finite
calculations. This is an independent implementation and review in a later
round, not an additional concurrent reviewer. The proof does not bound a
uniform fourth-and-higher remainder, establish ordering at p=c/n, or concern
ordinary initialization. The earlier exponential higher-residence obstruction
is retained. Exact calculation results are separately **mechanically checked**
in [verification.json](verification.json).

## Model, information, and coefficient identity

**Definition.** Fix n>=3, T=2 or 3, m=n+1. Supply ideal extrema (0,n), pinned
labels b_k=k, and true weights C=(2,1,2,...,n), at zero initialization cost.
Ascending cyclic breeder i mutates its own incumbent, independently flipping
bits with probability 1/n. A fresh Bernoulli(p) gate activates an independent
second mask of the same rate for observation. One observation is offered to
the filled cardinality-T neighborhood, with even breeders preferring the
right and odd breeders preferring the left. Invalid indices are skipped.
This is not a clipped-radius neighborhood. Pinned max-Chebyshev selection
accepts observation k only at recipient k, storing the child's true weight.

The filtration F_t contains the supplied state and consumed masks/gates
through attempt t. All expectations below condition before a proposal or at
the stated stopping time; no acceptance-conditioned noise law is used. The
stopping time is the first full sweep boundary with simultaneous true target
assignment. Aligned interior-phase states are retained. Rewards of 1/m per
attempt measure time in sweeps; attempts multiply the result by m. No drift
theorem, tail-from-mean inference, or external theorem transfer is used.

**Proved.** Write the attempt kernel as K_i+p Delta_i, with K clean and
Delta=J-K activated minus clean. Include next breeder phase in the state and
kill only at an aligned phase-zero boundary. The clean occupation matrix G
is finite: own repair probabilities are positive and clean errors only
disappear. The finite-state response is analytic around p=0. With h0=G(1/m),
the cubic coefficient for one arm is

\[
 c_T=e_CG\Delta G\Delta G\Delta h_0.                 \tag{1}
\]

An insertion maps phase i to phase i+1 (mod m). This convention includes
within-sweep placements and never inserts twice at one attempt. Let

\[
 q=1-(1-d(2,0))(1-d(1,0)),\quad L=20n,\quad
 Z=m^3(L+1)^3/q,
\]

where d is the standard-bit weight kernel. For T=2 and 3 the clean corner
visits only itself at unsolved boundaries, so e_CG has mass m/q. Also
q>=d(1,0)>=(3n)^{-1}. In even-n T=2, split Delta=R+O by accepted recipient:
O changes only orphan n, and only breeder n has such an operator. R changes
the nonorphans. Each is the difference of two stochastic recipient-restricted
kernels, has row sum zero, and row norm at most two. This algebraic split
does not assume independent gates or independent last-pair/orphan evolution.
An ordered word XYZ denotes e_CG X G Y G Z h0, not a probability of exactly
three noisy events.

## Two entries into a slow pair

**Proved clean geometry.** At n>=4, T=3 states needed in (1) have at most
four errors and at least one correct site. Correctness spreads across each
adjacent edge with conditional probability at least 1/(3n) per scheduled
correct-donor visit. Four successive extensions give at most 12n+1 sweeps
from any phase, hence less than L. This is a sum of conditional waiting
means, not a maximum estimated from individual means.

T=2 forms pairs {0,1},{2,3},...; at even n the last pair also receives breeder
n. Omit this extra repair opportunity when bounding nonorphan completion.
The original error (0,2) is special: even if 1 is wrong, breeder 0 repairs 1
with probability at least 2/(3n) while its weight is 2, or at least 1/3 if
0 has already repaired. Thus a pair with original weight 2 at slot 0 is fast.
Call a configuration good if every other erroneous pair has a correct partner.
At most four good errors require at most four successive extensions. This
bound is uniform over the orphan value and its future evolution; it uses
the nonorphan pair's own fresh proposal randomness.

After two arbitrary nonorphan overwrites, there can be at most one bad pair.
For its true values x,y at targets k,l, set a=d(x,k), b=d(y,l). Until its first
repair those values stay fixed. The two own turns give escape probability at
least (a+b)/2 per full sweep. Afterwards all remaining errors are good. The
bound

\[
 M(a,b)=L+2/(a+b)                                      \tag{2}
\]

covers remaining clean mean, the mean count of relevant orphan turns, and
all clean descendants from every phase, uniformly over orphan evolution.
For precision, the first escape costs at most 1+2/(a+b) boundaries and at
most three subsequent good extensions cost 9n+1; allowing one further
boundary for a partial-phase count is still below (2). A good state uses M=L.

**Proved two-entry weighting.** An erroneous overwrite of k by x has positive
coefficient d(parent,x)d(x,k). Negative repair and diagonal coefficients
cannot create a bad pair. Two bad arbitrary values require two surviving
erroneous overwrites to distinct recipients; their acceptance factors are
exactly a and b. Before the second insertion every continuation is good.
This remains true when a clean transition deletes either earlier error, and
when the first overwrite replaces the original corner error itself.

For 0<a,b<=1,

\[
 ab\{L+2/(a+b)\}^2\le(L+1)^2,\qquad
 b\{L+2/(a+b)\}^2\le2L^2+2/a.                        \tag{3}
\]

The first follows from ab<=1, ab/(a+b)<=1/2 and
ab/(a+b)^2<=1/4. For the second, use (u+v)^2<=2u^2+2v^2
and b/(a+b)^2<=1/(4a). No polynomial lower bound on a or b is needed.
The remaining mutation factors are summed *after* (3). At the second birth,
the parent may depend on the first child; its conditional mutation row still
sums to one, so this dependence does not invalidate the summation.

Consequently, if a phase function F is bounded by U on good states and by
V(M) on bad ones after the second insertion,

\[
 |e_CG R G R F|
 \le {m^2L\over q}\{4U+4\sup_{a,b}abV(M(a,b))\}.       \tag{4}
\]

The two occupation masses before the insertions are at most m/q and mL.
Good paths use two signed row norms, giving 4U. Bad paths are both positive
births, have at most two recipient choices per attempt, and retain ab.
Paths that lose an error become good. The inequality also applies after
subtracting from F any phase function annihilated by the second R.

With the orphan kept correct, the first R response H=G R h0 obeys
|H|<=3mL^2 on good states and |H|<=3mM^2 on bad ones needed here. To see this
without discarding acceptance, an overwrite inside the bad pair contributes
at most 2 per possible recipient to its extra escape wait:
d(z,k)2/(d(z,k)+b)<=2. An overwrite outside it adds only good errors at
this insertion budget. A restricted activated expectation is at most M+4;
the corresponding clean expectation is at most M. Their difference is at
most M+4<=3M, because both expectations are nonnegative. Multiply by clean
occupation at most mM. Applying (3)-(4) gives |RRR|<=24Z, for odd and even n.

## The orphan excess, including the phase correction

**Proved boundary identity.** Put R noise to zero and give O a parameter v.
For sufficiently small **nonnegative** v the split chain is stochastic.
This qualification matters: negative v creates negative off-diagonal entries;
stochasticity is not claimed on a two-sided real neighborhood. Analytic
identities subsequently extend around zero by finite-state algebra.

The orphan is autonomous, with one-turn boundary kernel A(v) and invariant
law nu_v=(1-v)delta_n+v d(n,cdot). Detailed balance follows by the reversible
weight identity binom(n,x)d(x,y)=binom(n,y)d(y,x). If f_v is its first boundary
hitting mean with f_v(n)=0, then on the unrestricted local chain

\[
 (I-A(v))f_v=1-e_n/\nu_v(n).                           \tag{5}
\]

Let rho be the first boundary with all nonorphans correct, allowing rho=0.
They remain correct with R disabled. Optional summation of (5) through rho
and the strong Markov property give

\[
 h^O(E,y;v)=f_v(y)+e_v(E,y),\qquad
 e_v(E,y)={1\over\nu_v(n)}
 E^v_{E,y}\sum_{t<\rho}1_{\{Y_t=n\}}.                 \tag{6}
\]

No independence of rho and Y is assumed. For each fixed n, f_v is bounded on
the finite state space, and E rho<=M for these nonorphan states. Thus stopped
summation is justified by truncation and integrable stopping; no tail bound
is imported. The chain killed at rho has a sweep kernel affine in v, since
O occurs only on the final attempt. Its clean inverse has row norm <=M and
its derivative norm <=2. With b=1-d(n,n), expansion of both that inverse and
(1-bv)^{-1} bounds boundary excess coefficients by M, 3M^2, 7M^3 through order 2.

**Required phase specification.** At phase i>0 the next orphan turn is still
pending. Its local first-*future*-boundary hitting function is

\[
 F_v^{(0)}(y)=f_v(y),\qquad
 F_v^{(i)}(y)={m-i\over m}+(A(v)f_v)(y)
 =f_v(y)-{i\over m}+{1_{\{y=n\}}\over\nu_v(n)}.        \tag{7}
\]

The formula does not replace aligned phase-zero killing by interior killing.
For i>0 it charges the pending suffix even when the orphan is currently
correct. Let S_i(v) be the unrestricted suffix operator. Subtracting (7)
from the population phase value gives precisely S_i(v)e_v. The suffix has
constant-part norm 1 and linear-part norm at most 2; it contains at most one
O insertion. Therefore, at **every** phase, the excess coefficients satisfy

\[
 |e_0|\le M,\qquad |e_1|\le5M^2\le64M^2,\qquad
 |e_2|\le13M^3\le512M^3.                              \tag{8}
\]

At an attempt ending at phase i+1, R F_j^(i+1)=0 exactly: R leaves the orphan
unchanged and has row sum zero. The wrap from n to phase zero uses f_j, not
the interior expression. This is the phase-aware cancellation used below.

**Contradicted shortcut, not a counterexample to the bound:** subtracting the
unshifted boundary f0 at an interior phase does not give a nonnegative excess.
At n=4, only the orphan wrong with weight 0, next breeder 1, f0(0)=256 while
the phase mean is 255.8; their difference is -1/5. Subtraction of (7) gives
the correct excess zero. The previous code's phase-to-phase subtraction
already used this correction implicitly; the written all-phase argument
must define it, especially when invoking nonnegativity.

**Proved predictable-count improvement.** For y<n let d=d(y,n). In a clean
continuation let sigma be the first orphan-repair boundary. Count orphan
turns while it is still wrong and nonorphan errors are still present just
before the proposal. The counting indicator is F_(t-1)-measurable, so the
probability of success at one of these turns is d times their expected count.
An orphan success observes n and cannot simultaneously repair a nonorphan.
After that boundary the nonorphan remaining mean is <=M; the count mean is
also <=M by the explicit phase slack in (2). Clean correctness persists.
Hence the excess in joint completion over the same local hitting function is

\[
 0\le e_0^{(i)}(E,y)\le dM^2.                         \tag{9}
\]

This includes the orphan-fed last pair: the proposal's predictable success
hazard, not independence of the two repair times, is the justification.
For two continuations with the same wrong orphan, their excess difference
lies in an interval of width d M_max^2. No second residence moment is inferred
from a mean.

## A marked first overwrite and the R response

**Proved.** Let H=G R h0. For a clean subset of C and any orphan weight/phase,
|H|<=K=64mL^2. If an additional arbitrary nonorphan overwrite x at k is present,
write a=d(x,k). Then the round-13 estimate holds at every phase:

\[
 |H|\le32m(L^2+1/a).                                  \tag{10}
\]

Here is a direct bound with spare constant. Before a wrong orphan repairs,
R cancels the local term in (7). A further R birth either leaves a good state
or creates a bad pair containing the marked error. For birth value z with
acceptance factor b'=d(z,l), (3) and (9) bound its contribution to the absolute
overwrite-minus-stay difference by
d d(parent,z)(2L^2+2/a). There are at most two recipients. The negative clean
repair part has total coefficient mass <=1 and contributes at most dL^2.
Thus the forcing magnitude is <=5d(L^2+1/a). If the marked error disappears,
the same bound remains valid using its remembered a.

Expected attempts before the next orphan-repair boundary are <=m/d from
any phase. At that stopping boundary the remaining nonorphan state is good.
With the orphan now correct, the restricted active expectation of a clean
completion value is <=L+4, and the clean expectation <=L. Therefore the
remaining R response is at most 2mL^2. Altogether this gives
7m(L^2+1/a), already smaller than (10). If the orphan starts correct, only
the latter bound is needed. Without a marked error, every one-insertion
continuation is good: the same argument gives at most 3mL^2, safely below K.

No noisy-residence expectation is substituted for the clean occupation in
these estimates. This distinction is essential because the operators are
Taylor coefficients at zero.

## Each of the six mixed cubic words

**Proved common entrance estimate.** From a correct orphan, an O birth of y<n
has coefficient c_y=d(n,y)d(y,n); the other branch is the negative unchanged
state. If a forcing is bounded by B on the baseline corner/orphan family,
then its post-O clean occupation is bounded by m(L+1/d(y,n)), versus mL on
the unchanged branch. Consequently

\[
 \sum_{y<n}c_y m\{1/d(y,n)+2L\}\le m(1+2L).            \tag{11}
\]

This retains the acceptance factor before bounding occupation. After this
first O the nonorphan state is only the original corner or its clean subset.

| Word | Audited bound | Cancellation and occupation used |
|---|---:|---|
| RRO | 512 Z | The second R annihilates the phase-local coefficient F1; apply (4) to e1, with U=64L^2 and V=64M^2, then (3). |
| ROR | 1024 Z | After the first marked R, (10) bounds O H uniformly in orphan weight; the first R acceptance cancels 1/a. Details below. |
| ROO | 1024 Z | The first R annihilates F2. Its good continuations have |e2|<=512L^3, so its signed norm and initial occupation give 1024mL^3/q<=1024Z. |
| ORR | 1536 Z | Bound R H on the baseline corner/orphan family by 512mL^2 using (10); then apply (11) and initial m/q. |
| ORO | 384 Z | R annihilates F1. Its continuations are good, so |R e1|<=128L^2. Apply (11) and initial m/q, giving at most 384m^2L^3/q<=384Z. |
| OOR | 384 Z | |O H|<=2K=128mL^2 on the baseline corner/orphan family. Apply (11) and initial m/q. |

For ROR, following a marked first R the orphan is still correct. Until O
occurs all regular configurations stay good, so clean occupation is <=mL.
Use 64m(L^2+1/a) uniformly on descendants in (10), also after the marked
error disappears. It follows that

\[
 |G O H|\le128m^2L(L^2+1/a).
\]

For the initial R's positive wrong overwrites, sum its two possible recipients
and their mutation probabilities with the acceptance a. This contributes
at most 256m^2L(L^2+1). The unchanged and negative repair terms contribute
at most 3(128m^2L^3). Since L>=1 their sum is <=1024m^2L^3;
multiplication by m/q proves the table entry. Dependence of the parent on
prior clean repairs does not affect any conditional row-sum bound.

For ORR, an R birth from the baseline family gives a marked state. Summing
its acceptance-weighted (10) over at most two recipients contributes at
most 64m(L^2+1). The unchanged/clean-repair terms add at most 3K.
Their sum is below 512mL^2. Equation (11), the initial mass m/q and
1+2L<=3L prove 1536Z. These calculations include the negative diagonal
and suppressed-clean-repair terms; merely bounding the positive births
would be insufficient.

All six arguments are phase statements. In particular, no R insertion is
commuted across O, and an O insertion cannot occur twice within one sweep.
Last-pair feedback is allowed in every excess and clean-occupation bound.

## Pure words and the final constant

**Proved.** RRR is bounded by 24Z as above. In OOO only the orphan is noisy;
the original corner has an independent geometric(q) repair clock. The local
Poisson identity (5), or summing it at that independent clock, gives

\[
 m_O(v)={[(I-(1-q)A(v))^{-1}]_{nn}\over\nu_v(n)}.
\]

The clean discounted inverse has norm 1/q and the derivative of A has norm
<=2. Expanding the inverse and (1-bv)^{-1}, the degree-three coefficient
is bounded by 4(2/q)^3/q=32/q^4. The undiscounted, potentially exponential
local hitting function is never bounded here.

For T=3, the clean mean is <=L throughout the needed error budget. Successive
phase occupation bounds in (1) give |c3|<=8m^3L^3/q; the previous looser
18Z also holds. For odd n the T=2 contribution is only RRR. For even n,
the seven R-containing constants sum to 4888. Therefore, in either parity,

\[
 |C_n|\le10000\,{m^3(20n+1)^3\over q}+{32\over q^4}
 <10^{10}n^7\quad(n\ge4).                              \tag{12}
\]

Indeed m<=2n, 20n+1<=21n and 1/q<=3n make the first term at most
2,222,640,000 n^7 and the second at most 2592n^4. At n=3 the independent
phase recurrence matches both published exact cubic fractions, verifying
the finite exceptional case. C is the coefficient of p^3, hence one sixth
of the third derivative, in sweep units.

## Reproducibility, limits, and falsifiers

**Mechanically checked:** [audit.py](audit.py) imports no earlier solver. It
uses full population tuples, a per-bit generating polynomial for mutation,
direct active/clean recipient kernels, and a backward affine cycle of phase
Poisson equations. A separate stopped-reward calculation verifies (6).
[test_audit.py](test_audit.py) uses literal genotype masks and max-Chebyshev
comparisons as an additional transition oracle. See [README.md](README.md)
for exact counts and replay commands. No statistical intervals or censoring
apply to these rational calculations.

**Mechanically checked dependencies:** the recursive round-11 replay checks
rounds 1-11, including committed registration, receipts, seed separation and
the blocked holdout. Round-12 and round-13 artifact hashes match their
published manifests. All sixteen ordered cubic terms at n=4,6 match the
round-13 exact rational hashes; their sums match its T=2 cubics. The large
round-12 full positive-p Schur solve is not a premise and is not rerun.
Private earlier execution logs are unavailable; chronology is checked only
to the extent supported by published receipts. No dependency repair was needed.

**Unresolved here:** the fourth-and-higher remainder uniformly in n, a sharp
order/sign of C, fixed-c ordering, growing-T theory, and ordinary-initialization
or pre-S explanations. Cubic control alone provides no enlarged noise window.
The old exponential entrance-weighted higher-residence example is compatible
with this result because its large terms cannot be bounded separately in the
signed response. No current-literature search or novelty claim is made in
this offline audit. The repository's October 2026 noiseless radius/archive
comparison remains a model distinction, not a theorem used here.

**Falsifiers:** a bad pair reached after two insertions without both final
acceptance factors; a clean state outside the stated error budget used in an
operator bound; a nonzero R F_j at a phase including the boundary wrap;
failure of the stopped-reward identity for the orphan-fed pair; failure of
(9) or (10); disagreement of phase kernels with literal masks or published
exact coefficients; or a coefficient violating (12). These would invalidate
the associated proof step. The explicit -1/5 phase witness already rejects
unshifted boundary subtraction, which is not used in this corrected proof.

The original preregistration, cap, seeds, and 240 missing gate-blocked holdout
rows are preserved. No new scientific trajectories or seeds were generated;
these are deterministic proof checks, not an unregistered sampling experiment.
