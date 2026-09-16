from playwright.sync_api import sync_playwright
from tests.helpers import compile_test_html


def test_carousel_opens_static_workspace_not_video_timeline():
    html=compile_test_html('shadcn-studio')
    with sync_playwright() as p:
        b=p.chromium.launch(headless=True,executable_path='/usr/bin/chromium',args=['--no-sandbox'])
        page=b.new_page(viewport={'width':1400,'height':900});page.set_content(html,wait_until='load');page.wait_for_timeout(80)
        page.locator('[data-piece-id="C1"]').click();page.wait_for_timeout(60)
        assert page.locator('.carousel-workspace').is_visible()
        assert page.locator('.carousel-slide-card').count()==2
        assert page.locator('.timeline-grid').count()==0
        b.close()


def test_calendar_has_unscheduled_sidebar_and_drop_both_directions():
    html=compile_test_html()
    with sync_playwright() as p:
        b=p.chromium.launch(headless=True,executable_path='/usr/bin/chromium',args=['--no-sandbox'])
        page=b.new_page(viewport={'width':1400,'height':900});page.set_content(html,wait_until='load');page.wait_for_timeout(80)
        page.locator('[data-view="calendar"]').click();page.wait_for_timeout(50)
        assert page.locator('#unscheduled-list [data-calendar-piece]').count()==2
        # Use runtime API for the same mutation that DnD commits, then assert projections.
        page.evaluate("ABRXOS.setScheduleDate('INTRO_1','2026-09-18')");page.wait_for_timeout(40)
        assert page.locator('[data-date="2026-09-18"] [data-calendar-piece="INTRO_1"]').count()==1
        assert page.locator('#unscheduled-list [data-calendar-piece="INTRO_1"]').count()==0
        page.evaluate("ABRXOS.setScheduleDate('INTRO_1','')");page.wait_for_timeout(40)
        assert page.locator('#unscheduled-list [data-calendar-piece="INTRO_1"]').count()==1
        b.close()


def test_carousel_slide_text_visual_and_prompt_are_directly_editable():
    html=compile_test_html('shadcn-studio')
    with sync_playwright() as p:
        b=p.chromium.launch(headless=True,executable_path='/usr/bin/chromium',args=['--no-sandbox'])
        page=b.new_page(viewport={'width':1400,'height':900});page.set_content(html,wait_until='load');page.wait_for_timeout(80)
        page.locator('[data-piece-id="C1"]').click();page.wait_for_timeout(60)
        page.locator('#static-headline-edit').fill('Nuevo titular')
        page.locator('#static-body-edit').fill('Nuevo cuerpo')
        page.locator('#static-visual-edit').fill('Nueva visual')
        page.locator('#static-prompt-edit').fill('Nuevo prompt')
        page.locator('[data-action="save-static-details"]').click();page.wait_for_timeout(60)
        result=page.evaluate("""() => {const x=ABRXOS.getPiece('C1').staticProduction.items[0];return {headline:x.headline,body:x.body,visual:x.visual.description,prompt:x.visual.prompt}}""")
        assert result=={'headline':'Nuevo titular','body':'Nuevo cuerpo','visual':'Nueva visual','prompt':'Nuevo prompt'}
        assert 'Nuevo titular' in page.locator('.preview-card').inner_text()
        b.close()
