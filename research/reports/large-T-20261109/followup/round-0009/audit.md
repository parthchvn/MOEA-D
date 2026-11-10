# Independent audit of the orphan mixed-insertion bound

**Proved after this audit, for the supplied pinned model:** the round-8
candidate survives, with its original constant:

\[
 E\tau_3-E\tau_2=pA_n+p^2B_n+O_n(p^3),\qquad
 \boxed{|B_n|\le1536n^5\quad(n\ge3).}
\]

Time is in sweeps; B is half the second derivative. Attempts multiply all
coefficients by n+1. The conclusion rests on the analytic argument below.
The exact finite checks in [verification.json](verification.json) are separate
checks of the implementation and proof inequalities. They do not extrapolate
a finite grid into a theorem. No remaining logical gap was identified in
this second-order bound. The higher-order remainder on a polynomial noise
window is an additional, unresolved obligation in this project.

**Process and information.** Supply ideal extrema (0,n), stored labels b_k=k,
and true weights C=(2,1,2,...,n), without initialization evaluations. Breeders
0,...,n repeatedly mutate their own current incumbent, flipping each bit
independently with probability 1/n. A fresh Bernoulli(p) gate activates an
independent second rate-1/n mask for the observation. The observation is shared
across the filled cardinality-T recipient set: alternate right/left for even
breeders and left/right for odd breeders, skip invalid indices, stop at T.
Only T=2,3 is considered. This is not a clipped-radius process.

Pinned scalarization max{k(n-z),(n-k)z} has its unique minimum at z=k. Thus an
observed z can replace only recipient z, with the child's true weight y.
Labels and extrema stay pinned. Let F_t reveal the initial state and consumed
mutation masks, gates and observation masks through attempt t; G_s=F_((n+1)s).
The stopping time tau is the first G_s boundary with all true weights equal
to their indices. Aligned intermediate states remain in the chain. All
conditional arguments use pre-attempt information or a stopping time followed
by fresh masks. No drift theorem, acceptance-conditioned noise probability,
or tail conclusion is used.

**Dependencies, checked before use.** The full round-8 reproduction was run,
including its recursive earlier-round replay. All eight round-8 outputs match
their published bytes. The separate n=512 registration was committed at
a5449de before its measurement; the receipts, plan hashes and seed separation
are usable. No dependency repair was necessary. The inherited empirical
claims and their limitations are in [dependency.json](dependency.json).
The original preregistration, cap, 240 missing blocked holdout observations,
and inconclusive two-stage decision are unchanged. Private trial logs are
unavailable; replay verifies published evidence, not unreported execution
history. No new trajectories or seeds were drawn. These deterministic proof
checks are not a new sampling experiment.

Neither the earlier error-family theorem nor an unavailable manuscript
appendix is a premise here. The first-order asymptotic is needed only when
discussing a future sign window, not to prove the bound on B. This offline
audit makes no global literature or novelty assertion and transfers no
external theorem. The existing comparison with Doerr, Elmoutassim, Krejca and
Kibulu (2026), arXiv:2610.35373, DOI 10.48550/arXiv.2610.35373, remains a model
boundary: their noiseless radius/archive result does not prove this noisy
boundary statement.

**Finite-dimensional response.** Let D(x,y) be the standard-bit weight kernel,
K_i the clean attempt kernel, J_i the activated-mask kernel and Delta_i=J_i-K_i.
Every attempt kernel is K_i+p Delta_i. Expand the ordered sweep product as
P_0+pP_1+p^2P_2+...; P_2 sums strictly ordered pairs of different attempts.
Restrict to nonaligned boundary states to obtain Q_j, and put
R_0=(I-Q_0)^(-1). At zero noise each wrong coordinate can repair on its own
turn with positive probability; correct coordinates cannot become wrong.
The finite-state clean mean is finite, so this inverse and the local analytic
expansion exist. With all h_j zero at the aligned boundary,

