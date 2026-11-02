# A separate noiseless frontier-scheduling baseline

This variant tests evaluation-efficient scheduling without changing the main cyclic experiment. It uses one-bit mutation, p=0, a fixed ideal reference, radius r>=1, and a **single evaluated initial solution** copied into all slots. It has no claimed novelty priority.

Let the initial solution have weight W=w. Slot w is optimal. Keep the actual contiguous interval [L,R] of solved indices, initially [w,w]. Choose one unfinished boundary uniformly when both are unfinished, mutate its incumbent, and perform the usual neighborhood replacement. After replacement update **both** interval boundaries if their adjacent slots have become optimal. A solved slot cannot lose its optimum. One-bit mutation cannot skip a target index, and r>=1 delivers any extension to the adjacent target.

**The singleton matters:** initially L=R, so both scheduler labels refer to the same parent. An upward mutation expands the right side even when the scheduler nominally chose the left side. The implementation tracks the actual solved interval instead of ignoring this opposite-side extension.

## Exact conditional expectation

Let H_0=0 and H_k=sum(1/s, s=1,...,k). For a non-singleton interval L<R, the expected number of additional evaluations is

`V(L,R) = n (H_L + H_(n-R))`.

Indeed, a trial assigned to the left boundary at s>0 extends it with probability s/n. The expected number of assigned trials until that extension is n/s. Summing across the left levels gives n H_L; the right side contributes n H_(n-R). Failed inward mutations remain within the already solved interval when L<R. Every trial is assigned to one unfinished boundary, so summing assigned trials introduces no factor two. All states have a positive progress probability, and only finitely many extensions are needed, so the expectations are finite.

For the interior singleton L=R=w with 0<w<n, the first mutation always extends one side. Conditioning on its direction gives

`V(w,w) = 1 + (w/n) V(w-1,w) + ((n-w)/n) V(w,w+1)`

`         = n (H_w + H_(n-w)) - 1`.

At a singleton endpoint, w=0 or w=n, there is just one unfinished direction and V(w,w)=n H_n. Including the shared initial evaluation, the exact formula is therefore

`E[evaluations | W=w] = 1 + n H_w + n H_(n-w) - 1{0<w<n}`.

For example, n=2 and w=1 give 4 evaluations in expectation, not 5: one initial evaluation, one mutation that necessarily expands the singleton, and a mean of two further mutations to find the other endpoint.

The earlier independent-boundary formula without the indicator was an upper bound but not the exact mean for this broadcast algorithm. The singleton correction and the implementation fix are covered by exact-rational Bellman equations for every interval for n=1,...,12, plus a separate literal-bitstring oracle that recomputes the entire solved set after each mutation. This is not just a test that repeats the formula in production code.

Since H_w+H_(n-w)>=H_n, the conditional expectation is at least n H_n and at most 1+2n H_n. Consequently its order is Theta(n log n), also under uniform initialization W~Bin(n,1/2). This theorem is for the specified variant, not a universal optimality, novelty, or noisy-runtime claim.

## Evaluation cost is not total computation

Copying/storing n+1 incumbents and comparing against neighborhoods has a cost not counted in objective evaluations. The count-space simulator does not store n-bit genomes explicitly. A literal implementation may incur additional memory and copying costs. The report retains scalar-comparison counts and makes no wall-clock optimality claim.

## Why the noisy extension is not implemented

At positive prior noise, observing the stored target does not certify the true target. Freezing a slot or advancing a certified interval on that evidence can be incorrect. The baseline rejects p>0 rather than silently treating noisy fitness as ground truth. A noisy scheduler requires a separately specified repair/exploration mechanism and its own analysis.
