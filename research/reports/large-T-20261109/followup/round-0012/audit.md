# Independent audit of the phase potential and joint Schur elimination

**Verdict: proved under the stated pinned, closed-pair assumptions.** The
round-11 phase-potential argument, its real-positive-p residence and exit
bounds, and its **one-block** full-population extension survive this audit.
The higher-residence counterexample also survives. The proofs below rederive
the premises; they do not assume the earlier tagged-family construction,
coefficient asymptotics, or an unavailable manuscript appendix.

This is an independent implementation and analytic review in round 12, not a
second reviewer working concurrently in the same round. Exact finite checks
support the review but are not the justification of the all-n conclusions.
No full-population Taylor remainder or new noise window is proved here.

## Process, information, stopping, and units

**Definition.** Fix n>=3, adjacent targets a,b=a+1, supplied ideal extrema
(0,n), and stored labels fixed at their targets. In an isolated pair, breeder
a then breeder b mutate their own current incumbents. Each mutation flips
every bit independently with probability 1/n. An independent Bernoulli(p)
gate activates a second independent rate-1/n mask for observation. A single
observed child is offered to both targets. Pinned Tchebycheff selection
accepts observation k only at target k; it retains the child's true weight.

Write d(w,z) for the standard-bit mutation weight kernel. The state is
(x,y); A=(a,b), S consists of exactly one erroneous coordinate, D of two.
One pair sweep has two attempts, with boundary kernel P=K_0(p)K_1(p).
Intermediate alignment is retained, and true alignment is not absorbing.
The natural filtration F_t contains the supplied state and the masks/gates
consumed through attempt t, not future draws. The boundary filtration is
F_(2s). From D, sigma is the first positive boundary index in G=S union {A};
from S, tau_A is the first boundary index at A. All times below are sweeps.
In a population, one closed pair sweep occurs per full sweep; multiply full
sweep times by n+1 to obtain offspring attempts. Initialization is supplied
and has zero charged cost in these conditional calculations.

**Proved model qualification.** The actual filled-cardinality T=2 rule pairs
even a with a+1. If n is odd all these pairs are closed. If n is even,
breeder n offers to {n,n-1}, so {n-2,n-1} is not autonomous; earlier pairs
are closed. A synthetic isolated pair with odd a is covered by the algebra,
but is not an actual T=2 component. Neither clipped-radius neighborhoods,
overlapping T=3 neighborhoods, moving extrema, nor unpinned labels meet
these hypotheses. The noiseless radius/archive theorem in the repository's
literature comparison is not an input to this proof.

## Phase calculation and acceptance weighting

**Proved.** Let r(z)=d(z,a)+d(z,b) and
q(x,y)=1-(1-r(x))(1-r(y)). All these quantities are positive at finite n.
Before the first clean repair, neither coordinate changes. Its clean
remaining attempt times, for breeder a or b next, are

\[
 V_0(x,y)=(2-r(x))/q(x,y),\qquad
 V_1(x,y)=(2-r(y))/q(x,y),
\]

on D; set both to zero on G. Direct substitution gives
(1-r(x))V_1-V_0=-1 and (1-r(y))V_0-V_1=-1. These are phase identities,
not a drift assertion for the boundary chain killed at a midpoint.

For either phase and either current coordinate z, V<=2/r(z), since
q>=r(z). After an accepted child z leaves the pair in D, one coordinate
equals z, so the same inequality applies to the **new** potential.
Given any pre-attempt history with breeder weight w, the accepted active
contribution is therefore at most

\[
 \sum_z d(w,z)\{d(z,a)+d(z,b)\}\frac{2}{r(z)}=2.
\]

This keeps the acceptance probability. It does not assert that a retained
observation is unbiased, bound a conditional-on-entry residence, or give a
polynomial lower bound for all r(z).

Let K_i and J_i denote inactive- and active-gate attempt operators. On D,
the inactive operator has holding mass 1-r(w). The unaccepted active mass
is at most one, giving

