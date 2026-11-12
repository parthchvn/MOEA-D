# Directed donors, surviving correct slots, and clean traps

**Status: proved analytically under the pinned process below; finite checks are
separate corroboration.** Filled cardinalities T>=3 protect every proper error
set by a bidirectional adjacent path. They do not eliminate slow states having
no correct slot. We give an exact family and a uniform clean upper bound that
locate the obstruction. No independent-agent review is claimed.

## 1. Exact process and information

Fix n>=3, m=n+1, and 2<=T<=m. The neighborhood of breeder i is the interval

\[
 B_T(i)=[L_i,L_i+T-1],\qquad
 L_i=\max\{0,\min(i-\ell_i,m-T)\},\quad
 \ell_i=\lfloor(T-1)/2\rfloor+
       1\{T\text{ even},\ i\text{ odd}\}.
\]

This is exactly the frozen construction: include i, alternate right/left for
even i and left/right for odd i, skip invalid indices, and fill T recipients.
It is not a clipped-radius process. In particular B_T(0)=[0,T-1] and
B_T(n)=[m-T,n], even when T is odd. Some boundary edges are nonreciprocal even
for odd T.

Supply ideal observed extrema (0,n) and stored labels b_k=k. Use the frozen
max-Chebyshev scalarization, ties accepted. Each ascending cyclic breeder
mutates its own incumbent by independent rate-1/n bit flips. A fresh
Bernoulli(p) gate activates an independent mask of that same rate for the
shared observation. Let D(x,y) be the exact mutation weight kernel. Its
integer formula, checked against literal masks, is implemented in
[structure.py](structure.py).

The unique minimum of the pinned scalarization means an observation k can
replace **only slot k**, and only if k belongs to B_T(i); its true child weight
y is stored there. Thus activated updates can create at most one erroneous
slot, even at full T. At p=0, an accepted proposal only changes w_k to k.
Clean errors disappear and correct weights persist. Labels and reference stay
pinned in both cases. These restrictions are essential: before labels are
pinned, one proposal may replace several recipients.

F_t contains the supplied state and all gates/masks consumed by attempt t;
G_s=F_{ms}. The clean stopping time tau is the first G_s boundary with all
w_k=k, including boundary zero. Phase-state means charge 1/m per attempted
offspring and stop only on aligned phase zero. Aligned interior states remain
live until the boundary. Initialization has zero cost. Multiply sweep means
by m for attempts; these are not archive times, historical coverage, or counts
including initialization. Every conditional argument below is before a fresh
draw, never conditioned on acceptance. We use direct conditional hazards and
finite-state equations, not an unstated drift or tail theorem.

## 2. The donor graph and a surviving-correct-slot lemma

Orient an edge i->k when k is in B_T(i). Ignore self loops for connectivity.

**Proved graph classification.** At T=2 and odd n the strongly connected
components are the closed pairs {0,1},{2,3},...,{n-1,n}. At even n they are
{0,1},...,{n-2,n-1} and {n}; the only intercomponent edge is n->n-1.
The orphan n has no external donor. The source components are all pairs for
odd n, and the orphan plus all but the last pair for even n. This follows
directly from the parity rule. At every T>=3, every adjacent pair communicates
in both directions. Therefore the whole donor graph is strongly connected.
This statement does not assert that every edge is reciprocal.

**Proved clean repair lemma.** For T>=3, from a boundary state with at least
one correct slot and m_e erroneous slots,

\[
                     E_w\tau\le 3n m_e.                 \tag{1}
\]

From any breeder phase the corresponding delay is at most 3n m_e+1 sweeps.
The bound is uniform in T, in the locations and values of the errors, and in
the history preceding this clean interval.

**Proof.** Unless aligned, the adjacent path has an edge i->k from a correct
slot i to a wrong slot k. Choose one such edge at a boundary and wait in whole
sweeps until k is correct. Correct i remains correct. On its scheduled own
turn, a mutation flipping exactly one appropriate bit gives k with probability

\[
 D(i,k)\ge {1\over n}(1-1/n)^{n-1}>{1\over3n}.
\]

Other updates can already have repaired k, which also completes this stage;
they cannot spoil the correct donor or the target. Conditional survival after
s failed stages is at most (1-1/(3n))^s by induction on the fresh draws. Summing
this explicit survival bound gives conditional mean at most 3n sweeps.
Restart with a newly chosen frontier edge at the next boundary. Each stage
removes at least one error, so summing at most m_e conditional means proves
(1). No maximum of marginal means or independence between repairs is used.
At an interior phase, finish the partial sweep (cost at most one), then apply
(1); clean updates cannot increase m_e. QED.

