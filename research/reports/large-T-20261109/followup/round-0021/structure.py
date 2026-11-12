"""Deterministic exact graph/clean-kernel checks. No sampling or population matrix.

Run from this file's directory: python structure.py --out /tmp/round21-check
Only the standard library is used. Every clean closure is capped at 256 states.
"""
from __future__ import annotations

import argparse
import csv
from fractions import Fraction as F
from functools import lru_cache
import hashlib
import itertools
import json
import math
import sys
from pathlib import Path

CAP = 256
sys.set_int_max_str_digits(200000)


def neighbors(n, t, i):
    left = (t - 1) // 2 + int(t % 2 == 0 and i % 2 == 1)
    first = max(0, min(i - left, n + 1 - t))
    return tuple(range(first, first + t))


def literal_neighbors(n, t, i):
    out = [i]
    signs = (1, -1) if i % 2 == 0 else (-1, 1)
    for d in range(1, n + 1):
        for sign in signs:
            k = i + sign * d
            if 0 <= k <= n and len(out) < t:
                out.append(k)
    return tuple(sorted(out))


def candidates(n):
    raw = [('2', 2), ('3', 3), ('4', 4), ('5', 5), ('7', 7),
           ('ceil_ln_n', math.ceil(math.log(n))),
           ('ceil_sqrt_n', math.isqrt(n) + (math.isqrt(n)**2 < n)),
           ('n+1', n + 1)]
    # Natural logarithm; inadmissible fixed cardinalities are omitted, not clipped.
    out = {}
    for name, t in raw:
        if 2 <= t <= n + 1:
            out.setdefault(t, []).append(name)
    return out


def components(adj):
    """Iterative Kosaraju; graph adjacency only, never population matrices."""
    rev = [[] for _ in adj]
    for i, row in enumerate(adj):
        for k in row:
            rev[k].append(i)
    seen, order = set(), []
    for root in range(len(adj)):
        if root in seen:
            continue
        stack = [(root, False)]
        while stack:
            v, finish = stack.pop()
            if finish:
                order.append(v)
            elif v not in seen:
                seen.add(v)
                stack.append((v, True))
                stack.extend((w, False) for w in adj[v] if w not in seen)
    groups, ids = [], {}
    for root in reversed(order):
        if root in ids:
            continue
        group, stack = [], [root]
        ids[root] = len(groups)
        while stack:
            v = stack.pop()
            group.append(v)
            for w in rev[v]:
                if w not in ids:
                    ids[w] = len(groups)
                    stack.append(w)
        groups.append(tuple(sorted(group)))
    incoming = {ids[k] for i, row in enumerate(adj) for k in row if ids[i] != ids[k]}
    return groups, [g for a, g in enumerate(groups) if a not in incoming], rev


@lru_cache(None)
def mutation(n, x):
    den = n**n
    out = [0] * (n + 1)
    for lost in range(x + 1):
        for gained in range(n - x + 1):
            flips = lost + gained
            out[x - lost + gained] += (math.comb(x, lost) *
                math.comb(n-x, gained) * (n-1)**(n-flips))
    assert sum(out) == den
    return tuple(F(a, den) for a in out)


def mask_mutation(n, x):
    base = (1 << x) - 1
    out = [F(0)] * (n+1)
    for mask in range(1 << n):
        flips = mask.bit_count()
        out[(base ^ mask).bit_count()] += F((n-1)**(n-flips), n**n)
    return tuple(out)


class Clean:
    """Exact clean mean on subsets of the initial errors; <=2**m states.

    Wrong values never change under a clean accepted proposal: only the
    observed target is replaced by its correct weight. Each instance enforces
    the closure cap before recursion, even if some subsets are unreachable.
    """
    def __init__(self, n, t, initial, cap=CAP):
        self.n, self.t, self.initial = n, t, tuple(initial)
        self.errors = sum(x != k for k, x in enumerate(initial))
        if 2**self.errors > cap:
            raise ValueError('clean closure cap exceeded')
        self.cap, self.rows, self.means = cap, {}, {}
        self.adj = [neighbors(n, t, i) for i in range(n+1)]

    def step(self, s, i):
        row = {}
        for y, prob in enumerate(mutation(self.n, s[i])):
            z = list(s)
            if y in self.adj[i]:
                z[y] = y
            z = tuple(z)
            row[z] = row.get(z, F(0)) + prob
        assert sum(row.values()) == 1
        return row

    def sweep(self, s):
        if s in self.rows:
            return self.rows[s]
        dist = {s: F(1)}
        for i in range(self.n+1):
            nxt = {}
            for z, mass in dist.items():
                for w, prob in self.step(z, i).items():
                    nxt[w] = nxt.get(w, F(0)) + mass * prob
            dist = nxt
            assert len(dist) <= self.cap
        self.rows[s] = dist
        assert len(self.rows) <= self.cap
        return dist

    def mean(self, s=None):
        s = self.initial if s is None else s
        if all(x == k for k, x in enumerate(s)):
            return F(0)
        if s not in self.means:
            row = self.sweep(s)
            self.means[s] = (1 + sum(p*self.mean(z) for z, p in row.items()
                                    if z != s)) / (1-row.get(s, F(0)))
        return self.means[s]

    def phase_mean(self, phase):
        if phase == 0:
            return self.mean()
        dist = {self.initial: F(1)}
        for i in range(phase, self.n+1):
            nxt = {}
            for z, mass in dist.items():
                for w, p in self.step(z, i).items():
                    nxt[w] = nxt.get(w, F(0)) + mass*p
            dist = nxt
        return F(self.n+1-phase, self.n+1) + sum(p*self.mean(s) for s,p in dist.items())