\[
 (J_i-K_i)V_{1-i}\le r(w)V_{1-i}+2\le4,
 \qquad K_i(p)V_{1-i}-V_i\le-1+4p.             \tag{A}
\]

The first term r(w)V_{1-i} is needed: simply bounding accepted active
contributions would miss the changed holding probability. From S, a clean
attempt cannot create D, while the active accepted contribution is at most
2, so K_i(p)V_{1-i}<=2p. From A no single attempt can enter D; the chance
of entering S is at most p. All statements condition before the proposal.

## Restoring boundary time and obtaining an inverse

**Proved.** For a D start, the first attempt contributes at most -1+4p.
At the midpoint the second contribution is at most -1+4p on D, 2p on S,
and zero on A. For p<1/6 every case is at most 2p. Hence, with V=V_0 and
delta=1-6p>0,

\[
 P_{DD}V\le V-\delta\mathbf1.                         \tag{B}
\]

This explicitly allows D -> S -> D within one sweep. For an S start the
first expected midpoint potential is at most 2p. The second attempt cannot
increase it on D for p<=1/4, adds at most 2p on S, and adds zero on A.
For an A start the midpoint is never D and is S with probability at most p.
Thus

\[
 P_{SD}V\le4p\mathbf1,\qquad P_{AD}V\le2p^2.           \tag{C}
\]

Iterating (B), with its nonnegative terminal potential retained, yields
delta sum_(j=0)^m P_DD^j 1 <= V for every finite m. Monotone convergence
gives a finite R_D 1, where R_D=(I-P_DD)^(-1). In a finite state space this
establishes almost-sure exit and the inverse, without assuming either.
Multiplication by the nonnegative entrance rows in (C) proves

\[
 P_{SD}R_D\mathbf1\le\frac{4p}{1-6p}\mathbf1,
 \qquad P_{AD}R_D\mathbf1\le\frac{2p^2}{1-6p}.          \tag{D}
\]

Almost-sure exit also gives R_D P_DG 1=1. A sweep from S needs at least one
active gate to reach D, and one from A needs both. Consequently entry-weighted
exit mass is at most 2p from S and p^2 from A. Multiplying these bounds by
M bounds any nonnegative exit value bounded by M; it does not prove that an
unknown full-population completion value has such a polynomial M.

**Proved exact Schur identity.** The unrestricted trace on G has kernel and
time reward

\[
 \widehat P=P_{GG}+P_{GD}R_DP_{DG},\qquad
 w=\mathbf1+P_{GD}R_D\mathbf1.                         \tag{E}
\]

Its rows sum to one and entries are nonnegative. The initial transition
costs one sweep; R_D 1 counts the additional sweeps after an entrance into D.
Deleting w changes hitting times. Killing only at boundary A gives exactly

\[
 h_S=(I-P_{SS}-P_{SD}R_DP_{DS})^{-1}
          (\mathbf1+P_{SD}R_D\mathbf1).                \tag{F}
\]

From every S state, both gates inactive and a one-bit mutation of the
correct donor to the adjacent missing target imply boundary A, with
probability at least eta=(1-p)^2/(3n). If the other breeder acts first,
its clean update cannot spoil the already correct donor; if it acts later,
it cannot spoil the completed pair. This justifies the bound in either
phase ordering. The reduced transient row sum is at most 1-eta, so its
inverse has row sums at most 1/eta. Therefore

\[
 \max_{s\in S}E_s\tau_A\le
 \frac{3n}{(1-p)^2}\left(1+\frac{4p}{1-6p}\right).      \tag{G}
\]

This is uniform over the wrong weight in S, not over arbitrary D starts.
Constants are uniform on any p<=p_0<1/6, for example p<=1/12.
No tail statement is inferred from (G).

## The full-population tensor extension

**Proved.** Conditional on a specified full boundary state, a closed pair
uses disjoint donors, recipients, and fresh random masks from the rest.
Pinned labels/extrema prevent feedback through a reference update. Hence
the unrestricted boundary kernel is P tensor B, with B=P_rest stochastic.
This is a statement about transition rows; no independent initial law is
needed. Internal dependence among the rest's coordinates is allowed,
including the orphan-fed component at even n.

