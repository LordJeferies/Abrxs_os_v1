# ABRXOS Content Builder V1 — Design Specification

Date: 2026-09-16
Status: APPROVED BY CURRENT USER REQUEST (“construyas ya las dos apps según lo definido”)
Scope: Package Builder only; no integrated AI/API.

## Goal

Create a local Mac/browser app that converts an editorial intent plus transcript/project/brand context into a deterministic AI upload package for generating ABRXOS R6 Beta/Alpha content fichas.

## Architecture

- Python 3 standard-library local server.
- Single-page HTML/CSS/JS frontend.
- Local JSON persistence.
- Canon R6 resources bundled read-only.
- Finder/browser file import via browser file inputs.
- Deterministic package compiler exports folder + ZIP.
- Standalone HTML fallback uses localStorage and browser downloads, but filesystem folder export requires local server mode.

## Primary Modes

- Fixed editorial plan + transcript → Alpha.
- Transcript only → Intro Alpha.
- Transcript only → Vertical Alpha(s).
- Transcript only → Horizontal Alpha(s).
- Transcript → Carousel/static Alpha.
- Transcript → Betas for selection.
- Selected Beta → Alpha.
- Update existing Alpha.
- Dynamic Edit / MOTION_SFX with no XR.
- Clean Edit / SFX_ONLY.
- Full episode Alpha.
- Multi-source package.
- Plan without timings → Alpha needs_review.
- Generate entire project.

## Content Types

Video:
- intro
- vertical
- horizontal
- full_episode

Static:
- carousel
- quote
- thread
- note
- pdf
- script

## Stage / Production Profile

Stages:
- BETA
- ALFA

Edit profiles:
- XR_FULL / Cinematic Edit
- MOTION_SFX / Dynamic Edit
- SFX_ONLY / Clean Edit

Defaults under XR_FULL:
- Intro: exactly 6 XR.
- Vertical: 2–4 XR.
- Horizontal: ~1 XR per 2 minutes.
- Full episode: ~1 XR per 5 minutes.
- Avoid same XR family consecutively; narrative function overrides diversity.

## Inputs

- projectId / project title
- Project Config JSON
- Brand Adapter JSON
- transcript text/file
- editorial plan text/file
- current Beta/Alpha ficha JSON when applicable
- source group
- orientations
- desired types/counts
- stage
- edit profile
- platform targets
- special rules / do-not-change

Raw inputs are preserved separately from structured selections.

## Output AI Package

Each package contains:

- `00_START_HERE.txt`
- `01_QUE_SUBIR_A_CHATGPT.txt`
- `02_PROMPT_FINAL.txt`
- `03_REQUEST.json`
- `04_TRANSCRIPCION.txt`
- `05_PLAN_EDITORIAL.txt`
- `06_PROJECT_CONFIG.json`
- `07_BRAND_ADAPTER.json`
- `08_FICHA_TARGET.json`
- `09_CANON_CONTEXT.txt`
- `10_CURRENT_FICHA.json` when applicable
- `11_SPECIAL_RULES.txt`
- `package_manifest.json`

The package instructions require AI output as JSON + TXT. JSON is the canonical Geometra import; TXT is human-readable.

## Local Library

Content Builder stores drafts and imported Brand Adapters / Project Configs locally. It does not depend on Brand Builder being installed.

Data roots:
- `~/ABRXOS_CONTENT_BUILDER_DATA/`
- `~/ABRXOS_CONTENT_BUILDER_EXPORTS/`

## Stability Rules

- Canon version pinning.
- Preserve imported JSON unknown fields.
- Autosave/draft recovery.
- Path traversal protection.
- No AI keys/secrets.
- Deterministic manifest with SHA256 hashes.
- No invented timestamps.
- A package can be generated with missing timings only if it declares needs_review mode.
- UI dynamically hides video-only controls for static formats.
