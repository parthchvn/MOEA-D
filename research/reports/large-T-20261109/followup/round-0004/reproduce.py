#!/usr/bin/env python3
"""Reproduce deterministic proof checks and replay the published dependency audit.

No sampler is invoked. Requires a repository checkout and NumPy for the OLD
registered bootstrap replay. The new proof checker uses the standard library.
"""
import argparse
import csv
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def dependency(repo, replay):
    old = repo/'research/reports/large-T-20261109/followup/round-0003'
    audit = json.loads((replay/'audit.json').read_text())
    files = ['audit.json', 'inputs.json', 'cells.csv', 'phases.csv', 'seeds.csv', 'trials.csv']
    equality = {name: (replay/name).read_bytes() == (old/name).read_bytes() for name in files}
    if not all(equality.values()):
        raise ValueError('Published round-3 dependency did not reproduce exactly')
    original = repo/'research/reports/large-T-20261109/campaign/cells.csv'
    with original.open() as f:
        cells = [row for row in csv.DictReader(f)
                 if row['stage'] == 'main' and row['n'] == '256'
                 and row['T'] in ('1', '3', '16')
                 and row['factor'] == '0.015625' and row['event'] == 'exact_sweep']
    keys = ['status', 'comparison_checks', 'max_absolute_numeric_discrepancy',
            'dependency_repair_needed', 'registration_commit', 'original_registration_commit',
            'followup_primary', 'followup_arms', 'followup_differences',
            'original_primary', 'original_stage_counts', 'original_decision',
            'blocked_holdout_mean_bounds', 'blocked_holdout_ratio_bounds', 'seed_audit',
            'published_timing', 'limitations']
    return dict(method='Exact replay of the committed round-3 independent receipt auditor',
                auditor='research/reports/large-T-20261109/followup/round-0003/audit.py',
                auditor_sha256=sha(old/'audit.py'),
                scientific_trajectories_generated=0,
                prior_outputs_byte_identical=equality,
                prior_output_sha256={name: sha(old/name) for name in files},
                original_n256_low_noise_cells=cells,
                verified={key: audit[key] for key in keys})


def main(repo, out):
    repo, out = repo.resolve(), out.resolve()
    here = Path(__file__).resolve().parent
    out.mkdir(parents=True, exist_ok=True)
    if out == here:
        raise ValueError('Choose a separate output directory')
    env = os.environ.copy()
    env.update(PYTHONDONTWRITEBYTECODE='1', OPENBLAS_NUM_THREADS='1',
               OMP_NUM_THREADS='1', MKL_NUM_THREADS='1', VECLIB_MAXIMUM_THREADS='1')
    subprocess.run([sys.executable, str(here/'check.py'), '--out', str(out)],
                   check=True, env=env, cwd=repo)
    subprocess.run([sys.executable,
                    'research/reports/large-T-20261109/followup/round-0003/audit.py',
                    '--repo', str(repo), '--out', str(out/'dependency')],
                   check=True, env=env, cwd=repo)
    value = dependency(repo, out/'dependency')
    (out/'dependency.json').write_text(json.dumps(value, indent=2, sort_keys=True)+'\n')
    matched = {}
    for name in ('kernels.csv', 'bounds.csv', 'verification.json', 'dependency.json'):
        if (here/name).exists():
            matched[name] = (here/name).read_bytes() == (out/name).read_bytes()
    if not all(matched.values()):
        raise ValueError(f'New curated output mismatch: {matched}')
    print(json.dumps(dict(new_outputs_byte_identical=matched, sampling_invocations=0)))


if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--repo', type=Path, default=Path('.'))
    p.add_argument('--out', type=Path, required=True)
    args = p.parse_args()
    main(args.repo, args.out)
