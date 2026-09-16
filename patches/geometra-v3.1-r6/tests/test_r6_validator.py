from __future__ import annotations
import copy, importlib.util, json
from pathlib import Path

WORK = Path(__file__).resolve().parents[1]
R6_ROOT = Path('/mnt/data/r6pkg/ABRXOS_CANON_R6_AI_GEOMETRA')
MODULE = WORK / 'payload' / 'geometra' / 'r6.py'


def load_module():
    spec = importlib.util.spec_from_file_location('abrxos_patch_r6', MODULE)
    mod = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(mod)
    return mod


def load_json(rel):
    return json.loads((R6_ROOT / rel).read_text(encoding='utf-8'))


def test_official_intro_cinematic_is_alpha_and_cutter_ready():
    r6 = load_module()
    doc = load_json('05_FICHAS/INTRO/FICHA_INTRO_ALFA_CINEMATIC_R6.json')
    report = r6.validate_r6_project(doc, r6.load_r6_libraries(R6_ROOT / '02_LIBRARIES'))
    assert report['r6Detected'] is True
    assert report['critical'] == []
    row = report['pieces'][0]
    assert row['id'] == 'INTRO_01'
    assert row['alphaReady'] is True
    assert row['cutterReady'] is True
    assert row['missing'] == []
    assert 0 <= row['progressPercent'] <= 100


def test_r6_caption_group_soft_range_and_hidden_suppression_validate():
    r6 = load_module()
    doc = load_json('05_FICHAS/VERTICAL/FICHA_VERTICAL_ALFA_CINEMATIC_R6.json')
    piece = doc['pieces'][0]
    cap = next(e for e in piece['timeline'] if e.get('track') == 'captions')
    cap['visibility'] = 'hidden'
    cap['suppressedBy'] = 'V01_XR01'
    report = r6.validate_r6_project(doc, r6.load_r6_libraries(R6_ROOT / '02_LIBRARIES'))
    assert report['critical'] == []
    assert not any('suppressedBy' in x for x in report['warnings'])


def test_invalid_comic_info_asset_count_is_critical_and_alpha_not_ready():
    r6 = load_module()
    doc = load_json('05_FICHAS/INTRO/FICHA_INTRO_ALFA_CINEMATIC_R6.json')
    xr = next(e for e in doc['pieces'][0]['timeline'] if e.get('xrFamily') == 'COMIC_INFO')
    xr['assets'] = []
    report = r6.validate_r6_project(doc, r6.load_r6_libraries(R6_ROOT / '02_LIBRARIES'))
    row = report['pieces'][0]
    assert any('COMIC_INFO' in x and '1 asset' in x for x in report['critical'])
    assert row['alphaReady'] is False
    assert row['cutterReady'] is True  # sourceRanges remain valid and independent


def test_edit_profile_disallows_xr_for_motion_sfx_profile():
    r6 = load_module()
    doc = load_json('05_FICHAS/VERTICAL/FICHA_VERTICAL_ALFA_CINEMATIC_R6.json')
    doc['pieces'][0]['editProfile'] = {'code': 'MOTION_SFX', 'commercialName': 'Dynamic Edit'}
    report = r6.validate_r6_project(doc, r6.load_r6_libraries(R6_ROOT / '02_LIBRARIES'))
    assert any('MOTION_SFX' in x and 'XR' in x for x in report['warnings'])


def test_legacy_xr00_xr09_is_preserved_and_not_reported_as_invalid_r6_family():
    r6 = load_module()
    legacy = {
        'schemaVersion': 'abrxos.document.v3',
        'projectId': 'LEGACY',
        'pieces': [{
            'canonicalId': 'V07', 'type': 'vertical', 'stage': 'ALFA', 'workflowStatus': 'HACIENDO',
            'schedule': {'date':'','time':'','platforms':[]}, 'source': 'DEFAULT',
            'sourceRanges': [{'start': 10.0, 'end': 20.0}],
            'timeline': [{'id':'V07_XR01','track':'xr','type':'xr','xrFamily':'XR06','start':1.0,'end':4.0,'states':[],'assets':[]}]
        }]
    }
    report = r6.validate_r6_project(legacy, r6.load_r6_libraries(R6_ROOT / '02_LIBRARIES'))
    assert report['r6Detected'] is False
    assert report['critical'] == []
    assert report['pieces'][0]['cutterReady'] is True
    assert all('family inválida' not in x for x in report['warnings'])


