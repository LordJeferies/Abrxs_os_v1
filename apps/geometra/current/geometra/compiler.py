from __future__ import annotations
import copy, json, re
from pathlib import Path
from typing import Any
from .core import piece_id
from .registry import RendererRegistry, CatalogRegistry


def _safe_script_json(obj: Any) -> str:
    return json.dumps(obj, ensure_ascii=False, separators=(',', ':')).replace('</script>', '<\\/script>')


def extract_embedded_document(html: str) -> dict[str, Any]:
    m = re.search(r'<script[^>]+id=["\']app-data["\'][^>]*>(.*?)</script>', html, re.I | re.S)
    if not m:
        raise ValueError('No app-data found')
    return json.loads(m.group(1))


def compile_lienzo(project: dict[str, Any], renderer_id: str, piece_ids: list[str], title: str, theme: str, renderers: RendererRegistry, catalogs: CatalogRegistry, root: Path) -> str:
    manifest = renderers.get(renderer_id)
    rdir = Path(manifest['_path'])
    template = (rdir / manifest.get('entryTemplate', 'template.html')).read_text(encoding='utf-8')
    styles = (rdir / manifest.get('styles', 'styles.css')).read_text(encoding='utf-8')
    adapter = (rdir / manifest.get('adapter', 'adapter.js')).read_text(encoding='utf-8') if manifest.get('adapter') else ''
    shared = (Path(root) / 'shared' / 'lienzo_core.js').read_text(encoding='utf-8')
    # ABRXOS_PATCH:R6_COMPILER_LOAD
    r6_patch_path = Path(root) / 'shared' / 'r6_patch.js'
    r6_patch = r6_patch_path.read_text(encoding='utf-8') if r6_patch_path.exists() else ''
    # /ABRXOS_PATCH:R6_COMPILER_LOAD
    wanted = set(piece_ids or [])
    doc = copy.deepcopy(project)
    doc['pieces'] = [copy.deepcopy(p) for p in project.get('pieces', []) if not wanted or piece_id(p) in wanted]
    doc['documentType'] = 'ABRXOS_LIENZO_V3'
    doc['schemaVersion'] = 'abrxos.document.v3'
    doc['renderer'] = {'id': renderer_id, 'version': manifest['version'], 'name': manifest.get('name', renderer_id), 'theme': theme}
    doc['canvas'] = {'title': title or project.get('title') or project.get('projectId'), 'rendererId': renderer_id, 'theme': theme}
    doc['catalogSnapshot'] = {k: catalogs.list(k) for k in ('xr', 'sfx', 'motion', 'captions')}
    return (template
            .replace('/*__ABRXOS_STYLES__*/', styles)
            .replace('/*__ABRXOS_SHARED_RUNTIME__*/', shared)
            .replace('/*__ABRXOS_RENDERER_ADAPTER__*/', adapter)
            .replace('__ABRXOS_APP_DATA__', _safe_script_json(doc))
            # ABRXOS_PATCH:R6_COMPILER_INLINE
            .replace('</body>', '<script data-abrxos-r6="v3.1-r6">' + r6_patch.replace('</script>', '<\\/script>') + '</script></body>', 1)
            # /ABRXOS_PATCH:R6_COMPILER_INLINE
            .replace('__ABRXOS_TITLE__', str(doc['canvas']['title'])))
