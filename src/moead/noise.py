"""Expanded noise experiments using the unchanged cyclic simulator.

Keep p=alpha/n and fixed-p experiments separate. All cells at a given n
share an administrative cap. Never discard censored observations.
"""
import argparse
from concurrent.futures import ProcessPoolExecutor
import csv
from datetime import datetime, timezone
import importlib.metadata
import json
import math
from pathlib import Path
import platform
import subprocess
import time

import numpy as np

from . import Config, simulate
from .experiments import digest, source_manifest, trial_seed
from .statistics import bootstrap_mean_interval, wilson_interval

RULES = {'self': lambda n: 0, 'local': lambda n: 1,
         'log': lambda n: min(n, math.ceil(math.log(n))), 'global': lambda n: n}


def cells(protocol: dict) -> list[dict]:
    """Validate and expand a versioned protocol; no rounding in cell IDs."""
    required = {'schema_version', 'master_seed', 'replicates', 'budget_sweep_factor', 'families'}
    if set(protocol) != required or protocol['schema_version'] != 1:
        raise ValueError('invalid noise protocol fields/version')
    Config(1, 0, seed=protocol['master_seed'])
    reps, factor = protocol['replicates'], protocol['budget_sweep_factor']
    if isinstance(reps, bool) or not isinstance(reps, int) or reps < 2:
        raise ValueError('need at least two replicates')
    if isinstance(factor, bool) or not isinstance(factor, (int, float)) or not math.isfinite(factor) or factor <= 0:
        raise ValueError('budget factor must be finite and positive')
    if not isinstance(protocol['families'], list) or not protocol['families']:
        raise ValueError('need nonempty families')
    result, seen = [], set()
    for family in protocol['families']:
        if set(family) != {'kind', 'n_values', 'noise_values', 'radius_rules'}:
            raise ValueError('invalid family fields')
        kind = family['kind']
        if kind not in {'scaled', 'fixed'}:
            raise ValueError('kind must be scaled or fixed')
        for key in ('n_values', 'noise_values', 'radius_rules'):
            if not family[key] or len(family[key]) != len(set(family[key])):
                raise ValueError('empty or duplicate family entries')
        for n in family['n_values']:
            Config(n, 0)
            for value in family['noise_values']:
                if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value) or value < 0:
                    raise ValueError('invalid noise value')
                p = float(value) / n if kind == 'scaled' else float(value)
                for rule in family['radius_rules']:
                    if rule not in RULES:
                        raise ValueError('unknown radius rule')
                    radius = RULES[rule](n)
                    Config(n, radius, p)
                    # Families use independent streams, including their p=0 controls.
                    cid = f'{kind}-n{n}-r{radius}-v{float(value).hex()}'
                    if cid in seen:
                        raise ValueError('duplicate actual cell within a family')
                    seen.add(cid)
                    budget = (n + 1) * (1 + math.ceil(factor * n * math.log(n + 2)))
                    result.append(dict(config_id=cid, family=kind, n=n, radius=radius,
                                       policy=rule, noise_value=float(value), p=p, budget=budget))
    return sorted(result, key=lambda c: (c['family'], c['n'], c['noise_value'], c['radius']))


def run_cell(task):
    cell, master, replicates, engine = task
    rows = []
    n = cell['n']
    for repetition in range(replicates):
        seed = trial_seed(master, cell['config_id'], repetition)
        result = simulate(Config(n, cell['radius'], cell['p'], seed, cell['budget']), engine)
        incorrect = int(np.count_nonzero(result.weights != np.arange(n + 1)))
        stored_optimal = int(np.count_nonzero(result.observed == np.arange(n + 1)))
        if result.completed != (incorrect == 0):
            raise AssertionError('incorrect completion flag')
        rows.append(dict(cell, repetition=repetition, seed=seed, evaluations=int(result.evaluations),
                         event=int(result.completed), front_hit=int(result.front_hit),
                         stored_hit=int(result.stored_hit), comparisons=int(result.comparisons),
                         final_incorrect=incorrect, final_stored_optimal=stored_optimal,
                         certificate_checks=int(result.certificate_checks),
                         certificate_violations=int(result.certificate_violations), engine=result.engine))
    return rows


