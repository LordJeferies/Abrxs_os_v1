from contextlib import contextmanager
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
PATCH_JS = (ROOT / 'PATCH_GEOMETRA' / 'shared' / 'r6_patch.js').read_text(encoding='utf-8')


@contextmanager
def boot(piece, event_id=None, validation=None):
    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=True, executable_path='/usr/bin/chromium', args=['--no-sandbox','--disable-dev-shm-usage'])
        try:
            page = browser.new_page(viewport={'width': 1200, 'height': 800})
            page.set_content('<html><head></head><body><div class="pieceactions"></div><div id="inspector"></div></body></html>')
            page.evaluate("""({piece,eventId,validation})=>{
              window.ABRXOS={
                state:{project:{projectId:'P',canvas:{title:'T'},pieces:[piece],r6Validation:validation},selectedPieceId:piece.canonicalId,selectedEventId:eventId},
                getPiece:id=>window.ABRXOS.state.project.pieces.find(x=>x.canonicalId===id),
                getEvent:id=>window.ABRXOS.state.project.pieces[0].timeline.find(x=>x.id===id),
                render:()=>{}
              };
            }""", {'piece': piece, 'eventId': event_id, 'validation': validation or {'pieces': []}})
            page.add_script_tag(content=PATCH_JS)
            page.wait_for_timeout(60)
            yield browser, page
        finally:
            browser.close()


def base_piece():
    return {
        'canonicalId': 'INTRO1', 'type': 'intro', 'title': 'Intro',
        'editProfile': {'code': 'XR_FULL'},
        'sourceAlignment': [
            {'id':'P01','desiredText':'Frase','status':'cue_based','microtrim':True,'startAnchor':'frase','endAnchor':'final','parentStartTc':'00:01:00.000','parentEndTc':'00:01:05.000'}
        ],
        'parts': [
            {'partId':'VO01','kind':'voiceover','role':'VOICEOVER','text':'Pregunta narrador','placement':{'after':'P01','before':'P02'},'timingStatus':'editorial_planned'}
        ],
        'timeline': [
            {'id':'VO01_VO','track':'vo','type':'vo','label':'NARRADOR · VO01','start':5,'end':10,'partId':'VO01','text':'Pregunta narrador','recordingStatus':'pending','timingStatus':'editorial_planned'}
        ],
        'productionChecklist': {}
    }


def validation():
    return {'pieces':[{'id':'INTRO1','alphaReady':False,'cutterReady':False,'projectionReady':False,'projectionMissing':['XR/A01: falta proyección T3 image'],'progressPercent':10,'missing':['sourceRanges faltante'],'sourceAlignment':{'count':1,'locatedCount':1,'microtrimRequiredCount':1,'unresolvedCount':0},'voiceovers':{'count':1,'placementReady':True}}]}


def test_piece_inspector_shows_source_alignment_and_projection_ready():
    with boot(base_piece(), validation=validation()) as (_, page):
        text=page.locator('#inspector').inner_text()
        assert 'SOURCE ALIGNMENT' in text
        assert 'MICROTRIM' in text
        assert 'Projection REVIEW' in text
        assert 'falta proyección T3 image' in text
        for key in ('sourceAlignment','microtrim','voRecording'):
            assert page.locator(f'[data-r6-checklist="{key}"]').count()==1


def test_vo_event_inspector_shows_placement_and_recording_status():
    with boot(base_piece(), event_id='VO01_VO', validation=validation()) as (_, page):
        text=page.locator('#inspector').inner_text()
        assert 'VOICEOVER ADDED' in text
        assert 'after' in text and 'P01' in text
        assert 'before' in text and 'P02' in text
        assert 'pending' in text
