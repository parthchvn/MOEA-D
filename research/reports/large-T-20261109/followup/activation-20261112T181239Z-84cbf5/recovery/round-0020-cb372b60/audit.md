# Independent analytic audit of RORR

**Verdict: proved under the supplied pinned model below.** The round-19
candidate's baseline decomposition and both entrance estimates are valid.
For even n >= 4, write m=n+1, L=20n, and

\[
q=1-(1-d(2,0))(1-d(1,0)),
\]

where d is the weight kernel of independent per-bit mutation of rate 1/n.
Then, in sweep units,

\[
\boxed{|\mathrm{RORR}|\le 1024m^3L^4/q
       \le3{,}932{,}160{,}000n^8<4\cdot10^9n^8.} \tag{1}
\]

This later-round review independently rederives the needed marked premise
and the new assembly. It is not a concurrent second-agent review. The proof
is separate from the finite rational checks in [verification.json](verification.json).
Only one ordered fourth response is bounded. The complete fourth-order gap
remains **conjectured polynomial in the published project**, and neither a
uniform Taylor remainder nor fixed-positive-c ordering follows.

## Process, conditioning and response convention

**Definitions.** Start from C=(2,1,2,...,n), ideal extrema (0,n), and stored
labels b_k=k. Initialization has no charge. Breeders 0,...,n repeat in
ascending order and mutate their own incumbents by fresh independent
per-bit flips of rate 1/n. An independent Bernoulli(p) gate activates an
independent observation mask with the same rate. One shared observed child
weight is offered to the filled-cardinality T=2 neighborhood. Even indices
prefer right and odd indices prefer left, skipping an invalid neighbor.
For even n, the regular pairs are {0,1},...,{n-2,n-1}; breeder n offers to
{n,n-1}. Only breeder n can change the orphan slot n. The last pair receives
orphan help and is not autonomous.
The frozen implementation's `scripts/neighborhood_sweep.cpp` functions
`first_recipient` and `cost` agree with this neighborhood and scalarization
when the reference is (0,n); this does not identify the supplied-state
experiment with ordinary initialization.

The scalarization is max{k(n-w),(n-k)w}. Its unique minimum is k, so with
pinned labels recipient k accepts exactly observation k and stores the true
child weight. Clean updates only correct errors; noisy updates need not.
The weight reduction is exact because both masks and selection depend on
genotypes only through their weights.

Let F_t reveal the supplied state, breeder phase and all masks/gates consumed
through t completed attempts. Bounds below condition before the next
proposal, using its fresh randomness. They do not condition a noise law on
acceptance or on a retained stored label. Let tau be the number of attempts
until the first fully aligned phase-zero boundary; aligned interior phases
remain live. The reward is 1/m per live attempt. No drift theorem is used,
and no tail is inferred from an expectation.

Let P be the unrestricted clean kernel on population/next-breeder phase and
K its restriction killed at a=(A_n,0), where A_y=(0,1,...,n-1,y). Set
G=(I-K)^(-1). Every fixed-n own repair probability is positive and clean
changes delete errors. Successive own-repair stages give finite absorption
means, so G exists. Functions below are zero at a, not at aligned interiors.

The activated-minus-clean difference splits algebraically as R+O by updated
recipient: R changes regular slots, and O changes slot n at breeder n.
Both are differences of recipient-restricted stochastic kernels. There
are not separate recipient noise gates. At most one target equals the
shared observation, which proves the split even at breeder n.

For a continuation f at the successor phase, the regular operator is

\[
R_i f(s)=\sum_{k\in B_2(i),k<n}\left[
\sum_xd(s_i,x)d(x,k)(f(s^{k\leftarrow x})-f(s))
-d(s_i,k)(f(s^{k\leftarrow k})-f(s))\right]. \tag{2}
\]

This includes the negative unchanged term and the suppressed clean repair.
Define H_0=G(1/m), H_1=GRH_0, H_2=GRH_1 and J=GOH_2. Then

\[
\mathrm{RORR}=e_{(C,0)}GRJ=e_{(C,0)}G R G O G R G R H_0. \tag{3}
\]

There is a clean resolvent between consecutive insertions. This is a
coefficient of ordinary powers of p, without factorials, and not a
probability of exactly four activations. At each fixed n, the finite killed
kernel is affine in p and invertible near zero; its expansion justifies
(3). No n-uniform radius of analyticity is assumed.

## The round-18 premise, checked before use

**Proved; independently rederived here.** Put
B_j(y,i)=H_j(A_y,i), D_j(s,i)=H_j(s,i)-B_j(s_n,i), and g_j=RH_{j-1}.
The particular estimates needed are

