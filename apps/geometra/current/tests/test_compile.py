from pathlib import Path
import json, re
from geometra.core import import_text, piece_id
from geometra.registry import RendererRegistry, CatalogRegistry
from geometra.compiler import compile_lienzo, extract_embedded_document

ROOT = Path(__file__).resolve().parents[1]
JOC = Path('/mnt/data/JOC55_AMANDA_ALPHA_R10.1_STORY_EDITOR (2) (1)(2).html')


def test_same_document_compiles_through_two_renderers_without_domain_changes():
    doc = import_text(JOC.name, JOC.read_text(encoding='utf-8', errors='replace'))
    ids = [piece_id(x) for x in doc['pieces'][:3]]
    rr = RendererRegistry(ROOT / 'renderers')
    cr = CatalogRegistry(ROOT / 'catalogs')
    html_a = compile_lienzo(doc, 'joc-classic', ids, 'Demo', 'dark', rr, cr, ROOT)
    html_b = compile_lienzo(doc, 'shadcn-studio', ids, 'Demo', 'dark', rr, cr, ROOT)
    a = extract_embedded_document(html_a)
    b = extract_embedded_document(html_b)
    assert a['pieces'] == b['pieces']
    assert a['projectId'] == b['projectId']
    assert a['renderer']['id'] == 'joc-classic'
    assert b['renderer']['id'] == 'shadcn-studio'
    assert len(a['pieces']) == 3


def test_compiled_lienzo_is_standalone_and_contains_shared_runtime():
    doc = import_text(JOC.name, JOC.read_text(encoding='utf-8', errors='replace'))
    rr = RendererRegistry(ROOT / 'renderers')
    cr = CatalogRegistry(ROOT / 'catalogs')
    html = compile_lienzo(doc, 'joc-classic', [piece_id(doc['pieces'][0])], 'One', 'dark', rr, cr, ROOT)
    assert '<script id="app-data" type="application/json">' in html
    assert 'ABRXOS_LIENZO_V3' in html
    assert 'data-abrxos-runtime="v3"' in html
    assert 'https://' not in html
    assert '<link ' not in html


def test_unknown_renderer_fails_cleanly():
    doc = {'schemaVersion':'abrxos.document.v3','projectId':'P','pieces':[]}
    rr = RendererRegistry(ROOT / 'renderers')
    cr = CatalogRegistry(ROOT / 'catalogs')
    try:
        compile_lienzo(doc, 'missing-renderer', [], 'X', 'dark', rr, cr, ROOT)
    except KeyError as exc:
        assert 'missing-renderer' in str(exc)
    else:
        raise AssertionError('expected KeyError')
