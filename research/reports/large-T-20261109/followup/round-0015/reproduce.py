#!/usr/bin/env python3
"""Serial exact replay; private fractions/logs stay in the requested directory."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import time

OUTPUTS = ('coefficients.csv', 'gaps.csv', 'words.csv', 'verification.json',
           'pair.csv', 'obstruction.csv', 'entrance.csv', 'pair.json',
           'excess.csv', 'stationary.csv', 'mixed.csv', 'excess.json',
           'dependency.json')


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def dependency(repo, replay):
    prior = repo/'research/reports/large-T-20261109/followup/round-0014'
    names = ('acceptance.csv', 'births.csv', 'words.csv', 'phases.csv',
             'verification.json', 'dependency.json')
    checks = {name: (prior/name).read_bytes() == (replay/name).read_bytes() for name in names}
    assert all(checks.values()), checks
    provenance = json.loads((prior/'provenance.json').read_text())
    hashes = {name: sha(prior/name) == value for name, value in provenance['artifacts_sha256'].items()}
    assert all(hashes.values()), hashes
    old = json.loads((replay/'dependency.json').read_text())
    keep = ('original_registration_commit', 'registration_commit', 'original_primary',
            'followup_primary', 'original_stage_counts', 'followup_arms',
            'prior_seed_count', 'followup_seed_count', 'prior_vs_followup_seed_overlap',
            'original_decision', 'chronology_limit')
    return dict(status='mechanically checked; no dependency repair needed',
                method='Full round-14 replay, recursively through prior plans and receipts; round-14 artifact manifest verified; new fourth coefficients match published orders zero through three.',
                round14_outputs_byte_identical=checks,
                round14_artifact_manifest_sha256=sha(prior/'provenance.json'),
                round14_artifact_hashes_verified=hashes,
                premises='Audited two-entry inequality and phase-aware orphan identity. The new isolated-pair argument is derived independently; no unpublished manuscript or positive-p Schur full solve is assumed.',
                scientific_trajectories=0, scientific_seeds=[],
                **{key: old[key] for key in keep})


def main(repo, out, seconds):
    repo, out = repo.resolve(), out.resolve()
    here = Path(__file__).resolve().parent
    if out.exists():
        raise ValueError('Use a fresh output directory')
    out.mkdir(parents=True)
    data = out/'data'
    data.mkdir()
    env = dict(os.environ, PYTHONDONTWRITEBYTECODE='1', OPENBLAS_NUM_THREADS='1',
               OMP_NUM_THREADS='1', MKL_NUM_THREADS='1', VECLIB_MAXIMUM_THREADS='1',
               NUMEXPR_NUM_THREADS='1', MPLCONFIGDIR=str(out/'mpl-cache'))
    start = time.monotonic()
    timings = []

    def run(name, args):
        remaining = seconds-(time.monotonic()-start)
        if remaining <= 0:
            raise TimeoutError('Replay deadline exhausted')
        before = time.monotonic()
        with (out/(name+'.log')).open('w') as log:
            process = subprocess.run([sys.executable, *map(str, args)], cwd=repo,
                                     env=env, stdout=log, stderr=subprocess.STDOUT,
                                     timeout=remaining)
        timings.append(dict(name=name, elapsed_seconds=time.monotonic()-before,
                            returncode=process.returncode, command=list(map(str, args))))
        if process.returncode:
            raise RuntimeError(f'{name} failed; see private log')

    prior = repo/'research/reports/large-T-20261109/followup/round-0014/reproduce.py'
    run('prior', [prior, '--repo', repo, '--out', out/'prior'])
    dep = dependency(repo, out/'prior')
    run('fourth', [here/'fourth.py', '--out', out/'exact', '--n', 3, 4, 5])
    run('verify', [here/'verify.py', '--repo', repo, '--inputs', out/'exact', '--out', data])
    run('pair', [here/'pair.py', '--out', data])
    run('excess', [here/'excess.py', '--repo', repo, '--out', data])
    (data/'dependency.json').write_text(json.dumps(dep, indent=2, sort_keys=True)+'\n')
    for name in OUTPUTS:
        (out/name).write_bytes((data/name).read_bytes())
    same = {name: (here/name).read_bytes() == (out/name).read_bytes()
            for name in OUTPUTS if (here/name).exists()}
    assert all(same.values()), same
    result = dict(status='pass', timings=timings,
                  elapsed_seconds=time.monotonic()-start,
                  outputs_byte_identical=same, numerical_threads=1,
                  scientific_trajectories=0, scientific_seeds=[])
    (out/'execution.json').write_text(json.dumps(result, indent=2, sort_keys=True)+'\n')
    print(json.dumps(result), flush=True)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--repo', type=Path, default=Path('.'))
    parser.add_argument('--out', type=Path, required=True)
    parser.add_argument('--seconds', type=int, default=3000)
    args = parser.parse_args()
    main(args.repo, args.out, args.seconds)
