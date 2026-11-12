"""Round 23 independent exact audit. No prior-round implementation imports.

Model: pinned ideal reference and labels; literal shared-observation cost
comparisons, ascending own-parent breeder, independent rate-1/n masks.
Only the full-runtime solver kills at aligned phase zero. Reseeding is an
auxiliary stopping event. No trajectories or prospective seeds are sampled.
"""
import argparse
import csv
from fractions import Fraction as F
from functools import lru_cache
import itertools
import json
import math
from pathlib import Path


@lru_cache(None)
def masks(n, x):
    assert 2 <= n <= 8
    counts = [0] * (n + 1)
    for mask in range(1 << n):
        weight = (((1 << x) - 1) ^ mask).bit_count()
        counts[weight] += (n - 1) ** (n - mask.bit_count())
    assert sum(counts) == n ** n
    return tuple(F(v, n ** n) for v in counts)


@lru_cache(None)
def recipients(n, t, i):
    # Independent alternating construction, not the closed interval formula.
    result = [i]
    for gap in range(1, n + 1):
        for direction in ((1, -1) if i % 2 == 0 else (-1, 1)):
            k = i + direction * gap
            if len(result) < t and 0 <= k <= n:
                result.append(k)
    assert len(result) == t
    return tuple(result)


def cost(n, k, b, lo=0, hi=None):
    if hi is None:
        hi = n
    return max(k * (hi - b), (n - k) * (b - lo))


def accept(n, t, w, labels, lo, hi, i, y, observed):
    lo, hi = min(lo, observed), max(hi, observed)
    new, stored = list(w), list(labels)
    for k in recipients(n, t, i):
        if cost(n, k, observed, lo, hi) <= cost(n, k, stored[k], lo, hi):
            new[k], stored[k] = y, observed
    return tuple(new), tuple(stored), lo, hi


@lru_cache(None)
def proposals(n, p, x):
    return tuple((y, z, py * ((1-p)*int(y == z) + p*masks(n, y)[z]))
                 for y, py in enumerate(masks(n, x)) for z in range(n+1)
                 if py * ((1-p)*int(y == z) + p*masks(n, y)[z]))


def transition(n, t, p, w, i):
    row = {}
    target = tuple(range(n+1))
    for y, z, prob in proposals(n, p, w[i]):
        v, b, lo, hi = accept(n, t, w, target, 0, n, i, y, z)
        assert b == target and (lo, hi) == (0, n)
        assert sum(a != b for a, b in zip(w, v)) <= 1
        row[v] = row.get(v, F(0)) + prob
    assert sum(row.values()) == 1
    return row


@lru_cache(None)
def degree(n, t, k):
    return sum(k in recipients(n, t, i) for i in range(n+1))


@lru_cache(None)
def phase_data(n, t, p, k, a):
    delta = 1 - (degree(n, t, k)+1)*p
    assert delta > 0
    # Solve the scalar cyclic compensation recurrence backward from g(k)=0.
    g = F(0)
    j = (k-1) % (n+1)
    values = {k: F(0)}
    while j != k:
        g += delta/F(n+1) + p*int(k in recipients(n, t, j))
        values[j] = g
        j = (j-1) % (n+1)
    return delta, values[a]


@lru_cache(None)
def phi(n, t, p, k, x, a):
    if x == k:
        return F(0)
    delta, g = phase_data(n, t, p, k, a)
    return F(n+1)/delta * (1/masks(n, x)[k] + g)


def seeds(w):
    return tuple(k for k, x in enumerate(w) if k == x)


def workload(n, t, p, w, a):
    return F(0) if seeds(w) else min(phi(n,t,p,k,x,a) for k,x in enumerate(w))


def charge(n, t, p, i, k, x):
    delta, g = phase_data(n,t,p,k,(i+1) % (n+1))
    rho = sum(masks(n,x)[y]*masks(n,y)[k] for y in range(n+1) if y != k)
    return F(n+1)*p/delta * (1-masks(n,x)[k]+g*rho)


def kappa(n,t,p):
    dmax=max(degree(n,t,k) for k in range(n+1))
    return F(2*(n+1))*p*(1-p)/(1-(dmax+1)*p)


