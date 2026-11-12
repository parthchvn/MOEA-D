"""Serial deterministic replay. Invoke with the configured Python, not `python`."""
import argparse
import csv
from datetime import datetime, timezone
from fractions import Fraction
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import time

HERE=Path(__file__).resolve().parent
OUTPUTS=('geometry.csv','repair.csv','traps.csv','forest.csv','verification.json','coefficients.csv')
RELEVANT=('AGENTS.md','research/PROJECT.md','research/CLAIMS.md','research/STATUS.md',
          'research/EXPERIMENTS.md','research/PAPER_COMPARISON.md','research/LARGE_T_THEORY.md',
          'research/LITERATURE.md','scripts/neighborhood_sweep.cpp',
          'research/reports/large-T-20261109/followup/round-0005/audit.md',
          'research/reports/large-T-20261109/followup/round-0010/proof.md',
          'research/reports/large-T-20261109/followup/round-0012/audit.md',
          'research/reports/large-T-20261109/followup/round-0015/proof.md',
          'research/reports/large-T-20261109/followup/round-0020/audit.md',
          'research/reports/large-T-20261109/followup/round-0008/coefficients.csv',
          'research/reports/large-T-20261109/followup/activation-20261112T181239Z-84cbf5/GOAL.md',
          'research/reports/large-T-20261109/followup/activation-20261112T181239Z-84cbf5/RECOVERY.json')


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def protected(repo):
    files=subprocess.check_output(['git','ls-files','-z'],cwd=repo).decode().split('\0')
    out={}
    for name in filter(None,files):
        path=repo/name
        data=os.readlink(path).encode() if path.is_symlink() else path.read_bytes()
        out[name]=hashlib.sha256(data).hexdigest()
    return out


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--repo',type=Path,required=True)
    parser.add_argument('--out',type=Path,required=True)
    parser.add_argument('--check-published',action='store_true')
    args=parser.parse_args()
    repo,out=args.repo.resolve(),args.out.resolve()
    if out==HERE:
        raise ValueError('replay output must be a separate directory')
    out.mkdir(parents=True,exist_ok=True)
    start=time.monotonic()
    before=protected(repo)
    head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=repo,text=True).strip()
    dirty=subprocess.check_output(['git','status','--porcelain'],cwd=repo,text=True).splitlines()
    env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1',OPENBLAS_NUM_THREADS='1',
             OMP_NUM_THREADS='1',MKL_NUM_THREADS='1',NUMEXPR_NUM_THREADS='1',
             VECLIB_MAXIMUM_THREADS='1',PYTHONPYCACHEPREFIX=str(out/'cache'))
    commands=[]
    def call(argv,cwd=repo):
        t=time.monotonic()
        result=subprocess.run(argv,cwd=cwd,env=env,text=True,capture_output=True)
        if result.returncode:
            print(result.stdout+result.stderr)
            raise RuntimeError(f'command failed: {argv[1:]}')
        output=result.stdout+result.stderr
        test=re.search(r'Ran (\d+) tests?',output)
        commands.append(dict(program=Path(argv[0]).name,args=[str(x) for x in argv[1:]],
                             elapsed_seconds=time.monotonic()-t,exit_code=0,
                             tests=int(test.group(1)) if test else None))
        return output
    call([sys.executable,str(HERE/'test_structure.py')])
    call([sys.executable,'-m','unittest','discover','-s','tests','-v'])
    call([sys.executable,'-m','py_compile','sim.py','large.py','scripts/run_research.py',
          *[str(HERE/name) for name in ('structure.py','response.py','test_structure.py','reproduce.py')]])
    call([sys.executable,str(HERE/'structure.py'),'--out',str(out)])
    call([sys.executable,str(HERE/'response.py'),'--out',str(out)])
    old=repo/'research/reports/large-T-20261109/followup/round-0008/coefficients.csv'
    prior=next(r for r in csv.DictReader(old.open()) if r['n']=='3' and r['T']=='3')
    fresh=[r for r in csv.DictReader((out/'coefficients.csv').open()) if r['n']=='3' and r['T']=='3']
    for r,name in zip(fresh,('mean0','first','second')):
        assert Fraction(r['coefficient'])==Fraction(prior[name])
    if args.check_published:
        for name in OUTPUTS:
            assert (HERE/name).read_bytes()==(out/name).read_bytes(),name
    after=protected(repo)
    assert before==after
    assert head==subprocess.check_output(['git','rev-parse','HEAD'],cwd=repo,text=True).strip()
    # Keep public commands portable: redact checkout/scratch absolute prefixes.
    for c in commands:
        c['args']=[s.replace(str(HERE),'BUNDLE').replace(str(out),'OUTPUT') for s in c['args']]
    receipt=dict(status='passed',utc=datetime.now(timezone.utc).isoformat(),
        elapsed_seconds=time.monotonic()-start,python=sys.version.split()[0],
        git_commit=head,initial_git_status=dirty,commands=commands,
        protected_tracked_files=len(before),protected_files_unchanged=True,
        protected_hashset_sha256=hashlib.sha256(json.dumps(before,sort_keys=True).encode()).hexdigest(),
        prior_exact_coefficients_matched=3,byte_identical_outputs=len(OUTPUTS) if args.check_published else 0,
        output_sha256={name:sha(out/name) for name in OUTPUTS},
        relevant_source_sha256={name:sha(repo/name) for name in RELEVANT},
        model_config=dict(neighborhood='frozen filled cardinality',parent='cyclic own-parent',
            mutation='standard bit 1/n',reference='supplied ideal',labels='pinned target',
            noise='p=0 for clean results; activated bitwise for response and entrance',
            stopping='simultaneous true alignment at full sweep boundaries',
            closure_cap=256,phase_state_cap=1024,logarithm='natural',seeds=[],
            sampling='none',censoring='not applicable; finite exact computations'),
        paid_cost=0,parallel_agents=0,holdout='240 original observations remain blocked; not sampled')
    (out/'checks.json').write_text(json.dumps(receipt,indent=2)+'\n')
    print(json.dumps({k:receipt[k] for k in ('status','elapsed_seconds','protected_tracked_files',
                      'prior_exact_coefficients_matched','byte_identical_outputs')},indent=2))


if __name__=='__main__':
    main()