def polarized(n, t):
    state, distances = [], []
    for i in range(n+1):
        row = neighbors(n, t, i)
        left, right = row[0], n-row[-1]
        x = n if right >= left else 0
        if x == i:  # Only possible for the full graph, where both distances vanish.
            assert t == n+1
            x = n-i
        state.append(x)
        distances.append(min(abs(x-k) for k in row))
    assert all(x != i for i,x in enumerate(state))
    return tuple(state), distances


def central_distance(n, t):
    b=n+1-t
    return (b+1)//2 + int(t%2==0 and n%4==3 and b>0)


def holding(n, t, state):
    survival = F(1)
    for i in range(n+1):
        rate = sum(mutation(n, state[i])[k] for k in neighbors(n, t, i))
        survival *= 1-rate
    return 1-survival


def write_csv(path, rows):
    with path.open('w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def run(out):
    out.mkdir(parents=True, exist_ok=True)
    counts = {}
    # Exhaustive neighborhood convention checks, independently constructed.
    geometry_checks = 0
    for n in range(2, 65):
        for t in range(2, n+2):
            adj = [neighbors(n,t,i) for i in range(n+1)]
            groups, sources, rev = components(adj)
            if t >= 3:
                assert len(groups) == len(sources) == 1
            else:
                assert len(groups) == (n+2)//2
                assert len(sources) == (n+1)//2
            for i, row in enumerate(adj):
                assert row == literal_neighbors(n,t,i)
                assert len(row) == t and i in row
                if t >= 3:
                    assert all(k in row for k in (i-1,i+1) if 0 <= k <= n)
                geometry_checks += 1
            assert min(max(row[0],n-row[-1]) for row in adj)==central_distance(n,t)
    counts['literal_neighborhood_rows_n2_through64_all_T_ge2'] = geometry_checks
    geometry = []
    for n in [3,4,5,6,7,8,9,16,17,32,33,64,65,128,256,512,1024]:
        for t, names in sorted(candidates(n).items()):
            adj = [neighbors(n,t,i) for i in range(n+1)]
            adj_sets = list(map(set,adj))
            groups, sources, rev = components(adj)
            j0 = set(k for i in rev[0] for k in rev[i])
            geometry.append(dict(n=n,T=t,choices='|'.join(names),
                T_parity=t%2,n_parity=n%2,scc=len(groups),source_scc=len(sources),
                nonreciprocal_edges=sum(i not in adj_sets[k] for i,row in enumerate(adj) for k in row),
                indegree_min=min(map(len,rev)),indegree_max=max(map(len,rev)),
                endpoint0_donors=len(rev[0]),endpointn_donors=len(rev[n]),
                endpoint0_twohop=len(j0),central_distance=central_distance(n,t),
                B0=' '.join(map(str,adj[0])),
                Bn=' '.join(map(str,adj[n]))))
    write_csv(out/'geometry.csv', geometry)
    counts['requested_cardinality_geometry_cells'] = len(geometry)

    mask_checks = 0
    for n in range(2,8):
        for x in range(n+1):
            assert mutation(n,x) == mask_mutation(n,x)
            mask_checks += 1
    counts['literal_mask_weight_rows_n2_through7'] = mask_checks
    seed_checks=0
    for n in range(2,33):
        for t in range(3,n+2):
            a=central_distance(n,t)
            assert a<=n//2
            i=min(range(n+1),key=lambda i:max(neighbors(n,t,i)[0],n-neighbors(n,t,i)[-1]))
            for x in range(n+1):
                rate=sum(mutation(n,x)[k] for k in neighbors(n,t,i))
                assert rate>=F(1,4*2**a*math.factorial(a))
                seed_checks+=1
    counts['central_seed_rate_checks_n2_through32_all_T_ge3_all_parent_weights']=seed_checks

    exact = []
    # All populations n=2,3, including all wrong: local clean closure at most 16.
    # The theorem is checked only where a correct seed exists and T>=3.
    means_checked = phase_checks = max_closure = 0
    max_ratio = F(0)
    for n in (2,3):
        for t in range(3,n+2):
            for s in itertools.product(range(n+1), repeat=n+1):
                m = sum(x!=k for k,x in enumerate(s))
                if m == n+1:
                    continue
                solver = Clean(n,t,s)
                h = solver.mean()
                assert h <= 3*n*m
                means_checked += 1
                for phase in range(1,n+1):
                    assert solver.phase_mean(phase) <= 3*n*m+1
                    phase_checks += 1
                max_closure = max(max_closure,len(solver.rows))
                if m:
                    max_ratio = max(max_ratio,h/F(3*n*m))
    counts.update(exhaustive_seeded_boundary_cases_n2_n3=means_checked,
                  exhaustive_seeded_nonzero_phase_cases_n2_n3=phase_checks,
                  exhaustive_max_materialized_closure=max_closure,
                  maximum_exact_seed_bound_ratio=str(max_ratio))

    # Larger exact counterexamples / repairs have only one or two wrong slots.
    for n in (5,6,9,10,17,18,33,34):
        initial = list(range(n+1))
        if n%2:
            initial[-2:] = [0,0]
            name = 'closed_last_pair'
        else:
            initial[-1] = 0
            name = 'orphan'
        for t in sorted(candidates(n)):
            solver = Clean(n,t,initial)
            h = solver.mean()
            if t >=3:
                assert h <= 3*n*solver.errors
            exact.append(dict(n=n,T=t,case=name,errors=solver.errors,
                mean_sweeps=str(h),mean_decimal=float(h),
                clean_bound_3nm=3*n*solver.errors,
                materialized_closure=len(solver.rows)))
    write_csv(out/'repair.csv',exact)
    counts['larger_exact_repair_cells'] = len(exact)

    traps=[]
    for n in (3,4,5,6,7,8,16,24,32):
        for t in sorted(candidates(n)):
            state, distances=polarized(n,t)
            a=(n+2-t)//2
            assert min(distances)>=a
            q=holding(n,t,state)
            assert 0<q<=1
            lower=F(math.factorial(a),n+1)
            assert 1/q>=lower
            # Direct clean sweep has no return after a repair. Check small cases
            # by the independent subset-state evolution, with the explicit cap.
            if n<=7:
                direct=Clean(n,t,state).sweep(state).get(state,F(0))
                assert direct==1-q
            # All n+1 prescribed active self-overwrites have positive probability.
            # Omit the p**(n+1) gate factor and report the conditional mask mass.
            corner=(2,)+tuple(range(1,n+1))
            entrance=F(1)
            for i in range(n+1):
                entrance*=mutation(n,corner[i])[state[i]]*mutation(n,state[i])[i]
            assert entrance>0
            traps.append(dict(n=n,T=t,a=a,actual_min_distance=min(distances),
                state=' '.join(map(str,state)),escape_per_sweep=str(q),
                mean_first_change_sweeps=str(1/q),mean_decimal=float(1/q),
                factorial_lower=str(lower),active_self_entrance_mask_mass=str(entrance),
                entrance_gate_power=n+1,direct_sweep_verified=n<=7,
                uniform_completion_upper=(4*2**central_distance(n,t)*math.factorial(central_distance(n,t))+3*n*n) if t>=3 else 'not_applicable_T2'))
    write_csv(out/'traps.csv',traps)
    counts['polarized_trap_cells']=len(traps)
    counts['direct_trap_sweep_cells_n3_through7']=sum(r['direct_sweep_verified'] for r in traps)
    forest=[]
    for n in (32,128,512,1024):
        for t,names in sorted(candidates(n).items()):
            adj=[neighbors(n,t,i) for i in range(n+1)]
            d0=sum(0 in row for row in adj)
            d1=sum(1 in row for row in adj)
            for c in (F(1,64),F(1)):
                p=c/n
                a=p/(1-2*p)
                beta=(t-1)*a
                A=(n+1)*t*a
                Aplus=((n+1)*t-d0)*a
                valid=beta<1 and d1*a<1
                exponent=A/((1-beta)*(1-p)) if beta<1 else None
                log_upper=None
                if valid:
                    qstar=(1-p)**(d0-1)*F((n-1)**(n-1),n**n)
                    B0=1/((1-d1*a)*qstar)
                    logC=-math.log1p(-float(beta))+float(exponent)
                    z=logC+math.log(float(Aplus))
                    log_upper=(math.log(n+1)+math.log(float(B0))+
                               max(0,z)+math.log1p(math.exp(-abs(z))))/math.log(10)
                forest.append(dict(n=n,T=t,c=str(c),valid_conditions=valid,
                    beta=str(beta),A=str(A),d1a=str(d1*a),
                    synchronization_exponent=str(exponent) if exponent else '',
                    log10_attempt_upper_float=log_upper if valid else '',
                    numeric_status='illustrative_float_not_interval_certified'))
    write_csv(out/'forest.csv',forest)
    counts['forest_formula_cells']=len(forest)
    counts['local_closure_cap']=CAP
    counts['sampling']='none; deterministic exact arithmetic; no seeds/censoring'
    counts['scope']='All-n statements rely on proof.md, not these finite checks.'
    (out/'verification.json').write_text(json.dumps(counts,indent=2)+'\n')
    return counts


if __name__=='__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('--out',type=Path,required=True)
    args=parser.parse_args()
    print(json.dumps(run(args.out),indent=2))
