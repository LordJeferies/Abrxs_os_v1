from pathlib import Path
from geometra.registry import RendererRegistry, CatalogRegistry

ROOT = Path(__file__).resolve().parents[1]


def test_renderer_registry_discovers_both_builtin_renderers():
    reg = RendererRegistry(ROOT / 'renderers')
    ids = {x['rendererId'] for x in reg.list()}
    assert {'joc-classic', 'shadcn-studio'} <= ids
    assert reg.get('joc-classic')['capabilities']['timeline'] is True
    assert reg.get('shadcn-studio')['capabilities']['calendar'] is True


def test_catalog_registry_returns_builtin_and_generic_unknown():
    cat = CatalogRegistry(ROOT / 'catalogs')
    xr6 = cat.get('xr', 'XR06')
    assert xr6['id'] == 'XR06'
    assert xr6['name']
    unknown = cat.get('xr', 'XR77')
    assert unknown['id'] == 'XR77'
    assert unknown['fallback'] is True
    assert unknown['kind'] == 'custom'


def test_sfx_catalog_contains_reusable_presets():
    cat = CatalogRegistry(ROOT / 'catalogs')
    rows = cat.list('sfx')
    assert any(x['id'] == 'SFX_HIT_SOFT_01' for x in rows)
    assert any(x['id'] == 'SFX_TICK_SOFT_01' for x in rows)
