# Fixed-cardinality noisy corner: candidate proof

**Status: candidate proof, with complete proposed argument and finite mechanical
checks; not independently reviewed.** The local lemmas below are proved by the
displayed calculations. The new extension is the error-particle coupling and
its renewal argument in Sections 5–6. Those are the priority for adversarial
review. Finite checks cannot certify an infinite family of stochastic processes.
No novelty claim or new empirical measurement is made.

**Proposed conclusion.** For every fixed real (c>0) and integer (T\ge2),
the supplied, pinned single-corner process below has expected simultaneous
boundary-alignment cost (\Theta_{c,T}(n^2)) offspring attempts. At (T=1),
the same supplied state has (\Theta_c(n^3)) expected simultaneous cost; its
endpoint's first repair alone is asymptotic to (e n^3) attempts. These are
supplied-state statements, not runtime laws from ordinary initialization.

The proof also bounds donor 1's time at an incorrect weight. Over any integrable
boundary stopping time (\sigma), starting with donor 1 correct,

\[
 E B_1(\sigma)\le d_1\frac p{1-2p}E\sigma,
 \qquad
 E\frac{O_1(\sigma)}{n+1}
 \le d_1\left(\frac p{1-2p}+p\right)E\sigma.                 \tag{1}
\]

Here (B_1) counts incorrect **pre-own-turn** states, (O_1) counts incorrect
states before **all individual attempts**, and (d_1) is the number of
breeders that can replace slot 1. Thus over (O(n)) expected sweeps, donor 1
spends (O_{c,T}(1)) expected sweep-equivalents incorrect, or (O_{c,T}(n))
attempt-times. This is an occupation bound, not a bound on a conditional
probability given a retained noisy observation.

## 1. Exact process and information

Take (n\ge3), (1\le T\le n+1), standard independent per-bit mutation at
rate (1/n), and observation kernel

\[
 D(i,j)=\Pr(|\operatorname{mut}(x)|=j\mid |x|=i),\qquad
 N(j,k)=(1-p)\mathbf1_{j=k}+pD(j,k).
\]

The activation gate and mutation/noise masks are fresh and independent at each
attempt. Set (p=c/n) for the asymptotic conclusions, and restrict finite
bounds to (0\le p<1/2). Breeders (0,1,\ldots,n) occur in that order,
repeatedly; each mutates its **own** current incumbent. (B_T(i)) is the
implemented filled-cardinality neighborhood: start at (i), alternate sides
(right first for even (i), left first for odd (i)), skip indices outside
([0,n]), and stop at exactly (T) recipients. This is not a clipped radius.

Supply ideal observed extrema (0,n), stored labels (b_k=k), true weights
(w_0=2,w_k=k\ (k\ge1)), and zero initialization evaluations. The cost
(C_k(b)=\max\{k(n-b),(n-k)b\}) has unique minimizer (b=k).
Consequently every observation is accepted by at most its own target slot:
an attempt from (i), with true child (j) and observation (k), replaces
slot (k) by true weight (j) iff (k\in B_T(i)). Labels and extrema remain
pinned forever. Accepted noise can change true weights arbitrarily; true
correctness is not absorbing.

Let (\mathcal F_t) contain the supplied state and all masks/gates consumed
through attempt (t), together with the deterministic breeder phase. No future
mask is revealed. Write (\mathcal G_s=\mathcal F_{(n+1)s}) for boundary
information. Define

\[
 \tau_0=\inf\{s\ge0:w_0((n+1)s)=0\},\qquad
 \tau=\inf\{s\ge0:\forall k,\ w_k((n+1)s)=k\}.
\]

Both are boundary stopping times; neither is archive coverage. Offspring
attempt cost is exactly ((n+1)\tau). The process can be continued after either
event for analysis. All stopped calculations first use (\sigma\wedge m)
and then nonnegative convergence/Fatou as specified below.

Put

\[
 I_k=\{i:k\in B_T(i)\},\quad d_k=|I_k|,\quad
 a=\frac p{1-2p},\quad \beta=(T-1)a,\quad A=(n+1)Ta.
\]

