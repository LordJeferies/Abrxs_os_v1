# SFX + MUSIC CANON R6

## SFX

Biblioteca pequeña y reutilizable. Repetir CLICK/WHOOSH/EMPHASIS es preferible a inventar diez sonidos diferentes porque existan diez eventos.

Familias iniciales:

- CLICK
- KEYBOARD
- WHOOSH
- CAMERA
- GOOD
- WRONG
- LOW_BOOM
- EMPHASIS
- SUSPENSE
- TENSION
- RISER
- IMPACT
- CLICK_DEEP

Cada evento SFX debe decir:

- libraryId;
- variante;
- trigger;
- propósito;
- placement temporal;
- start/end;
- mix/ducking;
- status.

El SFX no es obligatorio por XR ni por Motion.

## MUSIC

La IA no inventa una canción concreta. Describe:

- función musical;
- qué tipo de track buscar;
- cuándo subir;
- cuándo bajar;
- cuándo mutear;
- cuándo reanudar;
- por qué.

Automatizaciones:

- BASE
- SWELL
- DUCK
- MUTE
- RESUME
- FADE_IN
- FADE_OUT
