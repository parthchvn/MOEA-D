# Real-p elimination of a closed T=2 pair

**Candidate proof, with exact finite checks; not independently audited.** Yes:
for an autonomous T=2 pair, the entire double-error block can be eliminated at
real noise probability without a Neumann expansion in p. The resulting
transition kernel is nonnegative and stochastic. Its acceptance-weighted
residence reward and its exits to polynomially bounded values are polynomial.
This is stronger than positivity of each holding denominator.

For 0 <= p < 1/6, let D denote the double-error states, S the single-error
states, A the aligned state, G=S union {A}, and P(p) the **two-attempt pair
sweep**, retaining aligned intermediate states. Write

\[
 R_D(p)=(I-P_{DD}(p))^{-1},\quad \delta=1-6p.
\]

The proposed uniform bounds, componentwise, are

\[
 P_{SD}R_D\mathbf1\le {4p\over\delta}\mathbf1,\qquad
 P_{AD}R_D\mathbf1\le {2p^2\over\delta},                 \tag{1}
\]
\[
 R_DP_{DG}\mathbf1=\mathbf1,\quad
 P_{SD}R_DP_{DG}\mathbf1\le2p\mathbf1,\quad
 P_{AD}R_DP_{DG}\mathbf1\le p^2.                         \tag{2}
\]

In particular these bounds are O(p), O(p^2), O(p), and O(p^2), with constants
independent of n for p<=1/12. For any nonnegative exit reward f on G bounded
by M(n), the last two bounds remain valid after multiplication by M(n).
A separate consequence is the following actual noisy boundary hitting bound
from **every single-error pair state**, including arbitrarily bad wrong weights:

\[
 \max_{s\in S} E_s\tau_A
 \le M_n(p):={3n\over(1-p)^2}
       \left(1+{4p\over1-6p}\right).                    \tag{3}
\]

Times in (1) and (3) are pair sweeps, one of which occurs per population
sweep for a closed pair. They are not full-population completion times.
The supplied corner lies in S for the first pair {0,1}.

**Contradicted strengthening.** A polynomial first-moment bound does not
extend to all iterated residence resolvents: for an actual last T=2 pair at
odd n, with E1 = (d/dp)P_SD(p) at zero and R_D0=R_D(0),

\[
 (E1\,R_{D0}^{\,2}\mathbf1)_{(0,n)}
 \ge {n^{n-4}\over32}.                                \tag{4}
\]

This is a nonnegative quantity, and no Taylor cancellation is being invoked.
It identifies a precise limitation of an attempted moment-based continuation.
It does **not** show that the full completion-time Taylor coefficient or
remainder is superpolynomial.

## Exact process and scope

**Definition.** Fix n>=3 and adjacent targets a,b=a+1. Both breeders offer to
exactly these two targets, in order a then b, and receive no proposals from
outside the pair. The pair state is (x,y), its true Hamming weights. Labels
are permanently pinned at (a,b), and ideal observed extrema (0,n) are supplied.
Every attempt mutates its breeder's own incumbent, flipping each bit
independently with probability 1/n. A fresh Bernoulli(p) gate activates a
second independent rate-1/n bit mask for observation. Let D_n(w,z) be the
mutation weight kernel; below abbreviate it to d(w,z).

Pinned Tchebycheff selection accepts only observation equal to the recipient's
target. Thus child weight z observed as k replaces just coordinate k if
k is one of a,b. Rejections and accepted unchanged values are retained.
The labels and reference remain pinned, but true alignment is not absorbing.
Stopping for (3) occurs only at the first aligned **boundary**, never midway
through the two attempts.

The filtration F_t reveals the initial pair state and exactly the masks and
gates consumed through its t-th attempt. G_s=F_(2s) is the pair boundary
filtration. Starting in D, sigma is the first s>=1 with X_(2s) in G.
Starting in S, tau_A is the first s>=0 with X_(2s)=A. Drift calculations
below condition on F_t before a proposal. No conditioning on accepted or
retained observations is used. The proof sums bounded-horizon inequalities;
no external drift theorem or tail-from-mean argument is applied.

**Proved neighborhood qualification.** Under the frozen filled-cardinality
rule, odd n partitions into closed pairs {0,1},{2,3},...,{n-1,n}. Their
boundary kernels are autonomous. At even n, breeder n is an orphan and
also offers to n-1. The last pair {n-2,n-1} then has an external incoming
proposal and is excluded from this autonomous-pair theorem. Earlier pairs
are closed. A symmetric radius or a T=3 neighborhood is a different process.
For arbitrary a, the calculation defines an isolated adjacent-pair model;
the actual T=2 pairs additionally have even a and the qualification above.

