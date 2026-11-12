# Round 5: adversarial audit of the pinned-corner argument

**Proved under the process below:** the error-family comparison and empty-boundary
renewal step in the round-4 candidate proof are valid. Together with the audited
local, endpoint and lower-bound calculations, they establish the proposed
fixed-cardinality supplied-corner orders. This is an analytic conclusion; the
finite calculations below are falsification checks, not its proof. No
counterexample to the stated bounds was found.

**Contradicted:** expected completion time is universally nonincreasing in T,
even from this supplied corner. The exact transition certificates give a small
T=2 to T=3 slowdown. The previous candidate did not assert this monotonicity.

The input proof is the committed round-4 `proof.md` under
`research/reports/large-T-20261109/followup/round-0004`. Its empirical dependencies were
replayed before use; [dependency.json](dependency.json) records the receipts,
prior registration and preserved blocked holdout. The purported revised
fixed-c T=3 manuscript appendix is not an input to this proof. This offline
audit makes no literature-completeness or novelty claim.

## Process, information and cost

Fix n>=3, 1<=T<=n+1 and 0<=p<1/2. Each breeder i=0,...,n, in that order in
every sweep, mutates its own incumbent by independent rate-1/n bit mutation.
An independent Bernoulli(p) gate activates another such mask for observation.
All gates and masks are fresh. Write D(x,y) for the mutation weight kernel and
N(y,k)=(1-p)1{y=k}+pD(y,k).

The neighborhood B_T(i) has exactly T indices: start at i, alternate sides
(right first for even i, left first for odd i), skip out-of-range indices.
It is a filled cardinality, not a clipped symmetric radius. The observed
extrema are supplied as (0,n); stored labels are supplied as b_k=k. Since
C_k(b)=max{k(n-b),(n-k)b} has its unique minimum at k, a proposal with true
weight y and observation k replaces only slot k, and only if k is a recipient.
The labels and extrema stay pinned. The true weights need not stay correct.

Let F_t reveal the initial state and all consumed randomness through attempt t;
no future random choices are revealed. G_s=F_{(n+1)s} is boundary information.
For the corner w=(2,1,2,...,n), define tau_0 as the first boundary with w_0=0,
and tau as the first boundary with all w_k=k. Both include boundary zero.
The initial corner is supplied at zero evaluation cost. The cost is (n+1)tau
attempts. These are neither first correctness during a sweep nor archive hits.
The process may be continued after its first hit for analytical purposes.

Put I_k={i:k in B_T(i)}, d_k=|I_k|, a=p/(1-2p), beta=(T-1)a,
A=(n+1)Ta, and A_plus=((n+1)T-d_0)a. We use d_k<=2T-1 and, for T>=2,
0,1 in I_0. These statements do not require reciprocal neighborhoods.

## Conditioning and stopping audit

