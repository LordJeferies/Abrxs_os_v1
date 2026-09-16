from pathlib import Path
import os, stat, subprocess, sys, json, tempfile

ROOT=Path(__file__).resolve().parents[1]


def test_mac_patch_commands_exist_and_reference_safe_default_paths():
    apply=(ROOT/'APLICAR_PATCH.command')
    revert=(ROOT/'REVERTIR_PATCH.command')
    verify=(ROOT/'VERIFICAR_PATCH.command')
    for p in (apply,revert,verify):
        assert p.exists(), p.name
        text=p.read_text(encoding='utf-8')
        assert 'ABRXOS_GEOMETRA_TARGET' in text
        assert '$HOME/ABRXOS_GEOMETRA_V3' in text
        assert '$HOME/ABRXOS_GEOMETRA_PATCH_BACKUPS' in text
    a=apply.read_text(encoding='utf-8')
    assert 'tools/apply_patch.py' in a
    assert 'tools/verify_patch.py' in a
    assert 'tools/revert_patch.py' in a
    assert 'ABRXOS_GEOMETRA_DATA' not in a
    assert 'ABRXOS Geometra V3.app' in a


def test_apply_command_rolls_back_if_post_verification_fails():
    text=(ROOT/'APLICAR_PATCH.command').read_text(encoding='utf-8')
    assert 'if !' in text or 'if ! python3' in text
    assert 'revert_patch.py' in text
    assert 'exit 1' in text


def test_verify_tool_reports_missing_target_without_modifying_anything(tmp_path):
    tool=ROOT/'tools'/'verify_patch.py'
    assert tool.exists()
    target=tmp_path/'missing'
    cp=subprocess.run([sys.executable,str(tool),'--target',str(target),'--patch-root',str(ROOT)],text=True,capture_output=True)
    assert cp.returncode != 0
    assert not target.exists()
    assert 'no encontrada' in (cp.stdout+cp.stderr).lower() or 'not found' in (cp.stdout+cp.stderr).lower()


def test_readme_explains_existing_app_and_rollback():
    p=ROOT/'README_PATCH.txt'
    assert p.exists()
    text=p.read_text(encoding='utf-8')
    assert 'misma' in text.lower() and '.app' in text
    assert 'REVERTIR_PATCH.command' in text
    assert 'ABRXOS_GEOMETRA_DATA' in text

def test_verify_tool_passes_on_patched_compatible_v3_candidate(tmp_path):
    from test_server_compiler_hooks import make_install
    import importlib.util
    target=make_install(tmp_path)
    spec=importlib.util.spec_from_file_location('patcher_verify_candidate',ROOT/'tools'/'apply_patch.py')
    mod=importlib.util.module_from_spec(spec); assert spec and spec.loader; spec.loader.exec_module(mod)
    backups=tmp_path/'backups';mod.apply_patch(target,ROOT,backups)
    cp=subprocess.run([sys.executable,str(ROOT/'tools'/'verify_patch.py'),'--target',str(target),'--patch-root',str(ROOT)],text=True,capture_output=True)
    assert cp.returncode==0, cp.stdout+cp.stderr
    report=json.loads(cp.stdout)
    assert report['ok'] is True
    assert any(x=='r6_validator=PASS' for x in report['checks'])