**Interpretation, proved within this clean model.** T>=3 moves the obstruction
from a small donor-isolated component to loss of *every* correct slot. A single
remaining correct slot is enough for (1). For T=2, each source component
needs a correct seed for this adjacent-frontier argument: the orphan is a
one-slot obstruction and a closed pair a two-slot obstruction. The earlier
round-10 and round-12/15 exponential residence examples therefore remain
valid at T=2. The lemma does not deny them or extend their autonomous-pair
calculations to overlapping neighborhoods.

## 3. Exact all-wrong family for every T, and its entrance

Put b=m-T and a=ceil(b/2). For each breeder choose the endpoint farthest from
its neighborhood:

\[
 w_i^*=\begin{cases}n,& n-(L_i+T-1)\ge L_i,\\0,&\text{otherwise.}\end{cases}
\]

For T<m this is always different from i, since the chosen endpoint lies
outside B_T(i). For T=m both distances are zero; use n at i<n and 0 at i=n.
All slots are wrong. Let

\[
 r_i=\sum_{k\in B_T(i)}D(w_i^*,k),\qquad
 q=1-\prod_{i=0}^n(1-r_i).                              \tag{2}
\]

**Proved exact holding law.** Before the first clean repair no weight changes.
The independent scheduled proposals therefore give a geometric(q) first
repair boundary in sweeps, with mean 1/q. Once a clean repair occurs, it
persists, so a sweep cannot return to w*. This is a first-change mean, **not**
the total alignment mean (except in special cases not asserted here).

For T<m, the distance of w_i* to its nearest recipient is
max(L_i,n-(L_i+T-1))>=a, since the two distances sum to b. A proposal from an
endpoint must flip at least a bits to enter its neighborhood. If X is
Bin(n,1/n),

\[
 r_i\le\Pr(X\ge a)\le E\binom Xa
       =\binom na n^{-a}\le1/a!.
\]

The union bound q<=sum r_i yields the all-n lower bound

\[
                  E_{w^*}\tau\ge1/q\ge {a!\over m}.    \tag{3}
\]

For a=0 the same inequality is trivially valid; at full T, q=1 and a correct
slot appears on the first attempt. At logarithmic or square-root T, a~n/2,
so (3) is exp(Theta(n log n)) rather than polynomial. It concerns a worst
supplied clean state, not the usual supplied corner or ordinary initialization.

**Proved accessibility for 0<p<1, with the cost retained.** Start at the
usual corner C=(2,1,2,...,n). In one sweep, at breeder i activate noise,
generate true child w_i*, and observe i. Because i belongs to its own
neighborhood, only slot i is changed. Previous overwrites remain in place and
future parents retain C_i. The exact prescribed path probability is

\[
 p^m\prod_{i=0}^n D(C_i,w_i^*)D(w_i^*,i)>0.              \tag{4}
\]

Slot zero stays wrong throughout, so the path does not cross a killed aligned
boundary. [traps.csv](traps.csv) retains the mask product and gate exponent
separately. This is a positive-mass path, not a typical entrance frequency.
Equation (3) is a **clean** residence lower bound, and cannot be multiplied
silently into a real-p runtime: later noise can also change/repair the trap.
No lower bound on the noisy corner expectation or signed coefficient follows.

## 4. A matching-scale upper bound, with an even-T parity penalty

Define the most central donor's maximum distance to its neighborhood by

\[
 a_* =\min_i\max\{L_i,n-(L_i+T-1)\}
     =\left\lceil{b\over2}\right\rceil
        +1\{T\text{ even},\ n\equiv3\pmod4,\ b>0\}.    \tag{5}
\]

**Proved formula.** For odd T the possible interval starts include every
integer 0,...,b. For T=2r the interior starts have parity r-1, with 0 and b
also supplied by clipping. A centered start is missed only when b is positive
and even and b/2 has the other parity; this is exactly n=3 mod 4. The nearest
available start then differs by one. This explicitly separates even T and
filled boundary effects. For example n=7,T=4 has starts 0,0,1,1,3,3,4,4 and
a*=3, whereas the ideal centered interval would give a=2.

**Proved uniform clean bound.** For every 3<=T<=m,

\[
       \sup_w E_w\tau\le 4\,2^{a_*}a_*!+3n^2.          \tag{6}
\]

