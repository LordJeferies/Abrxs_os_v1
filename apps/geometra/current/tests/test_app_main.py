import json
from geometra.app_main import prepare_library


def test_prepare_library_migrates_legacy_once_and_reuses_v3(tmp_path):
    legacy=tmp_path/'library.json'
    legacy.write_text(json.dumps({'projects':{'P':{'schemaVersion':'abrxos.lienzo.v2','projectId':'P','title':'Legacy','pieces':[]}},'currentProjectId':'P'}),encoding='utf-8')
    lib=prepare_library(tmp_path)
    assert lib.current()['projectId']=='P'
    assert (tmp_path/'library_v3.json').exists()
    # A later run must use the V3 library, not re-copy modified legacy data.
    legacy.write_text(json.dumps({'projects':{}}),encoding='utf-8')
    lib2=prepare_library(tmp_path)
    assert lib2.current()['projectId']=='P'
