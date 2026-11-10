# Independent audit of compensated centering and ORRR

**Verdict: proved in the supplied pinned model.** The round-17 candidate
survives this later analytic audit. For even \(n\ge4\), let \(m=n+1\),

\[
L=20n,\qquad q=1-(1-d(2,0))(1-d(1,0)),
\]

where \(d(x,z)\) is the weight transition probability under independent
per-bit mutation of rate \(1/n\). In full-population sweep units,

\[
\boxed{|\mathrm{ORRR}|\le2048m^3L^4/q<8\cdot10^9 n^8.} \tag{1}
\]

This is one ordered fourth response. The full fourth-order gap remains
**conjectured polynomial** in the published research; (1) supplies neither
a uniform Taylor remainder nor ordering at fixed positive \(c\), \(p=c/n\).
The finite calculations below are separately **mechanically checked**.
They are not the justification of the all-\(n\) conclusion.

This is an independent review and implementation in a later round, not a
second concurrent agent. The review does not use the still-candidate
isolated-pair second response. The original constants suffice. One notation
point is made explicit: the extended compensated equation uses the
**unrestricted** clean kernel, while its occupation inverse uses killing.
Confusing these two kernels would make that equation false at the killed row.

## Process and operators

**Definitions.** The supplied population is \(C=(2,1,2,\ldots,n)\), with
ideal extrema \((0,n)\), labels \(b_k=k\), and no initialization cost.
Breeders \(0,\ldots,n\) repeat in ascending order, each mutating its own
incumbent by independent per-bit flips of rate \(1/n\). An independent
Bernoulli(\(p\)) gate activates a second independent mask of the same rate
for observation. A shared observation is offered to a filled cardinality
two neighborhood. Even breeders prefer right, odd breeders left, and invalid
indices are skipped. Thus breeder \(n\) offers to \(n,n-1\). This is not a
clipped-radius model.

Pinned max-Chebyshev selection has cost

\[
C_k(w)=\max\{k(n-w),(n-k)w\}.
\]

Its unique minimum at \(k\) makes an offer acceptable exactly when its
observed weight is \(k\); the stored true weight becomes the child's weight.
Let \(\mathcal F_t\) reveal the supplied state and all consumed masks and gates
through attempt \(t\). The runtime \(\tau\) is the first phase-zero boundary
with all true weights correct; aligned interior phases remain live. Bounds
condition on the pre-proposal history, using fresh randomness. No claim
conditions the noise law on acceptance or retention; no drift or tail theorem
is invoked.

Write \(P\) for the unrestricted clean kernel on population and next-breeder
phase, \(a=(A_n,0)\) for the aligned boundary, and \(K\) for its restriction
to live states, with transitions to \(a\) killed. Every fixed-\(n\) clean
error has a positive own-repair probability, and clean updates only delete
errors, so \(G=(I-K)^{-1}\) exists. Extend every response by zero at \(a\).
The reward is \(1/m\) per live attempt.

Split the unrestricted activated-minus-clean difference into \(R+O\)
by recipient: \(R\) changes only slots \(0,\ldots,n-1\), and \(O\) only
slot \(n\), at breeder \(n\). Each is the difference of two stochastic
restricted-update kernels, with row sum zero. This split is algebraic;
it does not assign independent gates to recipients. In particular, for a
phase function \(f\), at the next phase,

\[
R_i f(s)=\sum_{k\in B_2(i),\ k<n}\left[
\sum_x d(s_i,x)d(x,k)\{f(s^{k\leftarrow x})-f(s)\}
-d(s_i,k)\{f(s^{k\leftarrow k})-f(s)\}\right]. \tag{2}
\]

Both the negative unchanged-state term and the suppressed clean repair
are present. Only one target can equal the shared observation, so the full
active kernel is the sum of its two recipient-restricted kernels minus the
identity, and the same is true for the clean kernel. Their difference is
therefore exactly R+O. This is the identity used by the new raw solver.

Let \(H_0=G(1/m)\), \(H_j=GRH_{j-1}\), and

\[
\mathrm{ORRR}=e_CGOH_3. \tag{3}
\]

These finite-state Taylor/ordered-word identities are justified at each
fixed \(n\), with coefficients of ordinary powers of \(p\), without
factorials. A word is a signed response, not a probability of exactly that
many activated gates. No uniform analytic radius is assumed.

## Audited compensated identity

**Proved.** Let \(A_y\) have every regular slot correct and orphan value \(y\).
Set \(B_j(y,i)=H_j(A_y,i)\) and \(D_j(s,i)=H_j(s,i)-B_j(s_n,i)\).
Define \(g_0=1/m\), \(g_j=R_iH_{j-1}\) for \(j\ge1\), and