## Clean phase potential and exact acceptance cancellation

**Proved local identities.** Put

\[
 r(z)=d(z,a)+d(z,b),\qquad
 q(x,y)=r(x)+r(y)-r(x)r(y)>0.
\]

For a double-error state, a clean accepted observation immediately leaves D.
Until this happens neither coordinate changes. The clean process killed at
its first departure from D consequently has expected remaining attempt times

\[
 V_0(x,y)={2-r(x)\over q(x,y)},\qquad
 V_1(x,y)={2-r(y)\over q(x,y)},                           \tag{5}
\]

where phase 0 means breeder a next and phase 1 means breeder b next. Set
both potentials to zero on G. In (5) the killing convention is only an
auxiliary calculation; the noisy boundary process continues through G.
If K_i is the clean attempt operator, the two elementary recurrences give

\[
 K_i V_{1-i}-V_i=-1\quad\hbox{on D}.                    \tag{6}
\]

Because q>=r(x),r(y), each potential is at most 2/r(z) for **either** current
coordinate value z. After an erroneous overwrite by child z, any resulting
D state therefore satisfies V_(next)<=2/r(z). In particular an active
proposal from arbitrary parent w has accepted D-state contribution at most

\[
 \sum_z d(w,z)\sum_{k\in\{a,b\}}d(z,k){2\over r(z)}
 =2.                                                   \tag{7}
\]

Discarding outcomes which do not stay in D only lowers this bound. Equation
(7) is unconditional before selection and retains the acceptance factor
d(z,k). It cancels the potentially enormous inverse repair weight. No minimum
repair probability is replaced by a polynomial lower bound.

Let J_i be the active-noise attempt operator. Its unaccepted mass is at most
one. On D its difference from the clean operator consequently obeys

\[
 J_iV_{1-i}-K_iV_{1-i}
 \le r(w)V_{1-i}+2\le4.                               \tag{8}
\]

The first term accounts for replacing the clean holding mass 1-r(w), and
must not be omitted. For K_i(p)=(1-p)K_i+pJ_i, (6) and (8) yield

\[
 K_i(p)V_{1-i}-V_i\le-1+4p\quad\hbox{on D}.             \tag{9}
\]

From S a one-attempt entry into D must corrupt its correct coordinate k.
The same acceptance cancellation gives

\[
 K_i(p)V_{1-i}\le2p\quad\hbox{on S}.                    \tag{10}
\]

A cannot reach D in one attempt: a shared observation accepts at most one
target. Starting from A, the probability of being in S after one attempt
is at most p. Clean proposals cannot create an error.

## Restoring the true boundary timing

**Candidate application; all cases explicitly retained.** Write
P=K_0(p)K_1(p), and V=V_0. For a state initially in D, (9) on the first
attempt bounds expected midpoint V_1 by V-1+4p. The second attempt contributes
at most -1+4p if its midpoint is in D, at most 2p if in S, and zero if in A.
For p<1/6 this implies

\[
 P_{DD}V\le V-(1-6p)\mathbf1.                           \tag{11}
\]

This deliberately loose bound allows a clean repair on attempt one followed
by corruption back into D on attempt two. Omitting such paths would change
P_DD and its Schur complement.

From S the first attempt contributes at most 2p to the midpoint potential.
If the midpoint is D, (9) says the second attempt cannot increase it when
p<=1/4; if it is S, (10) adds at most 2p. From A the first attempt cannot
reach D, and its chance of a midpoint S is at most p. Therefore

\[
 P_{SD}V\le4p\mathbf1,\qquad P_{AD}V\le2p^2.             \tag{12}
\]

Iterate (11) with the nonnegative matrix P_DD. For every integer m>=0,

\[
 \delta\sum_{j=0}^mP_{DD}^j\mathbf1\le V.
\]

Each finite-n entry of V is finite; monotone convergence gives finite
R_D1 and almost-sure exit. Equivalently E sigma<=V/delta from each D state.
Multiplying this bound by the nonnegative entrance matrices and using (12)
proves (1). This is a real-p argument and uses no expansion about p=0.
It is valid even when p times the absolute insertion norm exceeds one.

For completeness, at any p<1 the event of two inactive gates and a clean
escape also proves eventual exit at each fixed n. That argument alone gives
only a possibly enormous bound. The quantitative estimates (1)-(3) are
restricted to p<1/6, uniformly bounded away from 1/6 when polynomial order
with n-independent constants is intended.

