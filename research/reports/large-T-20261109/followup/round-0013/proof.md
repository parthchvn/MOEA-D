# Cubic response: a candidate polynomial bound after signed cancellation

**Candidate proof, awaiting independent audit.** Write the supplied-corner
gap, in sweeps, as

\[
 m_3(n,p)-m_2(n,p)=pA_n+p^2B_n+p^3C_n+O_n(p^4).
\]

The argument below gives the deliberately loose candidate bound

\[
 \boxed{|C_n|\le 10^{10}n^7\qquad(n\ge3).}                 \tag{1}
\]

Thus C is one sixth of the third derivative. This is a finite-order claim,
not a uniform remainder or a fixed-positive-c result at p=c/n. The proof
does **not** bound entrance-weighted second residence moments uniformly.
Those moments remain exponentially large in the audited family. The new
steps requiring independent review are the weighted two-birth calculation,
the orphan excess identity at arbitrary phases, and the mixed-word bounds.
The exact numerical checks are separate from this all-n argument.

## Process and the coefficient identity

**Definition.** Fix n>=3, T in {2,3}. Supply ideal extrema (0,n), labels
b_k=k, and true weights (2,1,2,...,n), with zero initialization charge.
Ascending cyclic breeders mutate their own incumbent by independent bit
flips of rate 1/n. A fresh Bernoulli(p) gate activates a second independent
rate-1/n mask for observation. The observation is offered to the exact
filled-cardinality neighborhood, with the published parity-dependent side
order. This is not clipped radius. Only observation k can replace pinned
recipient k, storing the child's true weight. The natural filtration reveals
only consumed gates/masks and the supplied state. Stop at the first full
sweep boundary with all true weights correct; retain aligned intermediate
states. Attempts equal (n+1) times sweeps. No conditioning on acceptance,
drift theorem, external theorem transfer, or tail-from-mean inference is used.

**Proved finite-state identity.** Let K_i,J_i be clean and activated attempt
kernels, Delta_i=J_i-K_i, and let Q_j be the p^j coefficient of the ordered
sweep product, restricted to nonaligned boundaries. Set R_0=(I-Q_0)^(-1).
Clean errors only disappear and every own repair has positive probability,
so R_0 exists at each finite n. With h_j zero at the aligned boundary,

\[
 h_0=R_0\mathbf1,\quad
 h_j=R_0\sum_{r=1}^j Q_rh_{j-r}\quad(j=1,2,3).          \tag{2}
\]

For C=(2,1,...,n), q=1-(1-d(2,0))(1-d(1,0)) is common to T=2,3.
The clean corner row visits only C before absorption, hence

\[
 c_T=h_3(C)=q^{-1}\{P_1h_2(C)+P_2h_1(C)+P_3h_0(C)\},
 \qquad C_n=c_3-c_2.                                  \tag{3}
\]

All three summands are signed. None is a disjoint trajectory class.
P_3 contains three *different* attempts within one sweep. A cubic calculation
needs at most four simultaneous errors in h_0, three in h_1, and two in h_2.
[cubic.py](cubic.py) implements (2); [oracle.py](oracle.py) separately solves
the clean Poisson equations over every population at n=3,4 using literal
mutation masks and scalar comparisons.

For the bounds, augment the state with the next breeder phase, killing only
upon arrival at an aligned phase-zero boundary. Let G be the clean
attempt occupation matrix. Reward 1/(n+1) per attempt gives h_0=G r in
sweeps. The cubic is exactly

\[
 c_T=e_C G\Delta G\Delta G\Delta h_0.                  \tag{4}
\]

This includes all placements across and within sweeps; a single attempt
cannot contain two insertions. A clean remaining mean of M sweeps bounds
the row sum of G by mM, where m=n+1. Phase means include the partial current
sweep. Common partial-sweep charges cancel in every signed insertion.

## Clean geometry and the two acceptance factors

Put **L=20n**, and consider only states reached from a clean subset of the
corner by at most three overwrites, and their clean descendants. Constants
below intentionally allow slack for partial sweeps.

**Candidate-proof lemma 1.** For T=3 and n>=4, every required clean state
has at most four errors and at least one correct coordinate. Every adjacent
edge communicates in both directions. A correct frontier donor extends the
correct set by a neighboring target with conditional probability at least
1/(3n) on its own turn. At most four sequential extensions suffice. Thus
the mean from any phase is at most 12n+1<L. This is a sum of conditional
geometric waiting means, not an assumption about independence or maxima.

