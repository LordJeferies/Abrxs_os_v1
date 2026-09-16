ABRXOS PATCH · GEOMETRA V3.1 R6
================================

QUÉ HACE
Actualiza la instalación existente ~/ABRXOS_GEOMETRA_V3 para añadir compatibilidad R6, validación Alfa/Cutter, Kanban drag & drop en Geometra, inspector R6 del Lienzo, Caption Groups, CINE, Edit Profiles y Production Checklist.

NO CREA OTRA APP
La misma "ABRXOS Geometra V3.app" del Escritorio continúa siendo el lanzador. Al reiniciarla, carga el código actualizado.

DATOS
El parche NO modifica ~/ABRXOS_GEOMETRA_DATA. Los proyectos y library_v3.json quedan fuera del payload y del rollback.

INSTALAR
1. Cierra Geometra si está abierto (el script también detiene el proceso local si lo detecta).
2. Deja esta carpeta en Descargas.
3. Ejecuta una sola vez:
   zsh ~/Downloads/ABRXOS_PATCH_GEOMETRA_V3_1_R6/APLICAR_PATCH.command
4. El script hace backup, aplica, verifica y abre la misma .app.
5. Si la verificación falla, intenta REVERTIR automáticamente antes de salir.

VERIFICAR SIN CAMBIAR NADA
   zsh ~/Downloads/ABRXOS_PATCH_GEOMETRA_V3_1_R6/VERIFICAR_PATCH.command

ROLLBACK MANUAL
   zsh ~/Downloads/ABRXOS_PATCH_GEOMETRA_V3_1_R6/REVERTIR_PATCH.command

BACKUPS
Por defecto quedan en:
~/ABRXOS_GEOMETRA_PATCH_BACKUPS/

OVERRIDE PARA PRUEBAS
ABRXOS_GEOMETRA_TARGET=/otra/ruta/ABRXOS_GEOMETRA_V3
ABRXOS_GEOMETRA_PATCH_BACKUPS=/otra/ruta/backups

COMPATIBILIDAD
El patch está diseñado para Kernel Geometra 3.x con los anchors de la entrega V3. Si esos anchors no existen, APLICAR_PATCH falla y restaura los archivos tocados en vez de adivinar una reescritura.

R6 + LEGACY
No remapea automáticamente XR00–XR09. Los documentos legacy se conservan; los documentos R6 pueden usar COMIC_INFO, COMIC_CC, TYPO, PHOTOS, OBJECTS, PHOTO_OBJECT y NO_XR.
