# ABRXOS MASTER CANON R6

## 1. Una ficha = una pieza final

Hook, desarrollo, rehook, cierre y demás partes pertenecen a una sola ficha cuando forman un solo video final.

## 2. Dos relojes separados

- `sourceRanges[].start/end`: tiempo absoluto del MASTER; lo usa Cutter.
- `timeline[].start/end`: tiempo relativo dentro de la pieza montada; lo usa el Lienzo.

Mover XR, imagen, Motion, SFX, CINE o Caption no autoriza a cambiar `sourceRanges`.

## 3. Tracks T1–T9

```text
T9 CAPTIONS
T8 MUSIC
T7 SFX
T6 VO
T5 B-ROLL / CINE
T4 MOTION
T3 IMAGES / OBJECTS
T2 XR
T1 A-ROLL
```

`story/parts` es una capa narrativa de lectura/inspección y puede mostrarse como una fila adicional en el Lienzo, pero no sustituye T1–T9.

## 4. Familias XR R6

- `COMIC_INFO`
- `COMIC_CC`
- `TYPO`
- `PHOTOS`
- `OBJECTS`
- `PHOTO_OBJECT`
- `NO_XR`

Los XR son conceptos visuales. Images, Motion y SFX permanecen como objetos independientes en sus tracks.

## 5. CINE Beats

No se crea T10. Los CINE beats se representan sobre las pistas actuales:

- T5: evento `type: cine`;
- T4: Motion de entrada/salida/hold;
- T7: SFX opcional;
- T8: automatización musical/silencio;
- T9: caption visible/oculto según el beat.

Canon inicial:

- `CINE01_BLACK_HOLD`
- `CINE02_FREEZE_HOLD`
- `CINE03_PUNCH_CUT`

## 6. Perfiles de edición

- `XR_FULL` · **Cinematic Edit**
- `MOTION_SFX` · **Dynamic Edit**
- `SFX_ONLY` · **Clean Edit**

El perfil limita/autoriza recursos; no obliga a usar efectos si el beat no los necesita.

## 7. Densidad XR cuando el perfil es XR_FULL

- Intro: 6 XR.
- Clip vertical: 2–4 XR.
- Clip horizontal: aproximadamente 1 XR cada 2 minutos.
- Episodio completo: aproximadamente 1 XR cada 5 minutos.

En horizontal/podcast la densidad es guía, no una cuota que deba empeorar la narración.

## 8. Diversidad XR

Prioridad:

1. función narrativa;
2. adecuación visual;
3. diversidad;
4. repetición.

Regla fuerte: evitar dos XR de la misma familia consecutivos. Preferir recorrer familias diferentes antes de repetir, excepto cuando repetir sea claramente la mejor traducción visual del beat.

## 9. Captions

El timeline T9 muestra **Caption Groups semánticos**, no palabras sueltas ni cientos de microcajas.

- objetivo normal: 8–15 palabras por group;
- soft range: 6–17 palabras;
- un `HERO_WORD` puede tener una sola palabra cuando existe justificación editorial;
- nunca mezclar `partId` diferentes;
- cada group puede tener `highlightWord` opcional;
- dentro del group pueden existir `displayCues` internos sin multiplicar bloques en el timeline.

## 10. COMIC_CC y captions

`COMIC_CC` integra el texto hablado dentro de las imágenes. Durante ese intervalo:

- T9 se conserva estructuralmente;
- `visibility: hidden`;
- `suppressedBy: <XR_ID>`;
- el lector/Story superior continúa mostrando el discurso completo.

## 11. Estado editorial y operativo

Madurez:

- BETA
- ALFA
- OMEGA

Workflow:

- PENDIENTE
- REVISADO
- HACIENDO
- LISTO
- PROGRAMADO
- PUBLICADO

No son la misma cosa.

## 12. Alfa completa

Una Alfa no significa “mucho texto”. Significa que otra persona puede producir la pieza sin tener que adivinar decisiones críticas.
