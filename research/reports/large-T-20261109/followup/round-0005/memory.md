# Round 5 claim and status supplement

**C19 unchanged — original registered two-stage decision inconclusive.**
The original n=256 restricted comparison is 2.327639 [2.050148, 2.674642].
One original high-noise main trajectory is capped; all 240 original holdout
trials remain missing and gate-blocked. No original gate, cap, seed or
preregistration changed.

**C20 unchanged — empirically supported finite separate comparison.**
The independently preregistered n=512,T=1/T=23 ratio is
2.339095 [2.085387, 2.596468], with 32/32 complete observations per arm,
p=1/32768 and horizon 38,341 sweeps. Four separately seeded smoke trials are
excluded. Registration a5449de predates measurement. The prior auditor again
reproduces 6,914 checks and the recorded seed separation. These results do not
establish an unrestricted expectation ordering or explain the supplied corner.

**C21 unchanged — proved, now adversarially audited.**
The pinned-process donor occupation bounds and endpoint boundary-repair upper
bound survive explicit predictable-indicator and stopping-time checks.
Acceptance conditioning is not used. All hypotheses and notation are in
[audit.md](audit.md).

**C22 upgraded from candidate to proved for its stated pinned process.**
The analytic audit validates the tagged error-family construction, finite-time
existence, expected generation work, boundary-work charge, independent-family
product, defective-renewal calculation and fresh-forest restart. Thus fixed
c>0 and fixed T>=2 yield Theta_{c,T}(n^2) expected simultaneous boundary-alignment
attempts from (2,1,2,...,n) with ideal extrema and labels b_k=k, versus
Theta_c(n^3) at T=1. The finite sufficient conditions are p<1/2,
(T-1)p/(1-2p)<1 and d_1 p/(1-2p)<1 for the T>=2 corner upper bound.
This promotion is based on the analytic proof, not finite numerical checks.

**C23 unchanged — proved T=1 local contrast.**
At p=c/n the endpoint's first repair from true weight 2 is asymptotic to
en^2 local turns, hence en^3 boundary-counted attempts. The T=1 coordinate is
autonomous; this persistence-through-the-rest-of-its-sweep statement does not
apply to sharing.

**C24 new — contradicted universal expected monotonicity in T.**
In the pinned supplied corner at n=3,p=1/192, certified expected simultaneous
boundary times are 4.7659580192 sweeps for T=2 and 4.7671266818 for T=3.
The difference has a strictly positive rational interval around
0.001168662645 sweeps. Both endpoint-donor sets are {0,1}. This strengthens the
negative evidence beyond a pathwise common-mask example, within a different
supplied-state scope. It does not refute C22 or order ordinary-initialization
expectations. [Certificates](certificates.csv), [verifier](verify.py).

**Additional contradicted shortcuts.** An accepted observation 0 from true
parent weight 2 at n=3,p=1/192 has posterior true-error probability 32/5197>p.
A positive-probability n=3,T=2 path becomes aligned inside a sweep but ends with
an interior error. Neither shortcut is used by the audited proof.

**Mechanically checked, not proof by enumeration.** 25 full-state cells,
4,339 population/cell combinations, 3,571 arbitrary-state upper comparisons,
1,644 occupation comparisons, and 242,064 bounded forest transitions pass.
The forest search is capped at two particles for expansion, explicitly not
exhaustive over arbitrary histories. No scientific trajectory was sampled.

**Remaining questions.** Ordinary initialization and its pre-S stages,
growing T, useful tails, and typical corner-entry frequency are unaddressed.
The fixed-c T=3 revised appendix remains unavailable and unused. The next
mathematical question is the small-noise expansion of the T=3 minus T=2
corner-time gap: the new finite witness shows that identical noiseless donors
do not imply equal noisy completion laws. New empirical studies still need a
plan published in a prior round and independent seeds.
