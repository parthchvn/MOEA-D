#!/usr/bin/env python3
"""Serial reproduction of dependencies and exact RORR checks, with a deadline.

Raw logs and execution timing are written only under --out. --verified-prior
can reuse a *completed full* round-18 replay, after checking its execution
receipt and every regenerated output against the published manifest.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import signal
import subprocess
import sys
import time

OUTPUTS = ('words.csv', 'entrance.csv', 'responses.csv', 'branches.csv', 'joint.csv',
           'shortcuts.csv', 'verification.json', 'dependency.json')
PRIOR_OUTPUTS = ('responses.csv', 'flux.csv', 'words.csv', 'entrance.csv',
                 'budget.csv', 'inequalities.csv', 'verification.json', 'dependency.json')


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def manifest_check(path):
    data = json.loads((path/'provenance.json').read_text())
    matches = {name: sha(path/name) == value for name, value in data['artifacts_sha256'].items()}
    assert all(matches.values()), matches
    return matches


def dependency(repo, replay):
    prior = repo/'research/reports/large-T-20261109/followup/round-0018'
    hashes = manifest_check(prior)
    receipt = json.loads((replay/'execution.json').read_text())
    assert receipt['status'] == 'pass'
    assert receipt['scientific_trajectories'] == 0
    assert receipt['scientific_seeds'] == []
    assert all(receipt['outputs_byte_identical'].get(name) is True for name in PRIOR_OUTPUTS)
    assert all(t['returncode'] == 0 for t in receipt['timings'])
    same = {name: (prior/name).read_bytes() == (replay/name).read_bytes() for name in PRIOR_OUTPUTS}
    assert all(same.values()), same
    old = json.loads((replay/'dependency.json').read_text())
    keep = ('original_registration_commit', 'registration_commit', 'original_primary',
            'followup_primary', 'original_stage_counts', 'followup_arms',
            'prior_seed_count', 'followup_seed_count', 'prior_vs_followup_seed_overlap',
            'original_decision', 'chronology_limit')
    oracle = repo/'research/reports/large-T-20261109/followup/round-0014'
    oracle_hashes = manifest_check(oracle)
    fingerprint = repo/'research/reports/large-T-20261109/followup/round-0015'
    p15 = json.loads((fingerprint/'provenance.json').read_text())
    assert sha(fingerprint/'words.csv') == p15['artifacts_sha256']['words.csv']
    return dict(status='mechanically checked; no plan or receipt repair needed',
                method='Completed full serial round-18 replay, including its recursive relevant plan, receipt, seed, geometry and centered-response checks; all eight outputs byte-identical. The new run separately computes RORR with sweep and phase solvers.',
                round18_outputs_byte_identical=same,
                round18_manifest_sha256=sha(prior/'provenance.json'),
                round18_artifacts_verified=len(hashes),
                round18_sources_sha256={name: sha(prior/name) for name in ('audit.md', 'audit.py', 'test_audit.py', 'reproduce.py')},
                round14_oracle_artifacts_verified=len(oracle_hashes),
                round14_oracle_sha256=sha(oracle/'audit.py'),
                round15_word_reference_sha256=sha(fingerprint/'words.csv'),
                premises='Round-18 marked D2 and baseline forcing bounds. No isolated-pair second-response candidate, positive-p global Schur bound or uniform remainder is assumed.',
                scientific_trajectories=0, scientific_seeds=[],
                **{key: old[key] for key in keep})


def main(repo, out, seconds, verified_prior):
    repo, out = repo.resolve(), out.resolve()
    here = Path(__file__).resolve().parent
    if out.exists():
        raise ValueError('Choose a fresh private output directory')
    out.mkdir(parents=True)
    env = dict(os.environ, PYTHONDONTWRITEBYTECODE='1', OPENBLAS_NUM_THREADS='1',
               OMP_NUM_THREADS='1', MKL_NUM_THREADS='1', VECLIB_MAXIMUM_THREADS='1',
               NUMEXPR_NUM_THREADS='1', MPLCONFIGDIR=str(out/'mpl-cache'))
    started = time.monotonic()
    timings = []

    def run(name, args):
        remaining = seconds-(time.monotonic()-started)
        if remaining <= 0:
            raise TimeoutError('Reproduction budget exhausted')
        before = time.monotonic()
        with (out/(name+'.log')).open('w') as log:
            process = subprocess.Popen([sys.executable, *map(str, args)], cwd=repo,
                                       env=env, stdout=log, stderr=subprocess.STDOUT,
                                       start_new_session=True)
            try:
                code = process.wait(timeout=remaining)
            except subprocess.TimeoutExpired:
                os.killpg(process.pid, signal.SIGTERM)
                process.wait(timeout=10)
                raise
        timings.append(dict(name=name, command=list(map(str, args)), returncode=code,
                            elapsed_seconds=time.monotonic()-before,
                            log_sha256=sha(out/(name+'.log'))))
        if code:
            raise RuntimeError(f'{name} failed; inspect the private log')

    prior = repo/'research/reports/large-T-20261109/followup/round-0018'
    manifest_check(prior)
    if verified_prior is None:
        replay = out/'prior'
        run('prior', [prior/'reproduce.py', '--repo', repo, '--out', replay,
                      '--seconds', max(1, int(seconds-(time.monotonic()-started)))])
        reused = False
    else:
        replay = verified_prior.resolve()
        reused = True
    dep = dependency(repo, replay)
    run('new-tests', [here/'test_rorr.py'])
    run('rorr', [here/'rorr.py', '--repo', repo, '--out', out/'data'])
    (out/'data/dependency.json').write_text(json.dumps(dep, indent=2, sort_keys=True)+'\n')
    for name in OUTPUTS:
        (out/name).write_bytes((out/'data'/name).read_bytes())
    same = {name: (here/name).read_bytes() == (out/name).read_bytes()
            for name in OUTPUTS if (here/name).exists()}
    assert all(same.values()), same
    result = dict(status='pass', elapsed_seconds=time.monotonic()-started,
                  timings=timings, outputs_byte_identical=same,
                  reused_completed_dependency_replay=reused,
                  dependency_execution_sha256=sha(replay/'execution.json'),
                  numerical_threads=1, scientific_trajectories=0, scientific_seeds=[])
    (out/'execution.json').write_text(json.dumps(result, indent=2, sort_keys=True)+'\n')
    print(json.dumps(result), flush=True)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--repo', type=Path, default=Path('.'))
    parser.add_argument('--out', type=Path, required=True)
    parser.add_argument('--seconds', type=int, default=9000)
    parser.add_argument('--verified-prior', type=Path)
    args = parser.parse_args()
    main(args.repo, args.out, args.seconds, args.verified_prior)
