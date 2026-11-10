#!/usr/bin/env python3
"""Serial deterministic replay with a hard wall deadline; no RNG or sampling."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import signal
import subprocess
import sys
import time

OUTPUTS = ('centered.csv', 'words.csv', 'flux.csv', 'entrance.csv',
           'verification.json', 'dependency.json')


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def dependency(repo, prior_out):
    prior = repo/'research/reports/large-T-20261109/followup'
    old = json.loads((prior_out/'dependency.json').read_text())
    manifest = json.loads((prior/'round-0016/provenance.json').read_text())
    hashes = {name: sha(prior/'round-0016'/name) == value
              for name, value in manifest['artifacts_sha256'].items()}
    assert all(hashes.values()), hashes
    same = {name: (prior/'round-0016'/name).read_bytes() == (prior_out/name).read_bytes()
            for name in ('rewards.csv', 'stationary.csv', 'words.csv', 'witness.json',
                         'verification.json', 'dependency.json')}
    assert all(same.values()), same
    keep = ('original_registration_commit', 'registration_commit', 'original_primary',
            'followup_primary', 'original_stage_counts', 'followup_arms',
            'prior_seed_count', 'followup_seed_count', 'prior_vs_followup_seed_overlap',
            'original_decision', 'chronology_limit')
    sources = ('round-0014/audit.py', 'round-0014/audit.md', 'round-0015/words.csv',
               'round-0016/audit.py', 'round-0016/audit.md', 'round-0016/reproduce.py')
    return dict(status='mechanically checked; no plan or receipt repair needed',
                method='Full serial round-16 replay, including its recursive earlier registration/receipt verification; relevant source hashes verified before use.',
                round16_outputs_byte_identical=same,
                round16_manifest_sha256=sha(prior/'round-0016/provenance.json'),
                round16_manifest_artifacts=len(hashes),
                sources_sha256={name: sha(prior/name) for name in sources},
                premises='Audited clean geometry and acceptance factors; new centered identity independently compared to published phase/sweep solvers at n=4. No isolated-pair second-response candidate or positive-p global Schur theorem is used.',
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
            raise RuntimeError(f'{name} failed; inspect private log')

    prior = repo/'research/reports/large-T-20261109/followup/round-0016'
    run('prior', [prior/'reproduce.py', '--repo', repo, '--out', out/'prior',
                  '--seconds', max(1, int(seconds))])
    dep = dependency(repo, out/'prior')
    run('centered', [here/'centered.py', '--repo', repo, '--out', out/'data'])
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
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--repo', type=Path, default=Path('.'))
    parser.add_argument('--out', type=Path, required=True)
    parser.add_argument('--seconds', type=int, default=1800)
    args = parser.parse_args()
    main(args.repo, args.out, args.seconds)
