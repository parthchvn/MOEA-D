# Fourth response: what is established and what remains unresolved

**Open in this checkout:** polynomial growth of the full supplied-corner
fourth coefficient for T=2, and hence of the T=3 minus T=2 gap, is not
established by this round. Finite exact coefficients do not settle it.
The new results below remove a local source of the difficulty and strengthen
the obstruction to an absolute residence argument. No full fourth-order
polynomial theorem, uniform remainder, or enlarged noise window is asserted.

## Process and coefficient

**Definition.** Fix n>=3 and filled cardinality T=2 or 3. Supply ideal extrema
(0,n), labels b_k=k and true weights C=(2,1,2,...,n); initialization costs
zero. Ascending breeders mutate their own incumbent using independent
per-bit flips of probability 1/n. A fresh Bernoulli(p) gate activates an
independent second mask of the same rate for observation. The one observation
is offered to the filled neighborhood, with even breeders preferring right
and odd breeders left and invalid indices skipped. Pinned max-Chebyshev
selection accepts only observation k at recipient k and stores the child's
true weight. This is cardinality, not clipped radius.

The filtration reveals the supplied state and consumed masks and gates
through each attempt. Stop at the first full sweep boundary with simultaneous
true alignment. Retain aligned states inside a sweep. No acceptance-conditioned
noise law, drift theorem, tail-from-mean argument, or external theorem transfer
is used. Time below is in full-population sweeps unless explicitly labeled
isolated-pair attempts.

**Proved finite-state identity.** Let K_i be a clean attempt kernel,
Delta_i=J_i-K_i its activated-minus-clean difference, Q_j the degree-j
coefficient of the ordered sweep kernel killed at aligned boundaries, and
R0=(I-Q0)^(-1). Positive own repair probabilities and clean deletion of
errors make R0 finite for each fixed n. With boundary functions zero at
alignment,

\[
 h_0=R_0 1,\qquad h_j=R_0\sum_{r=1}^j Q_rh_{j-r}.
\]

Set d_{T,n}=h_4(C) and D_n=d_{3,n}-d_{2,n}. Then

\[
 E\tau_3-E\tau_2=pA_n+p^2B_n+p^3C_n+p^4D_n+O_n(p^5).
\]

D is the fourth derivative divided by 24. For
q=1-(1-d(2,0))(1-d(1,0)), the clean corner row gives the exact decomposition

\[
 d_{T,n}=q^{-1}(Q_1h_3+Q_2h_2+Q_3h_1+Q_4h_0)(C).       \tag{1}
\]

All four summands are signed. In particular Q4 uses four distinct attempts
within one sweep. [fourth.py](fourth.py) evaluates (1); the independent
phase-cycle solver from the verified round-14 source evaluates
e_C G Delta G Delta G Delta G Delta h0. G is the clean occupation matrix
on population/next-breeder phase, killed only at aligned phase zero, with
reward 1/(n+1) per attempt. These formulations preserve within-sweep effects.

## A polynomial bound for T=3 and the pure orphan word

**Proved using the audited clean geometry.** For n>=5 the required clean
states have at most five errors, so at least one of n+1 sites is correct.
Every adjacent edge communicates both ways under T=3. A correct frontier
extends the correct set with conditional probability at least 1/(3n) per
scheduled visit. Five extensions and a partial-sweep allowance cost at
most 15n+1<20n sweeps in mean, from every phase. This is a sum of conditional
waiting means, not a bound on a maximum inferred from marginal means.

Put m=n+1, L=20n. The initial occupation mass is m/q, every subsequent clean
occupation needed in the fourth response is at most mL, h0<=L, and each
signed insertion has row norm at most two. Therefore

\[
 |d_{3,n}|\le16m^4L^4/q\le122880000 n^9,\quad n\ge5.    \tag{2}
\]

The exact n=3,4 calculations check the finite exceptions against the same
loose polynomial. This proves a T=3 bound, not a bound on D_n.

**Proved from the previously audited discounted orphan identity.** When n
is even and only recipient n is noisy, the degree-four coefficient is at
most 80/q^5 in absolute value. Indeed the degree-j bound is
(j+1)(2/q)^j/q. Thus the OOOO word is polynomial. This does not control
any of the fourteen mixed R/O words or RRRR in the full T=2 process.

