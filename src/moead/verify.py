"""Verify evidence integrity and trial accounting, NOT a mathematical theorem."""

import argparse
import json
from pathlib import Path

from .experiments import digest
from .report import verify_data
from .statistics import load_runs, summarize


def verify(out: Path, check_source=False):
    manifest = verify_data(out)
    count = 0
    for line in (out / 'checksums.sha256').read_text().splitlines():
        expected, relative = line.split('  ', 1)
        path = (out / relative).resolve()
        if not path.is_relative_to(out.resolve()):
            raise ValueError('checksum path escapes evidence directory')
        if digest(path) != expected:
            raise ValueError(f'checksum mismatch: {relative}')
        count += 1
    rows = load_runs(out / 'runs.csv')
    if len(rows) != manifest['trials'] or sum(row['event'] for row in rows) != manifest['completed']:
        raise ValueError('trial counts disagree with manifest')
    summarize(rows)  # Validate configuration-level censoring horizons and seeds.
    if any(row['certificate_violations'] for row in rows):
        raise ValueError('a claimed noiseless certificate failed an eligible check')
    if check_source:
        root = Path(__file__).resolve().parents[2]
        for name, expected in manifest['source_sha256'].items():
            if digest(root / name) != expected:
                raise ValueError(f'source differs from the experiment: {name}')
    return dict(verified_files=count, trials=len(rows), censored=manifest['censored'])


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--input', type=Path, required=True)
    parser.add_argument('--check-source', action='store_true')
    args = parser.parse_args()
    print(json.dumps(verify(args.input, args.check_source), indent=2))


if __name__ == '__main__':
    main()
