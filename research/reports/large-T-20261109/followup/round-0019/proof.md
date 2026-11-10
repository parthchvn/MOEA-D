# RORR with both entrance factors retained

**Candidate proof, awaiting independent analytic audit.** For even
\(n\ge4\), in the supplied pinned model below, put
\[
m=n+1,\qquad L=20n,\qquad
q=1-(1-d(2,0))(1-d(1,0)).
\]
Here \(d(x,z)\) is the weight transition probability of independent bit
mutation at rate \(1/n\). The proposed fourth-word bound, in sweep units, is
\[
\boxed{|\mathrm{RORR}|\le1024\,m^3L^4/q<4\cdot10^9n^8.} \tag{1}
\]
The new argument uses the round-18 **audited** marked two-R bound. It keeps
the first regular acceptance \(a=d(x,k)\) and the later orphan acceptance
\(d_y=d(y,n)\) until their respective inverse factors have canceled.
It neither commutes R and O nor freezes the orphan-fed last pair.

The status is intentionally a candidate for the new assembly. Exact finite
identities and inequalities are **mechanically checked**, not a substitute
for an all-n analytic audit. No complete fourth-order gap, uniform remainder,
fixed-positive-c ordering, or ordinary-initialization claim follows.

## Process, information, and operators

**Definitions.** Initialize true weights \(C=(2,1,2,\ldots,n)\), ideal extrema
\((0,n)\), and stored labels \(b_k=k\), with no initialization charge.
Breeders \(0,\ldots,n\) run in ascending cycles, each mutating its own
incumbent by fresh independent per-bit flips of probability \(1/n\).
An independent Bernoulli(\(p\)) gate activates a second mask with the same
bit-flip probability for observation. One shared observation is offered to
the filled-cardinality \(T=2\) neighborhood: even breeders prefer right,
odd breeders left, skipping invalid indices. Thus breeder \(n\) offers to
\(n,n-1\); only that breeder can update orphan slot \(n\).

The pinned max-Chebyshev cost is
\(C_k(w)=\max\{k(n-w),(n-k)w\}\). Its unique minimum is at \(k\), so a
recipient accepts precisely observation \(k\) and stores the true child
weight. The current true population need not be correct even though the
stored labels remain pinned. This is a cardinality model, not a radius model.

Let \(\mathcal F_t\) reveal the supplied state and all consumed masks and
gates through attempt \(t\). Let \(I_t\) be the next breeder phase, and let
\(\tau\) be the first phase-zero boundary at which all true weights equal
their indices. Aligned interior phases remain live. Each attempt earns
\(1/m\) sweep. Bounds condition before proposals, with fresh randomness;
no noise distribution is conditioned on acceptance or retention. No drift
theorem or tail-from-mean inference is used.

Write \(P\) for the unrestricted clean population/phase kernel, \(K\) for
its restriction killed on the aligned boundary \((A_n,0)\), and
\(G=(I-K)^{-1}\). This inverse exists at each fixed n: clean updates only
delete errors and every own-repair probability is positive. Responses are
extended by zero at the killed boundary, but **not** at aligned interiors.

Split the activated-minus-clean unrestricted kernel as \(R+O\), where R
changes only regular slots \(0,\ldots,n-1\), and O changes only slot n at
breeder n. Each is the difference of two recipient-restricted stochastic
kernels, with row sum zero and absolute row sum at most two. The split is
algebraic: it does not introduce separate activation gates. The shared
observation can equal only one recipient target.

For a next-phase function f the regular difference is
\[
R_i f(s)=\sum_{k\in B_2(i),\ k<n}\left[
 \sum_x d(s_i,x)d(x,k)\{f(s^{k\leftarrow x})-f(s)\}
 -d(s_i,k)\{f(s^{k\leftarrow k})-f(s)\}\right]. \tag{2}
\]
This includes the negative unchanged branch and the suppressed clean repair.
Define
\[
H_0=G(1/m),\quad H_1=GRH_0,\quad H_2=GRH_1,\quad J=GOH_2.
\]
Then chronological insertion order gives
\[
\mathrm{RORR}=e_C G R J=e_C G R G O G R G R H_0. \tag{3}
\]
There is one G between each adjacent insertion. These are coefficients of ordinary
powers of p, without factorials, at fixed n. They are signed responses,
not probabilities of exactly four activated gates. Finite-state
analyticity near zero supplies the coefficient identities, not a uniform
radius of analyticity as n varies.

