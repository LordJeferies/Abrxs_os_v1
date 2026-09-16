# ABRXOS Ecosystem Hotfix V3.1.1 R6.1 — Design

## Goal

Close the integration boundary between Geometra V3.1 R6, Content Builder V1 and Brand Builder V1 without replacing their kernels, user data directories or installed `.app` launchers.

## Constraints

- Geometra kernel/library/sourceRanges/T1–T9 IDs remain unchanged.
- Existing V3.1 hooks are reused; no duplicate hook markers.
- Legacy XR00–XR09 and R6 families remain valid.
- R6 is the baseline; R6.1 is an additive compatibility layer.
- User data directories are never patched or rolled back.
- Each installed app is backed up independently.
- Hotfix may skip a missing Builder, but Geometra V3.1 R6 is mandatory.
- No direct GitHub/token, AI API or VideoFlow integration.

## Geometra delta

- package tests become self-contained; no `/mnt/data/r6pkg` dependency;
- package manifest excludes caches/pyc and verifies cleanly;
- `sourceAlignment[]` validation + inspector;
- `VO_ADDED` placement/recording metadata inspector;
- R6.1 route semantics validation;
- `shortSourceException` support for Caption Groups;
- production checklist keys: `sourceAlignment`, `microtrim`, `voRecording`;
- third readiness axis: `projectionReady`;
- Projection Gate validates that timed nested XR assets/motion/SFX/VO/CINE/captions expected in the Lienzo have timeline projections;
- Geometra Library/Kernel/Cutter contract stay unchanged.

## Content Builder delta

- keep canon family `R6`, add revision `R6.1`;
- generated AI packages include `contract_manifest.json`;
- include R6.1 source-alignment + VO/route/caption supplement;
- include projection contract;
- plan-fixed/transcript prompt explicitly performs source alignment before final sourceRanges;
- package manifest includes library hashes and required features.

## Brand Builder delta

- no UX or methodology change;
- package metadata declares `canonFamily=R6`, `canonRevision=R6.1`;
- generated package includes the same ecosystem contract handshake;
- Brand Adapter remains schema `abrxos.brand-adapter.r6` / adapterVersion R6.1.

## Installer

One reversible ecosystem package with:

- `APLICAR_HOTFIX.command`
- `VERIFICAR_HOTFIX.command`
- `REVERTIR_HOTFIX.command`
- per-app backup registry;
- target discovery for the existing Geometra V3, Content Builder V1 and Brand Builder V1 installs;
- independent patch/verify for each app;
- cross-app contract test;
- full rollback if mandatory Geometra verification fails;
- optional Builders are skipped if absent.
