# Round 6 claim and status supplement

**C19 unchanged:** the original two-stage decision remains inconclusive.
Its n=256 primary ratio reproduces, one main trajectory remains capped, and
all 240 original holdout trajectories remain missing and gate-blocked.

**C20 unchanged, empirically supported:** the separately registered n=512
restricted ratio remains 2.339095 [2.085387,2.596468], 32 complete trajectories
per arm. Prior committed registration, receipts, seed separation and 6,914
arithmetic comparisons reproduce. No new scientific sampling occurred.

**C21–C23 unchanged:** the earlier donor occupation, fixed-T supplied-corner
orders and T=1 endpoint contrast retain their published round-5 scope. This
round's derivative argument does not assume the error-family theorem.

**C24 unchanged, contradicted universal expectation monotonicity:** the
published n=3,p=1/192 T=3 slowdown survives exact certificate replay.

**C25 new, proved finite-n response identity; mechanically checked values:**
for every fixed n≥3 in the ideal/pinned supplied-corner process,
`m_3(n,p)−m_2(n,p)=p A_n+O_n(p²)`. Equations (3)–(6) in
[derivation.md](derivation.md) compute A_n using at most two erroneous slots
after one derivative insertion. The direct endpoint contribution cancels.
A_3=0.22213184717778317… is independently checked by all 256 population states
for each T. Exact arithmetic gives A_n<0 at every n=4,…,10. Thus the n=3 sign
does not persist across all sizes. At n=3 the recipient-1 term is +0.3131733141
and recipient-2 term is −0.09104146695; the two other terms cancel exactly.

**C26 new, candidate asymptotic theorem, not yet independently reviewed:**
`A_n=−(n/2)log n+O(n)`. The argument isolates `n/[2(k+1)]` contributions from
slow-directed T=2 pairs near the left edge, and their right-edge counterparts.
Summing each parity-spaced edge gives `(n/4)log n`; T=3's interior repair
contributions and all exceptional sites total O(n). Deterministic numerical
evaluations through n=1024/1025 are checks, not the proof. Parity changes the
O(n) contribution. In attempts the candidate coefficient is
`−(n²/2)log n+O(n²)`.

**Unresolved here:** independent review of the asymptotic estimates, negativity
at every n≥4, a Taylor remainder uniform in n, and expectation ordering at
fixed positive c when p=c/n. The finite-n identity alone settles none of these.
The next bounded step is independent scrutiny of the candidate asymptotic
proof, particularly its uniform edge estimates and exceptional-site bounds.
After that, uniformity of the remainder decides whether the negative
derivative predicts a finite-noise ordering in the corner theorem's scaling.

**Falsifiers:** a full-state derivative disagreement invalidates C25's
reduction; a rigorous sequence with A_n/(n log n) not tending to −1/2 invalidates
C26. Incorrect boundary killing, treating an even-n T=2 orphan as a pair,
discarding rare-but-long repair states, or conditioning on future lifetimes
are concrete failure modes covered or identified by this checkpoint.

This is an offline, model-specific result with no novelty claim. All original
preregistration/evidence files and PDFs are preserved. Details and executable
checks are linked in [README.md](README.md).
