# Larger T: activation 10aae295fdf6, 2026-11-09

**Empirically supported at n=256; replication open.** At p=1/(64n), T=16 used fewer first-exact evaluations than T=1: mean ratio 2.327639, pointwise 95% interval [2.050148, 2.674642]. The registered two-stage decision is **inconclusive** because the holdout gate blocked all n=512 sampling. This is this activation's dated C17–C19 claim/status supplement; it makes no new asymptotic or monotonicity claim.

**Mechanically checked provenance.** At the evidence review, the worker's activation was `10aae295fdf6`, state `review`, updated 2026-11-09T20:51:28Z: “Partial campaign evidence published.” I read the actual [campaign report](campaign/report.md), [evidence index](../../evidence/large-T-20261109/campaign/INDEX.json), and archived holdout `status.json`. Sampling began from clean commit `b8652edaa461d99715f4fe913ff4a52f323fd009`; the worker's evidence commit is `a89cd4742b4623667ad49dae73874a7c39b98bdf`. The frozen C++ source hash is `11bdbd26facb39b22df911d063e1718dd03a2ae8fd01a18458d1c5e8f694df10`; clang 20.1.8, libc++ 200100, C++17/O3, Python 3.13.12, Apple M3 Pro/arm64. All three scientific files still match the packet. No source PDF, frozen harness, seed, cap, gate, or Git history was changed by this agent.

Evidence INDEX.json SHA-256: 05b8dab6a35c8b7de1e2087d2f798a41d6c85b4ea2b79d663b0ca173266c4b71

**Mechanically checked validation.** The worker passed 93 tests in 10.765 s. Packet verification passed all four stage archives. Independent raw-receipt arithmetic matched 8,369 numerical checks, including counts, missingness, sums, means, quantiles, phase denominators, work totals and every frozen bootstrap contrast. Reanalysis reproduced all 13 report files byte for byte. All 1,484 planned seeds are distinct across stages/configurations; receipt hashes and source hashes passed. Bytewise report reproduction and arithmetic checks are reproducibility evidence, not an independent proof review.

Commands used, from the checkout (Python was `/Users/parth/miniforge3/bin/python`):

```sh
task=research/runs/larger-neighborhoods-20261109/agent-work/10aae295fdf6
packet=research/evidence/large-T-20261109/campaign
python scripts/package_neighborhood_evidence.py verify --packet "$packet"
python scripts/package_neighborhood_evidence.py unpack --packet "$packet" --out "$task/verified-raw"
python scripts/analyze_neighborhood_campaign.py --runs "$task/verified-raw/smoke" "$task/verified-raw/calibrate" "$task/verified-raw/main" "$task/verified-raw/holdout" --out "$task/replayed-report"
python "$task/check_structure.py"
python "$task/audit_receipts.py"
python -m py_compile sim.py large.py scripts/run_research.py
shasum -a 256 research/evidence/large-T-20261109/campaign/INDEX.json
```

Scratch scripts/results and reviewed status snapshots remain under the specified ignored activation directory. The unpack destination must be new on a rerun. The worker ran `scripts/neighborhood_campaign.py --stage STAGE --out research/runs/larger-neighborhoods-20261109 --seconds REMAINING` for smoke, calibrate, main and holdout; its log records the exact remaining budgets 15871, 15869, 15867 and 15827 seconds, respectively. The packet manifests contain the full frozen seed plans.

**Model scope.** Ordinary trials initialize independent Binomial(n,1/2) true weights, evaluate each once, and use ascending cyclic own-parent standard-bit mutation. One Bernoulli(p) gate activates independent per-bit 1/n observation noise; one observed offspring is shared across T recipients. Extrema include rejected observations and are updated before both scalar comparisons. T is a filled cardinality with parity-dependent ordering, not a clipped radius. The endpoint is first simultaneous true slot-to-target assignment at a sweep boundary.

**Mechanically checked eligibility and censoring.** Smoke: 62/62 exact and post-S endpoints. Calibration: 102/102 receipts, comprising 96 completed supplied-corner trials and six intentionally capped 32-sweep timing trials. Main: 1,080/1,080 receipts, 1,079 exact hits, one cap, no missing trial. Holdout: 0/240 receipts, all missing, `gate_blocked`; no n=512 outcome estimate exists.

