from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Any

EXCLUDED_DIRS = {'.pytest_cache', '__pycache__'}
EXCLUDED_SUFFIXES = {'.pyc', '.pyo'}


def _sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open('rb') as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b''):
            h.update(chunk)
    return h.hexdigest()


def _include(path: Path, root: Path) -> bool:
    rel = path.relative_to(root)
    if any(part in EXCLUDED_DIRS for part in rel.parts):
        return False
    if path.suffix in EXCLUDED_SUFFIXES:
        return False
    return path.is_file()


def build_manifest(root: Path, *, package: str | None = None, version: str | None = None) -> dict[str, Any]:
    root = Path(root)
    files = []
    for path in sorted(root.rglob('*')):
        if not _include(path, root):
            continue
        if path.name == 'PACKAGE_MANIFEST.json':
            continue
        files.append({
            'path': path.relative_to(root).as_posix(),
            'bytes': path.stat().st_size,
            'sha256': _sha256(path),
        })
    out = {'fileCountExcludingManifest': len(files), 'files': files}
    if package:
        out['package'] = package
    if version:
        out['version'] = version
    return out


def verify_manifest(root: Path, manifest: dict[str, Any]) -> list[str]:
    root = Path(root)
    errors: list[str] = []
    expected = {row['path']: row for row in manifest.get('files', [])}
    for rel, row in expected.items():
        path = root / rel
        if not path.exists():
            errors.append(f'missing:{rel}')
            continue
        if path.stat().st_size != int(row.get('bytes', -1)):
            errors.append(f'bytes:{rel}')
            continue
        if _sha256(path) != row.get('sha256'):
            errors.append(f'sha256:{rel}')
    actual = {p.relative_to(root).as_posix() for p in root.rglob('*') if _include(p, root) and p.name != 'PACKAGE_MANIFEST.json'}
    extra = sorted(actual - set(expected))
    errors.extend(f'extra:{rel}' for rel in extra)
    return errors
