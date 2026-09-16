#!/bin/zsh
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
INSTALL_DIR="$HOME/Applications/ABRXOS/ABRXOS_X_BRAND_BUILDER_V1"
APP_OUT="$HOME/Desktop/ABRXOS X Brand Builder.app"
FALLBACK="$HOME/Desktop/ABRXOS X Brand Builder.command"
LOG_DIR="$HOME/Library/Logs"
LOG_FILE="$LOG_DIR/abrxos_x_brand_builder_v1.log"
PYTHON_BIN="$(command -v python3 || true)"
if [[ -z "$PYTHON_BIN" ]]; then
  echo "ERROR: No se encontró python3. Instala Python 3 y vuelve a ejecutar." >&2
  read -k 1 "?Pulsa una tecla para cerrar..."; exit 1
fi
mkdir -p "$INSTALL_DIR" "$LOG_DIR" "$HOME/ABRXOS_BRAND_BUILDER_DATA" "$HOME/ABRXOS_BRAND_BUILDER_EXPORTS"
rsync -a --delete --exclude 'tests' --exclude '__pycache__' "$SCRIPT_DIR/" "$INSTALL_DIR/"
LAUNCHER="$INSTALL_DIR/LAUNCH_ABRXOS_X_BRAND_BUILDER.command"
cat > "$LAUNCHER" <<EOF
#!/bin/zsh
mkdir -p "$LOG_DIR"
nohup "$PYTHON_BIN" "$INSTALL_DIR/app.py" >> "$LOG_FILE" 2>&1 &
exit 0
EOF
chmod +x "$LAUNCHER"
rm -rf "$APP_OUT"
if command -v osacompile >/dev/null 2>&1; then
  osacompile -o "$APP_OUT" -e "do shell script \"/bin/zsh \" & quoted form of \"$LAUNCHER\"" >/dev/null
  echo "✓ App creada: $APP_OUT"
else
  echo "⚠ osacompile no disponible; se creará launcher .command."
fi
cp "$LAUNCHER" "$FALLBACK"; chmod +x "$FALLBACK"
echo "✓ Instalado en: $INSTALL_DIR"
echo "✓ Datos: $HOME/ABRXOS_BRAND_BUILDER_DATA"
echo "✓ Exports: $HOME/ABRXOS_BRAND_BUILDER_EXPORTS"
echo "✓ Python: $PYTHON_BIN"
if [[ -d "$APP_OUT" ]]; then open "$APP_OUT"; else open "$FALLBACK"; fi
