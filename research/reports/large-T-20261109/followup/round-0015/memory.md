# Round 15 durable claim/status supplement

**C35 — mechanically checked:** the fourth coefficient D_n of the supplied
pinned-corner T=3 minus T=2 sweep-boundary mean gap is +1.0175850894053977
at n=3, -1.2004132916762715 at n=4, and +0.6027534143674425 at n=5.
It is the fourth derivative divided by 24. A phase-cycle implementation
independently matches all four n=3,4 arm coefficients, and the n=4 sixteen
ordered R/O terms sum exactly to the T=2 fourth coefficient. No finite-grid
fit or asymptotic inference is made.

**C36 — proved, supplied-model scope:** the T=3 arm alone has
|d_{3,n}|<=122880000 n^9. For n>=5, at most five errors leave a correct
frontier and the audited clean repair argument applies. Exact calculations
cover n=3,4. This is not a bound on the difference D_n.

**C37 — contradicted shortcut; proved negative result:** retaining both
mutation and acceptance factors in a positive two-birth entrance does not
make its third clean residence polynomial. For odd n>=9 an explicit path
from the supplied corner to the last pair with both weights (n-1)/2 has
w/q_E^3 >= 2^n/[12288 n^4(n+1)]. This is a positive majorant, not a lower
bound on a signed coefficient. Earlier higher-residence obstructions remain
valid.

**C38 — candidate proof, awaiting independent audit:** for an isolated closed
pair with r(z)=d(z,k)+d(z,k+1), the local second response v2, in attempts,
satisfies r(x)r(y)|v2((x,y),phase)| <=2176(32n)^3. The proof retains
rho(z)^2<3r(z), the small activated escape rate, and signed holding terms.
It does not replace the global population response by independent local
hitting times. The even-n orphan-fed pair is outside this isolated model.

**C39 — candidate proof, awaiting independent audit:** the ordered full-T=2
word RROO has absolute value at most 5000(n+1)^2(20n)^4/q. Correct-orphan
stationarity bounds the second excess by 5M^2 for a closed bad pair; a
separate stopped-reward argument gives 20(20n)^3 for an orphan-fed bad
last pair, at every phase. This addresses RROO only.

**C40 — conjectured, unresolved here:** the full fourth gap D_n is polynomial
in n. A complete bound on RRRR and the other thirteen mixed fourth words
is still absent. ORRR, with three nonorphan insertions after an orphan
birth, is a concrete remaining transfer problem. No uniform fifth-and-higher
remainder, new noise window, fixed-positive-c ordering, or ordinary-
initialization result follows from this round.

**Mechanically checked dependencies:** round 14 and its recursive earlier
registration/receipt replay reproduce. No missing plan or receipt required
repair. The empirical n=256 ratio 2.327639 [2.050148,2.674642] and the
separately registered n=512 restricted-mean ratio 2.339095
[2.085387,2.596468] are unchanged, with 24 and 32 complete observations
per arm respectively and their earlier approximate nominal 95% intervals.
The original cap, preregistration, 240 missing blocked holdout trials and
inconclusive two-stage decision remain intact. No new scientific trajectories
or seeds were generated. This offline work makes no novelty claim.

The full derivations, limitations and falsifiers are in [proof.md](proof.md).
Finite checks, code and exact rational fingerprints are linked from
[README.md](README.md). The new local and mixed all-n arguments have no
independent reviewer yet.
