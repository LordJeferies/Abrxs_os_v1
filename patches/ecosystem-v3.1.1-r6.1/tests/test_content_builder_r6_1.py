from pathlib import Path
import importlib.util, json

ROOT = Path(__file__).resolve().parents[1]
ENGINE = ROOT / 'PATCH_CONTENT_BUILDER' / 'content_engine.py'
BASE_RES = ROOT / 'tests' / 'fixtures' / 'content_resources' / 'canon_r6'


def load_engine():
    spec=importlib.util.spec_from_file_location('hotfix_content_engine', ENGINE)
    mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod);return mod


def request():
    return {
        'requestId':'INTRO_AMANDA','projectId':'JOC55','workflowMode':'fixed_plan','contentType':'intro','stage':'ALFA','editProfile':'XR_FULL','timingQuality':'exact','quantity':1,'sourceGroup':'DEFAULT',
        'transcript':'[00:00] texto','editorialPlan':'AMANDA: frase','projectConfig':{},'brandAdapter':{},'specialRules':''
    }


def test_content_builder_package_declares_r6_family_r61_revision_and_features(tmp_path):
    eng=load_engine()
    result=eng.build_content_ai_package(request(),tmp_path,BASE_RES)
    folder=Path(result['folder'])
    contract=json.loads((folder/'contract_manifest.json').read_text(encoding='utf-8'))
    assert contract['canonFamily']=='R6'
    assert contract['canonRevision']=='R6.1'
    assert {'sourceAlignment','microtrim','voAdded','routeSemanticsR61','shortSourceException','projectionReady'} <= set(contract['features'])
    manifest=json.loads((folder/'package_manifest.json').read_text(encoding='utf-8'))
    assert manifest['canonFamily']=='R6'
    assert manifest['canonRevision']=='R6.1'
    assert manifest['contractFile']=='contract_manifest.json'


def test_content_builder_package_includes_r61_supplements_and_projection_contract(tmp_path):
    eng=load_engine();folder=Path(eng.build_content_ai_package(request(),tmp_path,BASE_RES)['folder'])
    assert (folder/'12_R6_1_SOURCE_ALIGNMENT.txt').exists()
    assert (folder/'13_R6_1_VO_ROUTE_CAPTIONS.txt').exists()
    projection=json.loads((folder/'14_LIENZO_PROJECTION_CONTRACT.json').read_text(encoding='utf-8'))
    assert projection['readinessAxis']=='projectionReady'
    assert projection['tracks']['images']=='T3'
    prompt=(folder/'02_PROMPT_FINAL.txt').read_text(encoding='utf-8')
    assert 'SOURCE ALIGNMENT R6.1' in prompt
    assert 'microtrim' in prompt.lower()
    assert 'sourceRanges finales' in prompt


def test_content_builder_contract_contains_hashes_for_shared_r6_libraries(tmp_path):
    eng=load_engine();folder=Path(eng.build_content_ai_package(request(),tmp_path,BASE_RES)['folder'])
    contract=json.loads((folder/'contract_manifest.json').read_text(encoding='utf-8'))
    libs=contract['libraries']
    for key in ('XR_FAMILIES_R6.json','SFX_LIBRARY_R6.json','MOTION_LIBRARY_R6.json','CINE_LIBRARY_R6.json','MUSIC_LIBRARY_R6.json','CAPTIONS_R6.json','EDIT_PROFILES_R6.json'):
        assert key in libs
        assert libs[key].startswith('sha256:')
