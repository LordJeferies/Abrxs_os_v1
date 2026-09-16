#!/bin/zsh
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
source "$ROOT/tools/lib/python_resolver.zsh"
export PATH="$(dirname "$ABRXOS_PYTHON"):$PATH"
exec /bin/zsh "$ROOT/apps/brand-builder/current/INSTALAR_ABRXOS_X_BRAND_BUILDER_V1.command"