\[
 h_0=R_0\mathbf1,\quad h_1=R_0Q_1h_0,\quad
 h_2=R_0(Q_1h_1+Q_2h_0).
\]

From C, the clean boundary chain remains at C until absorption. For both T,
q=1-(1-D(2,0))(1-D(1,0)). Hence

\[
 b_T=h_2(C)=\{P_1h_1(C)+P_2h_0(C)\}/q,\qquad B_n=b_3-b_2.
\]

All insertion terms are signed algebraic terms. In particular they are not
probabilities of disjoint noisy histories. The equation includes insertions
in different sweeps and in the same sweep. The latter cannot be discarded.

**Regular clean repair bound.** Set m=n+1, L=6n, J=L(L+1). A regular state
is a clean subset of C with at most one coordinate overwritten by an arbitrary
weight. Exclude an incorrect orphan n for even n,T=2. Every regular state has
clean boundary mean at most L, and every clean descendant stays regular.

Indeed alpha=(1-1/n)^(n-1)>=1/3, so a correct adjacent donor repairs its target
neighbor with probability at least 1/(3n) per visit. The T=2 sites form pairs
{0,1},{2,3},...; when n is even, only n is unpaired. Every T=3 site has an
adjacent donor. If the overwritten coordinate k is not 0 or 1, it has a
correct adjacent donor; wait at most 3n expected boundaries for k, then at
most 3n more for 0. If k=0, donor 1 is correct. If k=1, donor 0 has weight 2
until it repairs and weight 0 afterwards, with
D(2,1)>=2/(3n) and D(0,1)=alpha. Repair 1 first and then 0. These are
conditional geometric waiting bounds from successive boundaries, not an
independence claim about repair times.

For even n,T=2 the same argument works for all nonorphan errors with breeder
n's broadcasts to n-1 omitted: n-1 still has correct partner n-2. This is a
direct hazard argument, not an appeal to general monotonicity in communication.
From any phase, the expected number of boundaries until those nonorphan errors
disappear is at most L+1; wait for the next boundary, then use L. At any full
boundary where they remain their conditional mean is at most L, including
when the orphan has just repaired.

If a further insertion overwrites k by y!=k, its following clean suffix value
is at most 1/D(y,k)+L. At the next boundary, wait for k's own repair if needed;
before repair its weight stays y, and afterwards the remaining state is a
regular subset. A proposal from a parent of weight x contributes at most

\[
 \sum_{k\in B_T(i)}\sum_{y\ne k}
 D(x,y)D(y,k)\frac1{D(y,k)}\le T
\]

to this added expectation. This calculation is before acceptance and sums
all wrong y, including rare far-away weights. Therefore an active suffix
expectation is at most L+T, a clean one at most L, and their absolute
difference at most L+T. Summing over at most L expected clean sweeps gives
K_T=Lm(L+T) as a bound on |h_1| for regular states. The signed attempt kernel
has row l1 norm at most two. Thus, when both insertions stay in regular
coordinates,

\[
 |b_T|\le R_T/q,\qquad
 R_T=2(L+T)\{m^2L+\tbinom m2\}.
\]

This covers all of T=3 and odd-n T=2. A wrong even-n orphan is deliberately
excluded: with true weight zero its clean mean is n^n, not O(n).

**Recipient split and the missing small factor.** For even n,T=2 split
Delta_i into O_i, acting on accepted recipient n, and R_i, acting on all
remaining recipients. O_i=0 unless i=n. Each restricted signed operator is
the difference of two stochastic recipient-restricted attempt kernels, has
row sum zero and norm at most two. This split is algebraic; no independence
of the full noisy coordinates is asserted. Let h_1^O and h_1^R be the two
linear responses. RR obeys R_2/q. On a regular state with a correct orphan,
one orphan insertion per sweep gives |h_1^O|<=L(L+1)=J by the preceding
inverse-repair cancellation with just one recipient.

