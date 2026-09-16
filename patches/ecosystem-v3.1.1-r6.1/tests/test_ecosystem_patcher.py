from pathlib import Path
import json
import pytest

from tools.apply_hotfix import apply_hotfix, HOTFIX_ID
from tools.verify_hotfix import verify_hotfix
from tools.revert_hotfix import revert_hotfix
from tools.install_hotfix import install_hotfix

ROOT=Path(__file__).resolve().parents[1]


def make_geometra(path: Path, version='3.1.0'):
    (path/'geometra').mkdir(parents=True);(path/'shared').mkdir();(path/'app').mkdir();(path/'r6').mkdir();(path/'.abrxos_patches').mkdir()
    (path/'VERSION.json').write_text(json.dumps({'product':'ABRXOS GEOMETRA','version':version,'patch':'ABRXOS_GEOMETRA_V3_1_R6'}),encoding='utf-8')
    (path/'.abrxos_patches'/'ABRXOS_GEOMETRA_V3_1_R6.json').write_text(json.dumps({'patchId':'ABRXOS_GEOMETRA_V3_1_R6','patchVersion':'3.1.0-r6.1'}),encoding='utf-8')
    for rel in ('geometra/r6.py','shared/r6_patch.js','app/r6_patch.js','app/r6_patch.css'):
        p=path/rel;p.write_text('OLD-'+rel,encoding='utf-8')
    source=ROOT/'PATCH_GEOMETRA'/'r6'
    for name in ('XR_FAMILIES_R6.json','EDIT_PROFILES_R6.json','CINE_LIBRARY_R6.json','SFX_LIBRARY_R6.json','MOTION_LIBRARY_R6.json','MUSIC_LIBRARY_R6.json','CAPTIONS_R6.json'):
        (path/'r6'/name).write_bytes((source/name).read_bytes())
    return path


def make_builder(path: Path, kind: str):
    path.mkdir(parents=True)
    (path/'VERSION.json').write_text(json.dumps({'product':kind,'version':'1.0.0','canon':'R6'}),encoding='utf-8')
    engine='content_engine.py' if kind=='content' else 'brand_engine.py'
    (path/engine).write_text('OLD-'+engine,encoding='utf-8')
    if kind=='content':
        libs=path/'resources'/'canon_r6'/'libraries';libs.mkdir(parents=True)
        source=ROOT/'PATCH_GEOMETRA'/'r6'
        for name in ('XR_FAMILIES_R6.json','EDIT_PROFILES_R6.json','CINE_LIBRARY_R6.json','SFX_LIBRARY_R6.json','MOTION_LIBRARY_R6.json','MUSIC_LIBRARY_R6.json','CAPTIONS_R6.json'):
            (libs/name).write_bytes((source/name).read_bytes())
    else:
        resources=path/'resources';resources.mkdir(parents=True)
        template=ROOT/'tests'/'fixtures'/'brand_resources'/'resources'/'brand_adapter_template.json'
        (resources/'brand_adapter_template.json').write_bytes(template.read_bytes())
    return path


def test_apply_verify_revert_updates_three_apps_and_preserves_data(tmp_path):
    home=tmp_path/'home';home.mkdir()
    geo=make_geometra(home/'ABRXOS_GEOMETRA_V3')
    content=make_builder(home/'Applications/ABRXOS/ABRXOS_CONTENT_BUILDER_V1','content')
    brand=make_builder(home/'Applications/ABRXOS/ABRXOS_X_BRAND_BUILDER_V1','brand')
    data=home/'ABRXOS_GEOMETRA_DATA';data.mkdir(); sentinel=data/'sentinel.txt';sentinel.write_text('KEEP',encoding='utf-8')
    result=apply_hotfix(ROOT,home=home)
    assert result['status']=='applied'
    assert result['components']['geometra']['status']=='applied'
    assert result['components']['contentBuilder']['status']=='applied'
    assert result['components']['brandBuilder']['status']=='applied'
    assert json.loads((geo/'VERSION.json').read_text())['version']=='3.1.1'
    assert json.loads((content/'VERSION.json').read_text())['version']=='1.0.1'
    assert json.loads((brand/'VERSION.json').read_text())['version']=='1.0.1'
    assert sentinel.read_text()=='KEEP'
    report=verify_hotfix(ROOT,home=home)
    assert report['ok'] is True, report
    reverted=revert_hotfix(home=home,backup_id=result['backupId'])
    assert reverted['status']=='reverted'
    assert (geo/'geometra/r6.py').read_text()=='OLD-geometra/r6.py'
    assert (content/'content_engine.py').read_text()=='OLD-content_engine.py'
    assert (brand/'brand_engine.py').read_text()=='OLD-brand_engine.py'
    assert sentinel.read_text()=='KEEP'


def test_missing_optional_builders_are_skipped(tmp_path):
    home=tmp_path/'home';home.mkdir();make_geometra(home/'ABRXOS_GEOMETRA_V3')
    result=apply_hotfix(ROOT,home=home)
    assert result['components']['geometra']['status']=='applied'
    assert result['components']['contentBuilder']['status']=='skipped_missing'
    assert result['components']['brandBuilder']['status']=='skipped_missing'
    assert verify_hotfix(ROOT,home=home)['ok'] is True


