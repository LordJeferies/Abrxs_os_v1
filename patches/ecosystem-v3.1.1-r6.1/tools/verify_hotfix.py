from __future__ import annotations

import hashlib
import importlib.util
import json
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any

from .apply_hotfix import HOTFIX_ID, default_targets

R6_LIBRARY_NAMES = (
    'XR_FAMILIES_R6.json',
    'EDIT_PROFILES_R6.json',
    'CINE_LIBRARY_R6.json',
    'SFX_LIBRARY_R6.json',
    'MOTION_LIBRARY_R6.json',
    'MUSIC_LIBRARY_R6.json',
    'CAPTIONS_R6.json',
)


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding='utf-8'))


def _sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open('rb') as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b''):
            h.update(chunk)
    return h.hexdigest()


def _load_module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f'No se pudo cargar {path}')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _check_engine_contract(key: str, engine: Path, errors: list[str], checks: list[str]):
    cp = subprocess.run([sys.executable, '-m', 'py_compile', str(engine)], capture_output=True, text=True)
    if cp.returncode:
        errors.append(f'{key} py_compile: {cp.stderr.strip()}')
        return None
    try:
        module = _load_module(engine, f'_verify_{key}')
    except Exception as exc:
        errors.append(f'{key} import: {exc}')
        return None
    if getattr(module, 'CANON_FAMILY', None) != 'R6':
        errors.append(f'{key} canonFamily={getattr(module, "CANON_FAMILY", None)}')
    if getattr(module, 'CANON_REVISION', None) != 'R6.1':
        errors.append(f'{key} canonRevision={getattr(module, "CANON_REVISION", None)}')
    if not any(x.startswith(f'{key} canon') for x in errors):
        checks.append(f'{key}_canon_handshake=PASS')
    return module


