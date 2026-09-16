ABRXOS · RESTAURAR DESDE GITHUB / MAC NUEVA

OBJETIVO
El repo sólo se vuelve una copia reinstalable completa DESPUÉS de capturar una vez la instalación real 3.1.1/1.0.1/1.0.1 de la Mac fuente.

PRIMERA VEZ EN LA MAC FUENTE
1. Ejecutar:
   zsh tools/DEJAR_REPO_LISTO.command

Eso ejecuta CAPTURAR_INSTALACION_ACTUAL.command y llena:
   apps/geometra/current
   apps/content-builder/current
   apps/brand-builder/current

2. Confirmar VERIFY_ALL PASS.
3. Commit/push del snapshot a GitHub.

MAC NUEVA / REINSTALACIÓN
Prerequisito: Python 3 instalado.

Después de clonar el repo:
   zsh install/INSTALAR_ECOSISTEMA_DESDE_CERO.command

El instalador usa directamente apps/*/current. No requiere volver a aplicar el patch R6 ni el hotfix R6.1 porque esos cambios ya están contenidos en los snapshots current.

NO SE GUARDAN EN GIT
~/ABRXOS_GEOMETRA_DATA
~/ABRXOS_CONTENT_BUILDER_DATA
~/ABRXOS_CONTENT_BUILDER_EXPORTS
~/ABRXOS_BRAND_BUILDER_DATA
~/ABRXOS_BRAND_BUILDER_EXPORTS

Los datos de trabajo se respaldan por separado. El repo reproduce el software, no tus datos privados de proyectos/clientes.

SI apps/geometra/current sólo contiene README_CAPTURE_REQUIRED.txt y VERSION_EXPECTED.json, el repo todavía NO está listo para restaurar Geometra. Ejecuta la captura en la Mac fuente antes de hacer el commit definitivo.
