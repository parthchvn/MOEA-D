"""Regression tests for expanded noise evidence, not asymptotic runtime tests."""
import copy
import csv
import json
from pathlib import Path

import numpy as np
import pytest

from moead.kernel import transition
from moead.noise import cells, load, run, run_cell, summarize, verify
from moead.noise_report import render

ROOT = Path(__file__).resolve().parents[1]


def small_protocol():
    return dict(schema_version=1, master_seed=197, replicates=2, budget_sweep_factor=1,
                families=[dict(kind=kind, n_values=[4], noise_values=values,
                               radius_rules=['self', 'global'])
                          for kind, values in [('scaled', [0, 0.1, 1]), ('fixed', [0, 0.5, 1])]])


def test_expanded_protocol_is_explicit_and_unique():
    protocol = json.loads((ROOT / 'experiments/noise-grid.json').read_text())
    grid = cells(protocol)
    assert len(grid) == 272
    assert len(grid) * protocol['replicates'] == 8704
    assert len({c['config_id'] for c in grid}) == len(grid)
    for c in grid:
        assert c['p'] == (c['noise_value']/c['n'] if c['family'] == 'scaled' else c['noise_value'])
    for n in [32, 64, 128, 256, 512]:
        assert len({c['budget'] for c in grid if c['n'] == n}) == 1
    changed = copy.deepcopy(protocol)
    changed['families'].reverse()
    for f in changed['families']:
        f['n_values'].reverse()
        f['noise_values'].reverse()
    assert cells(changed) == grid


@pytest.mark.parametrize('change', [dict(replicates=1), dict(replicates=True),
                                   dict(budget_sweep_factor=0), dict(budget_sweep_factor=float('nan')),
                                   dict(schema_version=2), dict(unknown=1), dict(families=[])])
def test_bad_protocol_rejected(change):
    with pytest.raises(ValueError):
        cells(dict(small_protocol(), **change))


@pytest.mark.parametrize('change', [dict(kind='unknown'), dict(noise_values=[-1]),
                                   dict(noise_values=[float('inf')]), dict(n_values=[4, 4]),
                                   dict(radius_rules=['unknown']), dict(noise_values=[0, 0])])
def test_bad_family_rejected(change):
    p = small_protocol()
    p['families'][0].update(change)
    with pytest.raises(ValueError):
        cells(p)


def test_fixed_probability_above_one_rejected():
    p = small_protocol()
    p['families'][1]['noise_values'] = [1.1]
    with pytest.raises(ValueError):
        cells(p)


def test_cell_replay_and_separate_control_streams():
    grid = cells(small_protocol())
    a = next(c for c in grid if c['family'] == 'scaled' and c['radius'] == 0 and c['p'] == 0)
    b = next(c for c in grid if c['family'] == 'fixed' and c['radius'] == 0 and c['p'] == 0)
    first = run_cell((a, 77, 2, 'python'))
    assert first == run_cell((a, 77, 2, 'python'))
    assert first[0]['seed'] != run_cell((b, 77, 2, 'python'))[0]['seed']


def test_full_small_pipeline_and_tamper_detection(tmp_path):
    protocol = tmp_path / 'protocol.json'
    protocol.write_text(json.dumps(small_protocol()))
    out = tmp_path / 'evidence'
    manifest = run(protocol, out, 'python')
    assert manifest['trials'] == 24
    rows = load(out)
    assert len(rows) == 24 and any(not r['event'] for r in rows)
    rendered = render(out)
    assert rendered['trials'] == 24 and len(rendered['figures']) >= 6
    assert verify(out, check_source=True)['trials'] == 24
    with pytest.raises(FileExistsError):
        run(protocol, out, 'python')
    with (out / 'summary.csv').open('a') as f:
        f.write('tampered\n')
    with pytest.raises(ValueError):
        verify(out)


def test_capped_observations_not_discarded():
    a = cells(small_protocol())[0]
    group = run_cell((a, 77, 2, 'python'))
    group[0].update(budget=100, evaluations=10, event=1, stored_hit=9)
    group[1].update(budget=100, evaluations=100, event=0, stored_hit=20)
    result, = summarize(group)
    assert result['mean_capped_evaluations'] == 55
    assert result['completed'] == result['censored'] == 1
    assert result['stored_hit_but_exact_censored'] == 1
    group[1]['budget'] = 101
    with pytest.raises(ValueError):
        summarize(group)


@pytest.mark.parametrize('n', [1, 2, 5, 8])
def test_p_one_stored_optimal_slots_cannot_become_true_optimal(n):
    # A legitimate p=1 population: observed[j]=j, true[j] differs by one.
    observed = np.arange(n+1, dtype=np.int64)
    weights = np.where(observed < n, observed+1, n-1).astype(np.int64)
    counts = np.bincount(weights, minlength=n+1)
    first = np.full(n+1, -1, dtype=np.int64)
    rng = np.random.default_rng(191+n)
    for t in range(200):
        transition(n, n, t % (n+1), 1., *rng.random(3), weights, observed, counts, first, n+2+t)
        np.testing.assert_array_equal(observed, np.arange(n+1))
        assert np.all(weights != observed)
        assert np.all(abs(weights-observed) == 1)
