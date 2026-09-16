from __future__ import annotations
import importlib.util, json, shutil, sys
from pathlib import Path
from playwright.sync_api import sync_playwright
from test_server_compiler_hooks import make_install

WORK=Path(__file__).resolve().parents[1]
R6_ROOT=Path('/mnt/data/r6pkg/ABRXOS_CANON_R6_AI_GEOMETRA')

def load_apply():
    spec=importlib.util.spec_from_file_location('patcher_e2e',WORK/'tools/apply_patch.py')
    mod=importlib.util.module_from_spec(spec); assert spec and spec.loader; spec.loader.exec_module(mod); return mod


def test_official_r6_intro_compiles_to_standalone_lienzo_with_r6_inspector_and_source_ranges_unchanged(tmp_path):
    target=make_install(tmp_path)
    # Replace the tiny compiler-test runtime with a small V3-compatible projection so
    # Chromium can select a real R6 event after the patch is inlined by the compiler.
    (target/'shared/lienzo_core.js').write_text(r'''(()=>{'use strict';
const project=JSON.parse(document.querySelector('#app-data').textContent||'{}');
const state={project,selectedPieceId:project.pieces?.[0]?.canonicalId||null,selectedEventId:null};
const pid=p=>p?.canonicalId||p?.id;const piece=()=>project.pieces.find(p=>pid(p)===state.selectedPieceId)||project.pieces[0];
function getPiece(id){return project.pieces.find(p=>pid(p)===id)||null}function getEvent(id){for(const p of project.pieces||[])for(const e of p.timeline||[])if(e.id===id)return e;return null}
function render(){const p=piece(),e=getEvent(state.selectedEventId);document.querySelector('#app').innerHTML=`<header class="piecehead"><div><h1>${p.title||pid(p)}</h1></div><div class="pieceactions"></div></header><div id="inspector"><h2>${e?.label||e?.id||p.title||pid(p)}</h2></div><div>${(p.timeline||[]).map(x=>`<button data-event-id="${x.id}">${x.label||x.id}</button>`).join('')}</div>`;document.querySelectorAll('[data-event-id]').forEach(b=>b.onclick=()=>{state.selectedEventId=b.dataset.eventId;render()})}
window.ABRXOS={state,getPiece,getEvent,render};render();})();''',encoding='utf-8')
    patch=WORK; backups=tmp_path/'backups';load_apply().apply_patch(target,patch,backups)
    sys.path.insert(0,str(target))
    try:
        import geometra.server as server
        class RR:
            def get(self,rid): return {'_path':str(target/'renderers/joc-classic'),'entryTemplate':'template.html','styles':'styles.css','version':'1.0'}
        class CR: pass
        project=json.loads((R6_ROOT/'05_FICHAS/INTRO/FICHA_INTRO_ALFA_CINEMATIC_R6.json').read_text(encoding='utf-8'))
        original_ranges=json.loads(json.dumps(project['pieces'][0]['sourceRanges']))
        html=server.compile_lienzo(project,'joc-classic',[],'R6 Intro','dark',RR(),CR(),target)
        assert html.count('data-abrxos-r6="v3.1-r6"')==1
        assert original_ranges==project['pieces'][0]['sourceRanges']
        with sync_playwright() as pw:
            b=pw.chromium.launch(headless=True,executable_path='/usr/bin/chromium',args=['--no-sandbox']);page=b.new_page();errors=[];page.on('pageerror',lambda e:errors.append(str(e)));page.set_content(html,wait_until='load');page.wait_for_timeout(100)
            xr_id=page.evaluate("ABRXOS.state.project.pieces[0].timeline.find(e=>e.track==='xr'&&e.xrFamily).id")
            page.locator(f'[data-event-id="{xr_id}"]').click();page.wait_for_timeout(100)
            text=page.locator('#inspector').inner_text()
            assert 'XR R6' in text
            assert not errors
            b.close()
    finally:
        sys.path.remove(str(target))
        for name in list(sys.modules):
            if name=='geometra' or name.startswith('geometra.'):
                sys.modules.pop(name,None)

def test_legacy_joc_amanda_source_ranges_survive_r6_validation_and_compile(tmp_path):
    import re
    legacy_path=Path('/mnt/data/JOC55_AMANDA_ALPHA_R10.1_STORY_EDITOR (2) (1)(2).html')
    raw=legacy_path.read_text(encoding='utf-8',errors='replace')
    match=re.search(r'<script[^>]+id=["\']app-data["\'][^>]*>(.*?)</script>',raw,re.I|re.S)
    assert match
    project=json.loads(match.group(1))
    original={str(p.get('canonicalId') or p.get('id')):json.loads(json.dumps(p.get('sourceRanges',[]))) for p in project.get('pieces',[])}
    target=make_install(tmp_path);load_apply().apply_patch(target,WORK,tmp_path/'backups')
    sys.path.insert(0,str(target))
    try:
        import geometra.server as server
        class RR:
            def get(self,rid): return {'_path':str(target/'renderers/joc-classic'),'entryTemplate':'template.html','styles':'styles.css','version':'1.0'}
        class CR: pass
        html=server.compile_lienzo(project,'joc-classic',[],'Legacy JOC','dark',RR(),CR(),target)
        m=re.search(r'<script[^>]+id=["\']app-data["\'][^>]*>(.*?)</script>',html,re.I|re.S);assert m
        embedded=json.loads(m.group(1))
        after={str(p.get('canonicalId') or p.get('id')):p.get('sourceRanges',[]) for p in embedded.get('pieces',[])}
        assert after==original
        assert embedded.get('r6Version')=='LEGACY_COMPAT'
    finally:
        sys.path.remove(str(target))
        for name in list(sys.modules):
            if name=='geometra' or name.startswith('geometra.'):
                sys.modules.pop(name,None)