## A stronger obstruction: keep both mutation probabilities

**Proved negative result.** Even a two-entry third-residence bound retaining
the actual supplied-corner mutation factors can grow exponentially. This is
a positive majorant, not the signed fourth coefficient.

Take odd n>=9, the closed last pair k=n-1,l=n, and x=(n-1)/2. Let

\[
 a=d(x,n-1),\quad b=d(x,n),\quad r=a+b,\quad s=1-r,
 \quad q_E=1-s^2,\quad c=(1-1/n)^n.
\]

E has both pair values x and every other site correct. Its clean holding
residence is geometric with escape probability q_E. Consider these two
specific sweeps, each containing one activation:

1. The corner remains wrong, with probability 1-q. Breeder n-1 generates x
   and observes n-1, corrupting its own slot, with weight d(n-1,x)a. Breeder
   n makes a clean no-flip copy, of probability c. The boundary state S has
   the original corner error and the new error at n-1.
2. The corner repairs with probability q. Breeder n-1 makes a literal
   no-flip copy x, of probability c, and observes n, with probability b,
   corrupting the second slot. Breeder n avoids either pair target under
   clean mutation, with probability s. The boundary is E.

All other proposals are clean and cannot create errors. The two positive
births retain weight

\[
 w=(1-q)q c^2s\,d(n-1,x)ab.                            \tag{3}
\]

At each sweep the new error makes its off-diagonal Q1 coefficient
nonnegative; a negative clean/diagonal term cannot create it. The selected
path is therefore a valid positive entrance term. It can be followed by
three clean residence factors at E, giving w/q_E^3.

Weight reversibility and elementary endpoint probabilities give

\[
 d(n-1,x)={\binom n x\over n}a,\qquad
 R={a\over b}=(n-x)(n-1)+{x\over n-1},\quad1\le R\le n^2.
\]

For n>=9, q>=1/(3n), 1-q>=1/2, c>=1/4, s>=1/2 and q_E<=2r.
For the last bound on s one may use r<=(n^2+1)n^{-(n+1)/2}<=2/n^3.
Consequently

\[
 {w\over q_E^3}
 \ge {\binom n x\over1536n^2}{R^2\over(R+1)^3}
 \ge {\binom n x\over12288n^4}
 \ge {2^n\over12288n^4(n+1)}.                          \tag{4}
\]

This is an actual supplied-state entrance, stronger than dropping mutation
factors and observing only ab(L+2/(a+b))^3. The latter is also unbounded
polynomially: taking both wrong weights zero gives a lower bound
4 n^(n-4). [entrance.csv](entrance.csv) and
[obstruction.csv](obstruction.csv) contain exact rational witnesses.
Neither (3) nor (4) is a lower bound on D_n. The two further signed insertions
in a real fourth coefficient cannot be replaced by factors of one.

## Closed-pair second response after two entries

**Candidate proof, complete local argument pending independent audit.**
This section concerns an autonomous pair with adjacent targets k,k+1,
breeders k then k+1, and no external proposals. Its stopping boundary occurs
after those two attempts; aligned interior states remain live. The argument
does not apply as written to the even-n orphan-fed last pair or to a pair
embedded in a population whose other coordinates can still be corrupted.
In the actual T=2 graph, the closed pairs have even k. Odd-k finite-check
rows are isolated comparators, not additional pairs in that graph.

Use *attempts* as the local reward. Let v_j(s,i) be the degree-j coefficient
of the local boundary hitting mean from pair state s and next phase i=0,1.
At an aligned phase-zero state v_j=0. Put

\[
 r(z)=d(z,k)+d(z,k+1),\qquad L=32n,\quad H=64L^2.
\]

The proposed local bound is, for every double-error state (x,y) and phase,

\[
 \boxed{r(x)r(y)|v_2((x,y),i)|\le34LH=2176(32n)^3.}    \tag{5}
\]

