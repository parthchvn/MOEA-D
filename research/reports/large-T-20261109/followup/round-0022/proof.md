# Acceptance-weighted loss of the last correct slot

**Status: proved by the argument below for the specified process.** Exact
finite checks are separate corroboration. This is a first-moment workload
bound under ongoing noise, not a Taylor argument or a polynomial bound on
total completion time. No independent reviewer or novelty certification is
claimed.

## 1. Process, information and quantities

Let n>=2, m=n+1, and 1<=T<=m. Breeders 0,...,n act in ascending cyclic
order, each mutating its own incumbent with independent per-bit rate 1/n.
Write D(x,y) for the resulting weight kernel. Each offspring has one fresh
Bernoulli(p) activation gate and, if activated, an independent rate-1/n
observation mask. One observed weight is shared by all its recipients:

    N(y,k)=(1-p) 1{y=k}+pD(y,k).

The filled neighborhood is B_T(i)=[L_i,L_i+T-1], with

    L_i=max(0,min(i-floor((T-1)/2)-1{T even and i odd},m-T)).

This is the existing cardinality convention, including its directed boundary
edges. Let I_k={i:k in B_T(i)}, d_k=|I_k| and d_max=max_k d_k.
In particular d_max<=min(m,2T-1). No reciprocity is assumed.

After the ideal reference (0,n) and stored target labels b_k=k are pinned,
an observation k is accepted only by slot k, and only if k is a recipient.
The true child weight y is stored there. This follows from the unique minimum
of max{k(n-b),(n-k)b}. Noise can corrupt correct slots; labels/reference stay
pinned. Before full pinning we retain the moving reference and literal
non-worsening comparisons, with ties accepted, of the existing simulator.

F_t reveals initialization and the gates/masks consumed through attempt t.
The next breeder is a=t mod m. No future randomness is revealed. Let C_t
be the number of true correct slots, w_k=k. A *seed* means C_t>=1, not
archive coverage or completion. A reseeding excursion starts just after an
attempt leaves C_t=0 and ends at the first later attempt with C_t>=1.
Its length L counts subsequent offspring attempts, including the restoring
attempt, excluding the entrance attempt. These are interior stopping times
used only for analysis. The actual simultaneous completion event remains
an aligned full-sweep boundary.

The finite sufficient condition throughout the positive results is

    delta_k=1-(d_k+1)p>0 for every k;
    delta_min=1-(d_max+1)p>0.                         (1)

It implies p<1/2. All bounds below condition on histories **before** fresh
proposals. Conditional distributions given an accepted/stored value are
never replaced by fresh noise laws.

## 2. A phase-corrected potential that tolerates external overwrites

For a fixed slot k put v_k(k)=0 and v_k(y)=1/D(y,k) for y!=k. All D(y,k)
are positive. While k is wrong, its own turn has conditional drift at most
-(1-2p). To see this, its direct repair contributes -N(k,k); the positive
part of all wrong-child updates is at most

    sum_{y!=k} D(w_k,y) pD(y,k) v_k(y) <= p.

The old-potential subtraction on other accepted proposals only helps, and
N(k,k)>=1-p. At any external eligible turn, with any history-dependent
parent x, the drift is at most

    sum_{y!=k} D(x,y) pD(y,k) v_k(y)
      =p(1-D(x,k)) <= p.                             (2)

An ineligible turn has zero drift. This includes wrong-to-wrong overwrites;
other coordinates evolve normally. It is not a frozen-rest calculation.

Set b=1-2p. For next breeder a let r=(k-a) mod m, and let e_k(a) count
eligible external breeders in the r cyclic turns a,...,k-1 before the next
own turn. Define

    g_k(a)=r delta_k/m + p e_k(a).                    (3)

Then g_k(k)=0 and 0<=g_k(a)<=b. If z_k(a) equals -b on the own turn,
p on an eligible external turn, and zero otherwise, direct subtraction gives

    g_k(a+1)-g_k(a)+z_k(a)=-delta_k/m.               (4)

