# Claim-by-claim theory audit

This audit distinguishes the supplied drafts from arguments actually included here. It is not an independent certification of the unpublished full paper. The original `large.py` described the candidate Theta-law as if proved; the active repository deliberately does not.

## Local facts with complete arguments

### Exact weight-space reduction

See [the model notes](methodology.md). Mutation and noise transitions, acceptance, and scheduling depend on the full population only through its vector of true and stored weights. Sharing one offspring observation is essential. Exhaustive mutation/noise enumeration and coupled bitstring tests check the implementation, not the asymptotic theorem.

### Permanent optima and no Phase II when p=0

Write the integer cost as `C_j(w)=max(j(n-w),(n-j)w)`. Its unique minimizer is w=j. Away from j its gap from j(n-j) is `j(j-w)` on the left and `(n-j)(w-j)` on the right. The degenerate endpoint branches have no out-of-domain weights. At p=0, true and stored weights coincide. Non-increasing scalar cost therefore makes a correctly solved slot permanent, and all stored optima are exactly all true optima. A separate noise-repair phase is unnecessary in this setting.

### Endpoint certification and invariant (J)

Let S=w_0 after **an actual acceptance by subproblem 0**, at p=0. The accepted offspring was bred at some k in [0,r]. Every ell in [0,r] satisfies |ell-k|<=r, so that same offspring was offered to ell. Whether ell accepted or rejected, its resulting scalar cost is at most C_ell(S). Scalar costs never increase, so this certificate persists until the next endpoint acceptance, when it is refreshed.

Consequently, for ell<=r:

- if ell>=S, then w_ell>=S;
- if ell<=S, then w_ell<=S.

For the first statement, w_ell<ell has gap ell(ell-w_ell), which the certificate bounds by ell(ell-S); the alternative w_ell>=ell is immediate. The second statement follows from the increasing right branch, or trivially if w_ell<=ell. The boundary coefficients at ell=0,n cause no exception because weights remain in [0,n].

**Precondition matters.** Independent initialization need not satisfy this certificate. Skipping a predetermined number of sweeps is not a proof that it holds. The implementation starts eligible checks only after an actual endpoint acceptance, uses p=0 only, and states that reported checks occur at completed-sweep boundaries. Oracle tests additionally check it after individual turns.

### Endpoint-only upper bound

After certification, consider a sweep that starts with S=s>=2. If S does not decrease before the own turn of ell<=min(r,s), certification implies w_ell<=s. A parent with w_ell<=s-2 causes an immediate strict endpoint decrease under either mutation direction. Otherwise w_ell is s-1 or s, and a downward mutation causes a decrease with conditional probability at least (s-1)/n. Each own turn has fresh randomness. Thus the probability of at least one endpoint decrease in the sweep is at least

`1-(1-(s-1)/n)^(min(r,s)+1)`.

This is at least a constant times `min(1,(min(r,s)+1)*s/n)`. For s=1, the endpoint's own downward mutation suffices with probability 1/n. Before the first certificate, if the endpoint is not already zero, its own turns also give a first acceptance in at most O(n) expected sweeps; earlier acceptances by other visible breeders only help.

Monotonicity of S permits an **upper** fitness-level sum even when levels are skipped. Using `max(1,n/((min(r,s)+1)*s))` and splitting at r+1 gives

`E[endpoint sweeps] = O(n + (n/(r+1))*log(1+n/(r+1)))`.

The right endpoint has the same argument, independent of which of its turns comes first. This proves an endpoint bound, **not** an upper bound on the maximum completion time of all n+1 subproblems. An interior argument is still required. It also supplies no matching lower bound.

## Claims not established by the supplied larger-neighborhood drafts

| Claim | What is missing or invalid |
|---|---|
| Full exact-assignment upper bound `O(n²+(n²/T)log(1+n/T))` | The noiseless note imports Hypothesis (H), a maximum-over-coordinates lemma, and an interior proof that are not supplied in an independently checkable complete form here. The endpoint result alone is insufficient. |
| Matching full Theta-law | The upper progress bound needed for a runtime lower bound lacks a proved control on imported advanced breeders, skipped levels, and within-sweep cascades. |
| Bounded jumps (NS) | A largest jump observed in finitely many runs is not an n-uniform deterministic or probabilistic bound. Per-acceptance and per-sweep jumps are different. |
| No leaks for r>=n/3 | The supplied initialization argument excludes weights O(1) only asymptotically past a threshold; it does not exclude all weights S=Theta(n) with S<=n/8. At k=n/3, w_init=n/2, S=n/8, the initial gap n/9 exceeds the candidate low-weight gap 5n/72. Such an acceptance is not excluded by monotonicity. |
| Helper bound alone implies a progress-probability bound | A deeply advanced parent can improve the endpoint even by an **upward** mutation. Invariant (J) does not rule out all such parents below the front. Bounding the helper index and its maximum weight does not control this mechanism. |
| Weighted Supply Lemma closes the lower bound | No full proof is supplied. Also an estimate `F(S_0)<=C E[tau]+O(n)` does not by itself imply `E[tau]=Omega(n)` when F(S_0)=Theta(n); that term needs an additional lower bound or a stronger estimate. |
| Noisy interacting Phase II is an independent product chain | Shared offspring and replacement couple the coordinates. The T=1 independence argument is not transferable without a new justification. |
| Finite plots prove a noise threshold or novelty priority | Neither follows from simulation. No first-in-literature claim is made in the active documentation. |

The supplied correction table itself records leaks below n/8 in some small-radius runs, contrary to its accompanying statement that all leaks are transient. Those historical counts lack retained per-trial raw data here and are not merged into the new experiment dataset.

## Why the earlier lower-bound fixes are insufficient

The proposed invariant (J) is valid under its certification precondition, but it does not say that every low-index parent stays within one of S. If a parent has weight at most S-2, even increasing its weight by one still improves the endpoint. Thus a downward-mutation-only rate argument requires more than a bound on eligible indices.

A no-leak definition with outer parent weight <=S-2 also misses an outer parent of weight S-1 that mutates down to S-2. Moreover, several accepted decreases can occur within one sweep. Charging each exceptional sweep only by its count does not charge the harmonic mass skipped by a deep jump. These issues must be handled by an actual stochastic or amortized supply lemma, not replaced by a numerical maximum.

## Separate result: frontier scheduling

The noiseless frontier variant has a fully supplied conditional-expectation proof in [frontier.md](frontier.md). Its theorem concerns a different reproduction schedule and initialization. It is not a repair of the cyclic lower-bound proof and does not establish robustness under noise.

## Publication rule

Use “observed in the specified experiment” for numerical trends and “conjectured” or “conditional on...” for incomplete arguments. Claims become theorems in this repository only when their hypotheses, stopping criteria, cost units, and complete proofs are available for checking. Tests validate code and local identities; they do not prove an n-uniform runtime law.
