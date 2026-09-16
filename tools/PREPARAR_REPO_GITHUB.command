#!/bin/zsh
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

echo "ABRXS OS V1 · PREPARAR REPO GITHUB"
echo "===================================="

/bin/zsh "$ROOT/tools/VERIFY_ALL.command"
/bin/zsh "$ROOT/tools/GENERAR_MANIFEST.command"

# Critical safety invariant: ROOT itself owns .git. Never inherit $HOME/.git.
if [[ ! -d "$ROOT/.git" ]]; then
  git -C "$ROOT" init -b main
fi
TOP="$(git -C "$ROOT" rev-parse --show-toplevel)"
if [[ "$TOP" != "$ROOT" ]]; then
  echo "ERROR: Git root inesperado: $TOP" >&2
  echo "Esperado: $ROOT" >&2
  exit 20
fi

git -C "$ROOT" add -A

echo
echo "Archivos preparados dentro del repo correcto:"
git -C "$ROOT" status --short
cat > "$ROOT/GITHUB_NEXT_STEPS.txt" <<'TXT'
REPO OFICIAL: Abrxs_os_v1

1. Revisa:
   git status
   git diff --cached

2. Commit:
   git commit -m "Abrxs_os_v1 · ecosystem 3.1.1 R6.1 reproducible snapshot"

3. Crear repo PRIVADO con GitHub CLI:
   gh repo create Abrxs_os_v1 --private --source=. --remote=origin --push

4. Tag:
   git tag abrxs-os-v1.0.0-r6.1
   git push origin --tags
TXT

echo
echo "NO hice commit ni push automáticamente."
echo "Lee: $ROOT/GITHUB_NEXT_STEPS.txt"
