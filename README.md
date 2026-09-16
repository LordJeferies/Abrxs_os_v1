# ABRXOS Ecosystem · Geometra + Content Builder + Brand Builder

Repositorio de desarrollo, documentación, canon, pruebas y release history del ecosistema ABRXOS.

## Apps actuales

| App | Versión | Canon | Rol |
|---|---:|---|---|
| ABRXOS Geometra | 3.1.1 | R6 / R6.1 | Biblioteca canónica, Lienzos, Kanban, Calendar, validator, compiler |
| ABRXOS Content Builder | 1.0.1 | R6 / R6.1 | Construye paquetes para IA a partir de planes, transcripciones y fichas |
| ABRXOS X Brand Builder | 1.0.1 | R6 / R6.1 | Construye estrategia/Brand Adapter y handoff hacia Content Builder |

## Regla de arquitectura

Una sola fuente de verdad. Las Builders preparan contratos; Geometra importa/normaliza/administra; los Lienzos proyectan y editan el mismo documento. Ninguna UI crea un proyecto paralelo.

## Antes de hacer push

En la Mac con las apps instaladas y verificadas:

```bash
zsh tools/CAPTURAR_INSTALACION_ACTUAL.command
zsh tools/VERIFY_ALL.command
zsh tools/GENERAR_MANIFEST.command
```

Después revisa `git diff` y sólo entonces commit/tag.

## Política recomendada

Este repo debe empezar como **privado**. No contiene intencionalmente data directories, proyectos de clientes ni exports. Si algún día se hace público, revisar además licencias, ejemplos y referencias de marca.

## Estructura

```text
apps/        snapshots de código actual por app
canon/       R6 baseline + R6.1 supplements
patches/     patches/hotfixes reversibles
releases/    artefactos binarios/versionados
resources/   recursos compartidos no sensibles
docs/        arquitectura, reparación, evolución y GitHub
tutorials/   uso por escenario
tools/       captura, verificación, manifests y helpers
install/     instaladores de referencia
references/  material legado/documentación histórica
```