Kill only at the fully aligned boundary. Let U=D times all rest states, and
W be the other transient states. Global absorption is impossible while in
U at a boundary. Therefore

\[
 Q_{UU}=P_{DD}\otimes B,\qquad
 R_U=\sum_{j\ge0}P_{DD}^{j}\otimes B^{j}.               \tag{H}
\]

Nonnegative row sums of the partial sums in (H) are exactly those of the
pair partial sums, because B^j 1=1. Thus (B) proves convergence of the
full-block inverse, rather than a formal tensor manipulation assuming its
existence. For a W start whose pair component is g in G,

\[
 Q_{WU}R_U\mathbf1=(P_{gD}R_D\mathbf1).
\]

All extra rest-step factors, including the entrance transition, have row
sum one. This proves exactly the residence bounds (D) in the full chain.
Including the aligned absorbing exit makes exit rows stochastic; including
only W makes them substochastic, with the missing mass equal to global
absorption. The corresponding entry-weighted exit mass bounds remain 2p
or p^2. The exact reduced transient kernel and time reward are

\[
 Q_{WW}+Q_{WU}R_UQ_{UW},\qquad
 \mathbf1+Q_{WU}R_U\mathbf1.                           \tag{I}
\]

For completeness, the full hitting mean is finite at each fixed n and
p<1: condition on a whole sweep of inactive gates, and have each breeder
produce its own target. Every such mutation has probability at least
n^(-n). Once correct, a coordinate cannot be spoiled by subsequent clean
proposals. Thus a conditional full-sweep success probability of at least
[(1-p)n^(-n)]^(n+1)>0 holds from every boundary state. This elementary
finite-n argument ensures uniqueness of the full hitting solution and the
equivalence of (I); it supplies no useful polynomial uniform bound.

**Important scope.** R_U is not R_D tensor I. Its j-th term evolves the
rest j additional sweeps. Even replacing R_U by R_D tensor I while keeping
the genuine exit step changes the joint exit law; that shortcut evolves the
rest only once during the excursion. It can preserve row sums and the pair
exit marginal and still be wrong. Independently tracing every pair also
fails to retain a common population clock. Reinfection prevents replacing
simultaneous completion by a maximum of pair first-hit times. The audit
validates (I) for one selected closed pair; it does not justify applying the
same unchanged pair bound after repeated eliminations alter the kernels.

## Higher residence moments: audited obstruction

**Proved; the polynomial strengthening is contradicted.** At odd n take
the actual final pair (n-1,n), S0=(0,n), E=(0,0), and
v=n^(-n), c=(1-1/n)^n, r=[n(n-1)+1]v, s=1-r, q=1-s^2.
One active first attempt can generate true zero and observe n, with
probability coefficient cv. A subsequent clean holding attempt contributes
s. Thus E1(S0,E)>=cvs for E1=P_SD'(0). All S-to-D derivative entries are
nonnegative, since no clean sweep enters D from S. The clean D block is
diagonal: clean repairs cannot re-create errors. Consequently

\[
 (E1R_D(0)^2\mathbf1)(S0)\ge cvs/q^2\ge n^{n-4}/32.    \tag{J}
\]

The last inequality uses c>=1/4, r<=n^2 v<=1/2, s>=1/2, and q<=2n^2 v.
The same path's first-residence contribution is cvs/q, which is small.
The second geometric residence moment satisfies
R_D(0)^2 1(E)=(E L^2+E L)/2=1/q^2. Hence a polynomial bound on all such
entrance-weighted moments is impossible. Signed derivatives of (E) can
combine large terms that cancel; (J) alone says nothing about their sum or
the supplied-corner full Taylor remainder.

## Mechanical evidence, dependencies, and falsifiers

