# ABRXOS PATCH GEOMETRA V3.1 R6 — TEST REPORT

Fecha: 2026-09-16

## Resultado

El patch candidate pasó la suite automatizada completa:

```text
36 passed in 12.31s
```

El objetivo verificado es actualizar una instalación compatible de Geometra V3 3.x **sin reemplazar la `.app` ni tocar `ABRXOS_GEOMETRA_DATA`**.

## R6 oficial

Los tres fixtures oficiales incluidos en el paquete R6 del usuario pasaron el validador oficial `VALIDAR_R6.py`:

```text
FICHA_INTRO_ALFA_CINEMATIC_R6.json
CRITICAL: 0
WARNINGS: 0
PASS

FICHA_VERTICAL_ALFA_CINEMATIC_R6.json
CRITICAL: 0
WARNINGS: 0
PASS

FICHA_CAROUSEL_ALFA_R6.json
CRITICAL: 0
WARNINGS: 0
PASS
```

El validador integrado por el patch también reporta:

- Intro cinematic R6: Alpha Ready = true; Cutter Ready = true.
- Vertical cinematic R6: Alpha Ready = true; Cutter Ready = true.
- Carousel R6: Alpha Ready = true; Cutter Ready = false/no aplica como video.

## Cobertura de tests

### Validator R6

PASS:
- detección R6;
- identidad Alfa de video (`title`, `objective`, `thesis`, `source`, `editProfile`, `schedule`);
- `sourceRanges` válidos separados de Alpha completeness;
- familias XR R6;
- reglas de `COMIC_INFO`;
- perfiles `XR_FULL / MOTION_SFX / SFX_ONLY`;
- CINE en T5 y campos de dirección;
- Caption Groups R6 + suppression;
- SFX según `eventRequiredFields` de la librería oficial;
- static/carousel `staticProduction.items`;
- legacy XR00–XR09 no se remapea ni se marca como familia R6 inválida;
- Production Checklist conserva estados existentes.

### Patch engine

PASS:
- apply;
- segunda aplicación idempotente;
- backup localizado;
- rollback byte-identical;
- directorios completos se respaldan/restauran correctamente;
- hook con indentación conserva sintaxis Python;
- anchor faltante provoca rollback;
- versión major desconocida se bloquea;
- carpeta de datos hermana no se modifica.

### Server / compiler

PASS:
- import hook R6;
- `/api/r6_validate`;
- static routes de JS/CSS del patch;
- validación actualizada antes de compilar Lienzo;
- runtime R6 inlined exactamente una vez;
- `r6Validation` y `r6Version` llegan al `app-data` exportado.

### Geometra UI

PASS:
- Kanban card drag `PENDIENTE → HACIENDO`;
- request exacta `{patch:{workflowStatus:"HACIENDO"}}`;
- `stage`, `sourceRanges` y `schedule` no cambian;
- badges Alpha/Cutter;
- progreso de producción;
- Edit Profile nombre comercial + código;
- validación en Biblioteca / Crear Lienzo.

### Lienzo UI

PASS:
- inspector XR R6;
- campos de assets R6;
- inspector CINE especializado;
- inspector SFX R6;
- Caption Group source/highlight/displayCues/suppressedBy;
- caption hidden sigue existiendo en T9 y se atenúa;
- Edit Profile;
- Production Checklist editable;
- modificación del checklist cambia el mismo `state.project`;
- persistencia usa la API `localStorage` del Lienzo.

### End-to-end candidate

PASS:
- aplicar patch sobre candidato V3 compatible;
- `VERIFICAR_PATCH.command` devuelve `ok:true`;
- versión `3.0.0 → 3.1.0`;
- rollback devuelve `3.0.0`;
- fixture Intro R6 oficial se compila a Lienzo standalone con inspector R6;
- R6 runtime aparece una sola vez;
- `sourceRanges` original permanece sin modificación;
- HTML JOC/Amanda legacy conserva todos sus `sourceRanges` después de validation + compile y queda marcado `LEGACY_COMPAT`.

## Sintaxis

PASS:

```text
python3 -m py_compile payload/geometra/r6.py tools/apply_patch.py tools/revert_patch.py tools/verify_patch.py
node --check payload/shared/r6_patch.js
node --check payload/app/r6_patch.js
bash -n APLICAR_PATCH.command
bash -n REVERTIR_PATCH.command
bash -n VERIFICAR_PATCH.command
```

Los scripts llevan shebang `zsh` para macOS. El entorno de construcción no incluye zsh, por lo que la validación estática del shell se hizo con Bash; no se afirma una ejecución end-to-end en una Mac real desde este container.

## Verificación del instalador real

Se ejecutó el flujo completo sobre un candidato compatible aislado:

```text
APLICAR_PATCH.command
→ backup
→ apply
→ verify
→ PASS

VERIFICAR_PATCH.command
→ PASS

REVERTIR_PATCH.command
→ restore
→ PASS
```

El verificador comprobó 26 condiciones, incluyendo archivos, markers, Python compile, Node syntax y validator R6.

## Limitación honesta

La instalación concreta que está en la Mac del usuario no está montada dentro de este entorno. Por eso no puedo afirmar que ejecuté el patch sobre **esa copia física exacta**. Para reducir ese riesgo:

1. el patch valida `VERSION.json`;
2. busca anchors exactos de la entrega Geometra V3;
3. hace backup antes de mutar;
4. si falta un anchor, restaura automáticamente;
5. después de aplicar ejecuta `verify_patch.py`;
6. si esa verificación falla, `APLICAR_PATCH.command` ejecuta rollback automático.

No se hacen reemplazos a ciegas del Kernel.
