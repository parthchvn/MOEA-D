#!/usr/bin/env python3
"""Independent exact n=3 full-population derivative; standard library only.

Enumerates literal masks and scalarization comparisons. It uses neither the
two-error reduction nor the disjoint-donor formula in coefficient.py.
"""
import argparse
import csv
from fractions import Fraction as F
from itertools import product
import json
from pathlib import Path
import sys


def neighbors(n,t,i):
    result=[i];distance=1
    while len(result)<t:
        sides=[i+distance,i-distance] if i%2==0 else [i-distance,i+distance]
        result.extend(k for k in sides if 0<=k<=n)
        distance+=1
    return result[:t]


def literal_kernel(n):
    result=[]
    for x in range(n+1):
        bits=[1]*x+[0]*(n-x);row=[0]*(n+1)
        for mask in product((0,1),repeat=n):
            row[sum(b^m for b,m in zip(bits,mask))]+=(n-1)**(n-sum(mask))
        result.append(row)
    return result,n**n


def replace(w,n,t,i,y,z):
    result=list(w)
    for k in neighbors(n,t,i):
        if max(k*(n-z),(n-k)*z)<=k*(n-k):result[k]=y
    return tuple(result)


def full_derivative(n,t):
    d,den=literal_kernel(n)
    states=list(product(range(n+1),repeat=n+1));target=tuple(range(n+1))
    clean=[];active=[]
    for i in range(n+1):
        c={};a={}
        for w in states:
            cr={};ar={}
            for y in range(n+1):
                v=replace(w,n,t,i,y,y);cr[v]=cr.get(v,0)+d[w[i]][y]
                for z in range(n+1):
                    v=replace(w,n,t,i,y,z)
                    ar[v]=ar.get(v,0)+d[w[i]][y]*d[y][z]
            assert sum(cr.values())==den and sum(ar.values())==den**2
            c[w]=cr;a[w]=ar
        clean.append(c);active.append(a)
    # Build a full sweep row, then solve in increasing number of incorrect slots.
    h={target:F(0)}
    order=sorted(states,key=lambda w:sum(x!=k for k,x in enumerate(w)))
    sweep_den=den**(n+1)
    for w in order[1:]:
        dist={w:1}
        for i in range(n+1):
            new={}
            for u,m in dist.items():
                for v,p in clean[i][u].items():new[v]=new.get(v,0)+m*p
            dist=new
        assert sum(dist.values())==sweep_den
        assert all(v==w or v in h for v in dist)
        h[w]=(sweep_den+sum(m*h[v] for v,m in dist.items() if v!=w))/(sweep_den-dist.get(w,0))
    # Aligned mid-sweep states remain present. Killing occurs only at boundaries.
    suffix=[None]*(n+2);suffix[-1]=h
    for i in reversed(range(n+1)):
        suffix[i]={w:sum(F(m,den)*suffix[i+1][v] for v,m in clean[i][w].items()) for w in states}
    corner=(2,)+tuple(range(1,n+1));prefix={corner:F(1)};rhs=F(0)
    aligned_prefix_rhs=F(0)
    for i in range(n+1):
        for w,p in prefix.items():
            delta=sum(F(m,den**2)*suffix[i+1][v] for v,m in active[i][w].items())-suffix[i][w]
            rhs+=p*delta
            if w==target:aligned_prefix_rhs+=p*delta
        new={}
        for w,p in prefix.items():
            for v,m in clean[i][w].items():new[v]=new.get(v,F(0))+p*F(m,den)
        prefix=new
    assert set(prefix)=={corner,target}
    q=prefix[target]
    assert h[corner]==1/q
    derivative=rhs/q
    return dict(n=n,T=t,states=len(states),baseline=str(h[corner]),derivative=str(derivative),
                decimal=float(derivative),aligned_prefix_contribution=str(aligned_prefix_rhs/q))


def main(bundle):
    if hasattr(sys,'set_int_max_str_digits'):sys.set_int_max_str_digits(0)
    full=[full_derivative(3,t) for t in (2,3)]
    components=list(csv.DictReader((bundle/'components.csv').open()))
    for r in full:
        saved=sum(F(c['coefficient']) for c in components if c['n']=='3' and c['T']==str(r['T']))
        assert saved==F(r['derivative'])
        assert F(r['aligned_prefix_contribution'])>0
    gap=F(full[1]['derivative'])-F(full[0]['derivative'])
    rows=list(csv.DictReader((bundle/'coefficients.csv').open()))
    saved=next(r for r in rows if r['n']=='3')
    assert gap==F(saved['gap_rational'])>0
    signs={r['n']:('positive' if F(r['gap_rational'])>0 else 'negative')
           for r in rows if r['gap_rational']}
    assert all(signs[str(n)]=='negative' for n in range(4,11))
    return dict(status='mechanically checked',arithmetic='exact integer/Fraction',
                full_state_checks=full,gap=str(gap),gap_decimal=float(gap),
                exact_signs=signs,scientific_trajectories=0,
                scope='The full-state cross-check is n=3 only; n=4..10 signs use the analytic reduction.')


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--bundle',type=Path,default=Path(__file__).resolve().parent)
    p.add_argument('--out',type=Path)
    args=p.parse_args();result=main(args.bundle)
    text=json.dumps(result,indent=2,sort_keys=True)+'\n'
    if args.out:args.out.write_text(text)
    else:print(text,end='')