Pair-sweep coefficients are v_j/2. Actual erroneous-entry acceptance
factors d(x,k)d(y,k+1) are no larger than r(x)r(y), so (5) also bounds that
acceptance-weighted second response. It is precisely a response left after
two earlier insertions, but only for this isolated pair.

**Local lemma: square-root active escape.** Let eta=1/n and
theta=2 eta(1-eta). For a fixed parent genotype, let P_eta and P_theta be
the one-mask and two-composed-mask laws. Cauchy-Schwarz on the event that
the resulting weight is k or k+1 gives

\[
 \rho(z)^2\le\chi_n r(z),\quad
 \rho(z)=\sum_u d(z,u)r(u),\quad
 \chi_n=\left({\theta^2\over\eta}
       +{(1-\theta)^2\over1-\eta}\right)^n<3.            \tag{6}
\]

Indeed the bracket is 1+eta(1-2eta)^2/(1-eta), whose logarithm times n
is at most one; e<3. The same argument applies to a weight event because
the bit-level likelihood ratio is summed before the inequality is used.
This is an unconditional pre-proposal bound. It does not bound activation
probability conditional on accepted or retained observations.

**Clean occupation and first response.** Single-error or aligned-interior
states have clean mean at most L attempts: a correct adjacent donor repairs
with probability at least 1/(3n) once every two turns. For a double-error
state write a=r(x), b=r(y), u=a+b. Until the first clean repair, x and y do
not change. The two-turn escape is u-ab>=u/2, so expected attempts until
that repair are at most 4/u. Thus

\[
 v_0(D,i)\le L+4/u,\qquad v_0(S,i)\le L.
\]

After an activated overwrite by z, any double-error continuation has clean
mean at most L+4/(r(z)+r(other)). Sum the acceptance probability before
bounding: the accepted extra waiting contribution is at most four per
attempt, since

\[
 \sum_z d(parent,z)\sum_{j\in\{k,k+1\}}
              d(z,j){4\over r(z)}=4.
\]

Write Delta F as accepted active overwrite-minus-stay differences minus
clean repair-minus-stay differences, at the successor phase. On a double
state the resulting forcing is bounded by 4L+4 rho(parent)/u, and hence
by 4L+7/sqrt(u) using (6). On single-error/aligned-interior states it is
at most 4L. The clean stopped Poisson sum through the first repair gives

\[
 |v_1(S,i)|\le4L^2,\qquad
 |v_1(D,i)|\le4L^2+16L/u+28/u^{3/2}
             \le H(1+u^{-3/2}).                       \tag{7}
\]

These are signed Poisson responses evaluated with absolute forcing bounds;
no noisy mean replaces clean occupation. Stopped summation is legitimate
at each fixed n because the state space is finite, all clean hitting means
are finite, and the displayed forcings are bounded on that space.

**Second response.** Replacing one double-error coordinate leaves the other
coordinate fixed, with repair weight a or b. The accepted new v1 values
satisfy

\[
 \sum_z d(parent,z)\,{r(z)\over(r(z)+b)^{3/2}}
       \le {1\over\sqrt b}.
\]

Including the unchanged active term, the negative clean term and both
recipient choices, (7) therefore yields

\[
 |\Delta v_1(D,i)|
 \le H\left(4+a^{-1/2}+b^{-1/2}+4/u\right).            \tag{8}
\]

For the holding terms, (rho(parent)+r(parent))u^(-3/2)
<=sqrt(3)/u+1/sqrt(u)<=4/u since u<=2. This is the step lost by replacing
every signed holding difference by a row norm of two.

For a single-error state whose wrong value has repair weight a, a new
double error can arise only by overwriting its correct partner. The same
accepted-new-value sum and |v1(S)|<=4L^2 give

\[
 |v_2(S,i)|\le LH(4+a^{-1/2}).                         \tag{9}
\]

Clean removal of the marked error only improves this bound; an aligned
interior state has |v2|<=4LH. From a double state, sum (8) until its first
clean repair, and then use (9) for the remaining single error:

\[
 |v_2(D,i)|\le {4H\over u}(4+a^{-1/2}+b^{-1/2}+4/u)
               +LH(4+a^{-1/2}+b^{-1/2}).              \tag{10}
\]

