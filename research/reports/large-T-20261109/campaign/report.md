# Larger-neighborhood campaign

The primary endpoint is first exact assignment at a sweep boundary. Evaluations include n + 1 initial observations for uniform starts. Each subsequent sweep costs n + 1 evaluations. All cohorts and stopping events are retained in cells.csv.

| Stage | Planned | Verified receipts | Missing | Role |
|---|---:|---:|---:|---|
| smoke | 62 | 62 | 0 | mechanics only |
| calibrate | 102 | 102 | 0 | timing and corner controls |
| main | 1080 | 1080 | 0 | main grid |
| holdout | 240 | 0 | 240 | predeclared validation |

## Finite-size contrasts

Ratio = mean exact evaluations at T=1 divided by the mean at T=ceil(sqrt(n)). Values above one favor the larger neighborhood. Each arm uses independent trials. Intervals are deterministic, pointwise 95% percentile bootstraps with 10,000 independent-arm resamples; no multiplicity correction. The primary contrast is n=256, factor=1/64, T=1 vs 16. Independent confirmation is n=512, factor=1/64, T=1 vs 23. Other intervals are exploratory. Repeated seeds are rejected.

Inconclusive — a primary or confirmation arm has cap-censored or missing exact times.

| Stage | n | Noise factor | T | Mean ratio [95% interval] | Restricted ratio |
|---|---:|---:|---:|---|---|
| main | 64 | 0 | 8 | 2.276 [1.860, 2.809] | 2.276 |
| main | 64 | 0.015625 | 8 | 2.206 [1.888, 2.598] | 2.206 |
| main | 64 | 1 | 8 | cap censored | 2.267 |
| main | 128 | 0 | 12 | 2.140 [1.791, 2.556] | 2.140 |
| main | 128 | 0.015625 | 12 | 2.282 [2.019, 2.599] | 2.282 |
| main | 128 | 1 | 12 | 2.713 [2.394, 3.076] | 2.713 |
| main | 256 | 0 | 16 | 2.111 [1.817, 2.444] | 2.111 |
| main | 256 | 0.015625 | 16 | 2.328 [2.050, 2.675] | 2.328 |
| main | 256 | 1 | 16 | 2.449 [2.120, 2.845] | 2.449 |
| holdout | 512 | 0 | 23 | missing receipts | [0.000, 38342.000] |
| holdout | 512 | 0.015625 | 23 | missing receipts | [0.000, 38342.000] |
| holdout | 512 | 1 | 23 | missing receipts | [0.000, 38342.000] |

## Local throughput benchmark

Aggregated over received timing trials; elapsed cost includes engine process start. Comparisons count recipient tests.

| n | T | Receipts | Attempts/s | Recipient comparisons/s |
|---:|---:|---:|---:|---:|
| 128 | 1 | 1/1 | 1,172,491 | 1,172,491 |
| 128 | 129 | 1/1 | 888,188 | 114,576,195 |
| 256 | 1 | 1/1 | 2,496,566 | 2,496,566 |
| 256 | 257 | 1/1 | 1,235,090 | 317,418,085 |
| 512 | 1 | 1/1 | 4,666,675 | 4,666,675 |
| 512 | 513 | 1/1 | 984,586 | 505,092,545 |

## Supplied-corner benchmark

With inactive noise and all stored labels pinned, only slot zero needs repair. Each sweep has independent success opportunities from its eligible donors. The analytical restricted expectation uses the resulting geometric law and each cell's actual cap. The last column is a central model-predictive 95% range for the planned sample mean, using 10,000 deterministic Monte Carlo draws of independent capped geometric samples of that size. No initialization evaluations are charged. See research/LARGE_T_THEORY.md for the derivation.

| Stage | n | T | Receipts / planned | Restricted mean evals [lower, upper] | Analytic | Prediction range |
|---|---:|---:|---:|---:|---:|---:|
| calibrate | 8 | 1 | 12/12 | [1959.0, 1959.0] | 1283.4 | [666.0, 2115.9] |
| calibrate | 8 | 2 | 12/12 | [207.8, 207.8] | 161.4 | [86.2, 260.2] |
| calibrate | 8 | 3 | 12/12 | [183.8, 183.8] | 161.4 | [87.0, 262.5] |
| calibrate | 8 | 9 | 12/12 | [177.0, 177.0] | 141.8 | [74.2, 228.0] |
| calibrate | 16 | 1 | 12/12 | [12775.5, 12775.5] | 10742.1 | [5502.1, 17554.0] |
| calibrate | 16 | 2 | 12/12 | [511.4, 511.4] | 672.4 | [358.4, 1088.0] |
| calibrate | 16 | 3 | 12/12 | [1158.8, 1158.8] | 672.4 | [349.9, 1116.3] |
| calibrate | 16 | 17 | 12/12 | [420.8, 420.8] | 631.1 | [324.4, 1027.1] |

## Observation horizon and computational work

At cap K, the restricted cost is initialization + (n+1) min(first-hit sweep,K). A missing receipt supplies no confirmed trajectory prefix. For that planned trial the restricted cost is bounded by initialization and initialization + (n+1)K. First exact assignment can occur before S, when stored labels have not all reached their targets. The shaded range in a runtime plot (when present) is a missing-data identification range, not a sampling interval. Completion plots count confirmed hits divided by all planned trials. Unrestricted means and quantiles are withheld if any required trial is missing or the event is cap-censored. Even fully observed finite samples cannot exclude rare longer trajectories.

For each event, cells.csv gives lower and upper restricted-mean logical comparison counts. At boundary s these equal T(n+1)s. Initialization contributes zero recipient comparisons. Wall time in work.csv covers each entire receipted run through the post-S endpoint or cap. An earlier exact boundary has no separate elapsed timestamp.

The phase columns in work.csv are mean_observed_U_sweeps (first ideal reference), mean_observed_S_minus_U_sweeps (from U to stored alignment), and mean_observed_phase_II_sweeps (from S to first post-S exact assignment). Each includes only trajectories that reached its end boundary. Its observed_* count gives the denominator and planned gives the total scheduled. The three durations sum to the post-S hitting sweep on a single completed trajectory. Cell means using different observed sets need not add. True/stored mismatch counts and maximum absolute errors at U and S use the same boundary-conditional convention. First corner donor counts classify the first observed endpoint-zero repair as own or external.

## Plots

Runtime and completion plots show uniform, moving-reference bitwise/bitwise cells. Each panel holds dimension and noise factor fixed. Calibration figures compare capped corner means with the geometric model and show measured throughput. Observed corner means are plotted only when all receipts are present. All trial types appear in the CSVs.

![runtime-smoke](runtime-smoke.png)
![completion-smoke](completion-smoke.png)
![corner-calibrate](corner-calibrate.png)
![throughput-calibrate](throughput-calibrate.png)
![runtime-main](runtime-main.png)
![completion-main](completion-main.png)
![runtime-holdout](runtime-holdout.png)
![completion-holdout](completion-holdout.png)
