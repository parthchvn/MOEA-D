# Round 10 durable research checkpoint

**C29, candidate proof:** for the pinned supplied-corner T=2 process, put
H=(I-Q_0)^(-1)Q_1. At an accessible odd-n state with adjacent slots n-1,n
both of true weight zero and every other slot correct,
|H_EE|>=g_n>=2^n/(8n^2)-5-3n. No strictly positive diagonal state weighting
can lower the induced infinity norm below this diagonal. The positive
corner-row majorant from |H| diverges at p=n^(-4) eventually, including after
discarding orders zero through two. R_0|Q_1| also fails. This retains exact
acceptance probabilities and permits clean cancellations before absolute
values. The no-go result is restricted to these norm/majorant strategies;
the actual Taylor radius and real-positive-p remainder are not determined.
An independent audit of the all-n application is still required.

**C30, proved restricted extension of the audited orphan identity:** if only
accepted recipient n is noisy at even n,T=2, the corner's independent
geometric(q) clock discounts the orphan resolvent. Its remainder after order
two is <=128p^3/q^4<=10368p^3n^4 for 0<=p<=q/4. This is negligible relative
to p n log n on the requested scale. It does not bound mixed sequences or
adjacent corrupted pairs in the full process.

**Mechanically checked:** exact full/local pair rows and clean resolvent
diagonals, six positive accessibility entries, even-n orphan rows, 127 exact
closed-form inequalities, and ten exact discounted orphan remainder values.
Ten first/second orphan coefficients match round 9. See
[verification.json](verification.json), [dependency.json](dependency.json)
and [checks.json](checks.json) for counts and accounting.

**Inherited claims remain:** A_n=-(n/2)log n+O(n) and |B_n|<=1536n^5 have
the prior audits. The full third-and-higher remainder on
p=o(log(n)/n^4) is unresolved in this checkout. The conservative earlier
full-process sign window is unchanged. No fixed-c ordering or ordinary
initialization theorem is added.

**Dependencies and experiment integrity:** round 9 and its recursive earlier
evidence reproduce. No missing plan/receipt obligation needed repair. Both
published empirical comparisons are unchanged. The original preregistration,
cap, 240 missing blocked holdout trials and inconclusive two-stage decision
remain intact. Zero new trajectories/seeds, no network, cost, commit or push.
The existing published chronology limitation is retained.

**Next bounded proof question:** eliminate the T=2 double-error pair block
using a real-p Schur complement, retaining its accepted entrance/exit masses,
and test whether this controls the mixed remainder. The exact holding
denominator remains >=(1-p)^2 q_E while the absolute Taylor majorant diverges,
which makes resummation a concrete next step. This is a candidate route, not
an established bound or a preregistered sampling experiment.
