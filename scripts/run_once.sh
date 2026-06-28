#!/usr/bin/env bash
# run_once.sh — one durable, hands-off pipeline pass for cron/launchd.
#
# Runs Claude Code headlessly to execute the gig-pipeline skill: scan,
# qualify, apply (paced, within caps), check replies, draft deliverables.
# It will NOT send deliverables or touch payment — those stay human.
#
# Local cron example (every hour, 8am-9pm):
#   0 8-21 * * *  cd /path/to/Gig-work && ./scripts/run_once.sh >> logs/cron.log 2>&1
#
# Requires: claude CLI installed and authenticated, config.json filled in.
set -euo pipefail
cd "$(dirname "$0")/.."

# Reset the daily send-cap counter at the first run of a new day.
TODAY=$(date +%Y-%m-%d)
STAMP=".last_run_day"
if [ ! -f "$STAMP" ] || [ "$(cat "$STAMP" 2>/dev/null)" != "$TODAY" ]; then
  : > logs/sent-today.log
  echo "$TODAY" > "$STAMP"
fi

# Drive the orchestrator. -p runs a single headless prompt.
claude -p "run the gig pipeline (single pass). Respect all sending caps and the human-gated steps. End with the standard pipeline report." \
  --dangerously-skip-permissions 2>&1 || {
    echo "[$(date)] pipeline run failed" >&2
    exit 1
  }

python3 scripts/metrics.py >/dev/null 2>&1 || true
echo "[$(date)] pipeline run complete"
