# -*- coding: utf-8 -*-
"""Small creation helpers used by DRG Tools menus."""

import nuke


def create_directional_dilate():
    """Create the DRG Directional Dilate gizmo in the current Node Graph."""
    return nuke.createNode("DRG_DirectionalDilate")
