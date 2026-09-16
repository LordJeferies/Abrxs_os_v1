from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def text(rel):
    return (ROOT / rel).read_text(encoding='utf-8')


def test_capture_does_not_clobber_zsh_path_special_parameter():
    src = text('tools/CAPTURAR_INSTALACION_ACTUAL.command')
    assert ' path=' not in src
    assert '; path=' not in src
    assert 'install_path=' in src


def test_tools_use_shared_python_resolver():
    resolver = ROOT / 'tools/lib/python_resolver.zsh'
    assert resolver.exists()
    for rel in [
        'tools/CAPTURAR_INSTALACION_ACTUAL.command',
        'tools/VERIFY_ALL.command',
        'tools/GENERAR_MANIFEST.command',
        'tools/ACTUALIZAR_REPO_DESDE_MAC.command',
    ]:
        src = text(rel)
        assert 'python_resolver.zsh' in src, rel
        assert 'ABRXOS_PYTHON' in src, rel


def test_one_command_finalize_tool_exists():
    p = ROOT / 'tools/DEJAR_REPO_LISTO.command'
    assert p.exists()
    src = p.read_text(encoding='utf-8')
    assert 'CAPTURAR_INSTALACION_ACTUAL.command' in src
    assert 'VERIFY_ALL.command' in src
    assert 'GENERAR_MANIFEST.command' in src


def test_clean_install_from_repo_exists_and_uses_current_snapshots():
    p = ROOT / 'install/INSTALAR_ECOSISTEMA_DESDE_CERO.command'
    assert p.exists()
    src = p.read_text(encoding='utf-8')
    assert 'apps/geometra/current' in src
    assert 'apps/content-builder/current' in src
    assert 'apps/brand-builder/current' in src
    assert 'ABRXOS Geometra V3.app' in src
    assert 'ABRXOS Content Builder.app' in src
    assert 'ABRXOS X Brand Builder.app' in src


def test_restore_docs_explain_capture_requirement():
    src = text('install/README_RESTORE_FROM_GITHUB.txt')
    assert 'CAPTURAR_INSTALACION_ACTUAL.command' in src
    assert 'INSTALAR_ECOSISTEMA_DESDE_CERO.command' in src
    assert 'apps/geometra/current' in src


def test_individual_install_wrappers_target_current_snapshots():
    brand = text('install/INSTALAR_BRAND_BUILDER.command')
    content = text('install/INSTALAR_CONTENT_BUILDER.command')
    assert 'apps/brand-builder/current/INSTALAR_ABRXOS_X_BRAND_BUILDER_V1.command' in brand
    assert 'apps/content-builder/current/INSTALAR_ABRXOS_CONTENT_BUILDER_V1.command' in content


def test_update_from_mac_runs_zsh_scripts_with_zsh():
    src = text('tools/ACTUALIZAR_REPO_DESDE_MAC.command')
    assert '/usr/bin/env bash' not in src
    assert '/bin/zsh' in src
