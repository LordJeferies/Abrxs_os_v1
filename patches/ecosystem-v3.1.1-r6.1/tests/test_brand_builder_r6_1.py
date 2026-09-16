from pathlib import Path
import importlib.util, json

ROOT=Path(__file__).resolve().parents[1]
ENGINE=ROOT/'PATCH_BRAND_BUILDER'/'brand_engine.py'
BASE_RES=ROOT/'tests'/'fixtures'/'brand_resources'/'resources'


def load_engine():
    spec=importlib.util.spec_from_file_location('hotfix_brand_engine',ENGINE)
    mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod);return mod


def project():
    return {
        'brandId':'JOC','brandName':'JOC','canonVersion':'R6','rawContext':'context','brandForm':{'sector':'media'},
        'method':{'summary':{'Brand Ego':'x'}},'brandAdapterDraft':{},'references':[]
    }


def test_brand_builder_package_declares_r6_r61_handshake(tmp_path):
    eng=load_engine();folder=Path(eng.build_brand_ai_package(project(),tmp_path,BASE_RES)['folder'])
    contract=json.loads((folder/'contract_manifest.json').read_text(encoding='utf-8'))
    assert contract['canonFamily']=='R6'
    assert contract['canonRevision']=='R6.1'
    assert contract['brandSchema']=='abrxos.brand-adapter.r6'
    assert contract['brandAdapterVersion']=='R6.1'
    manifest=json.loads((folder/'package_manifest.json').read_text(encoding='utf-8'))
    assert manifest['canonFamily']=='R6'
    assert manifest['canonRevision']=='R6.1'
    assert manifest['contractFile']=='contract_manifest.json'


def test_brand_builder_keeps_method_and_adapter_outputs_separate(tmp_path):
    eng=load_engine();folder=Path(eng.build_brand_ai_package(project(),tmp_path,BASE_RES)['folder'])
    expected=json.loads((folder/'07_EXPECTED_OUTPUT_SCHEMA.json').read_text(encoding='utf-8'))
    assert 'strategy' in expected and 'brandAdapter' in expected
    assert expected['brandAdapter']['schemaVersion']=='abrxos.brand-adapter.r6'
