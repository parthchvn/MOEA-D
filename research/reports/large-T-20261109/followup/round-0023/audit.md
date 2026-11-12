# Round 23 adversarial audit

**Finding: the precise round-21/22 claims examined below survive this audit.**
No counterexample to their stated inequalities was found. Their analytic
derivations and the new finite checks are separate evidence. The review is a
fresh context in the same model family, by the sole writer; it is provisional
assurance, not formal proof certification or an independent-model endorsement.

The audit does **not** establish noisy growing-T total runtime. It preserves
the original proofs and records three invalid shortcuts in
[witnesses.json](witnesses.json), plus an acceptance-conditioning counterexample
in [verification.json](verification.json). Earlier Taylor-word results are
historical dependencies, not all recertified in this turn. No external theorem
is transferred. External novelty and literature completeness are **UNVERIFIED**.

## Exact process and scope

All new positive statements here assume n>=2, m=n+1, ascending cyclic
own-parent standard-bit mutation, and one fresh independent activation gate
and observation mask per proposal. Both masks flip each bit with probability
1/n. If D(x,y) is the mutation weight kernel, the observation law is

`N(y,k) = (1-p) 1{y=k} + p D(y,k)`.

The cardinality T is filled, using the breeder-parity tie rule of
`scripts/neighborhood_sweep.cpp`; it is not a symmetric clipped radius.
An offspring receives **one shared observation**. Once ideal extrema and labels
are pinned, observation k is accepted only by slot k, when that slot is a
recipient. Its stored true weight becomes the child y. An unchanged/rejected
proposal consumes an attempt. At most one true coordinate changes per attempt.

F_t reveals only initialization and all randomness consumed through attempt t;
the next breeder is a=t mod m. Parents, eligible recipients, seed counts and
the potentials below are known before the next draw. Conditioning on acceptance,
future survival, or stored observations does not preserve the fresh noise law.

Let C(w) be the number of true correct coordinates. A seed means C>=1. For the
pinned theorem, tau is the first future fully aligned **sweep boundary**, with
time zero included when it is already an aligned boundary. For ordinary
initialization, A is the first full-pinning attempt, and tau is the first aligned
boundary at or after A. This agrees with the recorded post-S endpoint; it need
not agree with the earlier first-exact endpoint. Initialization costs m
evaluations in the ordinary process and zero in the supplied-corner process.
All Z,V,R occupation counts below are in attempts, not sweeps or archive hits.

## Independent derivation of the occupation inequality

**Proved under the stated assumptions.** Put I_k={i:k in B_T(i)}, d_k=|I_k|,
delta_k=1-(d_k+1)p, and assume delta_min>0. Thus p<1/2. Define

`v_k(x)=1/D(x,k)` if x!=k, and `v_k(k)=0`.

While slot k is wrong, its own turn has expected potential change at most
`-(1-2p)`. Its direct repair contributes exactly `-N(k,k)`: the child probability
D(w_k,k) cancels v_k(w_k). All positive wrong-child terms sum to at most p,
since each has factor `D(w_k,y) p D(y,k) v_k(y)`. The negative old-potential
terms on those accepted branches are retained or safely dropped for an upper
bound. On an external eligible turn the positive terms sum to at most p,
uniformly over the history-dependent parent; on an ineligible turn the change
is zero. No independence among coordinates is used.

Let r=(k-a) mod m and let e_k(a) count eligible external turns before the next
own turn. Set

`g_k(a)=r delta_k/m+p e_k(a)`.

For z_k(a)=-(1-2p) on the own turn, p on another eligible turn, and zero
otherwise, direct cyclic subtraction gives

`g_k(a+1)-g_k(a)+z_k(a)=-delta_k/m`.

In particular `g_k(k)=0` and `0<=g_k(a)<=1-2p`. The largest value is at
phase k+1, immediately after the own turn, and equals
`1-2p-delta_k/m`. This handles both the wrap from n to 0 and the delay after
corruption on the own turn. Define Phi_k=0 when k is correct, otherwise

`Phi_k(w,a)=m [v_k(w_k)+g_k(a)]/delta_k`.

Killing Phi at its tracked-slot first repair removes a nonnegative phase term.
Thus its conditional decrease is at least one on every live attempt, even
while other coordinates evolve, become correct, or overwrite k. Truncation
at deterministic H gives the local first-repair mean bound without an
integrability assumption. This verifies the round-22 repair premise.

Here is a second proof of the trajectory result, avoiding an excursion
renewal argument. On the full pinned state/phase space put

`W(w,a)=min_k Phi_k(w,a)` if C(w)=0, and `W(w,a)=0` otherwise.

At an unseeded state choose a minimizing k using the known current state.
For every next state, W is at most this fixed coordinate's next Phi, including
when a different coordinate reseeds. Therefore

`E[W_next | F_t] <= W_t-1` when C_t=0.

This uses the minimum **before** expectation; it does not interchange a minimum
and expectation or select a coordinate using future randomness.

