# Instalar DRG Tools

1. Cierra Nuke y descomprime el ZIP.
2. Copia la carpeta `DRG_Tools` completa a `C:\Users\TU_USUARIO\.nuke`.
3. Abre el `init.py` que ya tengas en `.nuke`; si no existe, crea un archivo de texto con ese nombre, sin extensión .txt.
4. Añade una sola vez:

```python
import nuke
nuke.pluginAddPath('DRG_Tools')
```

5. Reinicia Nuke. Verás el menú DRG y Nodes > DRG Tools > Filter > Directional Dilate.

No sustituyas el init.py ni el menu.py del usuario por los archivos internos del paquete. Si ya usabas NodeInfo independiente, desactiva sus entradas antiguas siguiendo MIGRATION_FROM_NODEINFO.md.

## Actualizar

Con Nuke cerrado, conserva una copia de la carpeta anterior fuera de las rutas de plugins y reemplaza DRG_Tools por la nueva. El registro inicial no cambia. Guarda tus herramientas personales fuera del paquete distribuido.

## Desinstalar

Con Nuke cerrado, elimina únicamente la línea que registra DRG_Tools y retira su carpeta. Conserva una copia si tienes composiciones que usan sus gizmos.

## Comprobación

Prueba Alt + botón central, Alt + Shift + I y crea Directional Dilate. El inspector no inicia automáticamente los temporizadores. Stop Performance Timers / Restore Nodes detiene el profiling activado manualmente.

Versión inicial dirigida a Nuke / NukeX 17.x en Windows; validación interactiva pendiente.