\[
|g_2(A_y,i)|\le10mL^2,\quad
|D_2(s,i)|\le64m^2L^3 \quad\hbox{on the unmarked corner/subset family}, \tag{4}
\]
\[
|D_2(s,i)|\le C(a):=64m^2L(L^2+1/a),\quad a=d(x,k)>0, \tag{5}
\]

after one regular overwrite k<-x, and along its clean descendants. All
phases and orphan values are included. The remembered a remains a valid
mark after that error is repaired. The published source is round-18
`audit.md`, equations (11)-(12), under
`research/reports/large-T-20261109/followup/`. Source hashes and tests are
verified in [dependency.json](dependency.json); no assertion of a complete
rerun of its much larger grid is made.

Here is an independent derivation of the assumptions and constants used.
Extend each H_j by zero at a and let lambda_j=sum_i g_j(A_n,i), with
g_0=1/m and lambda_0=1. At aligned interior phases the clean population
remains aligned until the next boundary. Thus on all states

\[
H_j=g_j+PH_j-\lambda_j1_a. \tag{6}
\]

The P here must be unrestricted, while G uses killed K. Since R preserves
the orphan and has unrestricted row sum zero, R B_j=0 at the matched
successor phase. Couple the actual and regular-correct baseline populations
using the same autonomous orphan trajectory. At breeder n use the same
child in both; do not split last-pair and orphan repair into independent
events. Until regular completion at a boundary rho, subtraction of (6)
gives

\[
D_j(s,i)=E\sum_{t<\rho}\left[
g_j(S_t,I_t)-g_j(A_{Y_t},I_t)
+\lambda_j1_{\{Y_t=n,I_t=0\}}\right]. \tag{7}
\]

If the regular slots are already correct, their difference and these
summands are zero. Telescoping first at rho truncated at a finite time and
then using finite mean duration justifies (7); fixed-n response functions
are bounded. In particular D_0 is a nonnegative expected count of
correct-orphan phase-zero boundaries before regular completion.

Count surviving arbitrary regular overwrites, excluding the original
slot-zero value 2. At budget three there are at most four regular errors
and at most one slow pair. Two slow pairs would require four arbitrary
overwrites: the first pair with its original 2 stays fast. A correct
adjacent donor supplies a neighbor's target with probability at least
1/(3n) at its scheduled turn. In the exceptional first pair, 2->1 has
probability at least 2/(3n); if slot zero repairs first, its correct value
0 also supplies 1 at rate at least 1/(3n). These bounds follow from the
one-bit component of standard-bit mutation and
(1-1/n)^(n-1)>1/e>1/3.

With no slow pair, at most four successive successful extensions suffice;
their conditional waiting means plus phase/boundary slack fit in L=20n.
For a slow pair with own-repair rates a,b, before its first repair the
wrong values are fixed. Conditional full-sweep failure is at most
(1-a)(1-b); external help can only delete errors. Its escape probability
is at least (a+b)/2. The initial partial sweep, this geometric wait and at
most three subsequent fast extensions fit in

\[
M=L+2/(a+b). \tag{8}
\]

This bounds both expected attempts/m and phase-zero counts, uniformly
along clean descendants and in orphan value. It uses successive conditional
means, not an unjustified maximum-of-means bound.

When an accepted extra birth creates or modifies a slow pair, retain its
acceptance factor b before summing the parent mutation row. The inequalities

\[
\frac{2b}{a+b}\le2,\qquad
b\{L+2/(a+b)\}^2\le2L^2+2/a \tag{9}
\]

hold pointwise. For the second, expand with (u+v)^2<=2u^2+2v^2 and use
b/(a+b)^2<=1/(4a), b<=1. Births outside an existing slow pair keep its old
cap; births inside it use the first inequality. At most two recipients
give active D_0 expectation <=M+4 and clean expectation <=M. Because D_0
is nonnegative, |g_1|<=M+4<=2M. On a regular-correct baseline
|g_1|<=L and |lambda_1|<=mL. Equation (7) yields
|D_1|<=4mM^2<=5mM^2 through two overwrites.

A once-marked state is good. A second birth can make a slow pair only
by corrupting the marked value's partner. Applying the second inequality
in (9), then summing the mutation rows, gives active and clean absolute
D_1 expectations <=5m(5L^2+4/a) and <=5mL^2. Therefore
|g_2|<=32m(L^2+1/a). On an unmarked corner/subset or baseline, all
one-birth successors are good, so |g_2|<=10mL^2 and
|lambda_2|<=10m^2L^2. The marked clean duration is <=L. Inserting these
three bounds into (7) gives

