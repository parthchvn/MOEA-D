"""Tiny phase-response check: <=256 populations / 1024 phase states, no matrix."""
import argparse
from fractions import Fraction as F
import itertools
from pathlib import Path
from structure import mutation, neighbors, write_csv


class Response:
    def __init__(self,n,t,cap=1024):
        if (n+1)**(n+2)>cap:
            raise ValueError('phase-state cap exceeded')
        self.n,self.t,self.m=n,t,n+1
        self.states=sorted(itertools.product(range(n+1),repeat=n+1),
                           key=lambda s:sum(x!=k for k,x in enumerate(s)))
        self.adj=[neighbors(n,t,i) for i in range(n+1)]
        self.clean={(s,i):self.row(s,i,False) for s in self.states for i in range(n+1)}

    def row(self,s,i,active):
        out={}
        for y,p in enumerate(mutation(self.n,s[i])):
            labels=enumerate(mutation(self.n,y)) if active else [(y,F(1))]
            for k,q in labels:
                z=list(s)
                if k in self.adj[i]:
                    z[k]=y
                z=tuple(z)
                out[z]=out.get(z,F(0))+p*q
        assert sum(out.values())==1
        return out

    def solve_clean(self,forcing):
        values={}
        aligned=tuple(range(self.m))
        for s in self.states:
            if s==aligned:
                v=[F(0)]*self.m
                for i in range(self.n,0,-1):
                    v[i]=forcing(s,i)+v[(i+1)%self.m]
                values[s]=tuple(v)
                continue
            # Backward affine recursion in the unknown phase-zero value.
            b,c=F(1),F(0)
            extra={}
            for i in range(self.n,-1,-1):
                row=self.clean[s,i]
                extra[i]=sum(p*values[z][(i+1)%self.m] for z,p in row.items() if z!=s)
                same=row.get(s,F(0))
                b,c=same*b,forcing(s,i)+extra[i]+same*c
            v0=c/(1-b)
            v=[F(0)]*self.m
            nxt=v0
            for i in range(self.n,-1,-1):
                v[i]=forcing(s,i)+extra[i]+self.clean[s,i].get(s,F(0))*nxt
                nxt=v[i]
            assert v[0]==v0
            values[s]=tuple(v)
        # Exact Bellman residual at every live phase, including aligned interiors.
        for s in self.states:
            for i in range(self.m):
                if s==aligned and i==0:
                    continue
                assert values[s][i]==forcing(s,i)+sum(
                    p*values[z][(i+1)%self.m] for z,p in self.clean[s,i].items())
        return values

    def coefficients(self,degree):
        values=self.solve_clean(lambda s,i:F(1,self.m))
        corner=(2,)+tuple(range(1,self.m))
        output=[values[corner][0]]
        for j in range(1,degree+1):
            f={}
            for s in self.states:
                for i in range(self.m):
                    ni=(i+1)%self.m
                    f[s,i]=sum(p*values[z][ni] for z,p in self.row(s,i,True).items())-sum(
                        p*values[z][ni] for z,p in self.clean[s,i].items())
            values=self.solve_clean(lambda s,i:f[s,i])
            output.append(values[corner][0])
        return output


def run(out):
    out.mkdir(parents=True,exist_ok=True)
    rows=[]
    for n,t in ((2,3),(3,3),(3,4)):
        solver=Response(n,t)
        coeff=solver.coefficients(n-1)
        q=1
        for i in range(n+1):
            if 0 in neighbors(n,t,i):
                q*=1-mutation(n,2 if i==0 else i)[0]
        q=1-q
        assert coeff[0]==1/q
        for j,value in enumerate(coeff):
            L=3*n*(j+1)+1
            bound=F(1,q) if j==0 else F(2**j*(n+1)**j*L**j,q)
            assert abs(value)<=bound
            rows.append(dict(n=n,T=t,degree=j,coefficient=str(value),
                             decimal=float(value),proved_bound=str(bound),
                             phase_states=(n+1)**(n+2)))
    write_csv(out/'coefficients.csv',rows)
    return rows


if __name__=='__main__':
    p=argparse.ArgumentParser()
    p.add_argument('--out',type=Path,required=True)
    a=p.parse_args()
    rows=run(a.out)
    print(f'Checked {len(rows)} exact coefficients; maximum 1024 phase states.')
