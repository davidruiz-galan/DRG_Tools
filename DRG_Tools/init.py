# -*- coding: utf-8 -*-
"""DRG Tools startup paths.

Created by David Ruiz-Galán.
Keep UI/menu code in menu.py; init.py only configures paths.
"""

import os
import nuke

_ROOT = os.path.dirname(os.path.abspath(__file__))

# Centralized paths for all present and future DRG tool types.
for _folder in ("python", "gizmos", "icons"):
    _path = os.path.join(_ROOT, _folder)
    if os.path.isdir(_path):
        nuke.pluginAddPath(_path)
