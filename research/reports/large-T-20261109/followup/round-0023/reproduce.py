"""Serial analysis-only replay into a new scratch directory.

Usage: PYTHON reproduce.py --repo REPO --out NEW_DIRECTORY [--check-published]
No engine/simulation entry point is called. Repository tests include only
their existing fixed fixtures. All numerical libraries are forced to one thread.
"""
import argparse
from datetime import datetime,timezone
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
GENERATED=('global.csv','occupation.csv','certificates.csv','clean.csv',
           'coefficients.csv','witnesses.json','verification.json','empirical.json')
SOURCES=('audit.py','receipts.py','verify.py','test_audit.py','reproduce.py')
INPUTS=('AGENTS.md','research/PROJECT.md','research/CLAIMS.md','research/STATUS.md',
        'research/EXPERIMENTS.md','research/PAPER_COMPARISON.md','research/LARGE_T_THEORY.md',
        'research/LITERATURE.md','scripts/neighborhood_sweep.cpp',
        'research/reports/large-T-20261109/followup/round-0021/proof.md',
        'research/reports/large-T-20261109/followup/round-0021/structure.py',
        'research/reports/large-T-20261109/followup/round-0021/response.py',
        'research/reports/large-T-20261109/followup/round-0021/coefficients.csv',
        'research/reports/large-T-20261109/followup/round-0022/proof.md',
        'research/reports/large-T-20261109/followup/round-0022/excursions.py',
        'research/reports/large-T-20261109/followup/round-0022/certificates.csv',
        'research/reports/large-T-20261109/followup/round-0022/cells.csv',
        'research/reports/large-T-20261109/followup/activation-20261112T181239Z-84cbf5/GOAL.md',
        'research/reports/large-T-20261109/followup/activation-20261112T181239Z-84cbf5/RECOVERY.json')


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def git(repo,*args):
    return subprocess.check_output(['git','-C',str(repo),*args],text=True).strip()


def run(repo,out,compare):
    if out.exists() or out.resolve()==BUNDLE:
        raise ValueError('choose a new scratch output directory')
    out.mkdir(parents=True)
    start=time.monotonic()
    began=datetime.now(timezone.utc).isoformat()
    head=git(repo,'rev-parse','HEAD')
    assert not git(repo,'diff','--name-only','HEAD')
    initial_status=git(repo,'status','--porcelain')
    input_hashes={p:sha(repo/p) for p in INPUTS}
    sources={p:sha(BUNDLE/p) for p in SOURCES}
    env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1',OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1',
             MKL_NUM_THREADS='1',VECLIB_MAXIMUM_THREADS='1',NUMEXPR_NUM_THREADS='1')
    commands=[]
    def call(args,display):
        tick=time.monotonic()
        result=subprocess.run([sys.executable,*map(str,args)],cwd=repo,env=env,
            stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True,timeout=300)
        entry=dict(command=display,exit_code=result.returncode,elapsed_seconds=time.monotonic()-tick)
        tests=re.search(r'Ran (\d+) tests',result.stdout)
        if tests:
            entry['tests']=int(tests.group(1))
        commands.append(entry)
        if result.returncode:
            print(result.stdout)
            (out/'failed.json').write_text(json.dumps(dict(commands=commands),indent=2)+'\n')
            raise RuntimeError(display)
        return result.stdout
    call(['-m','unittest','discover','-s','tests','-v'],'PYTHON -m unittest discover -s tests -v')
    call(['-m','unittest','discover','-s',BUNDLE,'-p','test_audit.py','-v'],
         'PYTHON -m unittest discover -s BUNDLE -p test_audit.py -v')
    with tempfile.TemporaryDirectory(prefix='moead-round23-compile-') as cache:
        env['PYTHONPYCACHEPREFIX']=cache
        call(['-m','py_compile','sim.py','large.py','scripts/run_research.py',*[BUNDLE/p for p in SOURCES]],
             'PYTHON -m py_compile sim.py large.py scripts/run_research.py BUNDLE/{audit,receipts,verify,test_audit,reproduce}.py')
        del env['PYTHONPYCACHEPREFIX']
    verification=json.loads(call([BUNDLE/'audit.py','--repo',repo,'--out',out],
                                 'PYTHON BUNDLE/audit.py --repo REPO --out OUTPUT'))
    empirical=json.loads(call([BUNDLE/'receipts.py','--repo',repo,'--out',out/'empirical.json'],
                              'PYTHON BUNDLE/receipts.py --repo REPO --out OUTPUT/empirical.json'))
    certificate=json.loads(call([BUNDLE/'verify.py','--bundle',out],
                                'PYTHON BUNDLE/verify.py --bundle OUTPUT'))
    identical=[]
    if compare:
        for p in GENERATED:
            assert (out/p).read_bytes()==(BUNDLE/p).read_bytes(),p
            identical.append(p)
    assert head==git(repo,'rev-parse','HEAD')
    assert not git(repo,'diff','--name-only','HEAD')
    assert input_hashes=={p:sha(repo/p) for p in INPUTS}
    assert sources=={p:sha(BUNDLE/p) for p in SOURCES}
    result=dict(started_utc=began,finished_utc=datetime.now(timezone.utc).isoformat(),
        elapsed_seconds=time.monotonic()-start,head=head,tracked_dirty_before=False,tracked_dirty_after=False,
        status_before=initial_status.splitlines(),status_after=git(repo,'status','--porcelain').splitlines(),
        interpreter=sys.executable,python=sys.version,
        numerical_threads={k:env[k] for k in ('OPENBLAS_NUM_THREADS','OMP_NUM_THREADS','MKL_NUM_THREADS',
            'VECLIB_MAXIMUM_THREADS','NUMEXPR_NUM_THREADS')},commands=commands,
        input_hashes=input_hashes,bundle_source_hashes=sources,
        output_hashes={p:sha(out/p) for p in GENERATED},byte_identical_outputs=identical,
        verification=verification,empirical=empirical,certificate_verification=certificate,
        model='unchanged pinned model; literal-cost independent implementation; boundary stopping',
        research_samples=0,research_seeds=[],censoring='none in deterministic work; existing censored/missing receipts retained',
        finite_caps=dict(max_complete_phase_states_per_cell=1023,max_literal_mask_n=8,
                         max_polynomial_degree=2,command_timeout_seconds=300),paid_cost=0)
    (out/'checks.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
    print(json.dumps(dict(elapsed_seconds=result['elapsed_seconds'],tests=sum(c.get('tests',0) for c in commands),
        reproduced_outputs=len(identical),global_phase_states=verification['global_phase_states'],
        certificate_phase_states=certificate['phase_states']),indent=2))


if __name__=='__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('--repo',type=Path,required=True)
    parser.add_argument('--out',type=Path,required=True)
    parser.add_argument('--check-published',action='store_true')
    args=parser.parse_args()
    run(args.repo.resolve(),args.out.resolve(),args.check_published)