The cap is n=64, T=1, f=1 (p=1/64), repetition 20, receipt `67178d8d2471ba15457b`, seed `10112010688641361696`. At H=3,206 sweeps (208,455 evaluations), U=469 but S, current front and exact assignment remain unobserved. This is valid censoring, **not failed receipt validation**. The frozen gate requires every main exact hit, including this high-noise cell, so it blocks holdout even though both n=256 low-noise primary arms completed. Its unrestricted mean and associated unrestricted comparisons are unavailable; retain the restricted observations. Do not increase its cap, replace its seed, or bypass the gate within this campaign.

The registered decision rule, verbatim: “Call the directional effect replicated only when both lower endpoints exceed one and both stages are fully eligible. Intervals crossing one give an inconclusive directional comparison.” The actual verified report's decision is: “Inconclusive — a primary or confirmation arm has cap-censored or missing exact times.”

**Mechanically checked primary arithmetic; empirical uncertainty.** Cost for ordinary initialization and first exact boundary s is (n+1)(1+s), including all n+1 initial evaluations.

| Stage, n, T; f=1/64 | Planned / observed / capped / missing | Sum of observed evaluations | Mean evaluations | q10 / median / q90 evaluations |
|---|---:|---:|---:|---:|
| Main, 256, 1 | 24 / 24 / 0 / 0 | 27,976,763 | 1,165,698.458 | 837,357.4 / 1,108,569.5 / 1,505,942.9 |
| Main, 256, 16 | 24 / 24 / 0 / 0 | 12,019,376 | 500,807.333 | 355,122.6 / 490,356.0 / 645,018.6 |
| Holdout, 512, 1 | 16 / 0 / 0 / 16 | unavailable | unavailable | unavailable |
| Holdout, 512, 23 | 16 / 0 / 0 / 16 | unavailable | unavailable | unavailable |

The raw ratio of the two main sums is 2.3276385562777966, matching [contrasts.csv](campaign/contrasts.csv). Its interval uses 10,000 independent within-arm resamples of whole trajectories. The 24+24 main seeds and the distinct planned 16+16 holdout seeds do not form paired observations. The n=512 fixed-horizon mean for **each** of its 15 arms is bounded only by [513, 19,669,446] evaluations; the primary restricted-ratio identification interval is [1/38342, 38342], not the rounded zero lower bound displayed in the report. These are missing-data bounds, not confidence intervals. Unrestricted means have no finite upper bound from this evidence.

**Empirical summaries of every main arm.** Here p=f/n; P/O/C/M means planned/exact-observed/capped/missing. Means are evaluations. R=mean(T=1)/mean(T) at fixed n,f, so R>1 favors sharing. T=1 is the reference, with no comparison interval. The ceil(sqrt(n)) intervals below are exactly the frozen analyzer's intervals. Other baseline contrasts are explicitly exploratory supplements using the same 10,000 independent whole-trajectory percentile bootstrap; their deterministic seed is the first 16 hex digits of SHA-256 of compact sorted-key JSON `["activation-10aae295fdf6-exploratory-v1",baseline_config,comparator_config]`, with config order as in `cells.csv`. They do not alter the registered decision. All intervals are pointwise nominal 95%, without across-grid coverage.

Phase entries are mean U / mean(S−U) / mean(post−S), in **sweeps**. Each denominator is 24 except the starred capped cell, whose denominators are 24 / 23 / 23. The latter two means condition on phase completion and must not be added to the all-trial U mean. For n=512 all three observed denominators are zero, for every T and factor. [cells.csv](campaign/cells.csv) gives distributions and endpoint-specific censoring; [work.csv](campaign/work.csv) gives every phase denominator and work counter.

