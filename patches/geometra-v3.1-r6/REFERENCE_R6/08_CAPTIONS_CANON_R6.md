# CAPTIONS CANON R6

## Objetivo

El timeline no debe llenarse de palabras individuales. T9 representa **unidades semánticas de información**.

## Caption Group normal

- target: 8–15 palabras;
- soft range: 6–17 palabras cuando preservar sintaxis/sentido es mejor;
- no cruzar `partId`;
- no mezclar Hook con Desarrollo;
- una palabra a resaltar es opcional;
- el highlight normalmente debe existir literalmente en `sourceText`.

## HERO_WORD

Una sola palabra puede constituir el group/display cuando su fuerza editorial lo justifica.

Debe guardar:

- sourceContext;
- reason;
- highlightWord;
- `displayMode: hero_word`.

## Display Cues

Un Caption Group puede tener varios `displayCues` internos. Eso permite mostrar una frase en dos pasos o aislar una palabra fuerte sin crear tres cajas T9.

Ejemplo:

```text
GROUP
"Yo pensaba que todo esto era absolutamente imposible de lograr"

Cue 1: "Yo pensaba que todo esto"
Cue 2: "IMPOSIBLE" · hero_word
Cue 3: "de lograr"
```

El Timeline sigue mostrando un solo bloque GROUP.

## COMIC_CC

Captions se conservan pero:

```text
visibility = hidden
suppressedBy = XR_COMIC_CC_ID
```

El lector Story superior conserva el discurso continuo.

## COMIC_INFO

Caption policy AUTO porque el texto del cómic suele ser complementario y no necesariamente duplica la voz.

## Compatibilidad Geometra V2

Guardar `captionSchema: "abrxos.caption.v2"` y `captionPolicyVersion: "R6"`. El primer campo evita que Geometra V2 vuelva a microsegmentar un Caption Group ya construido; el segundo identifica que su política semántica es R6.
