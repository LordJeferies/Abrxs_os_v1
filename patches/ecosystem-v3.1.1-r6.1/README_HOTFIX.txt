ABRXOS ECOSYSTEM HOTFIX V3.1.1 · R6.1
======================================

OBJETIVO
Cerrar la frontera entre Geometra V3.1 R6, Content Builder V1 y Brand Builder V1 sin reemplazar kernels, launchers, bibliotecas de usuario ni Cutter.

RESULTADO
- Geometra: 3.1.0 R6 → 3.1.1 R6.1
- Content Builder: 1.0.0 → 1.0.1
- Brand Builder: 1.0.0 → 1.0.1

NO CREA OTRA APP.
La misma ABRXOS Geometra V3.app sigue lanzando ~/ABRXOS_GEOMETRA_V3.
Las dos Builders conservan sus instaladores/apps actuales.

QUÉ ACTUALIZA

1. GEOMETRA 3.1.1 R6.1
   - Source Alignment / microtrim validation.
   - VO_ADDED placement/recording inspector.
   - shortSourceException en Caption Groups.
   - route semantics R6.1.
   - Production Checklist R6.1: sourceAlignment, microtrim, voRecording.
   - tercer gate independiente: Projection Ready.
   - Projection Ready verifica T3/T4/T7 cuando recursos internos necesitan proyección editable.
   - Alpha Ready y Cutter Ready no cambian de significado.
   - NO cambia Kernel, Library, canonicalId, sourceRanges ni Cutter.

2. CONTENT BUILDER 1.0.1
   - conserva R6 como baseline estable;
   - añade delta R6.1 al AI Package;
   - Source Alignment antes de sourceRanges finales;
   - microtrim anchors explícitos;
   - VO_ADDED sin sourceRange falso;
   - routeSemantics R6.1;
   - projection contract T1–T9;
   - contract_manifest.json con canonFamily/canonRevision/features;
   - hashes SHA-256 de las 7 librerías R6 compartidas.

3. BRAND BUILDER 1.0.1
   - no cambia UI, 5 Drivers, 25 Tools ni Branding Method;
   - mantiene Branding Method y Brand Adapter como capas separadas;
   - añade handshake canonFamily=R6 / canonRevision=R6.1;
   - verifica Brand Adapter schema abrxos.brand-adapter.r6 / adapterVersion R6.1.

4. RELEASE ENGINEERING
   - fixtures autocontenidas;
   - tests sin rutas absolutas de la máquina de build;
   - PACKAGE_MANIFEST limpio, sin .pytest_cache/__pycache__/*.pyc;
   - verificación cross-app de hashes;
   - aplicación + verificación + rollback automático si la verificación posterior falla.

REQUISITO OBLIGATORIO
Geometra debe tener YA aplicado ABRXOS_PATCH_GEOMETRA_V3_1_R6.
El hotfix verifica:
- versión 3.1.x;
- registry .abrxos_patches/ABRXOS_GEOMETRA_V3_1_R6.json;
- las siete librerías R6 base.
Si falta algo, BLOQUEA ANTES de modificar archivos.

BUILDERS
Son opcionales.
- instalada → se actualiza y verifica;
- no instalada → SKIPPED_MISSING;
- Geometra puede actualizarse igualmente.

DATOS PROTEGIDOS
NO se modifican:
~/ABRXOS_GEOMETRA_DATA/
~/ABRXOS_CONTENT_BUILDER_DATA/
~/ABRXOS_CONTENT_BUILDER_EXPORTS/
~/ABRXOS_BRAND_BUILDER_DATA/
~/ABRXOS_BRAND_BUILDER_EXPORTS/

BACKUPS
~/ABRXOS_ECOSYSTEM_HOTFIX_BACKUPS/

INSTALACIÓN
1. Descomprime el ZIP.
2. Cierra Geometra/Builders si están abiertas.
3. En Terminal:

zsh "/ruta/ABRXOS_HOTFIX_ECOSYSTEM_V3_1_1_R6_1/APLICAR_HOTFIX.command"

También puedes escribir `zsh `, arrastrar APLICAR_HOTFIX.command y pulsar Enter.

APLICAR_HOTFIX.command ahora es ATÓMICO:
PRECHECK → BACKUPS → PATCH → VERIFY CROSS-APP.
Si VERIFY falla, restaura automáticamente el backup y devuelve error.

VERIFICAR
zsh "/ruta/ABRXOS_HOTFIX_ECOSYSTEM_V3_1_1_R6_1/VERIFICAR_HOTFIX.command"

Debe devolver `"ok": true` y checks como:
- geometra_r61_validator=PASS
- contentBuilder_canon_handshake=PASS
- content_geometra_library_hashes=PASS
- brandBuilder_canon_handshake=PASS
- brand_adapter_contract=PASS

REVERTIR
zsh "/ruta/ABRXOS_HOTFIX_ECOSYSTEM_V3_1_1_R6_1/REVERTIR_HOTFIX.command"

Revierte los archivos de código/versiones del último backup. Los datos de usuario no participan.

LOS 3 GATES
Alpha Ready     = ficha editorial/productivamente desarrollada.
Cutter Ready    = sourceRanges permiten saber qué cortar.
Projection Ready= recursos temporales internos que deben manipularse tienen proyección correcta en T1–T9.

EJEMPLO LEGACY R6
Una ficha R6 puede seguir:
Alpha READY
Cutter READY
Projection REVIEW
porque sus assets viven anidados dentro de XR pero todavía no tienen bloques T3 independientes.
Esto NO la migra ni la rompe.

EJEMPLO R6.1 AMANDA
El fixture real conserva 25 sourceAlignment nodes, 16 microtrims y 2 VO_ADDED.
Projection Ready puede ser READY aunque Alpha/Cutter sigan REVIEW mientras falten sourceRanges finales o campos R6 requeridos. Los tres gates son independientes por diseño.