\[
|D_2|\le52m^2L^3+32m^2L/a\le C(a).
\]

The unmarked calculation gives 30m^2L^3<=64m^2L^3. This proves (4)-(5)
without using the candidate isolated-pair second response. Only the
three-overwrite support budget is used; it is not extended to four births.

## The baseline and the orphan entrance

**Proved.** At A_y, y<n, regular slots stay correct under clean evolution.
The orphan has repair probability d_y=d(y,n) each final turn, and stays at
y until repair. From phase zero its expected lifetime is exactly 1/d_y
sweeps, or m/d_y attempts. Combining H_2=Gg_2 with (4) gives

\[
|B_2(y,0)|\le10m^2L^2/d_y,\qquad B_2(n,0)=0. \tag{10}
\]

This is a first-moment occupation bound, not a higher residence-moment
bound. At an O insertion with a correct orphan, a wrong child y observed
as n has coefficient c_y=d(n,y)d_y. Its paired unchanged coefficient is
-sum_{y<n}c_y. Define

\[
\beta=\sum_{y<n}c_yB_2(y,0).
\]

Multiplying (10) by the actual entrance c_y before summing proves

\[
|\beta|\le10m^2L^2\sum_{y<n}d(n,y)\le10m^2L^2. \tag{11}
\]

The baseline inverse d_y has canceled. A uniform supremum over wrong y
before this multiplication would be invalid for the intended polynomial
estimate.

For a correct-orphan population s before breeder n put

\[
\Gamma(s)=\sum_{y<n}c_y\bigl[D_2(s^{n\leftarrow y},0)-D_2(s,0)\bigr].
\]

Both branches are at successor phase zero. Substituting H_2=B_2+D_2,
including the negative unchanged branch, gives the exact identity

\[
(OH_2)(s,n)=\beta+\Gamma(s). \tag{12}
\]

It follows from (5) that |Gamma(s)|<=2C(a), and from (4) that
|Gamma(s)|<=128m^2L^3 for unmarked s. If all regular slots are correct,
Gamma(s)=0 exactly. This statement includes the orphan-fed last pair:
the centered responses already use the coupled full process.

## All-phase occupation through the middle O

**Proved.** Before the middle O only one R has been inserted, so the orphan
is correct. R's positive branch changes at most one regular slot. Starting
from C or A_n, there are at most two regular errors, and they form a good
configuration as above. Clean descendants remain good. Ignore orphan help
and use at most two successive scheduled fast extensions. From any phase,
their total mean duration is <=6n sweeps; after regular completion, at most
one sweep reaches the next boundary. If

\[
N(s,i)=E_{s,i}\sum_{t<\tau}1_{\{I_t=n\}},
\]

then the extra initial phase offset is less than one sweep. Consequently
N(s,i)<=6n+2<=L for n>=4. This bound is uniform over all marks and clean
descendants; it is not conditioned on the parent's retained noise.

Occupation of (12) gives exactly

\[
J(s,i)=\beta N(s,i)+E_{s,i}\sum_{t<\tau}
             1_{\{I_t=n\}}\Gamma(S_t). \tag{13}
\]

The final breeder turn is included even when regular alignment happened
earlier in that sweep. The bound N<=L and (11)-(12) imply

\[
|J(s,i)|\le138m^2L^2(L^2+1/a)=:V(a) \tag{14}
\]

on the marked family, and

\[
|J(s,i)|\le138m^2L^4=:U \tag{15}
\]

on the unmarked family. For example the unsimplified marked expression is
10m^2L^3+128m^2L^2(L^2+1/a), which is bounded by (14).
All interior phases remain covered.

**Proved identity; contradicted shortcut.** On every clean path from phase
i, tau=m N_path-i, including the killed initial boundary. Hence
N(s,i)=H_0(s,i)+i/m. The unrestricted R row annihilates the successor-phase
constant; at phase zero that constant is also zero at the killed state.
Thus the baseline contribution to the word is

\[
e_CGR(\beta N)=\beta H_1(C,0). \tag{16}
\]

It is generally nonzero. At (A_n,n), OD_2=0 but OH_2=beta. Centering H_2
inside O, or stopping at aligned interior phases, deletes this real term.
[words.csv](words.csv) independently reproduces the nonzero omitted amount
and the resulting incorrect signed coefficient.

## Positive-kernel accounting for the first R

**Proved.** Prior to the first insertion, clean states are C or A_n with a
correct orphan. Write R=P_R^+-P_R^0 with the two restricted stochastic
kernels. In P_R^+, the accepted event (k,x) has probability
d(s_i,x)a, a=d(x,k). Distinct recipient targets correspond to disjoint
observations. The remaining no-accepted-target branch has nonnegative
mass at most one and is unmarked. Accepted events with x=s_k are allowed
in the sum; they are not a second copy of that branch.

