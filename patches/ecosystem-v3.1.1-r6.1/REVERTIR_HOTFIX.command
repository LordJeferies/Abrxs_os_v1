#!/bin/zsh
set -euo pipefail
ROOT="$(cd "$(dirname "$0")" && pwd)"
export PYTHONPATH="$ROOT"
pkill -f "$HOME/ABRXOS_GEOMETRA_V3/ABRXOS_GEOMETRA_V3.py" 2>/dev/null || true
pkill -f "$HOME/Applications/ABRXOS/ABRXOS_CONTENT_BUILDER_V1/app.py" 2>/dev/null || true
pkill -f "$HOME/Applications/ABRXOS/ABRXOS_X_BRAND_BUILDER_V1/app.py" 2>/dev/null || true
python3 -m tools.revert_hotfix
if [[ -d "$HOME/Desktop/ABRXOS Geometra V3.app" ]]; then open "$HOME/Desktop/ABRXOS Geometra V3.app"; fi
