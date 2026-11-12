#!/usr/bin/env python3
"""Serial deterministic audit and recursive receipt replay; never samples."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import time


PRIOR = ('dependency.json', 'inequalities.csv', 'schur.csv', 'moments.csv',
         'bounds.csv', 'verification.json')
OUTPUTS = ('dependency.json', 'phase.csv', 'pair.csv', 'tensor.csv', 'moments.csv',
           'verification.json')


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main(repo, out, reuse_prior=None):
    repo, out = repo.resolve(), out.resolve()
    here = Path(__file__).resolve().parent
    prior = repo/'research/reports/large-T-20261109/followup/round-0011'
    if out.exists():
        raise ValueError('Use a fresh output directory')
    out.mkdir(parents=True)
    env = dict(os.environ, PYTHONDONTWRITEBYTECODE='1', OPENBLAS_NUM_THREADS='1',
               OMP_NUM_THREADS='1', MKL_NUM_THREADS='1', VECLIB_MAXIMUM_THREADS='1',
               NUMEXPR_NUM_THREADS='1', MPLCONFIGDIR=str(out/'mpl-cache'))
    timing = []

    def run(args, name):
        start = time.monotonic()
        with (out/(name+'.log')).open('w') as log:
            proc = subprocess.run([sys.executable, *map(str, args)], cwd=repo,
                                  env=env, stdout=log, stderr=subprocess.STDOUT,
                                  timeout=6000)
        timing.append(dict(command=list(map(str, args)), elapsed_seconds=time.monotonic()-start,
                           returncode=proc.returncode))
        if proc.returncode:
            raise RuntimeError(f'{name} failed; see its private replay log')

    replay = reuse_prior.resolve() if reuse_prior else out/'prior'
    if reuse_prior is None:
        run([prior/'reproduce.py', '--repo', repo, '--out', replay], 'prior')
    equal = {name: (prior/name).read_bytes() == (replay/name).read_bytes() for name in PRIOR}
    assert all(equal.values()), equal
    old = json.loads((replay/'dependency.json').read_text())
    run([here/'audit.py', '--repo', repo, '--out', out], 'audit')
    fields = ('original_registration_commit', 'registration_commit', 'original_primary',
              'followup_primary', 'original_stage_counts', 'followup_arms',
              'prior_seed_count', 'followup_seed_count', 'prior_vs_followup_seed_overlap',
              'original_decision', 'chronology_limit', 'prior_absolute_majorant_witness')
    dependency = dict(status='mechanically checked; no dependency repair needed',
                      method='Complete round-11 replay and recursive rounds 1-10, including prior registration, receipt and seed checks.',
                      round11_outputs_byte_identical=equal,
                      round11_sha256={name: digest(prior/name) for name in
                                      (*PRIOR, 'proof.md', 'check.py', 'reproduce.py')},
                      **{key: old[key] for key in fields},
                      scientific_trajectories=0, scientific_seeds=[],
                      proof_dependencies='The phase and tensor premises are rederived in audit.md and independently checked by audit.py; no prior forest or coefficient theorem is assumed.')
    (out/'dependency.json').write_text(json.dumps(dependency, indent=2, sort_keys=True)+'\n')
    same = {name: (here/name).read_bytes() == (out/name).read_bytes()
            for name in OUTPUTS if (here/name).exists()}
    assert all(same.values()), same
    (out/'execution.json').write_text(json.dumps(dict(timings=timing,
        reuse_prior=str(reuse_prior) if reuse_prior else None,
        outputs_byte_identical=same, scientific_trajectories=0), indent=2, sort_keys=True)+'\n')
    print(json.dumps(dict(status='pass', outputs_byte_identical=same, scientific_trajectories=0)))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--repo', type=Path, default=Path('.'))
    parser.add_argument('--out', type=Path, required=True)
    parser.add_argument('--reuse-prior', type=Path,
                        help='Completed round-11 replay; all six outputs are still byte-compared')
    args = parser.parse_args()
    main(args.repo, args.out, args.reuse_prior)
