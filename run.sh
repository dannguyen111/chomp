#!/usr/bin/env bash
# Watchdog. Cron this hourly if you like -- the lock guarantees that only one
# session ever runs, so an hourly trigger just means "start a session if none
# is alive", not "start 24 sessions a day".
#
#   0 * * * * cd /path/to/chomp && ./run.sh 01-recurrence >> runs/cron.log 2>&1
set -euo pipefail
cd "$(dirname "$0")"
ISLAND="${1:-01-recurrence}"

# The key lives in .env (gitignored) or already in the environment.
if [ -z "${OPENROUTER_API_KEY:-}" ] && [ -f .env ]; then
  set -a; . ./.env; set +a
fi
if [ -z "${OPENROUTER_API_KEY:-}" ]; then
  echo "OPENROUTER_API_KEY is not set and .env does not define it" >&2
  exit 1
fi

run() {
  python -m harness.session \
    --root . --island "$ISLAND" --session-cap "${SESSION_CAP:-3.00}"
}

# flock is absent on Git Bash for Windows and on stock macOS. mkdir is atomic
# on every filesystem we care about, so fall back to it rather than running
# unlocked -- two concurrent sessions would race the ledger.
if command -v flock >/dev/null 2>&1; then
  exec 9>.session.lock
  if ! flock -n 9; then
    echo "a session is already running (.session.lock is held)" >&2
    exit 1
  fi
  run
else
  if ! mkdir .session.lock.d 2>/dev/null; then
    echo "a session is already running (remove .session.lock.d if stale)" >&2
    exit 1
  fi
  trap 'rmdir .session.lock.d 2>/dev/null || true' EXIT
  run
fi
