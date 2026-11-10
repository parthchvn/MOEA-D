# Second-order response of the supplied corner

**Proved finite-dimensional identity; candidate uniform polynomial bound.**
For the process below, write the expansion in **sweeps** as

\[
 m_3(n,p)-m_2(n,p)=pA_n+p^2B_n+R_n(p).
\]

Thus B is half the second derivative. The exact recurrence below computes B
using clean states with at most three errors. The new candidate bound is

\[
 \boxed{|B_n|\le1536n^5\quad(n\ge3).}                    \tag{1}
\]

The complete argument, including the even-n orphan, is given here for later
independent audit. The finite arithmetic checks are distinct from that proof
obligation. No asymptotic equivalent or all-n sign of B is asserted.
An additional, proved but very conservative resolvent bound supplies a genuine
n-dependent sign window. Neither bound establishes ordering at fixed c>0 with
p=c/n. A bound on B alone cannot control the higher-order remainder.

## Process, information and inherited premises

Fix n>=3, T in {2,3}. Supply ideal observed extrema (0,n), labels b_k=k,
and true weights C=(2,1,2,...,n), without initialization cost. Breeders
0,...,n mutate their own current incumbents in ascending order. Mutation flips
each bit independently with probability 1/n. A fresh Bernoulli(p) gate
activates an independent second rate-1/n mask for observation. The filled
cardinality neighborhood starts at its breeder, alternates right/left for an
even breeder and left/right for an odd breeder, skips invalid indices, and
contains exactly T recipients. It is not a symmetric clipped radius.

Unique-minimum scalarization max{k(n-z),(n-k)z} means a proposal of true
weight y observed as z can replace only slot z, if z is a recipient. Extrema
and labels remain pinned; true correctness need not persist under noise.
Let F_t reveal the supplied state and all consumed masks and gates through
attempt t; G_s=F_((n+1)s). The stopping time is the first G_s boundary with
all true weights correct. Correct intermediate populations are retained.
All expectations are unconditional from the supplied state, or conditional on
explicit pre-attempt histories. No drift theorem is used.

The round-7 evidence and its recursive dependencies were replayed before use.
Its established premises are q=1-(1-D(2,0))(1-D(1,0)), common to both T,
m_T(n,0)=1/q, and A_n=-(n/2)log n+O(n). We rederive the needed kernel and
neighborhood facts below. Neither the earlier error-family theorem nor an
unavailable manuscript appendix is a premise. Published ordinary-initialization
measurements do not provide evidence for these Taylor coefficients.

## Exact second coefficient

Let K_i be the clean attempt kernel and J_i the active-mask attempt kernel.
Set Delta_i=J_i-K_i, so the true attempt kernel is K_i+p Delta_i.
With row kernels acting on column values, define

\[
 P_0=\prod_{i=0}^nK_i,\quad
 P_1=\sum_iK_0\cdots K_{i-1}\Delta_iK_{i+1}\cdots K_n,
\]
\[
 P_2=\sum_{i<j}K_0\cdots\Delta_i\cdots\Delta_j\cdots K_n. \tag{2}
\]

There is no factor two in P_2 and no twice-inserted single attempt: each gate
is affine in p. Restrict the full sweep to nonaligned boundary states, giving
Q_j. The clean transient resolvent is R_0=(I-Q_0)^(-1). Every finite-n clean
state has finite mean absorption time because each wrong slot has positive
own-turn repair probability and clean updates cannot create errors.

Let h_0 be the clean boundary mean, h_1 its p coefficient and h_2 its p^2
coefficient, with all three zero on the aligned **boundary** state. Then

\[
 h_0=R_0\mathbf1,\qquad h_1=R_0Q_1h_0,\qquad
 h_2=R_0(Q_1h_1+Q_2h_0).                                \tag{3}
\]

Starting at C, the clean boundary chain visits only C before absorption.
Consequently, for each T,

\[
 b_T=\frac{(P_1h_1)(C)+(P_2h_0)(C)}q,\qquad B_n=b_3-b_2. \tag{4}
\]