For T=2, the nonorphan coordinates form adjacent even/odd pairs. At even n,
the last pair additionally receives breeder n's proposals; omitting those
clean repairs gives the bounds below directly. The original error (0,2)
is special: if slot 1 is wrong, donor 0 of weight 2 repairs 1 with probability
at least 2/(3n), and if 0 repairs first, its new weight 0 repairs 1 with
probability at least 1/3. This pair therefore remains fast until both
coordinates have been overwritten by arbitrary values.

Call a nonorphan configuration *good* if no pair has two arbitrary erroneous
values, retaining this special treatment of (0,2). Up to four errors in a
good configuration have remaining clean mean at most 12n+1<L, uniformly
over an arbitrary orphan history. A configuration after two insertions can
have at most one *bad* pair. If its erroneous values are x,y at targets k,l,
put a=d(x,k), b=d(y,l). Before its first clean repair, both values remain
fixed. Its own turns give escape probability at least (a+b)/2 per sweep.
After that repair all remaining errors are good. Thus a valid mean bound,
uniform over descendants and arbitrary orphan histories, is

\[
 M(a,b)=L+\frac{2}{a+b}.                               \tag{5}
\]

**Candidate-proof lemma 2.** An erroneous overwrite to x at k has
coefficient d(parent,x)d(x,k). Two arbitrary errors in a bad pair therefore
require two actual erroneous overwrites, each retaining its own acceptance
factor. Negative diagonal terms and clean repairs cannot create that pair.
Consequently the two weights a,b multiply any later bad-pair value. The
elementary cancellation needed at cubic order is

\[
 ab M(a,b)^2\le(L+1)^2.                               \tag{6}
\]

Here ab/(a+b)^2<=1/4, ab/(a+b)<=1/2, and ab<=1. No lower bound
polynomial in n on a or b is asserted. Sum the mutation probabilities over
the child values *after* applying (6); each such sum is at most one.
There are at most two target choices at each insertion. Between the first
and second insertion the configuration is good, so its occupation mass is
at most mL. Before the first insertion it is at most m/q.

For later reference, if a function F has |F|<=U on good configurations and
|F|<=V(M) on bad ones, this gives

\[
 |e_C G R G R F|
 \le\frac{m^2L}{q}\{4U+4\sup_{a,b}ab V(M(a,b))\}.       \tag{7}
\]

R denotes all insertions if there is no orphan, or nonorphan insertions
otherwise. Formula (7) also applies after subtracting any function annihilated
by the second R. Its factor four for good paths is the product of the two
signed row norms, each at most two; the second four counts the two birth
recipient choices. Clean descendants that lose an error cease to be bad.

An active overwrite inside a bad pair has expected extra clean wait at
most two, because d(z,k)/(d(z,k)+a)<=1. An overwrite outside it adds only
good errors at this order. Thus |R h_0|<=3M on bad configurations needed
after two insertions, and |R h_0|<=3L on good ones. Summing clean occupation
gives |h_1^R|<=3mM^2 and 3mL^2, respectively. From (6)-(7), the RRR word
is bounded by 24 m^3(L+1)^3/q. This proves the candidate odd-n T=2 bound
without replacing the supplied entrance law by the worst single-error row.

For T=3, direct signed norm bounds in (2), using clean means <=L, give

\[
 |c_3|\le\frac8q\left(m^3L^3+2m\binom m2 L^2+
                              \binom m3 L\right)
 \le18\frac{m^3(L+1)^3}{q},\qquad n\ge4.               \tag{8}
\]

## The even-n orphan: subtract its hitting function first

Split each insertion as R+O, with O acting only on accepted recipient n.
Only breeder n has an O component. Both restricted operators are differences
of stochastic recipient-restricted kernels and have row norm at most two.
The split is algebraic; it does not assume independence of the last pair
and the orphan. Use parameters u for R and v for O.

Only a sufficiently small real neighborhood of u=v=0 is needed here.
There the recipient-split matrices are stochastic: new off-diagonal error
rates are nonnegative, clean repair rates stay positive, and every clean
diagonal has positive mass from mutations outside the recipient set. This
does not identify the split with independent activation gates for whole
evaluations, nor require stochasticity over the whole square [0,1]^2.

**Candidate-proof lemma 3, exact signed identity.** With u=0 the orphan
chain Y is autonomous, with boundary kernel A(v), and the nonorphan errors
only disappear. Let f_v(y) be the orphan's boundary hitting mean, with
f_v(n)=0. Its invariant law is
nu_v=(1-v)delta_n+v d(n,cdot). Detailed balance follows from the standard
bit-mutation weight identity binom(n,x)d(x,y)=binom(n,y)d(y,x).
Its Poisson equation on the *unrestricted* local chain is

