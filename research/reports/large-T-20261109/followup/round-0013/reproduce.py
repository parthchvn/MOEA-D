#!/usr/bin/env python3
"""Serial exact replay. Generates no scientific trajectories or random seeds."""
import argparse
import json
import os
from pathlib import Path
import subprocess
import sys
import time


OUTPUTS = ('dependency.json', 'coefficients.csv', 'gaps.csv', 'oracle.json',
           'words.csv', 'excess.csv', 'cancellation.csv', 'verification.json')


def main(repo, out, reuse_work=None):
    repo, out = repo.resolve(), out.resolve()
    here = Path(__file__).resolve().parent
    if out.exists():
        raise ValueError('Use a new output directory')
    out.mkdir(parents=True)
    work = reuse_work.resolve() if reuse_work else out/'work'
    if not reuse_work:
        work.mkdir()
    env = dict(os.environ, PYTHONDONTWRITEBYTECODE='1', OPENBLAS_NUM_THREADS='1',
               OMP_NUM_THREADS='1', MKL_NUM_THREADS='1', VECLIB_MAXIMUM_THREADS='1',
               NUMEXPR_NUM_THREADS='1', MPLCONFIGDIR=str(out/'mpl-cache'))
    timing = []

    def run(arguments, name):
        start = time.monotonic()
        with (out/(name+'.log')).open('w') as log:
            completed = subprocess.run([sys.executable, *map(str, arguments)],
                cwd=repo, env=env, stdout=log, stderr=subprocess.STDOUT, timeout=6000)
        timing.append(dict(command=list(map(str, arguments)),
                           elapsed_seconds=time.monotonic()-start,
                           returncode=completed.returncode))
        if completed.returncode:
            raise RuntimeError(f'{name} failed; inspect its private log')

    if not reuse_work:
        prior = repo/'research/reports/large-T-20261109/followup'
        run([prior/'round-0011/reproduce.py', '--repo', repo, '--out', work/'prior'], 'prior')
        run([prior/'round-0012/audit.py', '--repo', repo, '--out', work/'round12', '--skip-full'], 'round12')
        run([here/'cubic.py', '--out', work/'exact', '--n', 3, 4, 5, 6], 'cubic')
        run([here/'oracle.py', '--out', work/'oracle.json', '--n', 3, 4], 'oracle')
        run([here/'words.py', '--out', work/'words', '--n', 4, 6], 'words')
    run([here/'curate.py', '--repo', repo, '--work', work, '--out', out], 'curate')
    same = {name: (here/name).read_bytes() == (out/name).read_bytes()
            for name in OUTPUTS if (here/name).exists()}
    assert all(same.values()), same
    (out/'execution.json').write_text(json.dumps(dict(timings=timing,
        reuse_completed_computations=bool(reuse_work), outputs_byte_identical=same,
        scientific_trajectories=0, scientific_seeds=[]), indent=2, sort_keys=True)+'\n')
    print(json.dumps(dict(status='pass', outputs_byte_identical=same,
                         reused_computations=bool(reuse_work)), sort_keys=True))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--repo', type=Path, default=Path('.'))
    parser.add_argument('--out', type=Path, required=True)
    parser.add_argument('--reuse-work', type=Path,
                        help='Existing completed raw calculations; revalidate and recurate, without rerunning algebra')
    args = parser.parse_args()
    main(args.repo, args.out, args.reuse_work)
