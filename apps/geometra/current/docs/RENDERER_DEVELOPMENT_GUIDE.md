# Renderer Development Guide

Un renderer es una proyección del mismo `abrxos.document.v3`.

## Regla

No importar/normalizar fichas dentro del renderer. No crear otro store de dominio. No renumerar IDs. No modificar `sourceRanges` por gestos de UI.

## Estructura

```text
renderers/my-renderer/
├── manifest.json
├── template.html
├── styles.css
└── adapter.js
```

Manifest mínimo:

```json
{
  "rendererId": "my-renderer",
  "name": "My Renderer",
  "version": "1.0.0",
  "documentSchema": "abrxos.document.v3",
  "entryTemplate": "template.html",
  "styles": "styles.css",
  "adapter": "adapter.js",
  "capabilities": {
    "video": true,
    "timeline": true,
    "calendar": true,
    "kanban": true,
    "carousel": true,
    "merge": true,
    "mobile": true
  },
  "themes": ["dark", "light"]
}
```

El compiler incrusta `styles.css`, `shared/lienzo_core.js`, `adapter.js` y `script#app-data` en un HTML standalone.

## Cómo evolucionar el frontend sin tocar Kernel

- Cambiar layout/color/componentes: renderer.
- Nuevo Player: renderer/capability.
- Nuevo Calendar: renderer.
- Dock panels: renderer.
- VideoFlow: renderer/capability.
- Cambiar qué significa una ficha o un sourceRange: Kernel/schema/migration.

## Gate

Antes de promover un renderer nuevo debe pasar: import real, compile, reimport, browser errors=0, timeline click/drag, XR inspector, carousel, calendar y responsive.
