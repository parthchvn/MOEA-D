# Round 19 durable claim/status supplement

**C44 — conjectured all-n bound, with a complete candidate proof:** for even
n>=4 in the supplied pinned T=2 model,
`|RORR| <= 1024 (n+1)^3 (20n)^4/q < 4e9 n^8` sweeps, with
`q=1-(1-d(2,0))(1-d(1,0))`. [proof.md](proof.md) retains the first
regular acceptance a=d(x,k) and the orphan entrance d(n,y)d(y,n). It uses
the already-audited round-18 marked two-R estimate, followed by a new
baseline-flux decomposition. The new all-n assembly awaits independent
analytic audit; finite calculations do not upgrade it to a theorem.

**Mechanically checked C44:** exact RORR values (rounded) are n=4: 0.15827832927629937; n=6: 0.2700577089365307.
The new ordered sweep/suffix solver and the previously published direct
phase solver agree exactly at both sizes. The n=4 value also matches the
published fourth-order fingerprint. Counts are 2,567 exact
identities, 7,814 inequalities, 864
phase-oracle matches, 788 marked phase cases,
5,116 centered cases, and 664
joint-entrance envelopes. The finite families exhaust all first regular
targets/children, orphan values and phases at n=4,6 from corner/aligned
origins. This is not an all-population or all-n check.

**C45 — contradicted shortcut:** deleting the orphan baseline before O
loses beta*H1(C). The exact nonzero missing contributions, rounded, are
n=4: 1.9615322524689527; n=6: 3.785419437135514. At an aligned live final turn O D2=0 while O H2=beta.
[shortcuts.csv](shortcuts.csv) preserves exact fingerprints, including the
incorrect full-word value produced by the omission. The negative unchanged
branch and terminal-sweep contribution must both remain.

**C40 — conjectured and unresolved here:** the full fourth-order gap still
requires the untreated words, including RRRR, and its uniform higher-order
remainder remains unbounded here. The audited RROO and ORRR bounds plus the
new RORR candidate do not establish fixed-positive-c ordering at p=c/n,
an enlarged noise window, or ordinary-initialization behavior. The earlier
positive exponential-residence obstructions remain valid. The isolated-pair
second-response argument is still a candidate and is not used.

**Mechanically checked dependencies:** all eight round-18 outputs regenerate
byte for byte, recursively including the relevant prior plans, receipts,
seed separation and proof checks. No dependency repair was needed. Published
receipts limit the chronology audit because earlier private logs are absent.
[dependency.json](dependency.json) records the exact scope.

**Empirically supported, unchanged:** the original n=256 ratio remains
2.327639 [2.050148,2.674642], with 24 complete observations per primary arm.
The separately registered n=512 restricted-mean ratio remains
2.339095 [2.085387,2.596468], with 32 complete observations per arm and the
previous approximate nominal 95% bootstrap interpretation. Distributions
and phase denominators are retained in the dependency record. The original
main cap, 240 missing gate-blocked holdout trials, preregistration and
inconclusive original two-stage decision are preserved. No new scientific
trajectory or seed was generated.

This offline one-CPU turn produces a mathematical candidate and deterministic
checks, not a new stochastic experiment or current-literature novelty claim.
[checks.json](checks.json) and [provenance.json](provenance.json) record actual
tests, elapsed time, source hashes and preservation. Raw logs remain outside
this bundle. No paid resources, PDF edits, commit or push occurred.

The next distinct question is whether an independent audit validates the
RORR baseline-flux decomposition, phasewise orphan-turn count and two
entrance estimates, since those new steps now carry the polynomial bound.
