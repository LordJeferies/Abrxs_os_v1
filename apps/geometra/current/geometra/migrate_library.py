from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .core import normalize_project
from .library import Library


def migrate_legacy_library(legacy_path: Path, target_path: Path) -> dict[str, Any]:
    legacy_path = Path(legacy_path)
    target_path = Path(target_path)
    if target_path.exists() or not legacy_path.exists():
        return {'migrated': 0, 'skipped': True}
    try:
        legacy = json.loads(legacy_path.read_text(encoding='utf-8'))
    except Exception as exc:
        return {'migrated': 0, 'skipped': True, 'error': str(exc)}
    projects = legacy.get('projects') if isinstance(legacy, dict) else None
    if not isinstance(projects, dict):
        return {'migrated': 0, 'skipped': True}
    lib = Library(target_path)
    count = 0
    for project_id, source in projects.items():
        if not isinstance(source, dict):
            continue
        doc = normalize_project(source, f'legacy-library:{project_id}', 'legacy-library')
        lib.merge(doc)
        count += 1
    current = legacy.get('currentProjectId')
    if current and current in lib.data.get('projects', {}):
        lib.select(current)
    return {'migrated': count, 'skipped': False, 'target': str(target_path)}