def test_incompatible_or_unpatched_geometra_blocks_before_changes(tmp_path):
    home=tmp_path/'home';home.mkdir();geo=make_geometra(home/'ABRXOS_GEOMETRA_V3',version='3.0.0')
    (geo/'.abrxos_patches'/'ABRXOS_GEOMETRA_V3_1_R6.json').unlink()
    before=(geo/'geometra/r6.py').read_text()
    with pytest.raises(RuntimeError):
        apply_hotfix(ROOT,home=home)
    assert (geo/'geometra/r6.py').read_text()==before


def test_verify_detects_cross_app_library_hash_mismatch(tmp_path):
    home=tmp_path/'home';home.mkdir()
    make_geometra(home/'ABRXOS_GEOMETRA_V3')
    content=make_builder(home/'Applications/ABRXOS/ABRXOS_CONTENT_BUILDER_V1','content')
    make_builder(home/'Applications/ABRXOS/ABRXOS_X_BRAND_BUILDER_V1','brand')
    apply_hotfix(ROOT,home=home)
    report=verify_hotfix(ROOT,home=home)
    assert report['ok'] is True, report
    lib=content/'resources'/'canon_r6'/'libraries'/'XR_FAMILIES_R6.json'
    lib.write_text(lib.read_text(encoding='utf-8')+'\n',encoding='utf-8')
    broken=verify_hotfix(ROOT,home=home)
    assert broken['ok'] is False
    assert any('XR_FAMILIES_R6.json' in x and 'hash' in x.lower() for x in broken['errors']), broken


def test_verify_checks_builder_canon_handshake_constants(tmp_path):
    home=tmp_path/'home';home.mkdir()
    make_geometra(home/'ABRXOS_GEOMETRA_V3')
    content=make_builder(home/'Applications/ABRXOS/ABRXOS_CONTENT_BUILDER_V1','content')
    make_builder(home/'Applications/ABRXOS/ABRXOS_X_BRAND_BUILDER_V1','brand')
    apply_hotfix(ROOT,home=home)
    engine=content/'content_engine.py'
    engine.write_text(engine.read_text(encoding='utf-8').replace("CANON_REVISION='R6.1'","CANON_REVISION='R6.0'"),encoding='utf-8')
    broken=verify_hotfix(ROOT,home=home)
    assert broken['ok'] is False
    assert any('contentBuilder' in x and 'canonRevision' in x for x in broken['errors']), broken


def test_install_orchestrator_rolls_back_if_post_apply_verification_fails(tmp_path):
    home=tmp_path/'home';home.mkdir()
    geo=make_geometra(home/'ABRXOS_GEOMETRA_V3')
    content=make_builder(home/'Applications/ABRXOS/ABRXOS_CONTENT_BUILDER_V1','content')
    make_builder(home/'Applications/ABRXOS/ABRXOS_X_BRAND_BUILDER_V1','brand')
    original_geo=(geo/'geometra/r6.py').read_text(encoding='utf-8')
    original_content=(content/'content_engine.py').read_text(encoding='utf-8')
    # Precheck allows this, but post-apply cross-app hash verification must reject it.
    lib=content/'resources'/'canon_r6'/'libraries'/'XR_FAMILIES_R6.json'
    lib.write_text(lib.read_text(encoding='utf-8')+'\nMISMATCH',encoding='utf-8')
    result=install_hotfix(ROOT,home=home)
    assert result['status']=='rolled_back_after_verify_failure'
    assert result['verify']['ok'] is False
    assert (geo/'geometra/r6.py').read_text(encoding='utf-8')==original_geo
    assert (content/'content_engine.py').read_text(encoding='utf-8')==original_content
    assert json.loads((geo/'VERSION.json').read_text(encoding='utf-8'))['version']=='3.1.0'
    assert json.loads((content/'VERSION.json').read_text(encoding='utf-8'))['version']=='1.0.0'


def test_verify_checks_brand_adapter_schema_and_revision(tmp_path):
    home=tmp_path/'home';home.mkdir()
    make_geometra(home/'ABRXOS_GEOMETRA_V3')
    make_builder(home/'Applications/ABRXOS/ABRXOS_CONTENT_BUILDER_V1','content')
    brand=make_builder(home/'Applications/ABRXOS/ABRXOS_X_BRAND_BUILDER_V1','brand')
    apply_hotfix(ROOT,home=home)
    template=brand/'resources'/'brand_adapter_template.json'
    obj=json.loads(template.read_text(encoding='utf-8'));obj['adapterVersion']='R6.0';template.write_text(json.dumps(obj),encoding='utf-8')
    broken=verify_hotfix(ROOT,home=home)
    assert broken['ok'] is False
    assert any('brandBuilder adapterVersion' in x for x in broken['errors']), broken


def test_incomplete_r6_baseline_blocks_before_any_change(tmp_path):
    home=tmp_path/'home';home.mkdir();geo=make_geometra(home/'ABRXOS_GEOMETRA_V3')
    (geo/'r6'/'XR_FAMILIES_R6.json').unlink()
    before=(geo/'geometra/r6.py').read_text(encoding='utf-8')
    with pytest.raises(RuntimeError):
        apply_hotfix(ROOT,home=home)
    assert (geo/'geometra/r6.py').read_text(encoding='utf-8')==before
    assert json.loads((geo/'VERSION.json').read_text(encoding='utf-8'))['version']=='3.1.0'
