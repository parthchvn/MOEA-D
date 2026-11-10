# Round 13 durable memory supplement

**Mechanically checked:** the supplied-corner T=3 minus T=2 cubic coefficients
in sweeps are C_3=+0.7833960714258787, C_4=-1.5499770573154794,
C_5=-0.02383424101435469, C_6=-5.367760391772157. They were computed as
exact rationals; decimals are rounded. The full-state literal-mask oracle
matches 28 quantities at n=3,4; all 20 inherited lower-order quantities
match. Sixteen even-n recipient words sum to the complete T=2 coefficient.

**Candidate proof, not yet independently audited:** |C_n|<=10^10 n^7 for
all n>=3. The proof retains both acceptance factors for an arbitrary
double-error pair. At even n it splits insertions into nonorphan R and
orphan O, subtracts the autonomous orphan hitting function, and bounds
the remaining stopped-occupancy response before summing all eight words.
The separate occupancy recurrence verifies 996 identities on 332 states.
The n=32 cancellation witness subtracts quantities of magnitude 2.27e57
to leave 6.12e-44, in exact arithmetic.

**Contradicted strengthening retained:** the prior exponential higher-residence
moment witness still applies. The new candidate does not bound arbitrary
single-error rows or a full resolvent norm. **Unresolved:** independent
review of the new weighted-entry and phase-excess proof, the sharp cubic
order/sign, and a uniform fourth-and-higher remainder. No enlarged full
noise window, fixed-positive-c ordering, or ordinary-initialization theorem.

**Prior evidence preserved:** recursive round-11 replay verifies earlier
plans, receipts and seed separation. Four pertinent round-12 tables replay
exactly and all its published artifact hashes match. Its expensive full
positive-p Schur solve is not reused as a premise. No plan/receipt repair
was necessary. The original blocked holdout, capped trial and inconclusive
two-stage decision remain unchanged. No new trajectories or scientific seeds.

Next bounded obligation: independently audit the two-birth inequality's
use inside the actual clean occupation kernels, the phase extension of
the orphan excess identity, and all six mixed recipient words. These now
carry the proposed polynomial cubic bound.
