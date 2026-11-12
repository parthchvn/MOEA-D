# Acceptance weighting, absolute resolvents, and adjacent errors

**Candidate proof; not independently audited.** Acceptance probabilities do
not suffice to make a state-weighted, absolute Neumann majorant polynomial.
The obstruction persists if clean excursions are summed with their signs
before taking absolute values. For the actual T=2 process, let

\[
Q(p)=Q_0+pQ_1+p^2Q_2+\cdots,\quad
R_0=(I-Q_0)^{-1},\quad H=R_0Q_1.
\]

There are accessible adjacent-error states E, for odd n, such that

\[
 |H_{EE}|\ge g_n\ge {2^n\over8n^2}-5-3n.                 \tag{1}
\]

Consequently every finite, strictly positive diagonal state weighting has
induced infinity norm at least g_n. The positive scalar majorant built from
|H|, starting at the supplied corner, diverges at p=n^(-4) for all sufficiently
large odd n. This sequence belongs to p=o(log(n)/n^4). The coarser majorant
R_0|Q_1| fails as well. Exact acceptance probabilities are retained throughout;
the obstruction is not obtained by replacing accepted mass by gate mass p.

**Scope of this negative result.** It rules out these absolute insertion
majorants and their positive diagonal reweightings. It does not rule out a
signed block elimination, a real-positive-p comparison, or a remainder bound
that sums cancellations before taking absolute values. It does not prove that
the actual Taylor series diverges at this p, that its cubic coefficient is
exponential, or that the desired real-p remainder estimate is false.

**Proved restricted positive result, conditional on the audited orphan
identity.** For the orphan-only noisy process defined below, the remainder
after its quadratic expansion satisfies

\[
 |m_O(p)-m_O(0)-p m'_O(0)-p^2 b_O|
 \le {128p^3\over q^4}\le10368p^3n^4,
 \qquad 0\le p\le q/4.                                  \tag{2}
\]

This controls all third-and-higher terms of that restricted response on the
requested window. Mixed insertions and the full adjacent-error response
remain unresolved in this checkout. The full gap's noise window is unchanged.

**Process and information.** Take n>=3 and T=2 or 3. Supply ideal extrema
(0,n), stored labels b_k=k, and true weights C=(2,1,2,...,n), with zero
initialization cost. Breeders 0,...,n mutate their own incumbents in ascending
order, independently flipping each bit with probability 1/n. An independent
Bernoulli(p) gate activates another independent rate-1/n mask for observation.
The recipient list starts at the breeder and alternates sides, right first for
even breeders and left first for odd breeders, skipping invalid indices and
stopping at T. This is filled cardinality, not clipped radius.

The pinned scalarization max{k(n-z),(n-k)z} accepts only observation z=k at
recipient k. Thus an accepted child of true weight y changes at most slot k,
with probability D(w_i,y)D(y,k) conditional on activation and the pre-attempt
history. F_t reveals only the supplied state and randomness consumed through
attempt t; G_s=F_((n+1)s). The stopping time is the first G_s boundary with all
true weights correct. Aligned intermediate states are retained. All time
quantities here are sweeps; attempts multiply by n+1. No drift theorem, noisy
persistence assumption, or probability conditioned on acceptance is used.

Q(p) is the sweep matrix restricted to nonaligned boundary states. Clean
updates only delete errors. Each wrong coordinate has a positive own repair
probability, so R_0 exists at every finite n. Q_1 sums one active-minus-clean
insertion at each possible breeder position, including clean prefixes and
suffixes. In particular Q_1 is signed and includes negative diagonal terms.

**Dependencies and evidence.** The complete round-9 replay reproduces its five
outputs and recursively validates round 8 and earlier registrations, receipts,
seed separation, exact coefficients and audits. No dependency repair was
needed. The relevant inherited statements are A_n=-(n/2)log n+O(n),
|B_n|<=1536n^5, and the discounted orphan identity. Neither the older tagged
forest theorem nor an unavailable manuscript appendix is a premise here.
[dependency.json](dependency.json) records the replay. No new scientific
trajectory, seed, empirical fit or uncertainty interval was generated.

The offline source comparison with Benjamin Doerr, Moaad Elmoutassim, Martin
S. Krejca and Guy Mushiata Kibulu, *Understanding the Co-evolutionary Solution
Exchange of the MOEA/D: Already the Smallest Communication Radius Gives the
Best-Possible Speed-Up* (2026), arXiv:2610.35373,
DOI:10.48550/arXiv.2610.35373, remains a model boundary. Its noiseless
radius/archive result is not transferred. No current literature search or
global novelty/open-problem claim is made in this offline turn.