\[
\lambda_j=\sum_{i=0}^n g_j(A_n,i),\qquad\lambda_0=1.
\]

At an aligned interior phase the clean population stays aligned until the
boundary, so \(H_j(A_n,i)=\sum_{r=i}^n g_j(A_n,r)\) for \(i>0\).
At phase zero it is instead zero. Therefore, on **all** population-phase
states, with \(P\) unrestricted,

\[
H_j=g_j+PH_j-\lambda_j1_a. \tag{4}
\]

Since \(R\) leaves the orphan unchanged and its unrestricted row sums to
zero, \(R_iB_{j-1}=0\) and \(g_j=R_iD_{j-1}\) at the successor phase.
There is no phase-wrap exception: the baseline itself is zero at the only
killed continuation \((A_n,0)\). Using unrestricted rows with zero-extended
functions makes this precise.

Couple a clean population with \(A_y\) at the same phase, retaining their
common orphan trajectory \(Y_t\). The orphan evolves only from its own
parent and is autonomous. At breeder \(n\), use the same child in both
chains, so last-pair repair and orphan repair retain their actual dependence.
All baseline regular slots remain correct. When the actual regular slots
become correct, the two populations coalesce.

Equivalently, the local centered equation has correction
\(\lambda_j1_{\{s_{0:n}\ne(0,\ldots,n-1),\,s_n=n,\,i=0\}}\).
Here \(s_{0:n}\) means the n regular coordinates. At a regular-complete
boundary both the actual and baseline killed-row corrections coincide
and cancel; no correction should be added there. The stopped formulation
below automatically enforces this qualification.

Let \(\rho\) be the first future regular-complete phase-zero boundary, with
\(\rho=0\) if the starting boundary is regular-complete. For a start with
regular errors, before \(\rho\) the actual chain cannot visit \(a\).
The baseline visits \(a\) exactly at phase-zero times with \(Y_t=n\).
Subtract (4), telescope to \(\rho\), and use the zero terminal difference:

\[
D_j(s,i)=E\sum_{t<\rho}\left[g_j(S_t,I_t)-g_j(A_{Y_t},I_t)
 +\lambda_j1_{\{Y_t=n,I_t=0\}}\right]. \tag{5}
\]

For \(j=0\) the \(g\) terms cancel. Thus \(D_0\ge0\) is exactly the expected
number of correct-orphan phase-zero boundaries before regular completion.
If the regular slots are already correct at an interior start, \(D_j=0\)
and every summand before the next boundary is zero. The same observation
permits stopping (5) at the first mid-sweep regular completion. This is an
auxiliary identity; the actual runtime still stops only at a full boundary.

For every fixed \(n\), the functions are bounded on a finite state space.
The regular completion times below have finite expectation. Apply (5) first
at \(\rho\wedge N\); the expected terminal difference tends to zero and
bounded forcing times integrable duration permits the limit. No moment or
tail estimate is inferred from a single starting mean.

**Contradicted shortcut.** Dropping \(\lambda_j\) is invalid. At \(n=4\)
the degree-one and degree-two residuals are about 2.071469580410 and
2.835341435438. The independently computed exact residual equals
\(\lambda_j\), including \(\lambda_0=1\); see [flux.csv](flux.csv).

## Audited surviving-overwrite budget

**Proved.** Regular pairs are \(\{0,1\},\ldots,\{n-2,n-1\}\); only the last
also receives orphan help. Clean changes only delete errors. Count a generic
wrong regular value as one surviving arbitrary overwrite, but count the
original value \(w_0=2\) as zero. This is a lower bound on the number of
previous arbitrary overwrites, even if overwritten values have been changed
again or repaired. Correct values cost zero. Consequently:

* At budget three there are at most four regular errors.
* A pair with both slots wrong needs two generic overwrites, except
  \(\{0,1\}\) with \(w_0=2\), which remains fast.
* Two slow pairs need at least four overwrites and cannot occur in the
  families needed to bound \(D_0\) after a third insertion.

A correct adjacent partner proposes its target neighbor with probability
at least \(1/(3n)\) on its scheduled turn. If the first pair has both slots
wrong but \(w_0=2\), breeder 0 proposes weight 1 with probability at least
\(2/(3n)\). If it has already repaired to 0, the corresponding probability
is at least \(1/3\). After that extension the other member is fast. Thus
a good configuration with at most four errors is solved by at most four
successive extensions, each with conditional expected delay at most \(3n\)
sweeps. Each successful extension persists in the clean chain. The allowance
\(L=20n\) covers these delays, an initial partial sweep and boundary rounding.
This proof ignores orphan help and hence is uniform over its trajectory.

