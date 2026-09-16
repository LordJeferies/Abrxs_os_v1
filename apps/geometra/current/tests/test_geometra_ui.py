from pathlib import Path
import json
from playwright.sync_api import sync_playwright
from geometra.library import Library
from geometra.registry import RendererRegistry, CatalogRegistry
from geometra.core import import_text
from geometra.compiler import compile_lienzo

ROOT=Path(__file__).resolve().parents[1]
JOC=Path('/mnt/data/JOC55_AMANDA_ALPHA_R10.1_STORY_EDITOR (2) (1)(2).html')


def state_fixture(tmp_path):
    lib=Library(tmp_path/'library.json')
    doc=import_text(JOC.name,JOC.read_text(encoding='utf-8',errors='replace'));lib.merge(doc)
    rr=RendererRegistry(ROOT/'renderers');cr=CatalogRegistry(ROOT/'catalogs');current=lib.current()
    return {
      'projects':[{'projectId':current['projectId'],'title':current['title'],'pieces':len(current['pieces']),'revision':current.get('revision',{})}],
      'currentProjectId':current['projectId'],'current':current,'renderers':rr.list(),'catalogs':{k:cr.list(k) for k in ('xr','sfx','motion','captions')}
    },rr,cr


def test_geometra_create_lienzo_lists_pieces_renderers_and_exports(tmp_path):
    state,rr,cr=state_fixture(tmp_path)
    index=(ROOT/'app/index.html').read_text(encoding='utf-8').replace('<head>','<head><base href="http://test.local/">',1)
    appjs=(ROOT/'app/app.js').read_text(encoding='utf-8');css=(ROOT/'app/styles.css').read_text(encoding='utf-8')
    captured={}
    with sync_playwright() as p:
        b=p.chromium.launch(headless=True,executable_path='/usr/bin/chromium',args=['--no-sandbox'])
        page=b.new_page(viewport={'width':1440,'height':900});errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
        def route(route,request):
            url=request.url
            if url.endswith('/styles.css'): route.fulfill(status=200,content_type='text/css',body=css)
            elif url.endswith('/app.js'): route.fulfill(status=200,content_type='application/javascript',body=appjs)
            elif url.endswith('/api/state'): route.fulfill(status=200,content_type='application/json',body=json.dumps({'ok':True,'state':state}))
            elif url.endswith('/api/compile'):
                body=json.loads(request.post_data or '{}');captured.update(body);html=compile_lienzo(state['current'],body['rendererId'],body['pieceIds'],body['title'],body['theme'],rr,cr,ROOT);route.fulfill(status=200,content_type='text/html',headers={'Content-Disposition':'attachment; filename="test.html"'},body=html)
            elif url.endswith('/api/select_project'): route.fulfill(status=200,content_type='application/json',body='{"ok":true}')
            else: route.fulfill(status=404,body='')
        page.route('http://test.local/**',route);page.set_content(index,wait_until='load');page.wait_for_timeout(150)
        page.locator('[data-view="build"]').click();page.wait_for_timeout(80)
        assert page.locator('[data-build-piece]').count()==45
        opts=page.locator('#rendererSelect option').all_text_contents();assert any('JOC Classic' in x for x in opts) and any('Shadcn Studio' in x for x in opts)
        page.locator('#selectNone').click();assert page.locator('#selectedBuildCount').inner_text().startswith('0')
        page.locator('#selectAll').click();assert page.locator('#selectedBuildCount').inner_text().startswith('45')
        page.select_option('#rendererSelect','shadcn-studio');page.fill('#canvasName','Amanda Shadcn')
        result=page.evaluate("""async()=>{const ids=[...document.querySelectorAll('[data-build-piece]:checked')].map(x=>x.value);const r=await fetch('/api/compile',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({projectId:window.APP_STATE.currentProjectId,pieceIds:ids,rendererId:document.querySelector('#rendererSelect').value,title:document.querySelector('#canvasName').value,theme:'dark'})});return {status:r.status,text:await r.text()}}""")
        assert result['status']==200 and 'ABRXOS_LIENZO_V3' in result['text'] and 'shadcn-studio' in result['text']
        assert captured['pieceIds'] and len(captured['pieceIds'])==45 and captured['rendererId']=='shadcn-studio'
        assert not errors
        b.close()


