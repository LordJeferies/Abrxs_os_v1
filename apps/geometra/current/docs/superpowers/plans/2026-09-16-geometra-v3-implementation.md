# ABRXOS Geometra V3 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [x]`) syntax for tracking.

**Goal:** Build Geometra V3 as a canonical kernel plus interchangeable standalone Lienzo renderer packs, with a safe timeline interaction model and catalog-driven XR/SFX.

**Architecture:** Python standard-library local server and compiler own import, normalization, persistence and renderer registry. Standalone exported HTML embeds one canonical document plus a shared JavaScript runtime and renderer-specific template/styles/adapter. Renderers never create their own domain model.

**Tech Stack:** Python 3.11+, HTML/CSS/vanilla JS, IndexedDB, pytest, Playwright/Chromium for UI regression tests.

**Spec:** `docs/superpowers/specs/2026-09-16-geometra-v3-design.md`

## Global Constraints

- Canonical schema: `abrxos.document.v3`.
- Mouse/pen drag threshold: 6 px; touch: 10 px.
- `sourceRanges` may not be changed by ordinary timeline drag/trim.
- Unknown fields and unknown XR/SFX definitions must survive roundtrip.
- No external CDN/runtime dependency in exported Lienzos.
- VideoFlow is out of V3.0 scope.

---

### Task 1: Canonical importer and migrations

**Files:**
- Create: `geometra/core.py`
- Test: `tests/test_core.py`

**Interfaces:**
- Produces: `import_text(name: str, text: str) -> dict`, `normalize_project(data: dict, source_name: str) -> dict`, `piece_id(piece: dict) -> str`.

- [x] Write tests for `app-data`, `seed`, JSON and V2/V2.1 migration.
- [x] Run tests and confirm failures because `geometra.core` does not exist.
- [x] Implement minimal importer/normalizer preserving unknown source payload and stable IDs.
- [x] Run tests to green.

### Task 2: Renderer and catalog registries

**Files:**
- Create: `geometra/registry.py`
- Create: `catalogs/xr_catalog.json`
- Create: `catalogs/sfx_catalog.json`
- Create: `catalogs/motion_catalog.json`
- Create: `catalogs/caption_styles.json`
- Create: `renderers/joc-classic/manifest.json`
- Create: `renderers/shadcn-studio/manifest.json`
- Test: `tests/test_registry.py`

**Interfaces:**
- Produces: `RendererRegistry`, `CatalogRegistry`.

- [x] Write failing tests for renderer discovery, capability lookup and unknown catalog fallback.
- [x] Verify red.
- [x] Implement registries and built-in catalogs.
- [x] Verify green.

### Task 3: Standalone renderer compiler

**Files:**
- Create: `geometra/compiler.py`
- Create: `shared/lienzo_core.js`
- Create: renderer templates/styles/adapters under `renderers/*`.
- Test: `tests/test_compile.py`

**Interfaces:**
- Consumes: canonical project and renderer ID.
- Produces: `compile_lienzo(project, renderer_id, piece_ids, title, theme) -> str`.

- [x] Write failing tests requiring one canonical project to compile through both renderers and retain identical `app-data` content.
- [x] Verify red.
- [x] Implement compiler token replacement and standalone assets.
- [x] Verify green.

### Task 4: Safe timeline interaction runtime

**Files:**
- Modify: `shared/lienzo_core.js`
- Test: `tests/test_timeline_ui.py`

**Interfaces:**
- Browser behavior: click selects; drag threshold enters gesture; commit/rollback/history.

- [x] Write Playwright regression test: click A-roll -> inspector changes, event timing unchanged, no confirm dialog.
- [x] Verify red.
- [x] Implement pointer state machine.
- [x] Verify green.
- [x] Add failing drag/undo test.
- [x] Implement editorial override + one-history-entry commit.
- [x] Verify green.

### Task 5: Inspector, XR/SFX catalogs and unknown fallback

**Files:**
- Modify: `shared/lienzo_core.js`
- Test: `tests/test_inspector_ui.py`

**Interfaces:**
- Selection exposes nested states/assets/motion/SFX; custom definitions live in document extensions.

- [x] Write failing XR selection/copy/edit/fallback tests.
- [x] Verify red.
- [x] Implement catalog-aware and generic inspectors plus `+ XR`/`+ SFX` creation.
- [x] Verify green.

### Task 6: Static/Carousel workspace and calendar

**Files:**
- Modify: `shared/lienzo_core.js`
- Modify renderer styles/adapters.
- Test: `tests/test_workspace_ui.py`

**Interfaces:**
- Carousel renders slide workspace; calendar has month + unscheduled sidebar.

- [x] Write failing carousel and calendar drag/drop tests.
- [x] Verify red.
- [x] Implement static workspace and dedicated calendar.
- [x] Verify green.

### Task 7: Local Geometra V3 application

**Files:**
- Create: `geometra/library.py`
- Create: `geometra/server.py`
- Create: `app/index.html`, `app/app.js`, `app/styles.css`
- Test: `tests/test_server.py`, `tests/test_geometra_ui.py`

**Interfaces:**
- Browser file import -> library; Create Lienzo -> renderer/theme/piece selection -> downloadable HTML.

- [x] Write failing API/UI tests.
- [x] Verify red.
- [x] Implement library/server/UI.
- [x] Verify green.

### Task 8: Installer, docs, examples and complete regression

**Files:**
- Create: `INSTALAR_ABRXOS_GEOMETRA_V3.command`
- Create: `RUN_GEOMETRA_V3.command`
- Create: `README_START_HERE.md`
- Create: `VERSION.json`
- Create: `TEST_REPORT.md`
- Create: `examples/*.html`

- [x] Build JOC55 examples for both renderers.
- [x] Run Python unit suite.
- [x] Run JavaScript syntax checks.
- [x] Run Playwright desktop/mobile smoke tests.
- [x] Run import -> compile -> reimport regression.
- [x] Zip package and verify archive integrity.
