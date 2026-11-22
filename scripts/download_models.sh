#!/usr/bin/env bash
# Download openly licensed ComfyUI weights into the official models directory.
# Usage:
#   download_models.sh                  # uses MODELS or HK_DOWNLOAD_MODELS
#   download_models.sh sdxl-turbo
#   download_models.sh flux-schnell,sdxl
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
candidates=(
    "${SCRIPT_DIR}/download_models.py"
    "${SCRIPT_DIR}/scripts/download_models.py"
    "/opt/homelab-kompass/scripts/download_models.py"
    "/workspace/homelab-kompass/scripts/download_models.py"
)
PY=""
for c in "${candidates[@]}"; do
    if [[ -f "${c}" ]]; then
        PY="${c}"
        break
    fi
done
if [[ -z "${PY}" ]]; then
    echo "[homelab-kompass] Cannot find download_models.py" >&2
    exit 1
fi

if [[ -n "${1:-}" ]]; then
    export MODELS="$1"
fi

exec python3 "${PY}"
