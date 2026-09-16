from playwright.sync_api import sync_playwright
from tests.helpers import compile_test_html


def test_custom_xr_definition_lives_in_document_and_catalog_lookup_uses_it():
    html=compile_test_html()
    with sync_playwright() as p:
        b=p.chromium.launch(headless=True,executable_path='/usr/bin/chromium',args=['--no-sandbox'])
        page=b.new_page();page.set_content(html,wait_until='load');page.wait_for_timeout(60)
        result=page.evaluate("""()=>{ABRXOS.createXRDefinition({id:'XR77',name:'Single Photo Hold',kind:'image_hold',defaultAssets:1,description:'Una foto sostenida'});return {defs:ABRXOS.state.project.extensions.xrDefinitions,lookup:ABRXOS.catalog('xr','XR77')}}""")
        assert any(x['id']=='XR77' for x in result['defs'])
        assert result['lookup']['name']=='Single Photo Hold'
        assert not result['lookup'].get('fallback',False)
        b.close()


def test_add_unknown_xr_from_ui_registers_definition_before_event_creation():
    html=compile_test_html('joc-classic')
    with sync_playwright() as p:
        b=p.chromium.launch(headless=True,executable_path='/usr/bin/chromium',args=['--no-sandbox'])
        page=b.new_page(viewport={'width':1400,'height':900});page.set_content(html,wait_until='load');page.wait_for_timeout(80)
        answers=iter(['XR77','Mapa progresivo','2','8'])
        page.on('dialog',lambda d:d.accept(next(answers)))
        page.locator('[data-action="add-xr"]').click();page.wait_for_timeout(100)
        result=page.evaluate("""() => ({
          def: ABRXOS.catalog('xr','XR77'),
          ext: ABRXOS.state.project.extensions.xrDefinitions,
          event: ABRXOS.state.project.pieces[0].timeline.find(x => x.definitionId === 'XR77')
        })""")
        assert result['def']['name']=='Mapa progresivo'
        assert result['def']['fallback'] is not True
        assert any(x['id']=='XR77' for x in result['ext'])
        assert result['event']['start']==2 and result['event']['end']==8
        b.close()


def test_add_unknown_sfx_from_ui_registers_reusable_definition():
    html=compile_test_html('shadcn-studio')
    with sync_playwright() as p:
        b=p.chromium.launch(headless=True,executable_path='/usr/bin/chromium',args=['--no-sandbox'])
        page=b.new_page(viewport={'width':1400,'height':900});page.set_content(html,wait_until='load');page.wait_for_timeout(80)
        answers=iter(['SFX_CUSTOM_BELL','Campana suave','3'])
        page.on('dialog',lambda d:d.accept(next(answers)))
        page.locator('[data-action="add-sfx"]').click();page.wait_for_timeout(100)
        result=page.evaluate("""() => ({
          def: ABRXOS.catalog('sfx','SFX_CUSTOM_BELL'),
          ext: ABRXOS.state.project.extensions.sfxDefinitions,
          event: ABRXOS.state.project.pieces[0].timeline.find(x => x.definitionId === 'SFX_CUSTOM_BELL')
        })""")
        assert result['def']['name']=='Campana suave'
        assert result['def']['fallback'] is False
        assert any(x['id']=='SFX_CUSTOM_BELL' for x in result['ext'])
        assert result['event']['start']==3
        b.close()
