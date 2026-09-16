# ABRXOS Repo Tooling Fix 1.0.1 — Test Report

## Root cause

`CAPTURAR_INSTALACION_ACTUAL.command` used a shell variable named `path`. In zsh, `path` is a special array tied to `PATH`; assigning to it replaced the process PATH, so `/usr/bin/env python3` could no longer resolve Python even when the parent Terminal could.

## TDD regression

Initial regression suite: **5 failures**, including the `path` assignment and missing shared resolver/clean installer.

After the repair:

```text
7 passed
```

Covered:
- no zsh `path` assignment in capture;
- shared Python resolver exists and is used by critical tools;
- one-command finalizer exists;
- clean-install-from-repo command exists;
- individual Builder wrappers point to `apps/*/current`;
- update-from-Mac uses zsh rather than bash;
- restore documentation exists.

## Static shell verification

`bash -n` PASS for all new/modified `.command`/resolver files. The target runtime is `/bin/zsh` on macOS; Bash syntax checking is used here because zsh is not installed in the build container.

## Manifest generation

PASS: repo manifest regenerated after changes.

## Not claimable in this environment

The final capture of `~/ABRXOS_GEOMETRA_V3` must happen on the user's Mac because that installed tree is the authoritative current Geometra snapshot. `tools/DEJAR_REPO_LISTO.command` performs that capture and then verifies it before Git preparation.
