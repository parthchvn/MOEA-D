# Small-noise response of the supplied corner

**Proved finite-n identity; mechanically checked exact coefficients.** Let
`m_T(n,p)` be expected sweeps to the first simultaneously correct boundary in
the pinned process specified below. For every fixed n≥3,

\[
m_3(n,p)-m_2(n,p)=p A_n+O_n(p^2),\qquad
A_n=\gamma_3(n)-\gamma_2(n).
\]

Equations (3)–(5) below give A_n by finite rational arithmetic, without
sampling, numerical differentiation, or an exponentially large population
matrix. At n=3, A_3=0.22213184717778317… sweeps per unit activation probability.
It is strictly negative for every n=4,…,10, checked exactly. There is no claim
here that these finite signs establish the sign at every n≥4.

**Candidate asymptotic theorem, with a complete argument below but no separate
review in this round:**

\[
\boxed{A_n=-\tfrac12 n\log n+O(n).} \tag{1}
\]

The logarithm is natural. The corresponding coefficient in attempts is
`(n+1)A_n = -(1/2)n² log n + O(n²)`. If the noise parameter is instead c with
p=c/n, the derivative **at c=0 for each n** is A_n/n in sweeps and
`(n+1)A_n/n` in attempts. Neither this chain rule nor (1) bounds the remainder
uniformly in n; substituting a fixed positive c into the first-order expansion
is not justified here.

## Process and information

Fix n≥3, T∈{2,3}. Supply ideal observed extrema (0,n), stored labels b_k=k,
and true weights C=(2,1,2,…,n), at zero initialization cost. Breeders are
0,…,n in ascending order every sweep and mutate their own incumbents. Each bit
flips independently with probability 1/n. A fresh independent Bernoulli(p)
gate activates a second independent rate-1/n mask for the observation.

The filled cardinality neighborhood B_T(i) starts at i and alternates sides,
right first for even i and left first for odd i, skipping out-of-range sites.
It is not a clipped radius. With the pinned scalarization
`C_k(z)=max{k(n-z),(n-k)z}`, an offspring with true weight y and observed weight
z can replace only slot z, and only when z∈B_T(i). Stored labels and extrema
remain pinned. This is the published supplied-corner process, not ordinary
initialization, `sim.py`, or the one-bit mutation model.

Let F_t contain the initial state and consumed masks/gates through attempt t,
and G_s=F_(n+1)s. The stopping time τ_T is the first s≥0 with every true slot
correct at boundary s. In particular, a correct intermediate population is
not killed: a later breeder in the same sweep may corrupt it. Expectations
are unconditional from the supplied state; no accepted-observation or stored
label conditioning is used. No drift theorem is invoked.

The weight kernel is

\[
D(x,y)=n^{-n}\sum_a {x\choose a}{n-x\choose y-x+a}
                    (n-1)^{n-2a-y+x}, \tag{2}
\]

over feasible choices `0≤a≤x`, `0≤y-x+a≤n-x`. The second mask conditional on
true weight y has observation kernel D(y,z), including the possibility of no
change. Genotype arrangements are irrelevant to these conditional weight
laws. Write I_k={i:k∈B_T(i)}. Both T have I_0={0,1}, so, with
`a_j=D(j,0)`, `q=1-(1-a_2)(1-a_1)`, their noiseless mean is 1/q.

## Why a derivative exists, and why only two errors are needed

**Proved.** On the finite population space, one full sweep has a polynomial
transition matrix P_T(p). Kill only at an aligned boundary. At p=0, no correct
slot can become wrong, and each wrong slot has positive own-turn probability
of becoming correct. A full sweep of prescribed own repairs, regardless of
earlier clean repairs, has a positive uniform probability over the finite
state space. Thus the transient matrix Q_T(0) has spectral radius less than
one. Its inverse resolvent, and consequently the hitting expectation, is
analytic in a neighborhood of p=0.

Let h_T be the zero-noise mean from each boundary state, with h_T(aligned)=0.
Differentiating `h(p)=1+Q(p)h(p)` gives
`h'(0)=(I-Q(0))^{-1}Q'(0)h_T`. Starting from C, the zero-noise boundary process
can visit only C and the target, with failure probability 1−q. Consequently

\[
\gamma_T(n)=m'_T(n,0)=q^{-1}(P'_T(0)h_T)(C). \tag{3}
\]