def test_static_carousel_alpha_requires_static_items():
    r6 = load_module()
    doc = load_json('05_FICHAS/CAROUSEL/FICHA_CAROUSEL_ALFA_R6.json')
    doc['pieces'][0]['staticProduction']['items'] = []
    report = r6.validate_r6_project(doc, r6.load_r6_libraries(R6_ROOT / '02_LIBRARIES'))
    assert report['pieces'][0]['alphaReady'] is False
    assert any('staticProduction.items' in x for x in report['critical'])


def test_production_checklist_default_does_not_overwrite_existing_statuses():
    r6 = load_module()
    piece = {'type':'vertical', 'productionChecklist': {'images': {'status': 'approved'}}}
    result = r6.ensure_production_checklist(piece)
    assert result['images']['status'] == 'approved'
    assert 'editorial' in result and 'qa' in result and 'captions' in result
    assert piece['productionChecklist'] == result

def test_r6_alpha_video_requires_full_identity_fields_not_objective_or_thesis_shortcut():
    r6=load_module()
    doc=load_json('05_FICHAS/VERTICAL/FICHA_VERTICAL_ALFA_CINEMATIC_R6.json')
    piece=doc['pieces'][0]
    for field in ('title','objective','thesis','source','editProfile','schedule'):
        broken=copy.deepcopy(doc)
        broken['pieces'][0].pop(field,None)
        report=r6.validate_r6_project(broken,r6.load_r6_libraries(R6_ROOT/'02_LIBRARIES'))
        row=report['pieces'][0]
        assert row['alphaReady'] is False, field
        assert any(field in item for item in row['missing']), (field,row['missing'])

def test_r6_cine_alpha_requires_directional_fields_without_adding_t10():
    r6=load_module()
    doc=load_json('05_FICHAS/VERTICAL/FICHA_VERTICAL_ALFA_CINEMATIC_R6.json')
    piece=doc['pieces'][0]
    piece['timeline'].append({'id':'CINE_TEST','track':'broll','type':'cine','cineType':'CINE01_BLACK_HOLD','start':1.0,'end':2.0,'function':'hold','visual':'#000'})
    report=r6.validate_r6_project(doc,r6.load_r6_libraries(R6_ROOT/'02_LIBRARIES'))
    row=report['pieces'][0]
    assert row['alphaReady'] is False
    for field in ('musicAutomation','silence','captionPolicy'):
        assert any(f'CINE_TEST: {field}' in item for item in row['missing']), row['missing']
    assert not any('T10' in item for item in row['critical']+row['missing']+row['warnings'])

def test_r6_sfx_event_requires_official_library_event_fields():
    r6=load_module()
    doc=load_json('05_FICHAS/VERTICAL/FICHA_VERTICAL_ALFA_CINEMATIC_R6.json')
    piece=doc['pieces'][0]
    piece['timeline'].append({'id':'SFX_TEST','track':'sfx','type':'sfx','start':2.0,'end':2.2,'sfx':{}})
    report=r6.validate_r6_project(doc,r6.load_r6_libraries(R6_ROOT/'02_LIBRARIES'))
    row=report['pieces'][0]
    assert row['alphaReady'] is False
    for field in ('libraryId','variant','trigger','purpose','mix','status'):
        assert any(f'SFX_TEST: SFX {field}' in item for item in row['missing']), (field,row['missing'])

def test_validation_is_read_only_and_does_not_expand_partial_checklist():
    r6=load_module()
    doc=load_json('05_FICHAS/VERTICAL/FICHA_VERTICAL_ALFA_CINEMATIC_R6.json')
    doc['pieces'][0]['productionChecklist']={'images':{'status':'approved'}}
    before=copy.deepcopy(doc)
    r6.validate_r6_project(doc,r6.load_r6_libraries(R6_ROOT/'02_LIBRARIES'))
    assert doc==before