## Schur complement, reward, and exits

**Proved matrix identities once (11) holds.** A full pair boundary transition
is stochastic. Almost-sure exit from D gives R_DP_DG1=1. Moreover an S-to-D
sweep needs at least one active gate, and an A-to-D sweep needs both gates,
so P_SD1<=2p and P_AD1<=p^2. These observations prove (2).

Eliminating D from the unrestricted pair chain gives the exact trace kernel
on G and its expected time reward

\[
 \widehat P=P_{GG}+P_{GD}R_DP_{DG},\qquad
 w=\mathbf1+P_{GD}R_D\mathbf1.                          \tag{13}
\]

The trace kernel has nonnegative entries and row sums one. Its reward counts
one sweep for the current transition plus every omitted D-boundary sweep.
Keeping w is essential; deleting D visits without their time cost does not
preserve completion times. Equations (1)-(2) bound w and every polynomially
bounded exit value without needing a polynomial bound on R_D itself.

For pair absorption at A, let h_S,h_D be the boundary means, with h(A)=0.
Block elimination of their first-step equations gives exactly

\[
 h_S=\bigl[I-P_{SS}-P_{SD}R_DP_{DS}\bigr]^{-1}
        \bigl[\mathbf1+P_{SD}R_D\mathbf1\bigr].          \tag{14}
\]

From any S state, two inactive gates and the correct neighbor mutating to
the missing target imply a boundary A. Since the targets are adjacent,
that one-flip probability is at least (1-1/n)^(n-1)/n >=1/(3n).
Clean later proposals preserve correctness. Thus each row in the reduced
transient kernel has missing mass at least eta=(1-p)^2/(3n).
Its inverse has infinity norm at most 1/eta. Combining (14) with (1) proves
(3), including an arbitrarily bad existing error in S.

The accepted excursion contribution to the actual pair completion value
also has a polynomial bound:

\[
 P_{SD}h_D\le{4p\over\delta}+2pM_n(p),\qquad
 P_{AD}h_D\le{2p^2\over\delta}+p^2M_n(p).               \tag{15}
\]

Here P_AD is the unrestricted transition out of A even though h(A)=0 in
the hitting calculation. Equation (15) follows from h_D=R_D1+R_DP_DS h_S.
All bounds are uniform over the entrance S row; none conditions on entry.
Dividing by a tiny entry probability can produce a very large conditional
residence time, and is not part of the claim.

## Exact elimination inside the full pinned population

**Candidate extension, by a tensor identity.** A closed pair has no shared
recipients or random draws with the remainder of the pinned population.
The frozen reference and labels remove any other source of feedback. Thus
the unrestricted boundary kernel factors exactly as P_pair tensor P_rest.
P_rest is stochastic; its coordinates need not be independent of each other.
This statement holds for any closed pair, including an early pair at even n.

Kill the full population only at its fully aligned boundary. Let U consist
of all full states whose selected pair is in D, and let W contain the other
transient states. While in U, global absorption is impossible. Consequently

\[
 Q_{UU}=P_{DD}\otimes P_{\rm rest},\qquad
 (I-Q_{UU})^{-1}
 =\sum_{j\ge0}P_{DD}^{\,j}\otimes P_{\rm rest}^{\,j}.    \tag{16}
\]

Taking row sums gives exactly the pair residence R_D1, for every other-state
coordinate. From a W row, the entry-weighted residence is exactly
P_gD R_D1, with g the pair component of that row: P_rest contributes row
sum one at every step. Thus the full-process time reward and bounded exit
reward have the same bounds (1)-(2). If only transient exits W are included,
exit rows have mass at most one; the missing mass is global absorption.
The killed Schur kernel is

\[
 Q_{WW}+Q_{WU}(I-Q_{UU})^{-1}Q_{UW}.                    \tag{17}
\]

It is nonnegative and substochastic and preserves both the stopping event
and elapsed time when equipped with reward
1+Q_WU(I-Q_UU)^(-1)1. The power of P_rest in (16) is essential. Replacing it
by the identity, or merely tensoring the separately traced pair kernels,
would change the process. This exact one-block elimination does not give a
polynomial inverse for (17), a derivative bound, or a justified repeated
elimination of all double-pair blocks after their kernels have changed.

## A higher-residence obstruction that remains after elimination

**Candidate proof of a negative result, mechanically checked.** Take odd
n, the actual pair a=n-1,b=n, S0=(0,n), E=(0,0). Put

