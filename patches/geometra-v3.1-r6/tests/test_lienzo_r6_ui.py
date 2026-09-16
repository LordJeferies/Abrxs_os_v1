from __future__ import annotations
import json
from pathlib import Path
from playwright.sync_api import sync_playwright

WORK=Path(__file__).resolve().parents[1]
PATCH=(WORK/'payload/shared/r6_patch.js').read_text(encoding='utf-8')


def project_fixture():
    return {
      'schemaVersion':'abrxos.document.v3','projectId':'P1','canvas':{'title':'Demo'},
      'r6Validation':{'r6Detected':True,'critical':[],'warnings':[],'pieces':[{'id':'V1','alphaReady':True,'cutterReady':True,'progressPercent':50,'missing':[],'warnings':[]}], 'summary':{}},
      'pieces':[{
        'canonicalId':'V1','type':'vertical','title':'R6 clip','stage':'ALFA','workflowStatus':'HACIENDO','editProfile':{'code':'XR_FULL','commercialName':'Cinematic Edit'},
        'productionChecklist':{'editorial':{'status':'ready'},'source':{'status':'ready'},'images':{'status':'pending'}},
        'timeline':[
          {'id':'XR1','track':'xr','type':'xr','xrFamily':'COMIC_CC','label':'Comic CC','start':2,'end':10,'partId':'P1','function':'Mostrar el discurso en escenas','anchorText':'frase literal','captionPolicy':'HIDE','states':[{'stateId':'S01','start':2,'end':4,'description':'wide'}], 'assets':[{'assetId':'A01','assetType':'image','description':'Foto principal','contextAndDetail':'Contexto y detalle','whatIsVisible':'Persona y objeto','whyItMatchesSpeech':'La frase habla del objeto','prompt':'Prompt completo','brollReference':'stock reference','googleSearchQuery':'person object editorial','placementRecommendation':'fullscreen','placementReason':'necesita contexto','emojiFallback':['📌','🎯'],'durationSeconds':2,'status':'pending_creation'}]},
          {'id':'CINE1','track':'broll','type':'cine','cineType':'CINE01_BLACK_HOLD','label':'Black Hold','start':10,'end':11,'function':'Dejar caer la frase','visual':'Negro #000','motionIds':['M1'],'sfxIds':['S1'],'musicAutomation':'DUCK_TO_MUTE_HOLD_RESUME','silence':True,'captionPolicy':'HIDE_DURING_BLACK_HOLD'},
          {'id':'CAP1','track':'captions','type':'caption_group','captionSchema':'abrxos.caption.v2','captionPolicyVersion':'R6','partId':'P1','start':2,'end':10,'sourceText':'Esta es una frase semántica de diez palabras exactas aquí','wordCount':10,'highlightWord':'semántica','highlightStatus':'literal','displayMode':'normal_with_highlight','visibility':'hidden','suppressedBy':'XR1','displayCues':[{'start':2,'end':5,'text':'Esta es una frase','mode':'normal'},{'start':5,'end':6,'text':'SEMÁNTICA','mode':'hero_word'}]}
        ]
      }]
    }


def page_html():
    project=json.dumps(project_fixture())
    return f'''<!doctype html><html><body><header class="piecehead"><div><h1>R6 clip</h1></div><div class="pieceactions"></div></header><div id="inspector"></div><div id="timeline"><button class="time-block" data-event-id="XR1">XR</button><button class="time-block" data-event-id="CINE1">CINE</button><button class="time-block" data-event-id="CAP1">CAP</button></div><script>
    const project={project};
    window.ABRXOS={{state:{{project,selectedPieceId:'V1',selectedEventId:null}},getPiece(id){{return project.pieces.find(x=>x.canonicalId===id)}},getEvent(id){{return project.pieces[0].timeline.find(x=>x.id===id)}},render(){{const e=this.getEvent(this.state.selectedEventId);document.querySelector('#inspector').innerHTML=e?`<h2>${{e.label||e.id}}</h2>`:'<h2>R6 clip</h2>';}}}};
    </script><script>{PATCH}</script><script>ABRXOS.render()</script></body></html>'''


def test_r6_xr_inspector_shows_family_and_asset_production_fields():
    with sync_playwright() as pw:
        b=pw.chromium.launch(headless=True,executable_path='/usr/bin/chromium',args=['--no-sandbox']);page=b.new_page();errors=[];page.on('pageerror',lambda e:errors.append(str(e)));page.set_content(page_html());page.evaluate("ABRXOS.state.selectedEventId='XR1';ABRXOS.render()") ;page.wait_for_timeout(100)
        text=page.locator('#inspector').inner_text()
        for expected in ['Comic CC','Contexto y detalle','Persona y objeto','La frase habla del objeto','Prompt completo','person object editorial','fullscreen','necesita contexto','📌','🎯']:
            assert expected in text
        assert not errors
        b.close()


