from __future__ import annotations
import importlib.util, json
from pathlib import Path

WORK = Path(__file__).resolve().parents[1]
APPLY = WORK / 'tools' / 'apply_patch.py'
REVERT = WORK / 'tools' / 'revert_patch.py'


def load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(mod)
    return mod


def make_patch_root(tmp_path: Path) -> Path:
    patch = tmp_path / 'patch'
    (patch / 'payload').mkdir(parents=True)
    (patch / 'payload' / 'new.txt').write_text('NEW\n', encoding='utf-8')
    manifest = {
        'patchId': 'TEST_PATCH',
        'patchVersion': '1.0.0',
        'targetVersionPrefix': '3.',
        'copy': [{'source':'payload/new.txt','target':'new.txt'}],
        'hooks': [{
            'target':'app/index.html', 'operation':'insert_before', 'anchor':'</body>',
            'marker':'TEST_HOOK', 'content':'<script>patched()</script>'
        }],
    }
    (patch / 'PATCH_MANIFEST.json').write_text(json.dumps(manifest), encoding='utf-8')
    return patch


def make_target(tmp_path: Path) -> Path:
    target = tmp_path / 'ABRXOS_GEOMETRA_V3'
    (target / 'app').mkdir(parents=True)
    (target / 'app' / 'index.html').write_text('<html><body>BASE</body></html>', encoding='utf-8')
    (target / 'VERSION.json').write_text(json.dumps({'product':'ABRXOS GEOMETRA','version':'3.0.0'}), encoding='utf-8')
    return target


def test_apply_is_idempotent_and_rollback_restores_original_bytes(tmp_path):
    apply_mod = load(APPLY, 'apply_patch_mod')
    revert_mod = load(REVERT, 'revert_patch_mod')
    target = make_target(tmp_path); patch = make_patch_root(tmp_path); backups = tmp_path / 'backups'
    before = (target/'app/index.html').read_bytes()
    first = apply_mod.apply_patch(target, patch, backups)
    assert first['status'] == 'applied'
    assert (target/'new.txt').read_text() == 'NEW\n'
    text = (target/'app/index.html').read_text()
    assert text.count('ABRXOS_PATCH:TEST_HOOK') == 2  # open + close marker
    assert '<script>patched()</script>' in text
    backup_id = first['backupId']

    second = apply_mod.apply_patch(target, patch, backups)
    assert second['status'] == 'already_applied'
    assert second['backupId'] == backup_id
    assert (target/'app/index.html').read_text().count('<script>patched()</script>') == 1

    result = revert_mod.revert_patch(target, backups, backup_id)
    assert result['status'] == 'reverted'
    assert (target/'app/index.html').read_bytes() == before
    assert not (target/'new.txt').exists()
    assert not (target/'.abrxos_patches/TEST_PATCH.json').exists()


def test_apply_never_touches_sibling_data_directory(tmp_path):
    apply_mod = load(APPLY, 'apply_patch_mod_data')
    target = make_target(tmp_path); patch = make_patch_root(tmp_path); backups = tmp_path / 'backups'
    data = tmp_path / 'ABRXOS_GEOMETRA_DATA'; data.mkdir(); secret = data/'library_v3.json'; secret.write_text('USER-DATA', encoding='utf-8')
    apply_mod.apply_patch(target, patch, backups)
    assert secret.read_text(encoding='utf-8') == 'USER-DATA'


def test_apply_fails_cleanly_on_unknown_major_version(tmp_path):
    apply_mod = load(APPLY, 'apply_patch_mod_version')
    target = make_target(tmp_path); patch = make_patch_root(tmp_path); backups = tmp_path / 'backups'
    (target/'VERSION.json').write_text(json.dumps({'product':'ABRXOS GEOMETRA','version':'4.0.0'}), encoding='utf-8')
    try:
        apply_mod.apply_patch(target, patch, backups)
    except RuntimeError as exc:
        assert 'versión' in str(exc).lower() or 'version' in str(exc).lower()
    else:
        raise AssertionError('expected RuntimeError')
    assert not (target/'new.txt').exists()


def test_missing_anchor_rolls_back_files_copied_earlier_in_same_apply(tmp_path):
    apply_mod = load(APPLY, 'apply_patch_mod_rollback')
    target = make_target(tmp_path); patch = make_patch_root(tmp_path); backups = tmp_path / 'backups'
    manifest = json.loads((patch/'PATCH_MANIFEST.json').read_text())
    manifest['hooks'][0]['anchor'] = '<missing-anchor>'
    (patch/'PATCH_MANIFEST.json').write_text(json.dumps(manifest), encoding='utf-8')
    before = (target/'app/index.html').read_bytes()
    try:
        apply_mod.apply_patch(target, patch, backups)
    except RuntimeError:
        pass
    else:
        raise AssertionError('expected failure')
    assert (target/'app/index.html').read_bytes() == before
    assert not (target/'new.txt').exists()

def test_existing_payload_directory_is_backed_up_and_restored(tmp_path):
    apply_mod = load(APPLY, 'apply_patch_mod_dir')
    revert_mod = load(REVERT, 'revert_patch_mod_dir')
    target=make_target(tmp_path)
    (target/'r6').mkdir()
    (target/'r6'/'legacy.json').write_text('{"legacy":true}\n',encoding='utf-8')
    original=(target/'r6'/'legacy.json').read_bytes()
    patch=make_patch_root(tmp_path)
    payload_dir=patch/'payload'/'r6';payload_dir.mkdir(parents=True)
    (payload_dir/'new.json').write_text('{"new":true}\n',encoding='utf-8')
    manifest=json.loads((patch/'PATCH_MANIFEST.json').read_text())
    manifest['copy'].append({'source':'payload/r6','target':'r6'})
    (patch/'PATCH_MANIFEST.json').write_text(json.dumps(manifest),encoding='utf-8')
    backup=tmp_path/'backups'
    result=apply_mod.apply_patch(target,patch,backup)
    assert (target/'r6'/'new.json').exists()
    revert_mod.revert_patch(target,backup,backup_id=result['backupId'])
    assert (target/'r6'/'legacy.json').read_bytes()==original
    assert not (target/'r6'/'new.json').exists()

def test_indent_from_anchor_keeps_python_block_syntax_valid(tmp_path):
    apply_mod=load(APPLY,'apply_patch_mod_indent')
    target=tmp_path/'ABRXOS_GEOMETRA_V3';(target/'geometra').mkdir(parents=True)
    (target/'VERSION.json').write_text(json.dumps({'version':'3.0.0'}),encoding='utf-8')
    source="class X:\n    def run(self):\n        value=1\n        return value\n"
    (target/'geometra/test.py').write_text(source,encoding='utf-8')
    patch=tmp_path/'patch_indent';patch.mkdir();(patch/'hook.txt').write_text("if True:\n    value=2",encoding='utf-8')
    manifest={'patchId':'INDENT','patchVersion':'1','targetVersionPrefix':'3.','copy':[],'hooks':[{'target':'geometra/test.py','operation':'insert_before','anchor':'return value','marker':'INDENT_HOOK','contentFile':'hook.txt','indentFromAnchor':True}]}
    (patch/'PATCH_MANIFEST.json').write_text(json.dumps(manifest),encoding='utf-8')
    apply_mod.apply_patch(target,patch,tmp_path/'backups')
    compiled=compile((target/'geometra/test.py').read_text(encoding='utf-8'),'test.py','exec')
    assert compiled