\[
 v=n^{-n},\quad c=(1-1/n)^n,\quad
 r=[n(n-1)+1]v,\quad s=1-r,\quad q_E=1-s^2.
\]

A positive contribution to E1(S0,E) is: on the first turn the weight-zero
breeder produces true child zero with probability c and, under activation,
observes n with probability v; on the second clean turn the new weight-zero
breeder avoids observations a,b with probability s. Thus
E1(S0,E)>=cvs. All one-insertion entries from S to D are nonnegative,
because a clean sweep cannot create a second error.

The clean D block is diagonal: every clean accepted target leaves D, so
R_D0(E,E)=1/q_E. Consequently

\[
 (E1 R_{D0}^{\,2}\mathbf1)(S0)\ge {cvs\over q_E^2}.
\]

For n>=3, c>=1/4, r<=n^2v<=1/2, s>=1/2 and q_E<=2n^2v.
These inequalities prove (4). In contrast, this same path's **first**
residence contribution is cvs/q_E, approximately c/(2n^2).

The iterated resolvent is related to a second residence moment: for a
geometric clean exit time L at E, R_D0^2 1(E)=(E L^2+E L)/2=1/q_E^2.
Hence a uniform polynomial bound on these entry-weighted moments is false.
An algebraic derivative of (13) can contain signed combinations of such
large terms. Their cancellation, additional entrance weighting from the
supplied corner, or a completion discount must be handled before using
(13) for a uniform Taylor remainder.

## Evidence, limits, and falsifiers

**Mechanically checked:** [check.py](check.py) independently constructs the
weight kernel by lost/gained-bit counting, checks it against literal XOR
masks, checks attempt rows against literal scalar comparisons, and uses exact
rational arithmetic throughout. [inequalities.csv](inequalities.csv) checks
all double and single states in the closed pairs at n=3,5,7,9, for p=0,
n^-4, 1/(64n), and 1/12. [schur.csv](schur.csv) solves both the unreduced
pair hitting equations and the Schur-reduced equations exactly in nine cells.
It verifies stochastic exits and nonnegative time rewards.
Direct full-population rows at n=3 also check the tensor factorization in
(16), retaining intermediate aligned states.
[moments.csv](moments.csv) records exact witnesses for (4).
[verification.json](verification.json) records counts, with no sampling error
or confidence intervals attached to deterministic values.

**Mechanically checked dependencies:** the complete round-10 replay reproduces
its four published outputs and recursively verifies rounds 1-9, the prior
registration, receipts, seed disjointness and blocked holdout. No repair was
needed. [dependency.json](dependency.json) records hashes and the unchanged
empirical estimates. The previous absolute-majorant obstruction is contextual;
(5)-(15) do not assume it, the earlier tagged-forest theorem, the small-noise
coefficient proofs, or an unavailable manuscript appendix.

**Open in this checkout:** a full-population third-and-higher-order bound on
p=o(log(n)/n^4). The pair results alone do not prove it. Equation (16)
preserves other-pair evolution during omitted sweeps, but gives no bound on
the remaining global inverse. Tracing each pair separately and adding means
does not preserve the joint simultaneous-alignment event. Even at odd
n, pair independence does not turn simultaneous completion into the maximum
of first hitting times, because pairs can be reinfected. At even n the orphan
feeds the last pair, and T=3 has overlapping neighborhoods. Those components
also remain outside the autonomous calculation. No enlarged full-process sign
window, fixed-c ordering at p=c/n, ordinary-initialization result or new tail
bound is claimed. The general arguments here await independent audit.

**Falsifiers:** an incorrect literal attempt row; failure of a clean phase
identity (6), accepted-potential bound (7), boundary drift (11), or entry bound
(12); a reduced hitting value differing from the direct solution; a nonunit
exit row sum; or an omitted within-sweep repair/reinfection path would falsify
the associated result. A purported uniform polynomial higher-residence bound
must confront the explicit family (4).

**Offline literature boundary:** the repository compares Benjamin Doerr,
Moaad Elmoutassim, Martin S. Krejca and Guy Mushiata Kibulu, *Understanding the
Co-evolutionary Solution Exchange of the MOEA/D: Already the Smallest
Communication Radius Gives the Best-Possible Speed-Up* (2026),
arXiv:2610.35373, DOI:10.48550/arXiv.2610.35373. Its noiseless radius/archive
theorem is not transferred here. No current literature search or global
novelty/open-problem assertion is made in this offline task.
