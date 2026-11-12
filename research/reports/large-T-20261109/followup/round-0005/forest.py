#!/usr/bin/env python3
"""Bounded multi-sweep adversarial search of the tagged error-family construction.

No probabilities are sampled. Exhausts all fresh outcomes at every retained
forest state; states over the declared particle cap are checked but not expanded.
Canonical particles carry (site, weight, tagged). Family genealogy is irrelevant
to this tag-invariant test; independence is proved in audit.md, not inferred here.
"""
import argparse
from collections import Counter
from itertools import product
import json
from pathlib import Path
from audit import literal_replace, recipients


def advance(weights, forest, n, t, breeder, draws):
    # Sources are base (-1), followed by every OLD particle at this breeder.
    old = [i for i,(site,w,tag) in enumerate(forest) if site == breeder]
    sources = [-1]+old
    assert len(draws) == len(sources)
    selected = next((i for i in old if forest[i][2]), -1)
    proposals = dict(zip(sources,draws))
    child,obs = proposals[selected]
    actual = literal_replace(weights,n,t,breeder,child,obs)
    updated = [list(p) for p in forest]
    selected_child = None
    for source in sources:
        j,k = proposals[source]
        if source != -1 and k == breeder:
            updated[source] = None if j == breeder else [breeder,j,False]
        if k in recipients(n,t,breeder) and j != k:
            if source != -1 and k == breeder:
                created = source
            else:
                created = len(updated)
                updated.append([k,j,False])
            if source == selected:
                selected_child = created
    if obs in recipients(n,t,breeder):
        for part in updated:
            if part is not None and part[0] == obs:
                part[2] = False
        if child != obs:
            assert selected_child is not None
            updated[selected_child][2] = True
    # A wrong selected breeder whose proposal did NOT replace itself retains
    # its old tag, unless the target of that proposal is the breeder itself.
    # Nonselected particles' preexisting tags cannot occur at this breeder.
    result = tuple(sorted(tuple(p) for p in updated if p is not None))
    tagged = {k:w for k,w,tag in result if tag}
    assert sum(tag for k,w,tag in result) == len(tagged)
    assert all(w != k for k,w,tag in result)
    assert tagged == {k:w for k,w in enumerate(actual) if w != k}
    return actual,result


def search(sweeps=3,cap=2):
    n = 2
    summaries=[]
    for t in (1,2,3):
        for initial in ((2,1,2),(0,1,2)):
            root=tuple((k,w,True) for k,w in enumerate(initial) if k!=w)
            frontier={(initial,root)}
            counts=Counter()
            sizes=[]
            for step in range((n+1)*sweeps):
                breeder=step%(n+1)
                new=set()
                for weights,forest in sorted(frontier):
                    source_count=1+sum(k==breeder for k,w,tag in forest)
                    for draws in product(tuple(product(range(n+1),repeat=2)),repeat=source_count):
                        state=advance(weights,forest,n,t,breeder,draws)
                        counts['transitions']+=1
                        if len(state[1])<=cap:
                            new.add(state)
                        else:
                            counts['over_cap_not_expanded']+=1
                frontier=new
                sizes.append(len(frontier))
            summaries.append(dict(n=n,T=t,initial=initial,sweeps=sweeps,particle_cap=cap,
                frontier_sizes=sizes,**counts))
    return dict(status='all checked transitions preserve exact tag correspondence',
                scientific_trajectories=0,searches=summaries,
                transitions=sum(r['transitions'] for r in summaries),
                limitation='Over-cap transitions validated but not expanded. This finite search is not the unbounded coupling proof.')


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--out',type=Path,required=True)
    args=p.parse_args()
    result=search()
    args.out.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
    print(json.dumps(result,sort_keys=True))