**Mechanically checked.** [audit.py](audit.py) imports no earlier solver.
It builds mutation probabilities by per-bit generating polynomials, tests
literal genotype-mask/selection rows, and solves integer-cleared systems
with exact residual verification. [phase.csv](phase.csv) checks all states
of all adjacent isolated pairs at n=3,...,8. Quadratic slack polynomials
have nonnegative degree-two Bernstein coefficients on [0,1/6], certifying
the entire interval for these finite pairs. The inverse formulas still
require strict p<1/6. [pair.csv](pair.csv) reproduces nine published Schur
solves with a separate implementation, including the boundary hitting
values. [tensor.csv](tensor.csv) checks every n=3 population row and four
explicit n=4 rows, where the rest includes the dependent orphan component.

[verification.json](verification.json) also records an exact full n=3
joint exit-law and hitting-equation audit. It retains every population state,
midpoint repair/reinfection, and the elapsed-time reward. Its shortcut tests
check the actual alternatives, not merely unit row sums: omission of time
underestimates the supplied-corner mean, and freezing the rest's internal
excursion steps changes the exit law in total variation. A positive n=4
orphan repair explicitly falsifies treating the last even-n pair as closed.
[moments.csv](moments.csv) independently reproduces (J)'s six exact witnesses.

**Mechanically checked numerical summary, not sampling.** At n=3, p=1/81,
the full chain has 256 states, U has 144, and W has 111. All 144 joint exit
rows and residence identities pass, and the direct 255-state transient
solution satisfies all 111 primary Schur equations exactly. A second reward
checks the deliberately incorrect deletion of U time. The displayed
decimals below are rounded exact fractions, with no statistical intervals.

| Quantity | Exact calculation, displayed as a decimal |
|---|---:|
| Full supplied-corner mean, sweeps | 4.810704305907737 |
| Underestimate if U residence time is deleted, sweeps | 0.026355723334401216 |
| Exit-law total variation error for R_D tensor I, U start (3,3,0,0) | 0.2027767542819273 |
| Correct one-pair trace's mass exiting with the other pair in D, from the corner | 0.000005369598552685596 |

The frozen-rest comparison retains the genuine final exit step, so it allows
one rest transition and preserves the pair exit marginal. It still fails.
The last row also shows why the output of this one-pair trace is not confined
to G times G, as a product of separately traced pair kernels would be.

The independent finite audit checks 1,312 literal attempt rows, 2,574 clean
phase identities, 5,154 nonnegative Bernstein coefficients across 33 adjacent
pairs, 27 published rational values from nine pair solves, and 78,036 exact
population transition entries. Finite counts and proofs remain separate.

**Mechanically checked dependencies.** [dependency.json](dependency.json)
records complete round-11 reproduction, recursively checking earlier plans,
receipts, seed separation, published algebra, and the blocked holdout. No
repair was needed. The round-10 divergent absolute majorant is context,
not a premise of (A)-(I). No new scientific samples, seeds, intervals, or
empirical fit were generated. Deterministic exhaustive algebra is not a
new randomized experiment; no prior-round sampling plan is being bypassed.

**Unresolved in this checkout:** bounding the remaining full-population
inverse or its signed derivatives uniformly, joint synchronization under
reinfection, even-n orphan/last-pair feedback, overlapping T=3 neighborhoods,
and a third-and-higher remainder on p=o(log(n)/n^4). The prior finite-noise
window remains unchanged. An empirical finite comparison does not fill any
of these gaps. No external novelty or current-literature completeness claim
is made in this offline audit.

**Falsifiers.** A phase-recurrence failure, accepted-potential bound violation,
negative Bernstein coefficient (a failed certificate, not automatically a
counterexample to the polynomial), violated boundary inequality at an actual
p, literal transition mismatch, incorrect joint tensor row, nonunit full
exit mass, or Schur/direct hitting disagreement would reject the associated
step. Generalizing the result to the last even-n pair already meets the
explicit orphan counterexample. Any proposed polynomial bound on
E1 R_D(0)^2 1 must confront (J). A claimed cubic or all-order conclusion
must establish cancellations for the actual signed observable; first-moment
control alone is not such a conclusion. A bound on real nonnegative p
does not supply a bound on a complex neighborhood for analytic derivative
estimates. Nor does failure of an absolute power-series bound imply failure
of a finite-order approximation after exact real-p resummation.