Every (I_k\subseteq[k-T+1,k+T-1]\cap[0,n]), hence (d_k\le2T-1).
For (T\ge2), (0,1\in I_0); let (L=d_0-2), the eligible breeders after
donor 1. No reciprocity assumption is used, including for even (T).

## 2. Local repair and a uniform injection bound

**Proved, rederived here.** For a fixed slot (k), let (Q_k) be the
own-turn chain that accepts only observation (k): for (i\ne j),

\[
 Q_k(i,j)=D(i,j)N(j,k),\quad
 Q_k(i,i)=1-\sum_{j\ne i}Q_k(i,j).
\]

Let (h_k(i)) be its expected first hitting time of (k) in local turns,
with (h_k(k)=0). This chain has finite hitting times: from every weight,
one clean mutation reaches (k) with positive probability, whose minimum
over the finite state space is positive. Therefore its first-step equation is

\[
 E[h_k(X')-h_k(i)\mid X=i]=-1\quad(i\ne k).                \tag{2}
\]

For (v(k)=0,v(i)=1/D(i,k)), a wrong own-turn has expected decrease at least

\[
 N(k,k)-p\sum_{j\ne k}D(i,j)\ge1-2p.
\]

Indeed the direct repair contributes (N(k,k)), each negative retained
potential term is at most (pD(i,j)), and omitted terms are nonnegative.
Summing this drift until the local hit, with finite truncation, gives

\[
 h_k(j)\le\frac1{(1-2p)D(j,k)}\quad(j\ne k),\qquad
 N(j,k)h_k(j)\le a.                                       \tag{3}
\]

For an arbitrary parent weight (x), independent fresh mutation/noise imply

\[
 \sum_jD(x,j)N(j,k)h_k(j)\le a.                           \tag{4}
\]

This is a bound **before observing or accepting** the proposal. It holds for
every parent and every history. An external proposal to (k) therefore
increases expected (h_k) by at most (a), since subtracting the old
potential on accepted proposals can only improve this bound. A correct own
turn also creates at most (a). A wrong own turn has exact decrease one.

The local manuscript's Lemma 9 supplies a stronger composed-mutation bound;
(3) suffices here and is proved independently. The local PDFs contain the
small-constant (T=1) results, not the revised fixed-(c), (T=3) appendix
described in the theory note. That unprovided result is not a premise.

## 3. Donor 1 occupation, without conditioning on accepted noise

**Proved.** For any bounded boundary stopping time (\sigma), sum the
conditional drifts of (h_1(w_1)) over the (d_1\sigma) eligible attempts.
The own-turn drift is at most (-\mathbf1_{w_1\ne1}+a); all other eligible
turns contribute at most (a). Since (h_1(w_1(0))=0) and final potential
is nonnegative,

\[
 E B_1(\sigma)\le d_1a E\sigma.                           \tag{5}
\]

This extends to integrable (\sigma) by applying it to (\sigma\wedge m).
No expected potential at an unbounded time is silently interchanged.

For the all-attempt occupation (O_1), partition time into intervals from
one pre-own-turn state to the next. Each interval contains (n+1) attempt
states. An incorrect state in such an interval is covered either by an
incorrect initial pre-own-turn state, or by an accepted erroneous observation
since that turn. The initial partial interval starts correct. Let (C_1)
count accepted erroneous replacements of slot 1, including wrong-to-wrong
replacements. Each needs an active gate at an eligible breeder. Pathwise,

\[
 O_1(\sigma)\le(n+1)\{B_1(\sigma)+C_1(\sigma)\},\qquad
 E C_1(\sigma)\le d_1p E\sigma.
\]

This proves (1). It does not assert that donor 1 is always correct. For
example, at (n=3,T=3), its true child 0 observed as 1 corrupts it, with
positive probability (D(1,0)pD(0,1)).

## 4. First endpoint boundary repair

**Proved.** Assume (T\ge2) and (d_1a<1). At the instant before donor 1's
turn in an unfinished sweep, if it is correct, the event

* donor 1 mutates weight 1 to 0 with its noise gate inactive; and
* all (L) later eligible donors have inactive gates

has conditional probability

\[
 q_*=(1-p)^{L+1}D(1,0),\qquad
 D(1,0)=\frac1n(1-1/n)^{n-1}.                             \tag{6}
\]

It ensures (w_0=0) at the boundary, regardless of the other coordinates.
Clean later replacements cannot corrupt a pinned target. The relevant future
gates are independent of the history through donor 1. This explicitly accounts
for the published (n=6,T=5) reinfection path; it does not assume persistence.

Before (\tau_0\wedge m), let (G) and (B) count good and bad donor 1
visits. A designated success above can occur at most once among these active
sweeps, since it forces stopping at that sweep's boundary. Conditional
expectation gives (q_*E G\le1), while (5) gives
(E B\le d_1a E(\tau_0\wedge m)). Since (G+B=\tau_0\wedge m),

\[
 E\tau_0\le B_0:=\frac1{(1-d_1a)q_*}.                    \tag{7}
\]

For fixed (c,T), (B_0\sim en) sweeps. This is an **upper bound**, not a
claim that the actual noisy expectation has asymptotic constant (e).
Equation (5) consequently bounds incorrect donor 1 own turns before this
endpoint hit by (d_1aB_0=O_{c,T}(1)).

Let (H_+=\sum_{k=1}^nh_k(w_k)). It starts at zero. Summing (4) over all
recipients other than 0, dropping negative drift, and stopping first at
(\tau_0\wedge m), gives by Fatou

\[
 E H_+(\tau_0)\le A_+E\tau_0,\qquad
 A_+=\big((n+1)T-d_0\big)a\le A.                         \tag{8}
\]

This controls remaining repair work, but does not alone imply simultaneous
correctness. The next construction supplies that step for every fixed (c).

## 5. Candidate construction: independent families of error particles

Start from any pinned population at a boundary. For each wrong slot (k)
with weight (j), place one particle ((k,j)) and tag it as representing that
actual incumbent. Correct slots have no tag. Untagged particles are retained.

At breeder (i)'s turn, do the following in an enlarged probability space.

1. Always draw one **base proposal** from true weight (i).
2. For every particle already at (i) before this turn, draw an independent
   proposal from that particle's weight. A particle's own state follows
   (Q_i), and it dies when its true weight becomes (i).
3. Whenever a particle's proposal is accepted with an erroneous observation
   at an external target (k\in B_T(i)\setminus\{i\}), create a child
   particle at ((k,j)). Keep the parent. A wrong accepted own proposal is
   its existing (Q_i) transition, not a new child.
4. The base proposal creates a new family root at its accepted target if
   true and observed weights differ. It creates no particle on a clean
   acceptance. Base roots at their own site are not processed again this turn.
5. Use the proposal of the tagged particle as the actual algorithm's proposal
   if its breeder is wrong, and the base proposal if it is correct. Clean
   accepted offspring erase the recipient's tag; an erroneous accepted
   offspring tags its corresponding new child/root (or retained own particle).

Particles born at later breeders may act later in this same sweep; those
born at already visited breeders wait until the next sweep. All existing
particles act once at their scheduled turn. All proposal selection decisions
are made before revealing those proposals. Thus the selected actual proposal
has exactly the original fresh conditional law. By induction every actual
wrong slot has a live matching tagged particle. An empty forest at a boundary
therefore implies true population alignment. The converse is not needed.

Each family evolves without reference to tags or to any other family.
Every base source, sweep, and descendant has independent fresh randomness.
Consequently distinct families are independent even though the actual tagged
population has dependent coordinates. At any finite time there are finitely
many particles: each particle can create at most one external child per turn,
and there are finitely many base proposals. These facts define the enlarged
process without an infinite-update problem.

**Proved estimates conditional on this coupling.** A particle born at
((k,j)) has expected lifetime (h_k(j)) own turns. By (4), the expected sum
of the (h)-values of external children created at each of its turns is at
most \(\beta=(T-1)a\). Summing over its stopped lifetime bounds total child
initial potential by \(\beta h_k(j)\). Correlation between a parent's lifetime
and its children is allowed; only fresh-turn conditional bounds are used.

Iterating by generations and using Tonelli, if \(\beta<1\), a root of initial
potential (h) has expected total family work (all particle own turns)

\[
 E W\le h(1+\beta+\beta^2+\cdots)=\frac h{1-\beta}.       \tag{9}
\]

Each boundary occupied by a family can be charged to a distinct particle turn
in the following sweep: some particle present at that boundary has its next
own turn then. Hence the number of occupied boundaries is at most its total
work. This also bounds the extinction boundary of initial families by their
total work. No tail assumption on a particle lifetime is needed.

A base proposal creates a root only if its noise gate activates, so its
probability of creating a root is at most (p). Its expected initial root
potential is at most (Ta), by summing (4) over its (T) possible targets.
All (n+1) base sources in one sweep therefore create expected total family
work at most (A/(1-\beta)).

## 6. Candidate renewal step: waiting for the entire forest to be empty

Here the needed renewal inequality is derived explicitly. Let (u_{i,r})
be the probability that the family initiated by base source (i) in sweep 1
is alive at boundary (r\ge1), including the possibility that no root was
born. A family cannot reappear after extinction. Section 5 implies

\[
 u_{i,r}\le p,\qquad
 \sum_i\sum_{r\ge1}u_{i,r}\le\frac A{1-\beta}.
\]

Let (q_s) be the probability that the forest with **only base immigration**,
started empty, is empty again at boundary (s). Independence of families
and the same cyclic phase in every sweep give

\[
 q_0=1,\quad q_s=\prod_{i=0}^n\prod_{r=1}^s(1-u_{i,r}),\quad
 q_\infty\ge\exp\left(-\frac A{(1-\beta)(1-p)}\right)>0.  \tag{10}
\]

The inequality uses (\log(1-u)\ge-u/(1-p)) for (0\le u\le p<1).

Let (L_0) be the extinction boundary of the initial families, independently
of all base families, and let (\rho) be the first empty boundary of the whole
forest. With initial total potential (H=\sum_kh_k(w_k)), (9) gives
(EL_0\le H/(1-\beta)). For (s\ge0),

\[
 e_s:=\Pr(\text{whole forest empty at }s)=\Pr(L_0\le s)q_s.
\]

At an empty boundary the future forest restarts from the same empty state
and breeder phase, using fresh randomness. Thus, writing (f_s=\Pr(\rho=s)),

\[
 e_s=\sum_{r=0}^s f_r q_{s-r}.
\]

For (0\le z<1) put (Q(z)=\sum q_sz^s) and (F(z)=\sum f_sz^s).
Subtracting the generating-function identity yields

\[
 1-F(z)=\frac{\sum_{s\ge0}\Pr(L_0>s)q_sz^s}{Q(z)}
 \le \frac{EL_0(1-z)}{q_\infty}.
\]

First let (z\uparrow1) to obtain (\Pr(\rho<\infty)=1); then use
((1-F(z))/(1-z)=E\sum_{r=0}^{\rho-1}z^r) and monotone convergence. Hence

\[
 E\tau\le E\rho\le C H,\qquad
 C=\frac1{1-\beta}\exp\left(\frac A{(1-\beta)(1-p)}\right). \tag{11}
\]

This proves the proposed arbitrary-pinned-state upper bound, provided the
coupling in Section 5 is valid. It does not infer a bound for a maximum from
individual means: it uses total family work and an explicit renewal identity.
Finite exact checks of that identity appear in [verification.json](verification.json).

## 7. Combining the bounds and a matching order lower bound

**Candidate fixed-(T) theorem.** At (\tau_0), slot 0 has zero potential.
Apply (11) to the remaining state using fresh future randomness, then (8):

\[
 \boxed{E\tau\le B_0(1+C A_+)}.                          \tag{12}
\]

The finite sufficient conditions are (p<1/2,\ \beta<1,\ d_1a<1), in
addition to the exact process in Section 1. They all hold for fixed (c,T)
and sufficiently large (n). Since (A_+\to cT), (C\to e^{cT}), and
(B_0/n\to e), the explicit proposed upper bound gives

\[
 \limsup_{n\to\infty}\frac{E\tau}{n}
 \le e\big(1+cT e^{cT}\big).                             \tag{13}
\]

This constant is loose; it is not a fitted or asserted limiting constant.

**Proved lower bound.** Let (J=\bigcup_{k\in I_0}I_k). At most
(d_0(2T-1)) breeders lie in (J). Force all gates at breeders in (J)
inactive for (s) sweeps. Before endpoint repair, the eligible donor weights
then remain at their supplied values, regardless of all other randomness:
every replacement into those slots is clean. Write

\[
 a_w=n^{-w}(1-1/n)^{n-w},\quad
 q_T=1-\prod_{i\in I_0}(1-a_{w_i}),\quad w_0=2,w_i=i\ (i>0).
\]

Conditional on those gates, the probability of no endpoint repair for (s)
sweeps is exactly ((1-q_T)^s). Therefore

\[
 \Pr(\tau>s)\ge[(1-p)^{|J|}(1-q_T)]^s,\qquad
 E\tau\ge\frac1{1-(1-p)^{|J|}(1-q_T)}.                  \tag{14}
\]

For fixed (T\ge2), (q_T\sim1/(en)) by the noiseless donor product, and
(|J|=O(T^2)). This gives (E\tau=\Omega_{c,T}(n)) sweeps. Combining (12)
and (14) yields the proposed \(\Theta_{c,T}(n^2)\) attempt theorem.

**Proved local (T=1) contrast; candidate simultaneous extension.** For
(T=1), the endpoint evolves autonomously as (Q_0). From weight 2 its
probability of leaving that weight in one turn is at most

\[
 D(2,0)+p(D^2)(2,0),\quad
 (D^2)(2,0)=r^2(1-r)^{n-2},\quad r=2n^{-1}(1-n^{-1}).
\]

The waiting time for that first departure is geometric and is a lower bound
on first repair. By (3),

\[
 \frac1{D(2,0)+p(D^2)(2,0)}\le h_0(2)
 \le\frac1{(1-2p)D(2,0)}.
\]

At (p=c/n), both sides are asymptotic to (en^2). Thus the first endpoint
repair costs (\sim en^3) attempts. For simultaneous correctness, (11) with
(T=1,\beta=0,H=h_0(2)) gives
(h_0(2)\le E\tau\le C h_0(2)), yielding the proposed cubic order for the
same corner. This says nothing about typical initialization or the legacy
one-bit-mutation model.

## 8. Exact review obligations, counterexamples, and scope

**Candidate-proof obligations.** No algebraic step is intentionally left as a
heuristic, but an independent reviewer must validate (a) the tagged-particle
coupling under ascending, within-sweep births; (b) the generation-work estimate
with parent/child dependence; (c) the independent-family product and empty-state
renewal at an unbounded stopping time; and (d) the strong-Markov use of (11)
after (\tau_0). These are the precise places an invalid extension could hide.
The full theorem remains a candidate until that audit. The finite checker
exhausts one-step couplings at (n=2), not all multi-sweep forests.

**Contradicted shortcuts.** Donor 1 is not persistent. Nor does an endpoint
repair imply boundary correctness: the published (n=6,T=5) path repairs 0 at
breeder 1 and reinfects it at breeder 2. Both witnesses are reproduced. The
proof avoids conditioning on acceptance, assuming coordinate independence,
claiming geometric noisy completion, or using a per-coordinate mean as a
maximum bound. The forest is an upper comparison, not the actual distribution.

**Falsifiers.** A valid tagged update leaving a wrong incumbent without a live
matching particle refutes the coupling. A kernel state violating (4), or a
family whose expected child potential exceeds \(\beta h\), breaks its work
bound. An exact finite-state expectation above (12), when its finite conditions
hold, refutes the proposed theorem. An exact noisy endpoint expectation above
(7) refutes the donor argument. An asymptotic sequence violating the orders
would refute the theorem, but a finite sampled slope would not.

**Remaining scope gaps.** No uniform result for growing (T) follows from the
constants, which can grow exponentially in (cT). No corner-entry frequency,
ordinary-initialization runtime improvement, monotonicity in (T), new tail
bound, or transfer to one-bit mutation/noise is claimed. The offline literature
state is the supplied repository comparison; no newer-work or novelty claim is
made. The stated (T=3) fixed-(c) theorem in the theory note was treated as a
hypothesis to recover, not an available proof dependency.

All new checks are deterministic: [code](check.py), [exact kernel values](kernels.csv),
[verification](verification.json), [tests](test_proof.py). Existing empirical
evidence and its preserved blocked holdout are summarized in
[dependency.json](dependency.json). These measurements do not prove (12).
