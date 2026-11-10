# Round 18 durable claim/status supplement

**C42 — proved within the supplied pinned model, after independent audit:**
for even n>=4, the T=2 ordered response ORRR satisfies
`|ORRR| <= 2048 (n+1)^3 (20n)^4/q = O(n^8)` in sweep units,
where `q=1-(1-d(2,0))(1-d(1,0))`. This upgrades the round-17 candidate
on the basis of the analytic argument in [audit.md](audit.md), separately
from finite exact checks.

The audit validates the compensated centering identity, the three-overwrite
support budget, the acceptance-weighted marked second response and the
first orphan's actual entrance factor. It explicitly distinguishes the
unrestricted clean equation from the killed occupation inverse. Negative
unchanged and suppressed-clean branches are retained, and the orphan-fed
last pair is not assumed independent of the orphan. The isolated-pair
second-response candidate is not used.

**Mechanically checked C42:** a new solver obtains uncentered responses
before taking matched-phase differences. It imports no previous solver.
The exact ORRR fractions at n=4 and n=6 agree with the published fingerprints,
adding the independent n=6 oracle missing from round 17. Separate positive
active/clean expectation checks test the intermediate majorants, rather than
only the final signed response. Full counts and finite grid scope are in
[verification.json](verification.json).

The new checks cover 4,956 response cases and 31,052 phase cases, with
75,006 identities and 116,176 inequalities (98,896 response inequalities
plus 17,280 scalar acceptance inequalities). Support enumeration covers
13,771 patterns and 134,517 edges. All 622 published centered fingerprints,
four flux fractions and 24 orphan-entrance response records match.

**C43 — contradicted shortcut, independently checked:** omitting the boundary
compensation gives a nonzero residual. At n=4, the first two compensations
are approximately 2.071469580410 and 2.835341435438. The exact residual equals
the compensation; degree zero likewise requires lambda0=1. Matched-phase
centering and boundary-only runtime killing remain essential.

**C40 — conjectured, unresolved here:** polynomiality of the complete
fourth-order gap still requires RRRR and the other untreated mixed words.
The audited RROO bound and now-audited ORRR bound do not supply a uniform
higher-order remainder, fixed-positive-c ordering, or an ordinary-initialization
theorem. The earlier exponential positive-residence counterexamples stand.
The isolated-pair second-response estimate remains a candidate proof.

**Mechanically checked dependencies:** relevant earlier registration,
receipts, seed separation and proof checks replay. No plan/receipt repair
was needed. Published n=256 and separate n=512 ratios remain
2.327639 [2.050148,2.674642] and 2.339095 [2.085387,2.596468], with 24 and
32 complete observations per arm and their prior approximate nominal 95%
bootstrap interpretation. The original cap, preregistration, 240 missing
blocked holdout rows and inconclusive original two-stage decision are
unchanged. No new empirical trial or scientific seed was generated.

This was an offline, serial one-CPU audit with no literature-novelty claim,
paid resources, source-PDF edits, commit or push. [checks.json](checks.json)
and [provenance.json](provenance.json) record final tests, preservation and
elapsed time. Raw execution logs are outside this publication bundle.

The best next bounded question is whether RORR has a polynomial bound that
retains both the first regular acceptance mark and the later orphan entrance
factor. The newly audited marked response supplies a plausible tool, while
the orphan's interior insertion position is not covered by ORRR or RROO.
