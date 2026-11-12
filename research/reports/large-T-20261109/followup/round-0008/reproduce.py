#!/usr/bin/env python3
"""Serial reproduction of published dependencies and round-8 arithmetic.

No scientific sampler is called. The new oracle/checks use only the standard
library; NumPy and Matplotlib are needed by the earlier dependency replay.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import time


OUTPUTS = ('dependency.json', 'coefficients.csv', 'gaps.csv', 'numeric.csv',
           'oracle.json', 'verification.json', 'comparison.json', 'bounds.csv')


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def dependency(repo, replay):
    prior = repo/'research/reports/large-T-20261109/followup/round-0007'
    names = ('dependency.json', 'edges.csv', 'exceptions.csv', 'verification.json')
    same = {name: (prior/name).read_bytes() == (replay/name).read_bytes() for name in names}
    assert all(same.values()), same
    result = json.loads((prior/'dependency.json').read_text())
    result.update(status='mechanically checked; no dependency repair needed',
                  method='Complete round-7 reproduction, recursively verifying committed plans, receipts, seed separation and earlier exact certificates.',
                  round7_outputs_byte_identical=same,
                  prior_round7_sha256={name: sha(prior/name) for name in (*names, 'audit.md', 'audit.py', 'reproduce.py')},
                  scientific_trajectories=0, scientific_seeds=[],
                  scope='Offline published evidence. No error-family theorem, unavailable appendix or external theorem is needed by the second-order proof.')
    return result


def main(repo, out, reuse_prior=None):
    repo, out = repo.resolve(), out.resolve()
    here = Path(__file__).resolve().parent
    if out.exists():
        raise ValueError('Use a new output directory')
    out.mkdir(parents=True)
    env = os.environ.copy()
    env.update(PYTHONDONTWRITEBYTECODE='1', OPENBLAS_NUM_THREADS='1', OMP_NUM_THREADS='1',
               MKL_NUM_THREADS='1', VECLIB_MAXIMUM_THREADS='1', NUMEXPR_NUM_THREADS='1',
               MPLCONFIGDIR=str(out/'mpl-cache'))
    timings = []
    def run(args, timeout=1800):
        started = time.monotonic()
        subprocess.run([sys.executable, *map(str, args)], cwd=repo, env=env,
                       check=True, timeout=timeout)
        timings.append(dict(command=list(map(str, args)), elapsed_seconds=time.monotonic()-started))
    if reuse_prior is None:
        prior_out = out/'prior'
        run([repo/'research/reports/large-T-20261109/followup/round-0007/reproduce.py',
             '--repo', repo, '--out', prior_out])
    else:
        prior_out = reuse_prior.resolve()
    dep = dependency(repo, prior_out)
    (out/'dependency.json').write_text(json.dumps(dep, indent=2, sort_keys=True)+'\n')
    run(['-S', here/'second.py', '--n', 3, 4, '--out', out])
    run(['-S', here/'second.py', '--float', '--n', *range(3, 13), '--out', out/'numeric'])
    shutil.copyfile(out/'numeric/gaps.csv', out/'numeric.csv')
    run(['-S', here/'oracle.py', '--n', 3, 4, '--out', out/'oracle.json'])
    run(['-S', here/'verify.py', '--repo', repo, '--bundle', out, '--out', out])
    same = {name: (out/name).read_bytes() == (here/name).read_bytes()
            for name in OUTPUTS if (here/name).exists()}
    assert all(same.values()), same
    # Execution receipt stays in the caller's regeneration directory.
    (out/'execution.json').write_text(json.dumps(dict(timings=timings,
        reuse_prior=str(reuse_prior) if reuse_prior else None,
        outputs_byte_identical=same, scientific_trajectories=0), indent=2, sort_keys=True)+'\n')
    print(json.dumps(dict(status='pass', byte_identical=same, scientific_trajectories=0), sort_keys=True))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--repo', type=Path, default=Path('.'))
    parser.add_argument('--out', type=Path, required=True)
    parser.add_argument('--reuse-prior', type=Path,
                        help='Reuse an already completed round-7 replay; every required output is still compared.')
    args = parser.parse_args()
    main(args.repo, args.out, args.reuse_prior)
