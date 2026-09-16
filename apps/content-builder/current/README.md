# ABRXOS Content Builder V1

App local que transforma una intención editorial + inputs en el paquete exacto que debes subir a ChatGPT/otra IA para obtener fichas ABRXOS R6.

## Casos incluidos

Plan fijo, transcripción a Intro/Vertical/Horizontal/estáticos, Betas, Beta→Alfa, actualización de Alfa, Dynamic Edit sin XR, Clean Edit, episodio completo, multi-source, plan sin timestamps y proyecto completo.

## Export

`Build AI Package` selecciona el prompt y ficha R6 pinneados, añade transcripción, plan, Project Config, Brand Adapter y canon, y exporta carpeta + ZIP con manifest SHA256 en `~/ABRXOS_CONTENT_BUILDER_EXPORTS/`.

## Instalación

Ejecuta `INSTALAR_ABRXOS_CONTENT_BUILDER_V1.command`. Se instala en `~/Applications/ABRXOS/` y crea `ABRXOS Content Builder.app` en el Escritorio.

## Standalone HTML

`ABRXOS_CONTENT_BUILDER_V1.html` funciona directamente con `localStorage`. La exportación completa de carpetas/ZIP requiere abrirlo mediante `app.py` o la `.app` instalada.
