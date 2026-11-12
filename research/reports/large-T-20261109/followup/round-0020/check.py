#!/usr/bin/env python3
"""Fresh deterministic recovery/schema/support checks; no RNG or old replay.

Run with --repo pointing at the repository. Outputs are small JSON/CSV files
beside this script by default, or in --out. Imports the hash-verified recovered
phase solver only for mutation probabilities; support enumeration is separate.
"""
import argparse
import csv
from fractions import Fraction as F
import hashlib
from itertools import combinations, product
import json
from pathlib import Path
import re
from audit import Audit


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def rows(p):
    with p.open() as f:
        return list(csv.DictReader(f))


def run(repo, out):
    base = repo / 'research/reports/large-T-20261109/followup'
    act = base / 'activation-20261112T181239Z-84cbf5'
    inventory = json.loads((act/'RECOVERY.json').read_text())
    checked = []
    for entry, folder in zip(inventory, ('round-0020-github-wip', 'round-0020-cb372b60')):
        for item in entry['files']:
            path = act/'recovery'/folder/item['path']
            assert sha(path) == item['sha256'] and path.stat().st_size == item['bytes']
            checked.append(str(path.relative_to(repo)))
    manifests = {}
    for r in (18, 19):
        p = base/f'round-{r:04d}'
        m = json.loads((p/'provenance.json').read_text())['artifacts_sha256']
        assert all(sha(p/k) == v for k, v in m.items())
        manifests[str(r)] = len(m)
    assert sha(Path(__file__).with_name('audit.py')) == inventory[0]['files'][2]['sha256']
    assert sha(Path(__file__).with_name('test_recovered.py')) == inventory[0]['files'][5]['sha256']

    p = base/'round-0019'
    schemas = {}
    expected = {
        'words.csv': {(n, 'RORR') for n in (4, 6)},
        'entrance.csv': {(n, y) for n in (4, 6) for y in range(n+1)},
        'joint.csv': {(n, o, k, x, y) for n in (4, 6) for o in ('aligned','corner')
                      for k in range(n) for x in range(n+1) for y in range(n)},
        'responses.csv': {(n, o, k, x, i) for n in (4, 6) for o in ('aligned','corner')
                          for k in range(n) for x in range(n+1) for i in range(n+1)},
        'branches.csv': {(n, s, i) for n in (4, 6)
                         for s in (' '.join(map(str, range(n+1))),
                                   ' '.join(map(str, (2, *range(1,n+1)))))
                         for i in range(n+1)},
        'shortcuts.csv': {(4,), (6,)}
    }
    keys = {'words.csv': ('n','word'), 'entrance.csv': ('n','y'),
            'joint.csv': ('n','origin','target','child','orphan'),
            'responses.csv': ('n','origin','target','child','phase'),
            'branches.csv': ('n','state','phase'), 'shortcuts.csv': ('n',)}
    kernels = {n: Audit(n) for n in (4, 6)}
    rational_product_checks = 0
    for file, want in expected.items():
        data = rows(p/file)
        got = [tuple(int(r[k]) if k in ('n','target','child','orphan','phase','y') else r[k]
                     for k in keys[file]) for r in data]
        assert len(set(got)) == len(got) and set(got) == want
        for r in data:
            assert None not in r and all(v is not None and v != '' for v in r.values())
            for k, v in r.items():
                if k.endswith('sha256'):
                    assert re.fullmatch('[0-9a-f]{64}', v)
            n = int(r['n']); d = kernels[n].d
            if file == 'joint.csv':
                k,x,y = (int(r[z]) for z in ('target','child','orphan'))
                a,dy,mut = d[x][k], d[y][n], d[n][y]
                assert [F(r[z]) for z in ('regular_acceptance','orphan_acceptance','orphan_mutation','joint_weight')] == [a,dy,mut,a*dy*mut]
                rational_product_checks += 1
            if file == 'entrance.csv':
                y = int(r['y']); assert F(r['acceptance']) == d[y][n]
                assert F(r['entrance']) == (d[n][y]*d[y][n] if y<n else 0)
                rational_product_checks += 1
            if file == 'responses.csv':
                assert F(r['acceptance']) == d[int(r['child'])][int(r['target'])]
                rational_product_checks += 1
            if file == 'words.csv':
                assert r['arithmetic'] == 'exact rational'
                assert r['independent_phase_match'] == 'True'
                assert F(r['polynomial_bound']) == 1024*(n+1)**3*(20*n)**4/kernels[n].q
        schemas[file] = {'rows':len(data), 'keys_unique_and_complete':True, 'sha256':sha(p/file)}
    v = json.loads((p/'verification.json').read_text())
    assert v['ns'] == [4,6] and v['scientific_trajectories'] == 0 and v['scientific_seeds'] == []
    assert v['joint_entrance_cases'] == schemas['joint.csv']['rows'] == 664
    assert v['marked_phase_cases'] == schemas['responses.csv']['rows'] == 788

    geometry = []
    # Enumerate generic overwrites on either the original corner or alignment.
    # Correct and original slot-zero=2 values have zero budget. Deduplicate.
    for n in (4,6,8):
        states = set()
        for initial in (tuple(range(n)), (2,*range(1,n))):
            for count in range(4):
                for places in combinations(range(n), count):
                    for values in product(range(n+1), repeat=count):
                        s = list(initial)
                        for k,x in zip(places,values): s[k] = x
                        states.add(tuple(s))
        slow_count = 0
        for s in states:
            budget = sum(x != k and not (k == 0 and x == 2) for k,x in enumerate(s))
            bad = [k for k in range(0,n,2) if s[k]!=k and s[k+1]!=k+1 and not(k==0 and s[0]==2)]
            assert budget <= 3 and len(bad) <= 1
            assert sum(x!=k for k,x in enumerate(s)) <= 4
            slow_count += bool(bad)
        marked_cases = partner_checks = 0
        for initial in (tuple(range(n)), (2,*range(1,n))):
            for k,x in product(range(n),range(n+1)):
                s = list(initial); s[k]=x
                errors = [j for j in range(n) if s[j]!=j]
                for repairs in product((False,True), repeat=len(errors)):
                    child = s.copy()
                    for j,repair in zip(errors,repairs):
                        if repair: child[j]=j
                    marked_cases += 1
                    assert not any(child[l]!=l and child[l+1]!=l+1 and not(l==0 and child[0]==2) for l in range(0,n,2))
                    for target,z in product(range(n),range(n+1)):
                        successor = child.copy(); successor[target]=z
                        for left in range(0,n,2):
                            if successor[left]!=left and successor[left+1]!=left+1 and not(left==0 and successor[0]==2):
                                assert child[k]==x and x!=k and target==(k^1)
                                assert successor[k]==x and successor[target]==z
                                partner_checks += 1
        geometry.append(dict(n=n,budget3_unique_regular_states=len(states),states_with_one_slow_pair=slow_count,
                             marked_descendant_cases=marked_cases,second_birth_slow_pair_cases=partner_checks))
    witness = (3,0,0,0,4)
    assert sum(witness[k]!=k and not(k==0 and witness[0]==2) for k in range(4)) == 4
    assert all(witness[k]!=k and witness[k+1]!=k+1 for k in (0,2))
    result = dict(status='mechanically checked', recovery_file_hashes_checked=len(checked),
        published_manifest_counts=manifests,published_schemas=schemas,
        rational_entrance_or_mark_fields_checked=rational_product_checks,
        geometry=geometry,first_excluded_budget4_state=list(witness),
        reused_scope='Published n=4,6 exact outputs after manifest/schema checks; saved hashes alone do not re-certify their arithmetic.',
        new_scope='Support enumeration n=4,6,8 through three generic overwrites; all first marks and their clean subsets, all second overwrites. No general-population response grid.',
        scientific_trajectories=0,scientific_seeds=[])
    out.mkdir(parents=True,exist_ok=True)
    (out/'targeted.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
    return result

if __name__ == '__main__':
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--repo',type=Path,required=True)
    ap.add_argument('--out',type=Path,default=Path(__file__).resolve().parent)
    a=ap.parse_args()
    print(json.dumps(run(a.repo.resolve(),a.out)))