def write_csv(path: Path, rows: list[dict]):
    with path.open('w', newline='', encoding='utf-8') as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def run(protocol_path: Path, out: Path, engine='numba', workers=1):
    protocol = json.loads(protocol_path.read_text())
    grid = cells(protocol)
    if isinstance(workers, bool) or not isinstance(workers, int) or workers < 1:
        raise ValueError('workers must be a positive integer')
    if out.exists() and any(out.iterdir()):
        raise FileExistsError('use a new output directory')
    out.mkdir(parents=True, exist_ok=True)
    (out / 'config.json').write_text(json.dumps(protocol, sort_keys=True, indent=2) + '\n')
    tasks = [(cell, protocol['master_seed'], protocol['replicates'], engine) for cell in grid]
    start = time.perf_counter()
    pool = ProcessPoolExecutor(max_workers=workers) if workers > 1 else None
    iterator = pool.map(run_cell, tasks) if pool else map(run_cell, tasks)
    rows = []
    try:
        with (out / 'runs.csv').open('w', newline='', encoding='utf-8') as handle:
            writer = None
            for batch in iterator:
                if writer is None:
                    writer = csv.DictWriter(handle, fieldnames=list(batch[0]))
                    writer.writeheader()
                writer.writerows(batch)
                handle.flush()
                rows.extend(batch)
                print(batch[0]['config_id'], sum(x['event'] for x in batch), '/', len(batch), flush=True)
    finally:
        if pool:
            pool.shutdown()
    root = Path(__file__).resolve().parents[2]
    try:
        commit = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=root, text=True, stderr=subprocess.DEVNULL).strip()
        dirty = bool(subprocess.check_output(['git', 'status', '--porcelain', '--', 'src', 'tests', 'experiments'], cwd=root, text=True).strip())
    except (OSError, subprocess.CalledProcessError):
        commit, dirty = None, None
    versions = {}
    for name in ['numpy', 'numba', 'matplotlib', 'pytest']:
        try:
            versions[name] = importlib.metadata.version(name)
        except importlib.metadata.PackageNotFoundError:
            versions[name] = None
    manifest = dict(schema_version=1, created_utc=datetime.now(timezone.utc).isoformat(),
                    source_commit=commit, source_tree_dirty=dirty, source_sha256=source_manifest(),
                    python=platform.python_version(), platform=platform.platform(), dependencies=versions,
                    rng='numpy.PCG64', seed_derivation='SHA256(master|config_id|repetition), first 8 bytes, big endian',
                    trials=len(rows), completed=sum(row['event'] for row in rows),
                    censored=sum(1-row['event'] for row in rows), elapsed_seconds=time.perf_counter()-start,
                    data_sha256={name: digest(out / name) for name in ['runs.csv', 'config.json']})
    (out / 'manifest.json').write_text(json.dumps(manifest, sort_keys=True, indent=2) + '\n')
    return manifest


def load(out: Path) -> list[dict]:
    manifest = json.loads((out / 'manifest.json').read_text())
    if set(manifest['data_sha256']) != {'runs.csv', 'config.json'}:
        raise ValueError('missing or unexpected data paths')
    for name, expected in manifest['data_sha256'].items():
        if digest(out / name) != expected:
            raise ValueError('invalid data hash')
    with (out / 'runs.csv').open(newline='') as handle:
        rows = list(csv.DictReader(handle))
    ints = ['n', 'radius', 'budget', 'repetition', 'seed', 'evaluations', 'event', 'front_hit',
            'stored_hit', 'comparisons', 'final_incorrect', 'final_stored_optimal',
            'certificate_checks', 'certificate_violations']
    for row in rows:
        for key in ints:
            row[key] = int(row[key])
        for key in ['noise_value', 'p']:
            row[key] = float(row[key])
    protocol = json.loads((out / 'config.json').read_text())
    expected = {(c['config_id'], rep): c for c in cells(protocol) for rep in range(protocol['replicates'])}
    seen = set()
    for row in rows:
        key = row['config_id'], row['repetition']
        if key in seen or key not in expected:
            raise ValueError('duplicate or unexpected trial')
        seen.add(key)
        if any(row[k] != v for k, v in expected[key].items()):
            raise ValueError('trial configuration differs from protocol')
        if row['seed'] != trial_seed(protocol['master_seed'], *key):
            raise ValueError('seed mismatch')
        if row['event'] not in (0, 1) or not row['n']+1 <= row['evaluations'] <= row['budget']:
            raise ValueError('invalid event/accounting')
        if not row['event'] and row['evaluations'] != row['budget']:
            raise ValueError('censored time must equal administrative cap')
        if bool(row['event']) != (row['final_incorrect'] == 0):
            raise ValueError('event disagrees with final exact assignment')
        if not 0 <= row['final_incorrect'] <= row['n']+1 or not 0 <= row['final_stored_optimal'] <= row['n']+1:
            raise ValueError('invalid state counts')
        for hit in ('stored_hit', 'front_hit'):
            if row[hit] != -1 and not row['n']+1 <= row[hit] <= row['evaluations']:
                raise ValueError('invalid recorded hitting time')
        if row['certificate_violations']:
            raise ValueError('noiseless certificate failed')
    if seen != set(expected) or len(rows) != manifest['trials']:
        raise ValueError('incomplete protocol')
    if sum(r['event'] for r in rows) != manifest['completed'] or sum(1-r['event'] for r in rows) != manifest['censored']:
        raise ValueError('manifest event totals mismatch')
    return rows


