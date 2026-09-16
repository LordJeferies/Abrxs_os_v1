from playwright.sync_api import sync_playwright
from tests.helpers import compile_test_html


def make_page(p, html):
    browser=p.chromium.launch(headless=True, executable_path='/usr/bin/chromium', args=['--no-sandbox'])
    page=browser.new_page(viewport={'width':1440,'height':900})
    errors=[]; page.on('pageerror',lambda e:errors.append(str(e)))
    page.set_content(html,wait_until='load');page.wait_for_timeout(80)
    return browser,page,errors


def test_click_locked_aroll_selects_without_moving_or_prompting():
    with sync_playwright() as p:
        b,page,errors=make_page(p,compile_test_html());dialogs=[];page.on('dialog',lambda d:(dialogs.append(d.message),d.dismiss()))
        block=page.locator('[data-event-id="AR1"]');before=page.evaluate("ABRXOS.getEvent('AR1').start")
        block.click();page.wait_for_timeout(40);after=page.evaluate("ABRXOS.getEvent('AR1').start")
        assert before==after==0;assert dialogs==[];assert page.locator('#inspector').get_by_text('A-roll Hook').count()>=1;assert page.evaluate('ABRXOS.state.selectedEventId')=='AR1';assert not errors
        b.close()


def test_small_pointer_motion_is_still_selection_not_drag():
    with sync_playwright() as p:
        b,page,errors=make_page(p,compile_test_html());block=page.locator('[data-event-id="AR1"]');block.scroll_into_view_if_needed();box=block.bounding_box();assert box
        page.mouse.move(box['x']+20,box['y']+15);page.mouse.down();page.mouse.move(box['x']+23,box['y']+15);page.mouse.up();page.wait_for_timeout(60)
        assert page.evaluate("ABRXOS.getEvent('AR1').start")==0;assert page.evaluate('ABRXOS.state.selectedEventId')=='AR1';assert not errors
        b.close()


def test_drag_crossing_threshold_creates_override_and_undo_restores():
    with sync_playwright() as p:
        b,page,errors=make_page(p,compile_test_html());block=page.locator('[data-event-id="AR1"]');block.scroll_into_view_if_needed();box=block.bounding_box();assert box
        page.mouse.move(box['x']+25,box['y']+15);page.mouse.down();page.mouse.move(box['x']+90,box['y']+15,steps=5);page.mouse.up();page.wait_for_timeout(80)
        moved=page.evaluate("ABRXOS.getEvent('AR1')");assert moved['start']>0.5;assert moved['timingMode']=='manual_review';assert moved['editorialOverride']['originalStart']==0;assert moved['editorialOverride']['originalEnd']==12;assert page.evaluate("ABRXOS.getPiece('INTRO_1').sourceRanges[0].start")==100
        page.locator('[data-action="undo"]').click();page.wait_for_timeout(60);restored=page.evaluate("ABRXOS.getEvent('AR1')");assert restored['start']==0;assert restored['end']==12;assert not errors
        b.close()


def test_drag_xr_moves_follow_parent_children_but_not_source_ranges():
    with sync_playwright() as p:
        b,page,errors=make_page(p,compile_test_html());block=page.locator('[data-event-id="XR1"]');block.scroll_into_view_if_needed();box=block.bounding_box();assert box
        before_xr=page.evaluate("ABRXOS.getEvent('XR1').start");before_img=page.evaluate("ABRXOS.getEvent('IMG1').start")
        page.mouse.move(box['x']+25,box['y']+15);page.mouse.down();page.mouse.move(box['x']+61,box['y']+15,steps=4);page.mouse.up();page.wait_for_timeout(60)
        after_xr=page.evaluate("ABRXOS.getEvent('XR1').start");after_img=page.evaluate("ABRXOS.getEvent('IMG1').start")
        delta=after_xr-before_xr
        assert delta>1
        assert abs((after_img-before_img)-delta)<0.02
        assert page.evaluate("ABRXOS.getPiece('INTRO_1').sourceRanges[0].start")==100
        assert not errors
        b.close()


def test_locked_source_drag_records_cut_override_for_future_cutter_without_touching_source_truth():
    with sync_playwright() as p:
        b,page,errors=make_page(p,compile_test_html());block=page.locator('[data-event-id="AR1"]');block.scroll_into_view_if_needed();box=block.bounding_box();assert box
        page.mouse.move(box['x']+25,box['y']+15);page.mouse.down();page.mouse.move(box['x']+65,box['y']+15,steps=4);page.mouse.up();page.wait_for_timeout(70)
        piece=page.evaluate("ABRXOS.getPiece('INTRO_1')")
        overrides=piece.get('cutOverrides') or []
        assert len(overrides)==1
        assert overrides[0]['eventId']=='AR1'
        assert overrides[0]['status']=='needs_review'
        assert overrides[0]['originalTimeline']=={'start':0,'end':12}
        assert overrides[0]['editorialTimeline']['start']>0
        assert piece['sourceRanges'][0]['start']==100 and piece['sourceRanges'][0]['end']==112
        b.close()
