#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$repo_root"

if [[ ! -x .venv/bin/python ]]; then
    echo "Missing .venv. Follow research/START_LOCAL.md before launching Codex." >&2
    exit 1
fi

if ! .venv/bin/python -c "import numpy, matplotlib" >/dev/null 2>&1; then
    echo "The local Python environment is missing NumPy or Matplotlib." >&2
    exit 1
fi

if [[ -n "$(git status --porcelain)" ]]; then
    echo "Refusing to start from a dirty checkout." >&2
    echo "Review and commit the prepared baseline first; see research/START_LOCAL.md." >&2
    exit 1
fi

if ! command -v codex >/dev/null 2>&1; then
    echo "Codex is not on PATH." >&2
    exit 1
fi

if [[ -z "${STY:-}" ]]; then
    echo "Start this script inside the screen session described in research/START_LOCAL.md." >&2
    echo "That session supplies the independent five-hour safety cutoff." >&2
    exit 1
fi

mkdir -p .cache/matplotlib .cache/fontconfig
export MPLCONFIGDIR="$repo_root/.cache/matplotlib"
export XDG_CACHE_HOME="$repo_root/.cache"
source "$repo_root/.venv/bin/activate"

screen_session="$STY"
(
    sleep 18000
    screen -S "$screen_session" -p 0 -X stuff $'\003'
    sleep 60
    screen -S "$screen_session" -X quit
) </dev/null >/dev/null 2>&1 &
watchdog_pid=$!

codex_status=0
caffeinate -dimsu codex \
    --no-daemon \
    --search \
    --approve-for-me \
    --enable goals \
    --enable multi_agent \
    --no-alt-screen \
    -C "$repo_root" || codex_status=$?

# If Codex exits normally or fails during startup, do not leave a stale timer
# that can interrupt a later session. If Codex is still active at five hours,
# the watchdog remains responsible for the interrupt and hard screen shutdown.
if kill -0 "$watchdog_pid" 2>/dev/null; then
    kill "$watchdog_pid" 2>/dev/null || true
    wait "$watchdog_pid" 2>/dev/null || true
fi

exit "$codex_status"