## Audited premise and its exact scope

**Proved in round 18, replayed before use here.** For
\(A_y=(0,1,\ldots,n-1,y)\), set, at matched phase i,
\[
B_2(y,i)=H_2(A_y,i),\qquad D_2(s,i)=H_2(s,i)-B_2(s_n,i),
\qquad g_2=R H_1.
\]
The relevant inequalities are
\[
|g_2(A_y,i)|\le10mL^2,                                    \tag{4}
\]
\[
|D_2(s,i)|\le64m^2L^3                                   \tag{5}
\]
for the unmarked corner or its clean subset, with arbitrary orphan y, and
\[
|D_2(s,i)|\le C(a):=64m^2L(L^2+1/a)                       \tag{6}
\]
after one arbitrary regular overwrite \(k\leftarrow x\), marked by
\(a=d(x,k)>0\), and along its clean descendants. After the marked value
repairs, retaining the old positive a is a valid upper bound. Every phase
and every orphan value are included.

Source locus: repository
`research/reports/large-T-20261109/followup/round-0018/audit.md`, the
"Audited marked response" section, equations (11)-(12) and the adjoining
unmarked bounds. Its source hash and replay receipt are in
[dependency.json](dependency.json).

The underlying centering requires compensation. For general degree j,
the zero-extended identity is
\(H_j=g_j+P H_j-\lambda_j1_{(A_n,0)}\), with unrestricted P,
\(\lambda_j=\sum_i g_j(A_n,i)\). The occupation inverse still uses killed K.
Thus (4)-(6) do not rely on an uncompensated Poisson equation.

For clarity, the marked estimate keeps the second regular birth's factor b
in \(b\{L+2/(a+b)\}^2\le2L^2+2/a\). At most three regular overwrites are
needed for (6)'s derivation. At that budget there is at most one slow pair;
the original \(w_0=2\) is a fast special value. These are the relevant
scope restrictions of the audited premise. The isolated-pair second-response
candidate from round 15 is not used.

**Proved clean-duration premise, rederived.** Every regular state reached
from C or its clean subset by one regular overwrite is good: each erroneous
pair has a correct partner, except possibly the first pair with its original
weight 2. A correct adjacent donor repairs its neighbor with conditional
probability at least \(1/(3n)\) on its scheduled turn. In the exceptional
first pair, weight 2 at slot 0 proposes weight 1 with probability at least
\(2/(3n)\), after which donor 1 can repair slot 0. Clean repairs persist.
At most two regular errors require two successive extensions. Even using
the round-18 allowance of four extensions, their conditional waiting means
sum to at most 12n sweeps. Initial partial-sweep and boundary slack fit in
\(L=20n\). This also bounds the expected number of orphan-turn visits
before full completion when the orphan starts correct. Ignoring extra
orphan help is allowed because it can only delete regular errors.

This argument uses successive conditional means, not an unjustified bound
on a maximum. It is uniform along clean descendants and over any orphan
trajectory. Last-pair and orphan events need not be independent.

## The orphan baseline and its entrance factor

**New candidate step.** Write \(d_y=d(y,n)\). Starting at the boundary A_y
with y<n, regular slots remain correct in the clean chain. The autonomous
orphan has a constant repair probability d_y on each final turn. It takes
mean \(1/d_y\) full sweeps, or \(m/d_y\) attempts, to the killed boundary.
Since \(H_2=Gg_2\), (4) implies
\[
|B_2(y,0)|\le10m^2L^2/d_y,\qquad B_2(n,0)=0.             \tag{7}
\]
No bound on a higher residence moment is being inferred here.

At an O insertion whose orphan is still correct, the positive birth
\(n\leftarrow y<n\) has the exact coefficient
\[
c_y=d(n,y)d_y.                                          \tag{8}
\]
The negative unchanged coefficient is \(-\sum_{y<n}c_y\).
Define the signed baseline flux
\[
\beta=\sum_{y<n}c_y B_2(y,0).
\]
Retain d_y before summation in (7):
\[
|\beta|\le10m^2L^2\sum_{y<n}d(n,y)\le10m^2L^2.          \tag{9}
\]
This is the second entrance cancellation in chronological order. A supremum
over the wrong-orphan values before multiplying by c_y would lose it.

