"""Regenerate all evidence figures and tables from raw trials, never invented curves."""

import argparse
import csv
import json
from pathlib import Path

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

from .experiments import digest
from .statistics import load_runs, summarize


POLICIES = [('self', 'r=0'), ('local', 'r=1'), ('log', 'r=ceil(log n)'),
            ('sqrt', 'r=floor(sqrt n)'), ('global', 'r=n (global)')]


def verify_data(out: Path) -> dict:
    manifest = json.loads((out / 'manifest.json').read_text())
    for name, expected in manifest['data_sha256'].items():
        if digest(out / name) != expected:
            raise ValueError(f'checksum mismatch: {name}')
    return manifest


def draw_series(ax, group, x, normalize=lambda row: 1.0, label=None):
    group = sorted(group, key=x)
    xs = [x(row) for row in group]
    ys = np.array([row['mean_observed_evaluations'] / normalize(row) for row in group])
    lo = np.array([row['ci_low'] / normalize(row) for row in group])
    hi = np.array([row['ci_high'] / normalize(row) for row in group])
    if np.all(lo <= ys) and np.all(ys <= hi):
        return ax.errorbar(xs, ys, yerr=np.vstack((ys - lo, hi - ys)),
                           fmt='o-', label=label, markersize=4, capsize=3)
    # Preserve exact endpoints even in the unusual case that a percentile
    # interval does not contain the point estimate (errorbar disallows that).
    line, = ax.plot(xs, ys, 'o-', label=label, markersize=4)
    for xx, low, high in zip(xs, lo, hi):
        ax.plot([xx, xx], [low, high], '-', linewidth=1.1)
    return line



def finish(fig, ax, path: Path):
    ax.grid(alpha=0.25)
    ax.legend(fontsize=8)
    fig.tight_layout()
    fig.savefig(path, format='svg', metadata={'Date': None, 'Creator': 'moead-oneminmax'})
    plt.close(fig)


