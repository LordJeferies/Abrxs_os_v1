from pathlib import Path
import json
import pytest

from geometra.core import import_text, normalize_project, piece_id

JOC = Path('/mnt/data/JOC55_AMANDA_ALPHA_R10.1_STORY_EDITOR (2) (1)(2).html')
WEEKS = Path('/mnt/data/JOC_ALFA_A_SEMANAS_1_2-2(4).html')


def test_import_app_data_preserves_45_pieces_and_stable_ids():
    doc = import_text(JOC.name, JOC.read_text(encoding='utf-8', errors='replace'))
    assert doc['schemaVersion'] == 'abrxos.document.v3'
    assert doc['projectId'] == 'JOC55_AMANDA'
    assert len(doc['pieces']) == 45
    ids = [piece_id(x) for x in doc['pieces']]
    assert len(ids) == len(set(ids))
    assert all(ids)
    assert doc['sourcePayload']['documentType'] == 'JOC55_AMANDA_ALPHA_R10.1_STORY_EDITOR'


def test_import_seed_keeps_piece_count():
    if not WEEKS.exists():
        pytest.skip('weeks fixture not present')
    doc = import_text(WEEKS.name, WEEKS.read_text(encoding='utf-8', errors='replace'))
    assert len(doc['pieces']) == 22
    assert doc['sourceFormat'] == 'seed'


def test_normalize_v2_keeps_unknown_fields_and_migrates_schema():
    source = {
        'schemaVersion': 'abrxos.lienzo.v2',
        'documentType': 'ABRXOS_LIENZO_V2',
        'projectId': 'P1',
        'title': 'Old',
        'pieces': [{'id': 'v01', 'canonicalId': 'V01', 'type': 'vertical', 'mystery': {'keep': 1}}],
        'unknownRoot': {'x': 7},
    }
    doc = normalize_project(source, 'old.json')
    assert doc['schemaVersion'] == 'abrxos.document.v3'
    assert doc['pieces'][0]['mystery'] == {'keep': 1}
    assert doc['sourcePayload']['unknownRoot'] == {'x': 7}
    assert doc['migration']['fromSchema'] == 'abrxos.lienzo.v2'


def test_json_single_piece_is_wrapped_as_project():
    piece = {'contentId': 'C1', 'type': 'carousel', 'title': 'X', 'custom': 9}
    doc = import_text('piece.json', json.dumps(piece))
    assert len(doc['pieces']) == 1
    assert piece_id(doc['pieces'][0]) == 'C1'
    assert doc['pieces'][0]['custom'] == 9


def test_source_payload_preserves_root_metadata_without_duplicating_normalized_pieces():
    source = {
        'schemaVersion': 'legacy.v1',
        'projectId': 'P2',
        'unknownRoot': {'keep': True},
        'pieces': [
            {'id': 'a', 'title': 'A', 'unknownPiece': 1},
            {'id': 'b', 'title': 'B', 'unknownPiece': 2},
        ],
    }
    doc = normalize_project(source, 'legacy.json')
    assert 'pieces' not in doc['sourcePayload']
    assert doc['sourcePayload']['unknownRoot'] == {'keep': True}
    assert [p['unknownPiece'] for p in doc['pieces']] == [1, 2]


def test_cutter_gate_validates_video_source_ranges_but_ignores_static_pieces():
    from geometra.core import cutter_gate
    doc = {
        'pieces': [
            {'canonicalId':'V1','type':'vertical','source':'DEFAULT','sourceRanges':[{'start':1.0,'end':2.0}]},
            {'canonicalId':'V2','type':'vertical','source':'DEFAULT','sourceRanges':[]},
            {'canonicalId':'C1','type':'carousel','sourceRanges':[]},
        ]
    }
    gate = cutter_gate(doc)
    assert gate['ready'] is False
    assert gate['critical'] == 1
    assert next(x for x in gate['pieces'] if x['id']=='V1')['ready'] is True
    assert next(x for x in gate['pieces'] if x['id']=='V2')['ready'] is False
    assert all(x['id']!='C1' for x in gate['pieces'])


def test_v3_roundtrip_source_payload_does_not_nest_itself_and_keeps_unknown_root_fields():
    source={
        'schemaVersion':'abrxos.document.v3','documentType':'ABRXOS_LIENZO_V3','projectId':'P3','title':'V3',
        'pieces':[{'id':'v1','canonicalId':'V1','type':'vertical','title':'One'}],
        'sourcePayload':{'legacyRoot':{'keep':1}},
        'futureRoot':{'keep':2},
        'renderer':{'id':'shadcn-studio'},
    }
    doc=normalize_project(source,'v3.html')
    assert doc['sourcePayload']['legacyRoot']=={'keep':1}
    assert doc['sourcePayload']['futureRoot']=={'keep':2}
    assert 'sourcePayload' not in doc['sourcePayload']
    assert 'pieces' not in doc['sourcePayload']


def test_caption_normalizer_splits_within_part_to_short_units_and_is_idempotent():
    source={
        'projectId':'CAPS','title':'Captions','pieces':[{
            'id':'v1','canonicalId':'V1','type':'vertical','title':'Clip',
            'timeline':[{'id':'CAP1','track':'captions','start':0,'end':8,'partId':'P1','text':'No hay atajos, nadie estudia por ti. Tú lo tienes que hacer.','timingMode':'locked_to_source'}],
            'sourceRanges':[{'start':10,'end':18}], 'parts':[]
        }]
    }
    doc=normalize_project(source,'caps.json')
    caps=[e for e in doc['pieces'][0]['timeline'] if e.get('track')=='captions']
    assert len(caps)>1
    assert all(e.get('captionSchema')=='abrxos.caption.v2' for e in caps)
    assert all(e.get('partId')=='P1' for e in caps)
    assert all(1 <= e.get('wordCount',0) <= 5 for e in caps)
    assert all(e.get('sourceText')=='No hay atajos, nadie estudia por ti. Tú lo tienes que hacer.' for e in caps)
    ids=[e['id'] for e in caps]
    doc2=normalize_project(doc,'caps-v3.json')
    assert [e['id'] for e in doc2['pieces'][0]['timeline'] if e.get('track')=='captions']==ids