**Elementary matrix fact, proved.** For any matrix H and positive diagonal
W=diag(w), (W^(-1)HW)_{xx}=H_{xx}. Hence
||W^(-1)HW||_infinity>=|H_{xx}|. For a nonnegative matrix M,
(M^j)_{xx}>=(M_{xx})^j. If (M^l)_{Cx}>0 and h_0(x)>0, then
sum_{k>=l}p^k(M^k h_0)(C) diverges whenever pM_{xx}>=1. A very small but
positive entrance mass does not rescue this infinite positive series.
This is a norm/majorant statement, not a spectral-radius statement for signed H.

**Adjacent corrupted donors: exact local calculation.** For odd n, T=2
decomposes into pairs {0,1},{2,3},...,{n-1,n}. Each pair's sweep kernel is
autonomous. Let a=n-1, b=n, and E have both pair weights zero and every other
slot correct. Set

\[
 v=n^{-n}=D(0,b),\quad u=n(n-1)v=D(0,a),\quad r=u+v,
 \quad s=1-r,\quad c=(1-1/n)^n,
\]
\[
 \theta={2(n-1)\over n^2},\quad
 r_2=n\theta^{n-1}(1-\theta)+\theta^n,
 \quad q_E=1-s^2.                                      \tag{3}
\]

Two independent masks compose to a per-bit flip rate theta, so r_2 is the
activated probability of observing either pair target from true parent zero.
During one attempt at E, the clean holding probability is s. Active proposals
leave E with probability r_2-c r: true child zero does not change either
slot, regardless of which target is observed. Thus the one-attempt signed
holding coefficient is r(1+c)-r_2.

For the ordered two-attempt pair sweep, the exact signed diagonal is

\[
 \ell_n=2s\{r(1+c)-r_2\}+c u^2+v^3.                   \tag{4}
\]

The first term places the insertion at either attempt. The c u^2 term is a
clean repair of a on the first turn followed by true child zero observed as
a on the second. The v^3 term is a clean repair of b on the first turn, then
mutation b->0 and observation 0->b on the second. These are the only ways to
return to E after a clean first-turn repair. Omitting them would be incorrect.
The clean pair holding probability is s^2, so its clean residence at E is
1/q_E. Define lambda_n=-ell_n/q_E.

Other initially correct pairs contribute nonpositive terms to the full
Q_1(E,E): their probability of ending correct is one at p=0 and at most one
for real p>=0. Therefore Q_1(E,E)<=ell_n. This yields the R_0|Q_1| diagonal
lower bound lambda_n, without making noisy coordinates independent globally.
Here independence of the closed T=2 pairs is justified by disjoint breeder
randomness and recipient sets.

**Clean cancellations before absolute values.** The only clean transient
descendants of E are E, F=(a,0), and G=(0,b) in this pair, with all other
slots correct. Once either member is correct, it supplies its partner with
repair probability at least 1/(3n) per sweep. Thus
R_0(E,F), R_0(E,G)<=3n. A one-insertion transition from F back to E must
overwrite a with true zero observed as a. Each of the two breeders contributes
at most D(0,a)=u. Likewise Q_1(G,E)<=2v. These entries are nonnegative:
clean transitions cannot recreate an error. Consequently

\[
 (R_0Q_1)_{EE}
 ={Q_1(E,E)\over q_E}
   +R_0(E,F)Q_1(F,E)+R_0(E,G)Q_1(G,E)
 \le-\lambda_n+6nr.                                    \tag{5}
\]

Put g_n=lambda_n-6nr. This proves |H_{EE}|>=g_n whenever g_n is positive
(and is a vacuous lower bound otherwise). Thus even taking absolute values
only after summing a complete clean excursion does not solve the problem.

For completeness, r<=n^(2-n)<=1/2, s>=1/2, r<=q_E<=2r and c>=1/4 for n>=3.
The last bound follows from monotonicity of (1-1/n)^n for n>=2.
Also c u^2+v^3<=r^2. Splitting the positive and negative terms in -ell_n/q_E
before using the two denominator bounds gives

\[
 \lambda_n\ge {r_2\over2r}-5
 \ge {2^n\over8n^2}-5,
 \qquad g_n\ge {2^n\over8n^2}-5-3n.                    \tag{6}
\]

For the second inequality use r_2>=theta^n=2^n c n^(-n) and
r<=n^2 n^(-n). The bounds are deliberately loose. No finite-grid
extrapolation is used to establish exponential growth.

**Accessibility and the actual corner row.** These states are not excluded
rare states. Start at C and, during one sweep, keep the corner wrong and
corrupt a to zero using true child zero observed as a. Keep b correct.
Let S be that boundary state. In the next sweep repair the corner, retain
the zero at a, and corrupt b to zero using true child zero observed as b.
This ends at E. Each specified mutation and observation has positive mass.
One activation is used per sweep, and an error is present at every boundary.
Therefore Q_1(C,S)>0 and Q_1(S,E)>0. All relevant clean ancestors of S give
nonnegative entries into E because a new error at b is required. Hence
(|H|^2)_{CE}>0. Combining this with (5) proves that