def render_report(out: Path) -> dict:
    manifest = verify_data(out)
    rows = load_runs(out / 'runs.csv')
    if len(rows) != manifest['trials']:
        raise ValueError('manifest trial count mismatch')
    summary = summarize(rows)
    with (out / 'summary.csv').open('w', newline='') as handle:
        writer = csv.DictWriter(handle, fieldnames=list(summary[0]))
        writer.writeheader()
        writer.writerows(summary)
    figures = out / 'figures'
    figures.mkdir(exist_ok=True)
    plt.rcParams['svg.fonttype'] = 'none'
    plt.rcParams['svg.hashsalt'] = 'moead-v1'
    protocol = json.loads((out / 'config.json').read_text())
    fixed_n = protocol.get('extra_radius_sweep', {}).get('n', max(protocol['n_values']))
    cyclic = [row for row in summary if row['algorithm'] == 'cyclic']
    alphas = sorted({row['alpha'] for row in cyclic})
    saved = []

    fig, ax = plt.subplots(figsize=(7.8, 5.0))
    for alpha in alphas:
        group = [row for row in cyclic if row['n'] == fixed_n and row['alpha'] == alpha]
        if group:
            draw_series(ax, group, lambda row: row['radius'] + 1,
                        label='p=0' if alpha == 0 else f'p={alpha:g}/n')
    ax.set(xscale='log', yscale='log', xlabel='Endpoint neighborhood size r + 1',
           ylabel='Mean observed evaluations (including initialization)',
           title=f'Neighborhood experiment, n={fixed_n}\nPointwise 95% bootstrap intervals')
    name = 'runtime_vs_radius.svg'
    finish(fig, ax, figures / name)
    saved.append(name)

    for alpha in alphas:
        fig, ax = plt.subplots(figsize=(7.8, 5.0))
        for policy, label in POLICIES:
            group = [row for row in cyclic if row['alpha'] == alpha and policy in row['policies'].split('|')]
            if group:
                draw_series(ax, group, lambda row: row['n'], lambda row: row['n'] ** 2, label)
        ax.set_xscale('log', base=2)
        ax.set(xlabel='Bit-string length n', ylabel='Mean observed evaluations / n²',
               title=f'Cyclic self-parent MOEA/D, p={alpha:g}/n\nNormalization is a diagnostic, not a proof of scaling')
        name = 'scaling_noiseless.svg' if alpha == 0 else f'scaling_alpha_{alpha:g}.svg'
        finish(fig, ax, figures / name)
        saved.append(name)

    with (out / 'diagnostics.jsonl').open() as handle:
        details = [json.loads(line) for line in handle if line.strip()]
    selected = [item for item in details if item['n'] == fixed_n]
    radii = sorted({item['radius'] for item in selected})
    for field, name, title in [
        ('acceptance_jumps', 'acceptance_jumps.svg', 'Endpoint drop per individual acceptance'),
        ('sweep_jumps', 'sweep_jumps.svg', 'Endpoint drop per completed sweep'),
    ]:
        if not selected:
            continue
        fig, ax = plt.subplots(figsize=(7.8, 5.0))
        for radius in radii:
            hist = np.sum([item[field] for item in selected if item['radius'] == radius], axis=0)
            total = int(hist[1:].sum())
            if total:
                positive = np.flatnonzero(hist[1:]) + 1
                ax.plot(positive, hist[positive] / total, 'o-', label=f'r={radius}', markersize=4)
        ax.set(yscale='log', xlabel='Positive decrease in w₀', ylabel='Fraction of observed positive drops',
               title=f'{title}, n={fixed_n}, p=0\nA finite observed maximum is not a universal bound')
        finish(fig, ax, figures / name)
        saved.append(name)

    if selected:
        fig, ax = plt.subplots(figsize=(7.8, 5.0))
        for radius in radii:
            arrays = np.array([item['level_visits'] for item in selected if item['radius'] == radius])
            values = arrays.mean(axis=0)  # zero contributions for skipped levels remain in denominator
            indices = np.flatnonzero(values[1:]) + 1
            ax.plot(indices, values[indices], '.', label=f'r={radius}', markersize=4)
        ax.set(xscale='log', yscale='log', xlabel='Endpoint level S=w₀ at sweep start',
               ylabel='Mean sweep-start observations per run',
               title=f'Endpoint occupation, n={fixed_n}, p=0\nUnvisited levels count as zero; zeros are not drawn on log axes')
        name = 'endpoint_occupation.svg'
        finish(fig, ax, figures / name)
        saved.append(name)

        fig, ax = plt.subplots(figsize=(7.8, 5.0))
        lookup = {(row['config_id'], row['repetition']): row for row in rows}
        for radius in radii:
            arrays = []
            for item in selected:
                if item['radius'] == radius:
                    values = np.array(item['first_hit'])
                    budget = lookup[item['config_id'], item['repetition']]['budget']
                    arrays.append(np.where(values >= 0, values, budget))
            ax.plot(range(fixed_n + 1), np.mean(arrays, axis=0), label=f'r={radius}', linewidth=1.3)
        ax.set(xlabel='Subproblem index j', ylabel='Mean capped first-hit evaluations',
               title=f'First time |xⱼ|₁=j, n={fixed_n}, p=0\nDescriptive profile, not an assertion that the interior is instantaneous')
        name = 'first_hit_profile.svg'
        finish(fig, ax, figures / name)
        saved.append(name)

    frontier = [row for row in summary if row['algorithm'] == 'frontier']
    if frontier:
        fig, ax = plt.subplots(figsize=(7.8, 5.0))
        global_rows = [row for row in cyclic if row['alpha'] == 0 and 'global' in row['policies'].split('|')]
        draw_series(ax, global_rows, lambda row: row['n'], label='Cyclic: global neighborhood, independent initialization')
        draw_series(ax, frontier, lambda row: row['n'], label='Frontier: r=1, single evaluated initial solution')
        ns, predicted = [], []
        for n in sorted({row['n'] for row in frontier}):
            ns.append(n)
            predicted.append(np.mean([row['conditional_expected_evaluations'] for row in rows
                                      if row['algorithm'] == 'frontier' and row['n'] == n]))
        ax.plot(ns, predicted, '--', label='Frontier: average of exact conditional expectations')
        ax.set(xscale='log', yscale='log', xlabel='Bit-string length n', ylabel='Mean observed evaluations',
               title='A separate noiseless scheduling baseline\nDifferent scheduling AND initialization; not a neighborhood-only comparison')
        name = 'frontier_comparison.svg'
        finish(fig, ax, figures / name)
        saved.append(name)

    checks = sum(row['certificate_checks'] for row in rows)
    violations = sum(row['certificate_violations'] for row in rows)
    censored = sum(1 - row['event'] for row in rows)
    text = [
        '# Reproducible neighborhood evidence', '',
        f"Generated from **{len(rows):,} trials**, with **{censored} right-censored trials**.",
        f"Protocol: {protocol['replicates']} replicates per cell; n in {protocol['n_values']}; p=alpha/n.",
        f"Noiseless certificate checks at eligible completed sweep boundaries: **{checks:,}**; violations: **{violations}**.",
        'The certificate is also proved in ../../docs/theory-status.md; finite checks alone are not a proof.', '',
        '## Reading the figures', '',
        'Raw trials are in `runs.csv`; all diagnostic arrays are in `diagnostics.jsonl`.',
        '`manifest.json` records source-file hashes, source commit when available, RNG, environment, and data hashes.',
        'Evaluation counts include initialization and stop at the first true exact assignment, checked after every offspring.',
        'One noisy objective vector is shared across replacement comparisons; parents are not re-evaluated.',
        'The reference point is fixed at (n,n). Radii define clipped symmetric intervals, not shifted fixed-width windows.', '',
        '**Uncertainty:** vertical segments are pointwise 95% percentile bootstrap intervals (2,000 resamples) for the sample mean.',
        'These are approximate Monte Carlo intervals, not finite-sample coverage guarantees or simultaneous confidence bands.',
        'If a cell is censored, the plotted statistic is the mean of min(runtime, budget), NOT the unconditional runtime mean.',
        'The summary leaves the unconditional mean field empty in such cells; no failed run is discarded.',
        'No censored runs in a finite experiment does not prove a tail bound or an asymptotic runtime.', '',
        '## Runtime by radius', '',
        '![Runtime by radius](figures/runtime_vs_radius.svg)', '',
        f'All tested radii at n={fixed_n}:', '',
        '| alpha | radius r | completed / trials | mean observed evaluations | bootstrap interval |',
        '|---:|---:|---:|---:|---:|',
    ]
    for row in sorted([x for x in cyclic if x['n'] == fixed_n], key=lambda x: (x['alpha'], x['radius'])):
        text.append(f"| {row['alpha']:g} | {row['radius']} | {row['completed']}/{row['trials']} | "
                    f"{row['mean_observed_evaluations']:.1f} | [{row['ci_low']:.1f}, {row['ci_high']:.1f}] |")
    text += ['', '## Scaling diagnostics', '',
             'Dividing by n² visualizes a candidate scaling; flat-looking curves do not establish a Theta-law.']
    for name in saved:
        if name != 'runtime_vs_radius.svg':
            text += ['', f'![{name[:-4].replace("_", " ")}](figures/{name})']
    text += ['', '## Claims not established', '',
             'These finite experiments do not prove a matching lower bound, a noise threshold, bounded endpoint jumps,',
             'or that endpoint optimization alone controls all subproblems. No fitted asymptotic law is presented as a theorem.',
             'The frontier plot concerns a separate noiseless algorithm and initialization; it is not a noisy-runtime result.',
             'See ../../docs/theory-status.md and ../../docs/methodology.md for the precise status and limitations.', '']
    (out / 'README.md').write_text('\n'.join(text))
    paths = [out / name for name in ('config.json', 'runs.csv', 'diagnostics.jsonl',
                                     'manifest.json', 'summary.csv', 'README.md')]
    paths += [figures / name for name in saved]
    (out / 'checksums.sha256').write_text(''.join(f'{digest(path)}  {path.relative_to(out)}\n' for path in paths))
    return dict(trials=len(rows), censored=censored, checks=checks, violations=violations, figures=saved)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--input', type=Path, required=True)
    args = parser.parse_args()
    print(json.dumps(render_report(args.input), indent=2))


if __name__ == '__main__':
    main()