For a correct-orphan state s just before breeder n, define
\[
\Gamma(s)=\sum_{y<n}c_y\{D_2(s^{n\leftarrow y},0)-D_2(s,0)\}.
\]
Both the positive and negative branches occur at successor phase zero.
The exact decomposition is
\[
(O H_2)(s,n)=\beta+\Gamma(s).                           \tag{10}
\]
For marked states and all their clean descendants, (6) gives
\[
|\Gamma(s)|\le2C(a)\sum_{y<n}c_y\le2C(a).              \tag{11}
\]
For unmarked states use (5), giving \(|\Gamma|\le128m^2L^3\).
When all regular slots are correct, \(\Gamma=0\) exactly.

## Integrating to the middle O, with the final turn retained

**New candidate step.** Before the O in RORR, only the first R has occurred.
The orphan is correct and remains correct under intervening clean evolution.
Thus (10) is the only O forcing encountered. Let
\[
N(s,i)=E_{s,i}\sum_{t<\tau}1_{\{I_t=n\}}
\]
under clean dynamics with correct orphan. All these states are good, and
the duration premise gives \(N(s,i)\le L\). This includes the final breeder
turn in a sweep whose regular population became correct earlier.

Applying the clean occupation representation to (10) gives exactly
\[
J(s,i)=\beta N(s,i)+
 E_{s,i}\sum_{t<\tau}1_{\{I_t=n\}}\Gamma(S_t).           \tag{12}
\]
For marked states, (9), (11) and \(N\le L\) yield
\[
\begin{aligned}
|J(s,i)|
&\le10m^2L^3+128m^2L^2(L^2+1/a)\\
&\le138m^2L^2(L^2+1/a)=:V(a).
\end{aligned}                                         \tag{13}
\]
For an unmarked corner/subset state,
\[
|J(s,i)|\le10m^2L^3+128m^2L^4
          \le U:=138m^2L^4.                            \tag{14}
\]
These statements hold at phase zero and at every live interior phase.
No orphan-only function has been bounded uniformly before its entrance
weight was used; no assumption of independent completion clocks was made.

**Exact identity; mechanically tested shortcut falsifier.** For a
correct-orphan start at phase i, the remaining attempts satisfy pathwise
\(\tau/m=N_{\rm path}-i/m\). Therefore
\[
N(s,i)=H_0(s,i)+i/m.                                   \tag{15}
\]
The phase-only term is annihilated by R, including the wrap to phase zero.
Consequently the contribution of the baseline in (12) to the entire word is
\[
e_CGR\{\beta N\}=\beta H_1(C,0).                       \tag{16}
\]
It is not generally zero. At an aligned live final turn,
\(O D_2=0\) but \(O H_2=\beta\). Hence replacing H2 by D2 *inside O*, or
killing at the first aligned interior phase, deletes a real contribution.
[shortcuts.csv](shortcuts.csv) records the exact fingerprints and rounded
size of (16), as well as the resulting incorrect RORR value.

## The first R and its acceptance factor

**New candidate assembly.** Just before the first R, the clean population
is C or A_n, with a correct orphan. Write the recipient-restricted kernels
as \(R=P_R^+-P_R^0\). Each is stochastic. For \(P_R^+\), an accepted
overwrite \(k\leftarrow x\) has positive probability
\(d(s_i,x)a\), \(a=d(x,k)\). The remaining unchanged branch has
nonnegative mass at most one and is still unmarked.

Keep the factor a when applying (13), and only then sum each mutation row:
\[
\begin{aligned}
P_R^+|J|
&\le U+138m^2L^2
 \sum_{k\in B_2(i),\ k<n}\sum_x d(s_i,x)(aL^2+1)\\
&\le U+276m^2L^2(L^2+1)
 \le690m^2L^4.
\end{aligned}                                         \tag{17}
\]
At most two recipients appear. The parent may depend on previous clean
repairs; its fresh conditional mutation row still sums to one. There is no
assumed law for a parent conditional on a retained observation.

