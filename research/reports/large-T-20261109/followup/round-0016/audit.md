# Independent audit of the phase-aware RROO bound

**Verdict: proved in the stated supplied, pinned T=2 model.** The round-15
candidate survives this later independent analytic and computational audit.
For even n>=4, put m=n+1, L=20n and
q=1-(1-d(2,0))(1-d(1,0)). In full-population sweep units,

\[
 |\mathrm{RROO}|\le5000\frac{m^2L^4}{q}.                 \tag{1}
\]

The proof below retains the dependence between the orphan and the last pair.
It bounds only this ordered fourth-order term. It neither proves polynomiality
of the full fourth coefficient nor enlarges the full-process noise window.
The isolated-pair second-response bound from round 15 is **still a candidate
proof** and is not a premise here. The finite checks are separately labeled
**mechanically checked**; they do not supply an all-n extrapolation.

This audit uses an independent implementation and review in a later round,
not a second concurrent agent. The original proof needs no changed constant.
The expanded explanation below makes explicit why a suffix can use the same
orphan-birth factor, why killed rows cause no extra term, and why a second
moment follows from a uniform conditional remaining mean.

**Definitions and model.** Supply ideal extrema (0,n), pinned labels b_k=k,
and true weights C=(2,1,2,...,n); initialization costs zero. Breeders visit
0,...,n cyclically and mutate their own incumbent by independent per-bit
flips of rate 1/n. A fresh Bernoulli(p) gate activates an independent mask
of that same rate for observation. One observation is offered to the filled
cardinality-two neighborhood, with even breeders preferring right, odd
breeders left, and invalid indices skipped. The pinned max-Chebyshev rule
accepts observation k only at recipient k, storing the child's true weight.
T is cardinality, not symmetric radius. The scalarization is
max{k(n-w),(n-k)w}. The primary stopping time tau is the first full sweep
boundary with simultaneous true assignment; aligned interior phases remain
live. Historical or archive coverage is not used.

Let F_t reveal the supplied state and consumed mutation masks, activation
gates and observation masks through attempt t. Bounds condition before a
proposal or at an indicated stopping time. They never condition on acceptance
or retention. The auxiliary O-only chain below uses its own natural
transition-history filtration. No drift theorem or tail-from-mean argument
is invoked.

Let K_i be the clean attempt kernel and Delta_i its activated-minus-clean
difference. For even n, split Delta_i=R_i+O_i by accepted recipient: R acts
only on 0,...,n-1, while O acts only on n and is nonzero only at breeder n.
Each restricted difference has row sum zero and row absolute norm at most
two. This is an algebraic split of a shared observation, not an independence
assumption about gates. Add next-breeder phase to the state; G is clean
occupation killed only at aligned phase zero. With reward 1/m per attempt,
h0=G(1/m), and

\[
 \mathrm{RROO}=e_CG R G R G O G O h_0.                 \tag{2}
\]

The rightmost two insertions are the degree-two coefficient of the O-only
hitting function. Ordered words are signed responses, not probabilities of
exactly four activations. Fixed-n analyticity follows because every clean
own repair has positive probability and clean errors can only disappear.
Thus the finite killed clean inverse exists. No uniform analytic radius is
asserted.

**Proved clean geometry and rechecked two-entry premise.** The graph consists
of closed pairs {0,1},{2,3},...,{n-2,n-1}, with the extra donor n feeding n-1.
The last pair receives that feed but cannot feed back to n. A correct
adjacent donor repairs its partner with conditional probability at least
1/(3n) per scheduled visit. The original error w_0=2 remains fast even if
slot 1 is wrong: breeder 0 can produce weight 1 with probability at least
2/(3n), or at least 1/3 after w_0 repairs to zero. Call a state good if all
other erroneous pairs have a correct partner. After at most two nonorphan
insertions, good states and clean descendants have remaining clean mean
at most L, including phase slack, uniformly over any orphan value.

If a bad pair exists, it consumes both arbitrary surviving erroneous
overwrites; the original corner may also remain. For bad values x,y at
targets k,k+1 put a=d(x,k), b=d(y,k+1) and

\[
 M=L+2/(a+b).                                         \tag{3}
\]

