#!/usr/bin/env python3
"""Replay published evidence and all new exact checks, serially, without sampling."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def dependency(repo, replay):
    prior = repo / 'research/reports/large-T-20261109/followup/round-0006'
    names = ('dependency.json', 'coefficients.csv', 'components.csv', 'verification.json', 'comparison.json', 'scaling.png')
    same = {name: (prior / name).read_bytes() == (replay / name).read_bytes() for name in names}
    assert all(same.values())
    old = json.loads((replay / 'dependency.json').read_text())
    paths = [prior / name for name in names]
    paths += [prior / name for name in ('coefficient.py', 'verify.py', 'reproduce.py', 'derivation.md', 'memory.md')]
    paths += [repo / name for name in ('AGENTS.md', 'research/PROJECT.md', 'research/EXPERIMENTS.md',
                                      'research/LITERATURE.md', 'research/PAPER_COMPARISON.md',
                                      'research/LARGE_T_THEORY.md', 'research/LARGER_NEIGHBORHOODS_PREREG.md',
                                      'research/reports/large-T-20261109/interpretation.md')]
    return dict(status='mechanically checked; no dependency repair needed',
                method='Complete round-6 reproduction; recursively replays earlier receipts, registration, exact certificates and deterministic checks.',
                round6_outputs_byte_identical=same,
                inherited_replay={key: old[key] for key in ('prior_round3_outputs_byte_identical', 'prior_round4_outputs_byte_identical', 'prior_round5_outputs_byte_identical', 'arithmetic_comparisons')},
                registration_commit=old['registration_commit'],
                original_registration_commit=old['original_registration_commit'],
                original_primary=old['original_primary'], followup_primary=old['followup_primary'],
                followup_arms=old['followup_arms'], original_stage_counts=old['original_stage_counts'],
                original_decision=old['original_decision'],
                followup_seed_count=old['followup_seed_count'], prior_seed_count=old['prior_seed_count'],
                prior_vs_followup_seed_overlap=old['prior_vs_followup_seed_overlap'],
                chronology_limit=old['chronology_limit'],
                inputs_sha256={str(path.relative_to(repo)): sha(path) for path in paths},
                scientific_trajectories=0, scientific_seeds=[],
                scope='Offline published evidence; no unpublished appendix or external theorem is a premise of the asymptotic audit.')


def main(repo, out):
    repo, out = repo.resolve(), out.resolve()
    here = Path(__file__).resolve().parent
    if out.exists():
        raise ValueError('Use a new output directory')
    out.mkdir(parents=True)
    env = os.environ.copy()
    env.update(PYTHONDONTWRITEBYTECODE='1', OPENBLAS_NUM_THREADS='1', OMP_NUM_THREADS='1',
               MKL_NUM_THREADS='1', VECLIB_MAXIMUM_THREADS='1', NUMEXPR_NUM_THREADS='1',
               MPLCONFIGDIR=str(out / 'mpl-cache'))
    def run(args):
        subprocess.run([sys.executable, *map(str, args)], cwd=repo, env=env, check=True)
    prior = repo / 'research/reports/large-T-20261109/followup/round-0006'
    run([prior / 'reproduce.py', '--repo', repo, '--out', out / 'prior'])
    dep = dependency(repo, out / 'prior')
    (out / 'dependency.json').write_text(json.dumps(dep, indent=2, sort_keys=True) + '\n')
    run(['-S', here / 'audit.py', '--repo', repo, '--out', out])
    names = ('dependency.json', 'edges.csv', 'exceptions.csv', 'verification.json')
    same = {name: (here / name).read_bytes() == (out / name).read_bytes() for name in names if (here / name).exists()}
    assert all(same.values()), same
    print(json.dumps(dict(status='pass', byte_identical=same, scientific_trajectories=0), sort_keys=True))


if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--repo', type=Path, default=Path('.'))
    p.add_argument('--out', type=Path, required=True)
    args = p.parse_args()
    main(args.repo, args.out)
