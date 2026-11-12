**Proved under the pinned clean process:** every filled \(T\ge3\) contains a bidirectional adjacent path. From any state with one correct slot and \(e\) errors, expected simultaneous boundary repair takes at most \(3ne\) sweeps.

**Strong connectivity does not eliminate slow traps.** An explicit all-wrong family has exact first-change mean at least
\[
\frac{\lceil(n+1-T)/2\rceil!}{n+1}.
\]
A factorial upper bound, including an even-\(T\) parity correction, establishes worst-state clean means of \(\exp(\Theta(n\log n))\) for logarithmic and square-root neighborhoods. Full communication creates a correct slot immediately.

Assumptions are supplied ideal reference, pinned target labels, ascending cyclic own-parent standard-bit mutation, and sweep-boundary stopping. These results do **not** establish noisy corner complexity or ordinary-initialization behavior. The earlier forest argument’s exponential factor arises when requiring every artificial error family to disappear simultaneously; that noisy synchronization gap remains.

Verification passed: **105 tests**, compilation, six byte-identical reproduced outputs, 91,518 neighborhood checks, 11,408 exact seed-rate inequalities, and bounded exact repair/trap calculations. All **543 tracked files remained unchanged**.

Saved the [proof](proof.md), [self-audit](audit.md), [results and reproduction guide](README.md), [proposed memory updates](memory.md), and progress/provenance records. Elapsed work: **13 minutes 8 seconds**; final replay: **19.2 seconds**. No paid resources, commits, pushes, or new scientific sampling. The **240 blocked holdout observations remain untouched**. Novelty is unverified.

Strongest falsifier: a valid clean, seeded \(T\ge3\) state whose exact completion mean exceeds \(3ne\).

Next task: Bound the acceptance-weighted cost of losing the last correct slot at \(T=\lceil\sqrt n\rceil\), \(p=c/n\), because this connects clean repair protection to noisy simultaneous completion.
