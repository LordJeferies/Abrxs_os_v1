# ABRXOS Geometra V3.1 R6 Patch Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [x]`) syntax for tracking.

**Goal:** Deliver a reversible patch that upgrades an existing ABRXOS Geometra V3 installation to R6-aware import, validation, Kanban and Lienzo inspection while preserving legacy documents, the installed `.app`, user data and Cutter source truth.

**Architecture:** Keep V3 Kernel/runtime intact and add R6 through focused modules plus marker-based hooks. Python owns validation/import compatibility; `app/r6_patch.js` enhances Geometra UI; `shared/r6_patch.js` enhances compiled Lienzos against the same canonical project state. The installer backs up only touched code and rolls back automatically on verification failure.

**Tech Stack:** Python 3 standard library, vanilla JS/HTML/CSS, pytest, Playwright/Chromium when available, zsh launcher scripts on macOS.

**Spec:** `docs/superpowers/specs/2026-09-16-geometra-v3-1-r6-patch-design.md`

## Global Constraints

- Never modify `~/ABRXOS_GEOMETRA_DATA` from apply/revert scripts.
- Support Geometra Kernel 3.0.x only; fail cleanly on unknown major versions.
- Preserve legacy XR00–XR09 without automatic family remapping.
- R6 CINE uses existing T1–T9 tracks; no T10.
- `sourceRanges` is never rewritten by R6 UI enhancements.
- Patch apply must be idempotent.
- Patch failure must automatically restore backed-up code.
- Existing `.app` launcher remains unchanged.

---

### Task 1: R6 validator and library module

**Files:**
- Create: `payload/geometra/r6.py`
- Create: `payload/r6/*.json`
- Test: `tests/test_r6_validator.py`

**Interfaces:**
- Produces `load_r6_libraries(root: Path) -> dict`.
- Produces `validate_r6_project(project: dict, libraries: dict | None = None) -> dict`.
- Produces `ensure_production_checklist(piece: dict) -> dict`.

- [x] Write tests using official R6 intro/vertical/carousel fixtures for family, CINE, captions, edit-profile, Alpha/Cutter readiness and legacy compatibility.
- [x] Run tests and verify RED because `geometra.r6` does not exist.
- [x] Implement validator and library loader.
- [x] Run tests to GREEN.

### Task 2: Safe patch engine and idempotent hooks

**Files:**
- Create: `tools/apply_patch.py`
- Create: `tools/revert_patch.py`
- Create: `PATCH_MANIFEST.json`
- Test: `tests/test_patcher.py`

**Interfaces:**
- `apply_patch(target: Path, patch_root: Path, backup_root: Path) -> dict`.
- `revert_patch(target: Path, backup_root: Path, backup_id: str | None = None) -> dict`.

- [x] Write synthetic V3 installation fixture and tests for apply, second apply, backup, no-data writes and byte-identical rollback.
- [x] Verify RED.
- [x] Implement marker-based injections/copy operations.
- [x] Verify GREEN.

### Task 3: Server/compiler R6 bridge

**Files:**
- Patch target through patcher: `geometra/server.py`
- Patch target through patcher: `geometra/compiler.py`
- Add: `payload/shared/r6_patch.js`
- Test: `tests/test_server_compiler_hooks.py`

**Interfaces:**
- Import hook calls `validate_r6_project()` and stores `r6Validation`.
- New API `POST /api/r6_validate` validates current/supplied project.
- Compiler inlines `r6_patch.js` once before `</body>`.

- [x] Write failing tests against synthetic installed source.
- [x] Verify RED.
- [x] Add patch operations and JS payload.
- [x] Verify GREEN.

### Task 4: Geometra Kanban + validation UI

**Files:**
- Create: `payload/app/r6_patch.js`
- Create: `payload/app/r6_patch.css`
- Patch target: `app/index.html`
- Patch target: `geometra/server.py` static mapping
- Test: `tests/test_geometra_r6_ui.py`

**Interfaces:**
- Overrides `renderKanban` against existing `APP_STATE`, `api`, `pieces`, `current`, `esc` globals.
- Persists drop with `/api/update_piece` patch `{workflowStatus}`.
- Decorates library/build with R6 validation and production progress.

- [x] Write browser test for PENDIENTE→HACIENDO drag and API payload.
- [x] Verify RED.
- [x] Implement UI patch.
- [x] Verify GREEN.

### Task 5: Lienzo R6 inspector and checklist

**Files:**
- Modify: `payload/shared/r6_patch.js`
- Test: `tests/test_lienzo_r6_ui.py`

**Interfaces:**
- Uses only `window.ABRXOS.state.project/getEvent/getPiece/render` and DOM; it does not create a second document store.
- Exposes `window.ABRXOS_R6` utility API for test/debug.

- [x] Write browser tests for R6 XR fields, CINE fields, Caption Group displayCues/hidden styling and checklist persistence.
- [x] Verify RED.
- [x] Implement decorators/editor.
- [x] Verify GREEN.

### Task 6: Patch commands, verification and rollback UX

**Files:**
- Create: `APLICAR_PATCH.command`
- Create: `REVERTIR_PATCH.command`
- Create: `VERIFICAR_PATCH.command`
- Create: `README_PATCH.txt`
- Test: `tests/test_command_contract.py`

**Interfaces:**
- macOS commands locate `~/ABRXOS_GEOMETRA_V3` by default and allow `ABRXOS_GEOMETRA_TARGET` override for testing.

- [x] Write contract tests before scripts exist.
- [x] Verify RED.
- [x] Implement scripts.
- [x] Verify GREEN.

### Task 7: End-to-end candidate and regression package

**Files:**
- Create: `TEST_REPORT.md`
- Create: `CHANGELOG_V3_1_R6.md`
- Create: `examples/`

**Interfaces:**
- Apply patch to isolated synthetic/compatible V3 candidate.
- Validate official R6 fixtures plus legacy JOC/Amanda source.

- [x] Run Python syntax checks.
- [x] Run JS syntax checks.
- [x] Run pytest suite.
- [x] Run browser smoke on official R6 fixture when Chromium is available.
- [x] Verify sourceRanges unchanged in legacy roundtrip compatibility test.
- [x] Verify apply twice and rollback.
- [x] Build ZIP and test archive integrity.
