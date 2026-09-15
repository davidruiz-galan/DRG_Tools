# Publicar DRG Tools

## Fuente única

Esta carpeta de repositorio es la única fuente editable. No edites los ZIP ni el archivo histórico. Para añadir herramientas consulta ADD_NEW_TOOL.md; actualiza también manifest.json, VERSION, config.py y CHANGELOG.md cuando cambie la versión.

## GitHub

1. Crea un repositorio llamado DRG_Tools en tu cuenta.
2. Sube el contenido de esta carpeta: README.md, LICENSE.txt, NOTICE.txt, .gitignore, .gitattributes, DRG_Tools/, dev/ y scripts/.
3. Completa las pruebas de RELEASE_CHECKLIST.md en Nuke y registra el resultado.
4. Ejecuta `python scripts/build_release.py`.
5. Crea una Release con etiqueta v0.1.0 y adjunta los archivos ZIP y SHA256 de dist/.
6. Mientras falten pruebas en Nuke, marca la Release como pre-release y conserva el aviso de validación pendiente.

No subas las carpetas locales 02_PUBLICAR ni 99_ARCHIVO al repositorio. GitHub puede generar un ZIP del código fuente; el ZIP de Release contiene directamente la carpeta instalable.

## Nukepedia

Publica una sola ficha de DRG Tools con las dos herramientas. Usa el mismo ZIP que en GitHub Releases, el texto preparado en 02_PUBLICAR y el enlace real de tu repositorio cuando exista. Selecciona la categoría que corresponda en el formulario vigente; no se ha confirmado una categoría específica para suites mixtas.

Los campos y límites de carga deben comprobarse en el formulario autenticado actual. Incluye capturas reales de NodeInfo y Directional Dilate antes de publicar. No anuncies compatibilidad que no hayas probado.

Referencia de instalación: https://www.nukepedia.com/knowledge/general-tutorials/getting-started-with-nuke-plugins/
