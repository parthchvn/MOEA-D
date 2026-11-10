#!/usr/bin/env python3
"""Independent phase oracle, published lower-order checks, compact curation."""
import argparse
import csv
from fractions import Fraction as F
import hashlib
import importlib.util
from itertools import product
import json
from pathlib import Path
import sys

sys.set_int_max_str_digits(0)
csv.field_size_limit(sys.maxsize)
KEYS = ('mean0', 'first', 'second', 'cubic', 'fourth',
        'fourth_13', 'fourth_22', 'fourth_31', 'fourth_40')


def load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def digest(value):
    return hashlib.sha256(str(value).encode()).hexdigest()


def read(path):
    with path.open() as file:
        return list(csv.DictReader(file))


def write(path, rows):
    with path.open('w', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def compact(row):
    result = {key: row[key] for key in ('n', 'T') if key in row}
    for key in KEYS:
        if key not in row:
            continue
        value = F(row[key])
        result[key+'_decimal'] = float(value)
        result[key+'_sha256'] = digest(value)
    result['arithmetic'] = 'exact rational; decimal display rounded'
    return result


def main(repo, inputs, out):
    out.mkdir(parents=True, exist_ok=True)
    prior = repo/'research/reports/large-T-20261109/followup'
    phase = load(prior/'round-0014/audit.py', 'independent_phase')
    reference = {(int(r['n']), int(r['T'])): r
                 for r in read(prior/'round-0013/coefficients.csv')}
    rows = [r for path in inputs for r in read(path/'coefficients.csv')]
    indexed = {(int(r['n']), int(r['T'])): r for r in rows}
    assert len(indexed) == len(rows)
    assert {(3, 2), (3, 3), (4, 2), (4, 3)} <= set(indexed)
    lower_checks, oracle_checks = 0, 0
    oracle_rows = []
    for (n, t), row in sorted(indexed.items()):
        for key in ('mean0', 'first', 'second', 'cubic'):
            assert digest(F(row[key])) == reference[n, t][key+'_sha256'], (n, t, key)
            lower_checks += 1
        assert F(row['fourth']) == sum(F(row[f'fourth_{j}{4-j}']) for j in range(1, 5))
        if t == 3:
            assert abs(F(row['fourth'])) <= 122880000*n**9
        if n in (3, 4):
            solver = phase.Phase(n, t)
            for j, key in enumerate(('mean0', 'first', 'second', 'cubic', 'fourth')):
                value = solver.values(solver.corner, 'D'*j)[0]
                assert value == F(row[key]), (n, t, key)
                oracle_checks += 1
            oracle_rows.append(dict(n=n, T=t, fourth_decimal=float(value),
                                    fourth_sha256=digest(value), exact_match=True))
            solver.clear()
            print(json.dumps(dict(stage='oracle', n=n, T=t)), flush=True)
    word_rows = []
    solver = phase.Phase(4, 2)
    total = F(0)
    for letters in product('RO', repeat=4):
        word = ''.join(letters)
        value = solver.values(solver.corner, word)[0]
        total += value
        word_rows.append(dict(n=4, word=word, coefficient_decimal=float(value),
                              coefficient_sha256=digest(value), arithmetic='exact rational'))
        if word == 'OOOO':
            q = 1-(1-solver.d[2][0])*(1-solver.d[1][0])
            assert abs(value) <= 80/q**5
        print(json.dumps(dict(stage='word', word=word, value=float(value))), flush=True)
    assert total == F(indexed[4, 2]['fourth'])
    solver.clear()
    gaps = []
    for n in sorted({n for n, _ in indexed}):
        a, b = indexed[n, 2], indexed[n, 3]
        gap = dict(n=n)
        for key in KEYS:
            if key != 'mean0':
                gap[key] = str(F(b[key])-F(a[key]))
        gaps.append(compact(gap))
    write(out/'coefficients.csv', [compact(indexed[key]) for key in sorted(indexed)])
    write(out/'gaps.csv', gaps)
    write(out/'words.csv', word_rows)
    result = dict(status='mechanically checked', exact_cells=len(rows),
                  exact_sizes=sorted({n for n, _ in indexed}),
                  independent_phase_checks=oracle_checks,
                  published_lower_order_checks=lower_checks,
                  independent_fourth_coefficients=oracle_rows,
                  fourth_words=len(word_rows), exact_word_sum=True,
                  phase_source_sha256=hashlib.sha256((prior/'round-0014/audit.py').read_bytes()).hexdigest(),
                  scientific_trajectories=0, scientific_seeds=[],
                  uncertainty='No sampling intervals or censoring apply to exact algebra.',
                  conclusion='Full T=2 polynomial fourth coefficient remains unresolved; no extrapolation from finite sizes.')
    (out/'verification.json').write_text(json.dumps(result, indent=2, sort_keys=True)+'\n')
    print(json.dumps(result), flush=True)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--repo', type=Path, default=Path('.'))
    parser.add_argument('--inputs', type=Path, nargs='+', required=True)
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    main(args.repo.resolve(), args.inputs, args.out)
