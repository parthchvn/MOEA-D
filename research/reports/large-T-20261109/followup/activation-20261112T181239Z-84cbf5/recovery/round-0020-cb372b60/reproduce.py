#!/usr/bin/env python3
"""Serial reproduction of this bounded independent analytic audit.

Replays published empirical evidence, verifies the directly used theoretical
artifacts, runs prior/new tests, and recomputes the declared exact grid. It
does not claim to rerun every large earlier theoretical grid recursively.
Raw logs and timings stay in the caller's private --out directory.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import signal
import subprocess
import sys
import time

from audit import check_manifest

OUTPUTS = ('words.csv', 'baseline.csv', 'phases.csv', 'entrances.csv',
           'branches.csv', 'verification.json', 'dependency.json')
EMPIRICAL = ('audit.json', 'inputs.json', 'cells.csv', 'phases.csv', 'seeds.csv', 'trials.csv')


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main(repo, out, seconds):
    repo, out = repo.resolve(), out.resolve()
    here = Path(__file__).resolve().parent
    if out.exists():
        raise ValueError('Use a fresh private output directory')
    out.mkdir(parents=True)
    start = time.monotonic()
    stages = []
    env = dict(os.environ, PYTHONDONTWRITEBYTECODE='1', OPENBLAS_NUM_THREADS='1',
               OMP_NUM_THREADS='1', MKL_NUM_THREADS='1', VECLIB_MAXIMUM_THREADS='1',
               NUMEXPR_NUM_THREADS='1', MPLCONFIGDIR=str(out/'mpl-cache'))

    def run(name, args):
        before = time.monotonic()
        remaining = seconds-(before-start)
        if remaining <= 0:
            raise TimeoutError('Deadline exhausted')
        with (out/(name+'.log')).open('w') as f:
            p = subprocess.Popen([sys.executable, *map(str, args)], cwd=repo, env=env,
                                 stdout=f, stderr=subprocess.STDOUT, start_new_session=True)
            try:
                code = p.wait(timeout=remaining)
            except subprocess.TimeoutExpired:
                os.killpg(p.pid, signal.SIGTERM)
                p.wait(timeout=10)
                raise
        log = (out/(name+'.log')).read_text()
        matches = re.findall(r'Ran (\d+) tests?', log)
        stages.append(dict(stage=name, command=list(map(str, args)), returncode=code,
                           elapsed_seconds=time.monotonic()-before,
                           tests=sum(map(int, matches)), log_sha256=sha(out/(name+'.log'))))
        if code:
            raise RuntimeError(f'{name} failed: inspect private log')

    prior = repo/'research/reports/large-T-20261109/followup'
    manifests = {f'round-{n:04d}': len(check_manifest(prior/f'round-{n:04d}')) for n in (18, 19)}
    # This older checkpoint has no self-artifact manifest. Compare its source
    # directly to the committed Git blob, then validate its registered inputs.
    empirical_source = prior/'round-0003/audit.py'
    committed = subprocess.check_output(['git', 'show', 'HEAD:'+str(empirical_source.relative_to(repo))], cwd=repo)
    assert committed == empirical_source.read_bytes()
    run('empirical', [prior/'round-0003/audit.py', '--repo', repo, '--out', out/'empirical'])
    same = {name: (out/'empirical'/name).read_bytes() == (prior/'round-0003'/name).read_bytes() for name in EMPIRICAL}
    assert all(same.values()), same
    evidence = json.loads((out/'empirical/audit.json').read_text())
    assert not evidence['dependency_repair_needed']
    run('prior18-tests', [prior/'round-0018/test_audit.py'])
    run('prior19-tests', [prior/'round-0019/test_rorr.py'])
    run('new-tests', [here/'test_audit.py'])
    run('exact', [here/'audit.py', '--repo', repo, '--out', out/'data'])
    keys = ('original_registration_commit', 'registration_commit', 'original_primary',
            'followup_primary', 'original_stage_counts', 'followup_arms', 'seed_audit',
            'original_decision', 'limitations', 'published_timing')
    dependency = dict(status='mechanically checked; no plan or receipt repair needed',
        method='Fresh round-3 receipt/registration analysis; six outputs byte-identical. Round-18/19 manifests and targeted tests verified; the marked premise is rederived analytically and independently checked on this bounded grid. Full round-18/19 grids are not reexecuted.',
        empirical_outputs_byte_identical=same, empirical_comparisons=evidence['comparison_checks'],
        empirical_source_matches_git=True, empirical_source_sha256=sha(empirical_source),
        theory_manifests_artifacts=manifests,
        sources_sha256={f'round-{n:04d}/{name}': sha(prior/f'round-{n:04d}'/name)
                       for n, names in ((18, ('audit.md', 'audit.py', 'test_audit.py', 'provenance.json')),
                                        (19, ('proof.md', 'rorr.py', 'test_rorr.py', 'provenance.json')))
                       for name in names},
        scientific_seeds=[], scientific_trajectories=0,
        **{k: evidence[k] for k in keys})
    (out/'data/dependency.json').write_text(json.dumps(dependency, indent=2, sort_keys=True)+'\n')
    for name in OUTPUTS:
        (out/name).write_bytes((out/'data'/name).read_bytes())
    output_matches = {name: (here/name).read_bytes() == (out/name).read_bytes()
                      for name in OUTPUTS if (here/name).exists()}
    assert all(output_matches.values()), output_matches
    receipt = dict(status='pass', elapsed_seconds=time.monotonic()-start,
        stages=stages, outputs_byte_identical=output_matches, numerical_threads=1,
        scientific_seeds=[], scientific_trajectories=0)
    (out/'execution.json').write_text(json.dumps(receipt, indent=2, sort_keys=True)+'\n')
    print(json.dumps(receipt), flush=True)


if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--repo', type=Path, default=Path('.'))
    p.add_argument('--out', type=Path, required=True)
    p.add_argument('--seconds', type=int, default=3600)
    a = p.parse_args()
    main(a.repo, a.out, a.seconds)