Here a+1 is modulo m. The maximum is immediately after the own turn:
g_k(k+1)=b-delta_k/m. Between own turns g decreases. The phase term pays
for waiting nearly a full sweep after a corruption at the own turn.

**Proved local repair bound.** From any pinned state with w_k!=k at phase a,
the expected attempts until k is first correct are at most

    Phi_k(w,a)=m/delta_k [1/D(w_k,k)+g_k(a)].         (5)

Use this nonnegative potential until that hit and set it to zero at the
hit. Killing removes a nonnegative g term. Equations (2)-(4) therefore give
conditional drift at most -1 on every live attempt. Summing up to the hit
or a deterministic H gives E[min(hit,H)]<=Phi_k(w,a); monotone convergence
proves finiteness and (5). No unbounded optional-stopping interchange is used.

If the entire population is unseeded, its first reseeding is no later than
this tracked-slot repair. Equivalently kill Phi as soon as any seed appears;
the extra killing only decreases the potential. Hence

    E[L | w,a] <= min_k Phi_k(w,a).                  (6)

This is an actual noisy-process bound. Donor weights may change, external
updates may overwrite the tracked slot, and the repair may occur mid-sweep.
The bound can be enormous from an adversarial supplied state.

## 3. Entrance weighting removes the large reciprocal

Suppose a pinned pre-attempt state has exactly one correct slot, k, and the
next breeder i can reach it. Let x=w_i and a=(i+1) mod m. Losing the last
correct slot requires a child y!=k observed as k. Its conditional probability
is pD(x,y)D(y,k). There is only one accepted slot, so the new state is
unseeded. Apply (6) with the just-corrupted k, then sum **with these entrance
probabilities still present**:

    E[1{last seed lost} L | F_t]
      <= J(i,k,x)
      := mp/delta_k [1-D(x,k)+g_k(a) rho(x,k)],      (7)

    rho(x,k)=sum_{y!=k} D(x,y)D(y,k).

The cancellation is termwise: D(y,k)v_k(y)=1. The rest of the population
and the law of its subsequent evolution do not enter the bound. In
particular this is not a claim that E[L | last seed lost] is small; that
conditional mean divides by a potentially tiny entrance probability.

Since rho<=1, 1-D(x,k)<=1 and g<=1-2p, a uniform charge is

    J(i,k,x) <= kappa
      := 2mp(1-p)/[1-(d_max+1)p].                   (8)

**Proved trajectory occupation theorem, supplied seeded version.** Start
from any pinned state with at least one correct slot, at any phase. Let
tau be the first future aligned sweep boundary (including time zero if it
is an aligned boundary). For any deterministic attempt horizon H, count

    Z_H = sum_{t<tau wedge H} 1{C_t=0},
    V_H = sum_{t<tau wedge H} 1{C_t=1 and its unique k is in B_T(t mod m)}.

Then

    E Z_H <= E sum_{vulnerable t<tau wedge H} J(i_t,k_t,w_i(t))
           <= kappa E V_H.                        (9)

Proof: the zero-seed intervals are disjoint. Charge each to its immediately
preceding last-seed-loss attempt. For an interval cut off at H, use its full
future length as an upper bound. Each indicator of an eligible pre-attempt
history is F_t-measurable; (7) and Tonelli sum the charges. No independence
between intervals, slots, durations, or exit states is needed. At tau all
zero-seed intervals have ended, because the boundary is fully aligned.

In particular, since V_H<=tau wedge H-Z_H,

    E[tau wedge H] <= (1+kappa) E[tau wedge H-Z_H].  (10)

This leaves the full evolution and cyclic phases of the seeded intervals
intact. It is an occupation decomposition, not deletion of elapsed time or
an alternate scheduler. Taking H to infinity is permitted by nonnegative
convergence, with extended expectations if necessary.

## 4. Entry at full pinning under ordinary initialization

Let A be the first **attempt time** at which the reference and all labels
are pinned, including initialization A=0. The recorded boundary event S is
the first boundary at or after A. Let tau be the first aligned boundary at
or after A, i.e. the post-S endpoint. This can be later than first true
alignment; none of the argument identifies those endpoints.

