#!/usr/bin/env python3
"""Bounded serial reproduction, with no recursive historical-grid replay.

Use the configured Python to run this script. --repo identifies the repository;
--out must be a fresh scratch directory. Current published round-18/19 manifests
and recovery hashes are checked before any exact response reuse. No RNG study.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import time


def main(repo, out, seconds):
    repo, out = repo.resolve(), out.resolve()
    here = Path(__file__).resolve().parent
    if out.exists():
        raise ValueError('--out must be fresh')
    out.mkdir(parents=True)
    start = time.monotonic()
    env = dict(os.environ, PYTHONDONTWRITEBYTECODE='1', OPENBLAS_NUM_THREADS='1',
               OMP_NUM_THREADS='1', MKL_NUM_THREADS='1', VECLIB_MAXIMUM_THREADS='1',
               NUMEXPR_NUM_THREADS='1', PYTHONPYCACHEPREFIX=str(out/'cache'),
               MPLCONFIGDIR=str(out/'mpl-cache'))
    stages=[]
    def run(name, args):
        before=time.monotonic()
        remaining=seconds-(before-start)
        if remaining<=0: raise TimeoutError('Reproduction budget exhausted')
        with (out/(name+'.log')).open('w') as log:
            p=subprocess.run([sys.executable,*map(str,args)],cwd=repo,env=env,
                             stdout=log,stderr=subprocess.STDOUT,timeout=remaining)
        content=(out/(name+'.log')).read_bytes()
        stages.append(dict(stage=name,returncode=p.returncode,
            elapsed_seconds=time.monotonic()-before,
            tests=sum(map(int,re.findall(rb'Ran (\d+) tests?',content))),
            log_sha256=hashlib.sha256(content).hexdigest()))
        if p.returncode:
            raise RuntimeError(f'{name} failed; inspect its scratch log')
    run('recovery-and-support',[here/'check.py','--repo',repo,'--out',out])
    run('recovered-tests',[here/'test_recovered.py'])
    run('repository-tests',['-m','unittest','discover','-s','tests','-v'])
    run('compile',['-m','py_compile',repo/'sim.py',repo/'large.py',repo/'scripts/run_research.py',
                   here/'audit.py',here/'check.py',here/'test_recovered.py',here/'reproduce.py'])
    run('exact',[here/'audit.py','--repo',repo,'--out',out,'--ns','4'])
    outputs=('targeted.json','verification.json','words.csv','baseline.csv','phases.csv','entrances.csv','branches.csv')
    same={name:(here/name).read_bytes()==(out/name).read_bytes() for name in outputs if (here/name).exists()}
    assert all(same.values()),same
    receipt=dict(status='pass',stages=stages,outputs_byte_identical=same,
                 elapsed_seconds=time.monotonic()-start,numerical_threads=1,
                 scientific_trajectories=0,scientific_seeds=[],
                 scope='Only this bounded grid and tests. Earlier full grids and empirical bootstraps are not recursively replayed.')
    (out/'execution.json').write_text(json.dumps(receipt,indent=2,sort_keys=True)+'\n')
    print(json.dumps(receipt))

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--repo',type=Path,required=True)
    p.add_argument('--out',type=Path,required=True)
    p.add_argument('--seconds',type=int,default=1800)
    a=p.parse_args()
    main(a.repo,a.out,a.seconds)
