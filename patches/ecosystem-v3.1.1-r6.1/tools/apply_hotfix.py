from __future__ import annotations

import datetime as dt
import json
import shutil
from pathlib import Path
from typing import Any

HOTFIX_ID = 'ABRXOS_ECOSYSTEM_V3_1_1_R6_1'
BACKUP_DIRNAME = 'ABRXOS_ECOSYSTEM_HOTFIX_BACKUPS'

R6_BASELINE_FILES = (
    'r6/XR_FAMILIES_R6.json',
    'r6/EDIT_PROFILES_R6.json',
    'r6/CINE_LIBRARY_R6.json',
    'r6/SFX_LIBRARY_R6.json',
    'r6/MOTION_LIBRARY_R6.json',
    'r6/MUSIC_LIBRARY_R6.json',
    'r6/CAPTIONS_R6.json',
)


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding='utf-8'))


def _write(path: Path, obj: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


def default_targets(home: Path) -> dict[str, Path]:
    return {
        'geometra': home / 'ABRXOS_GEOMETRA_V3',
        'contentBuilder': home / 'Applications' / 'ABRXOS' / 'ABRXOS_CONTENT_BUILDER_V1',
        'brandBuilder': home / 'Applications' / 'ABRXOS' / 'ABRXOS_X_BRAND_BUILDER_V1',
    }


def _component_spec(root: Path) -> dict[str, dict[str, Any]]:
    return {
        'geometra': {
            'required': True,
            'files': [
                ('PATCH_GEOMETRA/geometra/r6.py', 'geometra/r6.py'),
                ('PATCH_GEOMETRA/shared/r6_patch.js', 'shared/r6_patch.js'),
                ('PATCH_GEOMETRA/app/r6_patch.js', 'app/r6_patch.js'),
                ('PATCH_GEOMETRA/app/r6_patch.css', 'app/r6_patch.css'),
                ('PATCH_GEOMETRA/r6/R6_1_CONTRACT.json', 'r6/R6_1_CONTRACT.json'),
            ],
            'version': {'version':'3.1.1','hotfix':HOTFIX_ID,'canonFamily':'R6','canonRevision':'R6.1'},
        },
        'contentBuilder': {
            'required': False,
            'files': [
                ('PATCH_CONTENT_BUILDER/content_engine.py', 'content_engine.py'),
                ('PATCH_CONTENT_BUILDER/resources/r6_1', 'resources/r6_1'),
            ],
            'version': {'version':'1.0.1','hotfix':HOTFIX_ID,'canon':'R6','canonFamily':'R6','canonRevision':'R6.1'},
        },
        'brandBuilder': {
            'required': False,
            'files': [('PATCH_BRAND_BUILDER/brand_engine.py', 'brand_engine.py')],
            'version': {'version':'1.0.1','hotfix':HOTFIX_ID,'canon':'R6','canonFamily':'R6','canonRevision':'R6.1'},
        },
    }


def _precheck_component(name: str, target: Path, required: bool) -> str:
    if not target.exists():
        if required:
            raise RuntimeError(f'{name}: instalación no encontrada: {target}')
        return 'skipped_missing'
    vf = target / 'VERSION.json'
    if not vf.exists():
        raise RuntimeError(f'{name}: VERSION.json no encontrado')
    version = str(_load(vf).get('version') or '')
    if name == 'geometra':
        baseline = target / '.abrxos_patches' / 'ABRXOS_GEOMETRA_V3_1_R6.json'
        if not version.startswith('3.1.') or not baseline.exists():
            raise RuntimeError(f'Geometra requiere V3.1 R6 aplicado; encontrado {version or "sin versión"}')
        missing = [rel for rel in R6_BASELINE_FILES if not (target / rel).exists()]
        if missing:
            raise RuntimeError(f'Geometra R6 baseline incompleto; faltan: {", ".join(missing)}')
    elif not version.startswith('1.0.'):
        raise RuntimeError(f'{name}: versión incompatible {version}; se requiere 1.0.x')
    return 'ready'


def _backup_component(target: Path, backup_dir: Path, spec: dict[str, Any]) -> dict[str, Any]:
    rows=[]
    touched=[dst for _,dst in spec['files']] + ['VERSION.json']
    for rel in dict.fromkeys(touched):
        src=target/rel; existed=src.exists(); rows.append({'target':rel,'existed':existed})
        if existed:
            out=backup_dir/'files'/rel; out.parent.mkdir(parents=True,exist_ok=True)
            if src.is_dir(): shutil.copytree(src,out)
            else: shutil.copy2(src,out)
    return {'target':str(target),'files':rows}


def _restore_component(record: dict[str, Any], backup_dir: Path) -> None:
    target=Path(record['target'])
    for row in record.get('files',[]):
        rel=row['target']; dst=target/rel
        if row.get('existed'):
            src=backup_dir/'files'/rel
            if dst.exists(): shutil.rmtree(dst) if dst.is_dir() else dst.unlink()
            dst.parent.mkdir(parents=True,exist_ok=True)
            if src.is_dir(): shutil.copytree(src,dst)
            else: shutil.copy2(src,dst)
        elif dst.exists():
            shutil.rmtree(dst) if dst.is_dir() else dst.unlink()
    reg=target/'.abrxos_hotfixes'/f'{HOTFIX_ID}.json'
    if reg.exists(): reg.unlink()


def _apply_component(root: Path, target: Path, spec: dict[str, Any], backup_id: str) -> None:
    for source_rel,target_rel in spec['files']:
        src=root/source_rel; dst=target/target_rel
        if not src.exists(): raise RuntimeError(f'Payload faltante: {source_rel}')
        if dst.exists() and dst.is_dir(): shutil.rmtree(dst)
        dst.parent.mkdir(parents=True,exist_ok=True)
        if src.is_dir(): shutil.copytree(src,dst)
        else: shutil.copy2(src,dst)
    vf=target/'VERSION.json'; obj=_load(vf); obj.update(spec['version']); _write(vf,obj)
    reg=target/'.abrxos_hotfixes'/f'{HOTFIX_ID}.json'
    _write(reg,{'hotfixId':HOTFIX_ID,'backupId':backup_id,'appliedAt':dt.datetime.now().isoformat(timespec='seconds')})


def apply_hotfix(root: Path, *, home: Path | None=None, backup_root: Path | None=None, targets: dict[str,Path] | None=None) -> dict[str, Any]:
    root=Path(root).resolve(); home=Path(home or Path.home()).expanduser().resolve()
    targets=targets or default_targets(home)
    specs=_component_spec(root)
    statuses={name:_precheck_component(name,targets[name],spec['required']) for name,spec in specs.items()}
    backup_root=Path(backup_root or (home/BACKUP_DIRNAME)); backup_root.mkdir(parents=True,exist_ok=True)
    backup_id=f'{HOTFIX_ID}_{dt.datetime.now().strftime("%Y%m%d-%H%M%S-%f")}'
    state_dir=backup_root/backup_id; state_dir.mkdir(parents=True,exist_ok=False)
    records={}
    components={}
    try:
        for name,spec in specs.items():
            target=targets[name]
            if statuses[name]=='skipped_missing':
                components[name]={'status':'skipped_missing','target':str(target)}
                continue
            comp_backup=state_dir/name
            record=_backup_component(target,comp_backup,spec); records[name]=record
            _apply_component(root,target,spec,backup_id)
            components[name]={'status':'applied','target':str(target)}
        _write(state_dir/'hotfix.json',{'hotfixId':HOTFIX_ID,'backupId':backup_id,'components':records,'targets':{k:str(v) for k,v in targets.items()}})
    except Exception as exc:
        for name,record in reversed(list(records.items())):
            _restore_component(record,state_dir/name)
        raise RuntimeError(f'Hotfix falló y se revirtió: {exc}') from exc
    return {'status':'applied','hotfixId':HOTFIX_ID,'backupId':backup_id,'backupRoot':str(backup_root),'components':components}


if __name__=='__main__':
    import argparse
    ap=argparse.ArgumentParser();ap.add_argument('--root',required=True);ap.add_argument('--home');args=ap.parse_args()
    print(json.dumps(apply_hotfix(Path(args.root),home=Path(args.home).expanduser() if args.home else None),ensure_ascii=False,indent=2))
