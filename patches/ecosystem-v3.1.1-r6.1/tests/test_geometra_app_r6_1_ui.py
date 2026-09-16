from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
APP_JS = (ROOT / 'PATCH_GEOMETRA' / 'app' / 'r6_patch.js').read_text(encoding='utf-8')


def test_geometra_kanban_cards_show_projection_readiness_and_r61_progress_keys():
    with sync_playwright() as pw:
        b=pw.chromium.launch(headless=True,executable_path='/usr/bin/chromium',args=['--no-sandbox'])
        page=b.new_page()
        page.set_content('<div id="kanban"></div><div id="build"></div><div id="library"></div>')
        page.evaluate("""()=>{
          window.$=s=>document.querySelector(s);window.$$=s=>Array.from(document.querySelectorAll(s));window.esc=s=>String(s??'');
          window.APP_STATE={currentProjectId:'P',view:'kanban',r6Validation:{pieces:[{id:'V1',alphaReady:true,cutterReady:true,projectionReady:false,projectionMissing:['A01 T3'],progressPercent:50}],summary:{criticalCount:0,warningCount:0,alphaReadyCount:1,cutterReadyCount:1,projectionReadyCount:0}}};
          window._piece={canonicalId:'V1',type:'vertical',title:'Clip',stage:'ALFA',workflowStatus:'PENDIENTE',editProfile:{code:'XR_FULL'},productionChecklist:{sourceAlignment:{status:'ready'},microtrim:{status:'pending'},voRecording:{status:'pending'}}};
          window.pieces=()=>[window._piece];window.current=()=>({r6Validation:APP_STATE.r6Validation});window.render=()=>{};window.renderBuild=()=>{};window.renderLibrary=()=>{};window.renderKanban=()=>{};window.api=async()=>({validation:APP_STATE.r6Validation});window.toast=()=>{};
        }""")
        page.add_script_tag(content=APP_JS)
        page.evaluate('renderKanban()')
        text=page.locator('#kanban').inner_text()
        assert 'Projection revisar' in text
        assert '50% producción' in text
        b.close()
