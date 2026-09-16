#!/bin/zsh
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
source "$ROOT/tools/lib/python_resolver.zsh"

GEO="$HOME/ABRXOS_GEOMETRA_V3"
CONTENT="$HOME/Applications/ABRXOS/ABRXOS_CONTENT_BUILDER_V1"
BRAND="$HOME/Applications/ABRXOS/ABRXOS_X_BRAND_BUILDER_V1"

echo "ABRXOS · CAPTURAR INSTALACIÓN ACTUAL"
echo "====================================="
echo "Python: $ABRXOS_PYTHON"

for spec in "geometra:$GEO:3.1.1" "contentBuilder:$CONTENT:1.0.1" "brandBuilder:$BRAND:1.0.1"; do
  name="${spec%%:*}"
  rest="${spec#*:}"
  install_path="${rest%:*}"
  expected="${rest##*:}"
  if [[ ! -d "$install_path" || ! -f "$install_path/VERSION.json" ]]; then
    echo "ERROR: $name no encontrado en $install_path"
    exit 2
  fi
  found="$("$ABRXOS_PYTHON" - "$install_path/VERSION.json" <<'PY'
import json,sys
print(json.load(open(sys.argv[1])).get('version',''))
PY
)"
  if [[ "$found" != "$expected" ]]; then
    echo "ERROR: $name versión $found; este repo espera $expected"
    echo "No capturo una versión distinta sin actualizar CURRENT_RELEASE_LOCK.json primero."
    exit 3
  fi
  echo "✓ $name $found"
done

if [[ ! -f "$GEO/.abrxos_hotfixes/ABRXOS_ECOSYSTEM_V3_1_1_R6_1.json" ]]; then
  echo "ERROR: Geometra 3.1.1 no tiene registry del hotfix ecosystem R6.1."
  exit 4
fi

capture() {
  local src="$1" dst="$2"
  mkdir -p "$dst"
  rsync -a --delete \
    --exclude '.git' \
    --exclude '.DS_Store' \
    --exclude '__pycache__' \
    --exclude '.pytest_cache' \
    --exclude '*.pyc' \
    --exclude '*.pyo' \
    --exclude 'LAUNCH_*.command' \
    --exclude '*.log' \
    --exclude '*.tmp' \
    "$src/" "$dst/"
}

echo
echo "Capturando código instalado..."
capture "$GEO" "$ROOT/apps/geometra/current"
capture "$CONTENT" "$ROOT/apps/content-builder/current"
capture "$BRAND" "$ROOT/apps/brand-builder/current"

find "$ROOT/apps" -type f -name 'LAUNCH_*.command' -delete 2>/dev/null || true
find "$ROOT/apps" -type d \( -name '__pycache__' -o -name '.pytest_cache' \) -prune -exec rm -rf {} + 2>/dev/null || true
find "$ROOT/apps" -type f \( -name '*.pyc' -o -name '*.pyo' -o -name '.DS_Store' \) -delete 2>/dev/null || true

"$ABRXOS_PYTHON" - "$ROOT" "$GEO" "$CONTENT" "$BRAND" <<'PY'
from pathlib import Path
import json,datetime,sys
root=Path(sys.argv[1])
components={}
for name,install_path in [('geometra',Path(sys.argv[2])),('contentBuilder',Path(sys.argv[3])),('brandBuilder',Path(sys.argv[4]))]:
    v=json.loads((install_path/'VERSION.json').read_text())
    components[name]={'source':str(install_path),'version':v.get('version'),'canonFamily':v.get('canonFamily',v.get('canon')),'canonRevision':v.get('canonRevision')}
report={'schemaVersion':'abrxos.local-capture-report.v1','capturedAt':datetime.datetime.now(datetime.timezone.utc).isoformat(),'components':components,'protectedDataDirectories':['~/ABRXOS_GEOMETRA_DATA','~/ABRXOS_CONTENT_BUILDER_DATA','~/ABRXOS_CONTENT_BUILDER_EXPORTS','~/ABRXOS_BRAND_BUILDER_DATA','~/ABRXOS_BRAND_BUILDER_EXPORTS']}
(root/'LOCAL_CAPTURE_REPORT.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
print(json.dumps(report,ensure_ascii=False,indent=2))
PY

"$ABRXOS_PYTHON" "$ROOT/tools/GENERAR_MANIFEST.py"
echo
echo "CAPTURA COMPLETA. Ahora ejecuta:"
echo "  zsh \"$ROOT/tools/VERIFY_ALL.command\""
