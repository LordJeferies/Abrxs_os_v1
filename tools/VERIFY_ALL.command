#!/bin/zsh
set -e
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
source "$ROOT/tools/lib/python_resolver.zsh"
exec "$ABRXOS_PYTHON" "$ROOT/tools/verify_repo.py"