\[
 (I-A(v))f_v=\mathbf1-e_n/\nu_v(n).                    \tag{9}
\]

Let rho be the first boundary with all nonorphan coordinates correct. The
full completion time equals rho followed by the local orphan hitting time;
nonorphan correctness persists when u=0. Optional summation of (9) through
rho, using the consumed-randomness filtration, gives

\[
 h^{O}(E,y;v)=f_v(y)+e_v(E,y),\qquad
 e_v(E,y)=\frac{1}{\nu_v(n)}
 E_{E,y}^{v}\sum_{t<\rho}\mathbf1_{\{Y_t=n\}}.          \tag{10}
\]

No independence of rho and Y is used. The mean of rho is uniformly bounded
by L on good nonorphan configurations or M(a,b) on the bad ones above,
including all their clean descendants and every orphan value. At fixed n
f_v is finite, so optional summation is justified by bounded state values
and the finite mean of rho. Prove (10) for real sufficiently small v first;
its finite-state analytic identity then gives the Taylor coefficients.

The chain killed at rho has a sweep kernel affine in v, since O occurs
only on the final attempt. Its clean resolvent has row norm at most M and
its derivative norm at most two. Expand this resolvent and
1/nu_v(n)=1/(1-v[1-d(n,n)]). At boundaries the first three excess
coefficients are bounded by M, 3M^2, 7M^3. A partial clean suffix has norm
one and its O coefficient has norm at most two. The following looser bounds
therefore hold at **every phase**:

\[
 |e_0|\le M,\qquad |e_1|\le64M^2,\qquad
 |e_2|\le512M^3.                                     \tag{11}
\]

Crucially **R f_j=0** for every local coefficient f_j, including at a
nonzero phase: R never changes the orphan value, and has row sum zero.
The common partial-sweep reward also cancels. Bounding f_j separately would
discard this exact cancellation and can introduce exponential quantities.

There is a sharper clean bound when the orphan is wrong y<n. Put d=d(y,n).
Before the next orphan repair its hazard at each own turn is d. Let N count
those turns at which nonorphan errors are still present immediately before
the proposal. This indicator is predictable, even for a last-pair error.
A clean successful orphan proposal cannot repair a nonorphan coordinate.
The conditional nonorphan remaining mean after that proposal is at most M,
and EN<=M. Therefore, including partial-sweep slack in M,

\[
 0\le e_0(E,y)\le dM^2.                              \tag{12}
\]

This is the earlier predictable-count mechanism applied also to a bad pair;
it does not infer a higher residence moment from a first moment. For two
continuations with the same wrong orphan, their clean suffix values have
the same f_0 part and excesses in [0,d M_max^2].

**Candidate-proof lemma 4, weighted R response.** For a clean subset of the
corner plus a wrong orphan, |h_1^R|<=K=64mL^2, uniformly in its weight and
phase. If one additional arbitrary nonorphan overwrite x at k is present,
put a=d(x,k). Then

\[
 |h_1^R|\le32m(L^2+1/a).                              \tag{13}
\]

To check (13), a further R overwrite can create at most one bad pair,
containing that marked error. An accepted wrong value with probability
factor b satisfies

\[
 b\left(L+2/(a+b)\right)^2\le2L^2+2/a.
\]

Apply (12) to the overwrite-minus-stay expression for R h_0. Summing the
two possible recipients, their mutation probabilities, and the clean-repair
part bounds its magnitude while the orphan is wrong by
5d(L^2+1/a). The expected attempt count to its repair is at most 2m/d.
After that stopping boundary the remaining nonorphan configuration is good;
one more insertion has an acceptance-weighted clean suffix mean at most
L+4, so the remaining R response is at most 2mL^2. These give (13), with
slack. If no marked error is present, all one-insertion continuations are
good, yielding the stated K. If the orphan starts correct, it stays correct
in this R-only response and the same bounds apply. Removed marked errors
may use K, or the larger 64m(L^2+1/a).

## All eight cubic words

Let Z=m^3(L+1)^3/q. The ordered word XYZ means
e_C G X G Y G Z h_0, **not** a probability of exactly those noisy events.
Each use of an initially correct orphan insertion has wrong-child weight
d(n,y)d(y,n). Multiplication by a subsequent clean occupation bound
m(1/d(y,n)+L) leaves at most m(1+L) after summing over y. The negative
unchanged branch adds at most mL. This is entrance weighting, before taking
an absolute value.

