"""Render the expanded-noise evidence from retained raw trials only."""
import argparse
import json
from pathlib import Path

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

from .experiments import digest
from .noise import load, summarize, write_csv

LABELS = {'self': 'r=0', 'local': 'r=1', 'log': 'r=ceil(ln n)', 'global': 'r=n (global)'}


def render(out: Path):
    rows = load(out)
    summary = summarize(rows)
    write_csv(out / 'summary.csv', summary)
    protocol = json.loads((out / 'config.json').read_text())
    figures = out / 'figures'
    figures.mkdir(exist_ok=True)
    plt.rcParams['svg.fonttype'] = 'none'
    plt.rcParams['svg.hashsalt'] = 'moead-noise-v1'
    saved = []

    def finish(fig, ax, name):
        ax.grid(alpha=0.25)
        ax.legend(fontsize=8)
        fig.tight_layout()
        fig.savefig(figures / name, format='svg', metadata={'Date': None, 'Creator': 'moead-oneminmax'})
        plt.close(fig)
        saved.append(name)

    kinds = sorted({r['family'] for r in summary})
    common = set.intersection(*[{r['n'] for r in summary if r['family'] == kind} for kind in kinds])
    chosen_n = max(common) if common else min(max(r['n'] for r in summary if r['family'] == k) for k in kinds)
    for kind in kinds:
        group = [r for r in summary if r['family'] == kind and r['n'] == chosen_n]
        if not group:
            continue
        xname = 'alpha in p=alpha/n' if kind == 'scaled' else 'Fixed noise probability p'
        for metric in ['runtime', 'completion']:
            fig, ax = plt.subplots(figsize=(8.2, 5.2))
            for policy, label in LABELS.items():
                data = sorted([r for r in group if r['policy'] == policy], key=lambda r: r['noise_value'])
                if not data:
                    continue
                x = [r['noise_value'] for r in data]
                if metric == 'runtime':
                    y = np.array([r['mean_capped_evaluations'] for r in data])
                    lo = np.array([r['mean_ci_low'] for r in data])
                    hi = np.array([r['mean_ci_high'] for r in data])
                else:
                    y = np.array([r['completion_rate'] for r in data])
                    lo = np.array([r['completion_ci_low'] for r in data])
                    hi = np.array([r['completion_ci_high'] for r in data])
                if np.all(lo <= y) and np.all(y <= hi):
                    ax.errorbar(x, y, yerr=np.vstack((y-lo, hi-y)), fmt='o-', capsize=3, markersize=4, label=label)
                else:
                    ax.plot(x, y, 'o-', label=label, markersize=4)
                    for xx, low, high in zip(x, lo, hi):
                        ax.plot([xx, xx], [low, high], '-')
            ax.set_xscale('symlog', linthresh=0.1 if kind == 'scaled' else 0.01)
            ax.set_xlabel(xname)
            if metric == 'runtime':
                ax.set_yscale('log')
                ax.set_ylabel('Sample mean of min(runtime, evaluation cap)')
                ax.axhline(group[0]['budget'], linestyle='--', label=f"Cap = {group[0]['budget']:,}")
                ax.set_title(f'Noise response, n={chosen_n}\nPointwise approximate 95% bootstrap intervals; capped means')
            else:
                ax.set_ylim(-0.03, 1.07)
                ax.set_ylabel('Fraction reaching true exact assignment by cap')
                ax.set_title(f'Completion within budget, n={chosen_n}\nPointwise approximate 95% Wilson intervals')
            finish(fig, ax, f'{kind}_{metric}.svg')

    data = [r for r in summary if r['family'] == 'fixed' and r['policy'] == 'global']
    if data:
        fig, ax = plt.subplots(figsize=(8.2, 5.2))
        for n in sorted({r['n'] for r in data}):
            selected = sorted([r for r in data if r['n'] == n], key=lambda r: r['p'])
            ax.plot([r['p'] for r in selected], [r['completion_rate'] for r in selected], 'o-', label=f'n={n}')
        ax.set_xscale('symlog', linthresh=0.01)
        ax.set(xlabel='Fixed noise probability p', ylabel='Fraction reaching true exact assignment by cap',
               ylim=(-0.03, 1.07), title='Global neighborhoods: success across tested sizes\nDescriptive proportions, not a noise-threshold estimate')
        finish(fig, ax, 'fixed_success_by_n.svg')

        selected = sorted([r for r in data if r['n'] == chosen_n], key=lambda r: r['p'])
        if selected:
            fig, ax = plt.subplots(figsize=(8.2, 5.2))
            x = [r['p'] for r in selected]
            ax.plot(x, [r['completion_rate'] for r in selected], 'o-', label='True exact assignment reached by cap')
            ax.plot(x, [r['stored_hit_observed']/r['trials'] for r in selected], 's-', label='Stored optima observed before stopping')
            ax.plot(x, [r['stored_hit_but_exact_censored']/r['trials'] for r in selected], '^-', label='Stored optima reached, true assignment still censored')
            ax.set_xscale('symlog', linthresh=0.01)
            ax.set(xlabel='Fixed noise probability p', ylabel='Observed fraction of runs', ylim=(-0.03, 1.07),
                   title=f'Stored optima versus true correctness, global r=n, n={chosen_n}\nObservation ends at true completion or cap, whichever comes first')
            finish(fig, ax, 'stored_vs_true.svg')

            cens = [r for r in selected if r['censored']]
            if cens:
                fig, ax = plt.subplots(figsize=(8.2, 5.2))
                ax.plot([r['p'] for r in cens], [r['mean_terminal_incorrect_censored']/(r['n']+1) for r in cens], 'o-', label='Mean incorrect fraction in capped runs only')
                ax.set(xlabel='Fixed noise probability p', ylabel='Incorrect slots / (n+1) at the administrative cap',
                       title=f'Terminal errors among censored runs, n={chosen_n}, global r=n\nSelected subset; NOT a stationary-distribution estimate')
                finish(fig, ax, 'terminal_errors_censored.svg')

    scaled = [r for r in summary if r['family'] == 'scaled' and r['policy'] == 'global']
    if scaled:
        fig, ax = plt.subplots(figsize=(8.2, 5.2))
        for alpha in sorted({r['noise_value'] for r in scaled}):
            selected = sorted([r for r in scaled if r['noise_value'] == alpha], key=lambda r: r['n'])
            ax.plot([r['n'] for r in selected], [r['mean_capped_evaluations']/r['n']**2 for r in selected], 'o-', label=f'alpha={alpha:g}')
        ax.set_xscale('log', base=2)
        ax.set(xlabel='Bit-string length n', ylabel='Mean capped evaluations / n²',
               title='Global neighborhoods with p=alpha/n\nNormalization is a diagnostic, not a proof of quadratic scaling')
        finish(fig, ax, 'scaled_global_normalized.svg')

    count = len(rows)
    censored = sum(1-r['event'] for r in rows)
    text = ['# Expanded one-bit prior-noise evidence', '',
            f'**{count:,} new seeded trials; {count-censored:,} completed; {censored:,} right-censored.**', '',
            'The cyclic self-parent Tchebycheff simulator is unchanged. This dataset is separate from the original neighborhood experiment.',
            'Its grid was selected after exploratory pilot runs; it is not a preregistered confirmatory study.', '',
            '## Protocol', '',
            f"Every cell has {protocol['replicates']} independent seeded replicates. The families are:", '']
    for f in protocol['families']:
        text.append(f"- {f['kind']}: n={f['n_values']}; noise values={f['noise_values']}; radius policies={f['radius_rules']}.")
    text += ['', '`scaled` means p=alpha/n; `fixed` means p is held constant across n. All logarithms are natural.',
             f"The common evaluation cap at a given n is B=(n+1)[1+ceil({protocol['budget_sweep_factor']} n ln(n+2))], including initialization.",
             'The original neighborhood experiment used factor 20; this expanded grid uses its own fresh controls and a smaller fixed cap.',
             'No early stopping based on apparent failure is used. All 32 attempts (or the protocol-specified count) remain in every mean.', '',
             '## Interpretation and uncertainty', '',
             'The estimand is E[min(tau,B)], not the unrestricted E[tau]. A plateau at the cap is a timeout effect, not runtime saturation.',
             'Bootstrap intervals use 2,000 percentile resamples; completion intervals use the Wilson approximation. Both are pointwise approximate 95% intervals, not simultaneous guarantees.',
             'An all-censored cell has a degenerate empirical bootstrap interval at B. This says nothing about the unrestricted runtime or its upper tail.',
             '32/32 successes do not prove success probability one; 0/32 does not prove impossibility.',
             'Stored-optimum hits are observed only until min(tau,B). Their counts are not a separate uncensored hitting-time experiment.',
             'Terminal error averages use censored runs only; they are not stationary-error estimates.',
             'No exponential-runtime, universal monotonicity, polynomial-noise threshold, or full-population Theta-law is inferred from these data.', '',
             '## Figures', '']
    for name in saved:
        text += [f'![{name[:-4].replace("_", " ")}](figures/{name})', '']
    text += [f'## All cells at n={chosen_n}', '',
             '| Family | alpha or p | radius r | exact / trials | stored hit observed | stored hit but exact censored | mean capped evaluations | bootstrap interval |',
             '|---|---:|---:|---:|---:|---:|---:|---:|']
    for r in sorted([r for r in summary if r['n'] == chosen_n], key=lambda r: (r['family'], r['noise_value'], r['radius'])):
        text.append(f"| {r['family']} | {r['noise_value']:g} | {r['radius']} | {r['completed']}/{r['trials']} | {r['stored_hit_observed']} | {r['stored_hit_but_exact_censored']} | {r['mean_capped_evaluations']:.1f} | [{r['mean_ci_low']:.1f}, {r['mean_ci_high']:.1f}] |")
    text += ['', '## Global scaled-noise cells at all sizes', '',
             '| n | alpha | actual p | exact / trials | mean capped evaluations / n² |',
             '|---:|---:|---:|---:|---:|']
    for r in sorted(scaled, key=lambda r: (r['noise_value'], r['n'])):
        text.append(f"| {r['n']} | {r['noise_value']:g} | {r['p']:.8g} | {r['completed']}/{r['trials']} | {r['mean_capped_evaluations']/r['n']**2:.4f} |")
    text += ['', '## Reproduce and audit', '',
             '```bash', 'python -m moead.noise --config experiments/noise-grid.json --out results-local/noise --workers 2',
             'python -m moead.noise_report --input results-local/noise',
             'python -m moead.noise --out results-local/noise --verify --check-source', '```', '',
             'Raw trials: `runs.csv`. Full summaries: `summary.csv`. Protocol: `config.json`. Source/environment/data hashes: `manifest.json`.',
             'The deterministic p=1 obstruction is explained separately in [the noise-analysis notes](../../docs/noise-analysis.md).', '']
    (out / 'README.md').write_text('\n'.join(text))
    paths = [out / name for name in ['config.json', 'runs.csv', 'manifest.json', 'summary.csv', 'README.md']]
    paths += [figures / name for name in saved]
    (out / 'checksums.sha256').write_text(''.join(f'{digest(path)}  {path.relative_to(out)}\n' for path in paths))
    return dict(trials=count, completed=count-censored, censored=censored, figures=saved)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--input', type=Path, required=True)
    args = parser.parse_args()
    print(json.dumps(render(args.input), indent=2))


if __name__ == '__main__':
    main()