To prove it, choose a donor with a most central interval [L,R]; both L and
n-R are at most a*, and a*<=floor(n/2) for T>=3. If its parent x lies in
[L,R], no mutation already produces a recipient, with probability at least
(1-1/n)^n>=1/4. If x<L, set d=L-x<=a*. Exactly d zero-to-one flips and no
other flips give L with probability

\[
 \binom{n-x}{d}n^{-d}(1-1/n)^{n-d}
 \ge {1\over4}\,{2^{-d}\over d!}
 \ge {1\over4\,2^{a_*}a_*!}.                            \tag{7}
\]

Every numerator factor in the binomial product is at least n-L+1>=n/2.
For x>R the same argument flips ones, using R+1>=n/2. The elementary bound
(1-1/n)^n>=1/4 holds for n>=2; its logarithm is increasing in real n>1
because log(1+u)<u. No distribution conditioned on acceptance is used.

If no slot is correct, any clean proposal reaching a recipient creates the
first correct slot. At every scheduled visit of the central breeder the
conditional probability is at least (7); earlier repairs only help. Therefore
the first seeded boundary costs at most \(4\,2^{a_*}a_*!\) sweeps. At that boundary
at most n errors remain, and (1) adds at most 3n^2. If initially seeded, (1)
alone applies. This proves (6).

**Proved asymptotic consequences for clean worst-case initialization.** Bounds
(3),(6), with a* in {a,a+1}, give a polynomial worst-case sweep bound whenever
b log(b+1)=O(log n). If b log(b+1)=omega(log n), (3) instead gives
n^{omega(1)} worst-case means. The assertions use the elementary factorial
growth log(a!)=a log a-O(a), not a finite-grid fit. In particular, for all
requested sublinear T>=3 (fixed 3/4/5/7, ceil(ln n), ceil(sqrt n)), the clean
worst-case mean is exp(Theta(n log n)); full T has the polynomial bound
1+3n^2, since its first proposal always creates a correct slot. These are
deliberately worst-state results. They coexist with O(n) clean sweeps from
the single-error corner at every T>=2.

## 5. Uniform finite-order reduction beyond isolated T=2 words

**Proved corollary, no uniform remainder claim.** Write the supplied-corner
boundary expectation at finite n as

\[
 E_C\tau(p)=\sum_{j\ge0}h_j(C)p^j
\]

in its finite-n neighborhood of zero. For 3<=T<=m, 1<=j<=n-1, put
L_j=3n(j+1)+1 and use the clean corner q_T from (2) with the corner weights
in place of w*. Then

\[
 |h_j(C)|\le {2^j m^j L_j^j\over q_T},\qquad
 q_T\ge D(1,0)>1/(3n).                                  \tag{8}
\]

For each fixed j this is O_j(n^{2j+1}), uniformly over every T>=3, including
growing T. h_j is the Taylor coefficient, not the derivative (which is j! h_j).

**Derivation.** On population/next-breeder phase, kill only at aligned phase
zero. Let K be the clean substochastic one-attempt kernel, J the activated
kernel, Delta=J-K, G=(I-K)^(-1), and r=1/m the reward on live states. All
clean states have positive own-target mutation probabilities, so finite-n
G exists, even for the slow all-wrong states. The actual attempt kernel is
K+p Delta, hence h_0=Gr and h_j=G Delta h_{j-1}. The signed row norm of Delta
is at most two; both positive activated and negative clean branches are kept.

A clean transition cannot add errors. Each support transition of Delta adds
at most one, including reinfection of a correct slot. Starting with one
corner error, after at most j insertions there are at most j+1<=n errors and
therefore always at least one correct slot in each intervening clean state.
The bound (1), including the phase allowance, bounds every later occupation
mass by mL_j and the final h_0 by L_j. The initial corner occupation mass is
exactly m/q_T. Multiplying these bounds in the ordered expression
G Delta ... G Delta h_0 gives (8). There are j signed insertions, j-1 later
occupation factors, and the final reward function. The argument does not
replace a genuine insertion by an unweighted residence factor.

At j>=n this error-count protection can fail. Nor does any finite list of
polynomial coefficients control the whole remainder at p=c/n. Consequently
(8) establishes neither fixed-positive-c ordering nor a growing-T noisy
runtime bound. The full fourth-order T=2 gap remains outside this corollary;
the earlier positive-residence counterexamples are preserved.

## 6. What the published donor/forest bound gives for growing T

