#!/usr/bin/env sh
# Local scan wrapper for cron.
#
# Runs entirely on this machine: stdlib Python, no model, no cloud runner.
# DCSA blocks hosted CI runners, so the scan has to originate from an ordinary
# desktop connection.

set -u

PROJECT="$(cd "$(dirname "$0")/../.." && pwd)"
LIBRARY="${DCSA_LIBRARY:-$HOME/Documents/DCSA Library}"
ALERTS="${DCSA_ALERTS:-$HOME/Desktop}"

if [ $# -lt 1 ]; then
  echo "Usage: run-scan.sh <job-id>" >&2
  echo "Jobs are declared in config/schedule.json" >&2
  exit 64
fi

job="$1"
cd "$PROJECT" || exit 1
python3 custodian.py scheduled-scan --job "$job" --library "$LIBRARY"
code=$?

report="$PROJECT/state/reports/$job-latest.txt"
# 0 clean, 1 incomplete, 3 findings, 4 library integrity problem
case "$code" in
  3) [ -f "$report" ] && cp "$report" "$ALERTS/DCSA-SCAN-FINDINGS.txt" ;;
  1) [ -f "$report" ] && cp "$report" "$ALERTS/DCSA-SCAN-INCOMPLETE.txt" ;;
  4) [ -f "$report" ] && cp "$report" "$ALERTS/DCSA-LIBRARY-PROBLEM.txt" ;;
esac

exit $code
