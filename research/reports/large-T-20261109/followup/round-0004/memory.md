# Round 4 durable claim supplement

**C19 unchanged: original two-stage decision inconclusive.** Original n=256
T=1/T=16 ratio is 2.327639 [2.050148, 2.674642]; all 240 original holdout rows
remain missing and blocked by the original main cap. The original protocol,
seeds and evidence remain unchanged.

**C20 unchanged: finite restricted comparison empirically supported.** The
separate n=512 T=1/T=23 study has 32/32 complete main observations per arm,
ratio 2.339095 [2.085387, 2.596468], at p=1/32768 and H=38,341. The preceding
independent auditor reproduced exactly in this round, with 6,914 comparisons.
Its six output files match byte for byte. No dependency repair was needed.

**C21 proved locally; mechanically checked: donor occupation and endpoint
boundary repair.** In the supplied pinned standard-bit/bitwise-noise process,
let a=p/(1-2p), I_k={i:k in B_T(i)}, d_k=|I_k| and start donor 1 correct.
For any integrable boundary stopping time sigma, its incorrect own turns B_1
satisfy E B_1 <= d_1 a E sigma. Its all-attempt occupation O_1 satisfies
E O_1/(n+1) <= d_1(a+p) E sigma. For T>=2 and d_1 a<1, the first endpoint
boundary-repair time has mean at most
1/[(1-d_1 a)(1-p)^(d_0-1)D(1,0)]. Thus at p=c/n, fixed c,T, donor 1 spends
only O_{c,T}(1) expected sweep-equivalents incorrect before an O(n)-sweep
endpoint repair. These are stopped occupation bounds, not conditional
acceptance probabilities or persistence claims.

**C22 conjectured with a complete candidate proof; independent review pending.**
For every fixed c>0,T>=2, the supplied single-corner simultaneous boundary
alignment time is Theta_{c,T}(n^2) attempts. At T=1 it is Theta_c(n^3).
The new error-particle construction proposes an arbitrary-pinned-state bound
E tau <= C sum h_k(w_k), with finite C depending on n,p,T and approaching
exp(cT) for fixed c,T. Combining it with C21 and a quiet-donor lower bound
gives the asserted orders. The precise outstanding review obligations are
the tagged coupling with within-sweep births, generation-work estimate,
independent-family empty-state renewal, and restart at the endpoint time.
No new empirical evidence is used to promote this conjecture to a theorem.

**C23 proved locally: T=1 first endpoint repair.** Under the same supplied
state and p=c/n, the local pinned repair time from weight 2 is asymptotic to
e n^2 turns, hence e n^3 attempts to its boundary hit. Direct upper/lower
bounds are in [proof.md](proof.md). This is distinct from legacy C6/C7.

**Mechanically checked.** There are 202 exact local-kernel cases, 6,628 kernel
comparisons, 2,142 neighborhood cells, 263,169 one-step tagged couplings and
24 exact renewal checks. All 95 repository, 15 new proof, and 16 prior-audit
tests pass. The reinfection and donor-corruption counterexamples persist.
New analytic constants in [bounds.csv](bounds.csv) are not measurements.

**Scope gaps retained.** Fixed-c T=3 was stated in the theory note but its
revised appendix was not supplied locally; it was not used as a theorem
dependency. The new candidate proof is self-contained. Ordinary initialization,
corner-entry frequency, growing T, tails, and monotonicity remain outside this
result. No scientific trial was generated; any future empirical study still
needs a separate plan published in a prior round and independent seeds.

See [proof](proof.md), [verification](verification.json),
[prior evidence](dependency.json), [source audit](sources.json), and
[reproduction guide](README.md). The next distinct task is independent
adversarial verification of the new coupling and renewal argument.
