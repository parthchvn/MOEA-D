"""Deterministic, versioned experiment runner. No censored trial is dropped."""

import argparse
import csv
from datetime import datetime, timezone
import hashlib
import importlib.metadata
import json
import math
from pathlib import Path
import platform
import subprocess
import time

import numpy as np

from . import Config, simulate
from .frontier import simulate_frontier


FIELDS = [
    'config_id', 'algorithm', 'n', 'radius', 'nominal_width',
    'max_neighborhood_size', 'endpoint_neighborhood_size', 'alpha', 'p',
    'policies', 'repetition', 'seed', 'budget', 'evaluations', 'event',
    'initial_evaluations', 'front_hit_evaluations', 'stored_hit_evaluations',
    'comparisons', 'certificate_checks', 'certificate_violations', 'engine',
    'initial_weight', 'conditional_expected_evaluations',
]


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def trial_seed(master: int, config_id: str, repetition: int) -> int:
    key = f'{master}|{config_id}|{repetition}'.encode('utf-8')
    return int.from_bytes(hashlib.sha256(key).digest()[:8], 'big')


def load_protocol(path: Path) -> dict:
    protocol = json.loads(path.read_text())
    allowed = {'schema_version', 'master_seed', 'n_values', 'replicates',
               'alpha_values', 'radius_rules', 'extra_radius_sweep',
               'diagnostic_cases', 'frontier_baseline', 'budget_sweep_factor'}
    if set(protocol) - allowed or protocol.get('schema_version') != 1:
        raise ValueError('unsupported experiment protocol or unknown fields')
    Config(1, 0, seed=protocol['master_seed'])
    if (isinstance(protocol['replicates'], bool) or not isinstance(protocol['replicates'], int)
            or protocol['replicates'] < 2 or not math.isfinite(protocol['budget_sweep_factor'])
            or protocol['budget_sweep_factor'] <= 0):
        raise ValueError('need at least two replicates and a positive budget factor')
    if len(set(protocol['n_values'])) != len(protocol['n_values']):
        raise ValueError('duplicate n values')
    if len(set(protocol['alpha_values'])) != len(protocol['alpha_values']):
        raise ValueError('duplicate noise strengths')
    if len(set(protocol['radius_rules'])) != len(protocol['radius_rules']):
        raise ValueError('duplicate radius rules')
    for n in protocol['n_values']:
        for alpha in protocol['alpha_values']:
            if alpha < 0:
                raise ValueError('alpha must be nonnegative')
            Config(n, 0, alpha / n)
    return protocol


def configurations(protocol: dict) -> list[dict]:
    cells = {}

    def add(n, r, alpha, policy, algorithm='cyclic'):
        Config(n, r, alpha / n)
        cid = f'{algorithm}-n{n}-r{r}-a{alpha:g}'
        if cid in cells and cells[cid]['alpha'] != alpha:
            raise ValueError('distinct noise strengths collide in the configuration identifier')
        if cid not in cells:
            cells[cid] = dict(config_id=cid, algorithm=algorithm, n=n,
                              radius=r, alpha=alpha, policies=[])
        if policy not in cells[cid]['policies']:
            cells[cid]['policies'].append(policy)

    rules = {'self': lambda n: 0, 'local': lambda n: 1,
             'log': lambda n: min(n, math.ceil(math.log(n))),
             'sqrt': lambda n: math.isqrt(n), 'global': lambda n: n}
    for n in protocol['n_values']:
        for rule in protocol['radius_rules']:
            if rule not in rules:
                raise ValueError(f'unknown radius rule: {rule}')
            for alpha in protocol['alpha_values']:
                add(n, rules[rule](n), alpha, rule)
        if protocol.get('frontier_baseline', False):
            add(n, 1, 0.0, 'frontier', 'frontier')
    extra = protocol.get('extra_radius_sweep', {})
    for r in extra.get('radii', []):
        for alpha in protocol['alpha_values']:
            add(extra['n'], r, alpha, 'radius-scan')
    return sorted(cells.values(), key=lambda c: (c['algorithm'], c['n'], c['alpha'], c['radius']))


def source_manifest() -> dict:
    root = Path(__file__).resolve().parents[2]
    paths = sorted((root / 'src').rglob('*.py')) + sorted((root / 'tests').rglob('*.py'))
    for name in ['pyproject.toml', 'requirements-evidence.txt']:
        if (root / name).is_file():
            paths.append(root / name)
    return {str(path.relative_to(root)): digest(path) for path in paths}


