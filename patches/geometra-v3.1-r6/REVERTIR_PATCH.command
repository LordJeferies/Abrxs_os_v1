#!/bin/zsh
set -euo pipefail
ROOT="$(cd "$(dirname "$0")" && pwd)"
TARGET="${ABRXOS_GEOMETRA_TARGET:-$HOME/ABRXOS_GEOMETRA_V3}"
BACKUPS="${ABRXOS_GEOMETRA_PATCH_BACKUPS:-$HOME/ABRXOS_GEOMETRA_PATCH_BACKUPS}"
APP="$HOME/Desktop/ABRXOS Geometra V3.app"
PATCH_ID="ABRXOS_GEOMETRA_V3_1_R6"

echo "ABRXOS · REVERTIR PATCH V3.1 R6"
echo "================================"
echo "Target:  $TARGET"
echo "Backups: $BACKUPS"
pkill -f "$TARGET/ABRXOS_GEOMETRA_V3.py" 2>/dev/null || true
python3 "$ROOT/tools/revert_patch.py" --target "$TARGET" --backup-root "$BACKUPS" --patch-id "$PATCH_ID"
echo "Patch revertido. Tus datos en ABRXOS_GEOMETRA_DATA no fueron tocados."
if [[ -d "$APP" ]]; then open "$APP"; fi
