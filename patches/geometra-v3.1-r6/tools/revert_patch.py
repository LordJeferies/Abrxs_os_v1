from __future__ import annotations
import json, shutil
from pathlib import Path
from typing import Any

REGISTRY_DIR = '.abrxos_patches'


def _registry(target: Path, patch_id: str) -> Path:
    return Path(target) / REGISTRY_DIR / f'{patch_id}.json'


def _restore_from_backup(target: Path, backup_dir: Path, record: dict[str, Any]) -> None:
    for row in record.get('files', []):
        rel = row['target']
        dst = target / rel
        if row.get('existed'):
            src = backup_dir / 'files' / rel
            if dst.exists():
                if dst.is_dir(): shutil.rmtree(dst)
                else: dst.unlink()
            dst.parent.mkdir(parents=True, exist_ok=True)
            if src.is_dir(): shutil.copytree(src, dst)
            else: shutil.copy2(src, dst)
        elif dst.exists():
            if dst.is_dir():
                shutil.rmtree(dst)
            else:
                dst.unlink()


def revert_patch(target: Path, backup_root: Path, backup_id: str | None = None, patch_id: str | None = None) -> dict[str, Any]:
    target = Path(target).expanduser().resolve()
    backup_root = Path(backup_root).expanduser().resolve()
    record = None
    backup_dir = None
    if backup_id:
        backup_dir = backup_root / backup_id
        meta = backup_dir / 'backup.json'
        if not meta.exists():
            raise RuntimeError(f'Backup no encontrado: {backup_id}')
        record = json.loads(meta.read_text(encoding='utf-8'))
    else:
        if patch_id:
            reg = _registry(target, patch_id)
            if not reg.exists():
                raise RuntimeError(f'Patch no registrado: {patch_id}')
            installed = json.loads(reg.read_text(encoding='utf-8'))
            backup_id = installed.get('backupId')
            backup_dir = backup_root / str(backup_id)
            record = json.loads((backup_dir/'backup.json').read_text(encoding='utf-8'))
        else:
            candidates = sorted(backup_root.glob('*/backup.json'), key=lambda p: p.parent.name, reverse=True)
            if not candidates:
                raise RuntimeError('No hay backups de patch disponibles.')
            backup_dir = candidates[0].parent
            record = json.loads(candidates[0].read_text(encoding='utf-8'))
            backup_id = backup_dir.name
    assert record is not None and backup_dir is not None
    _restore_from_backup(target, backup_dir, record)
    pid = record.get('patchId')
    if pid:
        reg = _registry(target, pid)
        if reg.exists():
            reg.unlink()
    return {'status':'reverted','patchId':pid,'backupId':backup_id,'target':str(target)}


if __name__ == '__main__':
    import argparse
    ap=argparse.ArgumentParser()
    ap.add_argument('--target',required=True)
    ap.add_argument('--backup-root',required=True)
    ap.add_argument('--backup-id')
    ap.add_argument('--patch-id')
    args=ap.parse_args()
    print(json.dumps(revert_patch(Path(args.target),Path(args.backup_root),args.backup_id,args.patch_id),indent=2,ensure_ascii=False))
