**Round 20 recovered and audited.** The baseline decomposition and both entrance factors justify
\[
|\mathrm{RORR}|\le1024(n+1)^3(20n)^4/q<4\cdot10^9n^8
\]
in sweep units. The [proof audit](audit.md) retains boundary compensation, negative branches and last-pair/orphan dependence.

Assumptions: even \(n\ge4\), filled \(T=2\), supplied corner \((2,1,2,\ldots,n)\), ideal reference, pinned labels, ascending own-parent standard-bit mutation, shared activated bitwise observation noise, and simultaneous alignment checked only at sweep boundaries. Each entrance factor cancels its corresponding inverse repair rate **before summation**.

This establishes one signed coefficient. The full fourth-order gap, uniform remainder, fixed-\(c\) ordering and ordinary-initialization transfer remain unresolved.

**Verification:** 112 tests and compilation passed. Fresh \(n=4\) calculations checked 460 identities and 1,738 inequalities; independent support checks covered 55,939 regular configurations. Published \(n=6\) results passed hash/schema verification. Its redundant fresh recomputation was interrupted and is explicitly recorded as unfinished.

The recovery copies matched their inventory, but nine advertised WIP outputs/receipts were missing; their completion claims were not accepted. The strongest shortcut falsifier remains concrete: deleting the baseline changes \(n=4\) RORR from **0.158278329276** to **−1.803253923193**.

Saved [HISTORY.md](HISTORY.md) indexing all 19 published rounds—including negative results—plus [proposed memory updates](memory.md), [checks](checks.json), reproduction code and exact outputs. All 512 protected files remain unchanged. Checkpoint saved after **10 minutes 33 seconds**, with no sampling, paid resources, commits or pushes.

Next task: What uniform bound does the donor/forest argument give when T grows like log n or √n, and which step causes its exponential synchronization factor?