**Proved algebraic consequence of the published round-5 bound**, whose forest
construction is used as a dependency rather than claimed as a new independent
audit. Let I_k={i:k in B_T(i)}, d_k=|I_k|,

\[
 a_p={p\over1-2p},\quad \beta=(T-1)a_p,\quad
 A=mTa_p,\quad A_+=(mT-d_0)a_p,
\]
\[
 q_*=(1-p)^{d_0-1}D(1,0),\quad
 B_0=[(1-d_1a_p)q_*]^{-1},\quad
 C=(1-\beta)^{-1}\exp\!\left({A\over(1-\beta)(1-p)}\right).
\]

For beta<1 and d_1 a_p<1 it gives E_C tau <= B_0(1+C A_+).
At p=c/n, fixed c>0, T=o(n), using d_k<=2T-1 gives

\[
 mE_C\tau=O_c\!\left(n^2[1+T\exp\{cT+O_c(T^2/n+T/n)\}]\right). \tag{9}
\]

Thus T=ceil(ln n) gives O_c(n^{2+c} log n) attempts and
T=ceil(sqrt n) gives O_c(n^{5/2} exp(c sqrt n)) attempts. Fixed T gives
O_{c,T}(n^2). For full T=m and fixed 0<c<1, the conditions hold eventually,
and the bound is O_c(n^3 exp(cn/(1-c))) attempts. For c>=1 the displayed
full-T sufficient conditions fail; this is not evidence of divergence.

**Location of the exponential cost.** The family-work bound first gives
H/(1-beta). The exponential appears when requiring *every artificial family*,
including untagged obsolete ones, to be absent at the same boundary:

\[
 q_\infty=\prod_{i,r}(1-u_{i,r})
 \ge\exp[-A/((1-\beta)(1-p))].
\]

The renewal comparison then divides by q_infinity. It discards the actual
population's surviving-correct-slot protection: artificial particles cannot
be killed by external clean repairs. Equations (1),(8) do not by themselves
remove this noisy synchronization cost, because correct slots can be
reinfected. An explicit n=6,T=5 path in the tests becomes aligned at breeder
1 and returns to the supplied corner when breeder 2 observes zero with true
child weight two. Stopping at that interior alignment would be wrong.

The old lower-bound construction's two-hop set J=union_{k in I_0} I_k also
has the sharper geometric bound |J|<=min(m,2T-1), since every donor edge spans
at most T-1 indices. This improves its crude O(T^2) count but still does not
match (9) for growing T.

## 7. Finite scope, provenance, and strongest falsifiers

**Mechanically checked:** exact finite scope is in [verification.json](verification.json)
and [checks.json](checks.json). All T=2,...,n+1 neighborhoods for n=2,...,64
are compared with independent alternating construction. The requested
deduplicated set uses natural log, excludes cardinalities exceeding n+1, and
is tabulated at 17 explicit n values in [geometry.csv](geometry.csv).
No omitted fixed T is silently clipped to a different arm.

The exact clean solver changes only subsets of the initial errors, with a
hard cap of 256 states per closure. It solves triangular sweep equations;
it never constructs a full population transition matrix. Seeded means are
exhaustive only at n=2,3. Larger pair/orphan comparisons have at most four
clean states. Exact first-change trap checks use product probabilities; an
independent direct sweep check is limited to n<=7. The separate coefficient
solver has an explicit 1024 phase-state cap and uses sparse phase recurrences
only at (n,T)=(2,3),(3,3),(3,4). No Monte Carlo, censoring or sampling intervals
are involved. Decimal columns are rounded displays of exact fractions;
forest logarithms alone are illustrative floating evaluations, not certified
intervals.

**Strongest falsifier of the new positive lemma:** a valid T>=3 clean state
with a correct slot whose exact boundary mean exceeds 3n times its error count,
or an accepted clean transition that destroys a correct slot. Neither occurred
in the declared finite scope. A wrong central-distance formula or a violation
of (7) would falsify the new all-state upper bound. A mismatch in exact holding
probabilities would falsify (2). An activated pinned proposal creating two new
errors would invalidate (8). These are separately testable, not assumptions
certified merely by a plot.

**Unresolved in this checkout:** a useful real-p, growing-T corner bound that
replaces the forest's artificial synchronization requirement; entrance-weighted
effects of total loss of correct slots; uniform Taylor remainder; ordinary
initialization. No external theorem is transferred, and no literature search
was performed: novelty and the global open-problem status are UNVERIFIED.
The 240 original blocked holdout observations remain blocked and untouched.