def test_geometra_calendar_drag_moves_between_unscheduled_and_month(tmp_path):
    state, rr, cr = state_fixture(tmp_path)
    index=(ROOT/'app/index.html').read_text(encoding='utf-8').replace('<head>','<head><base href="http://test.local/">',1)
    appjs=(ROOT/'app/app.js').read_text(encoding='utf-8'); css=(ROOT/'app/styles.css').read_text(encoding='utf-8')
    updates=[]
    with sync_playwright() as p:
        b=p.chromium.launch(headless=True,executable_path='/usr/bin/chromium',args=['--no-sandbox'])
        page=b.new_page(viewport={'width':1440,'height':900})
        def route(route, request):
            url=request.url
            if url.endswith('/styles.css'): route.fulfill(status=200,content_type='text/css',body=css)
            elif url.endswith('/app.js'): route.fulfill(status=200,content_type='application/javascript',body=appjs)
            elif url.endswith('/api/state'): route.fulfill(status=200,content_type='application/json',body=json.dumps({'ok':True,'state':state}))
            elif url.endswith('/api/update_piece'):
                payload=json.loads(request.post_data or '{}');updates.append(payload)
                piece=next(x for x in state['current']['pieces'] if (x.get('canonicalId') or x.get('id'))==payload['pieceId'])
                piece.setdefault('schedule', {'date':'','time':'','platforms':[]})['date']=payload['patch']['scheduleDate']
                route.fulfill(status=200,content_type='application/json',body=json.dumps({'ok':True,'piece':piece}))
            else: route.fulfill(status=200,content_type='application/json',body='{"ok":true}')
        page.route('http://test.local/**',route);page.set_content(index,wait_until='load');page.wait_for_timeout(120)
        page.locator('[data-view="calendar"]').click();page.wait_for_timeout(80)
        assert page.locator('.unscheduled [data-calendar-piece]').count()==45
        first=page.locator('.unscheduled [data-calendar-piece]').first
        piece_id=first.get_attribute('data-calendar-piece')
        target=page.locator('.day[data-date]').nth(10)
        date=target.get_attribute('data-date')
        first.drag_to(target);page.wait_for_timeout(150)
        assert updates and updates[-1]['pieceId']==piece_id and updates[-1]['patch']['scheduleDate']==date
        assert page.locator(f'.day[data-date="{date}"] [data-calendar-piece="{piece_id}"]').count()==1
        scheduled=page.locator(f'.day[data-date="{date}"] [data-calendar-piece="{piece_id}"]')
        scheduled.drag_to(page.locator('.unscheduled'));page.wait_for_timeout(150)
        assert updates[-1]['patch']['scheduleDate']==''
        assert page.locator(f'.unscheduled [data-calendar-piece="{piece_id}"]').count()==1
        b.close()


def test_geometra_calendar_can_navigate_months_without_losing_unscheduled_sidebar(tmp_path):
    state, rr, cr = state_fixture(tmp_path)
    index=(ROOT/'app/index.html').read_text(encoding='utf-8').replace('<head>','<head><base href="http://test.local/">',1)
    appjs=(ROOT/'app/app.js').read_text(encoding='utf-8'); css=(ROOT/'app/styles.css').read_text(encoding='utf-8')
    with sync_playwright() as p:
        b=p.chromium.launch(headless=True,executable_path='/usr/bin/chromium',args=['--no-sandbox']);page=b.new_page(viewport={'width':1440,'height':900})
        def route(route, request):
            if request.url.endswith('/styles.css'): route.fulfill(status=200,content_type='text/css',body=css)
            elif request.url.endswith('/app.js'): route.fulfill(status=200,content_type='application/javascript',body=appjs)
            elif request.url.endswith('/api/state'): route.fulfill(status=200,content_type='application/json',body=json.dumps({'ok':True,'state':state}))
            else: route.fulfill(status=200,content_type='application/json',body='{"ok":true}')
        page.route('http://test.local/**',route);page.set_content(index,wait_until='load');page.wait_for_timeout(100);page.locator('[data-view="calendar"]').click();page.wait_for_timeout(60)
        before=page.locator('.calendar-month-label').inner_text()
        page.locator('#calendarNext').click();page.wait_for_timeout(50)
        after=page.locator('.calendar-month-label').inner_text()
        assert before!=after
        assert page.locator('.unscheduled [data-calendar-piece]').count()==45
        b.close()


def test_geometra_catalogs_show_project_custom_xr_and_sfx_definitions(tmp_path):
    state, rr, cr = state_fixture(tmp_path)
    state['current'].setdefault('extensions', {}).setdefault('xrDefinitions', []).append({'id':'XR77','name':'Mapa custom','description':'Custom XR'})
    state['current']['extensions'].setdefault('sfxDefinitions', []).append({'id':'SFX_CUSTOM','name':'Bell custom','search':'soft bell'})
    index=(ROOT/'app/index.html').read_text(encoding='utf-8').replace('<head>','<head><base href="http://test.local/">',1)
    appjs=(ROOT/'app/app.js').read_text(encoding='utf-8'); css=(ROOT/'app/styles.css').read_text(encoding='utf-8')
    with sync_playwright() as p:
        b=p.chromium.launch(headless=True,executable_path='/usr/bin/chromium',args=['--no-sandbox']);page=b.new_page()
        def route(route, request):
            if request.url.endswith('/styles.css'): route.fulfill(status=200,content_type='text/css',body=css)
            elif request.url.endswith('/app.js'): route.fulfill(status=200,content_type='application/javascript',body=appjs)
            elif request.url.endswith('/api/state'): route.fulfill(status=200,content_type='application/json',body=json.dumps({'ok':True,'state':state}))
            else: route.fulfill(status=200,content_type='application/json',body='{"ok":true}')
        page.route('http://test.local/**',route);page.set_content(index,wait_until='load');page.wait_for_timeout(100);page.locator('[data-view="catalogs"]').click();page.wait_for_timeout(50)
        txt=page.locator('#catalogs').inner_text()
        assert 'XR77' in txt and 'Mapa custom' in txt
        assert 'SFX_CUSTOM' in txt and 'Bell custom' in txt
        b.close()
