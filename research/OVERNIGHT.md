# Bounded overnight Codex runbook

## Recommended first five-hour goal

The canonical, paste-ready prompt is in `research/FIVE_HOUR_GOAL.txt`. The local
launch procedure is in `research/START_LOCAL.md`. Its core objective is:

```text
/goal Follow the full five-hour contract in research/FIVE_HOUR_GOAL.txt. Determine
whether same-Hamming-weight offspring or archive-versus-alignment stopping best
explains the finite-size radius behavior. Run the exact-versus-lazy one-bit and
archive-versus-alignment 2x2 comparison with one sole-writing builder and two
independent read-only reviewers. Do not work on noise or claim asymptotics.
```

## Operating loop

1. Read the durable project files and relevant source/PDF sections.
2. Restate one falsifiable subclaim and its acceptance test.
3. Ask an evaluator to identify hidden conditioning, dependence, or stopping-time assumptions.
4. Implement the smallest mechanical check or experiment that can refute the subclaim.
5. If it survives, attempt the proof; if it fails, preserve the counterexample.
6. Have the evaluator review the result without editing it.
7. Update the claim ledger and status.
8. Continue only if the evidence points to a distinct next step within scope.

## Hard stop conditions

- The explicit time/token budget is reached.
- Three materially different approaches fail without producing new information.
- Progress requires an undefined algorithm convention or a human research choice.
- Tests or manifests cannot be made reproducible.
- Paid compute, credentials, external communication, or destructive actions would be required without authorization.

## Morning acceptance criteria

- Every changed claim has a status label.
- Every experiment is reproducible from a recorded command and seed.
- Failed attempts and counterexamples are retained.
- The current checkout passes the test suite.
- The report separates what was proved, checked, observed, and merely suggested.

## Later overnight goals

After canonical-model reconciliation, use separate goals for any warranted post-burn-in replacement for contradicted C5, C6/C7 (noisy drift and simultaneous coverage), and any genuinely distinct noiseless theorem that remains. Do not combine literature review, proof repair, large parameter sweeps, and paper rewriting into one unbounded goal.