def write_csv(path, rows):
    with path.open('w',newline='') as f:
        writer=csv.DictWriter(f,fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def global_check(n,t,p):
    """Exhaustive unit/charge drift on every population and breeder phase."""
    minimum = None
    count = local = entries = 0
    for w in itertools.product(range(n+1),repeat=n+1):
        correct=seeds(w)
        for a in range(n+1):
            row=transition(n,t,p,w,a)
            na=(a+1) % (n+1)
            current=workload(n,t,p,w,a)
            expected=sum(q*workload(n,t,p,v,na) for v,q in row.items())
            vulnerable=len(correct)==1 and correct[0] in recipients(n,t,a)
            budget=charge(n,t,p,a,correct[0],w[a]) if vulnerable else F(0)
            residual=current-expected-int(not correct)+budget
            assert residual >= 0, (n,t,p,w,a,residual)
            minimum=residual if minimum is None else min(minimum,residual)
            count+=1
            if vulnerable:
                assert budget <= kappa(n,t,p)
                entries+=1
            # Stronger original local lemma: other slots can be seeded.
            for k,x in enumerate(w):
                if x==k:
                    continue
                residual_k=phi(n,t,p,k,x,a)-sum(
                    q*phi(n,t,p,k,v[k],na) for v,q in row.items())
                assert residual_k >= 1
                local+=1
    return dict(n=n,T=t,p=str(p),states=count,local_slot_checks=local,
                vulnerable_checks=entries,min_global_slack=str(minimum))


def boundary_system(n,t,p):
    target=tuple(range(n+1))
    states=[(w,a) for w in itertools.product(range(n+1),repeat=n+1)
            for a in range(n+1) if not (w==target and a==0)]
    assert len(states) <= 1023
    index={state:j for j,state in enumerate(states)}
    rows=[]
    for w,a in states:
        rows.append({index[(v,(a+1) % (n+1))]:q
                     for v,q in transition(n,t,p,w,a).items()
                     if (v,(a+1) % (n+1)) in index})
    return states,index,rows


def certify_full(n,t,p):
    """Float proposals, then rigorous rational residual error enclosures.

    If (I-Q)t >= alpha*1 >0, t/alpha bounds all mean times.
    Thus residual error epsilon in any reward solution gives pointwise
    error at most epsilon*t/alpha. No floating tolerance certifies a claim.
    """
    import numpy as np
    states,index,rows=boundary_system(n,t,p)
    size=len(states)
    matrix=np.eye(size)
    rewards=[]
    for r,((w,a),row) in enumerate(zip(states,rows)):
        for j,prob in row.items():
            matrix[r,j]-=float(prob)
        s=seeds(w)
        rewards.append((1,int(not s),int(len(s)==1 and s[0] in recipients(n,t,a))))
    proposed=np.linalg.solve(matrix,np.asarray(rewards,dtype=float))
    values=[[F(format(x,'.12f')) for x in v] for v in proposed]
    residual=[[v[c]-sum(q*values[j][c] for j,q in row.items())-rewards[i][c]
               for c in range(3)] for i,(v,row) in enumerate(zip(values,rows))]
    alpha=1+min(r[0] for r in residual)
    assert alpha>0 and all(v[0]>0 for v in values)
    eps=[max(abs(r[c]) for r in residual) for c in range(3)]
    upper_time=[v[0]/alpha for v in values]
    def interval(r,c):
        return max(F(0),values[r][c]-eps[c]*upper_time[r]), values[r][c]+eps[c]*upper_time[r]
    seeded_checked=0
    max_ratio=F(0)
    for r,(w,a) in enumerate(states):
        if seeds(w):
            # Near-zero rewards may round to zero; the analytic one-step
            # check handles all states, this interval check is separate.
            zl,zu=interval(r,1)
            vl,vu=interval(r,2)
            assert zu <= kappa(n,t,p)*vl
            max_ratio=max(max_ratio,zu/vl)
            seeded_checked+=1
    corner=(2,)+tuple(range(1,n+1))
    r=index[(corner,0)]
    summary=dict(n=n,T=t,p=str(p),live_phase_states=size,
                 seeded_interval_checks=seeded_checked,alpha=str(alpha),
                 residual_error_time=str(eps[0]),residual_error_Z=str(eps[1]),residual_error_V=str(eps[2]),
                 kappa=str(kappa(n,t,p)),max_seeded_Z_over_V_upper=float(max_ratio))
    for c,name in enumerate(('attempts','unseeded','vulnerable')):
        lo,hi=interval(r,c)
        summary[name+'_lower']=str(lo)
        summary[name+'_upper']=str(hi)
        summary[name+'_decimal']=float((lo+hi)/2)
    certificate=[dict(n=n,T=t,p=str(p),weights=','.join(map(str,w)),phase=a,
                      time=str(v[0]),Z=str(v[1]),V=str(v[2])) for (w,a),v in zip(states,values)]
    return summary,certificate


def prepin_checks():
    counts=[0,0]
    witness=None
    for n in (2,3):
        target=tuple(range(n+1))
        w=tuple((k+1) % (n+1) for k in range(n+1))
        for labels in itertools.product(range(n+1),repeat=n+1):
            if labels==target:
                continue
            for lo in range(min(labels)+1):
                for hi in range(max(labels),n+1):
                    for t in range(1,n+2):
                        for i in range(n+1):
                            for z in range(n+1):
                                y=(z+1) % (n+1)
                                v,b,l,h=accept(n,t,w,labels,lo,hi,i,y,z)
                                counts[0]+=1
                                if b==target and (l,h)==(0,n):
                                    assert [k for k in range(n+1) if labels[k]!=k]==[z]
                                    assert z in recipients(n,t,i)
                                    assert all(v[k]==w[k] for k in range(n+1) if k!=z)
                                    counts[1]+=1
                                    if (lo,hi)!=(0,n) and witness is None:
                                        witness=dict(n=n,T=t,phase=i,weights=w,labels=labels,
                                                     lo=lo,hi=hi,child=y,observed=z,after=v)
    return dict(proposals=counts[0],final_pins=counts[1],nonideal_reference_witness=witness)


def geometry_checks():
    count=0
    for n in range(2,65):
        for t in range(1,n+2):
            starts=[]
            for i in range(n+1):
                ns=recipients(n,t,i)
                left=max(0,min(i-(t-1)//2-int(t%2==0 and i%2==1),n+1-t))
                assert set(ns)==set(range(left,left+t))
                if t>=3:
                    assert all(k in ns for k in (i-1,i+1) if 0<=k<=n)
                starts.append(left)
                count+=1
            assert max(degree(n,t,k) for k in range(n+1))<=min(n+1,2*t-1)
            if t>=3:
                actual=min(max(l,n-(l+t-1)) for l in starts)
                claimed=(n+2-t)//2+int(t%2==0 and n%4==3 and t<n+1)
                assert actual==claimed
    return count


def failures():
    # Precise shortcut: removing g cannot give unit drift on every attempt.
    n,t,p,k,a,w=3,2,F(1,192),0,2,(2,1,2,3)
    row=transition(n,t,p,w,a)
    inv=1/masks(n,w[k])[k]
    raw_drift=inv-sum(q*(F(0) if v[k]==k else 1/masks(n,v[k])[k]) for v,q in row.items())
    assert raw_drift==0
    # Full-sweep path with positive exact mask/gate mass.
    n,t,p=3,3,F(1,192)
    w=(2,1,2,3)
    path=[(0,0,0),(1,1,0),(2,2,2),(3,3,3)]
    prob=F(1)
    stages=[w]
    for a,y,z in path:
        prob*=masks(n,w[a])[y]*((1-p)*int(y==z)+p*masks(n,y)[z])
        w,_,_,_=accept(n,t,w,tuple(range(n+1)),0,n,a,y,z)
        stages.append(w)
    assert stages[1]==tuple(range(n+1)) and stages[-1]!=tuple(range(n+1)) and prob>0
    # The clean error count is not a per-attempt noisy drift potential even
    # in a supplied-corner state: breeder 3 cannot reach its only error.
    corner=(2,1,2,3)
    positive=sum(q*sum(v[k]!=k for k in range(4))
                 for v,q in transition(3,3,F(1,192),corner,3).items())-1
    assert positive>0
    return dict(phase_omission=dict(n=3,T=2,p='1/192',k=0,phase=2,weights=(2,1,2,3),
                                    reciprocal_drift=str(raw_drift)),
                reinfection=dict(n=n,T=t,p=str(p),path=path,states=stages,exact_path_mass=str(prob)),
                noisy_error_count=dict(n=3,T=3,p='1/192',phase=3,weights=corner,
                                       expected_error_increase=str(positive)))


def clean_check():
    """Independent sweep-product triangular solve of the seeded clean lemma."""
    rows=[]
    for n in (2,3):
        m=n+1
        target=tuple(range(m))
        populations=sorted(itertools.product(range(m),repeat=m),
                           key=lambda w:sum(x!=k for k,x in enumerate(w)))
        for t in range(3,n+2):
            mean={target:F(0)}
            for w in populations:
                if w==target:
                    continue
                distribution={w:F(1)}
                for a in range(m):
                    nxt={}
                    for v,mass in distribution.items():
                        for dest,q in transition(n,t,F(0),v,a).items():
                            nxt[dest]=nxt.get(dest,F(0))+mass*q
                    distribution=nxt
                hold=distribution.pop(w,F(0))
                assert hold<1
                mean[w]=(1+sum(q*mean[v] for v,q in distribution.items()))/(1-hold)
                errors=sum(x!=k for k,x in enumerate(w))
                if seeds(w):
                    assert mean[w]<=3*n*errors
                    rows.append(dict(n=n,T=t,weights=','.join(map(str,w)),errors=errors,
                                     mean_sweeps=str(mean[w]),bound=3*n*errors))
            # Retain aligned boundary as a separately checked zero-cost case.
            rows.append(dict(n=n,T=t,weights=','.join(map(str,target)),errors=0,
                             mean_sweeps='0',bound=0))
    return rows


def dependency_certificates(repo):
    """Verify prior rational proposals using only this new literal kernel."""
    bundle=repo/'research/reports/large-T-20261109/followup/round-0022'
    groups={}
    with (bundle/'certificates.csv').open() as f:
        for r in csv.DictReader(f):
            key=int(r['n']),int(r['T']),F(r['p'])
            state=tuple(map(int,r['weights'].split(','))),int(r['phase'])
            assert state not in groups.setdefault(key,{})
            groups[key][state]=F(r['proposal'])
    count=0
    strongest=None
    larger_t=None
    with (bundle/'cells.csv').open() as f:
        for cell in csv.DictReader(f):
            n,t,p=int(cell['n']),int(cell['T']),F(cell['p'])
            vals=groups[(n,t,p)]
            assert len(vals)==n**(n+1)*(n+1)
            residuals=[]
            for (w,a),value in vals.items():
                assert not seeds(w)
                residuals.append(value-sum(q*vals[(v,(a+1) % (n+1))]
                    for v,q in transition(n,t,p,w,a).items() if not seeds(v)))
                count+=1
            assert min(residuals)==F(cell['residual_min'])>0
            assert max(residuals)==F(cell['residual_max'])
            if p!=F(1,64*n):
                continue
            for k in range(n+1):
                options=[(j,) if j==k else tuple(x for x in range(n+1) if x!=j)
                         for j in range(n+1)]
                for w in itertools.product(*options):
                    for a in range(n+1):
                        if k not in recipients(n,t,a):
                            continue
                        mass=weighted_lower=F(0)
                        for v,q in transition(n,t,p,w,a).items():
                            if not seeds(v):
                                mass+=q
                                weighted_lower+=q*vals[(v,(a+1) % (n+1))]/max(residuals)
                        assert mass>0
                        conditional_lower=weighted_lower/mass
                        ratio=conditional_lower/kappa(n,t,p)
                        example=dict(n=n,T=t,p=str(p),weights=w,phase=a,unique_seed=k,
                                entrance_probability=str(mass),conditional_mean_attempts_lower=str(conditional_lower),
                                weighted_mean_attempts_lower=str(weighted_lower),kappa=str(kappa(n,t,p)),
                                conditional_over_kappa_lower=str(ratio))
                        if strongest is None or ratio>strongest[0]:
                            strongest=(ratio,example)
                        if t>=3 and (larger_t is None or ratio>larger_t[0]):
                            larger_t=(ratio,example)
    assert strongest[0]>1
    return dict(prior_cells=len(groups),prior_rational_residuals=count,
                conditioning_shortcut_counterexample=strongest[1],
                larger_T_conditioning_counterexample=larger_t[1])


def coefficients(n,t,degree_max):
    """Independent signed sweep-polynomial expansion, not phase recurrences.

    Retains all intermediate aligned states, drops only aligned sweep ends,
    and includes the complete activated-minus-clean signed row.
    """
    assert (n,t,degree_max) in ((2,3,1),(3,3,2),(3,4,2))
    target=tuple(range(n+1))
    states=sorted(itertools.product(range(n+1),repeat=n+1),
                  key=lambda w:sum(x!=k for k,x in enumerate(w)))
    local={}
    for w in states:
        for a in range(n+1):
            clean=transition(n,t,F(0),w,a)
            active=transition(n,t,F(1),w,a)
            delta={v:active.get(v,F(0))-clean.get(v,F(0)) for v in set(clean)|set(active)}
            delta={v:q for v,q in delta.items() if q}
            assert sum(delta.values())==0 and sum(abs(q) for q in delta.values())<=2
            local[(w,a)]=(clean,delta)
    sweeps={}
    for start in states[1:]:
        layers=[{start:F(1)}]+[{} for _ in range(degree_max)]
        for a in range(n+1):
            nxt=[{} for _ in layers]
            for degree,layer in enumerate(layers):
                for w,mass in layer.items():
                    for added,operator in enumerate(local[(w,a)]):
                        if degree+added>degree_max:
                            continue
                        dest_layer=nxt[degree+added]
                        for v,q in operator.items():
                            dest_layer[v]=dest_layer.get(v,F(0))+mass*q
            layers=[{w:q for w,q in layer.items() if q} for layer in nxt]
        for layer in layers:
            layer.pop(target,None)
        sweeps[start]=layers
    solutions=[]
    for degree in range(degree_max+1):
        values={target:F(0)}
        for w in states[1:]:
            forcing=F(1) if degree==0 else sum(
                q*solutions[degree-ell][v]
                for ell in range(1,degree+1) for v,q in sweeps[w][ell].items())
            clean=sweeps[w][0]
            values[w]=(forcing+sum(q*values[v] for v,q in clean.items() if v!=w))/(1-clean.get(w,F(0)))
        solutions.append(values)
    corner=(2,)+tuple(range(1,n+1))
    return [s[corner] for s in solutions]


def coefficient_checks(repo):
    expected={}
    if repo is not None:
        with (repo/'research/reports/large-T-20261109/followup/round-0021/coefficients.csv').open() as f:
            for r in csv.DictReader(f):
                expected[int(r['n']),int(r['T']),int(r['degree'])]=F(r['coefficient'])
    output=[]
    for n,t,d in ((2,3,1),(3,3,2),(3,4,2)):
        values=coefficients(n,t,d)
        for j,value in enumerate(values):
            if expected:
                assert value==expected[n,t,j]
            bound=values[0] if j==0 else 2**j*(n+1)**j*(3*n*(j+1)+1)**j*values[0]
            assert abs(value)<=bound
            output.append(dict(n=n,T=t,degree=j,coefficient=str(value),bound=str(bound),
                               prior_match=bool(expected)))
    return output


def run(out,repo=None):
    out.mkdir(parents=True,exist_ok=True)
    global_rows=[]
    for n in (2,3):
        for t in range(1,n+2):
            dmax=max(degree(n,t,k) for k in range(n+1))
            for p in (F(0),F(1,64*n),F(99,100*(dmax+1))):
                global_rows.append(global_check(n,t,p))
    write_csv(out/'global.csv',global_rows)
    cells,certs=[],[]
    for n in (2,3):
        for t in range(1,n+2):
            for p in (F(1,64*n),F(1,4*n)):
                cell,cert=certify_full(n,t,p)
                cells.append(cell)
                certs.extend(cert)
    write_csv(out/'occupation.csv',cells)
    write_csv(out/'certificates.csv',certs)
    clean=clean_check()
    write_csv(out/'clean.csv',clean)
    coeff=coefficient_checks(repo)
    write_csv(out/'coefficients.csv',coeff)
    result=dict(global_cells=len(global_rows),global_phase_states=sum(r['states'] for r in global_rows),
                local_slot_checks=sum(r['local_slot_checks'] for r in global_rows),
                vulnerable_checks=sum(r['vulnerable_checks'] for r in global_rows),
                full_boundary_cells=len(cells),full_boundary_phase_states=len(certs),
                seeded_interval_checks=sum(r['seeded_interval_checks'] for r in cells),
                exact_clean_seeded_boundary_cases=len(clean),
                independent_sweep_coefficients=len(coeff),
                geometry_rows=geometry_checks(),prepin=prepin_checks(),
                research_samples=0,finite_scope='n=2,3 all populations/all T/all phases; see grids in CSV')
    if repo is not None:
        result['prior_certificates']=dependency_certificates(repo)
    (out/'witnesses.json').write_text(json.dumps(failures(),indent=2)+'\n')
    (out/'verification.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
    print(json.dumps(result,indent=2,sort_keys=True))


if __name__=='__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('--out',type=Path,required=True)
    parser.add_argument('--repo',type=Path)
    args=parser.parse_args()
    run(args.out,args.repo)