From C_t>=2 a single pinned update cannot leave zero seeds, so W remains zero.
From C_t=1 let k be its unique correct coordinate. If k is ineligible, W also
remains zero. Otherwise let x=w_a and a'=(a+1) mod m. For every y!=k the
last-seed-loss branch has its actual probability

`p D(x,y) D(y,k)`.

The new W is at most the just-corrupted Phi_k. Summing with this probability
still attached cancels D(y,k) **term by term**, giving

`E[W_next | F_t] <= J(a,k,x)`

`J = mp/delta_k [1-D(x,k)+g_k(a') sum_(y!=k) D(x,y)D(y,k)]`.

There is no division by the probability of losing the seed. In particular
this is not a uniform bound conditional on that loss. The bound

`J <= kappa = 2mp(1-p)/[1-(d_max+1)p]`

uses only rho<=1, 1-D(x,k)<=1, g<=1-2p and delta_k>=delta_min. It is
uniform over the incoming breeder, all incumbent values, all phases and all
past selection histories satisfying the pinned model.

Let Z_H count unseeded pre-attempt states and V_H count eligible unique-seed
pre-attempt states before tau wedge H. The established one-step inequality is

`E[W_next-W_t | F_t] <= -1{C_t=0}+J_t 1{vulnerable}`.

Summing up to tau wedge H and dropping its nonnegative final W proves

`E Z_H <= W_initial + E sum J_t 1{vulnerable} <= W_initial+kappa E V_H`.

For a supplied seeded state W_initial=0. Nonnegative convergence permits H to
increase to infinity, with extended expectations if necessary. This proof
keeps all elapsed attempts, all phase-dependent exits, shared observations,
failed proposals and reinfection. It assumes neither independent excursions
nor independent slots and never deletes the time of an all-wrong excursion.
The process still stops only at an aligned boundary, where W=0.

**Constant uniformity checked analytically.** Every donor edge spans at most
T-1 indices, so d_max<=min(m,2T-1). At p=c/n, fixed c>0 and T=o(n), eventually
delta_min>0 and `kappa=2c+O_c(T/n+1/n)`. This includes square-root and
natural-log cardinalities. No parameter hidden in this conclusion grows
exponentially with T. It remains a bound on **unseeded occupation relative to
vulnerable seeded occupation**, not a bound on either total quantity alone.

## Ordinary initialization, full communication and traps

**Proved, with the original restricted interpretation.** On the decisive
full-pinning transition, a shared observation can newly pin only its own
target k. At most one target label was missing before this transition. The
reference is updated first; once it is ideal, other already-pinned targets
reject this observation. Thus only k changes. If the new state is all wrong,
the same factor `pD(x,y)D(y,k)` applies for y!=k, regardless of earlier
selection. The indicator that a pre-attempt state has one missing label and
an eligible target is predictable. Charging its possible transition gives
the original R_H term without conditioning on successful pinning.

Equivalently set W=0 before A and use the pinned W after A in the preceding
telescoping proof. From ordinary uniform initialization the initial all-wrong
fully-pinned contribution is at most

`B_init <= mp(1-2^(-n))/delta_0`.

This follows by tracking slot zero, whose phase correction at initialization
is zero, retaining its observation likelihood pD(y,0), and dropping all other
initialization requirements. No independence conditional on pinning is needed.
Therefore `E Z_H<=B_init+kappa E(R_H+V_H)` is valid. It bounds neither the
time to A/S nor the law of a typical post-S population. There is no
ordinary-initialization runtime theorem here.

**Proved full-communication exception.** At T=m every inactive gate supplies a
seed immediately. Products of conditional failure probabilities give first
reseeding mean at most 1/(1-p), for all p<1. A last-seed-loss or all-wrong
final-pinning entrance requires an active gate, so its weighted charge is at
most p/(1-p). No degree condition is required. This concerns reseeding,
not simultaneous boundary completion or persistent alignment.

**Proved supplied-state obstruction retained.** In the polarized all-wrong
state each breeder's true endpoint is at least a=ceil((m-T)/2) from its
nearest recipient. Until the first true change, acceptance requires at least
a flips in the observed string. An active gate composes two independent masks,
giving per-bit flip probability 2(1-1/n)/n<=2/n. The factorial-moment bound
on the number of flips gives a per-attempt change probability at most
`u=[(1-p)+p 2^a]/a!`. Conditional survival products, not stationary reasoning,
give first-change mean at least 1/u. A first seed requires a true change, so
the same lower bound applies to reseeding. If u>1 the claim is merely the
trivial lower bound below one attempt. For T=o(n), p=c/n, the displayed lower
bound grows as `exp((1/2+o(1)) n log n)`.

Accepted unchanged-weight proposals can alter genotypes; this does not break
the argument because every future mutation/observation weight law depends
only on the current weight. This is a first-change statement; it would be
incorrect to treat its holding product as noisy boundary-return residence.
Positive accessibility or initialization mass does not give an ordinary-run
lower bound without multiplying the actual entrance probability.