Multiplication by ab proves (5). Specifically ab/u<=1,
ab/(u sqrt(a))<=1, ab/(u sqrt(b))<=1, ab/u^2<=1/4,
ab<=1, ab/sqrt(a)<=1 and ab/sqrt(b)<=1. The two terms in
(10) are at most 28H and 6LH, whose sum is at most 34LH.

The mechanism controls an actual signed second response, not the third
clean residence moment. It is compatible with (4) and with the audited
earlier higher-residence counterexample. [pair.py](pair.py) checks (5)-(9)
at both phases using exact rational arithmetic; square-root inequalities
are checked by squaring a nonnegative residual, not by rounded floating
point comparisons.

## The RROO term: subtract the correct-orphan stationary contribution

**Candidate proof, pending independent audit.** The particular mixed word
RROO can also be bounded polynomially, without using (5). Continue with
even n>=4, m=n+1 and L=20n in full-population sweep units. R changes only
nonorphans, O only recipient n. The second R annihilates the phase-local
orphan coefficient F2, so RROO depends only on the second excess e2.
Expectations first use sufficiently small nonnegative O parameter v;
finite-state identities then extend analytically around zero. Negative v
is not given a stochastic interpretation.

After two R insertions the orphan is still correct. There is either no bad
pair, one bad closed pair, or a bad orphan-fed last pair. No other arbitrary
errors coexist with that bad pair: the two births are used by its two
coordinates; the original corner can remain elsewhere. Clean descendants
are included in these cases. Set M=L+2/(a+b), where a,b are the two wrong
values' own-target repair probabilities, as in the audited two-entry bound.

**Closed bad pair.** The nonorphan completion boundary rho is independent
of the O-only orphan evolution: all errors lie in closed pairs and the
orphan-fed pair is correct throughout. Let A(v) be the autonomous orphan
kernel, nu_v(n)=1-bv, b=1-d(n,n), and U_v(t)=A(v)^t(n,n).
Stationarity with the *linear* invariant law gives the exact identity

\[
 {U_v(t)\over1-bv}
 ={1\over1-bv}-{v\over(1-bv)^2}
       \sum_{y<n}d(n,y)A(v)^t(y,n).                    \tag{11}
\]

Since the degree-one coefficient of A(v)^t has row norm at most 2t,

\[
 \left|[v^2]{U_v(t)\over1-bv}\right|\le3+2t.           \tag{12}
\]

The first-degree coefficient is, more sharply,
sum_{y<n} d(n,y)(1-d(y,n))^t. No unbounded orphan hitting function is bounded
separately in these identities.

At a boundary with the orphan correct, the stopped Poisson identity gives
e_v=E sum_{t<rho} U_v(t)/(1-bv). At an interior phase with the orphan correct,
the same formula omits t=0: the local first-future-boundary function already
charges that term. The next orphan turn is still pending. Independence of
rho is used only in this closed-pair case. Uniform conditional remaining
nonorphan mean <=M implies E rho^2 <=(2M+1)E rho<=3M^2: sum expected residual
times at integer boundaries, rather than inferring a second moment from
one initial mean. Equations (11)-(12) consequently give, at every phase,

\[
 |e_2|\le E\rho^2+2E\rho\le5M^2.                     \tag{13}
\]

**Orphan-fed bad last pair.** Independence is not assumed here. When the
orphan is correct, nonorphan completion costs at most L, even if both members
of the last pair are wrong: the correct orphan first supplies n-1, then the
correct partner supplies n-2, and the original corner is also fast. These
are at most three successive O(n) clean extensions. From any wrong orphan
y, own pair repairs still bound the nonorphan mean by M; alternatively wait
for the orphan's geometric repair and then at most L. Thus the mean is at
most min(M,1/d(y,n)+L), uniformly over clean descendants and phases with
the stated boundary slack.

At boundaries let B(v)=B0+v B1 be the O-only chain killed at nonorphan
completion and r=1{orphan correct}. Put W_j=G0(B1 G0)^j r, G0=(I-B0)^(-1).
Then e2=W2+b W1+b^2 W0. Uniformly in the orphan value, W0<=L: no reward is
earned while it is wrong; after its first clean repair, the remaining
nonorphan mean is at most L. Therefore

