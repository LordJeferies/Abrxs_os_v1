# ABRXOS Ecosystem Hotfix V3.1.1 R6.1 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [x]`) syntax for tracking.

**Goal:** Produce a reversible ecosystem hotfix that upgrades Geometra V3.1 R6 to R6.1 integration and aligns Content Builder/Brand Builder package contracts without replacing kernels, launchers or user data.

**Architecture:** Patch the existing Geometra R6 extension files and Builder package-generation engines only. Add contract manifests and R6.1 supplements at package boundaries. The installer operates on copies/backups and verifies each component plus a cross-app handshake.

**Tech Stack:** Python 3, vanilla JavaScript/CSS, JSON, zsh/macOS launcher scripts, pytest/node syntax checks.

**Spec:** `docs/superpowers/specs/2026-09-16-ecosystem-hotfix-r6-1-design.md`

## Global Constraints

- Target Geometra must already have V3.1 R6 patch markers/registry.
- `~/ABRXOS_GEOMETRA_DATA`, Builder data/export folders are immutable to the patch.
- No Kernel V4, no schema-breaking migration, no Cutter behavior change.
- Release ZIP must contain no `.pytest_cache`, `__pycache__`, `.pyc` or absolute test fixture paths.

---

### Task 1: Release self-containment and manifest hygiene

**Files:**
- Create: `tests/test_release_package.py`
- Create: `tools/release_manifest.py`
- Copy fixtures into: `PATCH_GEOMETRA/tests/fixtures/`

**Interfaces:**
- `build_manifest(root: Path) -> dict`
- `verify_manifest(root: Path, manifest: dict) -> list[str]`

- [x] Write failing tests for no cache/pyc entries, no `/mnt/data/r6pkg`, clean hash verification.
- [x] Run RED.
- [x] Implement fixture relinking and clean manifest helper.
- [x] Run GREEN.

### Task 2: Geometra R6.1 validator and Projection Ready

**Files:**
- Create: `tests/test_geometra_r6_1.py`
- Modify copy of: `payload/geometra/r6.py`

**Interfaces:**
- `validate_r6_project(...)` returns per-piece `alphaReady`, `cutterReady`, `projectionReady`, `missing`, `projectionMissing`, `warnings`.

- [x] Write failing tests for sourceAlignment, VO placement, shortSourceException, projection readiness and new checklist keys.
- [x] Run RED.
- [x] Implement minimal validator additions.
- [x] Run GREEN + old validator tests.

### Task 3: Lienzo R6.1 inspector/readiness UI

**Files:**
- Create: `tests/test_lienzo_r6_1_ui.py`
- Modify copy of: `payload/shared/r6_patch.js`
- Modify copy of: `payload/app/r6_patch.js`
- Modify copy of: `payload/app/r6_patch.css`

**Interfaces:**
- show Source Alignment, VO Added and Projection Ready without touching sourceRanges.

- [x] Write failing DOM/string tests for new UI blocks and checklist keys.
- [x] Run RED.
- [x] Implement source alignment/VO/projection blocks and CSS.
- [x] Run GREEN + JS syntax.

### Task 4: Content Builder contract handshake

**Files:**
- Create: `tests/test_content_builder_r6_1.py`
- Modify patch copy of: `content_engine.py`
- Add: `resources/r6_1/*`

**Interfaces:**
- package contains `12_R6_1_SOURCE_ALIGNMENT.txt`, `13_R6_1_VO_ROUTE_CAPTIONS.txt`, `14_LIENZO_PROJECTION_CONTRACT.json`, `contract_manifest.json`.

- [x] Write failing package-generation test.
- [x] Run RED.
- [x] Implement additive R6.1 supplement/contract manifest.
- [x] Run GREEN + existing Builder tests.

### Task 5: Brand Builder handshake

**Files:**
- Create: `tests/test_brand_builder_r6_1.py`
- Modify patch copy of: `brand_engine.py`

**Interfaces:**
- generated package declares canon family/revision and compatible schemas/features.

- [x] Write failing test.
- [x] Run RED.
- [x] Implement metadata-only handshake.
- [x] Run GREEN + existing Brand Builder tests.

### Task 6: Reversible ecosystem installer/verifier/reverter

**Files:**
- Create: `tools/apply_hotfix.py`
- Create: `tools/verify_hotfix.py`
- Create: `tools/revert_hotfix.py`
- Create: `APLICAR_HOTFIX.command`
- Create: `VERIFICAR_HOTFIX.command`
- Create: `REVERTIR_HOTFIX.command`
- Test: `tests/test_ecosystem_patcher.py`

**Interfaces:**
- patch mandatory Geometra; optional Builders; never mutate data dirs.

- [x] Write failing sandbox-install tests.
- [x] Run RED.
- [x] Implement patch/apply/verify/revert.
- [x] Run GREEN.

### Task 7: Cross-app contract integration and release

**Files:**
- Create: `tests/test_cross_app_contract.py`
- Create: `README_HOTFIX.txt`
- Create: `CHANGELOG_V3_1_1_R6_1.md`
- Create: `TEST_REPORT.md`
- Create: `HOTFIX_MANIFEST.json`

**Interfaces:**
- Brand package and Content package advertise compatible R6/R6.1 handshake; Geometra supports requested features.

- [x] Write failing cross-app compatibility test.
- [x] Run RED.
- [x] Add compatibility metadata/verification.
- [x] Run complete test suite and syntax checks.
- [x] Build clean ZIP, verify manifest and archive integrity.
