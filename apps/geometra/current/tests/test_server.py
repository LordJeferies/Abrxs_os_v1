from pathlib import Path
import json
from geometra.library import Library
from geometra.registry import RendererRegistry, CatalogRegistry
from geometra.server import create_server

ROOT=Path(__file__).resolve().parents[1]


def test_library_merge_updates_same_piece_without_duplicate(tmp_path):
    lib=Library(tmp_path/'library.json')
    a={'schemaVersion':'abrxos.document.v3','documentType':'ABRXOS_CANONICAL_DOCUMENT','projectId':'P','title':'P','pieces':[{'id':'v1','canonicalId':'V1','type':'vertical','title':'Old','timeline':[],'sourceRanges':[]}], 'revision':{'id':'R1','number':1}, 'catalogVersions':{}, 'extensions':{}, 'importHistory':[], 'sourcePayload':{}}
    b=json.loads(json.dumps(a));b['pieces'][0]['title']='New';b['pieces'].append({'id':'v2','canonicalId':'V2','type':'vertical','title':'Two','timeline':[],'sourceRanges':[]})
    lib.merge(a); result=lib.merge(b)
    assert result['stats']=={'new':1,'updated':1,'unchanged':0}
    assert len(lib.get('P')['pieces'])==2
    assert next(x for x in lib.get('P')['pieces'] if x['canonicalId']=='V1')['title']=='New'


def test_server_state_exposes_renderers_and_catalogs(tmp_path):
    lib=Library(tmp_path/'library.json')
    rr=RendererRegistry(ROOT/'renderers'); cr=CatalogRegistry(ROOT/'catalogs')
    server=create_server(('127.0.0.1',0),lib,rr,cr,ROOT)
    assert server.library is lib
    assert {x['rendererId'] for x in server.renderers.list()} >= {'joc-classic','shadcn-studio'}
    assert server.catalogs.get('xr','XR06')['id']=='XR06'
    server.server_close()


def test_calendar_update_transitions_ready_and_scheduled_workflow(tmp_path):
    lib=Library(tmp_path/'library.json')
    doc={'schemaVersion':'abrxos.document.v3','documentType':'ABRXOS_CANONICAL_DOCUMENT','projectId':'CAL','title':'Calendar','pieces':[{'id':'v1','canonicalId':'V1','type':'vertical','title':'Ready','workflowStatus':'LISTO','timeline':[],'sourceRanges':[]}], 'revision':{'id':'R1','number':1}, 'catalogVersions':{}, 'extensions':{}, 'importHistory':[], 'sourcePayload':{}}
    lib.merge(doc)
    row=lib.update_piece('CAL','V1',{'scheduleDate':'2026-09-20'})
    assert row['schedule']['date']=='2026-09-20'
    assert row['workflowStatus']=='PROGRAMADO'
    row=lib.update_piece('CAL','V1',{'scheduleDate':''})
    assert row['schedule']['date']==''
    assert row['workflowStatus']=='LISTO'