| n | f | T | P/O/C/M | Mean evaluations | R [95% interval] | U / S−U / post−S sweeps |
|---:|---:|---:|---:|---:|---|---:|
| 64 | 0 | 1 | 24/24/0/0 | 53,950.0 | reference | 683.7 / 145.3 / 0.0 |
| 64 | 0 | 3 | 24/24/0/0 | 17,940.0 | 3.007 [2.628, 3.458] | 269.9 / 5.1 / 0.0 |
| 64 | 0 | 8 | 24/24/0/0 | 23,706.0 | 2.276 [1.860, 2.809] | 359.6 / 4.1 / 0.0 |
| 64 | 0 | 16 | 24/24/0/0 | 24,575.4 | 2.195 [1.910, 2.531] | 373.3 / 3.8 / 0.0 |
| 64 | 0 | 65 | 24/24/0/0 | 22,259.8 | 2.424 [2.067, 2.826] | 337.4 / 4.0 / 0.0 |
| 64 | 1/64 | 1 | 24/24/0/0 | 56,281.9 | reference | 700.8 / 158.5 / 5.5 |
| 64 | 1/64 | 3 | 24/24/0/0 | 25,019.6 | 2.250 [1.921, 2.676] | 378.8 / 5.1 / 0.1 |
| 64 | 1/64 | 8 | 24/24/0/0 | 25,512.5 | 2.206 [1.888, 2.598] | 387.4 / 4.1 / 0.0 |
| 64 | 1/64 | 16 | 24/24/0/0 | 23,806.2 | 2.364 [1.948, 2.897] | 361.5 / 3.8 / 0.0 |
| 64 | 1/64 | 65 | 24/24/0/0 | 21,764.2 | 2.586 [2.178, 3.119] | 329.5 / 4.4 / 0.0 |
| 64 | 1 | 1 | 24/23/1/0 | 65,319.6 restricted* | reference | 615.2 / 227.2 / 59.7 |
| 64 | 1 | 3 | 24/24/0/0 | 23,654.6 | 2.761 [2.185, 3.563] restricted | 345.7 / 14.5 / 2.7 |
| 64 | 1 | 8 | 24/24/0/0 | 28,819.4 | 2.267 [1.725, 3.018] restricted | 432.6 / 4.4 / 5.4 |
| 64 | 1 | 16 | 24/24/0/0 | 25,707.5 | 2.541 [1.973, 3.331] restricted | 385.8 / 4.3 / 4.3 |
| 64 | 1 | 65 | 24/24/0/0 | 23,427.1 | 2.788 [2.127, 3.688] restricted | 353.4 / 3.8 / 2.2 |
| 128 | 0 | 1 | 24/24/0/0 | 240,112.0 | reference | 1,496.6 / 363.7 / 0.0 |
| 128 | 0 | 3 | 24/24/0/0 | 106,145.5 | 2.262 [1.880, 2.718] | 816.0 / 5.9 / 0.0 |
| 128 | 0 | 12 | 24/24/0/0 | 112,203.1 | 2.140 [1.791, 2.556] | 864.2 / 4.6 / 0.0 |
| 128 | 0 | 32 | 24/24/0/0 | 123,748.6 | 1.940 [1.598, 2.317] | 953.5 / 4.8 / 0.0 |
| 128 | 0 | 129 | 24/24/0/0 | 111,789.2 | 2.148 [1.733, 2.611] | 860.9 / 4.7 / 0.0 |
| 128 | 1/64 | 1 | 24/24/0/0 | 234,774.6 | reference | 1,565.5 / 253.5 / 0.0 |
| 128 | 1/64 | 3 | 24/24/0/0 | 111,488.2 | 2.106 [1.827, 2.461] | 850.1 / 13.1 / 0.0 |
| 128 | 1/64 | 12 | 24/24/0/0 | 102,872.1 | 2.282 [2.019, 2.599] | 792.0 / 4.5 / 0.0 |
| 128 | 1/64 | 32 | 24/24/0/0 | 112,342.9 | 2.090 [1.831, 2.410] | 865.1 / 4.8 / 0.0 |
| 128 | 1/64 | 129 | 24/24/0/0 | 104,387.9 | 2.249 [1.955, 2.599] | 803.0 / 5.2 / 0.0 |
| 128 | 1 | 1 | 24/24/0/0 | 274,732.4 | reference | 1,553.8 / 499.5 / 75.4 |
| 128 | 1 | 3 | 24/24/0/0 | 114,949.8 | 2.390 [1.982, 2.870] | 882.5 / 6.8 / 0.8 |
| 128 | 1 | 12 | 24/24/0/0 | 101,270.4 | 2.713 [2.394, 3.076] | 777.5 / 5.0 / 1.6 |
| 128 | 1 | 32 | 24/24/0/0 | 103,888.0 | 2.645 [2.279, 3.058] | 796.1 / 4.5 / 3.8 |
| 128 | 1 | 129 | 24/24/0/0 | 111,724.8 | 2.459 [2.128, 2.846] | 859.0 / 4.2 / 1.8 |
| 256 | 0 | 1 | 24/24/0/0 | 1,073,017.8 | reference | 3,522.4 / 651.8 / 0.0 |
| 256 | 0 | 3 | 24/24/0/0 | 505,829.5 | 2.121 [1.854, 2.446] | 1,960.5 / 6.7 / 0.0 |
| 256 | 0 | 16 | 24/24/0/0 | 508,335.3 | 2.111 [1.817, 2.444] | 1,971.3 / 5.6 / 0.0 |
| 256 | 0 | 64 | 24/24/0/0 | 445,284.6 | 2.410 [2.130, 2.716] | 1,726.0 / 5.6 / 0.0 |
| 256 | 0 | 257 | 24/24/0/0 | 468,029.1 | 2.293 [2.014, 2.616] | 1,814.2 / 5.9 / 0.0 |
| 256 | 1/64 | 1 | 24/24/0/0 | 1,165,698.5 | reference | 3,761.1 / 773.7 / 0.0 |
| 256 | 1/64 | 3 | 24/24/0/0 | 606,177.3 | 1.923 [1.553, 2.390] | 2,350.5 / 7.2 / 0.0 |
| 256 | 1/64 | 16 | 24/24/0/0 | 500,807.3 | 2.328 [2.050, 2.675] | 1,942.1 / 5.6 / 0.0 |
| 256 | 1/64 | 64 | 24/24/0/0 | 549,316.1 | 2.122 [1.813, 2.495] | 2,131.1 / 5.2 / 0.1 |
| 256 | 1/64 | 257 | 24/24/0/0 | 506,654.1 | 2.301 [2.001, 2.665] | 1,964.8 / 5.5 / 0.1 |
| 256 | 1 | 1 | 24/24/0/0 | 1,157,528.0 | reference | 3,724.8 / 675.9 / 102.3 |
| 256 | 1 | 3 | 24/24/0/0 | 506,236.5 | 2.287 [1.827, 2.871] | 1,960.1 / 7.1 / 1.6 |
| 256 | 1 | 16 | 24/24/0/0 | 472,655.1 | 2.449 [2.120, 2.845] | 1,830.2 / 5.8 / 2.2 |
| 256 | 1 | 64 | 24/24/0/0 | 494,810.7 | 2.339 [1.963, 2.793] | 1,916.6 / 5.8 / 2.0 |
| 256 | 1 | 257 | 24/24/0/0 | 492,058.6 | 2.352 [2.003, 2.767] | 1,906.5 / 5.9 / 1.2 |

