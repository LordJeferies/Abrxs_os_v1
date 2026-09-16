# ABRXOS Ecosystem Repository — Test Report

Date: 2026-09-16
Release: 3.1.1-r6.1

## Current Builder snapshots

Brand Builder current source:
- 8/8 tests PASS
- Python syntax PASS

Content Builder current source:
- 8/8 tests PASS
- Python syntax PASS

## Repository bootstrap tooling

A simulated Mac home was created with:
- Geometra 3.1.1 + R6/R6.1 hotfix registry
- Content Builder 1.0.1
- Brand Builder 1.0.1
- byte-identical shared R6 libraries

`CAPTURAR_INSTALACION_ACTUAL.command`:
- prechecked all three versions
- captured only code directories
- excluded caches/logs/compiled Python
- generated capture report and repo manifest

`VERIFY_ALL.command` result on the simulated captured repo:

```json
{
  "ok": true,
  "errors": [],
  "warnings": [],
  "checks": [
    "geometra_version=PASS",
    "contentBuilder_version=PASS",
    "brandBuilder_version=PASS",
    "geometra_hotfix_registry=PASS",
    "json_and_python=PASS",
    "node_check=PASS",
    "content_geometra_library_hashes=PASS",
    "brand_adapter_schema=PASS",
    "contentBuilder_pytest=PASS",
    "brandBuilder_pytest=PASS"
  ]
}
```

## Important bootstrap note

This downloadable repo intentionally does **not invent/reconstruct the full Geometra Kernel snapshot** from partial patch files. Before the first GitHub push on the real Mac, run:

```bash
zsh tools/CAPTURAR_INSTALACION_ACTUAL.command
```

That copies the exact already-installed and already-verified `~/ABRXOS_GEOMETRA_V3` source into `apps/geometra/current/` and refreshes both Builder snapshots from their installed code.

After this one-time bootstrap, Git should become the source of truth and installed apps should be deployment targets.
