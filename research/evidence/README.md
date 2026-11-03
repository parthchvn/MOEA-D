# Published evidence for the completed studies

Prepared 2026-11-03 after the user explicitly authorized committing the proposal
and important completed-experiment evidence to `parthchvn/MOEA-D`, branch `main`.
Earlier reports' no-commit/no-push statements describe their historical study
boundaries; this later publication authorization does not authorize new studies.
The [standard-bit proposal](../STANDARD_BIT_PROPOSAL.md) remains unimplemented,
not preregistered and unlaunched.

These six compressed packs preserve the exact regular-file bytes of the reported
smoke, main and validation runs, including results, manifests, executed dirty
source snapshots, working-tree patches and any existing per-run analysis output.
Owner IDs, file modes and timestamps are normalized in the containers. Original
local run directories remain unchanged. The packs total 852,789 bytes; they
contain no PDFs, caches, virtual environments, Git metadata or credentials
identified by the publication checks. This is curated evidence, not every local
harness/debug run. The earlier exploratory radius diagnostic is not used for
the controlled conclusions and is omitted.

| Study | Smoke | Main | Validation | Inferential sample |
|---|---|---|---|---|
| Exact/lazy × archive/alignment | 54 trajectories | 576 trajectories | 144 trajectories | 720 independent population trajectories; paired stopping observations |
| Lazy broadcast ON/OFF | 36 trajectories / 18 blocks | 192 / 96 blocks | 96 / 48 blocks | 288 trajectories / 144 independent paired seed blocks |

All six grids completed without censored endpoints. Smoke supports semantic,
checkpoint and timing gates and is excluded from inferential summaries.
See the [factorial report](../reports/20261102T212758Z-radius-factorial.md),
[broadcast report](../reports/20261103T022831Z-broadcast-ablation.md), and their
curated [factorial](../reports/20261102T212758Z-factorial-summary.json) and
[broadcast](../reports/20261103T022831Z-broadcast-summary.json) summaries.
Neither finite study establishes an asymptotic result or universal event identity.

[INDEX.json](INDEX.json) maps each pack to its original run path, role, counts,
compressed/content sizes, and SHA-256 digests of every member, manifest and raw
results file. [SHA256SUMS](SHA256SUMS) covers the archives and index. Each original
manifest contains command, seed assignments, initialization/cost conventions,
censoring/cutoff policy, Git commit and dirty status, source hashes, Python and
installed dependency versions. In particular, the historical HEAD alone is not
the executed source: use the included exact dirty snapshot and patch. Old
absolute workspace/interpreter paths are provenance, not portable commands.

## Verify and extract to a new temporary directory

Run from the repository root. This extraction example uses Python 3.12 or newer
for its data filter. It checks compressed and member hashes and rejects absolute,
traversing, symbolic-link and other non-regular archive entries before extraction.
It does not overwrite local `research/runs/`.

```bash
export MOEAD_EVIDENCE_DIR="$(mktemp -d)"
python - <<'PYVERIFY'
import hashlib, json, os, pathlib, tarfile
base = pathlib.Path('research/evidence')
index = json.loads((base / 'INDEX.json').read_text())
for line in (base / 'SHA256SUMS').read_text().splitlines():
    expected, name = line.split('  ', 1)
    assert hashlib.sha256((base / name).read_bytes()).hexdigest() == expected
for record in index['archives']:
    with tarfile.open(base / record['archive'], 'r:gz') as archive:
        assert set(archive.getnames()) == set(record['member_sha256'])
        for member in archive.getmembers():
            path = pathlib.PurePosixPath(member.name)
            assert member.isfile() and not path.is_absolute()
            assert '..' not in path.parts and path.parts[:2] == ('research', 'runs')
            data = archive.extractfile(member).read()
            assert hashlib.sha256(data).hexdigest() == record['member_sha256'][member.name]
        archive.extractall(os.environ['MOEAD_EVIDENCE_DIR'], filter='data')
print(os.environ['MOEAD_EVIDENCE_DIR'])
PYVERIFY
```

## Recompute the reported summaries without rerunning experiments

Use the project environment (`requirements.txt`), or match the exact NumPy and
Python versions in each manifest for byte-level numerical reproducibility. The
following reads extracted raw records, uses the original bootstrap seeds/counts,
and writes only temporary recomputed summaries. It starts no simulator trials.

```bash
python scripts/analyze_factorial.py \
  "$MOEAD_EVIDENCE_DIR/research/runs/20261102T213520Z-factorial-grid-factorial-main" \
  "$MOEAD_EVIDENCE_DIR/research/runs/20261102T213945Z-factorial-grid-factorial-validation512" \
  --bootstrap 10000 --seed 2611029000 \
  --output "$MOEAD_EVIDENCE_DIR/factorial-recomputed.json"
python scripts/analyze_broadcast.py \
  "$MOEAD_EVIDENCE_DIR/research/runs/20261103T024310Z-broadcast-grid-broadcast-main" \
  "$MOEAD_EVIDENCE_DIR/research/runs/20261103T024933Z-broadcast-grid-broadcast-validation512" \
  --bootstrap 20000 --seed 2611039000 \
  --output "$MOEAD_EVIDENCE_DIR/broadcast-recomputed.json"
```

Only the `sources[].directory` paths should differ when the recorded numerical
environment is matched; raw/manifest hashes remain identical. The full recorded
statistics can be checked against the curated summaries after dropping the
`sources` list from each JSON object. A future simulator rerun is separate work:
first read its frozen preregistration, manifest, and exact source snapshot, and
set a new bounded budget rather than blindly executing historical commands.

Publication verification: compressed/member hashes and source hashes were
checked against the unchanged originals; contents were inspected for unexpected
files and common credential/private-key patterns. Both recomputation commands
were run on a fresh temporary extraction, reproducing every non-path summary
value exactly; no simulator was run. Existing independent numerical
verdicts are preserved in each report. The new proposal has separate independent
design/source approval, which is not approval to implement or launch it.

Independent publication audit **approved 2026-11-03 04:07:36 UTC**: all six
packs, 195 safe regular members and 1,098 trajectories passed hash, original-byte,
count and censoring checks. Independent in-memory analysis from archive contents
exactly reproduced both curated summaries apart from source paths; no simulator
was run. The coordinator separately reviews the Git file selection and publication.
