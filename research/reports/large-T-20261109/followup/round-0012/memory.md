# Round 12 durable checkpoint

**C31: proved under the pinned closed-pair assumptions; independently audited.**
Round 11's phase potential and one-block full-population extension survive
the independent analytic and implementation audit in [audit.md](audit.md).
For 0<=p<1/6, R_D=(I-P_DD)^(-1),
P_SD R_D 1<=4p/(1-6p), and P_AD R_D 1<=2p^2/(1-6p).
Entry-weighted exit mass is at most 2p and p^2, respectively. Every
single-error pair state has mean boundary alignment time at most
3n(1+4p/(1-6p))/(1-p)^2 sweeps. This does not bound residence conditional
on entering D, or give a polynomial bound from every D state.

The proof retains the phase change, increased active holding mass, and
midpoint repair/reinfection. The full extension uses
sum_j P_DD^j tensor P_rest^j and the actual time reward. It is conditional
on the full starting state and does not need independence of the initial
coordinates. The rest may have internal dependence. The selected pair
must have no incoming or outgoing communication to the rest. The last
even-n pair, fed by the orphan, is excluded. No T=3 transfer is made.

**C32: contradicted strengthening; the counterexample proof is now audited.**
For the last pair at odd n, E1=P_SD'(0) and S0=(0,n),
(E1 R_D(0)^2 1)(S0)>=n^(n-4)/32. The explicit n=33 path contributes
more than 1.0465e43, despite its small first-residence contribution.
Therefore a polynomial bound on all acceptance-weighted higher residence
moments is false. This does not refute cancellation in signed derivatives
or a full supplied-corner Taylor remainder.

**Mechanically checked:** exact finite interval certificates, independent
published pair solves, joint tensor rows including even-n orphan feedback
inside the rest, and full-population Schur hitting equations. See
[verification.json](verification.json), [phase.csv](phase.csv),
[pair.csv](pair.csv), [tensor.csv](tensor.csv), and [moments.csv](moments.csv).
The full-state calculation also detects the incorrect frozen-rest exit
law and omitted time reward. Analytic proof, not finite extrapolation,
carries the general result.

**Inherited evidence preserved:** recursive replay validates the prior
registration and receipts and their seed separation. No dependency repair
was needed. The original n=256 estimate and separate n=512 restricted-mean
estimate remain unchanged. The original preregistration, capped main trial,
240 missing blocked holdout trials, and inconclusive original two-stage
decision are preserved. Private earlier per-trial execution logs remain
unavailable; the chronology limitation is unchanged.

**Unresolved here:** the remaining global inverse and its signed derivatives,
synchronization under reinfection, last-pair orphan feedback, overlapping
T=3 neighborhoods, and a useful uniform third-and-higher remainder. A
validated first-moment elimination is not a Taylor theorem. No enlarged
noise window, ordinary-initialization theorem, new tails, novelty claim,
or current-literature completeness assertion is made.

This round used deterministic algebra and tests, not new scientific
trajectories. The prior-round publication requirement for sampling is
preserved. Curated source, outputs, receipts and reproduction commands are
in [README.md](README.md). Raw logs remain outside this bundle.
