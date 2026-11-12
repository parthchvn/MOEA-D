#!/usr/bin/env python3
"""Serial exact audit replay, including published dependency verification.

Writes raw logs only to a fresh caller-selected private run directory.
No scientific trajectories, seeds, external access or commits are generated.
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

OUTPUTS = ('responses.csv', 'flux.csv', 'words.csv', 'entrance.csv',
           'budget.csv', 'inequalities.csv', 'verification.json', 'dependency.json')
PRIOR_OUTPUTS = ('centered.csv', 'words.csv', 'flux.csv', 'entrance.csv',
                 'verification.json', 'dependency.json')


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def verify_manifest(prior):
    manifest = json.loads((prior/'provenance.json').read_text())
    matches = {name: sha(prior/name) == value
               for name, value in manifest['artifacts_sha256'].items()}
    if not all(matches.values()):
        raise AssertionError(matches)
    return matches


def dependency(repo, prior_out):
    prior = repo/'research/reports/large-T-20261109/followup/round-0017'
    hashes = verify_manifest(prior)
    same = {name: (prior/name).read_bytes() == (prior_out/name).read_bytes()
            for name in PRIOR_OUTPUTS}
    assert all(same.values()), same
    old = json.loads((prior_out/'dependency.json').read_text())
    keep = ('original_registration_commit', 'registration_commit', 'original_primary',
            'followup_primary', 'original_stage_counts', 'followup_arms',
            'prior_seed_count', 'followup_seed_count', 'prior_vs_followup_seed_overlap',
            'original_decision', 'chronology_limit')
    sources = ('proof.md', 'centered.py', 'test_centered.py', 'words.csv',
               'centered.csv', 'flux.csv', 'entrance.csv', 'reproduce.py')
    return dict(status='mechanically checked; no plan or receipt repair needed',
                method='Full serial round-17 replay, including its recursive relevant earlier registration, receipt, seed and geometry verification; published artifacts hash-checked before replay.',
                round17_outputs_byte_identical=same,
                round17_manifest_sha256=sha(prior/'provenance.json'),
                round17_manifest_artifacts=len(hashes),
                round17_sources_sha256={name: sha(prior/name) for name in sources},
                premises='Clean geometry and acceptance factors rederived in the new audit. Published centered/word fractions used only as comparison targets after replay. No isolated-pair second-response candidate or positive-p global Schur theorem is assumed.',
                scientific_trajectories=0, scientific_seeds=[],
                **{key: old[key] for key in keep})


def main(repo, out, seconds):
    repo, out = repo.resolve(), out.resolve()
    here = Path(__file__).resolve().parent
    if out.exists():
        raise ValueError('Choose a fresh output directory')
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
            proc = subprocess.Popen([sys.executable, *map(str, args)], cwd=repo,
                                    env=env, stdout=f, stderr=subprocess.STDOUT,
                                    start_new_session=True)
            try:
                code = proc.wait(timeout=remaining)
            except subprocess.TimeoutExpired:
                os.killpg(proc.pid, signal.SIGTERM)
                proc.wait(timeout=10)
                raise
        timings.append(dict(name=name, elapsed_seconds=time.monotonic()-before,
                            returncode=code, command=list(map(str, args))))
        if code:
            raise RuntimeError(f'{name} failed; inspect its private log')

    prior = repo/'research/reports/large-T-20261109/followup/round-0017'
    verify_manifest(prior)
    run('prior', [prior/'reproduce.py', '--repo', repo, '--out', out/'prior',
                  '--seconds', max(1, int(seconds))])
    dep = dependency(repo, out/'prior')
    run('audit', [here/'audit.py', '--repo', repo, '--out', out/'data'])
    (out/'data/dependency.json').write_text(json.dumps(dep, indent=2, sort_keys=True)+'\n')
    for name in OUTPUTS:
        (out/name).write_bytes((out/'data'/name).read_bytes())
    same = {name: (here/name).read_bytes() == (out/name).read_bytes()
            for name in OUTPUTS if (here/name).exists()}
    assert all(same.values()), same
    result = dict(status='pass', elapsed_seconds=time.monotonic()-start,
                  timings=timings, outputs_byte_identical=same, numerical_threads=1,
                  scientific_trajectories=0, scientific_seeds=[])
    (out/'execution.json').write_text(json.dumps(result, indent=2, sort_keys=True)+'\n')
    print(json.dumps(result), flush=True)


if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--repo', type=Path, default=Path('.'))
    p.add_argument('--out', type=Path, required=True)
    p.add_argument('--seconds', type=int, default=7200)
    a = p.parse_args()
    main(a.repo, a.out, a.seconds)
