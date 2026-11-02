import copy
import csv
import json
from pathlib import Path
import numpy as np
import pytest

from moead.experiments import configurations, load_protocol, run_experiments, trial_seed
from moead.report import verify_data
from moead.statistics import bootstrap_mean_interval, load_runs, summarize, wilson_interval


ROOT = Path(__file__).resolve().parents[1]


def test_seeds_are_stable_and_configuration_specific():
    assert trial_seed(7, 'a', 0) == trial_seed(7, 'a', 0)
    values = [trial_seed(7, c, r) for c in ['a', 'b'] for r in range(20)]
    assert len(set(values)) == len(values)
    assert trial_seed(7, 'a', 0) != trial_seed(8, 'a', 0)


def test_protocol_has_no_duplicate_configurations():
    protocol = load_protocol(ROOT / 'experiments/neighborhoods.json')
    cells = configurations(protocol)
    assert len(cells) == 67
    assert len({(x['algorithm'], x['n'], x['radius'], x['alpha']) for x in cells}) == len(cells)
    reversed_protocol = copy.deepcopy(protocol)
    reversed_protocol['n_values'].reverse()
    assert configurations(reversed_protocol) == cells


def test_bootstrap_is_reproducible_and_constants_are_exact():
    assert bootstrap_mean_interval([7, 7, 7], 42) == (7, 7)
    assert bootstrap_mean_interval([1, 2, 10], 42) == bootstrap_mean_interval([1, 2, 10], 42)
    with pytest.raises(ValueError):
        bootstrap_mean_interval([1])
    with pytest.raises(ValueError):
        bootstrap_mean_interval([1, np.nan])
    lo, hi = wilson_interval(32, 32)
    assert 0 < lo < 1 and hi == pytest.approx(1)
    with pytest.raises(ValueError):
        wilson_interval(2, 1)


def test_pipeline_preserves_all_trials_and_checksums(tmp_path):
    protocol = load_protocol(ROOT / 'experiments/smoke.json')
    protocol.update(n_values=[4], radius_rules=['self', 'global'],
                    extra_radius_sweep={}, diagnostic_cases=[[4, 0]], frontier_baseline=False)
    path = tmp_path / 'protocol.json'
    path.write_text(json.dumps(protocol))
    out = tmp_path / 'evidence'
    manifest = run_experiments(path, out, engine='python')
    rows = load_runs(out / 'runs.csv')
    assert manifest['trials'] == len(rows) == 8
    assert len(summarize(rows)) == 4
    assert verify_data(out)['trials'] == 8
    with pytest.raises(FileExistsError):
        run_experiments(path, out, engine='python')
    # Explicit censoring test: keep the capped observation in the mean.
    group = copy.deepcopy(rows[:2])
    for i, row in enumerate(group):
        row.update(config_id='censor-test', repetition=i, seed=i, budget=100)
    group[0].update(evaluations=10, event=1)
    group[1].update(evaluations=100, event=0)
    result, = summarize(group)
    assert result['mean_observed_evaluations'] == 55
    assert result['mean_runtime_if_uncensored'] == ''
    assert result['statistic'] == 'restricted_mean' and result['censored'] == 1
    group[1]['budget'] = 99
    with pytest.raises(ValueError):
        summarize(group)
    with (out / 'runs.csv').open('a') as handle:
        handle.write('tampered\n')
    with pytest.raises(ValueError, match='checksum mismatch'):
        verify_data(out)


def test_parser_rejects_bad_protocol(tmp_path):
    original = load_protocol(ROOT / 'experiments/smoke.json')
    for changes in [{'schema_version': 2}, {'typo': True}, {'replicates': 1},
                    {'n_values': [8, 8]}, {'alpha_values': [0, 0]}]:
        path = tmp_path / 'bad.json'
        path.write_text(json.dumps(dict(original, **changes)))
        with pytest.raises(ValueError):
            load_protocol(path)
