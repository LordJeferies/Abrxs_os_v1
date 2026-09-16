# ABRXOS Content Builder V1 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a standalone/local Mac Content Builder that selects the correct ABRXOS R6 prompt/template/canon for a requested content workflow and exports a deterministic AI upload package.

**Architecture:** Python standard-library server plus self-contained HTML frontend. A scenario compiler maps input mode/type/stage/profile to a pinned R6 prompt and ficha template. Server mode stores drafts/libraries and exports folder+ZIP; standalone HTML can still compose requests and download JSON/TXT.

**Tech Stack:** Python 3 stdlib, HTML5, CSS, vanilla JavaScript, unittest, Node syntax check, optional Playwright smoke.

**Spec:** `docs/superpowers/specs/2026-09-16-content-builder-v1-design.md`

## Global Constraints

- No integrated AI/API.
- JSON is canonical output expected back for Geometra; TXT is companion only.
- Fixed-plan mode must preserve editorial order and do-not-change rules.
- R6 XR/CINE/Motion/SFX/Music/Caption canon is pinned into each package via snapshot/context.
- No invented timestamps.
- Video and static forms differ; static content never pretends to use audiovisual timeline controls.
- Each app is independently installable.

---

### Task 1: Scenario compiler and persistence
**Files:** Create `ABRXOS_CONTENT_BUILDER_V1/content_engine.py`; Test `tests/test_content_engine.py`.
**Interfaces:** `ContentStore`, `select_case`, `resolve_prompt_template`, `build_content_ai_package`, `safe_slug`.
- [ ] Write failing tests covering all 14 scenario routes, video/static target template resolution, unknown-field preservation, package manifest.
- [ ] Run RED.
- [ ] Implement minimal engine.
- [ ] Run PASS.

### Task 2: Local server APIs
**Files:** Create `app.py`; Test `tests/test_content_server.py`.
**Interfaces:** `/api/health`, `/api/drafts`, `/api/draft/save`, `/api/library/brand`, `/api/library/project`, `/api/export`, `/api/cases`.
- [ ] Write failing API tests.
- [ ] Run RED.
- [ ] Implement API/static server.
- [ ] Run PASS.

### Task 3: Content Builder HTML
**Files:** Create `ABRXOS_CONTENT_BUILDER_V1.html`, `web/index.html`; Test `tests/test_content_html.py`.
- [ ] Write failing structural tests for type/stage/profile/input-mode selectors, dynamic XR rules, transcript/plan/current-ficha inputs, project/brand import, package preview.
- [ ] Run RED.
- [ ] Implement UI and standalone fallback.
- [ ] Run tests + JS syntax.

### Task 4: R6 resource snapshot
**Files:** Create `resources/canon_r6/` with prompts/templates/libraries required by scenario compiler.
- [ ] Write resource completeness test.
- [ ] Run RED.
- [ ] Copy exact pinned R6 files from current canon.
- [ ] Run PASS.

### Task 5: macOS packaging/install
**Files:** `INSTALAR_ABRXOS_CONTENT_BUILDER_V1.command`, `COMANDOS_TERMINAL.txt`, `README.md`, `VERSION.json`.
- [ ] Write installer static assertions.
- [ ] Implement Python detection, install folder, Desktop `.app`, logs, fallback launcher.
- [ ] Run shell syntax/static checks.

### Task 6: Browser smoke and release ZIP
- [ ] Run all Python tests.
- [ ] Run JS syntax check.
- [ ] Browser smoke: fixed intro plan XR_FULL, transcript-only vertical Beta, carousel Alpha, all-project package; zero page errors.
- [ ] Build ZIP and run `unzip -t`.
