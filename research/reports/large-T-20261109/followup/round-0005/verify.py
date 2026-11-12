#!/usr/bin/env python3
"""Verify saved rational certificates without NumPy or floating linear solves.

Run: python deliverables/verify.py --bundle deliverables
All transition probabilities and residual comparisons are exact integers/Fractions.
"""
import argparse
import csv
from fractions import Fraction as F
import json
from math import lcm
from pathlib import Path
from audit import (SCALE, constants, exact_back, literal_replace, local_potentials,
                   mask_kernel, posterior_witness, reward_nums, transitions)


def certify(nums, ids, steps, den):
    factor=den**len(steps)
    propagated=exact_back(steps,den,nums)
    assert all(nums[i]>0 for i in ids)
    assert all(nums[i]==0 for i in set(range(len(nums)))-set(ids))
    drifts=[F(nums[i]*factor-propagated[i],SCALE*factor) for i in ids]
    low,high=min(drifts),max(drifts)
    assert low>0
    return dict(lower=[F(v,SCALE)/high for v in nums],
                upper=[F(v,SCALE)/low for v in nums],dmin=low,dmax=high,ids=ids)


def verify(bundle):
    saved=json.loads((bundle/'verification.json').read_text())
    cells=list(csv.DictReader((bundle/'expectations.csv').open()))
    all_cert=list(csv.DictReader((bundle/'certificates.csv').open()))
    expected_keys={(n,t,str(p)) for n in (2,3)
                   for p in (F(0),F(1,64*n),F(1,4*n))+((F(1,n),) if n==3 else ())
                   for t in range(1,n+2)}
    assert len(cells)==len(expected_keys)==25
    assert {(int(r['n']),int(r['T']),r['p']) for r in cells}==expected_keys
    counts=dict(cells=0,state_cells=0,transition_rows=0,simultaneous_inequalities=0,
                endpoint_inequalities=0,occupation_inequalities=0,corner_lower_inequalities=0,
                corner_upper_inequalities=0)
    for row in cells:
        n,t,p=int(row['n']),int(row['T']),F(row['p'])
        group=[r for r in all_cert if r['n']==str(n) and r['T']==str(t) and r['p']==str(p)]
        states,index,steps,den=transitions(n,t,p)
        assert len(group)==len(states)==int(row['states'])
        assert [tuple(map(int,r['state'].split())) for r in group]==states
        assert all(int(r['scale'])==SCALE for r in group)
        values={name:[int(r[name]) for r in group] for name in
                ('time_num','endpoint_num','own_num','occupation_num')}
        exact=certify(values['time_num'],[i for i,w in enumerate(states) if w!=tuple(range(n+1))],steps,den)
        endpoint=certify(values['endpoint_num'],[i for i,w in enumerate(states) if w[0]!=0],steps,den)
        corner=index[(2,)+tuple(range(1,n+1))]
        for prefix,certificate in [('time',exact),('endpoint',endpoint)]:
            assert F(row[prefix+'_drift_min'])==certificate['dmin']
            assert F(row[prefix+'_drift_max'])==certificate['dmax']
        for prefix,certificate in [('simultaneous',exact),('endpoint',endpoint)]:
            for side in ('lower','upper'):
                assert F(row[prefix+'_'+side])==certificate[side][corner]
        factor=den**len(steps)
        occupations=[]
        for name,only,prefix in [('own_num',True,'own'),('occupation_num',False,'occupation')]:
            nums=values[name]
            reward=reward_nums(states,steps,den,only)
            propagated=exact_back(steps,den,nums)
            assert all(nums[i]==0 for i,w in enumerate(states) if w[0]==0)
            error=max(abs(F(nums[i]*factor-propagated[i]-SCALE*reward[i],SCALE*factor))
                      for i in endpoint['ids'])
            assert error==F(row[prefix+'_residual'])
            cert=dict(lower=[max(F(0),F(v,SCALE)-error*endpoint['upper'][i]) for i,v in enumerate(nums)],
                      upper=[F(v,SCALE)+error*endpoint['upper'][i] for i,v in enumerate(nums)])
            output_prefix='own_bad' if only else 'occupation'
            assert all(F(row[output_prefix+'_'+side])==cert[side][corner] for side in ('lower','upper'))
            occupations.append(cert)
        h,bound=local_potentials(n,p),constants(n,t,p)
        potentials=[sum(h[k][v] for k,v in enumerate(w)) for w in states]
        if p==0:
            hd=lcm(*(v.denominator for v in potentials))
            hn=[int(v*hd) for v in potentials]
            hp=exact_back(steps,den,hn)
            assert all(hn[i]*factor-hp[i]>=hd*factor for i in exact['ids'])
            assert all(states[j][1]==1 for rows in steps for i,r in enumerate(rows)
                       if states[i][1]==1 for j,mass in r if mass)
        for i,w in enumerate(states):
            if 'C_lower' in bound:
                assert not p or exact['upper'][i]<=bound['C_lower']*potentials[i]
                counts['simultaneous_inequalities']+=1
            if w[1]==1 and w[0]!=0:
                for cert,multiplier in zip(occupations,(bound['d1']*bound['a'],
                                                        (n+1)*bound['d1']*(bound['a']+p))):
                    assert not p or cert['upper'][i]<=multiplier*endpoint['lower'][i]
                    counts['occupation_inequalities']+=1
        if 'B0' in bound:
            assert endpoint['upper'][corner]<=bound['B0']
            counts['endpoint_inequalities']+=1
        if 'lower' in bound:
            assert exact['upper'][corner]>=bound['lower']
            assert not p or exact['lower'][corner]>=bound['lower']
            counts['corner_lower_inequalities']+=1
        if 'C_lower' in bound and 'B0' in bound:
            assert exact['upper'][corner]<=bound['B0']*(1+bound['C_lower']*bound['Aplus'])
            counts['corner_upper_inequalities']+=1
        counts['cells']+=1
        counts['state_cells']+=len(states)
        counts['transition_rows']+=len(states)*(n+1)
    assert counts==saved['counts']
    assert len(all_cert)==counts['state_cells']
    witness=saved['witnesses']['boundary']
    n,t,p=witness['n'],witness['T'],F(witness['p'])
    d,md=mask_kernel(n)
    state=tuple(witness['initial'])
    probability=F(1)
    aligned=False
    for phase,(i,x,y,k,new) in enumerate(witness['path']):
        assert i==phase and state[i]==x
        state=literal_replace(state,n,t,i,y,k)
        assert state==tuple(new)
        aligned|=state==tuple(range(n+1))
        probability*=F(d[x][y],md)*((1-p)*int(y==k)+p*F(d[y][k],md))
    assert aligned and state!=tuple(range(n+1)) and state==tuple(witness['final'])
    assert probability==F(witness['probability'])>0
    assert posterior_witness()==saved['witnesses']['acceptance_bias']
    small=next(r for r in cells if (r['n'],r['T'],r['p'])==('3','2','1/192'))
    large=next(r for r in cells if (r['n'],r['T'],r['p'])==('3','3','1/192'))
    gap=saved['witnesses']['expected_monotonicity']
    assert F(gap['larger_minus_smaller_sweeps_lower'])==F(large['simultaneous_lower'])-F(small['simultaneous_upper'])>0
    assert F(gap['larger_minus_smaller_sweeps_upper'])==F(large['simultaneous_upper'])-F(small['simultaneous_lower'])
    return dict(status='pass',arithmetic='exact; no NumPy or numerical solver',counts=counts,
                witnesses=3,scientific_trajectories=0)


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--bundle',type=Path,default=Path(__file__).resolve().parent)
    print(json.dumps(verify(p.parse_args().bundle),sort_keys=True))
