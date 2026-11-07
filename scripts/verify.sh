#!/usr/bin/env bash
set -Eeuo pipefail
HOST_PORT="${HOST_PORT:-8000}"
BASE="http://127.0.0.1:${HOST_PORT}"

curl --fail --show-error --silent "$BASE/health" | python3 -m json.tool
curl --fail --show-error --silent "$BASE/deployment" | python3 -m json.tool
curl --fail --show-error --silent "$BASE/" >/dev/null

if [ -n "${DEPLOY_VERSION:-}" ]; then
  RECEIVED=$(curl --fail --show-error --silent "$BASE/deployment" | python3 -c 'import json,sys; print(json.load(sys.stdin)["commit"])')
  if [ "$RECEIVED" != "$DEPLOY_VERSION" ]; then
    echo "ERROR: Expected commit $DEPLOY_VERSION but service reports $RECEIVED" >&2
    exit 1
  fi
fi

echo "Deployed version verified at $BASE"
if [ -n "${GITHUB_STEP_SUMMARY:-}" ]; then
  {
    echo "## HW3 Deployment Verification"
    echo "- Local URL: $BASE"
    echo "- Commit: ${DEPLOY_VERSION:-manual}"
    echo "- API: /health and /deployment returned HTTP 200"
  } >> "$GITHUB_STEP_SUMMARY"
fi
