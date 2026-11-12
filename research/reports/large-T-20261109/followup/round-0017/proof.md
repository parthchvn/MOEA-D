# ORRR with the wrong-orphan entrance retained

**Candidate proof, awaiting independent analytic audit.** For even n>=4,
in the supplied pinned T=2 process defined below, put m=n+1, L=20n and

\[
q=1-(1-d(2,0))(1-d(1,0)).
\]

The proposed bound, in full-population sweeps, is

\[
\boxed{|\mathrm{ORRR}|\le2048\,m^3L^4/q<8\cdot10^9 n^8.}       \tag{1}
\]

This is a bound on one ordered fourth-order response. The proof does not
commute O past R, use the isolated-pair second-response candidate, or assume
independence of the last pair and orphan. It does not establish polynomiality
of the full fourth coefficient or a uniform Taylor remainder. The new
argument and the finite exact checks are separate evidence: the checks
cannot establish (1) for all n.

## Process, phase and response

**Definitions.** Initialize true weights C=(2,1,2,...,n), ideal extrema (0,n)
and pinned labels b_k=k, at zero initialization cost. Breeders 0,...,n repeat
in ascending order, mutating their own incumbent by independent bit flips
of rate 1/n. A fresh Bernoulli(p) gate activates an independent observation
mask of the same rate. One observation is offered to the filled cardinality
two neighborhood: even breeders prefer right, odd breeders left, skipping
invalid indices. Thus the last even breeder n offers to n and n-1.
The max-Chebyshev scalarization is max{k(n-w),(n-k)w}; pinned recipient k
accepts only observation k and stores the child's true weight. T is
cardinality, not radius.

The filtration reveals supplied state and consumed masks/gates through each
attempt. The actual stopping time is the first phase-zero boundary with all
true weights correct. Interior aligned states remain live. All clean
stopping calculations below condition before proposals and use fresh masks;
no acceptance-conditioned distribution or drift theorem is used.

Let K be the clean kernel on population and next-breeder phase i. Kill only
at the aligned phase-zero state. Its occupation matrix G exists for each
fixed n: clean errors only disappear and every own repair has positive
probability. Reward 1/m per attempt gives h0=G(1/m). Split the activated-minus-
clean attempt difference by recipient as R+O: R changes regular slots
0,...,n-1 and O changes only orphan n, at breeder n only. Both are signed
differences of recipient-restricted stochastic kernels, with row sum zero.
This is an algebraic split of the shared observation, not independent gates.

Define H0=h0 and Hj=G R H(j-1). In chronological insertion order,

\[
\mathrm{ORRR}=e_C G O H_3.                            \tag{2}
\]

Finite-state analyticity justifies these Taylor/word identities for fixed n.
Words are signed responses, not probabilities of specified activation counts.
Initialization, rewards and killing conventions are unchanged.

## New centering identity and the boundary compensation

**Candidate lemma, with exact finite checks.** For orphan value y let A_y
be the population with every regular slot correct and orphan y. At every
phase define

\[
B_j(y,i)=H_j(A_y,i),\qquad D_j(s,i)=H_j(s,i)-B_j(s_n,i).
\]

The subtraction is phase specific. Since R preserves y and has row sum zero,

\[
g_j(s,i):=(R_iH_{j-1})(s,i+1)=(R_iD_{j-1})(s,i+1),\quad j\ge1. \tag{3}
\]

The successor phase wraps to zero after breeder n. Put

\[
\lambda_0=1,\qquad \lambda_j=\sum_{i=0}^{n}g_j(A_n,i),\quad j\ge1. \tag{4}
\]

These compensations are necessary because H_j is zero at aligned phase
zero, while its unrestricted one-step equation there need not vanish.
Indeed, along the clean aligned cycle H_j(A_n,i)=sum_{t=i}^n g_j(A_n,t)
for i>0, but H_j(A_n,0)=0. On all states, including this killed state, the
extended equation is

\[
H_j=g_j+K H_j-\lambda_j1_{\{s=A_n,i=0\}}.             \tag{5}
\]

For j=0 replace g_j by the constant 1/m. Clean orphan evolution is
autonomous. Couple a clean population s to A_y using the same orphan proposal;
all other baseline slots remain correct. The two chains coalesce once the
regular population is correct. At breeder n the shared proposal can repair
the last pair or the orphan; their dependence is retained.

Let rho be the first future regular-complete phase-zero boundary, allowing
rho=0 for a regular-complete boundary start. Subtract (5) for the two
chains and stop at rho. Before rho, the actual chain is never aligned at
phase zero, whereas the baseline is aligned there exactly when Y=n. Thus

