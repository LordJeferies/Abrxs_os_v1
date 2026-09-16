# ABRXOS X · Brand Builder V1 — Design Specification

Date: 2026-09-16
Status: DESIGN APPROVED FOR REVIEW
Scope: Package Builder only (no integrated AI/API in V1)

## 1. Product Goal

ABRXOS X · Brand Builder V1 is a local Mac/browser application for creating reproducible AI packages that help an external AI produce a complete ABRXOS Brand Adapter R6 plus structured branding-strategy outputs.

The application does not call an AI directly. It collects, preserves, structures and exports the user’s brand information, the selected Branding Method inputs, the active ABRXOS canon, and the expected output contracts.

Primary flow:

RAW BRAND INFORMATION
→ optional structured form
→ Branding Method input
→ Brand Adapter input
→ deterministic AI package
→ user uploads package to ChatGPT/other AI
→ AI returns Brand Adapter JSON + TXT
→ user imports result back into Brand Builder / Geometra ecosystem.

## 2. Architectural Principles

1. Preserve raw user input exactly.
2. Keep strategy and production adaptation separate.
3. No AI/API dependency in V1.
4. Canon and schemas are external versioned resources, not hard-coded copies spread through the UI.
5. Unknown fields must survive import/edit/export round-trips.
6. Export packages must be deterministic and version pinned.
7. Autosave and draft recovery are mandatory.
8. The app must remain usable even if a Branding Method section is incomplete.

## 3. Technology

V1 uses the same practical pattern as current ABRXOS local tools:

- Python 3 local server
- HTML/CSS/JavaScript frontend
- localhost browser UI
- macOS `.app` launcher created by installer
- local JSON persistence
- Finder-based import/export

No Tauri, Firebase, user account, cloud backend or OpenAI API in V1.

Default local data roots:

- `~/ABRXOS_BRAND_BUILDER_DATA/`
- `~/ABRXOS_BRAND_BUILDER_EXPORTS/`

## 4. Branding Method Layer

The uploaded Branding Method is treated as a separate strategic layer from the Brand Adapter.

The source organizes brand development around five drivers:

1. THE BRAND EGO — consumer analysis
2. THE BRAND GANG — competitive strength
3. THE BRAND ESSENCE — brand platform / DNA
4. THE BRAND IDENTITY — brand assets and identities
5. THE BRAND EXPERIENCE — activation and experience

The source further organizes each driver around five tools. The application will not reproduce the PDF verbatim. Instead it offers a structured workspace derived from the user-provided method and can tell the user to attach the original PDF when external AI analysis needs the full source.

### 4.1 Mode chosen for V1

V1 uses **Mode A**:

- default: `Resumen de 5 Drivers`
- optional expansion: `Ver las 25 tools`

The 25 tools are not mandatory for every client.

### 4.2 Summary Driver outputs

#### Driver 1 · Brand Ego
Core summary fields:
- buyer/client
- consumer/user
- ideal audience
- lost opportunity
- external context
- internal context
- desired self-image
- pains/fears
- gains
- emotional meaning
- trust/proof needs

#### Driver 2 · Brand Gang
Core summary fields:
- market minimums / hygienic attributes
- valued differentiators
- singular advantages
- brand territory
- direct competitors
- historical competitors
- current/star competitors
- revolutionary/indirect competitors
- category opportunity
- brands outside category that inspire innovation

#### Driver 3 · Brand Essence
Core summary fields:
- territory
- core value
- positioning
- purpose
- values
- personality
- evangelizes
- defends
- motivates
- elevates
- contributes
- reason to believe
- unique selling proposition

#### Driver 4 · Brand Identity
Core summary fields:
- symbolic identity
- behavioral/attitudinal identity
- verbal identity
- visual identity
- sensory identity
- archetype/personality
- tone of voice
- voice land
- voice path / verbal rules
- key words
- forbidden words
- differential verbal resources
- logo/symbol references
- typography
- color
- photography
- illustration
- icons/emojis/stickers
- layout
- motion
- sonic identity
- texture/touch and other sensory cues if relevant

#### Driver 5 · Brand Experience
Core summary fields:
- Why We: problem / best option / CTA
- internal narrative
- external narrative
- sagas/content territories
- proof points
- actions/storydoing
- rituals: IN / DURING / OUT
- golden moments / customer journey notes
- loyalty/recommendation ideas
- memorable “BURN” moments / experience differentiation

## 5. 25 Tools Expansion

The optional deep mode exposes the 25 tools as collapsible cards grouped by driver.

Driver 1:
- The Dog Matrix
- The Feel Map
- Brand Desire Canvas
- Attitudinal Journey
- The Brand Ego

Driver 2:
- Max Pyramid
- The Brand Territory
- ABC Roll Axis
- Revolution Matrix
- The 5 Friends

Driver 3:
- Los 5 Qués del Branding
- The Core Value
- Brand Positioning Model
- Purpose Check
- Brand Values

Driver 4:
- The Brand Symbol
- Brand Charisma Archetypes
- Tone of Voice Path
- Full Brand Board
- The Sense Square

Optional verbal subtools supported inside Driver 4:
- Naming
- Tagline / Slogan distinction

Driver 5:
- Why We?
- Brand Narratives
- Brand Rituals
- The 10 Golden Moments
- The Burn Pyramid

Each tool card contains:
- user input area
- optional structured mini-form
- raw notes
- source status
- completion status
- `AI can infer` toggle
- `must be human-confirmed` toggle

## 6. Brand Adapter Layer

The Brand Adapter remains a separate operational contract used by content-generation and production systems.

Sections:

