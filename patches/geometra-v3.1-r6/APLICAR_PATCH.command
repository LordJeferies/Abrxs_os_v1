#!/bin/zsh
set -euo pipefail
ROOT="$(cd "$(dirname "$0")" && pwd)"
TARGET="${ABRXOS_GEOMETRA_TARGET:-$HOME/ABRXOS_GEOMETRA_V3}"
BACKUPS="${ABRXOS_GEOMETRA_PATCH_BACKUPS:-$HOME/ABRXOS_GEOMETRA_PATCH_BACKUPS}"
APP="$HOME/Desktop/ABRXOS Geometra V3.app"
PATCH_ID="ABRXOS_GEOMETRA_V3_1_R6"

echo "ABRXOS · PATCH GEOMETRA V3.1 R6"
echo "================================"
echo "Target:  $TARGET"
echo "Backups: $BACKUPS"
echo

if [[ ! -d "$TARGET" ]]; then
  echo "ERROR: no encuentro la instalación Geometra V3 en: $TARGET"
  exit 1
fi

# Stop only the local Geometra process that is executing this installation.
pkill -f "$TARGET/ABRXOS_GEOMETRA_V3.py" 2>/dev/null || true

python3 "$ROOT/tools/apply_patch.py" --target "$TARGET" --patch-root "$ROOT" --backup-root "$BACKUPS"

if ! python3 "$ROOT/tools/verify_patch.py" --target "$TARGET" --patch-root "$ROOT"; then
  echo
  echo "VERIFICACIÓN FALLÓ. Restaurando automáticamente el backup..."
  python3 "$ROOT/tools/revert_patch.py" --target "$TARGET" --backup-root "$BACKUPS" --patch-id "$PATCH_ID" || true
  echo "La instalación anterior fue restaurada."
  exit 1
fi

echo
echo "PATCH V3.1 R6 APLICADO Y VERIFICADO."
if [[ -d "$APP" ]]; then
  echo "Abriendo la misma app instalada: $APP"
  open "$APP"
else
  echo "La app de Escritorio no fue encontrada; el código quedó actualizado en $TARGET."
fi
