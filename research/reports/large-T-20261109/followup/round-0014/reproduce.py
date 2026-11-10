#!/usr/bin/env python3
"""Serial deterministic reproduction with published dependency verification."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import time


OUTPUTS = ('acceptance.csv', 'births.csv', 'words.csv', 'phases.csv',
           'verification.json', 'dependency.json')


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main(repo, out, reuse_prior=None):
    repo, out = repo.resolve(), out.resolve()
    here = Path(__file__).resolve().parent
    prior_root = repo/'research/reports/large-T-20261109/followup'
    if out.exists():
        raise ValueError('Use a fresh output directory')
    out.mkdir(parents=True)
    env = dict(os.environ, PYTHONDONTWRITEBYTECODE='1', OPENBLAS_NUM_THREADS='1',
               OMP_NUM_THREADS='1', MKL_NUM_THREADS='1', VECLIB_MAXIMUM_THREADS='1',
               NUMEXPR_NUM_THREADS='1', MPLCONFIGDIR=str(out/'mpl-cache'))
    timings = []

    def run(args, name):
        start = time.monotonic()
        with (out/(name+'.log')).open('w') as log:
            done = subprocess.run([sys.executable, *map(str, args)], cwd=repo,
                                  env=env, stdout=log, stderr=subprocess.STDOUT,
                                  timeout=2400)
        timings.append(dict(name=name, command=list(map(str, args)),
                            elapsed_seconds=time.monotonic()-start,
                            returncode=done.returncode))
        if done.returncode:
            raise RuntimeError(f'{name} failed; see private log')

    replay = reuse_prior.resolve() if reuse_prior else out/'prior'
    if not reuse_prior:
        run([prior_root/'round-0011/reproduce.py', '--repo', repo, '--out', replay], 'prior')
    prior_outputs = ('dependency.json', 'inequalities.csv', 'schur.csv',
                     'moments.csv', 'bounds.csv', 'verification.json')
    equal = {name: (prior_root/'round-0011'/name).read_bytes() == (replay/name).read_bytes()
             for name in prior_outputs}
    assert all(equal.values()), equal
    manifests = {}
    for number in (12, 13):
        source = prior_root/f'round-{number:04}'
        provenance = json.loads((source/'provenance.json').read_text())
        checks = {name: sha(source/name) == expected
                  for name, expected in provenance['artifacts_sha256'].items()}
        assert all(checks.values()), checks
        manifests[str(number)] = dict(manifest_sha256=sha(source/'provenance.json'),
                                      artifacts=len(checks), all_match=True)
    run([here/'audit.py', '--repo', repo, '--out', out, '--n', 4, 6, '--phases', 4, 6], 'audit')
    old = json.loads((replay/'dependency.json').read_text())
    keep = ('original_registration_commit', 'registration_commit', 'original_primary',
            'followup_primary', 'original_stage_counts', 'followup_arms',
            'prior_seed_count', 'followup_seed_count', 'prior_vs_followup_seed_overlap',
            'original_decision', 'chronology_limit')
    dependency = dict(status='mechanically checked; no dependency repair needed',
                      method='Recursive rounds 1-11 replay; round 12/13 artifact manifests verified; independent phase solver matches all 16 round-13 ordered cubic words and both T=2 cubic totals at n=4,6.',
                      round11_outputs_byte_identical=equal,
                      published_manifests=manifests,
                      premises='The audit rederives clean geometry, two-entry weighting, local Poisson and phase identities, and all mixed-word bounds. The round-12 positive-p full Schur solve is not a premise and is not rerun.',
                      **{key: old[key] for key in keep},
                      scientific_trajectories=0, scientific_seeds=[])
    (out/'dependency.json').write_text(json.dumps(dependency, indent=2, sort_keys=True)+'\n')
    same = {name: (here/name).read_bytes() == (out/name).read_bytes()
            for name in OUTPUTS if (here/name).exists()}
    assert all(same.values()), same
    (out/'execution.json').write_text(json.dumps(dict(timings=timings,
        reused_prior_replay=bool(reuse_prior), outputs_byte_identical=same,
        scientific_trajectories=0, scientific_seeds=[]), indent=2, sort_keys=True)+'\n')
    print(json.dumps(dict(status='pass', timings=timings, outputs_byte_identical=same)))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--repo', type=Path, default=Path('.'))
    parser.add_argument('--out', type=Path, required=True)
    parser.add_argument('--reuse-prior', type=Path,
                        help='Already completed round-11 replay; all six outputs are still checked')
    args = parser.parse_args()
    main(args.repo, args.out, args.reuse_prior)
