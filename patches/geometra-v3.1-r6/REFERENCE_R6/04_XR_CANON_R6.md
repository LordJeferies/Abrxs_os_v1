# XR CANON R6

## COMIC_INFO

**Assets:** 1 imagen maestra.  
**Duración total:** 12–20 s.  
**Texto:** información editorial/complementaria por defecto.  
**Caption policy:** AUTO.

La composición debe poder leerse en cinco vistas:

1. inferior izquierda;
2. inferior derecha;
3. superior izquierda;
4. superior derecha;
5. zoom out / composición completa, revelando también el elemento central más importante.

No son cinco imágenes. Es una imagen rica recorrida mediante Motion.

## COMIC_CC

**Assets:** 3 imágenes.  
**Duración:** 2–4 s por imagen.  
**Encuadres:**

1. A01 = plano amplio;
2. A02 = close-up;
3. A03 = plano medio.

El texto integrado en cada imagen representa lo que se está diciendo durante su intervalo. No usar burbujas de cómic. El texto debe formar parte de la composición.

**Caption policy:** HIDE. Los Caption Groups se conservan estructuralmente, pero se ocultan visualmente durante el XR.

## TYPO

**Assets raster:** 0.  
**Duración total:** 6–12 s.  
**Fondo:** plano/simple/brand/dark.

Tres estados:

1. frase normal;
2. palabra o frase fuerte de 1–5 palabras en pantalla completa;
3. frase normal de salida/resolución.

## PHOTOS

**Assets:** 3 fotografías distintas.  
**Duración total:** 6–12 s.  
**Orden:**

1. A01 = close-up;
2. A02 = plano amplio;
3. A03 = close-up.

Cada foto debe tener prompt, referencia de búsqueda, contexto, detalle, relación con la frase, placement recomendado, duración, Motion y SFX opcional.

## OBJECTS

**Assets:** 3 objetos.  
**Duración total:** 6–12 s.

Cada objeto debe declarar:

- objeto;
- `placementRecommendation`: foreground/background;
- razón del placement;
- dos emojis fallback;
- prompt si se genera PNG/objeto;
- B-roll/search reference;
- Motion;
- SFX opcional.

Los emojis pueden sustituir el objeto si no se produce o si funcionan mejor editorialmente.

## PHOTO_OBJECT

**Assets:** 3 en total.  
**Duración total:** 8–12 s.

- A01 = fotografía de fondo.
- A02 = objeto frontal.
- A03 = objeto frontal.

La foto contextualiza; los objetos enfatizan conceptos concretos.

## NO_XR

No significa “sin edición”. Puede tener:

- A-roll;
- zoom/pan/slow drift;
- transición;
- SFX;
- Music automation;
- Captions;
- CINE beat.
