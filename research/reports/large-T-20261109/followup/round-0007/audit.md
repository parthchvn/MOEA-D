# Independent audit of the small-noise asymptotic

**Proved for the stated supplied-corner process, after this audit:** the round-6
candidate survives. If time is measured in sweeps, then

\[
 A_n=\left.\frac{\partial}{\partial p}
       \{E\tau_3-E\tau_2\}\right|_{p=0}
     =-\frac n2\log n+O(n).
\]

The constants below are absolute and apply for every integer n≥8. The finite
set n=3,…,7 does not affect the asymptotic statement. This conclusion rests on
the analytic bounds below; the finite exact checks in [verification.json](verification.json)
are separate implementation checks. It establishes eventual negativity of the
derivative, without claiming negativity at every n≥4 or ordering at p=c/n for
fixed positive c. No remaining logical gap in this asymptotic argument was
identified. A uniform Taylor remainder remains an additional obligation.

**Process, filtration and boundary event.** Supply ideal extrema (0,n), pinned
stored labels b_k=k and true weights (2,1,2,…,n), without initialization cost.
Ascending breeders 0,…,n mutate their own incumbents with independent per-bit
rate 1/n. An independent Bernoulli(p) gate activates a second independent
rate-1/n mask for the observation. The filled-cardinality recipient set starts
at its breeder, alternates right/left for even breeders and left/right for odd
breeders, skips invalid indices and stops at T recipients. Only T=2,3 is used.
Pinned scalarization is max{k(n−z),(n−k)z}. Its unique minimum is z=k, so an
accepted proposal changes at most the coordinate indexed by its observed
weight. The labels stay pinned; true correctness need not persist with noise.

F_t reveals exactly the initial state and consumed masks/gates through attempt
t. G_s=F_(n+1)s. The stopping time τ_T is the first G_s boundary with all true
weights equal to their indices. It is not a first visit to an aligned
intermediate state, an archive time or a time from ordinary initialization.
All conditional bounds below condition on a pre-attempt history, or a stopping
time followed by fresh masks. No drift theorem or acceptance-conditioned noise
bound is used.

**Dependency audit.** The complete round-6 reproduction, including the earlier
published plans, receipts and exact certificates, reproduces all six round-6
outputs byte for byte. Its recursion also reproduces rounds 3–5. The separate
n=512 registration exists in ancestor commit a5449de before measurement; usable
receipts and the recorded seed separation are present. No dependency repair is
needed. The original preregistration, capped main observation, 240 missing
holdout observations and inconclusive two-stage decision are preserved.
[dependency.json](dependency.json) records the receipts and limitations. Private
per-trial logs remain unavailable, so published evidence cannot establish the
absence of unreported invocations. No new scientific sampling is performed.

**Finite-n response formula, rechecked analytically.** Let D(x,y) be the
standard-bit weight kernel. Equivalently, n^n D(x,y) is the coefficient of z^y
in (1+(n−1)z)^x ((n−1)+z)^(n−x). At p=0 correct slots cannot become wrong.
For each finite n every wrong slot has positive own-turn repair probability,
and a full sweep can repair all slots with positive probability uniformly
over the finite state space. The killed boundary matrix Q(0) has spectral
radius below one. Its resolvent is analytic near p=0, giving
h'(0)=(I−Q(0))^−1 Q'(0)h(0).

Write a_j=D(j,0) and q=a_1+a_2−a_1a_2. Both cardinalities have endpoint donors
{0,1}. Before absorption the clean boundary process from the corner can visit
only that corner, so its derivative is q^−1 times the expected derivative
insertion in a single sweep. An insertion is one active-mask transition minus
one clean transition; aligned intermediate prefixes must be retained. Only
one additional coordinate can become wrong. In the following clean suffix,
errors disappear but never change their wrong weights. This justifies the
round-6 two-error recurrence without using its earlier error-family theorem.

Let γ_(T,k) be the insertion contribution at recipient k, so m'_T(0)=Σ_k γ_(T,k).
Let V_(T,i)(E) be expected clean boundary value after the suffix beginning at
breeder i from error set E. Immediately before breeder i the corner error is
present with probability 1, 1−a_2 or 1−q according as i=0, i=1 or i≥2.
These are unconditional clean-prefix probabilities, not posterior laws of
accepted observations. Inserting observed k with true y changes V by
V(E[k←y])−V(E), with proposal mass D(w_i,y)D(y,k). One must also subtract the
clean accepted mass D(w_i,k); equivalently its y=k correction is
D(w_i,k)(D(k,k)−1). For k≥1 that correction has zero value because k was correct.
The direct endpoint terms γ_(3,0)=γ_(2,0) cancel exactly.

