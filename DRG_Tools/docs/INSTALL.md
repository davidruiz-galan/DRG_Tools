# Installing DRG Tools

## Windows / Nuke 17.x

Copy the folder:

`DRG_Tools`

into:

`C:\Users\YOUR_USER\.nuke\DRG_Tools`

Then open your existing `.nuke/init.py` and add:

```python
import nuke
nuke.pluginAddPath('DRG_Tools')
```

If `init.py` already imports Nuke, only the `pluginAddPath` line is needed.

Restart Nuke. Do not copy the internal Python, gizmo or icon files into separate locations; the suite's own `init.py` registers those subfolders.

## Verify the installation

In Nuke, confirm:

1. The **DRG** menu appears at the top.
2. `Nodes > DRG Tools > Filter > Directional Dilate` exists.
3. Alt + MMB over a node opens NodeInfo while the buttons are held.

## Updating

Replace the old `DRG_Tools` folder with the newer release folder while preserving any personal work outside the suite directory. The user's `.nuke/init.py` line stays the same.

## Existing standalone NodeInfo users

If you already have the old standalone NodeInfo installed, follow `MIGRATION_FROM_NODEINFO.md` first so NodeInfo is not loaded twice.
