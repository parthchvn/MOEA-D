"""Verify published rational vectors with literal masks/cost comparisons.

Standard library only. This intentionally does not import excursions.py.
All populations outside the all-wrong set are killed immediately; completion
at sweep boundaries is a separate stopping event in the theorem.
"""
import argparse
import csv
from fractions import Fraction as F
from functools import lru_cache
import json
from pathlib import Path


@lru_cache(None)
def d(n,x):
    out=[F(0)]*(n+1)
    genotype=(1<<x)-1
    for mask in range(1<<n):
        out[(genotype^mask).bit_count()]+=F((n-1)**(n-mask.bit_count()),n**n)
    return tuple(out)


@lru_cache(None)
def recipients(n,t,i):
    found=[i]
    for distance in range(1,n+1):
        for direction in ((1,-1) if i%2==0 else (-1,1)):
            k=i+direction*distance
            if len(found)<t and 0<=k<=n:
                found.append(k)
    return tuple(found)


def row(n,t,p,w,i):
    out={}
    for y,py in enumerate(d(n,w[i])):
        for observed in range(n+1):
            chance=py*((1-p)*int(observed==y)+p*d(n,y)[observed])
            if not chance:
                continue
            z=list(w)
            for k in recipients(n,t,i):
                incumbent=max(k*(n-k),(n-k)*k)
                candidate=max(k*(n-observed),(n-k)*observed)
                if candidate<=incumbent:
                    z[k]=y
            if all(x!=k for k,x in enumerate(z)):
                key=(tuple(z),(i+1)%(n+1))
                out[key]=out.get(key,F(0))+chance
    return out


def run(bundle):
    groups={}
    with (bundle/'certificates.csv').open() as f:
        for item in csv.DictReader(f):
            key=int(item['n']),int(item['T']),F(item['p'])
            state=tuple(map(int,item['weights'].split(','))),int(item['phase'])
            group=groups.setdefault(key,{})
            assert state not in group
            group[state]=F(item['proposal'])
    with (bundle/'cells.csv').open() as f:
        cells=list(csv.DictReader(f))
    assert len(cells)==len(groups)==14
    checked=0
    for cell in cells:
        n,t,p=int(cell['n']),int(cell['T']),F(cell['p'])
        values=groups[(n,t,p)]
        assert len(values)==n**(n+1)*(n+1)==int(cell['states'])
        assert len(values)<=324
        residuals=[]
        for (w,phase),v in values.items():
            assert v>0 and all(x!=k for k,x in enumerate(w))
            transitions=row(n,t,p,w,phase)
            residuals.append(v-sum(q*values[state] for state,q in transitions.items()))
            checked+=1
        assert min(residuals)==F(cell['residual_min'])>0
        assert max(residuals)==F(cell['residual_max'])
    result=dict(cells=len(cells),literal_mask_scalarization_residuals=checked,
                status='all rational residual bounds match; no NumPy used')
    print(json.dumps(result,indent=2,sort_keys=True))
    return result


if __name__=='__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('--bundle',type=Path,default=Path(__file__).resolve().parent)
    run(parser.parse_args().bundle)
