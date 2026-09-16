#!/bin/zsh
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
source "$ROOT/tools/lib/python_resolver.zsh"
export PATH="$(dirname "$ABRXOS_PYTHON"):/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin:${PATH:-}"

GEO_SRC="$ROOT/apps/geometra/current"
CONTENT_SRC="$ROOT/apps/content-builder/current"
BRAND_SRC="$ROOT/apps/brand-builder/current"
GEO_DEST="$HOME/ABRXOS_GEOMETRA_V3"
GEO_APP="$HOME/Desktop/ABRXOS Geometra V3.app"
GEO_FALLBACK="$HOME/Desktop/ABRXOS Geometra V3.command"
GEO_LOG="$HOME/Library/Logs/abrxos_geometra_v3.log"

echo "ABRXOS · INSTALAR ECOSISTEMA DESDE CERO"
echo "========================================"
echo "Python: $ABRXOS_PYTHON"

after_capture_required() {
  echo "ERROR: apps/geometra/current todavía no contiene el snapshot real." >&2
  echo "En la Mac fuente ejecuta primero:" >&2
  echo "  zsh tools/DEJAR_REPO_LISTO.command" >&2
  echo "y sube/commit ese resultado a GitHub." >&2
  exit 10
}

[[ -f "$GEO_SRC/VERSION.json" && -f "$GEO_SRC/ABRXOS_GEOMETRA_V3.py" ]] || after_capture_required
[[ -f "$CONTENT_SRC/VERSION.json" && -f "$CONTENT_SRC/INSTALAR_ABRXOS_CONTENT_BUILDER_V1.command" ]] || { echo "ERROR: snapshot Content Builder incompleto"; exit 11; }
[[ -f "$BRAND_SRC/VERSION.json" && -f "$BRAND_SRC/INSTALAR_ABRXOS_X_BRAND_BUILDER_V1.command" ]] || { echo "ERROR: snapshot Brand Builder incompleto"; exit 12; }

mkdir -p "$HOME/ABRXOS_GEOMETRA_DATA" "$HOME/Library/Logs" "$HOME/Desktop"

echo
echo "1/3 Instalando Geometra 3.1.1 R6.1..."
mkdir -p "$GEO_DEST"
rsync -a --delete \
  --exclude '.git' --exclude '.DS_Store' --exclude '__pycache__' --exclude '.pytest_cache' --exclude '*.pyc' \
  "$GEO_SRC/" "$GEO_DEST/"
chmod +x "$GEO_DEST/ABRXOS_GEOMETRA_V3.py" 2>/dev/null || true

GEO_LAUNCHER="$GEO_DEST/LAUNCH_ABRXOS_GEOMETRA_V3.command"
cat > "$GEO_LAUNCHER" <<EOF
#!/bin/zsh
mkdir -p "$HOME/Library/Logs"
nohup "$ABRXOS_PYTHON" "$GEO_DEST/ABRXOS_GEOMETRA_V3.py" >> "$GEO_LOG" 2>&1 &
exit 0
EOF
chmod +x "$GEO_LAUNCHER"
rm -rf "$GEO_APP"
if command -v osacompile >/dev/null 2>&1; then
  osacompile -o "$GEO_APP" -e "do shell script \"/bin/zsh \" & quoted form of \"$GEO_LAUNCHER\"" >/dev/null
else
  cp "$GEO_LAUNCHER" "$GEO_FALLBACK"
  chmod +x "$GEO_FALLBACK"
fi

echo
echo "2/3 Instalando Content Builder 1.0.1 R6.1..."
/bin/zsh "$CONTENT_SRC/INSTALAR_ABRXOS_CONTENT_BUILDER_V1.command"

echo
echo "3/3 Instalando Brand Builder 1.0.1 R6.1..."
/bin/zsh "$BRAND_SRC/INSTALAR_ABRXOS_X_BRAND_BUILDER_V1.command"

echo
echo "Verificando versiones instaladas..."
"$ABRXOS_PYTHON" - "$HOME" <<'PY'
from pathlib import Path
import json,sys
home=Path(sys.argv[1])
checks={
 'geometra':(home/'ABRXOS_GEOMETRA_V3/VERSION.json','3.1.1'),
 'contentBuilder':(home/'Applications/ABRXOS/ABRXOS_CONTENT_BUILDER_V1/VERSION.json','1.0.1'),
 'brandBuilder':(home/'Applications/ABRXOS/ABRXOS_X_BRAND_BUILDER_V1/VERSION.json','1.0.1'),
}
for name,(p,expected) in checks.items():
    if not p.exists(): raise SystemExit(f'FALTA {name}: {p}')
    got=str(json.loads(p.read_text()).get('version'))
    if got!=expected: raise SystemExit(f'{name}: {got} != {expected}')
    print(f'✓ {name} {got}')
geo=home/'ABRXOS_GEOMETRA_V3/.abrxos_hotfixes/ABRXOS_ECOSYSTEM_V3_1_1_R6_1.json'
if not geo.exists(): raise SystemExit('Geometra: falta registry hotfix ecosystem R6.1')
print('✓ geometra hotfix R6.1 registry')
PY

echo
echo "ECOSISTEMA INSTALADO DESDE EL REPO."
echo "Apps:"
echo "  $HOME/Desktop/ABRXOS Geometra V3.app"
echo "  $HOME/Desktop/ABRXOS Content Builder.app"
echo "  $HOME/Desktop/ABRXOS X Brand Builder.app"
echo
echo "Datos persistentes (no fueron borrados):"
echo "  $HOME/ABRXOS_GEOMETRA_DATA"
echo "  $HOME/ABRXOS_CONTENT_BUILDER_DATA"
echo "  $HOME/ABRXOS_BRAND_BUILDER_DATA"
