# ABRXOS ECOSYSTEM HOTFIX V3.1.1 · R6.1 — TEST REPORT

Fecha de validación: 2026-09-16

## Resultado general

El hotfix fue probado en dos grupos aislados para evitar que Chromium/Playwright comparta ciclo de vida con las pruebas puramente Python del harness:

```text
Non-UI / contracts / patcher / validator: 26 PASS
Browser UI:                             3 PASS
TOTAL:                                 29 PASS
```

Evidencia:
- `evidence/PYTEST_NON_UI.txt`
- `evidence/PYTEST_UI.txt`

## Regresión de las Builders existentes

Se copiaron las apps V1 originales, se sustituyó únicamente el engine correspondiente por el hotfix y se ejecutaron sus suites originales:

```text
ABRXOS Content Builder V1: 8 PASS
ABRXOS X Brand Builder V1: 8 PASS
```

Esto verifica que el handshake R6.1 es aditivo y que no rompe el comportamiento previo de Package Builder.

Evidencia: `evidence/BUILDERS_BASELINE_REGRESSION.txt`.

## R6 / R6.1 validator

Fixtures R6 originales con el validator 3.1.1:

```text
INTRO ALFA CINEMATIC R6
critical=0 warnings=0
Alpha READY
Cutter READY
Projection REVIEW

VERTICAL ALFA CINEMATIC R6
critical=0 warnings=0
Alpha READY
Cutter READY
Projection REVIEW

CAROUSEL ALFA R6
critical=0 warnings=0
Alpha READY
Projection READY
Cutter no aplica / false
```

`Projection REVIEW` en fichas de video R6 legacy es intencional: sus assets XR pueden existir anidados y ser Alpha/Cutter Ready aunque todavía no tengan bloques T3 independientes.

Fixture real `INTRO_AMANDA_ALFA_PREBUILD_R6_1.json`:

```text
critical=0
warnings=0
sourceAlignment nodes=25
located=25
microtrim required=16
VO_ADDED=2
VO placement ready=true
Projection READY
Alpha REVIEW
Cutter REVIEW
```

Alpha/Cutter quedan REVIEW porque la prebuild todavía no resuelve `sourceRanges` finales y conserva campos R6 incompletos en CINE/SFX. El hotfix no inventa esos datos para hacer pasar el gate.

Evidencia: `evidence/R6_R61_VALIDATION.json`.

## Projection Ready

Se verificó que sea independiente de los otros gates:

- recursos XR temporales sin evento T3 → Projection REVIEW;
- agregar las proyecciones T3 correspondientes → Projection READY;
- este cambio no altera `sourceRanges`;
- Alpha Ready y Cutter Ready mantienen su semántica anterior.

## Source Alignment / microtrim

Se verificó:

- `sourceAlignment`, `microtrim`, `voRecording` presentes en Production Checklist;
- `cue_verified`/`cue_based` contabilizados como source localizado;
- microtrims reportados sin convertir automáticamente parent cues en sourceRanges finales;
- `shortSourceException` elimina warnings falsos para captions cortos completos;
- VO_ADDED con placement after/before no necesita sourceRange falso.

## Lienzo R6.1

Chromium comprobó:

- Source Alignment visible en inspector de ficha;
- microtrim visible;
- Projection READY/REVIEW visible;
- VO Added inspector muestra placement, timing/recording status;
- nuevos checklist keys visibles;
- JavaScript sin errores de sintaxis.

## Geometra app R6.1

Chromium comprobó:

- Kanban/cards pueden mostrar Projection readiness;
- progreso R6.1 visible;
- checklist R6.1 reconocido;
- el Kanban funcional de V3.1 permanece como baseline; este hotfix no cambia su schema.

## Content Builder contract handshake

El package generado por Content Builder 1.0.1 contiene:

- `canonFamily=R6`
- `canonRevision=R6.1`
- `sourceAlignment`
- `microtrim`
- `voAdded`
- `routeSemanticsR61`
- `captionGroupsR6`
- `shortSourceException`
- `projectionReady`
- `12_R6_1_SOURCE_ALIGNMENT.txt`
- `13_R6_1_VO_ROUTE_CAPTIONS.txt`
- `14_LIENZO_PROJECTION_CONTRACT.json`
- `contract_manifest.json`

El verifier compara los SHA-256 de las 7 librerías R6 de Content Builder con las de Geometra. Una alteración de `XR_FAMILIES_R6.json` fue detectada como incompatibilidad en prueba negativa.

## Brand Builder contract handshake

Se verificó:

- engine 1.0.1;
- canonFamily R6;
- canonRevision R6.1;
- Brand Adapter schema `abrxos.brand-adapter.r6`;
- adapterVersion R6.1;
- Branding Method y Brand Adapter continúan como outputs separados.

Una modificación de `adapterVersion` a R6.0 fue detectada por el verifier en prueba negativa.

## Installer / verifier / rollback

Sandbox completo:

```text
ANTES
Geometra        3.1.0
Content Builder 1.0.0
Brand Builder   1.0.0

APPLY + VERIFY
Geometra        3.1.1
Content Builder 1.0.1
Brand Builder   1.0.1
verify.ok=true

CHECKS
geometra_r61_validator=PASS
contentBuilder_canon_handshake=PASS
content_geometra_library_hashes=PASS
brandBuilder_canon_handshake=PASS
brand_adapter_contract=PASS

REVERT
Geometra        3.1.0
Content Builder 1.0.0
Brand Builder   1.0.0
```

El sentinel dentro de `ABRXOS_GEOMETRA_DATA` permaneció `UNCHANGED` antes y después del rollback.

Evidencia: `evidence/SANDBOX_INSTALL_VERIFY_REVERT.json`.

También se probó la condición negativa: si el post-apply verify detecta incompatibilidad, `install_hotfix` ejecuta rollback automático y restaura los tres componentes.

## Precheck de seguridad

El hotfix bloquea ANTES de tocar archivos si:

- Geometra no es 3.1.x;
- falta `.abrxos_patches/ABRXOS_GEOMETRA_V3_1_R6.json`;
- falta alguna librería R6 base requerida.

Las Builders son opcionales y pueden quedar `SKIPPED_MISSING`.

## Sintaxis

PASS:

```text
python3 -m py_compile tools/*.py
python3 -m py_compile PATCH_GEOMETRA/geometra/r6.py
python3 -m py_compile PATCH_CONTENT_BUILDER/content_engine.py
python3 -m py_compile PATCH_BRAND_BUILDER/brand_engine.py
node --check PATCH_GEOMETRA/shared/r6_patch.js
node --check PATCH_GEOMETRA/app/r6_patch.js
bash -n APLICAR_HOTFIX.command
bash -n VERIFICAR_HOTFIX.command
bash -n REVERTIR_HOTFIX.command
```

El destino de los `.command` es `/bin/zsh` en macOS. El entorno de construcción no dispone de zsh; el parseo de shell se verificó con Bash y las operaciones de filesystem/rollback se probaron mediante los módulos Python que ejecutan los `.command`.

Evidencia: `evidence/SYNTAX_CHECKS.txt`.

## Release self-contained

Los tests del hotfix usan fixtures incluidas en el propio paquete. No dependen de `/mnt/data/r6pkg` ni de la máquina de build.

`PACKAGE_MANIFEST.json` excluye deliberadamente:

- `.pytest_cache`
- `__pycache__`
- `.pyc`
- `.pyo`

La integridad del ZIP final se verifica después de empaquetar y después de extraerlo en un directorio limpio.

## Límites deliberados

- No modifica Kernel V3.
- No modifica Library V3.
- No migra datos de usuario.
- No cambia canonicalId ni sourceRanges.
- No cambia el Cutter actual.
- `cutOverrides`/microtrim continúan requiriendo resolución explícita antes de convertirse en sourceRanges finales.
- No integra IA directamente dentro de ninguna app.