\[
D_j(s,i)=E\sum_{t<\rho}\left[
g_j(S_t,I_t)-g_j(A_{Y_t},I_t)
+\lambda_j1_{\{Y_t=n,I_t=0\}}\right],\quad j\ge1.     \tag{6}
\]

Time t in (6) counts attempts. For j=0 the g terms cancel and D0 is the
expected count of correct-orphan phase-zero boundaries before rho. In
particular 0<=D0<=M whenever the expected clean regular completion time,
including phase slack, is at most M sweeps. D_j=0 whenever the regular
slots are already correct, at every phase. One may then stop at their
first mid-sweep completion in (6); all omitted summands are zero before
the stopping boundary. This is an auxiliary identity, not a changed runtime
event.

For each fixed n all response functions are finite on a finite state space.
The clean regular completion bounds below are integrable; truncation proves
the stopped sum and terminal equality. No higher moment is inferred from
a single expected hitting time. Omitting lambda_j is a false identity:
[flux.csv](flux.csv) gives nonzero exact compensations.

## Clean families and accepted overwrites

**Verified earlier premise, rederived for the needed budget.** Closed pairs
are {0,1},{2,3},...,{n-2,n-1}; the last also receives breeder n. Ignoring that
extra donor can only remove clean repairs. A correct partner repairs the
adjacent target with probability at least 1/(3n) per scheduled visit. The
original error w0=2 is special: even if slot 1 is wrong, breeder 0 repairs
it with probability at least 2/(3n), or at least 1/3 if w0 has repaired to 0.

Consider clean descendants of C or A_n after at most three arbitrary regular
overwrites, allowing any orphan value. Call a pair bad when both slots are
wrong, except that {0,1} with w0=2 remains fast. At most one bad pair can
exist: two generic surviving wrong values require two overwrites, and a
second such pair would require two more. The original corner does not supply
a generic slow value. All good configurations needed here have at most four
regular errors and regular completion mean at most L, from every phase.

With a bad pair at k,k+1, put a=d(x,k), b=d(z,k+1) and

\[
M=L+2/(a+b).                                         \tag{7}
\]

Its two own turns escape with probability at least (a+b)/2 per full sweep.
The initial partial sweep and at most three subsequent good extensions fit
inside (7). These bounds hold along every clean descendant and uniformly
over orphan evolution. They bound both expected attempts/m and expected
number of phase-zero boundaries before regular completion. No polynomial
lower bound on a or b is claimed.

An active overwrite of k by x has its actual positive weight
d(parent,x)d(x,k). If it changes a bad-pair coordinate, its accepted extra
wait is bounded before summation by

\[
d(x,k)\frac{2}{d(x,k)+b}\le2.                        \tag{8}
\]

With two candidate recipients, the active expectation of D0 is therefore
at most M+4, and the clean restricted expectation at most M. This covers
both creation of a new bad pair from a good state and modification of an
existing one. One extra overwrite outside the existing bad pair cannot
create a second bad pair within this insertion budget. Since D0>=0,

\[
|g_1(s,i)|\le M+4\le2M,\quad
|g_1(A_y,i)|\le L,\quad |\lambda_1|\le mL.            \tag{9}
\]

The second inequality uses the fact that a single overwrite from A_y has a
correct partner. Combining (6), expected attempts <=mM and boundary counts
<=M yields the useful uniform centered bound

\[
|D_1(s,i)|\le5mM^2.                                  \tag{10}
\]

It holds for all orphan values and every phase after at most two regular
overwrites. In particular, every good state in that family satisfies
|D1|<=5mL^2. This bounds a difference of responses; it does not assert the
same bound for the uncentered H1 at every wrong-orphan state.

## Two centered responses after a marked overwrite

**Candidate lemma.** Start with C or its clean subset and one arbitrary
regular overwrite x at k, whose acceptance is a=d(x,k)>0. Keep a as a
remembered mark if clean repair later deletes the error. All these starting
states are good. A subsequent birth can create a bad pair only by supplying
the marked error's wrong partner. For that birth's acceptance b,

\[
b\{L+2/(a+b)\}^2\le2L^2+2/a.                       \tag{11}
\]

This uses (u+v)^2<=2u^2+2v^2 and b/(a+b)^2<=1/(4a).
For each recipient, sum the mutation row only after (11). Two possible
recipients and (10) bound the active absolute D1 expectation by
5m(5L^2+4/a), and the clean one by 5mL^2. Hence

\[
|g_2(s,i)|\le32m(L^2+1/a).                           \tag{12}
\]

From A_y, or the unmarked corner and its clean subset, a single birth is
still good. Thus |g2|<=10mL^2 on that unmarked family, and
|lambda2|<=10m^2L^2. Apply (6), now with regular duration <=L, to obtain

\[
|D_2(s,i)|\le64m^2L(L^2+1/a)                         \tag{13}
\]