For a slow pair with wrong values \(x,z\) at \(k,k+1\), set

\[
a=d(x,k),\quad b=d(z,k+1),\quad M=L+2/(a+b). \tag{6}
\]

Before its first repair the two wrong values stay fixed. On a full sweep,
the two own proposals escape with probability at least
\(1-(1-a)(1-b)\ge(a+b)/2\). One partial sweep, that geometric waiting time,
then at most three good extensions fit in (6). More explicitly, each of
expected attempts divided by \(m\) and expected phase-zero counts is at most
\(2/(a+b)+9n+3\le M\). The same cap holds for every clean descendant; a
first repair removes the slow pair. This also covers the orphan-fed pair
without assuming independent clocks.

An accepted active overwrite has probability \(d(\mathrm{parent},x)d(x,k)\).
If it creates or modifies a slow pair, its extra mean is controlled **before**
summing its mutation row:

\[
d(x,k)\frac{2}{d(x,k)+b}\le2. \tag{7}
\]

For a state with at most two prior overwrites, one more cannot create a
second slow pair. A birth outside an existing slow pair retains its old cap;
a birth inside it is controlled by (7). A good state either stays good or
creates just one such pair. Thus the active restricted expectation of
\(D_0\) is at most \(M+4\), while the clean restricted expectation is at most
\(M\). Since \(D_0\ge0\), their difference obeys

\[
|g_1|\le M+4\le2M,\quad |g_1(A_y,i)|\le L,
\quad |\lambda_1|\le mL. \tag{8}
\]

Equation (5), with expected attempts at most \(mM\) and phase-zero counts
at most \(M\), now gives

\[
|D_1|\le mM(2M+L)+mLM\le4mM^2\le5mM^2. \tag{9}
\]

This applies through two surviving overwrites, uniformly in orphan value
and phase. In particular good states use \(M=L\). It bounds a centered
response, not the uncentered \(H_1\) during an arbitrarily long orphan error.

## Audited marked response

**Proved.** Start from the corner or its clean subset, with one arbitrary
regular overwrite \(x\) at \(k\), marked by \(a=d(x,k)>0\). Such a state is
good. Clean descendants either retain this marked wrong value or have erased
it; retaining the old positive \(a\) as a mark remains a valid upper bound.
After erasure the unmarked estimates below already suffice.

If a subsequent birth creates a slow pair, it must overwrite the wrong
marked value's partner. It cannot use the original \(w_0=2\) alone to form
a slow pair, and a birth changing the mark itself leaves a good state.
Writing \(b\) for the second accepted observation factor, the exact inequality

\[
b\{L+2/(a+b)\}^2\le2L^2+2/a \tag{10}
\]

follows from \((u+v)^2\le2u^2+2v^2\) and
\(b/(a+b)^2\le1/(4a)\). Apply it to (9), and only then sum each conditional
mutation row. There are at most two recipients. Keeping the unchanged and
clean branches gives active and clean absolute expectations bounded by
\(5m(5L^2+4/a)\) and \(5mL^2\), respectively. Hence

\[
|g_2|\le32m(L^2+1/a). \tag{11}
\]

From \(A_y\) or an unmarked corner/subset a single birth is always good, so
\(|g_2|\le10mL^2\), and \(|\lambda_2|\le10m^2L^2\).
The marked population remains good under clean evolution, with regular
duration at most \(L\). Equation (5) therefore yields

\[
|D_2|\le52m^2L^3+32m^2L/a
       \le64m^2L(L^2+1/a). \tag{12}
\]

On the unmarked family the corresponding bound is \(30m^2L^3\), so the
convenient common bound \(64m^2L^3\) holds there. This calculation integrates
only to regular completion, not over the possibly much longer orphan life.

Finally, from an unmarked corner/subset, keep the actual acceptance factor
\(a=d(x,k)\) on the next birth and use (12). Its active absolute expectation
is at most

\[
64m^2L^3+128m^2L(L^2+1)\le320m^2L^3.
\]

The clean absolute expectation is at most \(64m^2L^3\). Therefore

\[
|g_3|=|R_iD_2|\le384m^2L^3\le B:=512m^2L^3. \tag{13}
\]

The parent may depend on all earlier repairs and overwrites. Each fresh
conditional mutation row still sums to one, which is all that was used.
There is no distributional assumption about a parent conditional on an
accepted observation.

## Audited orphan entrance and assembly

**Proved.** After the first \(O\), regular slots are still the corner or
its clean subset. Put \(d_y=d(y,n)\). At a boundary with wrong orphan \(y\),
its clean repair mean is \(1/d_y\) sweeps. Since correct slots persist,
joint boundary completion is no later than the sum of regular and orphan
boundary completion times, even when dependent. Integrating (13) in
\(H_3=Gg_3\) gives

