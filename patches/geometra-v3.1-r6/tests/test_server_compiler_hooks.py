from __future__ import annotations
import importlib.util, json, shutil, sys
from pathlib import Path

WORK = Path(__file__).resolve().parents[1]


def load_apply():
    spec=importlib.util.spec_from_file_location('patcher_hooks',WORK/'tools/apply_patch.py')
    mod=importlib.util.module_from_spec(spec); assert spec and spec.loader; spec.loader.exec_module(mod); return mod


def make_install(tmp: Path) -> Path:
    t=tmp/'ABRXOS_GEOMETRA_V3'
    for d in ['geometra','app','shared','renderers/joc-classic']:(t/d).mkdir(parents=True,exist_ok=True)
    (t/'VERSION.json').write_text(json.dumps({'product':'ABRXOS GEOMETRA','version':'3.0.0'}))
    (t/'geometra/__init__.py').write_text('')
    (t/'geometra/core.py').write_text("def import_text(name,text):\n import json\n return json.loads(text)\ndef piece_id(x): return x.get('canonicalId') or x.get('id')\n")
    (t/'geometra/registry.py').write_text('class RendererRegistry: pass\nclass CatalogRegistry: pass\n')
    (t/'geometra/compiler.py').write_text('''from __future__ import annotations\nimport copy, json, re\nfrom pathlib import Path\nfrom typing import Any\nfrom .core import piece_id\nfrom .registry import RendererRegistry, CatalogRegistry\n\ndef _safe_script_json(obj): return json.dumps(obj)\n\ndef compile_lienzo(project, renderer_id, piece_ids, title, theme, renderers, catalogs, root):\n    manifest = renderers.get(renderer_id)\n    rdir = Path(manifest['_path'])\n    template = (rdir / manifest.get('entryTemplate','template.html')).read_text(encoding='utf-8')\n    styles = (rdir / manifest.get('styles','styles.css')).read_text(encoding='utf-8')\n    adapter = ''\n    shared = (Path(root) / 'shared' / 'lienzo_core.js').read_text(encoding='utf-8')\n    wanted=set(piece_ids or [])\n    doc=copy.deepcopy(project)\n    doc['pieces']=[copy.deepcopy(p) for p in project.get('pieces',[]) if not wanted or piece_id(p) in wanted]\n    doc['documentType']='ABRXOS_LIENZO_V3'\n    doc['renderer']={'id':renderer_id,'version':'1.0','theme':theme}\n    doc['canvas']={'title':title,'rendererId':renderer_id,'theme':theme}\n    return (template\n            .replace('/*__ABRXOS_STYLES__*/', styles)\n            .replace('/*__ABRXOS_SHARED_RUNTIME__*/', shared)\n            .replace('/*__ABRXOS_RENDERER_ADAPTER__*/', adapter)\n            .replace('__ABRXOS_APP_DATA__', _safe_script_json(doc))\n            .replace('__ABRXOS_TITLE__', str(doc['canvas']['title'])))\n''')
    (t/'geometra/server.py').write_text('''from __future__ import annotations\nimport json, mimetypes\nfrom pathlib import Path\nfrom .core import import_text, piece_id\nfrom .compiler import compile_lienzo\n\nclass Handler:\n    def do_GET(self):\n        path='/'\n        mapping={'/':'app/index.html','/app.js':'app/app.js','/styles.css':'app/styles.css'}\n    def do_POST(self):\n        path='/api/compile'; data={}\n        if path=='/api/compile':\n            return\n''')
    (t/'app/index.html').write_text('<!doctype html><html><head></head><body><script src="/app.js"></script></body></html>')
    (t/'app/app.js').write_text('window.APP_STATE={};\n')
    (t/'app/styles.css').write_text('body{}\n')
    (t/'shared/lienzo_core.js').write_text("(()=>{window.ABRXOS={state:{project:{pieces:[]}}};})();\n")
    (t/'renderers/joc-classic/template.html').write_text('<!doctype html><html><head><style>/*__ABRXOS_STYLES__*/</style></head><body><div id="app"></div><script id="app-data" type="application/json">__ABRXOS_APP_DATA__</script><script>/*__ABRXOS_SHARED_RUNTIME__*/</script><script>/*__ABRXOS_RENDERER_ADAPTER__*/</script></body></html>')
    (t/'renderers/joc-classic/styles.css').write_text('body{}')
    return t


def make_patch_copy(tmp: Path) -> Path:
    p=tmp/'patch'; shutil.copytree(WORK,p)
    return p


def test_patch_injects_server_r6_routes_and_compiler_runtime(tmp_path):
    apply=load_apply(); target=make_install(tmp_path); patch=make_patch_copy(tmp_path); backups=tmp_path/'backups'
    result=apply.apply_patch(target,patch,backups)
    assert result['status']=='applied'
    server=(target/'geometra/server.py').read_text()
    assert 'validate_r6_project' in server
    assert '/api/r6_validate' in server
    assert '/r6_patch.js' in server and '/r6_patch.css' in server
    compiler=(target/'geometra/compiler.py').read_text()
    assert "shared/r6_patch.js" in compiler or "'r6_patch.js'" in compiler
    assert 'data-abrxos-r6' in compiler
    index=(target/'app/index.html').read_text()
    assert '<script src="/r6_patch.js"></script>' in index
    assert '<link rel="stylesheet" href="/r6_patch.css">' in index


def test_patched_compiler_inlines_r6_runtime_once(tmp_path):
    apply=load_apply(); target=make_install(tmp_path); patch=make_patch_copy(tmp_path); backups=tmp_path/'backups'; apply.apply_patch(target,patch,backups)
    sys.path.insert(0,str(target))
    try:
        import geometra.compiler as c
        class RR:
            def get(self,rid): return {'_path':str(target/'renderers/joc-classic'),'entryTemplate':'template.html','styles':'styles.css','version':'1.0'}
        class CR: pass
        html=c.compile_lienzo({'projectId':'P','pieces':[{'canonicalId':'V1'}]},'joc-classic',[],'X','dark',RR(),CR(),target)
        assert html.count('data-abrxos-r6="v3.1-r6"') == 1
        assert 'ABRXOS_R6' in html
    finally:
        sys.path.remove(str(target))
        for name in list(sys.modules):
            if name=='geometra' or name.startswith('geometra.'):
                sys.modules.pop(name,None)

def test_server_compile_wrapper_refreshes_r6_validation_before_export(tmp_path):
    apply=load_apply(); target=make_install(tmp_path); patch=make_patch_copy(tmp_path); backups=tmp_path/'backups'; apply.apply_patch(target,patch,backups)
    sys.path.insert(0,str(target))
    try:
        import geometra.server as s
        class RR:
            def get(self,rid): return {'_path':str(target/'renderers/joc-classic'),'entryTemplate':'template.html','styles':'styles.css','version':'1.0'}
        class CR: pass
        project={'schemaVersion':'abrxos.content-project.r6','projectId':'P','pieces':[{'canonicalId':'V1','type':'vertical','stage':'ALFA','workflowStatus':'PENDIENTE','source':'DEFAULT','sourceRanges':[{'start':1,'end':2}],'timeline':[]}]}
        html=s.compile_lienzo(project,'joc-classic',[],'X','dark',RR(),CR(),target)
        assert '"r6Validation"' in html or '&quot;r6Validation&quot;' in html
        assert '"r6Version":"R6"' in html or '"r6Version": "R6"' in html
    finally:
        sys.path.remove(str(target))
        for name in list(sys.modules):
            if name=='geometra' or name.startswith('geometra.'):
                sys.modules.pop(name,None)