- identity and metadata
- audiences
- voice and copy
- visual language
- photography / camera / lighting
- typography
- palette
- logo/symbol use
- video edit style
- edit profile defaults
- XR preferences and prohibitions
- Motion preferences
- CINE preferences
- SFX library/policy
- Music direction
- Caption style
- covers/thumbnails
- carousel style
- claims and legal/verification rules
- asset-generation rules
- negative constraints

The app visually shows the relationship:

`Branding Method = Strategy / Meaning / DNA`

`Brand Adapter = Operational expression / production contract`

The two JSON objects remain distinct.

## 7. Input Modes

### 7.1 Guided Form
User fills structured fields by section.

### 7.2 Free Text
Large textarea accepts unstructured brand description.

The app preserves this text in full as `rawBrandContext` and never overwrites it with normalized form values.

### 7.3 Hybrid
User can combine both modes. Conflicts are shown, not silently resolved.

### 7.4 External reference files
V1 allows recording reference filenames and copying selected text/notes into package metadata. The app can instruct the user to attach the original Branding Method PDF and other references to the AI package. It does not embed or republish third-party source material into the application bundle.

## 8. Data Model

Primary brand workspace document:

```json
{
  "schemaVersion": "abrxos.brand-builder.workspace.v1",
  "workspaceId": "...",
  "brandId": "...",
  "brandName": "...",
  "revision": 1,
  "rawBrandContext": "...",
  "brandForm": {},
  "brandingMethod": {
    "mode": "summary|full25",
    "drivers": {},
    "tools": {}
  },
  "brandAdapterDraft": {},
  "referenceFiles": [],
  "sourceStatuses": {},
  "completion": {},
  "createdAt": "...",
  "updatedAt": "...",
  "unknownFields": {}
}
```

Source status enum:
- `USER_CONFIRMED`
- `SOURCE_DERIVED`
- `AI_INFERENCE_ALLOWED`
- `NEEDS_REVIEW`

## 9. Main UI

### 9.1 Home / Library

Cards:
- brand name
- brandId
- method completion
- adapter completion
- last edited
- last export

Actions:
- New Brand
- Import Workspace
- Import Brand Adapter
- Open
- Duplicate
- Export

### 9.2 Brand Workspace

Left navigation:
- Overview
- Raw Context
- Brand Form
- Branding Method
- Brand Adapter
- References
- QA
- Export

Branding Method view:
- 5 Driver summary cards first
- progress per driver
- button `Ver las 25 tools`

Brand Adapter view:
- contextual accordions, not all fields at once
- completion and warnings

### 9.3 Export view

User chooses:
- package name
- target AI (generic label only; no API coupling)
- include Branding Method PDF reminder yes/no
- include raw context yes/no
- include summary Method JSON yes/no
- include full 25-tool Method JSON yes/no
- include Brand Adapter template yes/no

Preview shows exact generated files before export.

## 10. AI Package Output

Example:

```text
CLIENTE_X_BRAND_AI_PACKAGE/
├── 00_START_HERE.txt
├── 01_QUE_SUBIR_A_LA_IA.txt
├── 02_PROMPT_FINAL.txt
├── 03_RAW_BRAND_CONTEXT.txt
├── 04_BRAND_FORM.json
├── 05_BRANDING_METHOD_INPUT.json
├── 06_BRAND_ADAPTER_TEMPLATE_R6.json
├── 07_EXPECTED_OUTPUT_SCHEMA.json
├── 08_REFERENCE_FILES.txt
├── 09_FILES_INDEX.json
└── package_manifest.json
```

Expected AI return:

```text
BRAND_ADAPTER_<BRAND>_R6.json
BRAND_ADAPTER_<BRAND>_R6.txt
BRANDING_METHOD_RESULT_<BRAND>.json
BRANDING_METHOD_RESULT_<BRAND>.txt
```

## 11. Stability Features

Mandatory V1 features:

- autosave after edits
- explicit save indicator
- revision history / snapshots
- crash recovery
- deterministic package generation
- schema validation before export
- unknown-field preservation
- duplicate ID detection
- package manifest with SHA-256 hashes
- canon version pinning
- Brand Adapter schema version pinning
- import validation
- no destructive overwrite without backup
- export to timestamped folder

## 12. Error Handling

Validation levels:

### Critical
Blocks export:
- missing workspace/brand ID
- malformed JSON import
- duplicate immutable IDs
- missing selected canon/template file

### Warning
Does not block export:
- incomplete driver
- missing palette
- missing official typography
- no competitor data
- inferred fields not human-confirmed

### Informational
- sections intentionally not applicable
- Method deep tools not completed because summary mode is being used

## 13. Testing Gates

Before release:

- Python compile check
- frontend JS syntax check
- schema tests
- export package test
- import round-trip test
- unknown-field preservation test
- autosave/recovery test
- duplicate ID test
- deterministic export test
- visual browser smoke tests

Viewports:
- 1440×900
- 390×844
- 844×390
- 820×1180
- 1180×820

## 14. Non-goals for V1

Not included:
- OpenAI/Claude/Gemini API calls
- automatic web research
- cloud sync
- Firebase
- user accounts
- multi-user collaboration
- Tauri packaging
- automatic completion of Branding Method
- automatic publishing

## 15. Future-Compatible Hooks

The architecture should allow later additions without migration-breaking changes:

- optional AI execution adapter
- pluggable branding methodologies
- central Brand Adapter library shared with Content Builder
- optional GitHub/cloud sync
- Tauri wrapper

## 16. V1 Success Criteria

V1 is successful when a user can:

1. create a brand workspace;
2. write free-form context and/or use forms;
3. complete the 5-driver summary;
4. optionally open and complete any of the 25 tools;
5. prepare a Brand Adapter draft;
6. export a deterministic AI package;
7. see exactly what to upload and what output to expect;
8. close/reopen the app without losing progress;
9. import an AI-generated Brand Adapter later without losing unknown fields.
