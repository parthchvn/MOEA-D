# Adversarial self-audit

This is the sole writer's explicit mathematical scope check, not an independent
reviewer verdict. No other agent or model was run. Recovery artifacts were
treated as source material, and earlier empirical results were neither sampled
nor newly certified.

1. **Does extra communication preserve correctness?** Only in the clean,
   pinned process. There an observation equals the true child weight, and only
   its unique target slot accepts. This establishes the invariant used in the
   proof. It does not hold for ordinary initialization with unpinned labels or
   activated observation noise. A noisy within-sweep reinfection witness is
   retained in the unit tests.
2. **Does the graph proof accidentally assume all odd-T edges are reciprocal?**
   No. Only the adjacent path must be bidirectional. Filled boundary intervals
   can produce nonreciprocal longer edges for odd T as well. Both constructions
   are checked at all n=2,...,64 and all T>=2.
3. **Does one seed imply a maximum-of-means bound?** No. The proof chooses one
   frontier target, bounds its conditional waiting time using fresh scheduled
   visits, then starts another stage. At most m_e stages occur. The interior
   phase allowance is explicit and stopping remains at a boundary.
4. **Does the trap formula confuse holding and completion?** No. It computes
   only the first clean state change. Clean correctness is persistent, so a
   repaired trajectory cannot return to the all-wrong state. Exact product
   survival and independent subset-sweep survival agree at the declared small
   instances. Completion can be later; the holding mean is only a lower bound.
5. **Are the slow states excluded by the actual noisy process?** No: the
   prescribed all-active self-overwrite sweep reaches them with the exact
   positive mask product shown in traps.csv. Slot zero remains wrong. But
   positivity says nothing about typical frequency, and a clean holding mean
   is not a noisy residence mean. The latter inference is explicitly excluded.
6. **Could the most central interval be missing because T is even?** Yes.
   The correction in a_star is necessary. At n=7,T=4, a=2 but a_star=3;
   starts 0,0,1,1,3,3,4,4 omit the centered start 2. The all-n proof and exact
   geometry checks use the corrected formula.
7. **Is the uniform seeding probability valid for an arbitrary parent, not
   merely the endpoint witness?** Yes. For a parent outside the central interval,
   the proof counts all subsets of favorable bits that hit the nearest endpoint
   of the interval. There are at least n/2 available choices per falling-factor
   term. For a parent already inside, no flip suffices. All parent weights are
   checked for every T>=3 at n=2,...,32 (11,408 exact inequalities).
8. **Does the factorial regime statement claim a typical-runtime threshold?**
   No. It brackets the supremum over all supplied pinned clean populations.
   Logarithmic and square-root T still admit the explicit pathological states.
   The corner is already seeded and belongs to the much faster class in (1).
9. **Do low-order coefficients reach the unseeded states anyway through
   negative branches or within-sweep reinfection?** A support transition of
   either signed branch can add at most one error. Starting with one, j<n
   leaves at most n errors. Negative branches are clean and do not add errors.
   Aligned intermediate states remain live in the phase solver, which checks
   every Bellman residual exactly. At order n the protection is no longer
   asserted. The bound is not a uniform remainder estimate.
10. **Has the old forest synchronization loss actually been removed?** No.
    Its artificial-family emptiness probability still leads to exp(cT).
    The new clean graph lemma explains a lost repair mechanism, but needs a
    noisy entrance/escape argument to replace that comparison. The displayed
    logarithmic/square-root/full-T bounds are algebraic consequences of the
    old result, with its finite sufficient conditions retained.
11. **Are large computations or incomplete runs hidden?** No. The clean solver
    enforces a 256-state subset cap, and the response solver a 1024 phase-state
    cap. One development run stopped on Python's integer string-conversion
    limit; a complete rerun passed after increasing that explicit limit. No
    assertion failure or partial grid was presented as a completed check.
12. **Is any independent review or novelty search implied?** No. The proof is
    the current writer's analytic result; exact checks are finite evidence.
    No new external literature search occurred. Novelty remains UNVERIFIED.

Remaining audit target for a future fresh context: verify the all-n central
interval/factorial upper-bound argument and the support restriction in the
uniform coefficient corollary. The strongest immediate falsifiers are a
clean seeded mean exceeding 3n m_e, a central-seed probability below (7), or
an activated pinned transition creating more than one new error.