The two summands describe signed insertions in different sweeps and within
one sweep. They are algebraic contributions, not probabilities or mutually
exclusive observed causes. In particular the second summand cannot be dropped.

For an error set E={(k,w_k):w_k!=k}, clean steps only delete pairs. If
p_E(F) is its clean sweep distribution, then

\[
 h_r(E)=\frac{\mathbf1_{r=0}+
    \sum_{j=1}^r(P_jh_{r-j})(E)+
    \sum_{F\subsetneq E}p_E(F)h_r(F)}{1-p_E(E)}.          \tag{5}
\]

This recursion includes already-correct mid-sweep prefixes. One activation
can change at most one coordinate. Thus (4) needs h_1 only on states reachable
with one insertion (at most two errors), and h_0 only on states with at most
three errors. No positive-noise trajectory truncation is made.

[second.py](second.py) implements this recurrence with rational or float64
arithmetic. [oracle.py](oracle.py) separately enumerates literal masks, scalar
comparisons and **every** population at n=3,4. It solves both clean Poisson
equations over the full state space and agrees exactly, including both terms
in (4). The oracle does not import the error-set solver.

## Candidate polynomial bound: regular states

Put m=n+1 and L=6n. A *regular state* below means a clean subset of C with
at most one overwritten coordinate of arbitrary true weight. For T=2 at even
n, initially exclude an error at the orphan n. For T=3 there is no exclusion.
Every clean descendant of a regular state is again regular.

**Local lemma, proved here:** every such state has clean boundary mean <=L,
uniformly in the arbitrary wrong weight. Adjacent correct donors have a
single-flip repair probability at least 1/(3n), since
alpha=(1-1/n)^(n-1)>=1/3. For T=2 at odd n every site belongs to a pair.
For T=3 every site has an adjacent donor. The extra wrong site can therefore
be repaired in <=3n expected sweeps, then slot 0 in <=3n. The sole blocked
pair is {0,1}: if slot 1 is wrong, donor 0 has weight 2 until its repair,
then weight 0; D(2,1)>=2/(3n) and D(0,1)>=1/3. Repair slot 1 first, then 0.
For even-n T=2, target n-1 still has its correct partner n-2 even if the
orphan is wrong; omitting all broadcasts from breeder n preserves these
bounds. From any phase, at most one additional boundary is needed.

If a further active observation overwrites k by y!=k, clean completion is
bounded by 1/D(y,k)+L: wait for k's own repair, then the remaining errors are
a regular subset. This argument also bounds any clean suffix value. Before
selection, the expected added inverse repair probability is at most

\[
 \sum_{k\in B(i)}\sum_{y\ne k}D(w_i,y)D(y,k)/D(y,k)\le T. \tag{6}
\]

Hence an active suffix expectation is in [0,L+T], a clean one in [0,L],
and their difference has absolute value <=L+T. In particular

\[
 |h_1(E)|\le K_T:=Lm(L+T)                                \tag{7}
\]

for regular E, by summing insertions over its <=L expected clean sweeps.
Each Delta_i has infinity norm <=2. The first term of (4) is therefore
bounded by 2mK_T. For two insertions in a single sweep, the first signed
insertion has total variation <=2 and leaves regular states; the second has
value bounded by L+T as above. Thus

\[
 |b_T|\le R_T/q,\quad
 R_T=2(L+T)\{m^2L+\tbinom m2\}.                         \tag{8}
\]

This already applies to T=3 for every n, and T=2 for odd n. A blanket claim
that every single-error state is regular at even-n T=2 is false: a wrong
orphan y repairs only on its own turn, with mean 1/D(y,n), possibly n^n.

## Candidate polynomial bound: the even-n orphan

Split each Delta by accepted recipient into an orphan part O and a remaining
part R. Only breeder n contributes O. Each restricted part is the difference
of two stochastic kernels that update only its selected recipients, and has
norm <=2. This is an algebraic split; it does not assume independence of all
coordinates under full noise. Write h_1^O,h_1^R for the corresponding linear
responses, and split b_2 into RR, RO+OR, and OO terms.