**Proved final-pinning fact.** On a transition from not fully pinned to fully
pinned, exactly one stored label was missing its target, say k, before the
attempt, and the observation is k. One shared observation can newly pin
only its own target. If the final ideal-reference discovery also occurs on
this attempt, update the reference first, as the code does. The reference is
now ideal, so every already pinned recipient rejects an observation different
from its target. Only k changes. Thus an all-wrong entrance at A>0 must have
the same wrong-child factor pD(x,y)D(y,k) as (7).

Let R_H count attempts t<tau wedge H that occur before A, have exactly one
missing stored target k, and have k in the current breeder's neighborhood.
Such a history is called pin-ready only to define this counter. It does
not condition on that attempt succeeding. Let V_H count post-A vulnerable
histories as in (9), and let Z_H count post-A unseeded pre-attempt states.
Then for an arbitrary initial law,

    E Z_H <= B_init + kappa E(R_H+V_H),             (11)

where B_init can be E[1{A=0,C_0=0} min_k Phi_k(w(0),0)]. The final-pinning
entrance is charged once, at its original pre-attempt history. All subsequent
entrances are last-seed losses and use (7). This proves (11) without assuming
fresh noise conditional on S or the stored labels.

For ordinary independent uniform bit-string initialization, each incumbent
is evaluated once by the specified observation rule and the reference
encloses those observations. Use k=0 for the initial bound. Since g_0(0)=0,
the event A=0,C_0=0 entails w_0!=0 and observation 0 at slot 0, hence

    B_init <= mp/delta_0 sum_{y!=0} Bin(n,1/2)(y)
            = mp(1-2^(-n))/delta_0.                (12)

The other initialization conditions were dropped, not assumed independent
after selection. This is an **unconditional** weighted initialization bound;
conditioning on all-wrong full pinning can make the repair expectation huge.

R_H and V_H are disjoint and lie outside Z_H. Consequently

    E[tau wedge H]
      <= (1+kappa) E[tau wedge H-Z_H] + B_init.     (13)

All n+1 initialization evaluations are excluded from these attempt counts;
add m to obtain evaluations including initialization. The stopping time tau
itself is still at a boundary, so tau/m is the exact sweep count. Z_H, R_H
and V_H are occupation counts, not independent sweep durations.

For completeness, tau has finite expectation at each fixed n and p<1.
From every valid state, one all-clean sweep forcing the endpoint breeders
to generate 0 and n supplies the ideal reference. A following all-clean sweep
forcing each breeder k to generate k pins and truly solves all slots. Every
prescribed weight has a uniformly positive mutation probability on this
finite state space. This gives a positive two-sweep minorization; it is not
a useful asymptotic bound. Nothing here reuses an expectation as a tail bound.

## 5. Explicit growing-T consequence and remaining obligation

**Proved:** at p=c/n, fixed c>0, and any T=o(n), condition (1) holds for
sufficiently large n and

    kappa = 2c + O_c(T/n+1/n),
    B_init <= c+O_c(T/n+1/n).

In particular this holds for T=ceil(sqrt(n)), natural-log T, and each fixed
T, without a constant exponential in T. A convenient finite sufficient
condition is 2Tp<1, giving

    kappa <= 2(n+1)p(1-p)/(1-2Tp).                 (14)

For full T=m, the displayed sufficient condition is p<1/(n+2); at p=c/n
it holds eventually for c<1 and kappa tends to 2c/(1-c). For c>=1 its
failure is only a failure of this sufficient drift estimate.

**Proved sharper full-communication case:** for T=m and every p<1, any
inactive gate creates a correct slot, since its true child y is observed as
y and slot y is a recipient. Thus from any unseeded state the conditional
failure probability on each attempt is at most p, giving E L<=1/(1-p)
by summing the product survival bound. Every last-seed-loss or all-wrong
final-pinning entrance requires an active gate. Consequently (9) and (11)
hold with kappa_full=p/(1-p); for ordinary initialization one may use
B_init_full=p/(1-p) as well. No degree condition is needed for this special
case. At p=c/n these charges are O_c(1/n). This bounds reseeding, not full
simultaneous completion, and does not change the scheduler.

