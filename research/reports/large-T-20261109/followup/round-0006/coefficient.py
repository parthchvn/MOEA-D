#!/usr/bin/env python3
"""Deterministic first derivative at p=0; no sampling or finite differences.

The exact version uses rational mutation probabilities and at-most-two-error
noiseless states. The fast version additionally uses the disjoint-donor formula
for targets k>=3. See derivation.md for the mathematical justification.
"""
from fractions import Fraction as F
from math import comb
from functools import lru_cache

def recipients(n,t,i):
    out=[i]
    for d in range(1,n+1):
        for s in ((1,-1) if i%2==0 else (-1,1)):
            if 0<=i+s*d<=n: out.append(i+s*d)
            if len(out)==t: return tuple(out)

def kernel(n,exact=True):
    if exact:
        den=n**n
        return [[F(sum(comb(x,a)*comb(n-x,y-x+a)*(n-1)**(n-a-(y-x+a))
                  for a in range(max(0,x-y),min(x,n-y)+1)),den)
                 for y in range(n+1)] for x in range(n+1)]
    import numpy as np
    # Stable binomial PMFs at rate 1/n and their convolution.
    bins=[]
    for m in range(n+1):
        row=np.empty(m+1);row[0]=(1-1/n)**m
        for j in range(m):row[j+1]=row[j]*(m-j)/(j+1)/(n-1)
        bins.append(row)
    return np.array([np.convolve(bins[x][::-1],bins[n-x]) for x in range(n+1)])

class Solver:
    def __init__(self,n,t,exact=True):
        if n<3 or t not in (2,3):raise ValueError('This reduction is for n>=3 and T in {2,3}')
        self.n=n;self.t=t;self.exact=exact
        self.d=kernel(n,exact);self.zero=F(0) if exact else 0.
        self.one=F(1) if exact else 1.
        self.b=[recipients(n,t,i) for i in range(n+1)]
        self.inc=[tuple(i for i in range(n+1) if k in self.b[i]) for k in range(n+1)]
        self.q=1-(1-self.d[2][0])*(1-self.d[1][0])
    @lru_cache(None)
    def sweep(self,errors,start=0):
        dist={errors:self.one}
        donors=sorted(set(i for k,_ in errors for i in self.inc[k] if i>=start))
        for i in donors:
            nxt={}
            for state,mass in dist.items():
                x=dict(state).get(i,i);stay=self.one
                for k,y in state:
                    if k in self.b[i]:
                        p=self.d[x][k];stay-=p
                        fixed=tuple(e for e in state if e[0]!=k)
                        nxt[fixed]=nxt.get(fixed,self.zero)+mass*p
                nxt[state]=nxt.get(state,self.zero)+mass*stay
            dist=nxt
        return dist
    @lru_cache(None)
    def h(self,errors):
        if not errors:return self.zero
        dist=self.sweep(errors)
        hit=sum(p for e,p in dist.items() if e!=errors)
        return (1+sum(p*self.h(e) for e,p in dist.items() if e!=errors))/hit
    @lru_cache(None)
    def value(self,errors,start):
        return sum(p*self.h(e) for e,p in self.sweep(errors,start).items())
    def change(self,state,k,y):
        e=dict(state)
        if y==k:e.pop(k,None)
        else:e[k]=y
        return tuple(sorted(e.items()))
    def derivative(self,targets=None):
        contrib=[self.zero]*(self.n+1)
        # Active-minus-inactive proposal, retaining aligned mid-sweep prefixes.
        f=self.one
        for i in range(self.n+1):
            for state,prob in ((((0,2),),f),((),1-f)):
                if not prob:continue
                x=dict(state).get(i,i)
                base=self.value(state,i+1)
                for k in self.b[i]:
                    if targets is not None and k not in targets:continue
                    # Active accepted into k vs no acceptance.
                    for y in range(self.n+1):
                        if y==k:continue
                        weight=self.d[x][y]*self.d[y][k]
                        if weight:
                            contrib[k]+=prob*weight*(self.value(self.change(state,k,y),i+1)-base)
                    # Noise can suppress a clean acceptance y=k.
                    weight=self.d[x][k]*(self.d[k][k]-1)
                    if weight:
                        contrib[k]+=prob*weight*(self.value(self.change(state,k,k),i+1)-base)
            if i==0:f*=1-self.d[2][0]
            if i==1:f*=1-self.d[1][0]
        return [v/self.q for v in contrib]

    def disjoint(self,k):
        """Contribution when I_k is disjoint from {0,1}, exact or floating."""
        assert k>=2 and not set(self.inc[k])&{0,1}
        d=self.d;one=self.one
        external=one
        for j in self.inc[k]:
            if j!=k:external*=1-d[j][k]
        result=self.zero
        for y in range(self.n+1):
            if y==k:continue
            r=(1-external)+external*d[y][k]
            numerator=self.zero
            for i in self.inc[k]:
                suffix=one
                for j in self.inc[k]:
                    if j>i:suffix*=1-d[y if j==k else j][k]
                numerator+=d[i][y]*d[y][k]*suffix
            result+=numerator/(r*(self.q+(1-self.q)*r))
        return result

    def fast(self):
        """Vectorized disjoint-donor terms; remaining terms use the same recurrence."""
        if self.exact:
            result=self.derivative(targets={0,1,2})
            for k in range(3,self.n+1):result[k]=self.disjoint(k)
            return result
        import numpy as np
        result=self.derivative(targets={0,1,2})
        for k in range(3,self.n+1):
            col=self.d[:,k]
            # Stable probability of at least one external repair.
            a=0.
            for j in self.inc[k]:
                if j!=k:a+=self.d[j][k]*(1-a)
            r=a+(1-a)*col
            num=np.zeros(self.n+1)
            for i in self.inc[k]:
                suffix=np.ones(self.n+1)
                for j in self.inc[k]:
                    if j>i:suffix*=1-(col if j==k else self.d[j][k])
                num+=self.d[i,:]*col*suffix
            # T=2 and even n: the final target has no external donor.
            # Cancel its possibly underflowed own-repair probability exactly.
            if not a:
                terms=self.d[k,:]/(self.q+(1-self.q)*col)
            else:
                terms=num/(r*(self.q+(1-self.q)*r))
            terms[k]=0
            result[k]=float(np.sum(terms))
        return result

    @staticmethod
    def clear():
        # lru_cache descriptors otherwise retain old solver objects.
        Solver.sweep.cache_clear();Solver.h.cache_clear();Solver.value.cache_clear()