For the other order fix a phase, an orphan value y<n, and d=D(y,n). The
baseline has only the possible original corner plus this orphan. A
nonorphan overwrite leaves an arbitrary regular nonorphan collection plus
the same orphan. In either clean continuation, the orphan remains y until
its own successful proposal, and no other breeder can repair it. Couple the
two continuations with the same future orphan proposals. Let G be their
common first orphan-repair boundary, and T be either continuation's
simultaneous completion boundary. Then T>=G.

Here is the precise predictable count, which also covers k=n-1 sharing the
orphan's breeder. Let N count breeder-n turns, starting at the specified
phase, at which the orphan is still wrong **and at least one nonorphan error
is still present immediately before the proposal**. Stop counting once
either condition fails. Its indicator is F_(t-1)-measurable. Conditional on
that history, the orphan repairs with probability exactly d. A successful
proposal has true and observed weight n and can replace only n, so it cannot
simultaneously repair a nonorphan error. Clean nonorphan correctness persists.
Consequently, by conditional expectation of truncated counts and then
monotone convergence,

\[
 \Pr(T>G)=d\,E N,\qquad EN\le L+1.
\]

This equality does not condition on a future nonorphan lifetime. At boundary
G, the remaining nonorphan state is regular, and fresh future masks give
conditional remaining mean at most L. More precisely, if W_G is that state,

\[
 E(T-G)=E[\mathbf1_{T>G}h_0(W_G)]
 \le Ld\,EN\le dL(L+1)=dJ.                 \tag{A}
\]

Both the baseline and the overwritten continuation have expected excess
over the same E G in [0,dJ]. Their expected completion difference, and hence
their clean suffix-value difference, is at most dJ in absolute value.
There is no extra factor two: this is the width of a common interval.
For a suffix before the current boundary, both completion means include
the same current-boundary charge; it cancels in the difference. At phase
m the value is the boundary h_0 itself. Thus (A) covers every phase.

In a recipient-restricted insertion, the sum of absolute overwrite
coefficients is at most 2T. It follows that, while the orphan is wrong,
the absolute R forcing per sweep is at most 2mT dJ. Its expected lifetime
is 1/d sweeps. After G the regular bound K_2 applies, including zero if
alignment has just occurred. Therefore

\[
 |h_1^R|\le K'=4mJ+K_2                         \tag{B}
\]

uniformly in every y<n. The factor d in (A) is essential: a uniform O(L)
suffix estimate alone would leave an exponentially large factor 1/d.

**Both temporal mixed orders.** Starting at C, an R insertion followed in a
later sweep by an O response is bounded before division by q by 2mJ. An O
insertion followed in a later sweep by an R response is bounded by 2K'.
For two insertions within one sweep O can only be last, because its only
breeder is n. The remaining within-sweep term is at most 2m(L+1). These are
valid loose bounds, even though there are only m-1 earlier positions. Thus

