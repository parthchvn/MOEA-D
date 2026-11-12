#!/usr/bin/env python3
"""Serial deterministic regeneration, including published dependency replay.

Requires the offline repository, NumPy and Matplotlib. It never invokes a
scientific sampler. Select a new --out directory outside the publication bundle.
"""
import argparse
from fractions import Fraction as F
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys


def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()


def dependency(repo,replay):
    r5=repo/'research/reports/large-T-20261109/followup/round-0005'
    names=('dependency.json','expectations.csv','certificates.csv','verification.json','forest.json')
    same={name:(r5/name).read_bytes()==(replay/name).read_bytes() for name in names}
    assert all(same.values())
    old=json.loads((replay/'dependency.json').read_text())
    witness=json.loads((replay/'verification.json').read_text())['witnesses']['expected_monotonicity']
    assert F(witness['larger_minus_smaller_sweeps_lower'])>0
    return dict(status='mechanically checked; no dependency repair needed',
        method='Replayed round-5 reproduction, including rounds 4 and 3, original receipts and committed round-1 registration.',
        prior_round5_outputs_byte_identical=same,
        prior_round4_outputs_byte_identical=old['prior_round4_outputs_byte_identical'],
        prior_round3_outputs_byte_identical=old['prior_round3_outputs_byte_identical'],
        arithmetic_comparisons=old['arithmetic_comparisons'],
        registration_commit=old['registration_commit'],
        original_registration_commit=old['original_registration_commit'],
        original_primary=old['original_primary'],followup_primary=old['followup_primary'],
        followup_arms=old['followup_arms'],
        original_stage_counts=old['original_stage_counts'],original_decision=old['original_decision'],
        followup_seed_count=old['followup_seed_count'],prior_seed_count=old['prior_seed_count'],
        prior_vs_followup_seed_overlap=0,
        round5_slowdown=witness,
        inputs_sha256={str(p.relative_to(repo)):sha(p) for p in [r5/'audit.py',r5/'verify.py',r5/'audit.md',
            r5/'verification.json',r5/'reproduce.py',repo/'research/LARGE_T_THEORY.md',
            repo/'research/LARGER_NEIGHBORHOODS_PREREG.md',
            repo/'research/reports/large-T-20261109/interpretation.md']},
        chronology_limit=old['chronology_limit'],
        scientific_trajectories_generated=0,scientific_seeds=[],
        scope='Offline published evidence only. No unavailable manuscript appendix or new theorem transfer is used.')


def comparison(dep,verification):
    witness=dep['round5_slowdown'];a=F(verification['gap']);p=F(1,192)
    low=F(witness['larger_minus_smaller_sweeps_lower']);high=F(witness['larger_minus_smaller_sweeps_upper'])
    return dict(status='exact comparison to previously certified finite-p interval',n=3,p=str(p),
        derivative=str(a),linear_prediction=str(p*a),linear_prediction_decimal=float(p*a),
        published_gap_lower=str(low),published_gap_upper=str(high),
        remainder_lower=str(low-p*a),remainder_upper=str(high-p*a),
        remainder_lower_decimal=float(low-p*a),remainder_upper_decimal=float(high-p*a),
        interpretation='A finite-p remainder, not sampling error; does not bound the Taylor remainder uniformly in n.')


def main(repo,out):
    repo,out=repo.resolve(),out.resolve();here=Path(__file__).resolve().parent
    if out.exists():raise ValueError('Use a new output directory')
    out.mkdir(parents=True)
    env=os.environ.copy()
    env.update(PYTHONDONTWRITEBYTECODE='1',OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1',
               MKL_NUM_THREADS='1',VECLIB_MAXIMUM_THREADS='1',NUMEXPR_NUM_THREADS='1')
    def run(args):subprocess.run([sys.executable,*map(str,args)],cwd=repo,env=env,check=True)
    run([repo/'research/reports/large-T-20261109/followup/round-0005/reproduce.py',
         '--repo',repo,'--out',out/'prior'])
    dep=dependency(repo,out/'prior')
    (out/'dependency.json').write_text(json.dumps(dep,indent=2,sort_keys=True)+'\n')
    run([here/'coefficient.py','--out',out])
    run(['-S',here/'verify.py','--bundle',out,'--out',out/'verification.json'])
    comp=comparison(dep,json.loads((out/'verification.json').read_text()))
    (out/'comparison.json').write_text(json.dumps(comp,indent=2,sort_keys=True)+'\n')
    run([here/'plot.py','--bundle',out])
    names=('dependency.json','coefficients.csv','components.csv','verification.json','comparison.json','scaling.png')
    same={name:(here/name).read_bytes()==(out/name).read_bytes() for name in names if (here/name).exists()}
    if not all(same.values()):raise AssertionError(f'Output mismatch: {same}')
    print(json.dumps(dict(status='pass',byte_identical=same,scientific_trajectories=0),sort_keys=True))


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--repo',type=Path,default=Path('.'));p.add_argument('--out',type=Path,required=True)
    args=p.parse_args();main(args.repo,args.out)
