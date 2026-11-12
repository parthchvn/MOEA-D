#!/usr/bin/env python3
"""Serial exact reproduction and recursive published-evidence replay."""
import argparse
import csv
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import time


PRIOR = ('dependency.json', 'obstruction.csv', 'orphan.csv', 'verification.json')
OUTPUTS = ('dependency.json', 'inequalities.csv', 'schur.csv', 'moments.csv',
           'bounds.csv', 'verification.json')


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main(repo, out, reuse_prior=None):
    repo, out = repo.resolve(), out.resolve()
    here = Path(__file__).resolve().parent
    prior = repo/'research/reports/large-T-20261109/followup/round-0010'
    if out.exists():
        raise ValueError('Use a new output directory')
    out.mkdir(parents=True)
    env = os.environ.copy()
    env.update(PYTHONDONTWRITEBYTECODE='1', OPENBLAS_NUM_THREADS='1',
               OMP_NUM_THREADS='1', MKL_NUM_THREADS='1', VECLIB_MAXIMUM_THREADS='1',
               NUMEXPR_NUM_THREADS='1', MPLCONFIGDIR=str(out/'mpl-cache'))
    timings = []

    def run(args):
        start = time.monotonic()
        subprocess.run([sys.executable, *map(str, args)], cwd=repo, env=env,
                       check=True, timeout=1800)
        timings.append(dict(command=list(map(str, args)), elapsed_seconds=time.monotonic()-start))

    replay = reuse_prior.resolve() if reuse_prior else out/'prior'
    if reuse_prior is None:
        run([prior/'reproduce.py', '--repo', repo, '--out', replay])
    equal = {name: (prior/name).read_bytes() == (replay/name).read_bytes() for name in PRIOR}
    assert all(equal.values()), equal
    old = json.loads((replay/'dependency.json').read_text())
    run(['-S', here/'check.py', '--out', out])
    rows = list(csv.DictReader((prior/'obstruction.csv').open()))
    witness = next(row for row in rows if row['n'] == '33' and row['kind'] == 'adjacent_pair')
    fields = ('original_registration_commit', 'registration_commit', 'original_primary',
              'followup_primary', 'original_stage_counts', 'followup_arms',
              'prior_seed_count', 'followup_seed_count', 'prior_vs_followup_seed_overlap',
              'original_decision', 'chronology_limit')
    dependency = dict(
        status='mechanically checked; no dependency repair needed',
        method='Complete round-10 replay, including recursive rounds 1-9, registration and receipt verification.',
        round10_outputs_byte_identical=equal,
        round10_sha256={name: sha(prior/name) for name in (*PRIOR, 'proof.md', 'check.py', 'reproduce.py')},
        prior_absolute_majorant_witness=witness,
        **{key: old[key] for key in fields},
        scientific_trajectories=0, scientific_seeds=[],
        scope='Offline deterministic algebra. The new proof rederives its premises; no prior forest theorem or unavailable appendix is used.')
    (out/'dependency.json').write_text(json.dumps(dependency, indent=2, sort_keys=True)+'\n')
    same = {name: (here/name).read_bytes() == (out/name).read_bytes()
            for name in OUTPUTS if (here/name).exists()}
    assert all(same.values()), same
    (out/'execution.json').write_text(json.dumps(dict(timings=timings,
        reuse_prior=str(reuse_prior) if reuse_prior else None,
        outputs_byte_identical=same, scientific_trajectories=0), indent=2, sort_keys=True)+'\n')
    print(json.dumps(dict(status='pass', byte_identical=same, scientific_trajectories=0), sort_keys=True))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--repo', type=Path, default=Path('.'))
    parser.add_argument('--out', type=Path, required=True)
    parser.add_argument('--reuse-prior', type=Path,
                        help='Completed round-10 replay; all four outputs are still byte-compared.')
    args = parser.parse_args()
    main(args.repo, args.out, args.reuse_prior)
