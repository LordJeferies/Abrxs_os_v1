#!/bin/zsh
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
source "$ROOT/tools/lib/python_resolver.zsh"
export PATH="$(dirname "$ABRXOS_PYTHON"):$PATH"
echo "Instalando ABRXOS X Brand Builder current..."
/bin/zsh "$ROOT/apps/brand-builder/current/INSTALAR_ABRXOS_X_BRAND_BUILDER_V1.command"
echo "Instalando ABRXOS Content Builder current..."
/bin/zsh "$ROOT/apps/content-builder/current/INSTALAR_ABRXOS_CONTENT_BUILDER_V1.command"
echo "✓ Builders instalados desde apps/*/current."
