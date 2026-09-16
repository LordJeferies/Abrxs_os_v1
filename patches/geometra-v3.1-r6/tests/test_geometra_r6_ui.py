from __future__ import annotations
import json
from pathlib import Path
from playwright.sync_api import sync_playwright

WORK=Path(__file__).resolve().parents[1]
PATCH=(WORK/'payload/app/r6_patch.js').read_text(encoding='utf-8')
CSS=(WORK/'payload/app/r6_patch.css').read_text(encoding='utf-8')


def fixture_html():
    project={
      'projectId':'P1','title':'Project','pieces':[
        {'canonicalId':'V1','type':'vertical','title':'Clip one','stage':'ALFA','workflowStatus':'PENDIENTE','schedule':{'date':'','time':'','platforms':[]},'sourceRanges':[{'start':10,'end':20}],'productionChecklist':{'editorial':{'status':'ready'},'source':{'status':'ready'},'images':{'status':'pending'}}},
        {'canonicalId':'C1','type':'carousel','title':'Carousel','stage':'BETA','workflowStatus':'REVISADO','schedule':{'date':'','time':'','platforms':[]},'sourceRanges':[]}
      ]
    }
    validation={'schema':'abrxos.r6-validation.v1','r6Detected':True,'critical':[],'warnings':[],'pieces':[{'id':'V1','alphaReady':True,'cutterReady':True,'progressPercent':40,'missing':[],'warnings':[]},{'id':'C1','alphaReady':False,'cutterReady':False,'progressPercent':20,'missing':['staticProduction.items'],'warnings':[]}], 'summary':{'criticalCount':0,'warningCount':0}}
    return f'''<!doctype html><html><head><style>{CSS}</style></head><body>
    <nav><button data-view="kanban">Kanban</button></nav><main><section id="library"></section><section id="build"></section><section id="kanban"></section></main><div id="toast"></div>
    <script>
    const $=s=>document.querySelector(s), $$=s=>Array.from(document.querySelectorAll(s));
    window.calls=[];
    window.APP_STATE={{data:{{currentProjectId:'P1',current:{json.dumps(project)},projects:[]}},currentProjectId:'P1',view:'kanban',selected:new Set(['V1','C1']),selectionProjectId:'P1',r6Validation:{json.dumps(validation)}}};
    function esc(s){{return String(s??'')}}
    function current(){{return APP_STATE.data.current}}
    function pieces(){{return current().pieces}}
    async function api(path,method='GET',body){{calls.push({{path,method,body}}); if(path==='/api/r6_validate') return {{ok:true,validation:APP_STATE.r6Validation}}; return {{ok:true,piece:pieces().find(x=>x.canonicalId===body?.pieceId)}}}}
    function toast(t){{document.querySelector('#toast').textContent=t}}
    function renderSidebar(){{}}
    function renderProjects(){{}}
    function renderKanban(){{document.querySelector('#kanban').innerHTML='<div>BASE</div>'}}
    function renderBuild(){{document.querySelector('#build').innerHTML='<label class="build-row"><input data-build-piece type="checkbox" value="V1"><span><b>Clip one</b></span></label><aside class="panel stack"></aside>'}}
    function renderLibrary(){{document.querySelector('#library').innerHTML='<table><tbody><tr data-piece-row="V1"><td>V1</td><td>Clip one</td></tr></tbody></table>'}}
    function render(){{if(APP_STATE.view==='kanban')renderKanban();else if(APP_STATE.view==='build')renderBuild();else renderLibrary()}}
    </script><script>{PATCH}</script><script>render()</script></body></html>'''


def test_kanban_drag_persists_only_workflow_status_and_updates_column():
    with sync_playwright() as pw:
        b=pw.chromium.launch(headless=True,executable_path='/usr/bin/chromium',args=['--no-sandbox'])
        page=b.new_page(viewport={'width':1400,'height':850});errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
        page.set_content(fixture_html(),wait_until='load');page.wait_for_timeout(80)
        card=page.locator('[data-kanban-piece="V1"]'); target=page.locator('[data-workflow="HACIENDO"]')
        assert card.count()==1 and target.count()==1
        card.drag_to(target);page.wait_for_timeout(120)
        call=page.evaluate("calls.find(x=>x.path==='/api/update_piece')")
        assert call['body']=={'projectId':'P1','pieceId':'V1','patch':{'workflowStatus':'HACIENDO'}}
        piece=page.evaluate("APP_STATE.data.current.pieces.find(x=>x.canonicalId==='V1')")
        assert piece['workflowStatus']=='HACIENDO'
        assert piece['stage']=='ALFA'
        assert piece['sourceRanges']==[{'start':10,'end':20}]
        assert piece['schedule']=={'date':'','time':'','platforms':[]}
        assert page.locator('[data-workflow="HACIENDO"] [data-kanban-piece="V1"]').count()==1
        assert not errors
        b.close()


def test_kanban_cards_show_production_progress_and_alpha_cutter_badges():
    with sync_playwright() as pw:
        b=pw.chromium.launch(headless=True,executable_path='/usr/bin/chromium',args=['--no-sandbox']);page=b.new_page();page.set_content(fixture_html());page.wait_for_timeout(70)
        text=page.locator('[data-kanban-piece="V1"]').inner_text()
        assert 'ALFA' in text
        assert 'Cutter' in text
        assert '40%' in text
        text2=page.locator('[data-kanban-piece="C1"]').inner_text()
        assert 'BETA' in text2 and '20%' in text2
        b.close()


def test_build_and_library_get_r6_validation_decorations():
    html=fixture_html().replace("APP_STATE.view:'kanban'","APP_STATE.view:'build'")
    with sync_playwright() as pw:
        b=pw.chromium.launch(headless=True,executable_path='/usr/bin/chromium',args=['--no-sandbox']);page=b.new_page();page.set_content(html);page.wait_for_timeout(70)
        page.evaluate("APP_STATE.view='build';render()")
        assert page.locator('#build .r6-validation-badge').count()>=1
        assert 'Alpha' in page.locator('#build').inner_text()
        page.evaluate("APP_STATE.view='library';render()")
        assert 'R6' in page.locator('#library').inner_text() or page.locator('#library .r6-validation-summary').count()==1
        b.close()

def test_geometra_kanban_shows_edit_profile_commercial_name_and_code():
    with sync_playwright() as pw:
        b=pw.chromium.launch(headless=True,executable_path='/usr/bin/chromium',args=['--no-sandbox']);page=b.new_page();page.set_content(fixture_html());page.evaluate("APP_STATE.data.current.pieces[0].editProfile={code:'XR_FULL',commercialName:'Cinematic Edit'};renderKanban()") ;page.wait_for_timeout(60)
        text=page.locator('[data-kanban-piece="V1"]').inner_text()
        assert 'Cinematic Edit' in text and 'XR_FULL' in text
        b.close()
