# ABRXOS GEOMETRA V3 · START HERE

Geometra V3 separa definitivamente **datos**, **lógica** y **frontend**.

```text
HTML / JSON / Lienzo anterior
            ↓
       GEOMETRA KERNEL
import · migrate · normalize · library · catalogs
            ↓
    ABRXOS DOCUMENT V3
            ↓
       RENDERER PACK
        ↙          ↘
 JOC Classic   Shadcn Studio V1
```

Una sola ficha/timeline puede exportarse en más de un Lienzo sin crear un segundo proyecto paralelo.

## Instalar en Mac

Descomprime la carpeta como:

```text
~/Downloads/ABRXOS_GEOMETRA_V3/
```

Ejecuta una sola vez:

```bash
zsh ~/Downloads/ABRXOS_GEOMETRA_V3/INSTALAR_ABRXOS_GEOMETRA_V3.command
```

Luego usa `ABRXOS Geometra V3.app` desde el Escritorio.

## Migración desde V2/V2.1

V3 usa:

```text
~/ABRXOS_GEOMETRA_DATA/library_v3.json
```

Si al primer arranque existe `library.json` de V2/V2.1 y todavía no existe `library_v3.json`, V3 copia y migra sus proyectos al esquema V3. El archivo anterior no se modifica.

## Crear un Lienzo

1. Importa un HTML/JSON con fichas.
2. Abre **Crear Lienzo**.
3. Selecciona fichas.
4. Escribe el nombre del Lienzo.
5. Elige Renderer:
   - `JOC Classic`
   - `Shadcn Studio V1`
6. Elige Light/Dark.
7. Exporta HTML.

Los dos renderers reciben el mismo documento canónico.

## Timeline: selección segura

- en intros/rutas múltiples aparece selector de ruta (`VO A`, `VO B`, `Entrevista original`, etc.) y sólo se dibuja una ruta a la vez; esto evita bloques alternativos superpuestos e imposibles de seleccionar;
- click = seleccionar y abrir inspector;
- mover menos de 6 px con mouse/pen sigue siendo selección;
- drag empieza después de 6 px;
- touch usa 10 px;
- handles izquierdo/derecho hacen trim;
- A-roll `locked_to_source` puede seleccionarse sin aviso;
- sólo un drag/trim real crea `editorialOverride`;
- `sourceRanges` del máster no se reescriben;
- el cambio queda también en `piece.cutOverrides[]` con `status=needs_review` para un Cutter futuro que decida consumirlo;
- Undo/Redo revierte el gesto completo.

## Inspector

Al seleccionar un bloque se ve su información interna. XR muestra definición, función, estados, assets y prompts. Imagen y SFX tienen edición directa. También existe JSON avanzado para campos nuevos/desconocidos.

## XR y SFX extensibles

Los catálogos base están en `catalogs/`. Si desde un Lienzo introduces un ID nuevo, por ejemplo `XR77`, V3 pide el nombre y crea una definición personalizada dentro de `document.extensions.xrDefinitions`. Lo mismo funciona para SFX custom. Un renderer viejo no se rompe: usa fallback genérico.

## Carruseles

Un carrusel no usa el editor de video. Abre un workspace de slides con preview, texto, visual y prompt editables.

## Calendario

Tanto Geometra como los Lienzos tienen mes + barra **Sin programar**. Se puede arrastrar una ficha al día y devolverla al lateral.

## Merge

Cada Lienzo incluye merge `LOCAL / REMOTE / BASE`. Los cambios no conflictivos se combinan; si ambos lados modificaron el mismo campo de manera distinta, se elige LOCAL o REMOTE.

## VideoFlow

No forma parte de V3.0. El objetivo primero es que ficha + inspector + timeline + calendario + carruseles sean estables. VideoFlow puede entrar luego como `player/timeline renderer` o capacidad del renderer, sin cambiar el Kernel.

## Shadcn Studio V1: qué significa en esta entrega

`Shadcn Studio V1` es un **renderer standalone de lenguaje visual shadcn**, sin CDN ni dependencia externa al abrir el HTML exportado. No incorpora todavía el runtime React/shadcn oficial dentro del Lienzo; esa sustitución puede hacerse más adelante sólo dentro del renderer porque el Kernel V3 ya está desacoplado.

Esto es deliberado: primero se estabiliza selección, timeline, inspector, calendarización, carruseles, merge y roundtrip. Después se puede promover un renderer React/shadcn real sin tocar importación, fichas, Cutter contract ni catálogos.