**Proved.** The isolated pinned chain at k has off-diagonal transition
Q_k(x,y)=D(x,y)N(y,k). Its first hitting expectation h_k(x), with h_k(k)=0,
is finite: the clean one-turn hit probability has a positive minimum over
the finite weight space. Its first-step equation is therefore legitimate.
For x!=k, the potential v(x)=1/D(x,k), v(k)=0 has expected decrease at least
N(k,k)-p sum_{y!=k}D(x,y)>=1-2p. This follows by expanding v(x)-E[v(X')]:
the direct hit contributes N(k,k), and dropping the other positive terms
leaves losses at most pD(x,y) per y. Stopping at the local hit truncated at m,
then using monotone convergence for the time, proves

h_k(x) <= 1/[(1-2p)D(x,k)],

N(x,k)h_k(x) <= a,

sum_y D(z,y)N(y,k)h_k(y) <= a for every parent z.                 (1)

The last inequality is conditional on the history **before** drawing a new
proposal. It is not conditional on acceptance or on a retained observation.
An external replacement increases expected potential by at most a; subtracting
the incumbent potential on acceptance only reduces the increase. A wrong own
turn has exact drift -1; a correct own turn injects at most a.

For a bounded boundary stopping time sigma, 1{s<sigma} is G_s-measurable.
Thus it is known before every attempt in sweep s+1. Summing these conditional
drifts gives, from w_1=1,

E B_1(sigma) <= d_1 a E sigma,                                  (2)

where B_1 counts wrong donor-1 states immediately before its own turns.
For all pre-attempt occupation O_1, split time into intervals between successive
own turns. A wrong pre-attempt state can be charged to an initially wrong own
turn or an erroneous replacement since that turn. The initial partial interval
starts correct; the final partial interval only shortens a charge. Therefore
O_1 <= (n+1)(B_1+C_1), where C_1 counts erroneous replacements, including
wrong-to-wrong replacements. Each requires an active gate at an eligible
breeder, so E C_1<=d_1 p E sigma. Truncating sigma first extends both bounds
to integrable sigma without interchanging an unbounded terminal potential.

For endpoint repair, count a sweep only if tau_0 has not occurred at its start.
Immediately before breeder 1, the event w_1=1 is measurable. Conditional on
that history, a clean mutation 1->0 and inactive gates at all d_0-2 later
eligible donors has probability

q_star=(1-p)^(d_0-1)D(1,0).

It forces endpoint correctness at the boundary. Conditioning instead on the
completed sweep, or merely on a retained observation, would invalidate this
hazard calculation. The event uses the gate at breeder 1 as well as the later
gates; it does not cover an earlier repair at breeder 0 by assuming persistence.
In sweeps before tau_0 wedge m, the number of these designated successes is at
most one, so q_star E G<=1. With G+B=tau_0 wedge m and (2),

E tau_0 <= B_0=1/[(1-d_1 a)q_star]                               (3)

when d_1 a<1. The truncation establishes integrability rather than assuming it.
Summing non-endpoint injection and dropping negative drift, then applying
Fatou, also gives E H_plus(tau_0)<=A_plus E tau_0, where
H_plus=sum_{k=1}^n h_k(w_k). Alone this does not prove simultaneous correctness.

## Proved comparison lemma: the tagged forest

For any deterministic pinned boundary state w, write H=sum_k h_k(w_k).
If beta<1, the following uniform expectation bound holds:

E_w tau <= C H,

C=(1-beta)^(-1) exp{A/[(1-beta)(1-p)]}.                          (4)

**Construction and filtration.** Give each initial wrong slot one particle
(site k, true weight w_k), tagged to represent it. Each possible immigrant is
identified by (sweep, breeder); every possible descendant receives a unique
genealogical address. Attach mutually independent infinite random tapes to
these countably many addresses. Reveal only the next tape entry when a
particle is actually processed. This avoids dependence from reused identities.
Tags are bookkeeping and never affect a family's evolution.

At breeder i, snapshot all particles already at site i. Generate one independent
base proposal from true weight i, even if the actual incumbent is wrong. Each
particle in the snapshot makes its own proposal from its current weight.
Its own state follows Q_i; on a clean own hit it dies. An erroneous accepted
proposal to an external k creates a child (k,y) while the parent remains.
An erroneous own acceptance changes that particle; it creates no extra child.
The base proposal creates a new family root precisely on an erroneous accepted
proposal, including a root at i. Such a new own-site root waits until the next
sweep. Children at later breeders may act in this sweep; children at earlier
breeders wait. There are finitely many particles at every finite attempt:
a turn with M particles creates at most M+1 new ones and there are finitely
many turns. This establishes existence without assuming eventual extinction.

Before revealing any of these proposals, select the tagged particle's proposal
if the actual breeder is wrong, otherwise the base proposal. The selected
parent weight equals the actual incumbent. Given the entire enlarged past,
its unrevealed randomness is independent and has exactly the original kernel.
Choosing it this way preserves the actual process's conditional transition law;
conditioning afterward on which sources were selected would not preserve
independence of their histories.

Use the selected proposal to update the actual recipient. A clean accepted
proposal removes that recipient's tag. An erroneous own acceptance retains
the selected particle's tag; an erroneous external acceptance uses its new
child's tag; a selected base error uses its new root's tag. An old recipient
particle is not killed by external updates: it becomes untagged. Induction
therefore proves that every wrong actual slot has exactly one live matching
tag, while all correct slots have none. **Forest emptiness implies actual
alignment; actual alignment does not imply forest emptiness.**

**Work bound with dependence allowed.** A particle born with potential h has
mean lifetime h in its own turns. At each live turn, (1) bounds expected total
external-child initial potential by beta. Liveness is determined before that
turn's fresh draw. Summing over truncated lifetimes and using Tonelli gives
expected total child potential at most beta h. A child's future tape is fresh
conditional on its birth state. Iterating by genealogical generation shows
that expected total particle work W in one family is at most h/(1-beta).
No independence between a parent's lifetime and its offspring is required.
In particular W is finite almost surely.

A family alive at a boundary has a particle which will be processed in the
next sweep; other particles cannot externally delete it. Charge that boundary
to such a next-sweep particle turn. Different boundaries have disjoint charges.
A family cannot reappear after extinction. Consequently the number of its
occupied boundaries is at most W, including births acting later in their birth
sweep. For the initial collection, its extinction boundary L_0 obeys
E L_0<=H/(1-beta). A base root has probability at most p of existing and expected
initial potential at most Ta. Thus all n+1 base sources in one sweep generate
expected future work at most A/(1-beta).

## Proved renewal lemma, including the unbounded stopping step

Let u_{i,r} be the probability that the family of base source i in sweep 1
is alive at boundary r. The construction above gives
u_{i,r}<=p and sum_{i,r>=1}u_{i,r}<=A/(1-beta).
Entire families, including the unused base families, are independent. Cyclic
phase is identical at corresponding boundaries. For a forest started empty,

q_s=Pr(empty at s)=product_i product_{r=1}^s (1-u_{i,r}), q_0=1,

q_inf=lim_s q_s >= exp{-A/[(1-beta)(1-p)]}>0.                    (5)

The product uses unconditional, artificial family laws. It must not be replaced
by an independence assertion about the actual population's coordinates.
The logarithm bound is log(1-u)>=-u/(1-p) for 0<=u<=p<1.

The initial families are independent of immigration. Let rho be the first
empty boundary of the full forest, including zero. Then

e_s=Pr(empty at s)=Pr(L_0<=s)q_s.

For every deterministic r, on {rho=r} no old family survives and all future
tapes are fresh. Summing over r<=s gives e_s=sum_{r=0}^s Pr(rho=r)q_{s-r}.
This argument does not presuppose finite rho or E rho. Put
Q(z)=sum q_s z^s, F(z)=sum Pr(rho=s)z^s for 0<=z<1. Nonnegative series yield

1-F(z) = [sum_{s>=0} Pr(L_0>s)q_s z^s]/Q(z).

The numerator is at most E L_0; Q(z)>=q_inf/(1-z). Taking z up to 1 first
shows Pr(rho<infinity)=1. Since (1-z)Q(z)->q_inf and the numerator increases
to its finite total, one obtains the stronger exact identity

E rho = [sum_{s>=0} Pr(L_0>s)q_s]/q_inf <= E L_0/q_inf.          (6)

This is a renewal argument, not a maximum-of-means argument and not a geometric
tail assertion. Since tau<=rho under the coupling, (4) follows. If H=0,
tau=rho=0; it is not a positive return-time bound.

## Restart, lower bound and fixed-T conclusion

At tau_0, use the original boundary filtration and **start a new comparison
forest** from the actual population. Do not condition the old forest's families
on the event tau_0. Future actual randomness has its original law, and (4) is
uniform over deterministic initial states, so conditional application gives

E tau <= B_0(1+C A_plus).                                     (7)

This also handles tau=tau_0. No independence between the endpoint time and
the remaining potential is assumed.

For the lower bound put J=union_{k in I_0} I_k. At a deterministic horizon s,
force the gates in J inactive during all s sweeps, an event of probability
(1-p)^(|J|s). Mutation masks remain independent under this conditioning.
Before the first repair every eligible donor keeps its supplied weight:
all its incoming replacements are clean and can only put its target in it;
slot 0 stays at weight 2 until its first target observation. Thus the
conditional probability of no repair is (1-q_T)^s, where
q_T=1-product_{i in I_0}(1-D(w_i,0)). This event implies tau>s and yields

E tau >= 1/[1-(1-p)^|J|(1-q_T)].                               (8)

For fixed c>0,T>=2 and p=c/n, beta<1 and d_1 a<1 eventually,
B_0~en, A_plus->cT, C->exp(cT), q_T~1/(en), and |J|=O(T^2).
Consequently (7)-(8) prove **Theta_{c,T}(n^2) attempts** from the supplied corner.
For T=1 the endpoint is autonomous. Its first departure from weight 2 has
probability at most D(2,0)+p(D squared)(2,0), while (1) bounds h_0(2) above by
1/[(1-2p)D(2,0)]. The composed flip rate is 2(1/n)(1-1/n), so both bounds
are asymptotic to en^2 own turns. Applying (4) with beta=0 yields
**Theta_c(n^3) simultaneous attempts**, and the endpoint's first boundary
repair alone is asymptotic to en^3 attempts.

The round-4 candidate proof therefore survives this audit. The additional
explicit details needed for a formal write-up are unique genealogical tapes,
pre-draw source selection, the boundary charge, and fresh-forest restart.
None changes its model or displayed bounds.

## Counterexamples and finite falsification checks

**Mechanically checked with exact certificates.** [audit.py](audit.py) builds
literal bit-mask kernels and scalarization updates at every population for
n=2,3. It tests 25 (n,T,p) cells: all T, p in {0,1/(64n),1/(4n)}, and also
p=1/3 at n=3. The n=2 cases are diagnostics outside the theorem's n>=3 scope.
There are 4,339 population/cell combinations and 17,113 phase transition rows.
The theorem's sufficient conditions are enforced; the high-noise T>=2 cases
at n=3 are not counted as tests of its upper bound.

For each cell, floating solves propose rational vectors. Exact integer sweep
propagation then certifies them. If v=0 on a boundary target and
0<d_min<=v-Pv<=d_max elsewhere, finite stopped telescoping proves
v/d_max<=E tau<=v/d_min. Positive drift proves finite expectation first.
Occupation certificates bound their exact Bellman residual in absolute value
by epsilon, giving error at most epsilon E tau_0. Targets are killed only at
boundaries: transitions out of aligned mid-sweep states remain in P.
Zero-noise equality cases use an exact potential supersolution and donor
persistence instead of insisting a rounded interval separate an equality.
The largest corner-time interval width is below 1.84e-9 sweeps.

The checks pass 3,571 arbitrary-state simultaneous inequalities, 1,644 stopped
occupation inequalities, 15 endpoint upper bounds, 15 corner upper bounds,
and 18 lower-bound compatibility checks (zero-noise equalities are contained
in the certified interval). [certificates.csv](certificates.csv) and
[expectations.csv](expectations.csv) retain every input vector and exact bound;
[verify.py](verify.py) checks them without numerical solves or NumPy.

At n=3,p=1/192 the supplied-corner expectations in sweeps are:

| T | First endpoint-correct boundary | First simultaneously correct boundary |
|---:|---:|---:|
| 1 | 13.5313354985 | 13.5674832781 |
| 2 | 4.7506796384 | 4.7659580192 |
| 3 | 4.7515449512 | 4.7671266818 |
| 4 | 3.3808250225 | 3.3968507356 |

These are deterministically certified values, not sampled means or confidence
intervals. T=3 minus T=2 is in a strictly positive rational interval around
0.001168662645 sweeps (multiply by 4 for attempts). Both have I_0={0,1}.
This refutes universal nonincreasing expected corner time in T. It also shows
that the noiseless equality of T=2 and T=3 does not persist with noise.
It says nothing about the expectation ordering from ordinary initialization.

**Contradicted conditioning shortcut.** With n=3,p=1/192, parent weight 2 and
accepted observation 0, the posterior probability of a wrong true child is
32/5197, strictly greater than p. Acceptance has probability 5197/69984;
wrong-and-accepted has probability 1/2187. Round 4 uses (1) before acceptance,
so this witness does not invalidate it.

**Contradicted boundary shortcut.** The independently enumerated positive-mass
path in [verification.json](verification.json) starts from the n=3,T=2 corner,
becomes fully correct during its first sweep and ends with slot 1 wrong while
slot 0 is correct. Thus neither interior-time alignment nor endpoint boundary
repair is interchangeable with simultaneous boundary alignment.

**Mechanically checked bounded forest search.** [forest.py](forest.py) examines
242,064 transitions over three sweeps at n=2,T=1,2,3 from both the corner and
alignment. It retains at most two live particles; transitions exceeding the
cap are checked for tag correctness but not expanded. No tag failure occurs.
This is explicitly not exhaustive over unbounded forests. It includes ignored
base roots, externally untagged particles and within-sweep descendants.
[forest.json](forest.json) records counts and pruning. General validity rests
on the induction and work/renewal proof above.

## Scope, proof gaps and falsifiers

**Proved only for the stated pinned process.** There is no remaining identified
logical gap in the fixed-c, fixed-T supplied-corner proof after this audit.
This does not upgrade a fitted empirical law to a theorem. Before labels are
pinned, one proposal can change several labels/slots; the forest above does
not model that phase. Ordinary-initialization runtime, corner-entry frequency,
uniform growing-T behavior, tail bounds, and causal explanations of the
observed pre-S savings remain unresolved by these results. Their global
literature status is not assessed in this offline turn.

A valid tagged transition losing a wrong slot's particle, family evolution
requiring another family's tape, a failure of the no-gap boundary charge,
or an exact expectation above a finite bound under its conditions would
falsify this proof. A posterior bound conditioned on acceptance, a geometric
noisy hitting law, and expected monotonicity in T are deliberately not premises.
All scientific trajectories in this round number zero: no new seeds or
experiment plan were needed for these deterministic mathematical checks.