\[
 |W_1(y)|\le2L\min(M,1/d(y,n)+L),\qquad
 |W_1(n)|\le2L^2.
\]

Starting with the orphan correct, a B1 birth of y has its *actual* factor
c_y=d(n,y)d(y,n); the other branch is the negative unchanged state. The
clean prefix before that final orphan turn does not invalidate these uniform
bounds. Hence

\[
 |B_1W_1|\le\sum_{y<n}c_y
       \{2L(1/d(y,n)+L)+2L^2\}\le6L^2.
\]

The initial clean occupation is at most L. Thus |W2(n)|<=6L^3 and
|e2(n)|<=9L^3 at boundaries. At an interior phase use the exact corrected
suffix identity e_v^(i)=S_i(v)e_v^(0). The constant suffix preserves a
correct orphan. Its linear suffix has the same c_y birth and unchanged
branches, and
|e1(y)|<=2L(1/d(y,n)+L)+L, |e1(n)|<=3L^2.
Its weighted contribution is at most 8L^2. Consequently

\[
 |e_2^{(i)}|\le20L^3                                  \tag{14}
\]

for every phase when this bad last pair starts with a correct orphan.
The future last-pair/orphan dependence is retained throughout.

**Application of the audited entrance inequality.** Good continuations use
the inherited |e2|<=512L^3. A common bad-state bound is
512L^3+5M^2, covering (13)-(14). The two-entry inequality, with
ab M^2<=(L+1)^2, therefore gives

\[
 |\mathrm{RROO}|\le {m^2L\over q}
          \{4096L^3+20(L+1)^2\}
       \le5000\,{m^2L^4\over q}.                       \tag{15}
\]

This is one ordered T=2 word, not the full fourth coefficient. In particular,
the new gain comes from retaining the correct initial orphan and the linear
stationary law in (11), rather than bounding a generic e2 by M^3. The phase
subtraction, boundary-only killing and negative unchanged branch all matter.

## Why a full fourth-order theorem does not yet follow

**Unresolved transfer, not claimed proved.** Replacing the full-population
second response h2 by this isolated-pair v2 is invalid. After the first two
insertions create a bad pair, the last two insertions may corrupt other
coordinates, create a second bad pair, or alter an orphan that feeds the
last pair. Completion remains a simultaneous boundary event. The earlier
one-block Schur result also preserves the rest's evolution and cannot be
replaced by a frozen rest or by adding independent local hitting means.

For even n, splitting Delta=R+O yields sixteen ordered fourth-degree words.
The pure OOOO bound and candidate RROO bound leave RRRR and thirteen other
mixed words without a complete all-n audit here. The corrected phase-dependent
orphan subtraction from round 14 remains necessary. In particular, ORRR
requires control of three nonorphan insertions after a wrong orphan has been
created; (5) and (15) do not supply that bound. None of these words may be
replaced by a trajectory probability or discarded because a finite value is
small.

**Conjecture, not established:** D_n is bounded by a polynomial in n. The
finite signed coefficients and the new local estimate are consistent with
this conjecture but do not select an exponent or bound a remainder.

**Falsifiers:** a literal-kernel disagreement, omitted within-sweep insertion,
failed two-sweep positive entrance in (3), failure of (6) for an actual weight
event, an isolated-pair phase value violating (5), a missing holding or clean
term in (8), failure of the independence qualification in (11)-(13), a
phase or stopped-reward counterexample to (14), or an independent fourth
coefficient disagreement. A full
polynomial claim would additionally require a valid bound on the global
second response after the two entries, including the rest's evolution and
the orphan-fed pair. Failure of that transfer would reject the proposed
route, not contradict the isolated-pair bound.

No stochastic experiment, new seed, current-literature search, or novelty
claim is used. The repository's comparison to Doerr, Elmoutassim, Krejca and
Kibulu (2026), arXiv:2610.35373, remains a noiseless radius/archive model
boundary. Its theorem is not transferred to this noisy coefficient. The
original preregistration and all 240 blocked holdout rows remain unchanged.
