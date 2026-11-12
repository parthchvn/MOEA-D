#!/usr/bin/env python3
"""Reproduce this audit and recheck its committed dependencies; no sampler.

Use a fresh --out directory outside the publication bundle. All subprocesses
are serial, and linear-algebra thread counts are limited to one.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def dependency(repo, prior):
    r4=repo/'research/reports/large-T-20261109/followup/round-0004'
    old=json.loads((prior/'dependency.json').read_text())
    verified=old['verified']
    names=('kernels.csv','bounds.csv','verification.json','dependency.json')
    matches={name:(r4/name).read_bytes()==(prior/name).read_bytes() for name in names}
    assert all(matches.values())
    return dict(status='mechanically checked; no dependency repair needed',
        method='Replayed round-4 checker and round-3 independent receipt auditor before relying on evidence',
        proof_sha256=sha(r4/'proof.md'),checker_sha256=sha(r4/'check.py'),
        prior_round4_outputs_byte_identical=matches,
        prior_round3_outputs_byte_identical=old['prior_outputs_byte_identical'],
        input_sha256={str(p.relative_to(repo)):sha(p) for p in
                     [r4/'proof.md',r4/'check.py',
                      repo/'research/reports/large-T-20261109/followup/round-0001/plan.json',
                      repo/'research/LARGER_NEIGHBORHOODS_PREREG.md',
                      repo/'research/reports/large-T-20261109/interpretation.md']},
        registration_commit=verified['registration_commit'],
        original_registration_commit=verified['original_registration_commit'],
        arithmetic_comparisons=verified['comparison_checks'],
        original_primary=verified['original_primary'],followup_primary=verified['followup_primary'],
        original_stage_counts=verified['original_stage_counts'],original_decision=verified['original_decision'],
        followup_arms={t:{k:arm[k] for k in ('planned','receipts','missing','means','quantiles','phases')}
                       for t,arm in verified['followup_arms'].items()},
        followup_seed_count=verified['seed_audit']['new_unique'],
        prior_seed_count=verified['seed_audit']['prior_unique'],
        prior_vs_followup_seed_overlap=0,
        revised_T3_appendix_used=False,scientific_trajectories_generated=0,
        chronology_limit='Published receipts verify committed registration and aggregate execution timing; private trial logs are unavailable.')


def main(repo,out):
    repo,out=repo.resolve(),out.resolve()
    here=Path(__file__).resolve().parent
    if out.exists(): raise ValueError('Use a new output directory')
    out.mkdir(parents=True)
    env=os.environ.copy()
    env.update(PYTHONDONTWRITEBYTECODE='1',OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1',
               MKL_NUM_THREADS='1',VECLIB_MAXIMUM_THREADS='1',NUMEXPR_NUM_THREADS='1')
    def run(command):
        subprocess.run([sys.executable,*command],env=env,cwd=repo,check=True)
    run([str(repo/'research/reports/large-T-20261109/followup/round-0004/reproduce.py'),
         '--repo',str(repo),'--out',str(out/'prior')])
    dep=dependency(repo,out/'prior')
    (out/'dependency.json').write_text(json.dumps(dep,indent=2,sort_keys=True)+'\n')
    run([str(here/'audit.py'),'--out',str(out)])
    run(['-S',str(here/'verify.py'),'--bundle',str(out)])
    run([str(here/'forest.py'),'--out',str(out/'forest.json')])
    matches={name:(here/name).read_bytes()==(out/name).read_bytes()
             for name in ('dependency.json','expectations.csv','certificates.csv','verification.json','forest.json')
             if (here/name).exists()}
    if not all(matches.values()):
        raise AssertionError(f'Output mismatch: {matches}; portable exact certificate verification is available separately')
    print(json.dumps(dict(status='pass',byte_identical=matches,scientific_trajectories=0),sort_keys=True))


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--repo',type=Path,default=Path('.'))
    parser.add_argument('--out',type=Path,required=True)
    args=parser.parse_args()
    main(args.repo,args.out)