The RR bound is R_2/q. For a regular state with a correct orphan, (6) with
only recipient n gives |h_1^O|<=J:=L(L+1): the clean duration is <=L and each
orphan insertion has absolute suffix value <=L+1.

For the other mixed order, start with only the possible original corner and
an orphan of arbitrary wrong weight y. Put d=D(y,n). Before the orphan's
clean repair it remains y. A nonorphan insertion leaves a regular collection
of other errors. Its clean completion, even after omitting breeder n's help,
has expected duration <=L+1 from any phase and <=L from a boundary.

Here is the required predictable-count argument. Couple the baseline and
modified clean continuations using the same future orphan proposals. They
share the orphan repair boundary. For either continuation, count orphan
turns at which the remaining errors have not yet disappeared. Conditional
on each pre-turn history its repair probability is exactly d. Expected count
is at most L+1, so the chance that the orphan repairs before those errors
disappear is at most d(L+1). At that stopping boundary their conditional
remaining mean is <=L. Therefore each completion mean exceeds the common
orphan mean by a number in [0,dL(L+1)]. Their difference has absolute value
at most dJ. This uses fresh randomness after stopping, not conditioning on a
future error lifetime. Correlation through breeder n's proposals is allowed.

The sum of the absolute signed acceptance masses of a recipient-restricted
insertion is at most 2T. While the orphan is wrong, the resulting total
remaining-recipient forcing is bounded by 2mT dJ per sweep. Its expected
clean lifetime is 1/d. After its repair the usual regular bound applies.
At T=2 this proves, uniformly in y,

\[
 |h_1^R|\le K':=4mJ+K_2.                               \tag{9}
\]

The two different-sweep mixed terms are bounded by 2mJ+2K'. Within one
sweep the orphan insertion can only come last, so the mixed term is at most
2m(L+1). Consequently

\[
 |b_{RO}+b_{OR}|\le M_{RO}/q,\quad
 M_{RO}=m(12L^2+16L+2).                                \tag{10}
\]

**Pure OO cancellation.** Only for this term, the orphan evolves autonomously
and the untouched corner has an independent geometric(q) repair boundary.
Let R(p) be the orphan own-turn kernel and
nu_p(y)=(1-p)1_(y=n)+pD(n,y). Detailed balance follows from
binom(n,x)D(x,y)=binom(n,y)D(y,x): nu_p is its invariant distribution.
Let s=1-q. The simultaneous mean in this restricted process is exactly

\[
 m_O(p)=\frac{[(I-sR(p))^{-1}]_{nn}}{\nu_p(n)}.           \tag{11}
\]

To verify (11), let h_p be the local first-hitting mean, zero at n. Stationarity
and its first-step equations give (I-R)h_p=1-1_n/nu_p(n). Apply the discounted
resolvent and use h_p(n)=0. Waiting for the independent endpoint clock and
then applying the strong Markov property gives (11). This identity keeps
orphan reinfections before the endpoint repairs; replacing it by a maximum
of first hitting times would be wrong under noise.

For y<n put d_y=D(y,n), c_y=D(n,y)d_y, f_y=q+s d_y, b=1-D(n,n), a=sum c_y.
Let W be the p coefficient of the transient local matrix: for z!=y,
W_yz=D(y,z)D(z,n), and W_yy=b d_y-sum_(z!=y,n) W_yz. Define

\[
 C_0=\sum_y c_yd_y/f_y,\qquad
 C_1=\sum_{y,z}c_yW_{yz}d_z/(f_yf_z),\qquad
 g=\sum_yD(n,y)/f_y.
\]

A Schur complement of (11) gives its p coefficient g and its p^2 coefficient

\[
 b_{OO}=qg^2-\frac{-bsa+2bs^2C_0-s^3C_1}{q^2}.         \tag{12}
\]

Since g<=1/q, a,b<=1, C_0<=a/s, sum c_y/f_y<=1/s,
d_y/f_y<=1/s and ||W||_infinity<=2, (12) implies
|b_OO|<=1/q+5/q^2<=6/q^2. The discount q removes the dangerous inverse
orphan probabilities. [bounds.py](bounds.py) implements (12), independently
checked against the restricted insertion recurrence.