All holdout combinations n=512, T∈{1,3,23,128,513}, f∈{0,1/64,1} have P/O/C/M=16/0/0/16 **per cell**, no observed effects or sampling intervals, and the bounds above. The restricted n=64,f=1 comparisons cannot support an unrestricted directional runtime statement. For the other main comparisons the finite observed direction favors sharing versus T=1; unobserved rare tails remain possible with 24 trajectories per arm.

**Empirical reversals and unresolved marginal gains.** Increasing T beyond ceil(sqrt(n)) does not consistently improve the point estimate. The table below reports every exploratory adjacent contrast R=mean(smaller T)/mean(larger T), with independent bootstrap intervals using the supplementary seed rule above. R<1 is an observed slowdown. Every interval crosses one; this establishes neither equality nor a plateau.

| n | f | ceil(sqrt(n)) → ceil(n/4): R [95%] | ceil(n/4) → full: R [95%] |
|---:|---:|---|---|
| 64 | 0 | 0.965 [0.777, 1.187] | 1.104 [0.931, 1.304] |
| 64 | 1/64 | 1.072 [0.880, 1.313] | 1.094 [0.878, 1.365] |
| 64 | 1 | 1.121 [0.883, 1.430] | 1.097 [0.866, 1.381] |
| 128 | 0 | 0.907 [0.711, 1.148] | 1.107 [0.854, 1.431] |
| 128 | 1/64 | 0.916 [0.778, 1.079] | 1.076 [0.902, 1.275] |
| 128 | 1 | 0.975 [0.849, 1.119] | 0.930 [0.795, 1.087] |
| 256 | 0 | 1.142 [0.978, 1.343] | 0.951 [0.825, 1.102] |
| 256 | 1/64 | 0.912 [0.783, 1.067] | 1.084 [0.927, 1.272] |
| 256 | 1 | 0.955 [0.814, 1.120] | 1.006 [0.850, 1.196] |

