#!/bin/zsh
set -euo pipefail
ROOT="$(cd "$(dirname "$0")" && pwd)"
export PYTHONPATH="$ROOT"

echo "ABRXOS ECOSYSTEM HOTFIX V3.1.1 · R6.1"
echo "========================================"
echo

echo "Cerrando procesos ABRXOS activos para evitar código viejo en memoria..."
pkill -f "$HOME/ABRXOS_GEOMETRA_V3/ABRXOS_GEOMETRA_V3.py" 2>/dev/null || true
pkill -f "$HOME/Applications/ABRXOS/ABRXOS_CONTENT_BUILDER_V1/app.py" 2>/dev/null || true
pkill -f "$HOME/Applications/ABRXOS/ABRXOS_X_BRAND_BUILDER_V1/app.py" 2>/dev/null || true
sleep 1

python3 -m tools.install_hotfix --root "$ROOT"

echo
echo "HOTFIX APLICADO Y VERIFICADO."
echo "Los directorios de datos no fueron modificados."
echo
if [[ -d "$HOME/Desktop/ABRXOS Geometra V3.app" ]]; then
  open "$HOME/Desktop/ABRXOS Geometra V3.app"
fi