def verify_hotfix(root: Path, *, home: Path | None = None, targets: dict[str, Path] | None = None) -> dict[str, Any]:
    root = Path(root).resolve()
    home = Path(home or Path.home()).expanduser().resolve()
    targets = targets or default_targets(home)
    errors: list[str] = []
    warnings: list[str] = []
    checks: list[str] = []
    components: dict[str, str] = {}

    geo = targets['geometra']
    geo_start = len(errors)
    if not geo.exists():
        errors.append(f'Geometra no encontrado: {geo}')
    else:
        version_file = geo / 'VERSION.json'
        if not version_file.exists():
            errors.append('Geometra VERSION.json faltante')
        else:
            v = _load(version_file)
            if v.get('version') != '3.1.1':
                errors.append(f'Geometra version={v.get("version")}')
        if not (geo / '.abrxos_hotfixes' / f'{HOTFIX_ID}.json').exists():
            errors.append('Geometra hotfix registry faltante')
        for rel in ('geometra/r6.py', 'shared/r6_patch.js', 'app/r6_patch.js', 'app/r6_patch.css', 'r6/R6_1_CONTRACT.json'):
            if not (geo / rel).exists():
                errors.append(f'Geometra falta {rel}')
        r6py = geo / 'geometra/r6.py'
        if r6py.exists():
            cp = subprocess.run([sys.executable, '-m', 'py_compile', str(r6py)], capture_output=True, text=True)
            if cp.returncode:
                errors.append(f'Geometra r6.py py_compile: {cp.stderr.strip()}')
            else:
                try:
                    mod = _load_module(r6py, '_verify_r61')
                    if 'sourceAlignment' not in mod.CHECKLIST_KEYS:
                        errors.append('Geometra R6.1 checklist no activo')
                    if getattr(mod, 'VALIDATION_SCHEMA', '') != 'abrxos.r6-validation.v1.1':
                        errors.append(f'Geometra validation schema={getattr(mod, "VALIDATION_SCHEMA", None)}')
                    if len(errors) == geo_start:
                        checks.append('geometra_r61_validator=PASS')
                except Exception as exc:
                    errors.append(f'Geometra r6 import: {exc}')
        node = shutil.which('node')
        if node:
            for rel in ('shared/r6_patch.js', 'app/r6_patch.js'):
                file = geo / rel
                if file.exists():
                    cp = subprocess.run([node, '--check', str(file)], capture_output=True, text=True)
                    if cp.returncode:
                        errors.append(f'{rel}: {cp.stderr.strip()}')
    components['geometra'] = 'PASS' if len(errors) == geo_start else 'REVIEW'

    for key, engine_name in (('contentBuilder', 'content_engine.py'), ('brandBuilder', 'brand_engine.py')):
        target = targets[key]
        if not target.exists():
            components[key] = 'SKIPPED_MISSING'
            continue
        start_errors = len(errors)
        version_file = target / 'VERSION.json'
        version = _load(version_file) if version_file.exists() else {}
        if version.get('version') != '1.0.1':
            errors.append(f'{key} version={version.get("version")}')
        if not (target / '.abrxos_hotfixes' / f'{HOTFIX_ID}.json').exists():
            errors.append(f'{key} registry faltante')
        engine = target / engine_name
        module = None
        if not engine.exists():
            errors.append(f'{key} engine faltante')
        else:
            module = _check_engine_contract(key, engine, errors, checks)

        if key == 'contentBuilder':
            for rel in (
                'resources/r6_1/12_R6_1_SOURCE_ALIGNMENT.txt',
                'resources/r6_1/13_R6_1_VO_ROUTE_CAPTIONS.txt',
                'resources/r6_1/14_LIENZO_PROJECTION_CONTRACT.json',
            ):
                if not (target / rel).exists():
                    errors.append(f'Content Builder falta {rel}')
            lib_dir = target / 'resources' / 'canon_r6' / 'libraries'
            mismatch = False
            for name in R6_LIBRARY_NAMES:
                content_lib = lib_dir / name
                geo_lib = geo / 'r6' / name
                if not content_lib.exists():
                    errors.append(f'contentBuilder library faltante {name}')
                    mismatch = True
                elif not geo_lib.exists():
                    errors.append(f'Geometra library faltante {name}')
                    mismatch = True
                elif _sha256(content_lib) != _sha256(geo_lib):
                    errors.append(f'contentBuilder/Geometra library hash mismatch: {name}')
                    mismatch = True
            if not mismatch:
                checks.append('content_geometra_library_hashes=PASS')
            if module is not None:
                features = set(getattr(module, 'R61_FEATURES', []))
                expected = {'sourceAlignment', 'microtrim', 'voAdded', 'routeSemanticsR61', 'captionGroupsR6', 'shortSourceException', 'projectionReady'}
                if not expected <= features:
                    errors.append(f'contentBuilder features incompletas: {sorted(expected - features)}')
        elif key == 'brandBuilder':
            adapter = target / 'resources' / 'brand_adapter_template.json'
            if not adapter.exists():
                errors.append('brandBuilder brand_adapter_template.json faltante')
            else:
                try:
                    obj = _load(adapter)
                    if obj.get('schemaVersion') != 'abrxos.brand-adapter.r6':
                        errors.append(f'brandBuilder schemaVersion={obj.get("schemaVersion")}')
                    if obj.get('adapterVersion') != 'R6.1':
                        errors.append(f'brandBuilder adapterVersion={obj.get("adapterVersion")}')
                    if obj.get('schemaVersion') == 'abrxos.brand-adapter.r6' and obj.get('adapterVersion') == 'R6.1':
                        checks.append('brand_adapter_contract=PASS')
                except Exception as exc:
                    errors.append(f'brandBuilder brand adapter parse: {exc}')

        components[key] = 'PASS' if len(errors) == start_errors else 'REVIEW'

    return {
        'ok': not errors,
        'hotfixId': HOTFIX_ID,
        'errors': errors,
        'warnings': warnings,
        'checks': checks,
        'components': components,
    }


if __name__ == '__main__':
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument('--root', required=True)
    ap.add_argument('--home')
    args = ap.parse_args()
    report = verify_hotfix(Path(args.root), home=Path(args.home).expanduser() if args.home else None)
    print(json.dumps(report, ensure_ascii=False, indent=2))
    raise SystemExit(0 if report['ok'] else 2)