def main(out,exact_ns,numeric_ns):
    import csv,json,sys
    # These integers arise from our finite rational calculation, not user input.
    if hasattr(sys,'set_int_max_str_digits'):sys.set_int_max_str_digits(0)
    from pathlib import Path
    from math import log
    out=Path(out);out.mkdir(parents=True,exist_ok=True)
    rows=[];components=[]
    for n,exact in [(n,True) for n in exact_ns]+[(n,False) for n in numeric_ns]:
        values=[]
        for t in (2,3):
            s=Solver(n,t,exact=exact)
            c=s.fast();values.append(c)
            baseline=float(1/s.q)
            if exact:
                for k,v in enumerate(c):
                    components.append(dict(n=n,T=t,target=k,coefficient=str(v),decimal=float(v)))
            s.clear()
        a,b=map(sum,values);gap=b-a
        rows.append(dict(n=n,arithmetic='exact rational' if exact else 'float64 deterministic',
            zero_noise_sweeps=baseline,derivative_T2=float(a),derivative_T3=float(b),
            gap_sweeps=float(gap),gap_attempts=(n+1)*float(gap),
            gap_over_n_log_n=float(gap)/(n*log(n)),
            gap_over_n_plus_half_log_n=float(gap)/n+.5*log(n),
            gap_rational=str(gap) if exact else ''))
    for name,table in [('coefficients.csv',rows),('components.csv',components)]:
        with (out/name).open('w',newline='') as f:
            w=csv.DictWriter(f,fieldnames=list(table[0]));w.writeheader();w.writerows(table)
    return dict(status='pass',exact_n=exact_ns,numerical_n=numeric_ns,
                coefficient_rows=len(rows),component_rows=len(components),
                scientific_trajectories=0,scientific_seeds=[],
                numeric_scope='Float rows are deterministic evaluations, not interval certificates or empirical samples.')


if __name__=='__main__':
    import argparse,json
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--out',default=str(__import__('pathlib').Path(__file__).resolve().parent))
    p.add_argument('--exact-n',type=int,nargs='+',default=list(range(3,11)))
    p.add_argument('--numeric-n',type=int,nargs='+',default=[16,17,32,33,64,65,128,129,256,257,512,513,1024,1025])
    args=p.parse_args()
    print(json.dumps(main(args.out,args.exact_n,args.numeric_n),sort_keys=True))
