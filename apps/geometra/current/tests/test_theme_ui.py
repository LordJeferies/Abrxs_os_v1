from pathlib import Path
from playwright.sync_api import sync_playwright
from geometra.registry import RendererRegistry, CatalogRegistry
from geometra.compiler import compile_lienzo
from tests.helpers import synthetic_project

ROOT=Path(__file__).resolve().parents[1]


def test_shadcn_light_theme_sets_document_theme_and_light_background():
    html=compile_lienzo(synthetic_project(),'shadcn-studio',[],'Light Demo','light',RendererRegistry(ROOT/'renderers'),CatalogRegistry(ROOT/'catalogs'),ROOT)
    with sync_playwright() as p:
        b=p.chromium.launch(headless=True,executable_path='/usr/bin/chromium',args=['--no-sandbox'])
        page=b.new_page();page.set_content(html,wait_until='load');page.wait_for_timeout(60)
        assert page.evaluate("document.documentElement.dataset.theme")=='light'
        bg=page.evaluate("getComputedStyle(document.body).backgroundColor")
        assert bg in {'rgb(250, 250, 250)','rgb(255, 255, 255)','rgb(248, 250, 252)'}
        b.close()