Thus from the supplied corner the expected total time with **no** correct
slot is at most (2c+o(1)) times the expected vulnerable seeded occupation.
Under ordinary initialization the same statement also charges pin-ready
attempts and the bounded initialization term (12). It makes no assertion
about the probability of reaching the supplied corner.

Together with round 21's clean seeded lemma this locates the remaining gap:
noisy completion while at least one correct slot survives. Clean expected
repair <=3n times the error count does not control these noisy seeded
intervals. There is still no polynomial total runtime here for growing T,
no ordering of T arms at fixed c, and no explanation of pre-U or U-to-S
speedup. The previously published finite phase diagnostics are not recertified
or used as premises. No Taylor coefficient or remainder is used.

## 6. Obstruction: ongoing noise does not give uniform fast reseeding

**Proved negative result for supplied states.** For T<m set
a=ceil((m-T)/2). At each breeder i choose the endpoint farthest from its
recipient interval: w_i*=n if n-max B_T(i)>=min B_T(i), and 0 otherwise.
Every slot is wrong and every parent is at distance at least a from its
nearest recipient. This is the polarized family from round 21.

While the population has not changed, a clean proposal can be accepted only
after at least a mutations. Under an activated proposal the observed genotype
is obtained by two independent rate-1/n masks. The combined bit-flip rate
is r=2(1-1/n)/n<=2/n. For X~Bin(n,q), the elementary factorial-moment bound

    Pr(X>=a)<=E binom(X,a)=binom(n,a)q^a<=(nq)^a/a!

therefore bounds the probability of any accepted proposal at a single attempt
by u=[(1-p)+p2^a]/a!. A true change is a subset of acceptance. Until the
first change this bound applies to each fresh attempt, so the survival product
gives mean first-change attempts at least 1/u (trivially if u>1). A first
seed requires a change. Hence

    E_{w*}[first-seed attempts] >= a!/[(1-p)+p2^a]. (15)

For p=c/n and T=o(n), this is exp((1/2+o(1))n log n). It is a lower bound
under **ongoing noise**, not a transfer of a clean residence mean. Thus a
uniform polynomial reseeding bound from arbitrary supplied unseeded states
is false even at square-root T. Equation (7) reconciles this with the positive
result by retaining the very small entrance probability.

For finite verification we compute the exact first-true-change mean, not a
boundary-return mean. If r_i is the probability at breeder i of an accepted
(y,k) with y!=w_k*, then, before the first change, independent proposals give

    E[first-change attempts]
      = [sum_{j=0}^{m-1} product_{i<j}(1-r_i)]
        /[1-product_{i=0}^{m-1}(1-r_i)].            (16)

After a change the noisy process can return within the same sweep; stopping
at that first change is essential to (16). These traps have positive ordinary
initialization mass at p>0 (all true endpoint weights and each observed target
have positive mass). Positivity does not establish typical frequency or a
runtime lower bound from ordinary initialization.

## 7. Scope, dependencies and falsifiers

The reciprocal local potential is the one used in the published round-4/5
local-repair argument; the phase correction and the global last-seed/final-
pinning occupation theorem are written out here. The phase-potential idea
also has a closed-pair predecessor in rounds 11/12. This proof does not
require the artificial-family renewal construction, tensor independence,
Taylor-word estimates, or a theorem transferred from the noiseless radius
paper. Source/config hashes and finite coverage accompany the bundle.

The strongest direct falsifier is an exact pinned all-wrong phase state with
Phi_k-K_D Phi_k<1 under condition (1), where K_D is the actual noisy kernel
killed on its first seed. A violation of (7), or a full-pinning entrance that
newly pins multiple targets, would separately break the occupation extension.
The finite grid is not an all-n proof. Novelty and the current external
literature status are **UNVERIFIED**; no external theorem is transferred.
