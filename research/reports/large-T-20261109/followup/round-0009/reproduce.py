#!/usr/bin/env python3
"""Serial published-evidence replay and independent exact audit, without sampling."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import time


OUTPUTS = ('dependency.json', 'suffix.csv', 'mixed.csv', 'local.csv', 'verification.json')
PRIOR_OUTPUTS = ('dependency.json', 'coefficients.csv', 'gaps.csv', 'numeric.csv',
                 'oracle.json', 'verification.json', 'comparison.json', 'bounds.csv')


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def dependency(repo, replay):
    prior = repo / 'research/reports/large-T-20261109/followup/round-0008'
    same = {name: (prior / name).read_bytes() == (replay / name).read_bytes()
            for name in PRIOR_OUTPUTS}
    assert all(same.values()), same
    old = json.loads((replay / 'dependency.json').read_text())
    fields = ('original_registration_commit', 'registration_commit', 'original_primary',
              'followup_primary', 'original_stage_counts', 'followup_arms',
              'prior_seed_count', 'followup_seed_count', 'prior_vs_followup_seed_overlap',
              'original_decision', 'chronology_limit')
    return dict(status='mechanically checked; no dependency repair needed',
                method='Complete round-8 replay, recursively checking earlier published registrations, receipts, seed separation and deterministic outputs.',
                round8_outputs_byte_identical=same,
                round8_sha256={name: sha(prior / name) for name in (*PRIOR_OUTPUTS, 'derivation.md', 'second.py', 'reproduce.py')},
                **{key: old[key] for key in fields},
                scientific_trajectories=0, scientific_seeds=[],
                scope='Offline audit. No error-family theorem, unavailable appendix or external theorem is used for the polynomial proof.')


def main(repo, out, reuse_prior=None):
    repo, out = repo.resolve(), out.resolve()
    here = Path(__file__).resolve().parent
    if out.exists():
        raise ValueError('Use a new output directory')
    out.mkdir(parents=True)
    env = os.environ.copy()
    env.update(PYTHONDONTWRITEBYTECODE='1', OPENBLAS_NUM_THREADS='1', OMP_NUM_THREADS='1',
               MKL_NUM_THREADS='1', VECLIB_MAXIMUM_THREADS='1', NUMEXPR_NUM_THREADS='1',
               MPLCONFIGDIR=str(out / 'mpl-cache'))
    timings = []

    def run(args):
        started = time.monotonic()
        subprocess.run([sys.executable, *map(str, args)], cwd=repo, env=env,
                       timeout=1800, check=True)
        timings.append(dict(command=list(map(str, args)), elapsed_seconds=time.monotonic() - started))

    prior_out = reuse_prior.resolve() if reuse_prior else out / 'prior'
    if reuse_prior is None:
        run([repo / 'research/reports/large-T-20261109/followup/round-0008/reproduce.py',
             '--repo', repo, '--out', prior_out])
    result = dependency(repo, prior_out)
    (out / 'dependency.json').write_text(json.dumps(result, indent=2, sort_keys=True) + '\n')
    run(['-S', here / 'audit.py', '--repo', repo, '--out', out])
    same = {name: (here / name).read_bytes() == (out / name).read_bytes()
            for name in OUTPUTS if (here / name).exists()}
    assert all(same.values()), same
    (out / 'execution.json').write_text(json.dumps(dict(timings=timings,
        reuse_prior=str(reuse_prior) if reuse_prior else None,
        outputs_byte_identical=same, scientific_trajectories=0), indent=2, sort_keys=True) + '\n')
    print(json.dumps(dict(status='pass', byte_identical=same, scientific_trajectories=0), sort_keys=True))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--repo', type=Path, default=Path('.'))
    parser.add_argument('--out', type=Path, required=True)
    parser.add_argument('--reuse-prior', type=Path,
                        help='Reuse a completed round-8 replay; all eight required outputs are still compared.')
    args = parser.parse_args()
    main(args.repo, args.out, args.reuse_prior)
