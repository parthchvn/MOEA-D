"""Independent analysis-only receipt audit; never calls an experiment runner.

Replays only registered bootstrap resamples of existing n=512 observations.
Reads relevant original campaign packets in memory without extracting files.
"""
import argparse
from datetime import datetime
from fractions import Fraction as F
import hashlib
import json
from pathlib import Path
import subprocess
import tarfile


BASE=Path('research/reports/large-T-20261109/followup')


def digest(value):
    return hashlib.sha256(json.dumps(value,sort_keys=True,separators=(',',':'),allow_nan=False).encode()).hexdigest()


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def validate(row,planned,manifest):
    assert all(row[k]==v for k,v in planned.items())
    assert row['record_sha256']==digest({k:v for k,v in row.items() if k!='record_sha256'})
    assert all(row[k]==manifest[k] for k in ('plan_sha256','model_sha256'))
    n,m,h=row['n'],row['n']+1,row['max_sweeps']
    assert 0<=row['sweeps']<=h
    assert row['attempts']==m*row['sweeps']
    assert row['comparisons']==row['T']*row['attempts']
    assert row['init_evals']==(0 if row['init']=='corner' else m)
    for event in ('exact_sweep','post_sweep','U','S','archive_sweep','front_sweep'):
        v=row[event]
        assert v is None or (type(v) is int and 0<=v<=row['sweeps'])
    for a,b in (('U','S'),('S','post_sweep'),('exact_sweep','post_sweep'),
                ('archive_sweep','front_sweep'),('front_sweep','exact_sweep')):
        if row[b] is not None:
            assert row[a] is not None and row[a]<=row[b]
    if row['post_sweep'] is not None:
        assert row['sweeps']==row['post_sweep']
    else:
        assert row['sweeps']==h


def read_campaign(repo):
    folder=repo/'research/evidence/large-T-20261109/campaign'
    index=json.loads((folder/'INDEX.json').read_text())
    stages={}
    hashes={str((folder/'INDEX.json').relative_to(repo)):sha(folder/'INDEX.json')}
    for entry in index['stages']:
        path=folder/entry['file']
        assert sha(path)==entry['sha256'] and path.stat().st_size==entry['bytes']
        hashes[str(path.relative_to(repo))]=sha(path)
        # Read only manifest/status/receipt JSON, not unrelated source members.
        documents={}
        with tarfile.open(path,'r:gz') as archive:
            for member in archive:
                if member.name in ('manifest.json','status.json') or member.name.startswith('rows/'):
                    assert member.isfile() and member.size<1_000_000 and member.name not in documents
                    documents[member.name]=json.loads(archive.extractfile(member).read())
        manifest=documents['manifest.json']
        assert digest(manifest['plan'])==entry['plan_sha256']==manifest['plan_sha256']
        assert digest([manifest['model_version'],manifest['sources'],manifest['toolchain']])==manifest['model_sha256']
        planned={r['id']:r for r in manifest['plan']}
        records={r['id']:r for name,r in documents.items() if name.startswith('rows/')}
        assert len(records)==entry['recorded'] and len(planned)-len(records)==entry['missing']
        for ident,row in records.items():
            validate(row,planned[ident],manifest)
        stages[entry['stage']]=(manifest,records,documents['status.json'])
    return stages,hashes