## Round-21 audit: clean repair and signed coefficients

**Proved within the clean pinned model.** At T>=3 every adjacent pair
communicates both ways, although more distant boundary edges can be directed.
With at least one correct slot, choose a correct-to-wrong adjacent edge at a
boundary. Its correct donor persists under p=0. Each scheduled donor visit
repairs the neighbor with conditional probability greater than 1/(3n), or
the neighbor was already repaired. Explicit conditional survival products
bound this stage by 3n sweeps. There are at most e stages from e errors, giving
3ne; an arbitrary initial phase costs at most one additional sweep. This is
a sum of conditional stage means, never a maximum of marginal means.

The polarized-state clean lower bound a!/m and the upper bound
`4*2^a_star*a_star!+3n^2` also survive analytic inspection. For even T, missing
central interval starts require exactly the stated additional unit when
n=3 mod 4 and T<m. The upper-bound binomial product has every favorable-bit
factor at least n/2; the no-flip probability is at least 1/4. These constants
hold uniformly over the parent weight and neighborhood cardinality. The
factorial conclusions are worst-supplied-state statements, not corner or
ordinary-initialization statements.

**Proved signed finite-order bound, with its cutoff essential.** On attempt
phases kill only aligned phase zero. The signed insertion is activated kernel
minus clean kernel, including its negative unchanged/clean branches; its
absolute row mass is at most two. Every branch adds at most one error. From
one corner error, j insertions with j<n leave at most j+1<=n errors, so a seed
survives in every intervening clean state. Initial occupation is m/q_T;
later occupations are at most mL_j and final sweep reward at most L_j,
where L_j=3n(j+1)+1. Multiplication gives exactly

`|h_j(C)| <= 2^j m^j L_j^j/q_T` for 1<=j<n.

Negative branches cannot invalidate this support argument; aligned interior
states must remain live because a later insertion can reinfect them. Our
independent sweep-polynomial calculation includes both same-sweep and
different-sweep insertions and agrees with all eight tiny published
coefficients. At j>=n the seed protection is unavailable. These coefficients
provide no uniform remainder at fixed positive c.

**Conditional algebraic conclusion only.** Substituting p=c/n into the earlier
forest bound gives the published logarithmic, square-root and full-T orders.
The exponential factor is the artificial-family simultaneous-emptiness cost.
This audit checked the substitution and located the dependency; it did not
recertify the entire old forest construction. Those displayed orders retain
that explicit dependency. No stronger new runtime claim is supported.

## Finite implementation and empirical checks

The independent [audit.py](audit.py) imports no prior-round implementation.
It enumerates actual bit masks and uses literal scalarization comparisons.
Its coefficient solver multiplies signed sweep polynomials; the previous
implementation used phase recurrences. Boundary/runtime equations include
aligned interior states. Floating linear solves only propose decimal
rationals; exact residuals and a positive time supersolution bound all errors.
[verify.py](verify.py) rechecks the resulting certificates without NumPy or a
linear solve. Declared finite coverage and exact values are in
[verification.json](verification.json), [global.csv](global.csv),
[occupation.csv](occupation.csv), [clean.csv](clean.csv), and
[coefficients.csv](coefficients.csv). None is an all-n proof.

[receipts.py](receipts.py) independently validates 1,312 existing receipts,
reads campaign packets without extraction, checks actual registration bytes
in Git, and recomputes the separate n=512 registered analysis. It preserves
the capped original main observation and the 240 missing, gate-blocked holdout
observations. Missing is not censoring; restricted means are not unrestricted
means; smoke is excluded from inference. Bootstrap resamples use the existing
registered analysis seeds only. No new scientific outcomes are generated.
Detailed distributions, phase denominators, hashes and scope are in
[empirical.json](empirical.json). Private execution chronology remains
unavailable; Git metadata and published receipts do not independently certify it.

## Verdict and remaining falsifier

**Retain proved status** for the precisely scoped clean-seed lemma, clean
worst-state bounds, finite-order coefficient bound, noisy local repair,
acceptance-weighted occupation theorem, final-pinning extension, full-T
reseeding bound and supplied noisy-trap obstruction. The new global W argument
is an alternative derivation of the occupation theorem, not a total-runtime
upgrade. No evidence requires downgrading those exact statements.

**Unsupported stronger claims remain open or contradicted:** polynomial
conditional reseeding from arbitrary all-wrong states, uniform noisy progress
from the clean lemma, ordinary-initialization transfer, fixed-c ordering, a
uniform Taylor remainder and total growing-T runtime. Numerical certificates
are finite mechanical evidence only. Prior author/reviewer scores are not
premises of this verdict.

The strongest direct falsifier of the retained occupation theorem would be
an admissible state/phase with
`W-E[W_next] < 1{C=0}-J 1{vulnerable}` under delta_min>0, or a valid final-pin
entrance changing multiple target coordinates. Neither occurs in the declared
finite search. The concrete counterexamples in this bundle falsify shortcuts,
not the stated theorem.