\[
 \sum_{k\ge3} p^k (|H|^k h_0)(C)=+\infty
 \quad\hbox{if }p g_n\ge1.                              \tag{7}
\]

At p=n^(-4), this condition holds eventually. Exact examples are n=33,
g_n/n^4=1314.3988127..., and n=65, g_n/n^4=3.7740421673...*10^11.
This subseries uses only Q_1; adding nonnegative bounds for Q_2,Q_3,... cannot
fix it. Cancellation between signed terms might, so (7) is not a statement
about the original Taylor series or actual expectation.

**Orphan check: an earlier obstruction with a known cure.** At even n,T=2,
slot n has no external incoming donor. In state E_O with only w_n=0 wrong,
its own clean repair probability is d=n^(-n). Suppress other recipient
perturbations temporarily. The exact signed holding coefficient divided by d
is

\[
 1-(2^n-1)c.
\]

To see this, the activated probability of reaching observation n is
(2(1-1/n)/n)^n; subtract the unchanged true-zero mass c d and compare with
the clean departure d. Other noisy recipients can only reduce the full
probability of ending at E_O, so
|H_{E_O E_O}|>=(2^n-1)c-1. Here R_0 has only its diagonal in row E_O.
This is also exponential. It does not invalidate the previously audited
orphan cancellation or imply a large orphan-only scalar remainder.

**All-order orphan remainder, proved from the audited identity.** Restrict
noise to accepted recipient n; all other recipients evolve cleanly. The
corner has its independent geometric(q) repair clock,
q=1-(1-D(2,0))(1-D(1,0))>=1/(3n). Write L(p)=L_0+p L_1 for the orphan's
local stochastic kernel, s_0=1-q, b_0=1-D(n,n), and
G_0=(I-s_0 L_0)^(-1). The audited identity is

\[
 m_O(p)={[(I-s_0 L(p))^{-1}]_{nn}\over1-b_0p}.          \tag{8}
\]

The corner's independent completion discount is essential. It includes
reinfections before the corner repairs; it is not a maximum of noisy first
hitting times. Since L_0 is stochastic, ||G_0||_infinity=1/q, and since L_1
is the difference of two stochastic kernels, ||L_1||_infinity<=2. The kth
coefficient of the numerator in (8) is bounded by q^(-1)(2/q)^k.
Multiplying by sum (b_0p)^j, with b_0<=1<=2/q, bounds the kth coefficient
of m_O by (k+1)(2/q)^k/q. For z=2p/q<=1/2,

\[
 \sum_{k\ge3}(k+1)z^k
 ={z^3(4-3z)\over(1-z)^2}\le16z^3.
\]

This proves (2). On the requested scale its ratio to p n log n tends to
zero. It controls only insertions all restricted to the orphan. It does
not include orphan/nonorphan mixed sequences or adjacent pair clusters.

**A possible continuation, not a completed proof.** At real p in [0,1),
the exact pair holding denominator satisfies

\[
 1-P_{p,EE}\ge(1-p)^2 q_E>0.                            \tag{9}
\]

Both gates inactive and a clean escape is a sufficient event. Thus the large
negative diagonal insertion can be summed in its exact denominator without
an alternating-series convergence assumption. Equation (9) is only a
holding-state bound: transitions among other double-error states and mixed
insertions remain. A useful next step is a Schur complement over each T=2
double-error pair, retaining real-p denominators and entrance/exit acceptance
weights, with a corresponding treatment of the orphan mixed terms. Merely
replacing diagonal entries in the existing absolute series is not yet a
remainder proof.

**Checks and falsifiers.** [check.py](check.py) imports no prior solver. Exact
polynomial kernels are compared with literal masks; local two-attempt rows
are compared with (4); full-population rows and the signed clean resolvent
diagonal are computed separately at n=3,5,7. Six positive insertion entries
check accessibility. Even-n full rows are checked at n=4,6,8. Exact rational
orphan solves verify (2) at n=4,6,8,10,12 for p=n^(-4) and p=q/4, and reproduce
the published first and second orphan coefficients. [verification.json](verification.json)
and [obstruction.csv](obstruction.csv) retain the finite checks and exact
fractions; [orphan.csv](orphan.csv) retains the restricted remainders.

A different literal transition row, a missing return term in (4), failure of
the 3n clean descendant bound, a zero proposed accessibility entry, or an
orphan identity/tail violation would falsify the associated step. The general
no-go argument awaits independent audit. The remaining proof obligation is a
uniform bound on the full third-and-higher remainder, not another fit to the
already audited quadratic coefficient. No enlarged full-process sign window
is claimed.
