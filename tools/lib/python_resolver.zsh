#!/bin/zsh
# Shared Python resolver for ABRXOS repo tooling.
# Safe to source from any repo tool. Does not assume PATH is configured.
abrxos_find_python() {
  local candidate framework_candidate

  candidate="$(command -v python3 2>/dev/null || true)"
  if [[ -n "$candidate" && -x "$candidate" ]]; then
    print -r -- "$candidate"
    return 0
  fi

  for candidate in \
    /opt/homebrew/bin/python3 \
    /usr/local/bin/python3 \
    /usr/bin/python3
  do
    if [[ -x "$candidate" ]]; then
      print -r -- "$candidate"
      return 0
    fi
  done

  framework_candidate="$(/bin/ls -1dt /Library/Frameworks/Python.framework/Versions/*/bin/python3 2>/dev/null | /usr/bin/head -n 1 || true)"
  if [[ -n "$framework_candidate" && -x "$framework_candidate" ]]; then
    print -r -- "$framework_candidate"
    return 0
  fi

  return 1
}

if [[ -z "${ABRXOS_PYTHON:-}" || ! -x "${ABRXOS_PYTHON:-}" ]]; then
  ABRXOS_PYTHON="$(abrxos_find_python || true)"
fi

if [[ -z "$ABRXOS_PYTHON" ]]; then
  echo "ERROR: No se encontró Python 3." >&2
  echo "Instala Python 3 y vuelve a ejecutar este comando." >&2
  echo "Rutas comprobadas: PATH, Homebrew, /usr/local, /usr/bin y Python.framework." >&2
  return 70 2>/dev/null || exit 70
fi

export ABRXOS_PYTHON
# Make child scripts that still use `command -v python3` see the same interpreter.
export PATH="$(dirname "$ABRXOS_PYTHON"):/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin:${PATH:-}"
