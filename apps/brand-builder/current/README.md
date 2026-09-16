# ABRXOS X · Brand Builder V1

App local para preparar paquetes de marca para una IA externa. Separa `Branding Method` (estrategia/ADN) de `Brand Adapter R6` (contrato operativo para contenido y producción).

## Modos de entrada

- Texto libre / Raw Context.
- Formulario general.
- Resumen de 5 Drivers.
- Expansión opcional de las 25 tools.
- Edición visual + JSON avanzado del Brand Adapter.
- Referencias locales.

## Export

`Build AI Package` crea una carpeta y un ZIP en `~/ABRXOS_BRAND_BUILDER_EXPORTS/` con prompt, raw context, method input, adapter template, draft y manifest SHA256.

## Instalación

Ejecuta `INSTALAR_ABRXOS_X_BRAND_BUILDER_V1.command`. El instalador detecta Python 3, copia la app a `~/Applications/ABRXOS/` y crea `ABRXOS X Brand Builder.app` en el Escritorio.

## Standalone HTML

`ABRXOS_X_BRAND_BUILDER_V1.html` funciona directamente en navegador con `localStorage`. En ese modo no puede crear carpetas del sistema; descarga proyecto/prompt en su lugar.