Until the first pair repair, these values stay fixed. Ignoring helpful
proposals, its two own turns give escape probability at least (a+b)/2 per
sweep. One partial sweep plus that wait and at most three good extensions
fit inside (3), from every phase. This also bounds clean descendants and
the mean number of future orphan turns before regular completion. The
argument does not require a polynomial lower bound on a or b.

Two bad values require two positive births with their actual acceptance
factors a and b. Negative diagonal or suppressed clean-repair terms cannot
create this bad pair. For 0<a,b<=1,

\[
 abM^2\le(L+1)^2.                                    \tag{4}
\]

This follows by expanding M^2 and using ab<=1, ab/(a+b)<=1/2 and
ab/(a+b)^2<=1/4. Mutation factors are summed only afterwards; even when the
second parent depends on the first overwrite, its conditional mutation row
sums to one. Initial clean occupation has mass m/q, and occupation after
one R insertion has mass at most mL. Hence for a phase function F bounded
by U on good states and by V(M) on bad states,

\[
 |e_CG R G R F|
 \le\frac{m^2L}{q}\{4U+4\sup_{a,b}abV(M)\}.           \tag{5}
\]

This rederives the round-14 premise used here. Its exhaustive two-birth
support checks and exact acceptance inequalities also replayed successfully.
The round-12 positive-p Schur solve and the round-15 isolated-pair response
are not needed.

**Proved orphan subtraction at the correct phase.** Give O a parameter v and
set R noise to zero. K+vO is stochastic for sufficiently small nonnegative v
at each fixed n; analytic identities then extend around zero. Negative v is
not given a stochastic interpretation. This auxiliary split chain preserves
the clean regular transitions; it is not obtained by conditioning the
original shared gate on an accepted observation.

The orphan marginal is autonomous, with one-turn kernel A(v) and invariant
law

\[
 \nu_v(y)=(1-v)1_{y=n}+v d(n,y),\qquad
 \nu_v(n)=1-\beta v,\quad\beta=1-d(n,n).
\]

For x!=z its transition probability is
d(x,z)[(1-v)1_{z=n}+v d(z,n)]. Weight reversibility
binom(n,x)d(x,z)=binom(n,z)d(z,x) proves the stated stationary law,
including its linear dependence on v. Let f_v(y) be the first boundary
hitting mean of n, with f_v(n)=0. Stationarity supplies its equation at n,
and the usual first-step equations supply the others:

\[
 (I-A(v))f_v=1-1_{\{y=n\}}/(1-\beta v).               \tag{6}
\]

Let rho be the first boundary where all nonorphans are correct, allowing
rho=0. Once correct they remain correct with R disabled. Summing (6) until
rho, then using the strong Markov property, gives

\[
 h^O_v(E,y)=f_v(y)+e_v(E,y),\qquad
 e_v(E,y)=\frac{1}{1-\beta v}
 E^v_{E,y}\sum_{t<\rho}1_{\{Y_t=n\}}.                \tag{7}
\]

This needs no independence of rho and Y. For fixed n, f_v is bounded on the
finite state space, and the regular completion mean is bounded by M even
under O-only evolution, by ignoring orphan help. Truncation and integrable
stopping justify the summation.

At next-breeder phase i>0, the next orphan turn has not yet occurred. Its
local first-future-boundary function is

\[
 F_v^{(i)}(y)=\frac{m-i}{m}+A(v)f_v(y)
 =f_v(y)-\frac{i}{m}+\frac{1_{\{y=n\}}}{1-\beta v},
 \qquad F_v^{(0)}=f_v.                               \tag{8}
\]

With S_i(v) the unrestricted suffix operator, subtraction of (8) gives
exactly e_v^(i)=S_i(v)e_v^(0). R leaves the orphan unchanged and has row sum
zero, so R F_2 vanishes at every successor phase, including the wrap to
zero. Killing causes no exception: at the aligned phase-zero state f_2(n)=0.
Consequently the last factor F in (5) can be replaced by the second excess
e_2. Subtracting an unshifted boundary function at interior phases is not
the definition used here.

**Proved closed-bad-pair cancellation.** After two R insertions, the orphan
is still correct. If the bad pair is closed, all nonorphan errors lie in
closed pairs and the orphan-fed pair stays correct. Their completion time
rho is independent of the O-only orphan chain. Set U_v(t)=A(v)^t(n,n).
Stationarity gives

