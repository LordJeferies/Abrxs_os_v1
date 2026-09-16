# ABRXOS GEOMETRA V3 — TEST REPORT

Fecha: 2026-09-16

## Arquitectura validada

Geometra V3 usa `abrxos.document.v3` como documento canónico y dos renderer packs sobre el mismo estado:

- `joc-classic`
- `shadcn-studio`

VideoFlow no forma parte de V3.0.

## Suite automatizada

Ejecución fresca con plugins externos de pytest deshabilitados para evitar interferencias del harness:

```text
45 passed in 47.50s
```

La suite cubre:

- import `app-data`, `seed`, JSON y V2/V2.1;
- preservación de IDs y campos desconocidos;
- captions V2 idempotentes;
- registry de renderers;
- catálogos XR/SFX y fallback desconocido;
- compile standalone sin CDN;
- selección segura de timeline;
- threshold click/drag;
- drag + trim + Undo;
- `editorialOverride` y `cutOverrides`;
- propagación XR → child `follow_parent`;
- inspector XR/imagen/SFX/caption;
- edición directa de prompts y datos internos;
- XR/SFX custom creados desde el Lienzo;
- Carousel Studio separado del timeline de video;
- calendario + Sin programar drag/drop;
- merge LOCAL/REMOTE/BASE;
- migración de biblioteca;
- Geometra UI: selección de renderer y export;
- responsive de los dos renderers;
- ruta editorial: sólo una ruta (`voA`, `voB`, `source`, etc.) se proyecta en el timeline para evitar overlays alternativos superpuestos.

## Regresión específica: click no es drag

Fixture de timeline:

- click sobre A-roll `locked_to_source` → selecciona e inspector cambia;
- no modifica `start/end`;
- no abre diálogo de override;
- movimiento menor de 6 px con mouse/pen sigue siendo selección;
- al cruzar 6 px comienza drag real;
- touch usa 10 px;
- sólo el gesto real crea `editorialOverride` y una entrada de historial.

## Prueba con datos reales JOC/Amanda

Fuente real importada: 45 fichas.

Se compiló un subset real con el primer intro + primer carrusel a los dos renderers y se ejecutó Chromium sobre cada Lienzo.

### JOC Classic

```json
{
  "pieces": 2,
  "aroll_click_no_move": true,
  "click_dialogs": [],
  "xr_inspector_chars": 4997,
  "carousel": true,
  "slides": 5,
  "calendar": true,
  "unscheduled": 2,
  "page_errors": []
}
```

### Shadcn Studio V1

```json
{
  "pieces": 2,
  "aroll_click_no_move": true,
  "click_dialogs": [],
  "xr_inspector_chars": 4997,
  "carousel": true,
  "slides": 5,
  "calendar": true,
  "unscheduled": 2,
  "page_errors": []
}
```

Durante esta prueba se detectó y corrigió una condición real de JOC/Amanda: los intros contienen A-roll alternativo para `source`, `voA` y `voB` en los mismos tiempos. V3 ahora muestra un selector de ruta y filtra el timeline por la ruta activa, de modo que los bloques alternativos no interceptan el click entre sí.

## Full JOC55 roundtrip

Los dos HTML completos fueron regenerados con las 45 fichas.

### JOC Classic

- bytes: 16,615,095
- embedded pieces: 45
- reimport pieces: 45
- IDs estables: PASS
- `sourceRanges` idénticos tras compile/reimport: PASS
- Cutter gate: READY
- críticos: 0
- warnings: 30

### Shadcn Studio V1

- bytes: 16,615,898
- embedded pieces: 45
- reimport pieces: 45
- IDs estables: PASS
- `sourceRanges` idénticos tras compile/reimport: PASS
- Cutter gate: READY
- críticos: 0
- warnings: 30

Los 30 warnings no son errores de rango: son avisos de que varias piezas de video del HTML original no llevan `source` explícito y requieren que el Cutter resuelva `DEFAULT/source group`. No hay `sourceRanges` invertidos ni ausentes en las piezas producibles verificadas por el gate.

## Sintaxis / empaquetado

PASS:

```text
node --check shared/lienzo_core.js
node --check app/app.js
python3 -m py_compile ABRXOS_GEOMETRA_V3.py geometra/*.py
bash -n RUN_GEOMETRA_V3.command
bash -n INSTALAR_ABRXOS_GEOMETRA_V3.command
```

El entorno de construcción no dispone de `zsh`; por eso la sintaxis de los `.command` se verificó con Bash. El shebang/uso objetivo sigue siendo zsh en macOS.

## Limitaciones deliberadas de V3.0

- VideoFlow / reproducción real / proxy / Virtual Cut: diferido.
- `cutOverrides` se registran para revisión futura; V3 no obliga al Cutter actual a modificar cortes automáticamente.
- Shadcn Studio V1 es un renderer standalone de lenguaje visual shadcn; no carga React/shadcn oficial desde CDN.
- El Kernel no hace IA generativa. Las fichas pueden copiarse a una IA externa y reimportarse.
