# DRG Tools

![DRG Tools](DRG_Tools/icons/DRG_logo.png)

Digital compositing toolkit for Foundry Nuke by **David Ruiz-Galán**.

## Included tools

- **NodeInfo 1.3.0**: hold Alt + middle mouse button over a node for a momentary inspector; Alt + Shift + I opens the persistent inspector. Profiling controls are available in the DRG menu.
- **Directional Dilate 1.0.0**: horizontal, vertical or both-axis dilation/erosion with channels, filter and mix controls.

## Install

Download `DRG_Tools_v0.1.0.zip` from this repository's Releases section. Extract and copy its **DRG_Tools** folder to your `.nuke` folder. Add the following to your existing `.nuke/init.py` (create the file if absent):

```python
import nuke
nuke.pluginAddPath('DRG_Tools')
```

Restart Nuke. Do not replace your existing init.py or menu.py. Only register the suite once. If you download GitHub's source archive instead, copy the inner `DRG_Tools` folder containing `init.py` and `menu.py`.

[Detailed installation](DRG_Tools/docs/INSTALL.md) · [Español](DRG_Tools/docs/INSTALACION_ES.md) · [Migration from standalone NodeInfo](DRG_Tools/docs/MIGRATION_FROM_NODEINFO.md)

## Compatibility and status

Initial target: Nuke / NukeX 17.x on Windows. Version 0.1.0 is an initial preview. Packaging and Python syntax are checked; interactive behavior and rendering still require validation inside Nuke. PySide2 fallback is present but older Nuke versions are not certified.

## Development

Edit only `DRG_Tools/` for runtime code and assets. See [adding tools](dev/ADD_NEW_TOOL.md), [release checklist](dev/RELEASE_CHECKLIST.md) and [publishing](dev/PUBLISHING.md).

Build a clean distribution with Python 3.11 or newer:

```text
python scripts/build_release.py
```

This creates `dist/DRG_Tools_v0.1.0.zip` and its SHA-256 checksum. Attach these to a GitHub Release and use the same ZIP on Nukepedia. Do not commit dist/ or local backups.

## Support

Report issues in this repository with your Nuke version, operating system, reproduction steps and any traceback. Remove confidential project information before attaching examples.

## License

MIT. See [LICENSE.txt](LICENSE.txt) and [NOTICE.txt](NOTICE.txt).