\[
|H_3(s,y)|\le mB(L+1/d_y),\qquad |H_3(s,n)|\le mBL. \tag{14}
\]

Before the first \(O\), the orphan is correct. Its positive birth of \(y<n\)
has exact coefficient \(c_y=d(n,y)d_y\), and the other term is the negative
unchanged state. Thus, before taking any supremum over wrong orphan values,

\[
|OH_3|\le mB\sum_{y<n}c_y(1/d_y+2L)
          \le mB(1+2L)\le3mBL. \tag{15}
\]

The \(d_y\) cancels the inverse repair rate; discarding it first would lose
the conclusion. The clean corner sees exactly one orphan turn per unsolved
sweep, with mean count \(1/q\). This includes the last turn in a sweep whose
corner repaired earlier. Consequently (3) and (15) imply

\[
|\mathrm{ORRR}|\le1536m^3L^4/q\le2048m^3L^4/q.
\]

Finally \(q\ge d(1,0)\ge1/(3n)\) and \(m\le2n\) prove (1).
The exact oracle explicitly retains the terminal-sweep contribution:

\[
\mathrm{ORRR}=\{(1-q)(OH_3)(C,n)+q(OH_3)(A_n,n)\}/q. \tag{16}
\]

## Reproducible checks, limits and falsifiers

**Mechanically checked.** [audit.py](audit.py) imports no earlier solver.
It solves raw uncentered responses by clean-cycle first-step equations, then
subtracts the matched baseline. It separately solves the stopped
correct-orphan boundary reward for \(D_0\). Literal genotype masks and pinned
max-Chebyshev comparisons check its transition/forcing formulas in
[test_audit.py](test_audit.py). [verification.json](verification.json) gives
the exact finite scope and counts, [responses.csv](responses.csv) the state
checks, [budget.csv](budget.csv) the abstract support enumeration, and
[inequalities.csv](inequalities.csv) the acceptance inequalities.

The deterministic finite grids were designed in this round. They are not
presented as preregistered stochastic measurements.

[words.csv](words.csv) matches the published exact ORRR fingerprints at
both \(n=4\) and \(n=6\). [entrance.csv](entrance.csv) retains each \(d_y\)
and \(c_y\). The calculations are deterministic rational computations with
no sampling uncertainty or censoring. Finite checks cannot establish the
all-\(n\) bound; the argument above does that work.

**Dependencies.** The full round-17 replay includes the relevant earlier
geometry, acceptance results and recursive registration/receipt verification.
Published artifact hashes and regenerated outputs are checked before use.
The new analytic proof rederives its clean geometry and does not depend on
the unreviewed isolated-pair response. See [dependency.json](dependency.json)
for the replay and the limits of published chronology. No prior experiment
needed a plan or receipt repair. New empirical measurement would still need
a plan committed in an earlier round; none was launched here.

**Unresolved in this checkout.** RRRR and the other untreated fourth-order
words, a useful uniform higher-order remainder, fixed-positive-\(c\) ordering
and ordinary-initialization behavior remain outside this proof. The positive
exponential residence counterexamples remain valid; they do not bound this
signed word below. The original preregistration, main cap, 240 missing
blocked holdout trials and inconclusive original two-stage decision are
preserved. No current-literature search or novelty assertion is made in this
offline audit, and the repository's noiseless radius/archive theorem is not
transferred to the noisy process.

**Proved scope limit:** the one-slow-pair support lemma cannot simply be
extended to four regular births. At n=4, start from (2,1,2,3,4), retain the
corner through breeder 0, then accept true weight 0 at regular targets 1,
2 and 3 on their successive own turns. Let breeder 4 make a clean copy.
At the next breeder-0 turn accept true weight 3 as observation 0. The state
is (3,0,0,0,4), with two slow regular pairs. Every specified mutation and
observation has positive probability. This lies outside the three-R budget
of ORRR and illustrates an extra obligation for RRRR; it is not a lower
bound on that signed word.

**Falsifiers.** A nonzero \(R_iB_j\) with the stated phase convention; failure
of (4) or (5); two slow pairs within three arbitrary regular overwrites;
a second birth making a slow pair without the marked acceptance factor;
failure of the uniform clean duration bound; an absent negative branch in
(2) or (15); or an independent exact coefficient disagreement would invalidate
the corresponding step. None was found. The nonzero flux already falsifies
the uncompensated shortcut. A full fourth-order claim would require its own
additional proof obligations and is not certified by this audit.
