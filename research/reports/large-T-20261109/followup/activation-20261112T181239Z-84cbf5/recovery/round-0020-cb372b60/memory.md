# Round 20 durable claim/status supplement

**C44 — proved within the supplied pinned model, after independent audit.**
For even n>=4, filled T=2, the ordered response obeys
`|RORR| <= 1024 (n+1)^3 (20n)^4/q < 4e9 n^8` sweeps, where
`q=1-(1-d(2,0))(1-d(1,0))`. This upgrades the round-19 candidate on the
basis of [audit.md](audit.md), separately from finite exact checks.

The audit rederives the compensated marked two-R premise and validates
the orphan baseline, all-phase final-turn occupation and positive-kernel
accounting. The actual orphan entrance d(n,y)d(y,n) cancels the inverse
orphan rate; the first regular acceptance d(x,k) cancels the marked inverse
rate. Both negative branches remain. The orphan-fed last pair is coupled,
not declared independent of the orphan. Boundary stopping is preserved.

**C45 — contradicted shortcut, independently reproduced.** Removing the
baseline before O loses beta H1(C). The missing amounts are approximately
1.961532252469 at n=4 and 3.785419437136 at n=6. The true RORR values are
approximately 0.158278329276 and 0.270057708937; the baseline omission makes
them negative. Exact fingerprints are in [words.csv](words.csv).

**Mechanically checked C44.** A new circular phase recurrence imports no
earlier solver and checks the published rational fingerprints. It also
computes visit and centered-forcing occupations separately. The declared
finite grid is smaller than round 19's at n=6: every target, orphan and
phase, but only children {0,k,n}; n=4 uses all children. Counts and precise
coverage are in [verification.json](verification.json). Numerical agreement
does not establish the all-n proof.

**C40 — conjectured, still unresolved in this project.** The complete
fourth-order gap requires additional words, including RROR and RRRR.
There is still no useful uniform higher-order remainder, fixed-positive-c
ordering at p=c/n, or ordinary-initialization conclusion from this audit.
The isolated-pair second-response argument remains a candidate and is not
used. Earlier positive exponential-residence counterexamples remain valid.

**Mechanically checked dependencies.** Published plans and receipts are
replayed using round 3's independent auditor; its six outputs reproduce
exactly. Round-18/19 source/output manifests and tests are verified; the
marked premise is rederived analytically and checked independently. The
entire earlier theoretical grids are not rerun. No plan or receipt repair
is needed. Private earlier logs remain absent, limiting chronology to
published receipts and committed registration.

**Empirically supported, unchanged.** The original n=256 ratio remains
2.327639 [2.050148,2.674642], with 24 complete observations per primary arm.
The separate registered n=512 restricted-mean ratio remains
2.339095 [2.085387,2.596468], with 32 complete observations per arm.
Intervals retain their approximate nominal 95% bootstrap interpretation.
The original cap, 240 missing gate-blocked holdout trials, preregistration
and inconclusive original two-stage decision are preserved. The follow-up
does not replace the blocked holdout. No new trajectory or seed is drawn.

Cumulative morning progress now includes audited empirical evidence,
polynomial response control through cubic order, and audited fourth-order
RROO, ORRR and RORR bounds. This turn uses one CPU offline, without paid
resources, source-PDF edits, commits or pushes. [checks.json](checks.json)
and [provenance.json](provenance.json) record timing and preservation.

The next distinct question is RROR: can its bound retain both pre-O
regular acceptance factors? Two earlier R insertions can create a slow
pair, so the newly audited N<=20n argument no longer applies directly.
