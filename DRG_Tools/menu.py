# -*- coding: utf-8 -*-
"""DRG Tools interactive menus for Foundry Nuke."""

import nuke
from drg_tools import config
from drg_tools import nodeinfo
from drg_tools import tools
from drg_tools import about

if nuke.GUI:
    # Global NodeInfo event filter: Alt + MMB while held.
    nodeinfo.install()

    # ------------------------------------------------------------------
    # Main application menu: utilities, profiling controls and About.
    # ------------------------------------------------------------------
    drg = nuke.menu("Nuke").addMenu("DRG", icon="DRG_32.png")

    nodeinfo_menu = drg.addMenu("NodeInfo", icon="DRG_NodeInfo_32.png")
    nodeinfo_menu.addCommand(
        "Inspect Selected Node",
        nodeinfo.show_selected,
        "Alt+Shift+I",
        icon="DRG_NodeInfo_32.png",
        tooltip="Open the persistent NodeInfo inspector for the selected node."
    )
    nodeinfo_menu.addSeparator()
    nodeinfo_menu.addCommand(
        "Start Performance Timers",
        nuke.startPerformanceTimers,
        tooltip="Start Nuke native performance profiling. This also shows Nuke native DAG timing labels."
    )
    nodeinfo_menu.addCommand(
        "Reset Performance Timers",
        nuke.resetPerformanceTimers,
        tooltip="Reset Nuke performance profiling counters."
    )
    nodeinfo_menu.addCommand(
        "Stop Performance Timers / Restore Nodes",
        nuke.stopPerformanceTimers,
        tooltip="Stop Nuke native profiling and restore the normal Node Graph appearance."
    )
    advanced = nodeinfo_menu.addMenu("Advanced")
    advanced.addCommand("Show Nuke Native Profiler", nodeinfo.show_native_profiler)
    advanced.addCommand("Hide Nuke Native Profiler", nodeinfo.hide_native_profiler)
    advanced.addCommand("Reset Profiling Data", nodeinfo.reset_native_profiler)
    nodeinfo_menu.addSeparator()
    nodeinfo_menu.addCommand("About NodeInfo…", nodeinfo.show_about, icon="DRG_NodeInfo_32.png")

    drg.addSeparator()
    drg.addCommand(
        "Create Directional Dilate",
        tools.create_directional_dilate,
        icon="DRG_DirectionalDilate.png",
        tooltip="Create DRG Directional Dilate."
    )
    drg.addSeparator()
    drg.addCommand("About DRG Tools…", about.show, icon="DRG_32.png")

    # ------------------------------------------------------------------
    # Nodes toolbar: scalable home for image-processing nodes/gizmos.
    # ------------------------------------------------------------------
    nodes = nuke.menu("Nodes")
    drg_nodes = nodes.addMenu("DRG Tools", icon="DRG_32.png")
    filter_menu = drg_nodes.addMenu("Filter")
    filter_menu.addCommand(
        "Directional Dilate",
        tools.create_directional_dilate,
        icon="DRG_DirectionalDilate.png"
    )
