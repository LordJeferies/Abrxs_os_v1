# ABRXOS Content Builder V1 — Test Report

Date: 2026-09-16

## Fresh verification

- Python compile: PASS (`python3 -m py_compile *.py`)
- Test suite: PASS — 8 tests, 0 failures
- Installer syntax: PASS under `bash -n` (target script uses `/bin/zsh` on macOS)
- Inline JavaScript syntax: PASS (`node --check`)
- Standalone browser smoke: PASS with system Chromium through Playwright `set_content`
  - transcript-only → carousel routes to case 05
  - static type disables video edit profile
  - all-project routes to case 14 and exposes quantity panel
  - zero page errors
- HTTP/server behavior: covered by API tests (health, drafts, libraries, cases, export package)
- R6 route/package matrix: PASS
  - 14 canonical cases build successfully
  - 5 additional static variants (quote/thread/note/pdf/script) build successfully
  - each generated package ZIP exists
  - non-carousel static Alpha uses generic static R6 prompt

## Environment limitation

The harness blocked direct Chromium navigation to `http://127.0.0.1` with `ERR_BLOCKED_BY_ADMINISTRATOR`, so the server UI was not browser-smoked through a real localhost navigation in this environment. Local server endpoints are independently exercised by HTTP tests, and the exact HTML/JS UI was browser-smoked standalone with zero page errors.
