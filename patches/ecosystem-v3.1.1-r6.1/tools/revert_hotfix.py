from __future__ import annotations
import json, shutil
from pathlib import Path
from typing import Any
from .apply_hotfix import HOTFIX_ID, BACKUP_DIRNAME, _restore_component


def revert_hotfix(*, home: Path | None=None, backup_id: str | None=None, backup_root: Path | None=None) -> dict[str,Any]:
    home=Path(home or Path.home()).expanduser().resolve(); root=Path(backup_root or (home/BACKUP_DIRNAME))
    if backup_id: state_dir=root/backup_id
    else:
        candidates=sorted(root.glob(f'{HOTFIX_ID}_*/hotfix.json'),key=lambda p:p.parent.name,reverse=True)
        if not candidates: raise RuntimeError('No hay backups de este hotfix.')
        state_dir=candidates[0].parent; backup_id=state_dir.name
    meta=state_dir/'hotfix.json'
    if not meta.exists(): raise RuntimeError(f'Backup no encontrado: {backup_id}')
    state=json.loads(meta.read_text(encoding='utf-8'))
    for name,record in reversed(list((state.get('components') or {}).items())):
        _restore_component(record,state_dir/name)
    return {'status':'reverted','hotfixId':HOTFIX_ID,'backupId':backup_id}

if __name__=='__main__':
    import argparse
    ap=argparse.ArgumentParser();ap.add_argument('--home');ap.add_argument('--backup-id');args=ap.parse_args()
    print(json.dumps(revert_hotfix(home=Path(args.home).expanduser() if args.home else None,backup_id=args.backup_id),ensure_ascii=False,indent=2))
