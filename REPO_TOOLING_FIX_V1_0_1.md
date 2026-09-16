# Repo Tooling Fix 1.0.1

## Root cause corregida

En zsh, `path` es un parámetro especial ligado a `PATH`. El script inicial de captura usaba una variable local llamada `path` al descomponer `name:path:version`, lo que sobrescribía el PATH y hacía que `/usr/bin/env python3` fallara aunque Python estuviera correctamente instalado.

## Cambios

- `path` renombrado a `install_path` en captura.
- Resolver compartido `tools/lib/python_resolver.zsh`.
- Tools críticos llaman al Python resuelto por ruta absoluta.
- `ACTUALIZAR_REPO_DESDE_MAC.command` usa zsh, no bash, para scripts zsh.
- `tools/DEJAR_REPO_LISTO.command` hace captura + verify + manifest + check de instaladores.
- Wrappers de instalación Brand/Content ahora instalan desde `apps/*/current`.
- Nuevo `install/INSTALAR_ECOSISTEMA_DESDE_CERO.command` reconstruye las tres apps desde snapshots current.
- Documentación de restore desde GitHub.

## Invariantes

No cambia Geometra, Content Builder, Brand Builder, R6/R6.1, sourceRanges, libraries ni datos de usuario. Es una reparación de tooling/reproducibilidad del repositorio.
