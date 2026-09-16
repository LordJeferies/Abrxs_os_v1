from pathlib import Path
import json

from tools.release_manifest import build_manifest, verify_manifest

ROOT = Path(__file__).resolve().parents[1]


def test_release_manifest_excludes_ephemeral_files_and_verifies_cleanly(tmp_path):
    pkg = tmp_path / 'pkg'
    (pkg / 'sub').mkdir(parents=True)
    (pkg / 'ok.txt').write_text('ok', encoding='utf-8')
    (pkg / '.pytest_cache').mkdir()
    (pkg / '.pytest_cache' / 'x').write_text('bad', encoding='utf-8')
    (pkg / 'sub' / 'x.pyc').write_bytes(b'bad')
    (pkg / '__pycache__').mkdir()
    (pkg / '__pycache__' / 'x.pyc').write_bytes(b'bad')
    manifest = build_manifest(pkg)
    paths = {row['path'] for row in manifest['files']}
    assert paths == {'ok.txt'}
    assert verify_manifest(pkg, manifest) == []


def test_hotfix_tests_do_not_contain_absolute_r6pkg_dependency():
    offenders = []
    for p in (ROOT / 'PATCH_GEOMETRA').rglob('*.py'):
        text = p.read_text(encoding='utf-8', errors='replace')
        if ('/mnt' + '/data/r6pkg') in text:
            offenders.append(str(p.relative_to(ROOT)))
    assert offenders == []


def test_hotfix_geometra_fixtures_are_self_contained():
    fixture_dir = ROOT / 'PATCH_GEOMETRA' / 'tests' / 'fixtures'
    expected = {
        'FICHA_INTRO_ALFA_CINEMATIC_R6.json',
        'FICHA_VERTICAL_ALFA_CINEMATIC_R6.json',
        'FICHA_CAROUSEL_ALFA_R6.json',
    }
    assert expected <= {p.name for p in fixture_dir.glob('*.json')}


def test_release_tests_have_no_build_machine_absolute_paths():
    offenders=[]
    for path in (ROOT/'tests').rglob('*.py'):
        text=path.read_text(encoding='utf-8',errors='replace')
        if ('/mnt' + '/data/') in text:
            offenders.append(str(path.relative_to(ROOT)))
    assert offenders==[]
