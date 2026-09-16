# ABRXOS Geometra V3.1 R6 Patch — Design

## Objective

Upgrade an installed `ABRXOS_GEOMETRA_V3` 3.0.x installation in place without replacing the `.app` launcher or touching `~/ABRXOS_GEOMETRA_DATA`, adding R6-aware import/validation/UI behavior while preserving legacy R5/R4 content and the Cutter boundary.

## Patch model

The patch is cumulative and reversible:

```text
~/ABRXOS_GEOMETRA_V3/            code target
~/ABRXOS_GEOMETRA_DATA/          NEVER touched by patch
~/ABRXOS_GEOMETRA_PATCH_BACKUPS/ backup snapshots
```

`APLICAR_PATCH.command` runs a Python patcher that:
1. verifies required V3 files and version compatibility;
2. creates timestamped backup of files it will change;
3. installs additive R6 modules/assets;
4. injects small, marker-based hooks into existing V3 files instead of replacing the entire Kernel/runtime;
5. updates `VERSION.json` patch metadata;
6. runs syntax/self-tests;
7. automatically rolls back code files if verification fails.

`REVERTIR_PATCH.command` restores the newest backup made by this patch.

## Protected invariants

- `canonicalId` identity remains stable.
- `sourceRanges` remains source/master truth for Cutter.
- `timeline.start/end` remains edit-relative time.
- no T10; CINE uses T5/T4/T7/T8/T9.
- legacy XR00–XR09 content is preserved; no blind R5→R6 mapping.
- unknown/custom fields survive.
- renderer packs consume the same document.
- `.app` launcher remains unchanged.
- data library is never modified by installer/rollback.

## R6 integration

### Python R6 module

Add `geometra/r6.py` with:
- R6 schema detection;
- official library loading from `r6/` JSON files;
- structural validation returning a JSON report instead of only CLI text;
- edit-profile validation;
- family validation;
- caption-group validation;
- `productionChecklist` normalization/defaults;
- deep Alpha completeness scoring;
- Cutter readiness kept separate from Alpha readiness.

### Import hook

Patch `geometra/server.py` import route after `import_text()`:
- run R6 validation for every project;
- attach `r6Validation` and `r6Version` to document state;
- preserve import even when Alpha is incomplete; critical structural errors appear in validation rather than silently disappearing.

Legacy V3/R5 documents receive a compatibility report but are not rewritten into R6 families.

### Compile hook

Patch `geometra/compiler.py` to inline `shared/r6_patch.js` after the existing Lienzo runtime. The base runtime remains the source of timeline/undo/export behavior; the R6 patch adds presentation and R6-specific editing without creating a second store.

### Geometra application patch

Load `/r6_patch.js` after `/app.js`.

The patch script:
- upgrades Geometra Kanban cards to draggable cards and persists `workflowStatus` via `/api/update_piece`;
- preserves `stage`, schedule and source ranges;
- adds R6 validation badges and Alpha/Cutter status to Create Lienzo/library views;
- shows production progress derived from `productionChecklist`;
- displays edit-profile information;
- keeps calendar LISTO↔PROGRAMADO semantics.

### Lienzo R6 patch

An additive browser patch, using `window.ABRXOS.state.project` as the only document state:
- decorates inspector for R6 XR, CINE, Caption Groups, SFX, Images/Objects and Edit Profile;
- dims hidden caption groups rather than deleting them;
- exposes `displayCues`, `suppressedBy`, family rules and R6 asset fields;
- adds a Production Checklist editor that persists in the same project and localStorage;
- shows Alpha/Cutter validation summary;
- leaves existing timeline drag/trim/undo behavior unchanged.

## R6 canonical behavior

XR families:
`COMIC_INFO`, `COMIC_CC`, `TYPO`, `PHOTOS`, `OBJECTS`, `PHOTO_OBJECT`, `NO_XR`.

Edit profiles:
- `XR_FULL` / Cinematic Edit
- `MOTION_SFX` / Dynamic Edit
- `SFX_ONLY` / Clean Edit

Caption Groups:
- `type=caption_group`
- target 8–15 words, soft 6–17;
- preserve `captionSchema=abrxos.caption.v2` and `captionPolicyVersion=R6`;
- `COMIC_CC` uses `visibility=hidden` + `suppressedBy`.

CINE:
- root event `track=broll`, `type=cine`;
- types `CINE01_BLACK_HOLD`, `CINE02_FREEZE_HOLD`, `CINE03_PUNCH_CUT`.

## Kanban

Allowed workflow states:
`PENDIENTE`, `REVISADO`, `HACIENDO`, `LISTO`, `PROGRAMADO`, `PUBLICADO`.

Geometra application and Lienzo both persist `workflowStatus` in the piece. Calendar date transitions remain additive:
- LISTO + date => PROGRAMADO;
- PROGRAMADO - date => LISTO.

## Validation result contract

```json
{
  "schema": "abrxos.r6-validation.v1",
  "r6Detected": true,
  "critical": [],
  "warnings": [],
  "pieces": [
    {
      "id": "V01",
      "alphaReady": true,
      "cutterReady": true,
      "progressPercent": 72,
      "missing": [],
      "warnings": []
    }
  ]
}
```

`alphaReady` and `cutterReady` are independent.

## Testing gates

- official R6 fixtures import/validate;
- legacy JOC/Amanda V3/R5 remains importable;
- Cutter sourceRanges unchanged;
- Kanban Geometra drag persists workflow only;
- compiler output contains R6 patch once;
- R6 inspector: XR/CINE/caption fields visible;
- hidden caption remains present and visually dimmed;
- production checklist persists in document;
- browser page errors = 0;
- patch apply twice is idempotent;
- rollback restores byte-identical backed-up files;
- patch never writes under `ABRXOS_GEOMETRA_DATA`.