def run_experiments(protocol_path: Path, out: Path, engine='auto', overwrite=False) -> dict:
    protocol = load_protocol(protocol_path)
    if out.exists() and any(out.iterdir()) and not overwrite:
        raise FileExistsError(f'{out} is not empty; choose another directory or --overwrite')
    out.mkdir(parents=True, exist_ok=True)
    # Overwrite only generated filenames; unrelated files are never deleted.
    (out / 'config.json').write_text(json.dumps(protocol, indent=2, sort_keys=True) + '\n')
    started = time.perf_counter()
    total = completions = 0
    diagnostic_cases = {tuple(case) for case in protocol.get('diagnostic_cases', [])}
    with (out / 'runs.csv').open('w', newline='') as raw, (out / 'diagnostics.jsonl').open('w') as diag:
        writer = csv.DictWriter(raw, fieldnames=FIELDS)
        writer.writeheader()
        for cell in configurations(protocol):
            n, radius, alpha = cell['n'], cell['radius'], cell['alpha']
            cap_sweeps = math.ceil(protocol['budget_sweep_factor'] * n * math.log(n + 2))
            budget = (n + 1) * (1 + cap_sweeps)
            for repetition in range(protocol['replicates']):
                seed = trial_seed(protocol['master_seed'], cell['config_id'], repetition)
                track = alpha == 0 and (n, radius) in diagnostic_cases and cell['algorithm'] == 'cyclic'
                config = Config(n, radius, alpha / n, seed, budget, track)
                row = {key: cell[key] for key in ('config_id', 'algorithm', 'n', 'radius', 'alpha')}
                row.update(nominal_width=config.nominal_width,
                           max_neighborhood_size=config.max_neighborhood_size,
                           endpoint_neighborhood_size=radius + 1,
                           p=alpha / n, policies='|'.join(cell['policies']),
                           repetition=repetition, seed=seed, budget=budget)
                if cell['algorithm'] == 'cyclic':
                    result = simulate(config, engine)
                    if result.completed and not np.array_equal(result.weights, np.arange(n + 1)):
                        raise AssertionError('completion flag disagrees with true assignment')
                    row.update(evaluations=int(result.evaluations), event=int(result.completed),
                               initial_evaluations=n + 1,
                               front_hit_evaluations=result.front_hit if result.front_hit >= 0 else '',
                               stored_hit_evaluations=result.stored_hit if result.stored_hit >= 0 else '',
                               comparisons=int(result.comparisons),
                               certificate_checks=int(result.certificate_checks),
                               certificate_violations=int(result.certificate_violations), engine=result.engine,
                               initial_weight='', conditional_expected_evaluations='')
                    if track:
                        detail = dict(config_id=cell['config_id'], repetition=repetition,
                                      seed=seed, n=n, radius=radius)
                        for field in ('first_hit', 'level_visits', 'acceptance_jumps', 'sweep_jumps'):
                            detail[field] = getattr(result, field).tolist()
                        diag.write(json.dumps(detail, separators=(',', ':')) + '\n')
                else:
                    result = simulate_frontier(config)
                    row.update(evaluations=result['evaluations'], event=int(result['completed']),
                               initial_evaluations=1, front_hit_evaluations='', stored_hit_evaluations='',
                               comparisons=result['comparisons'], certificate_checks=0,
                               certificate_violations=0, engine='python',
                               initial_weight=result['initial_weight'],
                               conditional_expected_evaluations=result['conditional_expected_evaluations'])
                writer.writerow(row)
                total += 1
                completions += row['event']
            raw.flush()
            diag.flush()
            print(f"{cell['config_id']}: {protocol['replicates']} trials recorded", flush=True)
    try:
        commit = subprocess.check_output(['git', 'rev-parse', 'HEAD'], text=True,
                                         stderr=subprocess.DEVNULL).strip()
        dirty = bool(subprocess.check_output(['git', 'status', '--porcelain', '--',
                                              'src', 'tests', 'experiments', 'pyproject.toml',
                                              'requirements-evidence.txt'], text=True).strip())
    except (subprocess.CalledProcessError, FileNotFoundError):
        commit, dirty = None, None
    versions = {}
    for package in ('numpy', 'matplotlib', 'numba', 'pytest'):
        try:
            versions[package] = importlib.metadata.version(package)
        except importlib.metadata.PackageNotFoundError:
            versions[package] = None
    manifest = dict(schema_version=1, created_utc=datetime.now(timezone.utc).isoformat(),
                    source_commit=commit, source_tree_dirty=dirty, python=platform.python_version(),
                    platform=platform.platform(), dependencies=versions, rng='numpy.PCG64',
                    seed_derivation='first 8 SHA256 bytes of master|config_id|repetition, big-endian',
                    trials=total, completed=completions, censored=total - completions,
                    elapsed_seconds=time.perf_counter() - started, source_sha256=source_manifest(),
                    data_sha256={name: digest(out / name) for name in
                                 ('config.json', 'runs.csv', 'diagnostics.jsonl')})
    (out / 'manifest.json').write_text(json.dumps(manifest, indent=2, sort_keys=True) + '\n')
    return manifest


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--config', type=Path, required=True)
    parser.add_argument('--out', type=Path, required=True)
    parser.add_argument('--engine', choices=['auto', 'python', 'numba'], default='auto')
    parser.add_argument('--overwrite', action='store_true')
    args = parser.parse_args()
    manifest = run_experiments(args.config, args.out, args.engine, args.overwrite)
    print(json.dumps({key: manifest[key] for key in ('trials', 'completed', 'censored')}, indent=2))


if __name__ == '__main__':
    main()
