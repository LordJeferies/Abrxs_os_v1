from playwright.sync_api import sync_playwright
from tests.helpers import compile_test_html

VIEWPORTS=[
    {'width':1440,'height':900},
    {'width':390,'height':844},
    {'width':844,'height':390},
    {'width':820,'height':1180},
    {'width':1180,'height':820},
]


def test_built_in_renderers_boot_without_page_errors_across_reference_viewports():
    with sync_playwright() as p:
        browser=p.chromium.launch(headless=True,executable_path='/usr/bin/chromium',args=['--no-sandbox'])
        for renderer in ('joc-classic','shadcn-studio'):
            html=compile_test_html(renderer)
            for viewport in VIEWPORTS:
                page=browser.new_page(viewport=viewport);errors=[];page.on('pageerror',lambda e,errs=errors:errs.append(str(e)))
                page.set_content(html,wait_until='load');page.wait_for_timeout(40)
                assert page.locator('[data-event-id="AR1"]').count()==1
                page.locator('[data-event-id="AR1"]').click();page.wait_for_timeout(20)
                assert page.evaluate("ABRXOS.state.selectedEventId")=='AR1'
                assert not errors, (renderer,viewport,errors)
                page.close()
        browser.close()
