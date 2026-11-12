"""Verify the new full-boundary rational certificates without NumPy/solves."""
import argparse
import csv
from fractions import Fraction as F
import json
from pathlib import Path
from audit import boundary_system, seeds, recipients, kappa


def run(bundle):
    groups={}
    with (bundle/'certificates.csv').open() as f:
        for r in csv.DictReader(f):
            key=int(r['n']),int(r['T']),F(r['p'])
            state=tuple(map(int,r['weights'].split(','))),int(r['phase'])
            assert state not in groups.setdefault(key,{})
            groups[key][state]=tuple(F(r[name]) for name in ('time','Z','V'))
    count=seeded=0
    with (bundle/'occupation.csv').open() as f:
        cells=list(csv.DictReader(f))
    assert len(cells)==len(groups)==14
    for cell in cells:
        n,t,p=int(cell['n']),int(cell['T']),F(cell['p'])
        states,index,rows=boundary_system(n,t,p)
        vals=groups[(n,t,p)]
        assert set(vals)==set(states)
        values=[vals[state] for state in states]
        residual=[]
        for i,((w,a),row) in enumerate(zip(states,rows)):
            s=seeds(w)
            reward=(1,int(not s),int(len(s)==1 and s[0] in recipients(n,t,a)))
            residual.append(tuple(values[i][c]-sum(q*values[j][c] for j,q in row.items())-reward[c]
                                  for c in range(3)))
        alpha=1+min(r[0] for r in residual)
        eps=[max(abs(r[c]) for r in residual) for c in range(3)]
        assert alpha==F(cell['alpha'])>0
        assert all(v[0]>0 for v in values)
        assert eps==[F(cell['residual_error_'+name]) for name in ('time','Z','V')]
        for r,(w,a) in enumerate(states):
            count+=1
            upper_time=values[r][0]/alpha
            if seeds(w):
                zu=values[r][1]+eps[1]*upper_time
                vl=max(F(0),values[r][2]-eps[2]*upper_time)
                assert zu<=kappa(n,t,p)*vl
                seeded+=1
        r=index[((2,)+tuple(range(1,n+1)),0)]
        for c,name in enumerate(('attempts','unseeded','vulnerable')):
            bound=eps[c]*values[r][0]/alpha
            assert F(cell[name+'_lower'])==max(F(0),values[r][c]-bound)
            assert F(cell[name+'_upper'])==values[r][c]+bound
    result=dict(cells=len(cells),phase_states=count,seeded_occupation_enclosures=seeded,
                status='all exact residual and enclosure checks pass; no numerical solve')
    print(json.dumps(result,indent=2,sort_keys=True))
    return result


if __name__=='__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('--bundle',type=Path,default=Path(__file__).resolve().parent)
    run(parser.parse_args().bundle)
