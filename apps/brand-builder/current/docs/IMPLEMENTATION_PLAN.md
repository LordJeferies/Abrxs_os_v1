# ABRXOS X Brand Builder V1 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a standalone/local Mac Brand Builder that preserves raw brand information, exposes Branding Method 5-driver summary plus optional 25 tools, edits an R6 Brand Adapter, and exports deterministic AI packages.

**Architecture:** Python standard-library server exposes JSON APIs and static UI. Frontend is a single self-contained HTML file with localStorage fallback; server mode adds durable JSON persistence, reference uploads, folder/ZIP package export, and library management. Canon resources are bundled read-only.

**Tech Stack:** Python 3 stdlib, HTML5, CSS, vanilla JavaScript, unittest, Node syntax check, optional Playwright smoke via system Chromium.

**Spec:** `docs/superpowers/specs/2026-09-16-brand-builder-v1-design.md`

## Global Constraints

- No integrated AI/API.
- No cloud/Firebase/Tauri.
- Raw user input must be preserved exactly.
- Branding Method strategy and Brand Adapter production rules remain separate.
- Default Method UI is 5-driver summary; 25 tools are optional expansion.
- Unknown imported JSON fields survive round trips.
- Exports are version-pinned and include SHA256 manifest entries.
- macOS installer creates a `.app` launcher but requires only an existing Python 3.

---

### Task 1: Package engine and persistence
**Files:** Create `ABRXOS_X_BRAND_BUILDER_V1/brand_engine.py`; Test `ABRXOS_X_BRAND_BUILDER_V1/tests/test_brand_engine.py`.
**Interfaces:** `BrandStore`, `safe_slug`, `deep_merge`, `build_brand_ai_package`.
- [ ] Write failing tests for slug safety, unknown-field merge, save/load, deterministic package manifest.
- [ ] Run tests and confirm missing-module/function failures.
- [ ] Implement minimal engine.
- [ ] Run tests and confirm PASS.

### Task 2: Local server APIs
**Files:** Create `ABRXOS_X_BRAND_BUILDER_V1/app.py`; Test `tests/test_brand_server.py`.
**Interfaces:** `/api/health`, `/api/brands`, `/api/brand/save`, `/api/brand/delete`, `/api/export`, `/api/reference/upload`.
- [ ] Write failing HTTP/API tests using temporary data/export roots.
- [ ] Run tests and confirm RED.
- [ ] Implement server routes and static serving.
- [ ] Run tests and confirm PASS.

### Task 3: Brand Builder HTML
**Files:** Create `ABRXOS_X_BRAND_BUILDER_V1/ABRXOS_X_BRAND_BUILDER_V1.html` and mirrored `web/index.html`; Test `tests/test_brand_html.py`.
**Interfaces:** server APIs above; standalone localStorage fallback.
- [ ] Write structural tests for required panels, method tool registry, form/raw modes, Brand Adapter editor, export UI.
- [ ] Run tests and confirm RED.
- [ ] Implement complete HTML/CSS/JS UI.
- [ ] Run structural tests and Node syntax extraction check.

### Task 4: Canon/resources and Method registry
**Files:** Create `resources/` subset, `resources/branding_method_registry.json`, `resources/BRANDING_METHOD_SOURCE_NOTE.txt`.
- [ ] Write failing test that required R6 resources and 5x5 method registry exist.
- [ ] Run RED.
- [ ] Copy/pin R6 templates and create paraphrased method registry.
- [ ] Run PASS.

### Task 5: macOS packaging/install
**Files:** Create `INSTALAR_ABRXOS_X_BRAND_BUILDER_V1.command`, `COMANDOS_TERMINAL.txt`, `README.md`, `VERSION.json`.
- [ ] Write static installer assertions first.
- [ ] Implement installer with Python detection, copy to `~/Applications/ABRXOS/`, Desktop `.app` via osacompile, logs, fallback `.command` launcher.
- [ ] Run static/shell syntax checks.

### Task 6: Browser smoke and release ZIP
- [ ] Run all Python tests.
- [ ] Run `node --check` on extracted inline JavaScript.
- [ ] Run headless Chromium smoke if available: create brand, switch Method summary/tools, edit raw input, build preview, ensure zero page errors.
- [ ] Build ZIP and run `unzip -t`.
