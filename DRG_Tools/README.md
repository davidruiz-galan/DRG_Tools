# DRG Tools

**Digital Compositing Toolkit for Foundry Nuke**  
Created by **David Ruiz-Galán**.

DRG Tools is a scalable home for custom Nuke gizmos, Python UI tools, BlinkScript tools, icons and future compiled plug-ins. The suite has one installation and one release version, while individual tools can keep their own internal versions.

## Included in v0.1.0

### NodeInfo 1.3.0
Houdini-inspired node inspector. Hold **Alt + Middle Mouse Button** over a node to show a momentary inspector. Use **Alt + Shift + I** for the persistent inspector. The DRG > NodeInfo menu also contains Start, Reset and Stop Performance Timers, including **Stop Performance Timers / Restore Nodes**.

### Directional Dilate 1.0.0
A gizmo based on Nuke's FilterErode that behaves like a Dilate control while allowing **Both / Horizontal / Vertical** processing. It includes channels, filter and mix controls. Positive Size grows light pixels; negative Size erodes.

## Installation

1. Copy the **DRG_Tools** folder into your `.nuke` directory.
2. Add this line to your existing `.nuke/init.py`:

```python
nuke.pluginAddPath('DRG_Tools')
```

3. Restart Nuke.

You should then see:
- **DRG** in Nuke's top application menu.
- **DRG Tools** in the Nodes toolbar.
- NodeInfo's **Alt + MMB** inspector.

See `docs/INSTALL.md`, `docs/MIGRATION_FROM_NODEINFO.md` for more detail.

## Folder philosophy

- `python/drg_tools/` — Python UI / automation / shared code.
- `gizmos/` — `.gizmo` nodes.
- `icons/` — menu and tool icons.
- `docs/` — user documentation.
- Developer instructions are maintained in the source repository.

## Compatibility

Initial target: **Nuke / NukeX 17.x**, Windows. NodeInfo includes PySide6 with a PySide2 fallback.

## License

MIT License. See `LICENSE.txt`.

Release status: initial preview; interactive Nuke validation is pending.

[Instalación en español](docs/INSTALACION_ES.md)