Keeping a through (14), rather than first taking a supremum, gives

\[
\begin{aligned}
P_R^+|J|&\le U+138m^2L^2
       \sum_{k\in B_2(i),k<n}\sum_xd(s_i,x)(aL^2+1)\\
&\le U+276m^2L^2(L^2+1)\le690m^2L^4.
\end{aligned} \tag{17}
\]

There are at most two recipients, a<=1, and each fresh conditional mutation
row sums to one. This cancels the inverse a from the marked response.
The restricted clean kernel only keeps or repairs the original corner;
P_R^0|J|<=U. Therefore at every reachable pre-insertion phase

\[
|R_iJ|\le828m^2L^4\le1024m^2L^4. \tag{18}
\]

In particular this does not infer a small absolute branch from a small
signed final answer. [branches.csv](branches.csv) checks the active and
clean absolute expectations separately.

For a pointwise check that keeps both entrances simultaneously, (10) and
(5) imply, for y<n,

\[
\begin{aligned}
a c_y\bigl(|H_2(s^{n\leftarrow y},0)|+|H_2(s,0)|\bigr)
\le d(n,y)\bigl[10a m^2L^2+
128m^2L d_y(aL^2+1)\bigr].
\end{aligned} \tag{19}
\]

The second absolute term pays the negative unchanged O branch. Neither
inverse acceptance rate remains. The first regular mutation factor
d(parent,x) is summed later; it is not part of (19)'s left-hand weight.

Finally, before any insertion the original corner is repaired by donors
0 and 1 with per-sweep probability q. Clean repair persists, but stopping
still waits for the boundary. Thus e_C G 1=m/q exactly. Multiplying (18)
by this occupation mass gives (1); m<=2n and q>=d(1,0)>=1/(3n) give its
stated numerical constant. Attempts multiply the coefficient and bound
by m; O(n^8) here is in sweeps, not attempts.

## Verification, scope and next obligation

**Mechanically checked.** [audit.py](audit.py) solves all phase values using
a direct circular first-change equation, without importing an earlier
solver. For a fixed population, it sums one rotation of phase forcings,
weighted by the probabilities of staying at that population, and divides
by the clean escape probability. A changed clean successor has fewer
errors. Aligned phase zero is killed separately; its interiors use the
remaining suffix rewards. This is independent of round-19's sweep-product
enumeration of insertion placements.

The finite grid checks every phase, regular target and orphan value, from
corner and aligned origins; it checks every child at n=4 and children
{0,k,n} at n=6. The latter is deliberately a bounded subset, not a claim
to duplicate round 19's larger grid. Custom rewards separately compute
N, the Gamma occupation and its first-R response. Literal genotype-mask
tests check stochastic kernels and the shared observation split. Exact
fractions drive all equality/inequality decisions; hashes record large
fractions and decimals are presentation only. There are no new sampled
trajectories, sampling intervals or censored deterministic results.

**Mechanically checked dependencies.** The empirical registration/receipt
audit is rerun and its six outputs compared byte for byte. The round-18
and round-19 artifact manifests and tests are checked before use. The
marked premise is rederived above and tested independently; entire large
earlier theoretical grids are not replayed. This targeted verification
avoids treating a prior result as an unexplained black box. Published
private-log limitations remain: receipts do not prove the absence of
unreported earlier invocations. No plan or receipt repair was needed.

**Falsifiers.** A marked successor outside the good family; a failure of
the compensated equation; an incorrect final-turn count at any phase;
a missing negative branch; failure of either entrance cancellation;
non-stochastic restricted kernels; or an independent exact word mismatch
would invalidate its corresponding step. No such failure was found.
The nonzero baseline and boundary-compensation witnesses instead refute
the shortcuts described above.

**Open in this project checkpoint.** The remaining fourth-order words,
including RRRR and RROR, a uniform higher-order remainder, fixed-c ordering
at p=c/n, and ordinary initialization remain untreated by this theorem.
The isolated-pair second-response argument is still a candidate proof and
is unused here. Earlier positive exponential-residence obstructions remain
valid. The next bounded question is RROR: the newly audited baseline
integration suggests a route, but two regular insertions before O can
create a slow pair, so N<=L can no longer be assumed.

The original preregistration, capped main trial, 240 missing gate-blocked
holdout trials and inconclusive two-stage decision remain unchanged. The
independent n=512 follow-up does not replace that holdout. No noiseless
radius/archive theorem is transferred, and no current-literature novelty
claim is made in this offline audit.