**Empirically supported mechanism limitation.** In the primary T=1 and T=16 cells, all 24 trajectories reached every phase: U means were 3,761.083 and 1,942.083 sweeps; S−U means 773.708 and 5.583; post−S was zero in every trajectory. The mean difference decomposes into 1,819 U sweeps and 768.125 S−U sweeps. Both arms recorded zero mismatches at U and S and zero pinned-endpoint repairs, own or external. Thus the observed primary difference occurs before S; a faster *post-S endpoint repair* does not explain these sampled trajectories. Earlier endpoint discovery may still affect U; the repair counter begins only after an endpoint is individually pinned.

Across all main cells only two external pinned-endpoint repairs were recorded: one at n=64,T=8,f=1 and one at n=128,T=32,f=1. There were none in any n=256 cell. The primary T=16 arm's 11,966,868 external replacements therefore cannot be interpreted as that many useful repairs; replacements include unchanged true weights and labels. One main trajectory (n=64,T=1,f=1, receipt `82184ab7b54a1af9ebd7`) first became truly exact at sweep 773, before S=780. The runner continued to post=780. This verifies why early exact and post-S times must remain separate. No phase-completion filtering was used for the uncensored primary means.

**Empirical work tradeoff, in separate units.** For n=256,f=1/64, each row below uses all 24 receipts. Comparisons are logical recipient tests to the recorded post-S endpoint; wall time is the mean full engine-run time including process start. Here exact=post for every primary T=1 and T=16 trajectory, so their recorded endpoints coincide. Other cells must retain their recorded post/cap timing interpretation.

| T | Mean recipient comparisons | Mean full-run seconds | Attempts/s (aggregate) |
|---:|---:|---:|---:|
| 1 | 1,165,441.5 | 0.056626 | 20,581,428 |
| 3 | 1,817,761.0 | 0.034681 | 17,471,038 |
| 16 | 8,008,805.3 | 0.041097 | 12,179,728 |
| 64 | 35,139,781.3 | 0.085179 | 6,445,939 |
| 257 | 130,144,050.4 | 0.217156 | 2,331,951 |

T=16 reduces observed evaluation cost by about 57.0%, while using 6.872 times as many logical comparisons as T=1. Its recorded aggregate wall-time ratio is only 1.378 in its favor. Full broadcast has fewer evaluations than T=1 but about 3.84 times its recorded wall time. These short local timings have no repeated timing uncertainty assessment; logical comparisons also include optimized pinned-state accounting and are not equivalent to CPU operations.

The six separate 32-sweep throughput cells are timing controls, one receipt each: at n=128/256/512, T=1 attempts/s were 1,172,491 / 2,496,566 / 4,666,675; full broadcast gave 888,188 / 1,235,090 / 984,586. Their logical comparisons/s were respectively the same as attempts/s at T=1, and 114,576,195 / 317,418,085 / 505,092,545 at full broadcast. Fixed-horizon controls and variable-length stopped runs visit different states and amortize startup differently; neither can be pooled into a runtime-effect estimate.

**Proved previously (C17), rederived here: the noiseless supplied-corner law.** Fix n≥3, 1≤T≤n+1, standard independent bit mutation at rate 1/n, p=0, ascending own-parent breeders, exact filled-cardinality neighborhoods and non-worsening observed Tchebycheff replacement. Supply ideal extrema (0,n), stored b_k=k, true w_0=2 and w_k=k for k≥1; initialization costs zero evaluations. Let F_t reveal the supplied genotypes/state and all consumed masks through attempt t, and let τ be the first sweep boundary at which all true weights equal their indices. No conditioning on accepted noise is involved and no drift theorem is invoked.

