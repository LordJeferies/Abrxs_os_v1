from pathlib import Path
import hashlib, importlib.util, json

ROOT=Path(__file__).resolve().parents[1]
CONTENT_ENGINE=ROOT/'PATCH_CONTENT_BUILDER'/'content_engine.py'
BRAND_ENGINE=ROOT/'PATCH_BRAND_BUILDER'/'brand_engine.py'
CONTENT_RES=ROOT/'tests'/'fixtures'/'content_resources'/'canon_r6'
BRAND_RES=ROOT/'tests'/'fixtures'/'brand_resources'/'resources'


def load(name,path):
    spec=importlib.util.spec_from_file_location(name,path);mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod);return mod


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def test_brand_content_geometra_contracts_are_compatible(tmp_path):
    content=load('ceng',CONTENT_ENGINE);brand=load('beng',BRAND_ENGINE)
    creq={'requestId':'V1','projectId':'P','workflowMode':'transcript_only','contentType':'vertical','stage':'ALFA','editProfile':'XR_FULL','timingQuality':'exact','transcript':'x','editorialPlan':'','projectConfig':{},'brandAdapter':{},'specialRules':''}
    cfolder=Path(content.build_content_ai_package(creq,tmp_path,CONTENT_RES)['folder'])
    bproj={'brandId':'B','brandName':'Brand','canonVersion':'R6','rawContext':'x','brandForm':{},'method':{'summary':{}},'brandAdapterDraft':{},'references':[]}
    bfolder=Path(brand.build_brand_ai_package(bproj,tmp_path,BRAND_RES)['folder'])
    c=json.loads((cfolder/'contract_manifest.json').read_text())
    b=json.loads((bfolder/'contract_manifest.json').read_text())
    g=json.loads((ROOT/'PATCH_GEOMETRA'/'r6'/'R6_1_CONTRACT.json').read_text())
    assert c['canonFamily']==b['canonFamily']==g['canonFamily']=='R6'
    assert c['canonRevision']==b['canonRevision']==g['canonRevision']=='R6.1'
    assert set(g['features']) <= set(c['features']) | {'captionGroupsR6'}
    assert b['brandSchema']=='abrxos.brand-adapter.r6'


def test_content_library_hashes_match_geometra_r6_libraries(tmp_path):
    content=load('ceng2',CONTENT_ENGINE)
    req={'requestId':'V2','projectId':'P','workflowMode':'transcript_only','contentType':'vertical','stage':'ALFA','editProfile':'XR_FULL','timingQuality':'exact','transcript':'x','editorialPlan':'','projectConfig':{},'brandAdapter':{},'specialRules':''}
    folder=Path(content.build_content_ai_package(req,tmp_path,CONTENT_RES)['folder'])
    contract=json.loads((folder/'contract_manifest.json').read_text())
    for name,digest in contract['libraries'].items():
        gp=ROOT/'PATCH_GEOMETRA'/'r6'/name
        assert gp.exists(), name
        assert digest==f'sha256:{sha(gp)}'


def test_hotfix_manifest_declares_non_destructive_targets_and_versions():
    manifest=json.loads((ROOT/'HOTFIX_MANIFEST.json').read_text(encoding='utf-8'))
    assert manifest['hotfixId']=='ABRXOS_ECOSYSTEM_V3_1_1_R6_1'
    assert manifest['targets']['geometra']['resultVersion']=='3.1.1'
    assert manifest['targets']['contentBuilder']['resultVersion']=='1.0.1'
    assert manifest['targets']['brandBuilder']['resultVersion']=='1.0.1'
    assert manifest['dataMigration'] is False
    assert manifest['appReplacement'] is False
    assert '~/ABRXOS_GEOMETRA_DATA' in manifest['protectedDataDirs']