\[
 \frac{U_v(t)}{1-\beta v}
 =\frac1{1-\beta v}
 -\frac{v}{(1-\beta v)^2}\sum_{y<n}d(n,y)A(v)^t(y,n). \tag{9}
\]

Write the final sum as S0+v S1+O(v^2). Then

\[
 [v^2]\frac{U_v(t)}{1-\beta v}=\beta^2-2\beta S0-S1,
 \qquad |[v^2]U_v(t)/(1-\beta v)|\le3+2t,             \tag{10}
\]

because 0<=S0<=1 and the first derivative of A(v)^t has row norm at most
2t. The first-degree coefficient is exactly
sum_{y<n}d(n,y)(1-d(y,n))^t. An unbounded orphan hitting function is never
bounded separately.

At a boundary, (7) and independence give an expected sum of (9) for
t=0,...,rho-1. At an interior phase, count future boundaries from one;
the analogous sum omits t=0 because (8) already charges it. At every
unsolved boundary the conditional remaining regular mean is at most M.
For example, Tonelli applied to
rho^2=2 sum_{t<rho}(rho-t)-rho gives a second-moment bound from these
conditional means. In particular the looser bound used in round 15 holds:

\[
 E\rho^2\le(2M+1)E\rho\le3M^2.
\]

The same reasoning applies to a partial initial phase using (3)'s slack.
This is not a second moment inferred from a single starting mean. Summing
(10) therefore proves, at every phase with the orphan initially correct,

\[
 |e_2|\le E\rho^2+2E\rho\le5M^2.                    \tag{11}
\]

**Proved orphan-fed last-pair cancellation.** Independence is not used in
this case. All expectation and occupation bounds in (12)-(16) use clean
dynamics (v=0); they are not noisy residence estimates. With the orphan
correct, at most three successive clean
extensions suffice: n repairs n-1, that correct partner repairs n-2, and
the original corner, if still present, repairs via donor 1. From every
phase and clean descendant this costs at most 9n+1<L sweeps. For wrong
orphan y, regular completion can instead be bounded either by ignoring
orphan help or by waiting for its own geometric repair and then these
extensions. Hence

\[
 E\rho\le\min\{M,1/d(y,n)+L\};\qquad E\rho\le L
 \text{ when }y=n.                                  \tag{12}
\]

At boundaries, kill only at regular completion. Its kernel is
B(v)=B0+vB1 because the only O turn is the last turn. Put
G0=(I-B0)^(-1), r=1_{orphan correct}, and

\[
 W_j=G0(B1G0)^j r,\qquad e_2=W_2+\beta W_1+\beta^2W_0.\tag{13}
\]

All W_j use clean occupation. Under clean dynamics, no reward is earned
before the orphan's first repair. If regular completion has not already
occurred then, its remaining mean is at most L. Thus 0<=W0<=L uniformly
over every orphan value in the required last-pair family. Using
||B1||<=2 and (12),

\[
 |W_1(y)|\le2L\min\{M,1/d(y,n)+L\},\quad
 |W_1(n)|\le2L^2.                                   \tag{14}
\]

Now start with the orphan correct. At its final turn the positive O birth
of y<n has the exact factor c_y=d(n,y)d(y,n), and the other branch is the
negative unchanged state. The clean prefix can only delete regular errors,
so the same bounds apply to both successor states. If that prefix has
completed all regular slots, both killed continuation values are zero.
There is no omitted boundary term. Therefore

\[
 |B1W_1|\le\sum_{y<n}c_y
 \{2L(1/d(y,n)+L)+2L^2\}\le2L+4L^2\le6L^2.          \tag{15}
\]

The actual acceptance factor d(y,n) cancels the inverse repair rate
before summation. Dropping it first would invalidate the polynomial bound.
The initial clean occupation with a correct orphan is at most L, giving
|W2(n)|<=6L^3 and, by (13), |e2(n)|<=9L^3 at boundaries.

For an interior phase write S_i(v)=S_i0+vS_i1. Its constant part preserves
the correct orphan. Its linear part is the same final-turn c_y birth and
negative unchanged branch after a clean prefix. Equation (14) and W0<=L
give

\[
 |e_1(y)|\le2L(1/d(y,n)+L)+L,\qquad |e_1(n)|\le3L^2.
\]