def run(repo,out):
    import numpy as np
    folder=repo/BASE/'round-0002'
    design=json.loads((folder/'plan.json').read_text())
    manifest=json.loads((folder/'manifest.json').read_text())
    registration=json.loads((folder/'registration.json').read_text())
    published=json.loads((folder/'summary.json').read_text())
    assert digest(design['plan'])==design['plan_sha256']==manifest['plan_sha256']
    assert manifest['plan']==design['plan']
    assert digest([manifest['study'],manifest['sources'],manifest['toolchain']])==manifest['model_sha256']
    assert sha(repo/design['engine'])==design['engine_sha256']
    registration_commit=registration['registration_commit']
    subprocess.run(['git','-C',str(repo),'merge-base','--is-ancestor',registration_commit,'HEAD'],check=True)
    # Verify actual registered bytes in the local object database, not its verdict.
    for name,expected in registration['file_sha256'].items():
        source=str(BASE/'round-0001'/name)
        body=subprocess.check_output(['git','-C',str(repo),'show',registration_commit+':'+source])
        assert hashlib.sha256(body).hexdigest()==expected==sha(repo/source)
    commit_time=subprocess.check_output(['git','-C',str(repo),'show','-s','--format=%cI',registration_commit],text=True).strip()
    assert datetime.fromisoformat(commit_time)<datetime.fromisoformat(manifest['started_utc'])
    records={}
    for path in sorted((folder/'rows').glob('*.json')):
        row=json.loads(path.read_text())
        assert row['id']==path.stem and path.stem not in records
        records[path.stem]=row
    assert len(records)==len(design['plan'])==68
    for planned in design['plan']:
        validate(records[planned['id']],planned,manifest)
    primary=design['primary']
    data,bootstrap,arms={}, {}, {}
    for t in (1,23):
        rows=sorted((r for r in records.values() if r['stage']=='main' and r['T']==t),key=lambda r:r['rep'])
        assert len(rows)==32 and [r['rep'] for r in rows]==list(range(32))
        h=primary['cap_sweeps']
        vectors=[]
        for r in rows:
            x,u,s,z=[h if r[k] is None else min(r[k],h) for k in ('exact_sweep','U','S','post_sweep')]
            a,b,c,g=u,s-u,z-s,z-x
            restricted=513*(1+x)
            assert restricted==513*(1+a+b+c-g)
            vectors.append((restricted,a,b,c,g))
        values=np.asarray(vectors,dtype=np.int64)
        rng=np.random.Generator(np.random.PCG64(primary['inference_seeds'][str(t)]))
        indices=rng.integers(0,32,size=(primary['bootstrap_replicates'],32))
        data[t]=values
        bootstrap[t]=values[indices].mean(axis=1)
        arms[str(t)]=dict(recorded=len(rows),observed=sum(r['exact_sweep'] is not None for r in rows),
            administratively_censored=sum(r['exact_sweep'] is None for r in rows),missing=0,
            restricted_mean_evaluations=str(F(sum(int(v[0]) for v in values),32)),
            q10_median_q90=np.quantile(values[:,0],[.1,.5,.9],method='linear').tolist(),
            phase_mean_sweeps=values[:,1:].mean(axis=0).tolist(),
            post_S_positive_delays=[r['post_sweep']-r['S'] for r in rows if r['post_sweep']!=r['S']],
            endpoint_repairs=sum(r['endpoint_repairs_own']+r['endpoint_repairs_external'] for r in rows))
    ratio=float(data[1][:,0].mean()/data[23][:,0].mean())
    ci=np.quantile(bootstrap[1][:,0]/bootstrap[23][:,0],primary['interval'],method='linear').tolist()
    assert ratio==published['primary']['ratio']
    assert ci==published['primary']['nominal_95_ci']
    differences=(data[1].mean(axis=0)-data[23].mean(axis=0)).tolist()
    intervals=np.quantile(bootstrap[1]-bootstrap[23],[.025,.975],axis=0,method='linear').T.tolist()
    campaign,hashes=read_campaign(repo)
    old_seedset={r['seed'] for manifest,_,_ in campaign.values() for r in manifest['plan']}
    followup_seedset={r['seed'] for r in records.values()}
    assert len(followup_seedset)==68 and not followup_seedset & old_seedset
    old_main=list(campaign['main'][1].values())
    censored=[r for r in old_main if r['post_sweep'] is None]
    assert len(censored)==1
    hold_manifest,hold_rows,hold_status=campaign['holdout']
    assert len(hold_manifest['plan'])==240 and not hold_rows and hold_status['state']=='gate_blocked'
    old_arms={}
    for t in (1,16):
        rows=[r for r in old_main if r['n']==256 and r['T']==t and r['factor']==1/64]
        assert len(rows)==24 and all(r['exact_sweep'] is not None for r in rows)
        old_arms[str(t)]=dict(recorded=24,observed=24,censored=0,
            mean_evaluations=str(F(sum(257*(1+r['exact_sweep']) for r in rows),24)))
    old_ratio=F(old_arms['1']['mean_evaluations'])/F(old_arms['16']['mean_evaluations'])
    result=dict(status='mechanically checked receipts and analysis; no new trajectory outcomes',
        n512=dict(arms=arms,ratio=ratio,nominal_95_ci=ci,mean_differences= differences,
                  nominal_pointwise_difference_intervals=intervals,
                  columns=['evaluations','pre_U','U_to_S','post_S','post_minus_first_exact'],
                  all_68_post_endpoints_observed=all(r['post_sweep'] is not None for r in records.values()),
                  bootstrap='registered PCG64 seeds only; existing observations resampled, no new experiment'),
        original=dict(arms=old_arms,ratio_exact=str(old_ratio),ratio_decimal=float(old_ratio),
            capped_main_receipt={k:censored[0][k] for k in ('id','n','T','factor','max_sweeps','exact_sweep','post_sweep','U','S')},
            holdout_planned=240,holdout_recorded=0,holdout_state=hold_status['state'],
            decision='original two-stage decision remains inconclusive; separate study is not replacement holdout'),
        seed_separation=dict(followup=68,campaign_planned=len(old_seedset),intersection=0,
            scope='campaign plans including blocked holdout; older factorial/broadcast seeds not re-audited'),
        registration=dict(commit=registration_commit,commit_time=commit_time,measurement_start=manifest['started_utc'],
            limitation='published receipts and Git metadata; private execution chronology not independently available'),
        source_hashes={**hashes,**{str(p.relative_to(repo)):sha(p) for p in
            [folder/'plan.json',folder/'manifest.json',folder/'registration.json',folder/'summary.json',
             *(folder/'rows').glob('*.json')]}},
        research_samples=0)
    out.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
    print(json.dumps(dict(n512_ratio=ratio,nominal_95_ci=ci,original_ratio=float(old_ratio),
                         receipts=len(records)+sum(len(rows) for _,rows,_ in campaign.values()),
                         blocked_holdout=240,research_samples=0),indent=2))


if __name__=='__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('--repo',type=Path,required=True)
    parser.add_argument('--out',type=Path,required=True)
    args=parser.parse_args()
    run(args.repo.resolve(),args.out)
