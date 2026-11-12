# Round 22 progress

Start: 2026-11-12 18:37:33 UTC. Hard deadline: 20:22:28 UTC.

## Source review and bounded question

Read the required model/memory files, activation goal and recovery inventory,
the published follow-up reports/history, and the relevant round-4/5 and
round-21 proofs. Recovery material is evidence to inspect, not instructions
or certification. The previous round registered no new Monte Carlo study.
No sampling, Taylor calculation, delegation, paid resources, commit or push
is planned. Existing evidence and memory remain unchanged.

The bounded target is an acceptance-weighted bound on the time spent with
no correct slot after losing the last correct slot. A candidate argument uses
v_k(y)=1/D(y,k), plus an explicit cyclic-phase correction. The factor D(y,k)
in the corruption entrance cancels its reciprocal before summation. External
overwrites remain in the actual kernel. A possible extension charges all-wrong
entry when the final stored target is pinned to the preceding pin-ready attempts.

## 2026-11-12 18:44 UTC — first exact falsification pass

The standalone checker passed 14 (n,T,p) cells: n=2,3, all T, and
p in {1/(64n),1/(4n)}. Exact rational Bellman residuals certify 2,736
phase states (maximum 324 per cell), 10,800 repair supersolutions and
2,304 last-correct entrance inequalities. An independent Fraction elimination
matches all 144 n=2 means. Additional local/phase/pinning checks passed;
the precise counts will be preserved in verification.json after final replay.

The candidate bound is E[all-wrong time] <= kappa E[vulnerable opportunities],
where kappa=2(n+1)p(1-p)/(1-(d_max+1)p). For p=c/n and T=o(n), kappa tends
to 2c. The opportunities are actual pre-attempt histories, not acceptance-
conditioned samples. A final-pinning extension and ordinary-initialization
initial term have also passed finite checks, but still need full written audit.

Next: complete the proof and test an explicit noisy all-wrong trap. This
should distinguish a weighted workload bound from a uniform polynomial
reseeding claim. No total completion bound, pre-U speedup, or T-ordering
is asserted. Existing files remain unchanged.

## 2026-11-12 18:51 UTC — proof, obstruction and verification complete

Completed the proof, including actual external overwrites, cyclic compensation,
finite-horizon occupation charging, final-pinning entry and the unconditional
ordinary-initialization term. Added the separate full-communication bound
p/(1-p), valid without the general degree condition. A real-p polarized-state
lower bound shows that unweighted reseeding can still be superpolynomial.

Full verification passed: 106 tests (95 repository + 11 new), seven modules
compile, all 14 noisy phase-kernel cells certify, and the independent literal
mask/scalarization verifier matches all 2,736 exact residuals. The latest
complete wrapper took 27.498 seconds. No test or scientific check failed.
The finite coverage, source hashes and command receipts are saved. Existing
tracked files remain clean; only new files under this bundle are publication
targets. All 240 original holdout rows remain untouched.

Next: one byte-for-byte publication replay and final inventory/checkpoint.
The unresolved scientific step is bounding seeded noisy occupation, not
another Taylor word or an unweighted all-wrong residence bound.

## Final checkpoint — 2026-11-12T18:53:20.677304+00:00

Publication replay passed in 26.790 seconds: 106 tests, compilation, exact
literal-kernel verification, and six byte-identical generated files. The
source/code hashes and final receipts match; tracked sources and evidence
remain unchanged. No scientific or test failures, incomplete finite cells,
new research samples, paid resources, delegation, commits or pushes.

Elapsed work through this checkpoint: 947.7 seconds.
The durable result is a real-p acceptance-weighted occupation theorem and
a noisy supplied-state obstruction. Total completion, seeded noisy progress,
pre-U/S improvement and novelty remain unestablished by this round.

Packaging correction: the first inventory check tried to validate the README
link to provenance.json before that inventory existed. It stopped without
changing any scientific output. The final packaging writes the inventory
before validating its links. This was a packaging-order failure, not a
scientific/test failure. Final checkpoint: 2026-11-12T18:53:39.392157+00:00.