Thus |S_i1 e1|<=2L+(5L^2+L)<=8L^2 and the exact phase identity yields

\[
 |e_2^{(i)}|\le9L^3+8L^2\le20L^3.                  \tag{16}
\]

The future pair/orphan dependence is retained throughout (12)-(16).
For a concrete falsifier of an independence shortcut, at n=4 just before
breeder 4 in state (0,1,2,0,0), the next clean turn completes the regular
slots with probability 3/64, and repairs the orphan with probability 1/256.
The intersection has probability zero, whereas the product is 3/16384.
This **proved finite counterexample**, also mechanically checked in
[witness.json](witness.json), rejects independence; it does not reject (7).

**Proved assembly.** On good continuations the generic phase-aware excess
bound |e2|<=512L^3 follows by expanding the affine killed regular kernel
and (1-beta v)^(-1), with clean norm <=L and signed norm <=2, then adding
the suffix. Explicitly, the boundary bounds through degree two are L,
3L^2 and 7L^3; the linear suffix adds at most 6L^2 to the second coefficient,
giving 13L^3<=512L^3. A common bound covering both bad-pair types is
512L^3+5M^2. Applying (4)-(5),

\[
 |\mathrm{RROO}|\le\frac{m^2L}{q}
 \{4096L^3+20(L+1)^2\}\le5000\frac{m^2L^4}{q}.
\]

Since q>=1/(3n), this is polynomial, O(n^7), for this word in sweeps.
It removes the M^3 obstruction from RROO without disputing the published
positive higher-residence counterexamples. Those counterexamples concern
absolute majorants, not this signed response.

**Mechanically checked evidence.** The new [solver](audit.py) imports no
earlier solver. It constructs mutation probabilities by a combinatorial
sum, forms unrestricted ordered sweep products, solves boundary equations
by clean error deletion, and reconstructs phases using suffix products.
This differs from round 15's use of the round-14 phase-cycle solver.
Literal genotype-mask and max-Chebyshev regressions provide an additional
transition oracle in [test_audit.py](test_audit.py).

Exact checks cover 408 initial pair states at n=4,6,8,10 (240 orphan-fed),
3,188 phases and 31,552 reward, suffix, moment, annihilation and bound
checks. The grid includes every wrong-value pair through n=6, every
orphan-fed wrong-value pair at n=8, and endpoint stress states elsewhere;
it is not an exhaustive all-population or all-n check. All 254 overlapping
round-15 excess fractions match exactly. Twenty-four stationary horizons
at n=4,6,8,12 pass, including coefficientwise invariance. Independent RROO
fractions match at n=4 and n=6, with rounded values 2.135753903581 and
4.179111924897. There is no sampling uncertainty or censoring for these
rational calculations. See [verification.json](verification.json).

**Dependencies and limits.** The round-14 replay recursively verifies the
earlier registered plans, receipts, seed separation, and blocked holdout;
round-15 relevant excess outputs replay exactly and its artifact manifest
is checked. No dependency repair was needed. This audit does not rerun
the unrelated round-15 full fourth-order grid or use its isolated-pair
candidate. Private old trial logs remain unavailable, so execution
chronology is checked only as far as published receipts permit.

**Unresolved in this checkout:** the full fourth gap remains conjectured
polynomial. RRRR and thirteen other mixed fourth words still need complete
bounds. A useful uniform higher-order remainder, fixed-positive-c ordering
at p=c/n, and ordinary-initialization behavior do not follow. No current
literature search or novelty assertion is made in this offline audit.
The repository comparison to Doerr, Elmoutassim, Krejca and Kibulu (2026),
arXiv:2610.35373, remains a noiseless radius/archive model distinction;
that theorem is not transferred here.

**Falsifiers:** a reachable bad pair after two R insertions missing either
acceptance factor; a clean descendant outside the stated family; a nonzero
R F2 at any phase; failure of stationarity (9), stopped summation (7), the
actual c_y coefficient or suffix identity; a violation of (11) or (16);
or a literal-kernel/independent-word mismatch. Any would invalidate the
corresponding proof step. No such failure was found. The original
preregistration, cap, all 240 missing blocked holdout trials, and its
inconclusive two-stage decision are preserved. No new scientific seeds or
trajectories were generated.
