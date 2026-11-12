#!/usr/bin/env python3
"""Serial replay of relevant premises and independent round-16 exact audit.

No simulations are launched. Prior study receipts are analyzed only. Private
logs and exact intermediate state caches stay in the requested fresh directory.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import time

OUTPUTS = ('rewards.csv', 'stationary.csv', 'words.csv', 'witness.json',
           'verification.json', 'dependency.json')


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def main(repo, out, seconds):
    repo, out = repo.resolve(), out.resolve()
    here = Path(__file__).resolve().parent
    prior = repo/'research/reports/large-T-20261109/followup'
    if out.exists():
        raise ValueError('Use a fresh replay destination')
    out.mkdir(parents=True)
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
        with (out/(name+'.log')).open('w') as f:
            # A process group makes the deadline include nested earlier replays.
            process = subprocess.Popen([sys.executable, *map(str, args)], cwd=repo,
                                       env=env, stdout=f, stderr=subprocess.STDOUT,
                                       start_new_session=True)
            try:
                code = process.wait(timeout=remaining)
            except subprocess.TimeoutExpired:
                import signal
                os.killpg(process.pid, signal.SIGTERM)
                process.wait(timeout=10)
                raise
        timings.append(dict(name=name, elapsed_seconds=time.monotonic()-before,
                            returncode=code, command=list(map(str, args))))
        if code:
            raise RuntimeError(f'{name} failed; inspect its private log')

    manifests = {}
    for number in (14, 15):
        source = prior/f'round-{number:04}'
        manifest = json.loads((source/'provenance.json').read_text())
        hashes = {name: sha(source/name) == value for name, value in manifest['artifacts_sha256'].items()}
        assert all(hashes.values()), hashes
        manifests[str(number)] = dict(manifest_sha256=sha(source/'provenance.json'),
                                      artifacts=len(hashes), all_match=True)
    run('prior', [prior/'round-0014/reproduce.py', '--repo', repo, '--out', out/'prior'])
    checks14 = {name: (prior/'round-0014'/name).read_bytes() == (out/'prior'/name).read_bytes()
                for name in ('acceptance.csv','births.csv','words.csv','phases.csv',
                             'verification.json','dependency.json')}
    assert all(checks14.values())
    run('excess', [prior/'round-0015/excess.py', '--repo', repo, '--out', out/'excess'])
    checks15 = {name: (prior/'round-0015'/name).read_bytes() == (out/'excess'/name).read_bytes()
                for name in ('excess.csv','stationary.csv','mixed.csv','excess.json')}
    assert all(checks15.values())
    run('audit', [here/'audit.py', '--repo', repo, '--out', out/'data'])
    old = json.loads((out/'prior/dependency.json').read_text())
    keep = ('original_registration_commit', 'registration_commit', 'original_primary',
            'followup_primary', 'original_stage_counts', 'followup_arms',
            'prior_seed_count', 'followup_seed_count', 'prior_vs_followup_seed_overlap',
            'original_decision', 'chronology_limit')
    dependency = dict(status='mechanically checked; no plan or receipt repair needed',
                      method='Full round-14 recursive replay through earlier plans/receipts; round-15 excess replay; independent round-16 sweep solver matches published exact excess and RROO fractions.',
                      round14_outputs_byte_identical=checks14,
                      round15_outputs_byte_identical=checks15,
                      manifests=manifests,
                      premises='Clean geometry, two-entry weighting and phase-local subtraction rederived in audit.md. No positive-p global Schur solve, isolated-pair second-response candidate, or full fourth-order numerical grid is used.',
                      scientific_trajectories=0, scientific_seeds=[],
                      **{key: old[key] for key in keep})
    (out/'data/dependency.json').write_text(json.dumps(dependency, indent=2, sort_keys=True)+'\n')
    for name in OUTPUTS:
        (out/name).write_bytes((out/'data'/name).read_bytes())
    same = {name: (here/name).read_bytes() == (out/name).read_bytes()
            for name in OUTPUTS if (here/name).exists()}
    assert all(same.values()), same
    result = dict(status='pass', timings=timings, elapsed_seconds=time.monotonic()-start,
                  outputs_byte_identical=same, numerical_threads=1,
                  scientific_trajectories=0, scientific_seeds=[])
    (out/'execution.json').write_text(json.dumps(result, indent=2, sort_keys=True)+'\n')
    print(json.dumps(result), flush=True)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--repo', type=Path, default=Path('.'))
    parser.add_argument('--out', type=Path, required=True)
    parser.add_argument('--seconds', type=int, default=1800)
    args = parser.parse_args()
    main(args.repo, args.out, args.seconds)
