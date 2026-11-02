# A separate noiseless frontier-scheduling baseline

This variant is included to test evaluation-efficient scheduling, not to change the definition of the main cyclic experiment. It uses one-bit mutation, p=0, fixed ideal reference, radius r>=1, and a **single evaluated initial solution** copied into all slots. It has no claimed novelty priority.

Let that initial solution have weight W=w. Slot w is already optimal. Keep the contiguous interval [L,R] of certified solved indices, initially [w,w]. At each evaluation choose one unfinished boundary (uniformly if both are unfinished), mutate that boundary's incumbent, and perform the same scalar-cost neighborhood replacement. A downward mutation from L extends the interval to L-1; an upward mutation from R extends it to R+1. A boundary already at 0 or n is not selected again.

## Exact conditional expected number of evaluations

At p=0, a solved slot cannot lose its optimum. Since r>=1, each successful boundary mutation reaches the adjacent target slot and solves it. One-bit mutation cannot skip a target index.

When the left boundary is s>0, a left-directed extension succeeds with probability s/n per evaluation **assigned to that boundary**. It requires expected n/s assigned evaluations. Summing over s=w,w-1,...,1 gives n H_w. The right side similarly requires n H_(n-w). Every evaluation after initialization belongs to exactly one unfinished boundary, so the expected total is exactly

`E[evaluations | W=w] = 1 + n H_w + n H_(n-w)`, with `H_0=0`.

The initial 1 is one evaluation of the shared initial solution. There is no extra factor two from choosing between boundaries: the proof sums their assigned evaluation counts, not elapsed iterations separately. Independent fresh mutation draws yield the geometric waiting-time expectations. The code tests the formula against every small-state Bellman equation as well as checking exact assignment in completed runs.

For uniform initialization, W is Bin(n,1/2). The formula is O(n log n) uniformly in w and at least n H_n for every w (H_w+H_(n-w)>=H_n), so its unconditional order is Theta(n log n). This is a theorem for this particular variant, not a universal optimality or novelty claim.

## Evaluation cost is not total computation

Copying/storing n+1 incumbents and comparing against neighborhoods has a cost not counted in objective evaluations. The count-space simulator does not store n-bit genomes explicitly. A literal implementation may incur additional memory and copying costs. This is why the report retains scalar-comparison counts and does not assert wall-clock optimality.

## Why the noisy extension is not implemented

At positive prior noise, observing the stored target does not certify the true target. Freezing a slot or advancing a “certified” interval on that evidence can be incorrect. The baseline rejects p>0 rather than silently treating noisy fitness as ground truth. A noisy scheduler requires a separately specified repair/exploration mechanism and its own analysis.
