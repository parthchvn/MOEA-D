**Proved locally:** donor 1 spends little expected time at an incorrect weight. **Candidate proof:** the supplied noisy corner has \(\Theta_{c,T}(n^2)\) expected simultaneous-alignment attempts for every fixed \(c>0,T\ge2\), versus \(\Theta_c(n^3)\) at \(T=1\). The full argument awaits independent review. See [proof](proof.md).

With \(a=p/(1-2p)\), \(d_1=|\{i:1\in B_T(i)\}|\), and boundary stopping time \(\sigma\),

\[
E B_1(\sigma)\le d_1aE\sigma,\qquad
E[O_1(\sigma)/(n+1)]\le d_1(a+p)E\sigma.
\]

Here \(B_1\) counts incorrect own turns; \(O_1\) counts incorrect states before all attempts. Starting donor 1 correct, an \(O(n)\)-sweep interval therefore contains only \(O_{c,T}(1)\) expected incorrect sweep-equivalents.

**Analytic illustration, not measurement:** at \(n=512,T=3,p=1/32768\), the endpoint boundary-repair bound is **1,390.571 sweeps**. Before that event, donor 1 has at most **0.127319 expected incorrect own turns**, or **0.254629 incorrect sweep-equivalents**. [Analytic bounds](bounds.csv) include the proposed simultaneous bound.

The candidate extension represents corruption by independent families of repair particles and derives a renewal bound for their joint extinction. It explicitly accommodates the published reinfection path. Assumptions are pinned ideal labels, the supplied single-corner state, cyclic own-parent standard-bit mutation, activated bitwise noise, and filled-cardinality neighborhoods.

**Remaining proof obligations:** independently validate the tagged coupling with within-sweep births, the generation-work estimate, family independence and renewal, and restart at endpoint repair. A wrong incumbent without a matching particle, an injection-bound violation, or an exact expectation exceeding the stated finite bound would falsify the relevant argument. Ordinary initialization, growing \(T\), and new tail bounds remain outside its scope. The cited revised \(T=3\) appendix was unavailable locally and was not assumed.

**Published measurements reverified; no new sampling:**

| Comparison | Observations per arm | Restricted-mean ratio and nominal 95% interval |
|---|---:|---:|
| Original \(n=256\), \(T=1/T=16\) | 24 | 2.327639 [2.050148, 2.674642] |
| Separate \(n=512\), \(T=1/T=23\) | 32 | 2.339095 [2.085387, 2.596468] |

These arms have no censoring. Distributions and phase denominators are retained in the [checkpoint guide](README.md). The original campaign’s **240 blocked holdout rows remain missing**, and its two-stage decision remains inconclusive. Its preregistration and evidence are unchanged.

**Checks passed:** 95 repository tests, 15 new proof tests, 16 prior-audit tests, and compilation. Exact checks cover 202 local kernels, 263,169 one-step tagged couplings, and 24 renewal examples. Four new outputs and six prior audit outputs reproduce byte for byte. No dependency repair was needed. [Verification and accounting](checks.json).

Morning report: cumulative progress now joins the audited empirical evidence to an explicit donor-occupation bound and a complete candidate corner proof. Curated outputs are under `deliverables/`; STATUS and CLAIMS were updated. Elapsed time was approximately **16 minutes 49 seconds**, using one CPU. No paid resources, network access, new scientific trajectories, commit, or push.

Next task: Independently audit the tagged error-family coupling, generation-work bound, and empty-state renewal argument, because these new steps now carry the proposed fixed-T noisy corner theorem.
