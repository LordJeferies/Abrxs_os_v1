from pathlib import Path
import copy, importlib.util, json

ROOT = Path(__file__).resolve().parents[1]
R6_PATH = ROOT / 'PATCH_GEOMETRA' / 'geometra' / 'r6.py'
FIX = ROOT / 'PATCH_GEOMETRA' / 'tests' / 'fixtures'


def load_r6():
    spec = importlib.util.spec_from_file_location('hotfix_r6', R6_PATH)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_r61_checklist_adds_source_alignment_microtrim_and_vo_recording():
    r6 = load_r6()
    assert {'sourceAlignment', 'microtrim', 'voRecording'} <= set(r6.CHECKLIST_KEYS)
    piece = {'productionChecklist': {'editorial': {'status': 'ready'}}}
    out = r6.ensure_production_checklist(piece)
    for key in ('sourceAlignment', 'microtrim', 'voRecording'):
        assert out[key]['status'] == 'pending'


def test_short_source_exception_removes_caption_soft_range_warning():
    r6 = load_r6()
    doc = json.loads((FIX / 'INTRO_AMANDA_ALFA_PREBUILD_R6_1.json').read_text(encoding='utf-8'))
    report = r6.validate_r6_project(doc)
    warnings = '\n'.join(report['warnings'])
    assert 'P02_CAP_G01' not in warnings
    assert 'P11_CAP_G01' not in warnings


def test_r61_source_alignment_and_vo_placement_are_validated_without_fake_source_range():
    r6 = load_r6()
    doc = json.loads((FIX / 'INTRO_AMANDA_ALFA_PREBUILD_R6_1.json').read_text(encoding='utf-8'))
    report = r6.validate_r6_project(doc)
    row = report['pieces'][0]
    assert row['sourceAlignment']['locatedCount'] == 25
    assert row['sourceAlignment']['microtrimRequiredCount'] > 0
    assert row['voiceovers']['count'] == 2
    assert row['voiceovers']['placementReady'] is True
    assert all('VO01' not in x or 'sourceRange' not in x for x in row['missing'])


def test_projection_ready_is_separate_from_alpha_and_cutter_readiness():
    r6 = load_r6()
    doc = json.loads((FIX / 'FICHA_INTRO_ALFA_CINEMATIC_R6.json').read_text(encoding='utf-8'))
    report = r6.validate_r6_project(doc)
    row = report['pieces'][0]
    assert row['alphaReady'] is True
    assert row['cutterReady'] is True
    assert row['projectionReady'] is False
    assert any('T3' in x or 'image' in x.lower() for x in row['projectionMissing'])


def test_projection_ready_passes_when_nested_assets_have_t3_projection():
    r6 = load_r6()
    doc = json.loads((FIX / 'FICHA_INTRO_ALFA_CINEMATIC_R6.json').read_text(encoding='utf-8'))
    piece = doc['pieces'][0]
    additions = []
    for xr in [e for e in piece['timeline'] if e.get('track') == 'xr']:
        for asset in xr.get('assets') or []:
            if asset.get('start') is None or asset.get('end') is None:
                continue
            additions.append({
                'id': f"{asset['assetId']}_EVENT",
                'track': 'images',
                'type': 'image',
                'label': asset['assetId'],
                'assetId': asset['assetId'],
                'parentId': xr['id'],
                'start': asset['start'],
                'end': asset['end'],
                'timingMode': 'follow_parent',
            })
    piece['timeline'].extend(additions)
    report = r6.validate_r6_project(doc)
    row = report['pieces'][0]
    assert row['projectionReady'] is True
    assert row['projectionMissing'] == []


def test_route_policy_rejects_media_type_as_primary_route_in_r61():
    r6 = load_r6()
    doc = json.loads((FIX / 'INTRO_AMANDA_ALFA_PREBUILD_R6_1.json').read_text(encoding='utf-8'))
    doc['pieces'][0]['routePolicy']['primaryRoute'] = 'vo'
    report = r6.validate_r6_project(doc)
    assert any('routePolicy' in x for x in report['pieces'][0]['warnings'])