\[
 |b_{RO}+b_{OR}|\le\frac{2mJ+2K'+2m(L+1)}q
 =\frac{m(12L^2+16L+2)}q.                    \tag{C}
\]

The signed terms need not have the same sign. At n=6 the separately computed
R-then-O and O-then-R different-sweep terms are respectively +6.7707331029
and -0.1077884782; the within-sweep mixed term is -0.2673261450.

**Pure OO term, separately audited.** In this restricted term only the
orphan can be corrupted. Its local own-turn chain R(p) is autonomous; the
untouched corner's geometric(q) repair clock uses disjoint breeder randomness
and is independent. Set s=1-q and
nu_p(y)=(1-p)1_(y=n)+pD(n,y). The weight-kernel identity
binom(n,x)D(x,y)=binom(n,y)D(y,x) proves detailed balance for this local
kernel and nu_p. Let h be its first-hitting mean, zero at n. The first-step
equations away from n, followed by summation against nu_p, give
(I-R)h=1-e_n/nu_p(n). Apply G=(I-sR)^(-1) and use h(n)=0. Waiting for the
independent geometric endpoint clock and then using the Markov property gives

\[
 m_O(p)=G_{nn}/\nu_p(n).                       \tag{D}
\]

This includes orphan reinfections before endpoint repair. Replacing it with
the maximum of two first-hitting times would not be valid with noise.

For an explicit coefficient bound write, for y<n,
d_y=D(y,n), c_y=D(n,y)d_y, f_y=q+s d_y, b=1-D(n,n),
a=sum c_y. The transient p-coefficient W has off-diagonal entries
W_yz=D(y,z)D(z,n) and diagonal
W_yy=b d_y-sum_(z!=y,n)W_yz. Set

\[
 g=\sum_y D(n,y)/f_y,\quad
 C_0=\sum_y c_yd_y/f_y,\quad
 C_1=\sum_{y,z}c_yW_{yz}d_z/(f_yf_z).
\]

Expanding the block inverse in (D), with transient block
diag(f)-psW, gives

\[
 b_{OO}=qg^2-\frac{-bsa+2bs^2C_0-s^3C_1}{q^2}.
\]

Here g<=1/q, C_0<=a/s, sum c_y/f_y<=1/s, max d_y/f_y<=1/s,
and ||W||_infinity<=2 (restriction of the difference of two local stochastic
kernels). Hence |C_1|<=2/s^2 and the numerator's absolute value is at most
5s<=5. This proves |b_OO|<=1/q+5/q^2<=6/q^2. Our independent calculation
uses successive exact linear solves for G_0 e_n, G_0 sR_1 G_0 e_n and
G_0 sR_1 G_0 sR_1 G_0 e_n, rather than the Schur coefficient formula.
An additional direct joint absorbing chain verifies (D) at finite positive p.

**Constant and conclusion.** For odd n,
|B_n|<=(R_2+R_3)/q. For even n, add (C) and 6/q^2. As
q>=D(1,0)>=1/(3n), the larger expression is at most

\[
 432n^5+2376n^4+2427n^3+543n^2+6n.
\]

Dividing by n^5 yields a decreasing positive sum for n>=3; at n=3 it is
40874/27 < 1536. This completes the all-n estimate with the original constant.

**Finite checks and falsifiers.** [audit.py](audit.py) imports no previous
response implementation. It constructs D by literal mutation masks, uses
full population tuples and a closed-interval recipient formula, and solves
the clean Poisson equations and signed insertion equations with rational
arithmetic. At n=4,6,8 it checks 16,512 suffix cases, including the exact
residual-reward identity underlying (A), all phase boundaries and all possible
wrong values. It checks 268 regular means with orphan help omitted, 268 mixed
forcings, and 20 h_1^R values at n=4,6. Both mixed temporal orders are evaluated
separately; at n=4 their sum plus RR and OO equals the published full-state
second coefficient exactly. The local discounted calculation agrees with all
ten published first/second coefficients at n=4,6,8,10,12, and its finite-p
identity agrees with five direct joint-chain solves.

A violation of the regular hazard bound, the predictable event identity,
the suffix interval (A), either insertion order in (C), or the local identity
(D) would falsify the corresponding proof step. A rational |B_n|>1536n^5
would falsify the final theorem. Exact small-grid agreement does not exclude
all implementation errors; the general conclusion uses the explicit proof.

**Remaining scope.** The audited first-order A_n=-(n/2)log n+O(n) and this
bound make the quadratic term negligible relative to the linear term when
p=o(log n/n^4). They do not bound the cubic and higher terms there. The
published conservative resolvent window is unchanged. No larger noise window,
fixed-positive-c ordering at p=c/n, all-n sign of B, ordinary-initialization
theorem, or pre-S causal mechanism follows. Two adjacent corrupted donors
after further insertions can defeat the regular-state repair argument; a new
weighted higher-order argument is required.