At ideal extrema the scalar cost is C_k(w)=max{k(n−w),(n−k)w}; it strictly decreases below k and increases above k (with the empty endpoint branches omitted), so k is its unique minimizer. Each pinned recipient can therefore accept only observed weight k; with p=0 its accepted child also has true weight k. Until repair, all slot weights stay at their supplied values. For D_T={i:0∈B_T(i)}, let a(w)=n^(−w)(1−1/n)^(n−w). Conditional on any unsolved history in F_t, donor i generates zero with probability a(w_i), regardless of genotype identity. Multiplying conditional failure probabilities across the eligible donors yields q_T=1−∏_{i∈D_T}(1−a(w_i)). This remains the same in every unsolved sweep. Once zero is repaired, true alignment persists. Thus Pr(τ>s)=(1−q_T)^s for integer s≥0, Eτ=1/q_T, and E[attempts]=(n+1)/q_T. Summing the survival probabilities through H−1 gives E[min(τ,H)]=[1−(1−q_T)^H]/q_T; multiply by n+1 for restricted attempts.

For T=1, q_T=a(2)∼1/(en²), giving mean attempts ∼en³. For every T≥2, donor 1 contributes a(1)∼1/(en). All other weights are at least two, with at most two slots at each weight; their probabilities sum to O(n^−2), uniformly in T, by the geometric ratio a(w+1)/a(w)=1/(n−1). Hence q_T=a(1)+O(n^−2) uniformly and mean attempts/n²→e uniformly over 2≤T≤n+1. This theorem concerns the supplied inconsistent true/stored corner state at zero noise, not ordinary uniform initialization.

**Mechanically checked boundary refinement.** For non-full T<n+1: if T=2m+1, D_T={0,…,m}; if T=2m, D_T={0,…,m−1} plus {m} only when m is odd. For full T=n+1, D_T={0,…,n}. The contiguous recipient interval starts at clamp(i−floor((T−1)/2)−1_{T even and i odd},0,n+1−T); it contains zero exactly under those conditions. Literal alternating neighborhoods verified the formula in all 2,142 (n,T) cells for 2≤n≤64. In particular non-full T=2,3,4 all give D={0,1}; larger even T need not add an endpoint donor. This is a finite mechanical check plus an algebraic derivation, not independent adversarial review of a new noisy theorem.

**Empirical corner calibration, kept separate.** All eight corner cells have 12/12 exact observations, no caps or missing trials. At n=8, means for T=1,2,3,9 were 1,959.0 / 207.8 / 183.8 / 177.0 attempts; at n=16, T=1,2,3,17 gave 12,775.5 / 511.4 / 1,158.8 / 420.8. The n=16,T=3 mean lies above its pointwise model-predictive range [349.9,1,116.3]; the other seven fall within theirs. This finite discrepancy must be retained. Eight separate 95% predictive ranges do not form a 95% simultaneous test, and 12 geometric observations have substantial variance. T=2 and T=3 have exactly equal theoretical laws despite unequal sample means. No corner observation enters the main estimate.

**Contradicted (C18), mechanically reproduced.** At n=2,p=0, initial genomes (00,00,01), stored true labels, moving initial reference (0,1), and ascending breeders, use mutation masks (01,01,10). T=1 gives weights (0,0,1)→(0,1,1)→(0,1,2); T=3 gives (0,1,1)→(0,0,1)→(0,2,2). Every mask has positive probability under standard-bit or one-bit mutation. Larger T can delay the first exact boundary under this coupling; this does not compare expectations. An independent literal-bit implementation and the unchanged C++ deterministic step interface agree.

**Mechanically checked noisy objections.** Before S, one shared erroneous observation can corrupt several slots: n=2,T=3, true/stored weights all zero, extrema (0,0), breeder 0 proposes true zero observed as one. Slots 1 and 2 both accept, producing true (0,0,0), stored (0,1,1). After S, all labels stay pinned and a shared observation can be accepted only by its single target slot. Nevertheless later breeders can undo a repair: at n=6,T=5 from the supplied corner, donor 0 proposes (true,observed)=(2,2), donor 1 proposes (0,0), then donor 2 proposes (1,0). The population is fully true-correct after donor 1 and ends the sweep at (1,1,2,3,4,5,6) if remaining breeders make noiseless copies. These events have positive probability for standard-bit mutation and activated bitwise noise whenever 0<p<1. The deterministic literal/native check reproduces both examples.

