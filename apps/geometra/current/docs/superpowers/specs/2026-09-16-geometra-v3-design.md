# ABRXOS Geometra V3 — Kernel + Renderer Packs

## Objective

Evolve Geometra V2.1 into a stable kernel that imports/normalizes editorial fichas once and can export the same canonical document through multiple independent Lienzo renderers without changing the domain logic.

## Invariants

- One canonical document is the source of truth.
- Renderer packs never own a second project model.
- Unknown fields, IDs and relations survive import/export.
- `sourceRanges` remain master/cutter truth; timeline drag creates editorial timing changes/overrides and never silently rewrites source truth.
- Video and static/carousel content use different workspaces.
- XR and SFX are catalog-driven with generic fallback for unknown/custom definitions.
- One completed pointer gesture creates one history entry.
- Click selects. Drag begins only after a movement threshold. A click on locked A-roll must never trigger an edit prompt or timing change.
- Lienzos remain standalone HTML files and can be reimported into Geometra.

## V3 scope

### Kernel

- HTML (`app-data`, `seed`, `editorialData`) and JSON import.
- Stable piece identity: `canonicalId/contentId/uid/id`.
- V2/V2.1 migration to V3 canonical envelope without deleting unknown data.
- Persistent project library.
- Renderer registry and capability validation.
- XR, SFX, Motion and Caption catalogs.
- Cutter structural QA.
- Standalone Lienzo compiler.

### Renderer packs in this release

1. `joc-classic` — production/editorial workspace influenced by the current JOC/Amanda Story Editor.
2. `shadcn-studio` — clean dashboard/studio renderer with denser inspector, calendar and responsive layout. It is standalone and dependency-free in this release so exported HTML does not depend on CDNs; the pack boundary allows replacing its UI with a React/shadcn build later without touching the kernel.

Both renderers consume the same `abrxos.document.v3` payload and shared runtime.

### Shared Lienzo behavior

- Ficha library/filtering.
- Video workspace with transcript/story, contextual inspector and T1–T9 timeline.
- Carousel/static workspace with slide preview/storyboard instead of video timeline.
- Kanban.
- Dedicated Calendar with unscheduled sidebar and drag/drop both directions.
- Undo/Redo.
- Selection vs drag threshold.
- Drag, trim and Alt/Option-drag duplicate.
- XR creation from registry and custom XR creation.
- SFX creation from registry.
- Generic JSON inspector for unknown/new resources.
- Copy actions for ficha/event/prompt/description.
- Local autosave.
- Export updated HTML and JSON.
- LOCAL/REMOTE/BASE merge.

## Canonical document V3

```json
{
  "schemaVersion": "abrxos.document.v3",
  "documentType": "ABRXOS_CANONICAL_DOCUMENT",
  "projectId": "...",
  "title": "...",
  "pieces": [],
  "catalogVersions": {
    "xr": "R5",
    "sfx": "1.0",
    "motion": "1.0",
    "captions": "2.0"
  },
  "extensions": {
    "xrDefinitions": [],
    "sfxDefinitions": []
  },
  "revision": {},
  "importHistory": []
}
```

Imported root fields not covered by this envelope are preserved under `sourcePayload` and relevant known fields are also normalized to the top level.

## Renderer contract

Every renderer directory contains:

- `manifest.json`
- `template.html`
- `styles.css`
- optional `adapter.js`

Manifest minimum:

```json
{
  "rendererId": "joc-classic",
  "version": "1.0.0",
  "documentSchema": "abrxos.document.v3",
  "capabilities": {
    "video": true,
    "timeline": true,
    "calendar": true,
    "kanban": true,
    "carousel": true,
    "merge": true,
    "mobile": true
  }
}
```

The compiler inlines the shared runtime, renderer adapter, renderer styles and canonical JSON into one HTML file.

## Timeline interaction state machine

```text
idle
  -> pointerdown -> dragCandidate

dragCandidate
  -> pointerup below threshold -> select
  -> pointermove >= threshold -> dragging/resizing
  -> Escape/pointercancel -> rollback

dragging/resizing
  -> pointerup -> commit one history operation
  -> Escape/pointercancel -> rollback
```

Thresholds: mouse/pen 6 px; touch 10 px.

For `locked_to_source` blocks, selection is always allowed. An actual drag/trim creates `editorialOverride` and changes `timingMode` to `manual_review`; original source timing is preserved.

## Catalog behavior

Catalog lookup is optional. An event with an unknown `definitionId` remains editable and visible through a generic fallback inspector. This guarantees XR10+ and custom SFX can enter the system before a renderer-specific visualization exists.

## Cutter contract

Current Cutter compatibility continues to depend on stable ID, type, source and valid `sourceRanges`. Timeline edits are exported as editorial state. V3 also emits `cutOverrides` when a source-affecting override is explicitly approved, but the current cutter is not forced to consume them.

## Not in V3.0

- VideoFlow integration.
- Heavy 4K media processing in the Lienzo.
- Automatic AI ficha generation.
- Direct GitHub credentials/token storage.
- DaVinci/CapCut automation.

Those remain capability/renderer packs for later releases.

## Gates

- Import real JOC55 HTML and preserve 45 pieces.
- Compile both renderers from one document.
- Reimport both outputs and retain piece IDs/sourceRanges.
- Browser smoke with zero page errors.
- Click A-roll selects with zero timing delta.
- Drag A-roll only starts after threshold and creates override.
- Undo restores drag.
- XR selection exposes internal states/assets and copy controls.
- Custom unknown XR renders via fallback.
- Carousel uses static workspace.
- Calendar supports unscheduled <-> dated drag.
- Renderer choice does not change canonical content hash except renderer metadata in export envelope.
