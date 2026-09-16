from playwright.sync_api import sync_playwright
from tests.helpers import compile_test_html


def test_xr_selection_shows_internal_states_assets_and_copy_controls():
    html=compile_test_html('shadcn-studio')
    with sync_playwright() as p:
        b=p.chromium.launch(headless=True,executable_path='/usr/bin/chromium',args=['--no-sandbox'])
        page=b.new_page(viewport={'width':1400,'height':900}); errors=[]; page.on('pageerror',lambda e:errors.append(str(e)))
        page.set_content(html,wait_until='load'); page.wait_for_timeout(100)
        page.locator('[data-event-id="XR1"]').click(); page.wait_for_timeout(60)
        txt=page.locator('#inspector').inner_text()
        assert 'Explicar el sistema' in txt
        assert 'S01' in txt and 'Entrada del sistema' in txt
        assert 'A01' in txt and 'Libreta inicial' in txt
        assert 'Prompt libreta inicial' in txt
        assert page.locator('#inspector [data-copy]').count() >= 2
        assert not errors
        b.close()


def test_unknown_custom_xr_uses_fallback_instead_of_breaking():
    html=compile_test_html()
    with sync_playwright() as p:
        b=p.chromium.launch(headless=True,executable_path='/usr/bin/chromium',args=['--no-sandbox'])
        page=b.new_page(viewport={'width':1400,'height':900}); page.set_content(html,wait_until='load')
        page.evaluate("""()=>{const p=ABRXOS.getPiece('INTRO_1');p.timeline.push({id:'XR77_1',track:'xr',type:'xr',definitionId:'XR77',xrFamily:'XR77',label:'Nuevo XR',start:8,end:10,function:'Custom',states:[],assets:[]});ABRXOS.render();}""")
        page.locator('[data-event-id="XR77_1"]').click();page.wait_for_timeout(40)
        txt=page.locator('#inspector').inner_text()
        assert 'Nuevo XR' in txt
        assert 'XR77' in txt
        assert 'Custom' in txt
        assert 'JSON avanzado' in txt
        b.close()


def test_xr_inspector_edits_function_and_asset_prompt_without_raw_json():
    html=compile_test_html('shadcn-studio')
    with sync_playwright() as p:
        b=p.chromium.launch(headless=True,executable_path='/usr/bin/chromium',args=['--no-sandbox'])
        page=b.new_page(viewport={'width':1400,'height':900});page.set_content(html,wait_until='load');page.wait_for_timeout(80)
        page.locator('[data-event-id="XR1"]').click();page.wait_for_timeout(50)
        page.locator('#xr-function-edit').fill('Nueva función narrativa')
        page.locator('[data-asset-prompt="A01"]').fill('Prompt modificado')
        page.locator('[data-action="save-event-details"]').click();page.wait_for_timeout(70)
        result=page.evaluate("""() => {const e=ABRXOS.getEvent('XR1');return {fn:e.function,prompt:e.assets.find(a=>a.assetId==='A01').prompt}}""")
        assert result=={'fn':'Nueva función narrativa','prompt':'Prompt modificado'}
        b.close()


def test_editing_xr_asset_prompt_updates_linked_image_projection():
    html=compile_test_html('joc-classic')
    with sync_playwright() as p:
        b=p.chromium.launch(headless=True,executable_path='/usr/bin/chromium',args=['--no-sandbox'])
        page=b.new_page(viewport={'width':1400,'height':900});page.set_content(html,wait_until='load');page.wait_for_timeout(80)
        page.locator('[data-event-id="XR1"]').click();page.locator('[data-asset-prompt="A01"]').fill('Prompt sincronizado');page.locator('[data-action="save-event-details"]').click();page.wait_for_timeout(50)
        page.locator('[data-event-id="IMG1"]').click();page.wait_for_timeout(50)
        assert 'Prompt sincronizado' in page.locator('#inspector').inner_text()
        assert page.evaluate("ABRXOS.getEvent('IMG1').asset.prompt")=='Prompt sincronizado'
        b.close()


def test_image_and_sfx_inspectors_offer_direct_edit_controls():
    html=compile_test_html('shadcn-studio')
    with sync_playwright() as p:
        b=p.chromium.launch(headless=True,executable_path='/usr/bin/chromium',args=['--no-sandbox'])
        page=b.new_page(viewport={'width':1400,'height':900});page.set_content(html,wait_until='load');page.wait_for_timeout(80)
        page.locator('[data-event-id="IMG1"]').click();page.wait_for_timeout(40)
        page.locator('#image-description-edit').fill('Nueva descripción imagen')
        page.locator('#image-prompt-edit').fill('Nuevo prompt imagen')
        page.locator('[data-action="save-event-details"]').click();page.wait_for_timeout(40)
        image=page.evaluate("ABRXOS.getEvent('IMG1').asset")
        assert image['description']=='Nueva descripción imagen' and image['prompt']=='Nuevo prompt imagen'

        page.locator('[data-event-id="SFX1"]').click();page.wait_for_timeout(40)
        page.locator('#sfx-search-edit').fill('nuevo sonido suave')
        page.locator('[data-action="save-event-details"]').click();page.wait_for_timeout(40)
        assert page.evaluate("ABRXOS.getEvent('SFX1').sfx.search")=='nuevo sonido suave'
        b.close()


def test_caption_inspector_edits_text_and_highlight_word_directly():
    html=compile_test_html('shadcn-studio')
    with sync_playwright() as p:
        b=p.chromium.launch(headless=True,executable_path='/usr/bin/chromium',args=['--no-sandbox'])
        page=b.new_page(viewport={'width':1400,'height':900});page.set_content(html,wait_until='load');page.wait_for_timeout(80)
        page.locator('[data-event-id="CAP1"]').click();page.wait_for_timeout(40)
        page.locator('#caption-text-edit').fill('Nueva frase corta')
        page.locator('#caption-highlight-edit').fill('frase')
        page.locator('[data-action="save-event-details"]').click();page.wait_for_timeout(40)
        result=page.evaluate("""() => {const e=ABRXOS.getEvent('CAP1');return {text:e.text,highlight:e.highlightWord,status:e.highlightStatus}}""")
        assert result=={'text':'Nueva frase corta','highlight':'frase','status':'confirmed'}
        b.close()
