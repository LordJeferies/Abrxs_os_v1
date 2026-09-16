# ABRXOS Ecosystem Hotfix V3.1.1 · R6.1

## Geometra 3.1.1
- Adds `projectionReady` as an independent readiness axis.
- Adds R6.1 Source Alignment statistics/validation.
- Adds microtrim awareness without fabricating final `sourceRanges`.
- Adds VO_ADDED placement/recording inspector.
- Adds `shortSourceException` support for source-complete short Caption Groups.
- Adds checklist keys `sourceAlignment`, `microtrim`, `voRecording`.
- Adds route-semantics warning when a media type is incorrectly used as primary route.
- Preserves R6/legacy Alpha/Cutter behavior and the Cutter `sourceRanges` boundary.

## Content Builder 1.0.1
- Keeps R6 baseline intact and adds an R6.1 supplement layer.
- Adds Source Alignment, VO/route/caption and Lienzo Projection contracts to AI Packages.
- Adds `contract_manifest.json` with family/revision/features.
- Adds SHA-256 hashes for shared R6 libraries.
- Fixed-plan/transcript packages explicitly map Source Alignment before final sourceRanges.

## Brand Builder 1.0.1
- Metadata/contract handshake only.
- Branding Method and Brand Adapter remain separate.
- Declares R6 / R6.1 and `abrxos.brand-adapter.r6` / R6.1 compatibility.

## Release engineering
- Self-contained test resources and fixtures.
- No build-machine absolute test dependencies.
- Clean release manifest excludes `.pytest_cache`, `__pycache__`, `.pyc`, `.pyo`.
- Verifier compares Content Builder R6 library hashes against Geometra R6 libraries.
- Verifier checks Builder canon constants and Brand Adapter schema/version.
- Apply command uses atomic `install_hotfix`: post-apply verify failure triggers automatic rollback.
- Geometra precheck verifies base R6 library presence before any modification.