The derivative of a sweep inserts exactly one *active-mask minus clean*
transition among otherwise clean updates. Before that insertion there is
either only the original endpoint error or no error. The insertion can change
only one coordinate. Afterward, with zero noise, errors only disappear and
their true weights remain fixed until repair. Therefore h_T and its suffix
values are needed only on states with at most two incorrect coordinates.
This is a derivative identity, not a claim that an entire positive-noise
trajectory contains at most one activation.

## Exact finite recurrence

Represent a state by its set E of pairs (wrong slot, true weight). Let
`P^0_{T,i:n}(E,F)` be the probability that the clean suffix i,…,n leaves error
set F. At breeder j, its weight is the error value at j, or j if j is correct.
Each erroneous recipient k is repaired with probability D(w_j,k). These events
are mutually exclusive within that attempt; all other outcomes leave E alone.
Repaired breeders use their corrected weights when their turn occurs later.

Compute h_T(∅)=0 and, in increasing error-set size,

\[
h_T(E)=\frac{1+\sum_{F\subsetneq E}P^0_{T,0:n}(E,F)h_T(F)}
                  {1-P^0_{T,0:n}(E,E)},\qquad
V_{T,i}(E)=\sum_F P^0_{T,i:n}(E,F)h_T(F). \tag{4}
\]

Set `V_{T,n+1}=h_T`. The denominator is positive. Only the union of the at
most two error sites' incoming donor sets needs processing.

Immediately before breeder i in a noiseless sweep from C, the endpoint is
wrong with probabilities
`f_0=1`, `f_1=1-a_2`, and `f_i=1-q` for i≥2. Let E be `{(0,2)}` with
probability f_i, or ∅ otherwise; w_i(E) is its breeder weight. Write
`E[k←y]` for overwriting k with true weight y, removing its error when y=k.
Define the contribution attributed to recipient k by

\[
\begin{split}
\gamma_{T,k}=q^{-1}\sum_{i\in I_k}\sum_E\Pr_i(E)
\bigg[&\sum_{y\ne k}D(w_i(E),y)D(y,k)
       \{V_{T,i+1}(E[k\leftarrow y])-V_{T,i+1}(E)\}\\
 &+D(w_i(E),k)(D(k,k)-1)
       \{V_{T,i+1}(E[k\leftarrow k])-V_{T,i+1}(E)\}\bigg]. \tag{5}
\end{split}
\]

Then `γ_T=Σ_k γ_{T,k}`. The last term accounts for the suppression of a clean
repair by an activated mask. For k≥1 that term vanishes because those slots
are correct before the insertion. Its inclusion at k=0 is essential.
The direct endpoint terms satisfy `γ_{3,0}=γ_{2,0}` exactly: neither process
has any other erroneous coordinate after an update to recipient 0.

[coefficient.py](coefficient.py) implements (2), (4), and (5). The independent
[verify.py](verify.py) enumerates all 256 n=3 populations per T, literal bit
masks, scalar comparisons and full sweep transitions. Its full-population
derivative equals (5) as a rational number for both T. It also verifies a
strictly positive contribution from already-aligned intermediate prefixes:
dropping those prefixes would change the answer.

## A simpler expression for distant errors

**Proved.** For k≥2 with `I_k∩{0,1}=∅`, put

\[
G_k=\prod_{j\in I_k\setminus\{k\}}(1-D(j,k)),\quad
r_k(y)=1-G_k(1-D(y,k)),
\quad b_{k,i}(y)=\prod_{j\in I_k,\ j>i}(1-D(w_j,k)),
\]

where `w_k=y` and other `w_j=j` in the last product. Then

\[
\boxed{\gamma_{T,k}=\sum_{i\in I_k}\sum_{y\ne k}
 \frac{D(i,y)D(y,k)b_{k,i}(y)}
 {r_k(y)\,[q+(1-q)r_k(y)]}.} \tag{6}
\]

All relevant breeders are after breeder 1. When the activation happens, the
endpoint is correct with probability q. The new error survives the suffix with
probability b. At future boundaries the endpoint and new error have independent
geometric repair times with parameters q and r: they use disjoint breeders,
and neither wrong slot changes the other's donor weights. The excess mean
over the endpoint-only time, averaged over its current status, is
`b[1/r−(1−q)/(q+r−qr)] = bq/[r(q+r−qr)]`. Equation (3) cancels q and yields
(6). No independence of actual noisy population coordinates is assumed.

This formula covers every k≥3 for both T, and k=2 for T=2. The exact tests
compare it against (5). For all such sites, `r_k(y)≥D(y,k)` implies the useful
bound `0≤γ_{T,k}≤|I_k|/q=O(n)`. For interior T=3 sites a stronger constant
bound follows below.

## Candidate proof of the n log n term

