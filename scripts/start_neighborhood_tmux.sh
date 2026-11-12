#!/usr/bin/env bash
set -euo pipefail
root="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd -P)"
cd "$root"
for candidate in "${MOEAD_PYTHON:-}" "$root/.venv/bin/python" "$HOME/miniforge3/bin/python" python3.13 python3.12 python3.11 python3; do
    if [[ -n "$candidate" ]] && command -v "$candidate" >/dev/null && "$candidate" -c 'import sys; sys.exit(sys.version_info < (3,11))'; then
        exec "$candidate" scripts/neighborhood_session.py "$@"
    fi
done
echo 'Install Python 3.11+ or set MOEAD_PYTHON to its executable.' >&2
exit 1