**Open noisy extension; candidate bound, not independently reviewed.** With ideal pinned labels and p=c/n, after donor 1 repairs slot zero let L=|D_T∩{2,…,n}|. Condition only on the history through that repair. Each remaining eligible evaluation has an independent activation gate, so the event that all L gates are inactive has conditional probability (1−p)^L; on that event no later donor reinfects slot zero. Thus the endpoint survives to the boundary with probability at least (1−p)^L≥1−Lp. For fixed T, L=O(T); for non-full T=2,3,4, L=0. This does not control errors in other coordinates or the time spent with donor 1 at the wrong true weight. Globally there are n+1 activation opportunities per sweep, not merely L. A one-slot survival bound cannot establish simultaneous correctness.

Two precise conjectures remain, without promotion: (1) at n=512 and p=1/(64n), the predeclared ratio mean(T=1)/mean(T=23) exceeds one; an eligible holdout interval wholly below one would oppose it, while any interval whose lower endpoint is ≤1 fails the registered replication criterion. (2) From the supplied ideal/pinned single-corner state, for every fixed c>0 and integer T≥2 there exist 0<A(c,T)≤B(c,T)<∞ and n₀(c,T) such that A n²≤E[attempts to simultaneous true alignment at a boundary]≤B n² for all n≥n₀, under standard-bit mutation and activated bitwise noise p=c/n. A rigorous sequence of normalized expectations tending to zero or infinity would falsify the latter; finite fitted slopes cannot decide it. A proof still needs control of donor corruption and the joint repair process. No independent proof scrutiny was performed in this single-agent activation, so no new noisy theorem is asserted.

**Literature scope and next discriminating check.** Benjamin Doerr, Moaad Elmoutassim, Martin S. Krejca and Guy Mushiata Kibulu, *Understanding the Co-evolutionary Solution Exchange of the MOEA/D: Already the Smallest Communication Radius Gives the Best-Possible Speed-Up* (2026), [arXiv:2610.35373v1](https://arxiv.org/html/2610.35373v1), DOI 10.48550/arXiv.2610.35373, establishes the noiseless ideal-reference radius/archive result. This campaign uses stored prior noise, moving extrema, filled cardinalities and simultaneous true assignment. The distinction prevents direct theorem transfer; see [the repository comparison](../../PAPER_COMPARISON.md). A bounded title/identifier and MOEA/D/OneMinMax/noise search on 2026-11-09 found no newer directly matching theorem; that is not a novelty claim.

The next useful mechanism observable is the fraction of the T=1-to-sharing mean reduction occurring before S versus after S, alongside actual external pinned-endpoint repairs; the current primary data put the entire observed difference before S and have no such repairs. A future independently registered diagnostic should distinguish earlier reference discovery U from faster stored-label alignment S−U and examine the capped stored-alignment tail. Replication requires an eligible independently specified continuation or new campaign; altering this gate after seeing the cap would not validate the frozen two-stage claim. For theory, first bound how long donor 1 is corrupted under sharing, then the joint boundary error process. Merely improving the endpoint's first-hit hazard leaves the reinfection counterexample unresolved.

**Activation accounting.** The worker produced all sampling and publication. Its receipted engine-process time totals 38.394 s (main 37.525 s); these sums exclude tests, analysis, compilation, publication and agent work. No paid resources or cloud jobs were used by this agent. This note is the only intended tracked agent change; deterministic checks, replay, supplementary arithmetic and drafts remain in ignored scratch. The agent's first bootstrap audit needed integer JSON seed serialization and the frozen observed-then-capped ordering to reproduce exact percentiles; both were corrected in scratch, after which all checks passed. No receipt validation failure was found. The key remaining risks are absent holdout, one censored high-noise arm, rare tails, exploratory multiple comparisons, and lack of an independently checked noisy proof.