All O constants here are absolute, independent of n, target and parity in the
stated ranges. This argument establishes (1) if the uniform estimates and the
two exceptional-site bounds below survive independent review. No fitted slope
is used as a premise.

**1. Exceptional sites cost at most O(n) in total.** We have
`q=1/(en)+O(n^−2)`. For recipient 0, the relevant active or suppressed
acceptance masses total O(1/n), while every affected zero-noise remaining
mean is O(n), because correct donor 1 has repair probability at least a
constant/n per sweep. Division by q in (5) gives `|γ_{T,0}|=O(n)`.

For recipient 1 there are a bounded number of donors, of bounded true weight.
A wrong true child observed as 1 has probability O(1/n): it requires a loss of
at least one of a bounded expected number of ones across the two masks.
For parent weight 1, the wrong-child condition rules out a path with no such
loss; for parent weight ≥2, observing 1 already requires a loss. A two-error
state at 0 and 1 has mean O(n) uniformly in the wrong value of slot 1:
before endpoint repair donor 0 has weight 2 and `D(2,1)≥c/n`; after endpoint
repair it has weight 0 and `D(0,1)≥c`. Once slot 1 repairs it stays correct,
and repairs endpoint 0 in O(n) sweeps. Thus `|γ_{T,1}|=O(n)` by (5).

Recipient 2 at T=3 has correct donor 1 and `D(1,2)≥c>0`, so its error has
uniformly bounded clean remaining lifetime. While the endpoint is wrong,
its repair probability at each eligible attempt is O(q), conditional on
the pre-attempt history. Count those attempts only while recipient 2 is still
wrong, using predictable indicators. Their expected count is O(1), hence
the probability of endpoint repair before this error disappears is O(q).
After such a repair the error's conditional remaining lifetime is still O(1).
An already-correct endpoint prefix has probability at most q. Therefore the
additional mean in (5) is O(q), giving `γ_{3,2}=O(1)`. This argument does not
condition on a future error lifetime or on accepted noise.

At the right endpoint, and at the at most two exceptional sites of the last
T=2 pair when n is even, the bound following (6) gives O(n) per site. In
particular, when n is even, T=2 has `I_n={n}`: this orphan must not be treated
as an ordinary two-site pair. All these exceptional terms are O(n) together.

**2. T=3 interior contribution is O(n).** For each other interior recipient k,
both neighbors are donors. One of the single-flip events from k−1 or k+1 to k
has probability at least
`(1/2)(1−1/n)^(n−1)≥c>0`. Thus r_k(y)≥c for all y, independently of its wrong
weight. With at most four incoming breeders, (6) is O(1) per site.
Together with step 1, `γ_3(n)=O(n)`.

**3. Identify the singular T=2 targets.** Apart from the exceptional last pair,
T=2 pairs (0,1),(2,3),…. A recipient k has one external donor j. Write
`a=D(j,k)`, `d_y=D(y,k)`, `r_y=a+(1−a)d_y`. Formula (6) becomes

\[
\gamma_{2,k}=
\begin{cases}
\sum_{y\ne k}\dfrac{d_y[D(j,y)+(1-a)D(k,y)]}{r_y[q+(1-q)r_y]},&j=k+1,\\
\sum_{y\ne k}\dfrac{d_y[(1-d_y)D(j,y)+D(k,y)]}{r_y[q+(1-q)r_y]},&j=k-1.
\end{cases} \tag{7}
\]

In the central half of the indices, a is bounded below by a positive constant,
so each contribution is O(1). In the left quarter, odd k have a donor below
them and also have a≥c. The potentially slow left targets are even
`2≤k≤n/4`, with j=k+1. Symmetrically, the potentially slow right targets are
odd k≥3n/4, with j=k−1.

**4. The single-step error gives the harmonic term.** For the slow left target,
let u=k+1, and consider the erroneous value y=j=k+1. Direct binomial estimates,
uniform for u≤n/4+1, give

\[
a=\frac{u}{en}[1+O(u/n+1/n)],\quad
D(j,j)=e^{-1}+O(u/n+1/n),\quad
D(k,j)=e^{-1}+O(u/n+1/n).
\]

For example, the term with one one-bit loss and no other flips in a is
`(u/n)(1−1/n)^(n−1)`. Every other way to lose net weight one requires at
least two one-bit losses and contributes O((u/n)²). The two probabilities
near e^−1 follow by isolating zero flips, or one zero-bit flip, and bounding
all cases involving a one-bit loss by O(u/n).

The contribution at y=j in (7) is exactly