def test_cine_inspector_shows_cine_direction_not_generic_broll():
    with sync_playwright() as pw:
        b=pw.chromium.launch(headless=True,executable_path='/usr/bin/chromium',args=['--no-sandbox']);page=b.new_page();page.set_content(page_html());page.evaluate("ABRXOS.state.selectedEventId='CINE1';ABRXOS.render()") ;page.wait_for_timeout(90)
        text=page.locator('#inspector').inner_text()
        assert 'CINE01_BLACK_HOLD' in text
        assert 'Dejar caer la frase' in text
        assert 'Negro #000' in text
        assert 'DUCK_TO_MUTE_HOLD_RESUME' in text
        assert 'HIDE_DURING_BLACK_HOLD' in text
        assert 'Silencio' in text
        b.close()


def test_caption_group_inspector_keeps_display_cues_and_hidden_block_is_dimmed():
    with sync_playwright() as pw:
        b=pw.chromium.launch(headless=True,executable_path='/usr/bin/chromium',args=['--no-sandbox']);page=b.new_page();page.set_content(page_html());page.evaluate("ABRXOS.state.selectedEventId='CAP1';ABRXOS.render()") ;page.wait_for_timeout(90)
        text=page.locator('#inspector').inner_text()
        assert '10 palabras' in text
        assert 'semántica' in text
        assert 'SEMÁNTICA' in text
        assert 'XR1' in text
        assert page.locator('[data-event-id="CAP1"]').evaluate("el=>el.classList.contains('r6-caption-hidden')") is True
        assert page.locator('[data-event-id="CAP1"]').count()==1
        b.close()


def test_piece_inspector_shows_edit_profile_and_checklist_edit_persists_to_document_and_local_storage():
    with sync_playwright() as pw:
        b=pw.chromium.launch(headless=True,executable_path='/usr/bin/chromium',args=['--no-sandbox']);page=b.new_page()
        # The harness blocks all navigation and gives about:blank an opaque origin.
        # Replace only the Storage surface so this test can verify that the R6 patch
        # persists through the same localStorage API used by the real standalone Lienzo.
        page.evaluate("""()=>{const m=new Map();Object.defineProperty(window,'localStorage',{configurable:true,value:{setItem:(k,v)=>m.set(k,String(v)),getItem:k=>m.has(k)?m.get(k):null,removeItem:k=>m.delete(k),clear:()=>m.clear()}})}""")
        page.set_content(page_html());page.evaluate("ABRXOS.state.selectedEventId=null;ABRXOS.render()") ;page.wait_for_timeout(100)
        text=page.locator('#inspector').inner_text()
        assert 'Cinematic Edit' in text and 'XR_FULL' in text
        select=page.locator('[data-r6-checklist="images"]')
        assert select.count()==1
        select.select_option('approved');page.wait_for_timeout(80)
        assert page.evaluate("ABRXOS.state.project.pieces[0].productionChecklist.images.status")=='approved'
        stored=page.evaluate("localStorage.getItem('abrxos:v3:P1:Demo')")
        assert stored and json.loads(stored)['pieces'][0]['productionChecklist']['images']['status']=='approved'
        b.close()

def test_sfx_inspector_shows_r6_library_trigger_purpose_placement_mix_and_status():
    html=page_html().replace("{'id':'CAP1'", "{'id':'SFX2','track':'sfx','type':'sfx','start':1,'end':1.2,'label':'Click R6','sfx':{'libraryId':'CLICK','variant':'soft','trigger':'aparece objeto','purpose':'confirmación','placement':'on reveal','mix':'-16 dB','status':'selected'}},{'id':'CAP1'")
    # The fixture string is generated from JSON, so append through JS instead of relying on textual Python repr.
    with sync_playwright() as pw:
        b=pw.chromium.launch(headless=True,executable_path='/usr/bin/chromium',args=['--no-sandbox']);page=b.new_page();page.set_content(page_html());page.evaluate("""()=>{ABRXOS.state.project.pieces[0].timeline.push({id:'SFX2',track:'sfx',type:'sfx',start:1,end:1.2,label:'Click R6',sfx:{libraryId:'SFX_CLICK',variant:'soft',trigger:'aparece objeto',purpose:'confirmación',placement:'on reveal',mix:'-16 dB',status:'selected'}});ABRXOS.state.selectedEventId='SFX2';ABRXOS.render()}""");page.wait_for_timeout(90)
        text=page.locator('#inspector').inner_text()
        for expected in ['SFX_CLICK','soft','aparece objeto','confirmación','on reveal','-16 dB','selected']:
            assert expected in text
        b.close()
