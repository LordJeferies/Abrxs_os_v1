# GEOMETRA / LIENZO · UI PATCH SPEC R6

Para aprovechar visualmente todo el canon R6, la próxima revisión de Geometra/Lienzo debe:

## Caption Groups
- T9 muestra un bloque por `caption_group`.
- Inspector muestra sourceText, wordCount, highlightWord, displayMode, visibility, suppressedBy y displayCues.
- Reemplazar cualquier acción “3–5 palabras” por agrupación R6 8–15 / soft 6–17.
- Si visibility=hidden, mostrar el bloque atenuado, no borrarlo.

## CINE
- Eventos `track=broll`, `type=cine` deben abrir inspector CINE, no inspector B-roll genérico.
- Mostrar cineType, función, visual, Motion relacionado, SFX, music automation, silence y caption policy.

## Edit Profile
- Mostrar nombre comercial + código interno:
  - Cinematic Edit · XR_FULL
  - Dynamic Edit · MOTION_SFX
  - Clean Edit · SFX_ONLY

## Assets R6
Inspector de Images/Objects debe mostrar:
- contextAndDetail
- whatIsVisible
- whyItMatchesSpeech
- prompt
- brollReference
- googleSearchQuery
- placementRecommendation
- placementReason
- emojiFallback cuando aplique
- duration/status

## XR
Inspector debe reconocer las familias R6 y validar sus reglas de assetCount/states.

## Calendar / Kanban
No cambia la estructura actual: usa workflowStatus + schedule.