The following bounds are candidate-proof consequences of the lemmas:

| Word | Bound | Reason |
|---|---:|---|
| RRR | 24 Z | (6)-(7), with F=h_1^R and orphan kept correct |
| RRO | 512 Z | Second R annihilates f_1; apply (7) to e_1<=64M^2 |
| ROR | 1024 Z | After first R, O h_1^R is bounded by twice (13); the first R's acceptance factor a cancels 1/a |
| ROO | 1024 Z | First R annihilates f_2; use e_2<=512L^3 on regular continuations |
| ORR | 1536 Z | Weighted R h_1^R<=512mL^2 from (13); first O cancels its following 1/d residence |
| ORO | 384 Z | R annihilates f_1; R e_1<=128L^2, then use first-O entrance weighting |
| OOR | 384 Z | O h_1^R<=2K on the baseline corner/orphan family; first-O weighting again |
| OOO | 32/q^4 | Audited discounted autonomous-orphan identity |

For clarity, the ROR estimate uses |G O h_1^R|<=
128m^2 L(L^2+1/a) after a marked first R. Summing the first R's wrong
overwrites with their factors a, and its clean-repair and unchanged terms,
gives at most 1024m^2L^3 per initial attempt. For ORR, the analogous
overwrite-minus-stay sum is at most 512mL^2; its clean occupation after O
and the first-O subtraction give at most 1536m^3L^3/q. For ORO and OOR,
the first-O factor is m(1+2L), and 1+2L<=3L.

For OOO, only the orphan can be corrupted and the corner has an independent
geometric(q) clean repair clock. The audited identity is

\[
 m_O(v)=\frac{[(I-(1-q)A(v))^{-1}]_{nn}}{\nu_v(n)}.
\]

Its clean discounted inverse has norm 1/q; the coefficient of A has norm
at most two. The coefficient of degree j is bounded by
(j+1)(2/q)^j/q. Taking j=3 gives the table's 32/q^4. The ordinary un-discounted
orphan hitting function is not bounded in this step.

Adding the seven R-containing words, the OOO bound, and (8) gives, for n>=4,

\[
 |C_n|\le10000\frac{m^3(20n+1)^3}{q}+\frac{32}{q^4}.   \tag{14}
\]

Since q>=1/(3n), m<=2n, and 20n+1<=21n, (14) is less than
10^10 n^7. For n=3, the exact rational calculation independently checked
by the full-state oracle verifies (1). No asymptotic extrapolation of
numerical coefficients enters this final step.

## What is and is not settled by this candidate

**Mechanically checked:** exact cubic coefficients and the independent
small-state oracle; the even-n recipient-word sums; the excess and weighted
R-response inequalities on the stated finite grid. See [README.md](README.md)
and [verification.json](verification.json). The code checks lower-order
coefficients against the published evidence before using them.

**Candidate proof:** (1), including both parities. It retains the supplied
entrance law and cancels the autonomous orphan hitting function before
bounding mixed insertions. It does not claim a polynomial norm for the
full resolvent, or polynomial higher residence moments for arbitrary S rows.

**Unresolved here:** independent audit of these new lemmas and constants,
a sharp order/sign of C_n, and a fourth-and-higher remainder uniform in n.
Even acceptance of (1) alone would only make the cubic term negligible
relative to p n log n when p=o(sqrt(log n)/n^3); without a uniform higher
remainder it supplies no new finite-noise sign window. The earlier desired
scale p=o(log n/n^4) is smaller, so this cubic bound would remove that
particular obstruction, but not the remaining orders.

**Falsifiers:** any disagreement of the independent cubic kernels or Poisson
equations; an omitted within-sweep term; a bad pair reachable after two
insertions without both acceptance factors; a regular configuration violating
the stated repair bound; failure of (10) at a last-pair state; a phase where
R f_j is nonzero; a failed (12) or (13); or an exact coefficient exceeding
(14). Negative finite Bernstein certificates from the prior audit would
only reject that certificate, not supply a cubic counterexample. Conversely
the known exponential residence witness does not refute (1).

The frozen original preregistration and blocked holdout are unchanged.
No new stochastic experiment, seed, current-literature search, or novelty
claim is used. The October 2026 noiseless radius/archive comparison remains
a model boundary, not a source theorem for this noisy coefficient.