\[
\frac{D(j,j)+(1-a)D(k,j)}
     {(2-a)[q+(1-q)a(2-a)]}
=\frac{n}{2(k+1)}+O\left(1+\frac{n}{(k+1)^2}\right). \tag{8}
\]

The q correction accounts for the `n/(k+1)²` term; it cannot be discarded
uniformly at fixed small k. On the right the cyclic order changes the numerator
to `(1-a)D(j,j)+D(k,j)`, giving the same leading term with `u=n-k+1`.

**5. All other error values contribute O(1) per slow site.** On the left,
children y≤k−1 have total proposal mass O((k+1)/n), since the first mask must
lose at least one original one. Because `r_y≥a` and `r_y≥d_y`, their terms
in (7) sum to at most this mass divided by `(1-q)a`, hence O(1).

For children y≥k+2, observing k requires at least two ones to flip in the
noise mask. Conditional probability is at most `y(y−1)/(2n²)`. From either
parent k or k+1 the mutated weight Y has `E[Y²]≤C(k+1)²`: the number of newly
flipped zeros has bounded first and second moments. Therefore the combined
erroneous-observation mass is O(((k+1)/n)²). Since `r_y≥a≥c(k+1)/n`, its
contribution in (7) is O(1). Complementing weights gives the same bounds on
the right; the two order-dependent numerators are each bounded by the sum
of the two proposal masses.

**6. Sum the two edges.** Even left indices have spacing two, so

\[
\sum_{2\le k\le n/4,\ k\ \mathrm{even}}\frac{n}{2(k+1)}
=\frac n4\log n+O(n).
\]

The right odd indices give another `(n/4)log n+O(n)`, for either parity of n.
The error terms in (8) sum to O(n), as do the nonsingular sites and step 1.
Thus `γ_2(n)=(n/2)log n+O(n)`, whereas `γ_3(n)=O(n)`, yielding (1).
Parity changes the O(n) term, not the logarithmic coefficient.

## Checks, interpretation, and limits

**Mechanically checked.** [coefficients.csv](coefficients.csv) contains exact
finite-n results for n=3,…,10 and deterministic float64 evaluations for paired
even/odd sizes through 1024/1025. [components.csv](components.csv) preserves
the exact recipient decomposition. No trajectory, seed, confidence interval
or censoring is associated with these calculations. Floating rows are not
certified intervals. The exact full-state check is restricted to n=3.

At n=3 the gap decomposes as follows, in sweeps per unit p:

| Recipient | T=3 minus T=2 contribution |
|---:|---:|
| 0 | 0 exactly |
| 1 | +0.31317331412278426 |
| 2 | −0.09104146694500106 |
| 3 | 0 exactly |

Thus the identical direct endpoint donors do not force the same derivative:
corrupting donor 1 changes later endpoint repair, and an interior error changes
the simultaneous stopping event. The positive n=3 balance reverses at n=4.
The larger-n logarithm instead comes from interior T=2 errors whose only
external donor points in the slow mutation direction near an end.

At the previously certified n=3,p=1/192, the linear prediction is
0.00115693670405095 sweeps; the published gap is about 0.00116866264509.
The difference, about 0.00001172594104, is a finite-p remainder, not simulation
error. [dependency.json](dependency.json) gives its exact certified interval.

**Proof gaps and falsifiers.** The finite-n recurrence has an exact independent
check at n=3, not at all n. A literal transition or full-state derivative
disagreeing with (4)–(6) would falsify the reduction. The asymptotic argument
is a candidate awaiting independent scrutiny of its uniform estimates,
exceptional-site bounds and cyclic suffix factors. A rigorous sequence for
which A_n/(n log n) fails to approach −1/2 would falsify it. All-n negativity
from n=4 is not proved here. Most importantly, no uniform Taylor remainder
has been established, so no positive-c noisy ordering is deduced from (1).

The original preregistration and gate-blocked holdout are preserved. Earlier
empirical comparisons concern ordinary initialization and are not evidence for
the derivative or its asymptotics. This offline round makes no novelty claim
or assertion of a globally open literature question. The already published
model comparison with Doerr, Elmoutassim, Krejca and Kibulu, *Understanding the
Co-evolutionary Solution Exchange of the MOEA/D: Already the Smallest
Communication Radius Gives the Best-Possible Speed-Up* (2026),
arXiv:2610.35373, DOI:10.48550/arXiv.2610.35373, remains the relevant scope
boundary: its noiseless radius/archive theorem does not supply this noisy,
filled-cardinality, simultaneous-boundary coefficient.
