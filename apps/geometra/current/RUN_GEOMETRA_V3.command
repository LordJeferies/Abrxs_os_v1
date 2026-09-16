#!/bin/zsh
set -e
ROOT="$(cd "$(dirname "$0")" && pwd)"
cd "$ROOT"
exec /usr/bin/env python3 "$ROOT/ABRXOS_GEOMETRA_V3.py"
