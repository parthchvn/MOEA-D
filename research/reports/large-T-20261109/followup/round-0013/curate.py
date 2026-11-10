#!/usr/bin/env python3
"""Validate exact computations and write compact, deterministic evidence."""
import argparse
import csv
from fractions import Fraction as F
import hashlib
import json
from pathlib import Path
import sys


KEYS = ('mean0', 'first', 'second', 'cubic', 'cubic_12', 'cubic_21', 'cubic_30')


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def table(path):
    with path.open() as file:
        return list(csv.DictReader(file))


def write_csv(path, rows):
    with path.open('w', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def compact(row, keys):
    result = {k: row[k] for k in ('n', 'T') if k in row}
    for key in keys:
        value = row[key]
        result[key+'_decimal'] = float(F(value))
        result[key+'_sha256'] = hashlib.sha256(value.encode()).hexdigest()
    # Full exact cubic for the independently checked cells; much larger
    # n=5,6 fractions are reproducible from code and certified by hashes.
    result['cubic_rational'] = row['cubic'] if int(row['n']) <= 4 else ''
    result['arithmetic'] = 'exact rational'
    return result


def main(repo, work, out):
    out.mkdir(parents=True, exist_ok=True)
    prior = repo/'research/reports/large-T-20261109/followup'
    prior11 = prior/'round-0011'
    files11 = ('dependency.json', 'inequalities.csv', 'schur.csv', 'moments.csv', 'bounds.csv', 'verification.json')
    equal11 = {name: (work/'prior'/name).read_bytes() == (prior11/name).read_bytes() for name in files11}
    assert all(equal11.values())
    prior12 = prior/'round-0012'
    files12 = ('phase.csv', 'pair.csv', 'tensor.csv', 'moments.csv')
    equal12 = {name: (work/'round12'/name).read_bytes() == (prior12/name).read_bytes() for name in files12}
    assert all(equal12.values())
    meta12 = json.loads((prior12/'provenance.json').read_text())
    hashes12 = {name: sha(prior12/name) == digest for name, digest in meta12['artifacts_sha256'].items()}
    assert all(hashes12.values())
    dependency = json.loads((work/'prior/dependency.json').read_text())
    dependency.update(method='Complete round-11 recursive replay, plus round-12 phase/pair/tensor-row/moment replay and all published artifact hashes.',
                      round11_outputs_byte_identical=equal11,
                      round12_outputs_byte_identical=equal12,
                      round12_artifact_hashes_verified=hashes12,
                      round12_not_repeated='The large positive-p full Schur solve is not used by the cubic proof or coefficient oracle; only its published artifact hash is checked.',
                      proof_dependencies='Clean coefficient identity and recipient geometry rederived; orphan identity rechecked by a separate stopped-occupancy recursion. No old forest theorem or unpublished appendix assumed.')
    (out/'dependency.json').write_text(json.dumps(dependency, indent=2, sort_keys=True)+'\n')
    rows = table(work/'exact/coefficients.csv')
    indexed = {(int(r['n']), int(r['T'])): r for r in rows}
    assert set(indexed) == {(n, t) for n in (3, 4, 5, 6) for t in (2, 3)}
    reference = json.loads((work/'oracle.json').read_text())
    comparisons = 0
    for r in reference['full_state_results']:
        new = indexed[int(r['n']), int(r['T'])]
        for key in KEYS:
            assert F(r[key]) == F(new[key]), (r['n'], r['T'], key)
            comparisons += 1
    old_count = 0
    for r in table(prior/'round-0008/coefficients.csv'):
        new = indexed[int(r['n']), int(r['T'])]
        for key in ('mean0', 'first', 'second', 'between', 'within'):
            assert F(r[key]) == F(new[key])
            old_count += 1
    gaps = table(work/'exact/gaps.csv')
    for row in gaps:
        n = int(row['n'])
        a, b = indexed[n, 2], indexed[n, 3]
        for key in ('first', 'second', 'cubic', 'cubic_12', 'cubic_21', 'cubic_30'):
            assert F(row[key]) == F(b[key])-F(a[key])
        assert F(row['cubic']) == sum(F(row[k]) for k in ('cubic_12', 'cubic_21', 'cubic_30'))
        assert abs(F(row['cubic'])) <= 10**10*n**7
    word_rows = table(work/'words/words.csv')
    for n in (4, 6):
        subset = [r for r in word_rows if int(r['n']) == n]
        assert len(subset) == 8
        # Word solver asserts exact sum before writing compact rows.
        if n == 4:
            assert sum(F(r['coefficient']) for r in subset) == F(indexed[n, 2]['cubic'])
        q = 1/F(indexed[n, 2]['mean0'])
        Z = F((n+1)**3*(20*n+1)**3, 1)/q
        for r in subset:
            if r['coefficient']:
                v = F(r['coefficient'])
                assert abs(v) <= (32/q**4 if r['word'] == 'OOO' else 10000*Z)
    write_csv(out/'coefficients.csv', [compact(r, KEYS) for r in rows])
    write_csv(out/'gaps.csv', [compact(r, ('first', 'second', 'cubic', 'cubic_12', 'cubic_21', 'cubic_30')) for r in gaps])
    for name in ('words.csv', 'excess.csv', 'cancellation.csv'):
        (out/name).write_bytes((work/'words'/name).read_bytes())
    # The independent oracle itself is small enough to retain all fractions.
    (out/'oracle.json').write_bytes((work/'oracle.json').read_bytes())
    excess = table(out/'excess.csv')
    witnesses = table(out/'cancellation.csv')
    assert all(r['exact_identities'] == 'True' and r['exact_bounds'] == 'True' for r in excess)
    checks = dict(status='mechanically checked; general bound remains a candidate proof',
                  arithmetic='exact rational; decimal displays rounded',
                  exact_cells=len(rows), exact_gap_sizes=[3, 4, 5, 6],
                  independent_full_population_cases=sum(r['states'] for r in reference['full_state_results']),
                  independent_rational_comparisons=comparisons,
                  published_lower_order_comparisons=old_count,
                  maximum_error_counts={k: max(int(r[k]) for r in rows) for k in
                    ('maximum_clean_errors', 'maximum_first_errors', 'maximum_second_errors')},
                  word_coefficients=len(word_rows), word_sum_checks=2,
                  excess_states=len(excess), exact_excess_identities=3*len(excess),
                  excess_inequality_checks=sum(4+int(int(r['orphan']) != int(r['n'])) for r in excess),
                  cancellation_witnesses=len(witnesses),
                  scientific_trajectories=0, scientific_seeds=[],
                  censoring='Not applicable to deterministic algebra; inherited empirical censoring is retained in dependency.json.',
                  candidate_bound='abs(C_n)<=10^10 n^7; not independently audited',
                  full_process_remainder='unresolved; no enlarged noise window',
                  source_files={str(p.relative_to(repo)): sha(p) for p in
                    (prior/'round-0008/second.py', prior/'round-0008/oracle.py', prior12/'audit.py')})
    (out/'verification.json').write_text(json.dumps(checks, indent=2, sort_keys=True)+'\n')
    print(json.dumps(checks, sort_keys=True))


if __name__ == '__main__':
    sys.set_int_max_str_digits(0)
    csv.field_size_limit(sys.maxsize)
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--repo', type=Path, default=Path('.'))
    parser.add_argument('--work', type=Path, required=True)
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    main(args.repo.resolve(), args.work.resolve(), args.out.resolve())