The restricted clean kernel only deletes the original corner error, so
\(P_R^0|J|\le U\). Equations (17) and (14) prove the proposed phasewise bound
\[
|R_iJ|\le828m^2L^4\le1024m^2L^4.                      \tag{18}
\]
This keeps both signed kernels and thus all suppressed-clean and unchanged
terms. The accepted diagonal x=s_k can harmlessly be included in (17);
it is part of the positive stochastic kernel, not an additional insertion.

Before any insertion, the only possible regular error is the original
corner. Its per-sweep repair probability is q, and killing occurs at the
boundary, so the total expected clean attempt count is exactly \(m/q\).
Multiplying (18) by that occupation mass proves the candidate (1).
Finally \(m\le2n\), \(q\ge d(1,0)\ge1/(3n)\), and \(L=20n\) give
\(1024m^3L^4/q\le3,932,160,000 n^8<4\cdot10^9n^8\).
Attempts multiply the word coefficient and its bound by m; initialization
is zero in this supplied-state model.

**Equivalent joint entrance check.** The two retained factors can also be
seen in a single inequality, before either positive branch is summed. For
a marked s with correct orphan and y<n, (6)-(8) give
\[
\begin{aligned}
&a c_y\bigl(|H_2(s^{n\leftarrow y},0)|+|H_2(s,0)|\bigr)\\
&\qquad\le d(n,y)\{10a m^2L^2+
             128m^2L d_y(aL^2+1)\}.                 \tag{19}
\end{aligned}
\]
The right side has neither 1/a nor 1/d_y. The second absolute value pays
the negative unchanged O branch. [joint.csv](joint.csv) checks (19) for
every positive orphan birth and every first regular mark in the finite grid.

## Verification, scope, and remaining audit

**Mechanically checked.** [rorr.py](rorr.py) sums ordered insertion placements
in unrestricted sweep/suffix products and solves clean boundary equations
by error deletion. It imports no earlier solver for its answers. The
published round-14 phase-equation implementation is a separate comparator.
A second recurrence with custom attempt rewards checks (12), (15) and (16).
[test_rorr.py](test_rorr.py) independently uses literal genotype masks and
pinned scalarization comparisons to check transition rows and the shared
observation split. All equalities and inequalities use rational arithmetic;
decimal fields are presentation only.

The grid includes every regular target, every child weight, both C and A_n
origins, every orphan value and every phase for the declared n=4,6 family.
It is not exhaustive over arbitrary populations and does not prove (1).
Separate positive active/clean expectation checks test (17)-(18), so a
small signed final answer alone cannot hide a large omitted branch.
See [verification.json](verification.json) and [README.md](README.md).

**Dependencies.** The full round-18 replay verifies the marked premise's
published outputs and recursively replays the relevant earlier registration,
receipts, seed separation and proof checks. Artifact hashes are checked
before use. The new independent comparator's source manifest and the earlier
n=4 RORR fingerprint are also checked. [dependency.json](dependency.json)
records what was actually replayed. Published receipts suffice; private
earlier trial logs are unavailable, so chronology retains that limitation.
No new stochastic measurement is conducted. A new experiment would require
a plan committed in a prior round and independent seeds.

**Remaining independent audit:** (7)-(12)'s baseline integration, the all-phase
orphan-turn count, use of the marked family after the first insertion,
and (17)'s positive-kernel accounting. These are the new steps carrying (1).
The round-18 marked lemma is already audited; this checkpoint does not
silently upgrade the complete fourth-order gap from conjecture to theorem.

**Falsifiers.** A mismatch of the two exact RORR solvers; a missing c_y or a;
a marked clean descendant outside the good family; violation of (4)-(6);
failure of (10), (12) or (15) at any phase; a nonzero row sum incorrectly
used to kill a phase function; an omitted negative branch; or a coefficient
above (1) would invalidate the associated step. The nonzero term (16)
already falsifies the baseline-deletion shortcut. Earlier exponential
positive-residence counterexamples remain valid and are not lower bounds
on this signed word.

**Unresolved in this checkout:** a full fourth-order gap bound, untreated
words such as RROR and RRRR, a useful uniform Taylor remainder, ordering at
fixed c with p=c/n, and ordinary initialization. No current-literature search
or novelty assertion is made in this offline work. The noiseless
radius/archive preprint discussed in the repository is not transferred to
this noisy pinned-cardinality process. The original preregistration, capped
trial, blocked 240-row holdout and inconclusive two-stage decision remain
unchanged.
