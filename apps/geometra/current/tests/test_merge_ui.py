from playwright.sync_api import sync_playwright
from tests.helpers import compile_test_html


def test_three_way_merge_combines_independent_changes_and_reports_real_conflict():
    html = compile_test_html('shadcn-studio')
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True, executable_path='/usr/bin/chromium', args=['--no-sandbox'])
        page = browser.new_page(viewport={'width': 1400, 'height': 900})
        page.set_content(html, wait_until='load')
        result = page.evaluate("""
        () => {
          const base = JSON.parse(JSON.stringify(ABRXOS.state.project));
          const local = JSON.parse(JSON.stringify(base));
          const remote = JSON.parse(JSON.stringify(base));
          local.pieces[0].title = 'LOCAL TITLE';
          local.pieces[0].notes = 'local note';
          remote.pieces[0].title = 'REMOTE TITLE';
          remote.pieces[0].workflowStatus = 'LISTO';
          const out = ABRXOS.mergeProjects(base, local, remote);
          return {
            title: out.merged.pieces[0].title,
            notes: out.merged.pieces[0].notes,
            workflow: out.merged.pieces[0].workflowStatus,
            conflicts: out.conflicts.map(x => x.pathLabel),
          };
        }
        """)
        assert result['notes'] == 'local note'
        assert result['workflow'] == 'LISTO'
        assert result['title'] == 'LOCAL TITLE'
        assert any(path.endswith('title') for path in result['conflicts'])
        browser.close()


def test_merge_button_opens_local_remote_base_workspace_and_applies_remote_choice(tmp_path):
    html = compile_test_html('joc-classic')
    remote_path = tmp_path / 'remote.json'
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True, executable_path='/usr/bin/chromium', args=['--no-sandbox'])
        page = browser.new_page(viewport={'width': 1400, 'height': 900})
        page.set_content(html, wait_until='load')
        original = page.evaluate("ABRXOS.state.project.pieces[0].title")
        page.evaluate("ABRXOS.state.project.pieces[0].title = ABRXOS.state.project.pieces[0].title + ' LOCAL'")
        remote = page.evaluate("JSON.parse(JSON.stringify(ABRXOS.baseDocument))")
        remote['pieces'][0]['title'] = original + ' REMOTE'
        remote_path.write_text(__import__('json').dumps(remote), encoding='utf-8')

        page.locator('[data-action="merge"]').click()
        assert page.locator('.merge-dialog').is_visible()
        page.locator('#merge-file').set_input_files(str(remote_path))
        page.wait_for_timeout(80)
        assert page.locator('.merge-conflict').count() >= 1
        title_conflict = page.locator('.merge-conflict').filter(has_text='.title').first
        title_conflict.locator('input[value="remote"]').check()
        page.locator('[data-action="apply-merge"]').click()
        page.wait_for_timeout(80)
        assert page.evaluate("ABRXOS.state.project.pieces[0].title") == original + ' REMOTE'
        browser.close()