on the marked family, uniformly in y and phase. For the unmarked family
the sharper bound |D2|<=64m^2L^3 follows by using 10mL^2 for both g terms.
The constants before rounding are 52 and 30 respectively. The proof uses
the regular completion time only; it never integrates a constant forcing
over an uncontrolled wrong-orphan lifetime.

From an unmarked corner/subset state, an R birth of x at k retains
a=d(x,k) in (13). Summing at most two mutation rows and adding unchanged
and suppressed-clean branches gives

\[
|g_3(s,i)|=|(R_iD_2)(s,i+1)|\le512m^2L^3=:B.          \tag{14}
\]

For clarity, the active absolute expectation is at most
64m^2L^3+128m^2L(L^2+1)<=320m^2L^3, and the clean one at most 64m^2L^3.
Thus 384 already suffices in (14). Negative unchanged-state terms have not
been discarded. The parent may depend on earlier repairs/overwrites; each
conditional mutation row still sums to one.

## The first O and its actual entrance factor

**Candidate assembly.** After O, no regular overwrite has yet occurred.
The regular state is C or its clean subset. If the orphan is y<n, write
d_y=d(y,n). Its clean repair time has mean 1/d_y sweeps; regular completion
has mean <=L. Joint completion is bounded by their sum without an
independence assumption. Using (14) in H3=Gg3, at a boundary,

\[
|H_3(s,y)|\le mB(L+1/d_y),\qquad |H_3(s,n)|\le mBL.   \tag{15}
\]

Before the first O the orphan is correct. Its positive birth of y<n has
exact coefficient

\[
c_y=d(n,y)d_y,                                      \tag{16}
\]

and its other branch is the negative unchanged state. Equations (15)-(16)
give, before taking any supremum over y,

\[
|O H_3|\le mB\sum_{y<n}c_y(1/d_y+2L)
\le mB(1+2L)\le3mBL.                               \tag{17}
\]

This is the requested wrong-orphan entrance retention. Dropping d_y before
the occupation bound would introduce an unjustified inverse minimum repair
rate. The initial clean corner reaches breeder n once per unsolved sweep;
its expected count is exactly 1/q. Hence (2) and (17) give
|ORRR|<=1536m^3L^4/q, which is below (1). Finally q>=1/(3n) and m<=2n
give the stated O(n^8) bound.

At phase n the current corner error survives with probability 1-q.
Consequently the exact implementation also uses

\[
\mathrm{ORRR}=q^{-1}\{(1-q)(O H_3)(C,n)+q(O H_3)(A_n,n)\}.       \tag{18}
\]

The second term is necessary: a clean repair earlier in a sweep does not
kill the trajectory before the final orphan turn.

## Evidence, limits and falsifiers

**Mechanically checked:** [centered.py](centered.py) directly solves (6),
using regular-completion killing and the compensation (4). It reconstructs
H3 and ORRR from (14)/(18). Checks compare centered differences with the
separate published phase solver and ORRR with both published phase and
sweep solvers at n=4. Exact fractions/hashes and finite-grid scope are in
[verification.json](verification.json), [centered.csv](centered.csv) and
[words.csv](words.csv). [entrance.csv](entrance.csv) retains d_y and c_y.
These are deterministic rational calculations, with no sampling intervals
or censoring. The finite grid is not an exhaustive all-population proof.

**Dependency status:** the relevant round-16 replay reproduces its six
outputs and recursively verifies earlier geometry, plans, receipts and
seed separation. No plan/receipt repair was needed. The proof uses the
audited clean geometry and acceptance arithmetic, not the unaudited
isolated-pair second response or an uncomputed positive-p remainder.

**Remaining proof obligation:** independently audit (5)-(6), the surviving-
overwrite budget in (8)-(10), and the marked transition from (11) to (14).
These are the new all-n steps. The last-pair/orphan dependence is included
through the common clean orphan proposal; it must not be replaced by
independent repair clocks. No bound here upgrades the conjectured full
fourth gap, fixed-positive-c ordering, or ordinary-initialization behavior.
No current-literature search or novelty claim is made in this offline work.
The repository's noiseless radius/archive literature comparison is unchanged.

**Falsifiers:** failure of the centered Poisson identity at any phase;
nonzero R acting on a baseline-only function; a required clean descendant
outside the one-bad-pair budget; a violated acceptance-weighted bound; an
independent ORRR rational mismatch; or an exact value exceeding (1).
Omitting the compensation is already falsified by its nonzero exact values.
The prior exponential positive-residence counterexamples remain valid and
are not lower bounds on this signed word.

The original preregistration, capped trial, blocked 240-row holdout and
inconclusive original two-stage decision remain unchanged. No new random
trajectory or seed was generated; a new stochastic measurement would require
its own plan committed in a prior round.
