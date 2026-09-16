# Changelog

## Ecosystem 3.1.1 · R6.1 — 2026-09-16

- Geometra baseline V3.1 R6 + ecosystem hotfix R6.1.
- Content Builder 1.0.1: `sourceAlignment`, microtrim, VO Added, route semantics, Caption Groups R6, Projection contract and contract handshake.
- Brand Builder 1.0.1: explicit R6/R6.1 ecosystem handshake without changing Branding Method or Brand Adapter methodology.
- Geometra: R6 validator, R6.1 source alignment/VO/caption/projection checks, Kanban functional, Production Checklist, Alpha/Cutter/Projection readiness.
- Release engineering: clean manifests, self-contained fixtures, atomic verify/rollback.

## Baseline V3.1 · R6

See `patches/geometra-v3.1-r6/CHANGELOG_V3_1_R6.md`.

## Repo Tooling 1.0.1 — 2026-09-16

### Fixed
- zsh `path` special parameter no longer clobbers PATH during current-install capture.
- shared robust Python resolver for repo tools.
- current Builder install wrappers now point to `apps/*/current`.
- update-from-Mac invokes zsh scripts with zsh.

### Added
- one-command `tools/DEJAR_REPO_LISTO.command`.
- `install/INSTALAR_ECOSISTEMA_DESDE_CERO.command` for a clean Mac after the current snapshot has been committed.
- GitHub restore documentation.

### Unchanged
- app versions and contracts remain Geometra 3.1.1 / Content Builder 1.0.1 / Brand Builder 1.0.1 / R6.1.
