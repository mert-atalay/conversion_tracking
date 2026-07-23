#!/usr/bin/env bash
set -euo pipefail

case "${PARENT_ACTIVATION_JOB:-poll}" in
  poll)
    exec python /app/tools/warehouse/run_parent_greenrope_lifecycle.py "$@"
    ;;
  dispatch)
    exec python /app/tools/warehouse/dispatch_parent_offline_conversions.py "$@"
    ;;
  diagnostics)
    exec python /app/tools/warehouse/refresh_parent_google_diagnostics.py "$@"
    ;;
  identity_binder)
    exec python /app/tools/warehouse/run_parent_greenrope_identity_binder.py "$@"
    ;;
  *)
    echo "Unsupported PARENT_ACTIVATION_JOB" >&2
    exit 2
    ;;
esac
