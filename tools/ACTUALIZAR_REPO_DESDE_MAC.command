#!/bin/zsh
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
source "$ROOT/tools/lib/python_resolver.zsh"
/bin/zsh "$ROOT/tools/CAPTURAR_INSTALACION_ACTUAL.command"
/bin/zsh "$ROOT/tools/VERIFY_ALL.command"
"$ABRXOS_PYTHON" "$ROOT/tools/GENERAR_MANIFEST.py"
echo
echo "✓ Snapshot actual capturado y verificado."
echo "Revisa git diff antes de commit."