Combining (8), (10), and (12) gives the parity-aware bounds

\[
 |B_n|\le\begin{cases}
 (R_2+R_3)/q,&n\text{ odd},\\
 (R_2+R_3+M_{RO})/q+6/q^2,&n\text{ even}.
 \end{cases}                                           \tag{13}
\]

Use q>=1/(3n), L=6n and m=n+1. Even the larger expression is at most
432n^5+2376n^4+2427n^3+543n^2+6n <=1536n^5 for n>=3. This proves (1)
conditional on the new mixed-insertion argument surviving independent audit.
It is a deliberately loose upper bound, not an asserted growth law.

## Proved conservative remainder and sign window

This separate bound does not rely on the candidate polynomial proof. Put
M=m n^n. From any clean state each coordinate repairs no later than its own
geometric(D(y,k)) repair clock. Summing their means, without inferring a
maximum from a mean alone, gives ||R_0||_infinity=max h_0<=M because
D(y,k)>=n^(-n). For complex |p|=r,

\[
 ||Q(p)-Q_0||_\infty\le d(r):=(1+2r)^m-1.
\]

The Neumann series converges when Md(r)<1. Its coefficientwise positive
majorant, specialized to the corner row R_0(C,.)=q^(-1)1_C, gives

\[
 |R_n(p)|\le\frac2q\left\{
 \frac{Md(p)}{1-Md(p)}-2mMp-
 [4\tbinom m2M+4m^2M^2]p^2\right\},                    \tag{14}
\]

for nonnegative p in that disk. The factor 2 accounts for the two cardinalities.
The same expression without its final subtraction bounds the remainder after
the linear term. This also supplies the independent conservative coefficient
bound |B_n|<=8[binom(m,2)M+m^2M^2]/q.

For p<=1/(8mM), set x=2mp<=1/(4M). The elementary bounds
d<=x/(1-x), d-x<=x^2/(1-x), and Md<=1/3 imply

\[
 |m_3-m_2-pA_n|\le32m^2M^2p^2/q.
\]

Hence, whenever the exact A_n is negative,

\[
 0<p\le\min\{1/(8mM), |A_n|q/(64m^2M^2)\}
 \quad\Longrightarrow\quad m_3-m_2\le pA_n/2<0.        \tag{15}
\]

This is a real finite-noise statement, not a Taylor truncation. For all
sufficiently large n, the audited first-order asymptotic implies negativity
through at least p=log(n)/[768(n+1)^4 n^(2n)]. The eventual threshold in n
is not made explicit here. This window shrinks vastly faster than 1/n and
does not establish any fixed-positive-c ordering. The candidate polynomial
bound makes the quadratic term negligible for p=o(log(n)/n^4); equation (14)
does not control the remaining terms on that larger scale.

## Limits and falsifiers

**Mechanically checked** results, exact coefficient signs, decomposition and
finite bounds are recorded in [verification.json](verification.json) and the
CSV files linked from [README.md](README.md). Deterministic float64 rows are
not certified enclosures, experimental observations or asymptotic evidence.

**Candidate-proof review obligations:** verify the regular-state uniform
repair bound with the orphan's broadcasts removed, the predictable-count
mixed bound (9), and the decomposition of both sweep orders in (10).
An exact suffix discrepancy, a violated stated inequality, or disagreement
with the literal-mask oracle would falsify the associated step. A rigorous
|B_n|>1536n^5 would refute (1). The next substantive gap is a useful uniform
third-and-higher-order remainder; two nearby corrupted donors after two
insertions prevent simply reusing the regular-state lemma at every order.

No claim about ordinary initialization, the pre-S empirical mechanism,
growing cardinality, or global literature novelty is made. The offline source
comparison with Doerr, Elmoutassim, Krejca and Kibulu (2026), arXiv:2610.35373,
DOI 10.48550/arXiv.2610.35373, remains a scope boundary: its noiseless
radius/archive theorem is not a premise of this noisy boundary calculation.
