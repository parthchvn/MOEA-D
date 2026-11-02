"""Censoring-aware descriptive summaries; intervals are pointwise Monte Carlo CIs."""

import csv
import hashlib
import math
from collections import defaultdict
from pathlib import Path
import numpy as np


def load_runs(path: Path) -> list[dict]:
    with path.open(newline='') as handle:
        rows = list(csv.DictReader(handle))
    if not rows:
        raise ValueError('no trials')
    integers = ('n', 'radius', 'nominal_width', 'max_neighborhood_size',
                'endpoint_neighborhood_size', 'repetition', 'seed', 'budget',
                'evaluations', 'event', 'initial_evaluations', 'comparisons',
                'certificate_checks', 'certificate_violations')
    seen = set()
    for row in rows:
        for field in integers:
            row[field] = int(row[field])
        for field in ('p', 'alpha'):
            row[field] = float(row[field])
        for field in ('front_hit_evaluations', 'stored_hit_evaluations', 'initial_weight'):
            row[field] = int(row[field]) if row[field] else None
        value = row['conditional_expected_evaluations']
        row['conditional_expected_evaluations'] = float(value) if value else None
        key = (row['config_id'], row['repetition'])
        if key in seen:
            raise ValueError('duplicate trial')
        seen.add(key)
        if row['event'] not in (0, 1) or not row['initial_evaluations'] <= row['evaluations'] <= row['budget']:
            raise ValueError('invalid event flag or evaluation accounting')
        if not row['event'] and row['evaluations'] != row['budget']:
            raise ValueError('right-censored trials must record their administrative budget')
    return rows


def bootstrap_mean_interval(values, seed=0, resamples=2000):
    values = np.asarray(values, dtype=float)
    if values.ndim != 1 or values.size < 2 or not np.all(np.isfinite(values)):
        raise ValueError('at least two finite scalar observations required')
    rng = np.random.Generator(np.random.PCG64(seed))
    means = values[rng.integers(values.size, size=(resamples, values.size))].mean(axis=1)
    return tuple(float(x) for x in np.quantile(means, [0.025, 0.975]))


def wilson_interval(successes, trials):
    if trials < 1 or not 0 <= successes <= trials:
        raise ValueError('invalid binomial counts')
    z = 1.959963984540054
    p = successes / trials
    denominator = 1 + z * z / trials
    center = (p + z * z / (2 * trials)) / denominator
    radius = z * math.sqrt(p * (1 - p) / trials + z * z / (4 * trials * trials)) / denominator
    return max(0.0, center - radius), min(1.0, center + radius)


def summarize(rows: list[dict]) -> list[dict]:
    groups = defaultdict(list)
    for row in rows:
        groups[row['config_id']].append(row)
    output = []
    for cid, group in sorted(groups.items()):
        first = group[0]
        if len({row['budget'] for row in group}) != 1:
            raise ValueError('each configuration must have a common censoring horizon')
        if len({row['seed'] for row in group}) != len(group):
            raise ValueError('replicates must have distinct seeds')
        values = [row['evaluations'] for row in group]  # NEVER filter on event.
        completed = sum(row['event'] for row in group)
        seed = int.from_bytes(hashlib.sha256(cid.encode()).digest()[:8], 'big')
        low, high = bootstrap_mean_interval(values, seed)
        success_low, success_high = wilson_interval(completed, len(group))
        result = {field: first[field] for field in
                  ('config_id', 'algorithm', 'n', 'radius', 'alpha', 'p', 'policies', 'budget')}
        result.update(trials=len(group), completed=completed, censored=len(group) - completed,
                      statistic='mean' if completed == len(group) else 'restricted_mean',
                      mean_observed_evaluations=float(np.mean(values)),
                      mean_runtime_if_uncensored=float(np.mean(values)) if completed == len(group) else '',
                      ci_low=low, ci_high=high, completion_rate=completed / len(group),
                      completion_ci_low=success_low, completion_ci_high=success_high,
                      mean_comparisons=float(np.mean([row['comparisons'] for row in group])),
                      certificate_checks=sum(row['certificate_checks'] for row in group),
                      certificate_violations=sum(row['certificate_violations'] for row in group))
        output.append(result)
    return output
