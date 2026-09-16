import json
from geometra.migrate_library import migrate_legacy_library
from geometra.library import Library


def test_v2_library_is_copied_into_v3_without_touching_legacy_file(tmp_path):
    legacy=tmp_path/'library.json'; target=tmp_path/'library_v3.json'
    legacy_data={'schemaVersion':'abrxos.geometra.library.v1','currentProjectId':'P1','projects':{'P1':{'schemaVersion':'abrxos.lienzo.v2','documentType':'ABRXOS_LIENZO_V2','projectId':'P1','title':'Old Project','pieces':[{'id':'v1','canonicalId':'V1','type':'vertical','title':'Clip','sourceRanges':[{'start':1,'end':2}],'timeline':[]}]}}}
    legacy.write_text(json.dumps(legacy_data),encoding='utf-8')
    before=legacy.read_text(encoding='utf-8')
    result=migrate_legacy_library(legacy,target)
    assert result['migrated']==1
    assert legacy.read_text(encoding='utf-8')==before
    lib=Library(target)
    assert lib.current()['schemaVersion']=='abrxos.document.v3'
    assert lib.current()['pieces'][0]['canonicalId']=='V1'
