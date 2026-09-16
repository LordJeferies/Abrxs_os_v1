#!/bin/zsh
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
compare(){ local src="$1" dst="$2" name="$3"; echo; echo "=== $name ==="; rsync -ani --delete --exclude '.git' --exclude '.DS_Store' --exclude '__pycache__' --exclude '.pytest_cache' --exclude '*.pyc' --exclude '*.log' "$src/" "$dst/" | head -200; }
compare "$HOME/ABRXOS_GEOMETRA_V3" "$ROOT/apps/geometra/current" "GEOMETRA"
compare "$HOME/Applications/ABRXOS/ABRXOS_CONTENT_BUILDER_V1" "$ROOT/apps/content-builder/current" "CONTENT BUILDER"
compare "$HOME/Applications/ABRXOS/ABRXOS_X_BRAND_BUILDER_V1" "$ROOT/apps/brand-builder/current" "BRAND BUILDER"
echo;echo "Sin salida en una sección = snapshot coincide con instalación para los archivos comparados."
