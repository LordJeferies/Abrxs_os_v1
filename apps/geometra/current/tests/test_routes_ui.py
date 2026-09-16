from playwright.sync_api import sync_playwright
from tests.helpers import ROOT, synthetic_project
from geometra.registry import RendererRegistry, CatalogRegistry
from geometra.compiler import compile_lienzo


def route_project():
    p=synthetic_project()
    piece=p['pieces'][0]
    piece['storyScripts']={
        'source':[{'id':'SRC_SOURCE','partId':'P1','role':'HOOK','speaker':'Amanda','text':'Source route','start':0,'end':4}],
        'voA':[{'id':'SRC_VOA','partId':'P1','role':'HOOK','speaker':'Amanda','text':'VO A route','start':0,'end':4}],
    }
    piece['timeline']=[
        {'id':'AR_SOURCE','track':'aroll','type':'aroll','label':'Source A-roll','start':0,'end':4,'partId':'P1','text':'Source route','routes':['source'],'timingMode':'locked_to_source'},
        {'id':'AR_VOA','track':'aroll','type':'aroll','label':'VO A A-roll','start':0,'end':4,'partId':'P1','text':'VO A route','routes':['voA'],'timingMode':'locked_to_source'},
        {'id':'XR_SOURCE','track':'xr','type':'xr','label':'Source XR','definitionId':'XR06','start':1,'end':3,'routes':['source'],'states':[],'assets':[],'timingMode':'free'},
        {'id':'XR_VOA','track':'xr','type':'xr','label':'VO A XR','definitionId':'XR06','start':1,'end':3,'routes':['voA'],'states':[],'assets':[],'timingMode':'free'},
    ]
    return p


def compile_route_html(renderer='joc-classic'):
    rr=RendererRegistry(ROOT/'renderers');cr=CatalogRegistry(ROOT/'catalogs')
    return compile_lienzo(route_project(),renderer,[],f'Route test {renderer}','dark',rr,cr,ROOT)


def test_route_selector_filters_overlapping_timeline_events_and_click_selects_only_visible_route():
    html=compile_route_html()
    with sync_playwright() as pw:
        b=pw.chromium.launch(headless=True,executable_path='/usr/bin/chromium',args=['--no-sandbox'])
        page=b.new_page(viewport={'width':1200,'height':800});errors=[];dialogs=[]
        page.on('pageerror',lambda e:errors.append(str(e)))
        page.on('dialog',lambda d:(dialogs.append(d.message),d.dismiss()))
        page.set_content(html,wait_until='load');page.wait_for_timeout(80)
        assert page.locator('#route-select').count()==1
        assert page.locator('#route-select').input_value()=='voA'
        assert page.locator('[data-event-id="AR_SOURCE"]').count()==0
        assert page.locator('[data-event-id="AR_VOA"]').count()==1
        before=page.evaluate("ABRXOS.getEvent('AR_VOA').start")
        page.locator('[data-event-id="AR_VOA"]').click();page.wait_for_timeout(30)
        assert page.evaluate('ABRXOS.state.selectedEventId')=='AR_VOA'
        assert page.evaluate("ABRXOS.getEvent('AR_VOA').start")==before
        assert dialogs==[]
        assert 'VO A route' in page.locator('.story-panel').inner_text()
        page.select_option('#route-select','source');page.wait_for_timeout(40)
        assert page.locator('[data-event-id="AR_VOA"]').count()==0
        assert page.locator('[data-event-id="AR_SOURCE"]').count()==1
        assert 'Source route' in page.locator('.story-panel').inner_text()
        assert not errors
        b.close()
