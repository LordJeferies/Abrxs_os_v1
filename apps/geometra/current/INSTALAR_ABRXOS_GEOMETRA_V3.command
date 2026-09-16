#!/bin/zsh
set -e

SRC="$HOME/Downloads/ABRXOS_GEOMETRA_V3"
DEST="$HOME/ABRXOS_GEOMETRA_V3"
APP="$HOME/Desktop/ABRXOS Geometra V3.app"
LOG="$HOME/Library/Logs/abrxos_geometra_v3.log"

echo "ABRXOS GEOMETRA V3 · INSTALADOR"
echo "================================"

if [[ ! -d "$SRC" ]]; then
  echo "No encuentro: $SRC"
  echo "Descomprime ABRXOS_GEOMETRA_V3_MAC.zip y deja ABRXOS_GEOMETRA_V3 dentro de Descargas."
  exit 1
fi
if ! command -v python3 >/dev/null 2>&1; then
  echo "Python 3 no está disponible en esta Mac."
  exit 1
fi

mkdir -p "$DEST" "$HOME/Library/Logs" "$HOME/ABRXOS_GEOMETRA_DATA"
rsync -a --delete --exclude '__pycache__' --exclude '.pytest_cache' "$SRC/" "$DEST/"
chmod +x "$DEST/ABRXOS_GEOMETRA_V3.py" "$DEST/RUN_GEOMETRA_V3.command"

TMPAS="/tmp/abrxos_geometra_v3_launcher.applescript"
cat > "$TMPAS" <<APPLESCRIPT
on run
  set cmd to "PATH=/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin nohup /usr/bin/env python3 " & quoted form of "$DEST/ABRXOS_GEOMETRA_V3.py" & " >>" & quoted form of "$LOG" & " 2>&1 &"
  do shell script cmd
end run
APPLESCRIPT

rm -rf "$APP"
osacompile -o "$APP" "$TMPAS"
rm -f "$TMPAS"

echo
echo "LISTO. App creada en:"
echo "  $APP"
echo
echo "Datos persistentes:"
echo "  $HOME/ABRXOS_GEOMETRA_DATA/library_v3.json"
echo
echo "Si existe library.json de V2/V2.1 y aún no existe library_v3.json, V3 crea una copia migrada. El archivo viejo no se modifica."
open "$APP"
