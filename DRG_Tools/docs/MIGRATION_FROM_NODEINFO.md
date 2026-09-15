# Migrating from standalone NodeInfo

If you already installed NodeInfo v1.x separately, disable the old standalone copy before enabling DRG Tools. Otherwise Nuke may load NodeInfo twice, create duplicate menus, or install two Alt+MMB event filters.

## Remove / disable the old startup entries

From your existing `.nuke/menu.py`, remove the old block that looks like:

```python
import nodeinfo

if nuke.GUI:
    nodeinfo.install()
    menu = nuke.menu('Nuke').addMenu('NodeInfo')
    ...
```

From your existing `.nuke/init.py`, remove any old NodeInfo-only path such as:

```python
nuke.pluginAddPath('NodeInfo_DRG')
# or
nuke.pluginAddPath('NodeInfo')
```

You can then delete or archive the old standalone `nodeinfo.py` / `NodeInfo_DRG` folder.

## Enable the unified suite

Keep only:

```python
nuke.pluginAddPath('DRG_Tools')
```

The unified DRG Tools package installs NodeInfo itself and exposes its commands under `DRG > NodeInfo`.
