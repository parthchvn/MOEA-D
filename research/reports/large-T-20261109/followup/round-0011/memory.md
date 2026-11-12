# Round 11 durable research checkpoint

**C31, candidate proof, mechanically checked:** a real-p Schur complement
eliminates the complete double-error block of a closed T=2 pair while
retaining polynomial acceptance-weighted time and exit rewards. If
R_D=(I-P_DD)^(-1), S denotes single-error states, A the aligned state, and
0<=p<1/6, then P_SD R_D 1<=4p/(1-6p) and
P_AD R_D 1<=2p^2/(1-6p). Exit mass is at most 2p from S and p^2 from A.
The exact trace kernel is stochastic and must retain its time reward.
Every single-error pair state has mean boundary alignment time at most
3n(1+4p/(1-6p))/(1-p)^2 sweeps.

The proof uses a phase-dependent clean exit potential bounded by 2/r(z)
after an accepted overwrite z, where r(z)=D(z,a)+D(z,a+1). The observation
acceptance factor cancels this inverse weight. Both attempts and midpoint
repair/reinfection are retained. No noisy persistence or acceptance-conditioned
noise law is assumed.

For a closed pair, the same bounds extend to its exact block elimination
inside the full pinned population: the eliminated resolvent retains the
other coordinates' evolution as a sum of P_DD^j tensor P_rest^j. This gives
no polynomial bound on the remaining global inverse. At odd n all T=2 pairs
are closed. At even n the orphan feeds the last pair, which is excluded.
No T=3 transfer is made.

**C32, contradicted strengthening, candidate all-n counterexample proof:**
uniform polynomial bounds for all acceptance-weighted iterated residence
resolvents fail. For the last pair at odd n, S0=(0,n),
E1=P_SD'(0), and R_D0=(I-P_DD(0))^(-1),
(E1 R_D0^2 1)(S0)>=n^(n-4)/32. At n=33 an explicit positive path contributes
at least 1.0465002071e43 to this iterated resolvent, while its first-residence
contribution is only 0.0001713501. This does not bound a signed Taylor
coefficient or refute the desired full-process remainder.

**Mechanically checked:** exact literal kernels and phase inequalities,
2,776 boundary drift inequalities, 808 boundary entry inequalities,
nine Schur/direct rational solves, and four direct full-population tensor
rows. All counts and exact fractions are in [verification.json](verification.json),
[schur.csv](schur.csv), [moments.csv](moments.csv) and
[checks.json](checks.json). General arguments await independent audit.

**Inherited evidence preserved:** the earlier empirical ratios, original
preregistration, one capped main trial, 240 missing blocked holdout trials,
and inconclusive original two-stage decision are unchanged. Full round-10
reproduction recursively validates earlier registrations, receipts and seed
separation; no repair was needed. The chronology limit concerning unavailable
private trial logs remains. No new scientific experiment or seeds were used.

**Still unresolved here:** uniform full-population third-and-higher-order
control on p=o(log(n)/n^4), synchronization under reinfection, the even-n
orphan coupling, and overlapping T=3 neighborhoods. A first-moment Schur
bound does not by itself supply a Taylor remainder. The previous full-process
noise window is unchanged. No current literature search or novelty claim
is made offline.
