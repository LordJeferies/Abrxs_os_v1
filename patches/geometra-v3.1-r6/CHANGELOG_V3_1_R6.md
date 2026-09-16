# ABRXOS Geometra V3.1 R6 — Changelog

## ADDED

- R6 validation module `geometra/r6.py`.
- Official R6 libraries for XR families, edit profiles, CINE, SFX, Motion, Music and Captions.
- `POST /api/r6_validate`.
- Geometra Kanban drag/drop for `workflowStatus`.
- R6 Alpha/Cutter readiness badges in Geometra.
- Production progress from `productionChecklist`.
- R6 Lienzo inspector for XR families, CINE, Caption Groups, Images/Objects and SFX.
- R6 Edit Profile display: Cinematic Edit / Dynamic Edit / Clean Edit.
- Production Checklist editor inside Lienzo.
- R6 Caption Group hidden/suppressed visual state without deleting T9 block.
- Safe patch apply / verify / rollback commands.

## CHANGED

- Compiled Lienzos now inline the additive R6 runtime layer once.
- Imports and Lienzo compilation attach a fresh `r6Validation` report.
- `VERSION.json` becomes `3.1.0` after the patch is applied.

## UNCHANGED INVARIANTS

- `canonicalId` identity.
- `sourceRanges` as Cutter/master truth.
- `timeline.start/end` as edit-relative timing.
- T1–T9; CINE stays in T5, not T10.
- Existing `.app` launcher.
- `~/ABRXOS_GEOMETRA_DATA`.
- Legacy XR00–XR09; no blind R5→R6 family remap.
- Current Cutter boundary.

## MIGRATION NOTES

No data migration is required. This patch is additive around the V3 canonical document. R6 projects are detected through the R6 schema/features and annotated with `r6Version=R6`; old projects remain `LEGACY_COMPAT` and retain their original XR families and source ranges.

If a future project wants to replace a legacy XR00–XR09 with an R6 family, that remains an editorial migration and must not be inferred automatically.