For I_k={i:k∈B_T(i)} disjoint from {0,1}, define

\[
 G_k=\prod_{j\in I_k\setminus\{k\}}(1-D(j,k)),\quad
 r_y=1-G_k(1-D(y,k)),\quad
 b_i(y)=\prod_{j\in I_k:j>i}(1-D(w_j,k)),
\]

where w_k=y and the other w_j=j. The exact contribution is

\[
 \gamma_{T,k}=\sum_{i\in I_k}\sum_{y\ne k}
 \frac{D(i,y)D(y,k)b_i(y)}{r_y[q+(1-q)r_y]}.                 \tag{A}
\]

The endpoint and the additional error use disjoint breeders and neither
changes the other's donor weights. Fresh masks give independent geometric
repair times at future full boundaries. For G_q,G_r supported on {1,2,…},
E max(G_q,G_r)−E G_q=1/r−1/(q+r−qr). Averaging the already-correct endpoint
prefix of probability q and the incorrect prefix of probability 1−q, then
multiplying by suffix survival b_i and q^−1, yields (A). The formulas do not
assert independence of noisy coordinates. All k≥3, and k=2 for T=2, qualify.

Since r_y≥D(y,k) and q+(1−q)r_y≥max(q,r_y), (A) immediately gives
0≤γ_(T,k)≤|I_k|/q. If an external clean donor has probability at least c, the
stronger bound is γ_(T,k)≤|I_k|/c. Always |I_k|≤4 here.

**Uniform preliminaries.** Put s=e^−1 and α=(1−1/n)^(n−1). The logarithmic
series gives
log(α)+1=Σ_(m≥1) 1/[m(m+1)n^m]∈[0,1/(2(n−1))] and
−log((1−1/n)^n)−1∈[0,1/(2(n−1))]. Consequently s≤α≤1,
|α−s|≤1/n and |(1−1/n)^n−s|≤1/n. In particular α≥1/3.
Since a_1=α/n and a_2=α/[n(n−1)],

\[
 \frac1{3n}\le q\le\frac2n,\qquad
 q=\frac1{en}+O(n^{-2}).                                 \tag{B}
\]

These are deterministic kernel bounds, not a fitted approximation.

**Exceptional recipient 0: |γ_(T,0)|≤36n.** Before either eligible insertion,
the breeder has weight 2 or 1. For y≥1, D(y,0)≤1/n; also D(1,0),D(2,0)≤1/n.
Thus the active erroneous-acceptance mass is at most 1/n, and the absolute
suppressed clean-acceptance mass at most 1/n, per eligible breeder. Every
resulting clean state has only a possible error at 0 and correct donor 1.
Its clean boundary mean, and every suffix value, is at most 1/a_1≤3n, uniformly
in that error's wrong weight. Two donors, the difference of values in [0,3n]
and 1/q≤3n yield the stated bound. Cancellation of this common contribution
is exact but is not needed to bound the individual derivatives.

**Exceptional recipient 1: |γ_(T,1)|≤225n.** At n≥8 its insertion donors are
{0,1} or {0,1,2}. Every relevant parent weight is 1 or 2: at breeder 0 the
clean prefix is still the supplied corner. This qualification matters. The
claim that every erroneous observation of 1 has mass O(1/n) would be false
for a parent of weight 0, since true child 0 can be observed as 1 with
probability bounded away from zero. Such a parent is absent from these
insertion histories.

For a parent of weight x∈{1,2}, a true child Y≠1 observed as 1 requires a
one-to-zero flip in at least one mask. For x=1, weights would otherwise be
nondecreasing and the wrong-child condition excludes Y=1. For x=2, observing
1 itself requires a decrease. A union bound, before selection, gives

\[
 \sum_{y\ne1}D(x,y)D(y,1)
 \le x/n+E[Y]/n\le(2x+1)/n\le5/n.                       \tag{C}
\]

If errors are confined to slots 0 and 1, with w_0=2 or 0 and arbitrary wrong
w_1, donor 0 repairs slot 1 with probability at least 2/(3n) on each sweep:
D(2,1)≥2α/n and D(0,1)=α. Hence slot 1's first correct boundary has mean at
most 3n/2. After it repairs, it remains correct and repairs endpoint 0 within
at most another 3n expected sweeps. All such clean boundary means and suffix
values are at most 5n, including arbitrary w_1. Formula (C), at most three
donors and 1/q≤3n imply 225n. No independence of the two repair times is used.

