# Model and experimental methodology

## Scope

The primary experiment is the cyclic, self-parent variant in the README. There are `n+1` Tchebycheff subproblems, a fixed ideal reference `(n,n)`, one-bit mutation, one-bit prior noise, and no re-evaluation. The code does **not** implement bitwise mutation/noise, a moving reference, crossover, a uniformly chosen neighborhood parent, a random subproblem schedule, or an external archive. Results for any of those variants are not interchangeable.

The radius parameter is an integer `0 <= r <= n` and `B(k)=[k-r,k+r] intersect [0,n]`. Its nominal width is `2r+1`, maximum actual size is `min(n+1,2r+1)`, and endpoint size is `r+1`. Global replacement requires `r=n`, not `r=n/2`. The evidence uses radii and endpoint sizes to avoid the ambiguity of calling all three quantities T.

## Why simulation in weight space is exact

Given a current string of weight w, uniform one-bit mutation gives weight w-1 with probability w/n and weight w+1 with probability (n-w)/n. Conditional on offspring weight u, its observation is u with probability 1-p, u-1 with probability p*u/n, and u+1 with probability p*(n-u)/n. Scalarization, acceptance, parent indices, and stopping depend only on these weights and stored observations.

Independent mutation and noise draws at successive evaluations therefore determine the same conditional transition law on the complete vector of true and stored weights as the literal-bitstring algorithm. Copying one offspring to several neighbors creates dependence between slots; the simulator preserves that dependence by copying the SAME true weight and the SAME noisy observation. It does not simulate independent per-neighbor evaluations. The reduction does not claim independence of subproblems or of their hitting times.

Initial true weights are independently Bin(n,1/2), exactly matching independent uniform strings. Each initial individual is separately evaluated under noise. The frontier baseline instead reuses one evaluated initial string; it is labeled separately throughout.

## Counters and observation times

One call returning the two-objective vector counts as one evaluation. There are n+1 initialization evaluations in the cyclic algorithm. Each offspring evaluation counts once, even if all n+1 scalarizations compare it. The `comparisons` field counts those scalar comparisons separately.

`evaluations` is the observed time, including initialization, at either first true exact assignment or the cap. `event=1` indicates exact assignment; `event=0` indicates right-censoring at `budget`. No `-1` runtime enters a mean. `front_hit_evaluations` records first simultaneous coverage by the **current true population**, not by the sequence of historically generated solutions. `stored_hit_evaluations` is the first time every stored observation equals its target. Either event can precede true exact assignment; a stored hit need not occur before an early true exact hit. Empty optional fields mean not observed before stopping.

All three hitting events are checked after initialization and after each atomic offspring broadcast. A final partial sweep is charged only for evaluations actually performed. Diagnostic level visits are observations at **sweep starts**, including the start of a final partial sweep; they are not automatically a geometric holding-time sample. Jump histograms distinguish a single accepted endpoint decrease from the total drop across a **completed sweep**. Positive-drop plots exclude zero drops and explicitly condition on observed positive drops.

First-hit profiles record first visits, not permanent correctness under noise. The diagnostic profiles in this protocol are noiseless. Unvisited levels contribute zero to occupation averages. A first hit not observed by the cap contributes the cap to a capped first-hit profile rather than being silently removed.

## Reproducibility

`experiments/neighborhoods.json` specifies the full grid before these runs. It is a reproducible exploratory protocol, not a claim of external preregistration. Each cell/replicate receives a seed from the first eight bytes of SHA256(`master_seed|config_id|repetition`), interpreted big-endian. The generator is NumPy PCG64. Distinct cells use distinct streams; the comparisons are not paired experiments.

The runner saves `runs.csv`, `diagnostics.jsonl`, a copy of the protocol, and a manifest of direct dependency versions, source file hashes, source commit when available, data hashes, and runtime environment. The report is reconstructed from those files. `checksums.sha256` covers data, tables, report, and SVGs. Timing and environment metadata may differ between machines even when numerical trials reproduce exactly. Pin the listed dependency versions when comparing raw files. A source commit plus source hashes, not a filename alone, identifies what was executed.

## Uncertainty and censoring

Every configuration has one administrative evaluation budget. The mean of all observed times estimates the **restricted mean** E[min(tau,B)], including censored runs. Only when the sample has no censoring is it also reported as the ordinary observed runtime sample mean; this is still not evidence that the underlying distribution has no mass beyond B. The unconditional-mean field is blank for a censored cell.

Pointwise mean intervals use 2,000 deterministic percentile-bootstrap resamples. They quantify Monte Carlo sampling uncertainty approximately; their finite-sample coverage is not guaranteed, especially for skewed runtimes and 32 replicates. Completion proportions also have Wilson intervals in `summary.csv`. No multiple-testing adjustment is used. Diagnostics are descriptive, not formal hypothesis tests. No hidden curve fitting, selectively dropped seeds, or survivor-only averaging is used.

## Limitations

The largest tested n is 512 and the only nonzero main-grid noise strength is 0.1/n. This cannot establish a uniform asymptotic bound, saturation threshold, polynomial/superpolynomial transition, arbitrary-p robustness, or matching lower bound. Zero failures of an invariant in simulation is not a proof; the local noiseless certificate has a separate deterministic proof. Neighborhood exchange couples coordinates, so independent product-chain reasoning for T=1 cannot simply be reused for r>0.

The simulated full-population criterion is stronger than true current-front coverage. The frontier baseline differs in both reproduction schedule and initialization and must not be interpreted as a pure ablation of radius. Evaluation improvements are not automatically CPU improvements because larger neighborhoods increase scalar comparisons.
