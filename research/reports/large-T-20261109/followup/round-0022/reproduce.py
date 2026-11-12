"""Serial bounded replay, exact checks, tests, and source-integrity receipt.

From this bundle: /path/to/python reproduce.py --repo /path/to/repo --out /tmp/new
The output must be a new directory outside this bundle. No scientific sampling.
"""
import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import tempfile
import time

BUNDLE=Path(__file__).resolve().parent
GENERATED=('bounds.csv','cells.csv','certificates.csv','traps.csv','verification.json','witness.json')
SOURCE_INPUTS=(
    'AGENTS.md','research/PROJECT.md','research/CLAIMS.md','research/STATUS.md',
    'research/EXPERIMENTS.md','research/PAPER_COMPARISON.md','research/LARGE_T_THEORY.md',
    'research/LITERATURE.md','scripts/neighborhood_sweep.cpp',
    'research/reports/large-T-20261109/followup/round-0004/proof.md',
    'research/reports/large-T-20261109/followup/round-0005/audit.md',
    'research/reports/large-T-20261109/followup/round-0012/audit.md',
    'research/reports/large-T-20261109/followup/round-0020/HISTORY.md',
    'research/reports/large-T-20261109/followup/round-0021/proof.md',
    'research/reports/large-T-20261109/followup/round-0021/structure.py',
    'research/reports/large-T-20261109/followup/activation-20261112T181239Z-84cbf5/GOAL.md',
    'research/reports/large-T-20261109/followup/activation-20261112T181239Z-84cbf5/RECOVERY.json')


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def git(repo,*args):
    return subprocess.check_output(['git','-C',str(repo),*args],text=True).strip()


def run(repo,out,compare):
    if out.exists() or out.resolve()==BUNDLE:
        raise ValueError('output must be a new scratch directory, not this bundle')
    out.mkdir(parents=True)
    start=time.monotonic()
    began=datetime.now(timezone.utc).isoformat()
    before_head=git(repo,'rev-parse','HEAD')
    before_diff=git(repo,'diff','--name-only','HEAD')
    if before_diff:
        raise ValueError('tracked inputs must be clean for this replay')
    before_status=git(repo,'status','--porcelain')
    inputs={name:digest(repo/name) for name in SOURCE_INPUTS}
    sources={name:digest(BUNDLE/name) for name in ('excursions.py','verify.py','test_excursions.py','reproduce.py')}
    env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1',OPENBLAS_NUM_THREADS='1',
             OMP_NUM_THREADS='1',MKL_NUM_THREADS='1',VECLIB_MAXIMUM_THREADS='1',
             NUMEXPR_NUM_THREADS='1')
    commands=[]
    def call(args,cwd,display):
        tick=time.monotonic()
        result=subprocess.run([sys.executable,*map(str,args)],cwd=cwd,env=env,
                              stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True,timeout=300)
        item=dict(command=display,exit_code=result.returncode,elapsed_seconds=time.monotonic()-tick)
        match=re.search(r'Ran (\d+) tests',result.stdout)
        if match:
            item['tests']=int(match.group(1))
        commands.append(item)
        if result.returncode:
            print(result.stdout)
            raise RuntimeError(display)
        return result.stdout
    call(['-m','unittest','discover','-s','tests','-v'],repo,
         'PYTHON -m unittest discover -s tests -v')
    call(['-m','unittest','discover','-s',str(BUNDLE),'-p','test_excursions.py','-v'],repo,
         'PYTHON -m unittest discover -s BUNDLE -p test_excursions.py -v')
    # py_compile always writes; give it a temporary pycache prefix.
    with tempfile.TemporaryDirectory(prefix='moead-round22-pycache-') as cache:
        env['PYTHONPYCACHEPREFIX']=cache
        call(['-m','py_compile','sim.py','large.py','scripts/run_research.py',
              *[BUNDLE/name for name in ('excursions.py','verify.py','test_excursions.py','reproduce.py')]],
             repo,'PYTHON -m py_compile sim.py large.py scripts/run_research.py BUNDLE/{excursions,verify,test_excursions,reproduce}.py')
        del env['PYTHONPYCACHEPREFIX']
    generated_stdout=call([BUNDLE/'excursions.py','--out',out],repo,
                          'PYTHON BUNDLE/excursions.py --out OUTPUT')
    verification=json.loads(generated_stdout)
    literal=json.loads(call([BUNDLE/'verify.py','--bundle',out],repo,
                            'PYTHON BUNDLE/verify.py --bundle OUTPUT'))
    reproduced=[]
    if compare:
        for name in GENERATED:
            assert (out/name).read_bytes()==(BUNDLE/name).read_bytes(),name
            reproduced.append(name)
    assert git(repo,'rev-parse','HEAD')==before_head
    assert git(repo,'diff','--name-only','HEAD')==before_diff
    assert git(repo,'status','--porcelain')==before_status
    assert inputs=={name:digest(repo/name) for name in SOURCE_INPUTS}
    receipt=dict(started_utc=began,finished_utc=datetime.now(timezone.utc).isoformat(),
                 elapsed_seconds=time.monotonic()-start,head=before_head,
                 tracked_dirty_before=False,tracked_dirty_after=False,
                 porcelain_unchanged=True,source_hashes=inputs,bundle_source_hashes=sources,
                 python=sys.version,interpreter=sys.executable,
                 numerical_threads={key:env[key] for key in ('OPENBLAS_NUM_THREADS','OMP_NUM_THREADS','MKL_NUM_THREADS',
                                                            'VECLIB_MAXIMUM_THREADS','NUMEXPR_NUM_THREADS')},
                 commands=commands,verification=verification,literal_verifier=literal,
                 byte_identical_outputs=reproduced,
                 output_hashes={name:digest(out/name) for name in GENERATED},
                 research_samples=0,research_seeds=[],censoring='not applicable: no Monte Carlo; all finite enumerations complete',
                 model='unchanged cyclic own-parent, filled T, shared activated bitwise noise; pinned excursion stopping is analytical only',
                 limits=dict(max_phase_states=324,exact_gaussian_states=24,command_wall_seconds=300),
                 protected_inputs=len(inputs),paid_cost=0)
    (out/'checks.json').write_text(json.dumps(receipt,indent=2,sort_keys=True)+'\n')
    print(json.dumps(dict(elapsed_seconds=receipt['elapsed_seconds'],tests=sum(c.get('tests',0) for c in commands),
                         byte_identical_outputs=len(reproduced),verification=verification),indent=2))


if __name__=='__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('--repo',type=Path,required=True)
    parser.add_argument('--out',type=Path,required=True)
    parser.add_argument('--check-published',action='store_true')
    args=parser.parse_args()
    run(args.repo.resolve(),args.out.resolve(),args.check_published)