**Exceptional recipient 2 for T=3: 0≤γ_(3,2)≤420.** This site is not covered
by (A). Couple an inserted-error clean process to its baseline with the same
endpoint-donor masks. Recipient 2 cannot affect either endpoint donor's weight;
clean updates into other already-correct slots have no effect. Thus the
endpoint repair occurs at exactly the same attempt in both coupled processes,
and an additional slot-2 error cannot shorten completion.

Correct donor 1 repairs slot 2 with probability
D(1,2)≥((n−1)/n)α≥1/6 per visit, uniformly over all past information and wrong
values at 2. From any phase the expected number of sweep boundaries until
this error disappears is at most L=1+6=7. The expected number of endpoint-donor
attempts while it is wrong is at most 2L=14.

If endpoint 0 is still wrong, its true weight is 2; the only eligible breeders
are 0 and 1 with weights 2 and 1. At either attempt, conditional on the
pre-attempt past, its repair probability is at most q. Count those attempts
with the predictable indicator that both errors remain. Truncation, conditional
expectation and then monotone convergence give probability at most 14q of
repairing the endpoint before the slot-2 error disappears. At that stopping
time the latter's conditional remaining boundary time is still at most L,
because its next donor-1 masks are fresh. Consequently the expected excess
boundary value is at most 14qL=98q when the endpoint was initially wrong.
This does not condition on a future error lifetime.

An already-correct endpoint prefix has probability at most q and conditional
excess value at most 7. For each of the at most four insertion donors, bound
the total proposal mass by one; averaging prefixes bounds its insertion value
by 98q+7q. Division by q proves 420. This supplies an explicit version of the
candidate's O(1) assertion despite the shared breeder and cyclic timing.

**Other exceptional sites and the T=3 interior.** For even n, T=2 has
I_n={n} and I_(n−1)={n−2,n−1,n}; the last target is an orphan, not an ordinary
pair. Exclude n−1,n in this parity, and n alone when n is odd. The generic
bound after (A) is at most 12n per excluded site. One can exclude n−2 as well
without changing the argument. The right endpoint for T=3 is also bounded
by 12n. Every remaining T=3 interior site k≥3 has both neighboring donors;
one single-flip probability is at least α/2≥1/6. Hence γ_(3,k)≤24. Together
with the explicit left exceptions, this proves γ_3(n)=O(n), including its
absolute value. Boundary filling and even-n nonreciprocity are accounted for.

**Uniform edge estimates for T=2.** Outside the exceptions, each target k has
one external donor j in a disjoint two-site pair. Put a=D(j,k), d_y=D(y,k),
r_y=a+(1−a)d_y. Expanding (A), with the ascending suffix order retained, gives

\[
 \gamma_{2,k}=\begin{cases}
 \displaystyle\sum_{y\ne k}\frac{d_y[D(j,y)+(1-a)D(k,y)]}
 {r_y[q+(1-q)r_y]},&j=k+1,\\[2mm]
 \displaystyle\sum_{y\ne k}\frac{d_y[(1-d_y)D(j,y)+D(k,y)]}
 {r_y[q+(1-q)r_y]},&j=k-1.
 \end{cases}                                             \tag{D}
\]

The singular left sites are even 2≤k≤n/4, with u=k+1, j=k+1. Singular right
sites are odd 3n/4≤k≤n−1, excluding the even-n exception, with u=n−k+1,
j=k−1. In either range 3≤u≤n/4+1 and t=u/n≤3/8. All other ordinary sites
have a≥1/12 by a single-flip event and thus γ_(2,k)≤2/a≤24.

Consider the left side first. A net loss of one from u has distinguished mass
αu/n. Every other such outcome needs at least two one-bit losses, so

\[
 a=\alpha t+\epsilon,\quad0\le\epsilon\le t^2/2,
 \quad t/3\le a\le t,\quad |a-st|\le t/n+t^2/2.          \tag{E}
\]

The last upper bound a≤t follows from the necessity of at least one loss.
Zero flips or one gain, respectively, give

\[
 |D(u,u)-s|\le t+1/n,\qquad
 |D(u-1,u)-s|\le2t+1/n.                                 \tag{F}
\]

The remaining paths in either case include a one-bit loss, of probability at
most t. These inequalities are uniform across the whole stated edge range.

The y=j summand of (D) is

\[
 L=\frac{N}{(2-a)[q+(1-q)a(2-a)]},\quad
 N=D(j,j)+(1-a)D(k,j).                                   \tag{G}
\]

