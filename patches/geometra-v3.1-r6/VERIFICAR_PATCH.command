#!/bin/zsh
set -euo pipefail
ROOT="$(cd "$(dirname "$0")" && pwd)"
TARGET="${ABRXOS_GEOMETRA_TARGET:-$HOME/ABRXOS_GEOMETRA_V3}"
BACKUPS="${ABRXOS_GEOMETRA_PATCH_BACKUPS:-$HOME/ABRXOS_GEOMETRA_PATCH_BACKUPS}"
echo "ABRXOS · VERIFICAR PATCH V3.1 R6"
echo "Target:  $TARGET"
echo "Backups: $BACKUPS"
python3 "$ROOT/tools/verify_patch.py" --target "$TARGET" --patch-root "$ROOT"