def summarize(rows: list[dict]) -> list[dict]:
    groups = {}
    for row in rows:
        groups.setdefault(row['config_id'], []).append(row)
    output = []
    for cid, group in sorted(groups.items()):
        a = group[0]
        if len({r['budget'] for r in group}) != 1:
            raise ValueError('mixed censoring horizons')
        values = [r['evaluations'] for r in group]
        lo, hi = bootstrap_mean_interval(values, trial_seed(0, cid, 0))
        complete = sum(r['event'] for r in group)
        wl, wh = wilson_interval(complete, len(group))
        censored = [r for r in group if not r['event']]
        row = {k: a[k] for k in ['config_id', 'family', 'n', 'radius', 'policy', 'noise_value', 'p', 'budget']}
        row.update(trials=len(group), completed=complete, censored=len(censored),
                   completion_rate=complete/len(group), completion_ci_low=wl, completion_ci_high=wh,
                   mean_capped_evaluations=float(np.mean(values)), mean_ci_low=lo, mean_ci_high=hi,
                   stored_hit_observed=sum(r['stored_hit'] >= 0 for r in group),
                   front_hit_observed=sum(r['front_hit'] >= 0 for r in group),
                   stored_hit_but_exact_censored=sum(r['stored_hit'] >= 0 for r in censored),
                   mean_terminal_incorrect_censored=float(np.mean([r['final_incorrect'] for r in censored])) if censored else '',
                   mean_comparisons=float(np.mean([r['comparisons'] for r in group])))
        output.append(row)
    return output


def verify(out: Path, check_source=False):
    rows = load(out)
    with (out / 'summary.csv').open(newline='') as handle:
        summary = list(csv.DictReader(handle))
    regenerated = [{k: str(v) for k, v in r.items()} for r in summarize(rows)]
    if summary != regenerated:
        raise ValueError('summary differs from raw trials')
    checked = set()
    for line in (out / 'checksums.sha256').read_text().splitlines():
        expected, name = line.split('  ', 1)
        path = (out / name).resolve()
        if not path.is_relative_to(out.resolve()) or digest(path) != expected:
            raise ValueError('artifact checksum/path mismatch')
        checked.add(name)
    if not {'config.json', 'runs.csv', 'manifest.json', 'summary.csv', 'README.md'} <= checked:
        raise ValueError('incomplete artifact checksum inventory')
    if check_source:
        root = Path(__file__).resolve().parents[2]
        for name, expected in json.loads((out / 'manifest.json').read_text())['source_sha256'].items():
            path = (root / name).resolve()
            if not path.is_relative_to(root) or digest(path) != expected:
                raise ValueError(f'generating source changed: {name}')
    return dict(trials=len(rows), completed=sum(r['event'] for r in rows), censored=sum(1-r['event'] for r in rows))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--config', type=Path)
    parser.add_argument('--out', type=Path, required=True)
    parser.add_argument('--engine', choices=['python', 'numba'], default='numba')
    parser.add_argument('--workers', type=int, default=1)
    parser.add_argument('--verify', action='store_true')
    parser.add_argument('--check-source', action='store_true')
    args = parser.parse_args()
    if not args.verify and args.config is None:
        parser.error('--config is required when running experiments')
    result = verify(args.out, args.check_source) if args.verify else run(args.config, args.out, args.engine, args.workers)
    print(json.dumps({k: result[k] for k in ['trials', 'completed', 'censored']}, indent=2))


if __name__ == '__main__':
    main()