On the right the numerator instead is N=(1−a)D(j,j)+D(k,j); complementing
weights proves the same (E)–(F) bounds without reversing the cyclic suffix
by assumption. For either numerator, |N−2s|≤5t and N≤2. Set
L_0=N/[a(2−a)^2]. Equations (E)–(F) imply

\[
 |a(2-a)^2-4st|\le4t/n+6t^2\le8t^2,
 \qquad |L_0-1/(2t)|\le15+12=27.
\]

To retain the small-k q correction, write r=a(2−a). As q+(1−q)r≥r,

\[
 0\le L_0-L
 = L_0\frac{q(1-r)}{q+(1-q)r}
 \le\frac{2q}{a^2}\le\frac{36n}{u^2}.
\]

Thus the following explicit version of the candidate estimate holds:

\[
 \boxed{\left|L-\frac{n}{2u}\right|
 \le64\left(1+\frac n{u^2}\right).}                     \tag{H}
\]

It is not legitimate to discard q uniformly for fixed u. The n/u² remainder
in (H) is exactly what permits summation while retaining those fixed sites.

**The remaining errors cost at most 24 per slow site.** On the left, proposals
y≤k−1 from either parent require at least one original-one loss, so their
combined probability mass is at most 2t. Since d_y≤r_y and
q+(1−q)r_y≥r_y≥a, their sum in (D) is at most 2t/a≤6.

For y≥k+2, observing k requires at least two losses in the second mask:
D(y,k)≤y(y−1)/(2n²). For either parent x∈{k,k+1}, Y≤u+Z where Z is the number
of newly flipped zeros, E Z≤1 and E Z²≤2. Hence E Y²≤u²+2u+2≤2u² for u≥3.
The combined accepted mass is at most 2t². The denominator is at least
r_y²≥a²≥t²/9, so the contribution is at most 18. On the right, complement
weights and use the fact that either order-dependent numerator in (D) is
bounded by the sum of the two proposal probabilities. This proves the same
6+18 bound on that side. These are bounds on all possible wrong values,
including far-tail values; no truncation of the mutation kernel is used.

**Summation and conclusion.** Each edge contributes n/(2u) over one parity
class with spacing two, between a fixed lower cutoff and a cutoff proportional
to n. Thus each sum is (n/4)log n+O(n), for either parity of n. Omitting a
bounded number of exceptional sites changes this by at most O(n).
The sum of the errors in (H) is O(n), since there are O(n) sites and
Σ_(u≥3) n/u²=O(n). The residual errors and nonsingular sites are each O(1)
per site, and all exceptions total O(n). Consequently

\[
 \gamma_2(n)=\tfrac12 n\log n+O(n),\qquad
 \gamma_3(n)=O(n),\qquad A_n=\gamma_3(n)-\gamma_2(n).
\]

The attempts coefficient is (n+1)A_n=−(n²/2)log n+O(n²). Under p=c/n,
A_n/n is the derivative with respect to c **at zero for each fixed n**.
Substitution of a fixed c>0 into the expansion requires additional uniform
control of the remainder and is not a consequence of this theorem.

**Checks, limitations and falsifiers.** [audit.py](audit.py) independently
constructs exact kernels by polynomial multiplication and checks literal masks,
closed-interval versus literal neighborhoods, all published exact recipient
coefficients at n=3,…,10, exceptional clean means and phase delays, and both
edge orders. It extends the earlier independent literal-mask full-population
oracle to all 3,125 states at n=4 for each T. Thus both the n=3 positive
coefficient and the n=4 negative coefficient now have full-population checks.
The universal argument above is not inferred from the checked finite grids.

A contrary clean suffix value, a failure of (C), (H) or its tail bounds under
their stated ranges, an unexpected incoming donor in an ordinary pair, or an
exact derivative disagreement would falsify the relevant step. An asymptotic
sequence contradicting A_n/(n log n)→−1/2 would falsify the final theorem.
All-n negativity from n=4, a uniform Taylor remainder, ordinary initialization,
and the pre-S empirical mechanism are unresolved by this audit. No global
literature or novelty claim is made in this offline checkout. The existing
comparison with Doerr, Elmoutassim, Krejca and Kibulu, *Understanding the
Co-evolutionary Solution Exchange of the MOEA/D: Already the Smallest
Communication Radius Gives the Best-Possible Speed-Up* (2026),
arXiv:2610.35373, DOI:10.48550/arXiv.2610.35373, remains a scope boundary;
its noiseless radius/archive statement is not a premise of this proof.
