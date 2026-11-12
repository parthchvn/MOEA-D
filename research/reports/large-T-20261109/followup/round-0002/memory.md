**2026-11-09 follow-up round 2: empirical evidence and durable status supplement.**

The original C19 two-stage comparison remains inconclusive: the published
n=256 result favors T=16, but all 240 original holdout rows are still missing
because the frozen high-noise main gate blocked them. Original preregistration,
holdout, receipts and interpretation were preserved unchanged.

**C20 — empirically supported, finite restricted comparison.** The separately
registered n=512, p=1/32768 comparison of T=1 and T=23 completed all 32 independent
trajectories per arm with no caps or missing receipts, plus four excluded smoke
trials. At H=38,341 sweeps, the restricted-mean evaluation ratio is
2.3390952207, nominal pointwise 95% percentile bootstrap
[2.0853866835, 2.5964682010]. The frozen decision favors T=23. This does not
retroactively clear the old holdout, order unrestricted expectations or prove
any asymptotic benefit. [Plan](plan.json), [receipts](trials.csv),
[summary](summary.json), [checks](checks.json).

**Empirically supported diagnostic, descriptive only.** T=1-minus-T=23 mean
occupied sweeps are 4,462.40625 before U, 1,272.5625 between U and S, and 0.125
after S. P=X in all 64 main observations; one T=1 row has a four-sweep post-S
delay. Every main row has zero pinned-endpoint repairs. The observed difference
is overwhelmingly before S, and is not explained by recorded post-S endpoint
repair. These are not causal or pathwise identities. The prior counterexamples
and stored-noise/joint-repair proof gaps remain live.

**Mechanically checked.** Published round-1 registration verified in ancestor
commit a5449deed0c45f4ff0538fe49d0fa6285a77b809; its prior audit reproduced
exactly and its 68 new seeds are disjoint from 2,420 published seeds. The kernel
was tested first. All 95 repository, 14 registered plan/analysis and 15 new
synthetic wrapper tests passed. New receipt/model/plan hashes and 275 separate
scalar arithmetic checks pass, including zero phase-identity residuals.
All six numerical/plot replay files match byte for byte on the recorded host.
The native kernel and registered analyzer remained unchanged. Single-agent
validation is not independent adversarial review.

The one authorized sampling invocation is consumed. It finished in 16.612791
seconds, with no technical or scientific failure, and no paid resources.
Further sampling requires a new prospective publication. The next useful
question is whether T=3 captures the pre-S savings at n=512 while reducing the
9.83155-fold logical-comparison overhead observed for T=23 versus T=1.
