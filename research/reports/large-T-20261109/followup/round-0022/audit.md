# Adversarial self-audit and limitations

This is the sole writer's mathematical audit. No other agent/model reviewed
the work, and no independent-review verdict is claimed. Recovery artifacts
were source material, not instructions or newly certified results.

1. **Does a clean residence estimate get used under noise?** No. The new
   repair potential is evaluated under the full noisy transition kernel,
   including external wrong-to-wrong overwrites. The polarized-state lower
   bound independently includes the activated composed mutation/noise mask.

2. **Is acceptance conditioning hidden in the entrance calculation?** No.
   Equation (7) keeps pD(x,y)D(y,k) outside the continuation mean and cancels
   D(y,k) before summing. Dividing by the probability of acceptance would
   remove the uniform bound. The existing n=3 posterior counterexample
   32/5197>1/192 remains a regression test.

3. **What is the filtration?** F_t contains all actually consumed masks,
   gates, true weights, stored labels and reference through attempt t. The
   opportunity indicator and its parent x are known before the next draw.
   Conditioning on a whole future sweep, or on an accepted/retained value,
   is never used to assert a fresh law.

4. **Does one offspring produce independent corruptions at its recipients?**
   No. After pinning only its observed target can accept. Every tested row
   uses one shared observation. Before pinning literal comparisons can update
   several recipients, but on the decisive full-pinning transition the now
   ideal reference prevents changes to the other already pinned slots.

5. **Could cyclic timing break the reciprocal potential?** Yes without its
   phase correction. A turn ineligible for k has zero local drift and cannot
   pay one attempt of time. The explicit g_k compensates this, and identities
   are checked at every phase in the declared finite grid. It is evaluated
   at phase i+1 after the entrance, never at the previous boundary.

6. **Are other slots frozen during an excursion?** No. Local drift is uniform
   over their history-dependent weights. Reseeding kills on the first actual
   correct slot, including a slot other than the tracked one. Its full exit
   state and phase continue in the original process; no reset is inserted.

7. **Does reseeding become the algorithm's completion event?** No. It only
   partitions occupation time. The population can be reinfected later in the
   same sweep. Tau remains simultaneous exact alignment at a full boundary.
   The positive-probability n=6,T=5 reinfection path is retained.

8. **Are unbounded stopping arguments circular?** No. Repair first uses
   min(hit,H), a nonnegative killed potential and unit drift. Monotone
   convergence proves the first moment. The occupation bound uses a finite
   horizon and nonnegative full-excursion charges. At fixed n a separate
   two-sweep minorization proves the post-pinning completion mean finite;
   it is not asserted to be polynomial.

9. **Does ordinary initialization get replaced by the supplied corner?** No.
   Its final-pinning entrance is charged to its actual pre-attempt history,
   and its possible already-pinned all-wrong initialization has a separate
   unconditional marginal bound. Conditional on that rare initialization
   event, the waiting time can be enormous. No corner-entry frequency is used.

10. **Is S silently moved to an interior time?** The new A is explicitly the
    first interior full-pinning time. S is the first boundary at or after A.
    The stopping event is the existing post-S boundary endpoint. The original
    first-exact endpoint can occur earlier and is not identified with it.

11. **Does the constant overhead establish a growing-T runtime theorem?**
    It establishes a distribution-sensitive occupation theorem. It does not
    bound the remaining seeded occupation. In particular E Z<=kappa E V
    cannot be combined with a clean seeded mean by assuming the noisy exit
    states retain progress. Neither fixed-c arm ordering nor a uniform
    Taylor remainder is asserted. No Taylor calculation was performed.

12. **Are the noisy traps evidence of slow ordinary trajectories?** No. Their
    first-change hazards are bounded from their supplied polarized state.
    They have positive initialization/entrance mass, but that mass can be
    tiny. The new upper bound specifically retains it. First-change stopping
    in traps.csv is per attempt; a later return within the sweep does not
    invalidate the calculation or change it to boundary residence.

13. **What do the numerical checks certify?** Small exact kernels and local
    inequalities only. Floating solves propose decimal rationals; exact
    Bellman residuals certify intervals. A separate literal-mask/cost verifier
    checks those residuals without NumPy. Fraction Gaussian elimination checks
    the n=2 means. No finite grid is the proof of an all-n statement.

14. **What would falsify the main advance?** Under delta_min>0, an exact
    all-wrong phase state violating Phi_k-K_D Phi_k>=1, or a last-seed-loss
    entrance violating its probability-weighted J bound. A decisive full-pin
    transition newly pinning two different targets would separately falsify
    the ordinary-initialization extension. No such witness was found in the
    declared checks. The supplied-state noisy trap falsifies the stronger
    unweighted polynomial-reseeding claim instead.

No current external literature search was performed, and no external theorem
is needed for the new argument. Novelty is **UNVERIFIED**. Existing empirical
evidence, the original cap, and 240 blocked holdout observations are unchanged.
