from __future__ import annotations
import datetime as dt
import json, shutil
from pathlib import Path
from typing import Any

REGISTRY_DIR = '.abrxos_patches'


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding='utf-8'))


def _version(target: Path) -> str:
    version_file = target / 'VERSION.json'
    if not version_file.exists():
        raise RuntimeError('VERSION.json no encontrado; no parece una instalación Geometra V3 compatible.')
    return str(_load_json(version_file).get('version') or '')


def _marker(marker: str, content: str) -> str:
    return f'<!-- ABRXOS_PATCH:{marker} -->\n{content}\n<!-- /ABRXOS_PATCH:{marker} -->'


def _py_marker(marker: str, content: str) -> str:
    return f'# ABRXOS_PATCH:{marker}\n{content}\n# /ABRXOS_PATCH:{marker}'


def _wrap_marker(target: Path, marker: str, content: str) -> str:
    if target.suffix in {'.py', '.command', '.sh'}:
        return _py_marker(marker, content)
    return _marker(marker, content)


def _insert(text: str, operation: str, anchor: str, block: str) -> str:
    if anchor not in text:
        raise RuntimeError(f'Anchor no encontrado: {anchor[:100]}')
    if operation == 'insert_before':
        return text.replace(anchor, block + '\n' + anchor, 1)
    if operation == 'insert_after':
        return text.replace(anchor, anchor + '\n' + block, 1)
    raise RuntimeError(f'Operación hook no soportada: {operation}')


def _backup_targets(target: Path, patch_root: Path, manifest: dict[str, Any], backup_root: Path, backup_id: str) -> tuple[Path, dict[str, Any]]:
    backup_dir = backup_root / backup_id
    files_dir = backup_dir / 'files'
    backup_dir.mkdir(parents=True, exist_ok=False)
    rows: list[dict[str, Any]] = []
    touched: list[str] = []
    for row in manifest.get('copy', []):
        touched.append(row['target'])
    for row in manifest.get('hooks', []):
        touched.append(row['target'])
    if manifest.get('versionUpdate'):
        touched.append('VERSION.json')
    for rel in dict.fromkeys(touched):
        src = target / rel
        existed = src.exists()
        rows.append({'target':rel,'existed':existed})
        if existed:
            out = files_dir / rel
            out.parent.mkdir(parents=True, exist_ok=True)
            if src.is_dir():
                shutil.copytree(src, out)
            else:
                shutil.copy2(src, out)
    record={'patchId':manifest['patchId'],'patchVersion':manifest.get('patchVersion'),'backupId':backup_id,'files':rows}
    (backup_dir/'backup.json').write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    return backup_dir, record


def _restore(target: Path, backup_dir: Path, record: dict[str, Any]) -> None:
    for row in record.get('files', []):
        rel=row['target']; dst=target/rel
        if row.get('existed'):
            src=backup_dir/'files'/rel
            if dst.exists():
                if dst.is_dir(): shutil.rmtree(dst)
                else: dst.unlink()
            dst.parent.mkdir(parents=True,exist_ok=True)
            if src.is_dir(): shutil.copytree(src,dst)
            else: shutil.copy2(src,dst)
        elif dst.exists():
            if dst.is_dir(): shutil.rmtree(dst)
            else: dst.unlink()


def apply_patch(target: Path, patch_root: Path, backup_root: Path) -> dict[str, Any]:
    target=Path(target).expanduser().resolve(); patch_root=Path(patch_root).expanduser().resolve(); backup_root=Path(backup_root).expanduser().resolve()
    if not target.exists(): raise RuntimeError(f'Instalación no encontrada: {target}')
    manifest=_load_json(patch_root/'PATCH_MANIFEST.json')
    patch_id=str(manifest['patchId']); patch_version=str(manifest.get('patchVersion') or '')
    current=_version(target); prefix=str(manifest.get('targetVersionPrefix') or '3.')
    if not current.startswith(prefix): raise RuntimeError(f'Versión incompatible: {current}; se requiere {prefix}x')
    registry=target/REGISTRY_DIR/f'{patch_id}.json'
    if registry.exists():
        installed=_load_json(registry)
        if installed.get('patchVersion')==patch_version:
            return {'status':'already_applied','patchId':patch_id,'patchVersion':patch_version,'backupId':installed.get('backupId'),'target':str(target)}
        raise RuntimeError(f'Ya existe {patch_id} con otra versión; reviértelo antes de actualizarlo.')

    backup_root.mkdir(parents=True,exist_ok=True)
    stamp=dt.datetime.now().strftime('%Y%m%d-%H%M%S-%f')
    backup_id=f'{patch_id}_{stamp}'
    backup_dir, record=_backup_targets(target,patch_root,manifest,backup_root,backup_id)
    try:
        for row in manifest.get('copy', []):
            src=patch_root/row['source']; dst=target/row['target']
            if not src.exists(): raise RuntimeError(f'Payload faltante: {row["source"]}')
            if src.is_dir():
                if dst.exists(): shutil.rmtree(dst)
                shutil.copytree(src,dst)
            else:
                dst.parent.mkdir(parents=True,exist_ok=True); shutil.copy2(src,dst)
        for row in manifest.get('hooks', []):
            dst=target/row['target']
            if not dst.exists(): raise RuntimeError(f'Archivo hook faltante: {row["target"]}')
            text=dst.read_text(encoding='utf-8')
            marker=str(row['marker'])
            if f'ABRXOS_PATCH:{marker}' in text:
                continue
            content=row.get('content')
            if content is None and row.get('contentFile'):
                content=(patch_root/row['contentFile']).read_text(encoding='utf-8').rstrip()
            if content is None: content=''
            block=_wrap_marker(dst,marker,str(content))
            effective_anchor=row['anchor']
            if row.get('indentFromAnchor'):
                anchor = row['anchor']
                pos = text.index(anchor)
                line_start = text.rfind('\n', 0, pos) + 1
                prefix = text[line_start:pos]
                if prefix.strip():
                    raise RuntimeError(f'indentFromAnchor requiere anchor al inicio lógico de línea: {anchor[:100]}')
                indent = prefix
                effective_anchor = indent + anchor
                block = '\n'.join((indent + line) if line else line for line in block.splitlines())
            dst.write_text(_insert(text,row['operation'],effective_anchor,block),encoding='utf-8')
        if manifest.get('versionUpdate'):
            vf=target/'VERSION.json'; obj=_load_json(vf); obj.update(manifest['versionUpdate']); vf.write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
        registry.parent.mkdir(parents=True,exist_ok=True)
        registry.write_text(json.dumps({'patchId':patch_id,'patchVersion':patch_version,'backupId':backup_id,'appliedAt':dt.datetime.now().isoformat(timespec='seconds')},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    except Exception as exc:
        _restore(target,backup_dir,record)
        if registry.exists(): registry.unlink()
        raise RuntimeError(f'Patch falló y fue revertido automáticamente: {exc}') from exc
    return {'status':'applied','patchId':patch_id,'patchVersion':patch_version,'backupId':backup_id,'target':str(target)}


if __name__=='__main__':
    import argparse
    ap=argparse.ArgumentParser()
    ap.add_argument('--target',required=True); ap.add_argument('--patch-root',required=True); ap.add_argument('--backup-root',required=True)
    args=ap.parse_args(); print(json.dumps(apply_patch(Path(args.target),Path(args.patch_root),Path(args.backup_root)),indent=2,ensure_ascii=False))
