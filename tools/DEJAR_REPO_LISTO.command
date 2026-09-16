#!/bin/zsh
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
source "$ROOT/tools/lib/python_resolver.zsh"

echo "ABRXOS · DEJAR REPO LISTO"
echo "=========================="
echo "Python: $ABRXOS_PYTHON"
echo

/bin/zsh "$ROOT/tools/CAPTURAR_INSTALACION_ACTUAL.command"
/bin/zsh "$ROOT/tools/VERIFY_ALL.command"
/bin/zsh "$ROOT/tools/GENERAR_MANIFEST.command"

missing=0
for f in \
  "$ROOT/apps/geometra/current/INSTALAR_ABRXOS_GEOMETRA_V3.command" \
  "$ROOT/apps/content-builder/current/INSTALAR_ABRXOS_CONTENT_BUILDER_V1.command" \
  "$ROOT/apps/brand-builder/current/INSTALAR_ABRXOS_X_BRAND_BUILDER_V1.command"
do
  if [[ -f "$f" ]]; then
    echo "✓ $(basename "$f")"
  else
    echo "✗ FALTA $f"
    missing=1
  fi
done

if [[ "$missing" -ne 0 ]]; then
  echo
  echo "ERROR: el snapshot no contiene todos los instaladores esperados."
  exit 6
fi

echo
echo "REPO COMPLETO PARA SNAPSHOT ACTUAL."
echo "Siguiente paso:"
echo "  zsh \"$ROOT/tools/PREPARAR_REPO_GITHUB.command\""
