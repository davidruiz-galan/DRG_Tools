# -*- coding: utf-8 -*-
"""NodeInfo for Foundry Nuke 17.x / NukeX.

Created by David Ruiz-Galán.
Copyright (c) 2026 David Ruiz-Galán.
Licensed under the MIT License. See LICENSE.txt in the distribution package.

Alt + Middle Mouse Button over a node -> Houdini-style node information popup.
"""

from __future__ import annotations

import math
import os
import sys
import traceback

import nuke

from . import config
from .paths import icon_path

try:
    from PySide6 import QtCore, QtGui, QtWidgets
except ImportError:
    from PySide2 import QtCore, QtGui, QtWidgets  # fallback for older Nuke

try:
    from nuke import memory2 as nuke_memory
except Exception:
    nuke_memory = None

__version__ = config.NODEINFO_VERSION
__author__ = config.AUTHOR
__copyright__ = config.COPYRIGHT
__license__ = config.LICENSE
__product__ = "NodeInfo"

# -----------------------------------------------------------------------------
# Configuration
# -----------------------------------------------------------------------------
LIGHT_MAX = 0.15      # <= 15% of the slowest profiled node
MEDIUM_MAX = 0.50     # <= 50% of the slowest profiled node

COLORS = {
    "LIGHT": "#45C878",
    "MEDIUM": "#F4A742",
    "HEAVY": "#E45B5B",
    "IDLE": "#8B949E",
}

_popup = None
_filter = None


def _safe_call(func, default=None):
    try:
        return func()
    except Exception:
        return default


def _fmt_time_us(value):
    try:
        us = float(value or 0)
    except Exception:
        us = 0.0
    if us < 1000.0:
        return "%.1f us" % us
    ms = us / 1000.0
    if ms < 1000.0:
        return "%.3f ms" % ms
    return "%.3f s" % (ms / 1000.0)


def _fmt_bytes(value):
    if value is None:
        return "N/A"
    try:
        value = float(value)
    except Exception:
        return "N/A"
    units = ["B", "KB", "MB", "GB", "TB"]
    idx = 0
    while abs(value) >= 1024.0 and idx < len(units) - 1:
        value /= 1024.0
        idx += 1
    return ("%.0f %s" if idx == 0 else "%.2f %s") % (value, units[idx])


def _category_info(node, category):
    try:
        data = node.performanceInfo(category)
        return {
            "callCount": int(data.get("callCount", 0) or 0),
            "timeTakenCPU": int(data.get("timeTakenCPU", 0) or 0),
            "timeTakenWall": int(data.get("timeTakenWall", 0) or 0),
        }
    except Exception:
        return {"callCount": 0, "timeTakenCPU": 0, "timeTakenWall": 0}


def _profiler_active():
    """Return whether Nuke's native performance profiler is currently active.

    NodeInfo 1.2 deliberately NEVER starts it automatically because
    startPerformanceTimers() also enables Nuke's native node-graph overlay.
    """
    try:
        return bool(nuke.usingPerformanceTimers())
    except Exception:
        return False


def show_native_profiler():
    """Explicit opt-in to Nuke's native profiler/overlay."""
    try:
        nuke.startPerformanceTimers()
    except Exception as exc:
        nuke.warning("Could not start Nuke performance timers: %s" % exc)


def hide_native_profiler():
    """Stop Nuke's native profiler so the node graph returns to normal."""
    try:
        nuke.stopPerformanceTimers()
    except Exception as exc:
        nuke.warning("Could not stop Nuke performance timers: %s" % exc)


def reset_native_profiler():
    try:
        nuke.resetPerformanceTimers()
    except Exception as exc:
        nuke.warning("Could not reset Nuke performance timers: %s" % exc)

def _numeric_total(obj, key_hint=""):
    """Best-effort extraction from memory2.info()'s implementation-dependent data.

    Only values whose key/parent hints look memory-related are counted when data is
    dictionary based. For plain numeric lists/tuples, all numeric values are summed.
    """
    memory_words = ("byte", "bytes", "memory", "mem", "size", "buffer", "allocated", "usage")
    if isinstance(obj, bool):
        return 0
    if isinstance(obj, (int, float)):
        if not key_hint or any(w in key_hint.lower() for w in memory_words):
            return max(0, int(obj))
        return 0
    if isinstance(obj, dict):
        total = 0
        for k, v in obj.items():
            total += _numeric_total(v, str(k))
        return total
    if isinstance(obj, (list, tuple, set)):
        total = 0
        for v in obj:
            if isinstance(v, (int, float)) and not isinstance(v, bool):
                total += max(0, int(v))
            else:
                total += _numeric_total(v, key_hint)
        return total
    return 0


def _node_memory(node):
    if nuke_memory is None:
        return None, "memory2 unavailable"
    try:
        info = nuke_memory.info()
    except Exception as exc:
        return None, "memory2.info error: %s" % exc

    if not isinstance(info, dict):
        return None, "No per-node memory data"

    candidates = [node.fullName(), node.name()]
    entry = None
    matched = None
    for key in candidates:
        if key in info:
            entry = info[key]
            matched = key
            break
    if entry is None:
        # Some builds prefix/group the node names differently.
        for key, value in info.items():
            if str(key).split(".")[-1] == node.name():
                entry = value
                matched = str(key)
                break

    if entry is None:
        return 0, "No active buffer reported for this node"

    value = _numeric_total(entry)
    return value, "memory2.info[%s]" % matched


def _node_format(node):
    try:
        f = node.format()
        return "%d x %d" % (f.width(), f.height())
    except Exception:
        try:
            return "%d x %d" % (node.width(), node.height())
        except Exception:
            return "N/A"


def _node_channels(node):
    try:
        chans = list(node.channels())
        if not chans:
            return "N/A"
        # Present layer summary rather than a huge channel list.
        layers = []
        for ch in chans:
            layer = ch.split(".")[0]
            if layer not in layers:
                layers.append(layer)
        if len(chans) <= 8:
            return ", ".join(chans)
        return "%d channels (%s%s)" % (
            len(chans), ", ".join(layers[:5]), "..." if len(layers) > 5 else ""
        )
    except Exception:
        return "N/A"


def _bbox(node):
    try:
        b = node.bbox()
        return "(%d, %d) - (%d, %d)" % (b.x(), b.y(), b.r(), b.t())
    except Exception:
        return "N/A"


def _all_profiled_engine_times():
    values = []
    for n in nuke.allNodes(recurseGroups=True):
        try:
            t = int(n.performanceInfo(nuke.PROFILE_ENGINE).get("timeTakenWall", 0) or 0)
            if t > 0:
                values.append((n, t))
        except Exception:
            pass
    return values


def _cost(node_wall):
    values = _all_profiled_engine_times()
    max_wall = max([t for _, t in values], default=0)
    total_wall = sum(t for _, t in values)
    ratio_to_max = (float(node_wall) / max_wall) if max_wall > 0 else 0.0
    script_share = (100.0 * float(node_wall) / total_wall) if total_wall > 0 else 0.0

    if node_wall <= 0 or max_wall <= 0:
        level = "IDLE"
    elif ratio_to_max <= LIGHT_MAX:
        level = "LIGHT"
    elif ratio_to_max <= MEDIUM_MAX:
        level = "MEDIUM"
    else:
        level = "HEAVY"
    return level, ratio_to_max * 100.0, script_share


def collect(node):
    profiler_active = _profiler_active()
    cats = {
        "Store": _category_info(node, nuke.PROFILE_STORE),
        "Validate": _category_info(node, nuke.PROFILE_VALIDATE),
        "Request": _category_info(node, nuke.PROFILE_REQUEST),
        "Engine": _category_info(node, nuke.PROFILE_ENGINE),
    }
    wall = cats["Engine"]["timeTakenWall"]
    level, relative, share = _cost(wall)
    memory, memory_note = _node_memory(node)

    return {
        "name": node.name(),
        "full_name": _safe_call(node.fullName, node.name()),
        "class": node.Class(),
        "frame": nuke.frame(),
        "format": _node_format(node),
        "channels": _node_channels(node),
        "bbox": _bbox(node),
        "memory": memory,
        "memory_note": memory_note,
        "level": level,
        "relative": relative,
        "script_share": share,
        "categories": cats,
        "profiler_active": profiler_active,
    }


def plain_text(data):
    c = data["categories"]
    lines = [
        "NODEINFO %s — Nuke 17" % __version__,
        "=" * 46,
        "Node:          %s" % data["full_name"],
        "Class:         %s" % data["class"],
        "Frame:         %s" % data["frame"],
        "Cost:          %s" % data["level"],
        "Relative:      %.1f%% of slowest profiled node" % data["relative"],
        "Script share:  %.1f%% (sum of profiled Engine wall times)" % data["script_share"],
        "Memory:        %s" % _fmt_bytes(data["memory"]),
        "Memory source: %s" % data["memory_note"],
        "Native profiler: %s" % ("ACTIVE" if data.get("profiler_active") else "OFF"),
        "",
        "PERFORMANCE (cumulative since last profiler reset)",
        "-" * 46,
    ]
    for name in ("Store", "Validate", "Request", "Engine"):
        info = c[name]
        lines.append("%-9s wall %-12s calls %-8d cpu %s" % (
            name + ":", _fmt_time_us(info["timeTakenWall"]), info["callCount"],
            _fmt_time_us(info["timeTakenCPU"])
        ))
    lines += [
        "",
        "IMAGE",
        "-" * 46,
        "Format:        %s" % data["format"],
        "Channels:      %s" % data["channels"],
        "BBox:          %s" % data["bbox"],
        "",
        "NOTE",
        "NodeInfo never starts Nuke native profiling automatically.",
        "Timing values update only while Nuke native profiling is enabled",
        "explicitly (NodeInfo > Advanced > Show Native Profiler).",
        "Stopping it removes the cpu/wall/memory labels from the DAG.",
        "On Windows, CPU time" ,
        "is not independent from wall time; use Engine Wall as the",
        "main performance indicator.",
        "",
        "CREATOR",
        "-" * 46,
        "NodeInfo %s" % __version__,
        "Part of %s %s" % (config.SUITE_NAME, config.VERSION),
        "Created by %s" % __author__,
        __copyright__,
        "License: %s" % __license__,
    ]
    return "\n".join(lines)


class NodeInfoPopup(QtWidgets.QFrame):
    def __init__(self):
        flags = QtCore.Qt.Tool | QtCore.Qt.FramelessWindowHint | QtCore.Qt.WindowStaysOnTopHint
        super(NodeInfoPopup, self).__init__(None, flags)
        self.setObjectName("NodeInfoPopup")
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose, False)
        self.setMinimumWidth(390)
        self._node = None
        self._data = None
        self._drag_pos = None
        self._momentary = False
        self._build_ui()

    def _build_ui(self):
        self.setStyleSheet("""
            QFrame#NodeInfoPopup { background:#202327; border:1px solid #4A5057; border-radius:8px; }
            QLabel { color:#D8DEE9; font-size:12px; }
            QLabel#Title { color:#FFFFFF; font-size:15px; font-weight:600; }
            QLabel#Sub { color:#929AA5; font-size:11px; }
            QLabel#Section { color:#AAB2BD; font-size:10px; font-weight:700; }
            QPushButton { background:#30353B; color:#DDE3EA; border:1px solid #4A5057; border-radius:4px; padding:5px 9px; }
            QPushButton:hover { background:#3B424A; }
            QProgressBar { border:0; background:#121417; border-radius:3px; height:6px; text-align:center; }
        """)
        root = QtWidgets.QVBoxLayout(self)
        root.setContentsMargins(13, 11, 13, 12)
        root.setSpacing(7)

        header = QtWidgets.QHBoxLayout()
        names = QtWidgets.QVBoxLayout()
        self.title = QtWidgets.QLabel("Node")
        self.title.setObjectName("Title")
        self.subtitle = QtWidgets.QLabel("Class")
        self.subtitle.setObjectName("Sub")
        names.addWidget(self.title)
        names.addWidget(self.subtitle)
        header.addLayout(names, 1)
        self.badge = QtWidgets.QLabel("IDLE")
        self.badge.setAlignment(QtCore.Qt.AlignCenter)
        self.badge.setMinimumWidth(74)
        header.addWidget(self.badge)
        self.close_btn = QtWidgets.QPushButton("×")
        self.close_btn.setFixedSize(24, 24)
        self.close_btn.setToolTip("Close")
        self.close_btn.setStyleSheet("QPushButton{background:transparent;color:#AAB2BD;border:0;font-size:18px;padding:0;} QPushButton:hover{color:#FFFFFF;background:#3B424A;border-radius:4px;}")
        self.close_btn.clicked.connect(self.hide)
        header.addWidget(self.close_btn)
        root.addLayout(header)

        self.progress = QtWidgets.QProgressBar()
        self.progress.setRange(0, 100)
        self.progress.setTextVisible(False)
        root.addWidget(self.progress)

        grid = QtWidgets.QGridLayout()
        grid.setHorizontalSpacing(18)
        grid.setVerticalSpacing(4)
        self.values = {}
        rows = [
            ("Engine Wall", "engine"), ("Calls", "calls"),
            ("Memory", "memory"), ("Script share", "share"),
            ("Store", "store"), ("Validate", "validate"),
            ("Request", "request"), ("Format", "format"),
            ("Channels", "channels"), ("BBox", "bbox"),
        ]
        for r, (label, key) in enumerate(rows):
            a = QtWidgets.QLabel(label)
            a.setObjectName("Sub")
            b = QtWidgets.QLabel("—")
            b.setTextInteractionFlags(QtCore.Qt.TextSelectableByMouse)
            b.setWordWrap(True)
            grid.addWidget(a, r, 0)
            grid.addWidget(b, r, 1)
            self.values[key] = b
        grid.setColumnStretch(1, 1)
        root.addLayout(grid)

        self.note = QtWidgets.QLabel("Profiler values are cumulative.")
        self.note.setObjectName("Sub")
        self.note.setWordWrap(True)
        root.addWidget(self.note)

        self.creator = QtWidgets.QLabel("NodeInfo %s  •  %s  •  by %s" % (__version__, config.SUITE_NAME, __author__))
        self.creator.setObjectName("Sub")
        self.creator.setAlignment(QtCore.Qt.AlignRight)
        self.creator.setStyleSheet("color:#6F7882;font-size:10px;")
        root.addWidget(self.creator)

        buttons = QtWidgets.QHBoxLayout()
        self.refresh_btn = QtWidgets.QPushButton("Refresh")
        self.reset_btn = QtWidgets.QPushButton("Reset timers")
        self.text_btn = QtWidgets.QPushButton("Plain Text")
        self.copy_btn = QtWidgets.QPushButton("Copy")
        buttons.addWidget(self.refresh_btn)
        buttons.addWidget(self.reset_btn)
        buttons.addStretch(1)
        buttons.addWidget(self.text_btn)
        buttons.addWidget(self.copy_btn)
        root.addLayout(buttons)

        self.refresh_btn.clicked.connect(self.refresh)
        self.reset_btn.clicked.connect(self.reset_timers)
        self.text_btn.clicked.connect(self.show_plain_text)
        self.copy_btn.clicked.connect(self.copy_plain_text)

    def set_momentary(self, enabled):
        self._momentary = bool(enabled)
        # Momentary popup is informational only; persistent mode keeps controls.
        for button in (self.refresh_btn, self.reset_btn, self.text_btn, self.copy_btn, self.close_btn):
            button.setVisible(not self._momentary)

    def set_node(self, node):
        self._node = node
        self.refresh()

    def refresh(self):
        if self._node is None:
            return
        try:
            self._data = collect(self._node)
        except Exception:
            nuke.warning("NodeInfo failed:\n%s" % traceback.format_exc())
            return
        d = self._data
        engine = d["categories"]["Engine"]
        self.title.setText(d["name"])
        self.subtitle.setText("%s  •  frame %s" % (d["class"], d["frame"]))
        color = COLORS[d["level"]]
        self.badge.setText(d["level"])
        self.badge.setStyleSheet("color:#111; background:%s; border-radius:9px; padding:3px 8px; font-weight:700;" % color)
        self.progress.setValue(int(max(0, min(100, d["relative"]))))
        self.progress.setStyleSheet("QProgressBar{border:0;background:#121417;border-radius:3px;height:6px;} QProgressBar::chunk{background:%s;border-radius:3px;}" % color)

        self.values["engine"].setText(_fmt_time_us(engine["timeTakenWall"]))
        self.values["calls"].setText(str(engine["callCount"]))
        self.values["memory"].setText(_fmt_bytes(d["memory"]))
        self.values["share"].setText("%.1f %%" % d["script_share"])
        self.values["store"].setText(_fmt_time_us(d["categories"]["Store"]["timeTakenWall"]))
        self.values["validate"].setText(_fmt_time_us(d["categories"]["Validate"]["timeTakenWall"]))
        self.values["request"].setText(_fmt_time_us(d["categories"]["Request"]["timeTakenWall"]))
        self.values["format"].setText(d["format"])
        self.values["channels"].setText(d["channels"])
        self.values["bbox"].setText(d["bbox"])
        if d.get("profiler_active"):
            self.note.setText("Native profiler ACTIVE. Memory: %s. Timings are cumulative since last reset." % d["memory_note"])
        else:
            self.note.setText("Native profiler OFF — no overlay. Showing last captured timing values, if any. Memory: %s." % d["memory_note"])
        self.adjustSize()

    def reset_timers(self):
        try:
            reset_native_profiler()
            self.refresh()
        except Exception as exc:
            nuke.warning("Could not reset performance timers: %s" % exc)

    def copy_plain_text(self):
        if self._data:
            QtWidgets.QApplication.clipboard().setText(plain_text(self._data))

    def show_plain_text(self):
        if not self._data:
            return
        dialog = QtWidgets.QDialog(self)
        dialog.setWindowTitle("NodeInfo — Plain Text")
        dialog.resize(690, 500)
        layout = QtWidgets.QVBoxLayout(dialog)
        edit = QtWidgets.QPlainTextEdit()
        edit.setReadOnly(True)
        edit.setPlainText(plain_text(self._data))
        edit.setStyleSheet("font-family: Consolas, monospace; font-size:12px;")
        layout.addWidget(edit)
        row = QtWidgets.QHBoxLayout()
        copy_b = QtWidgets.QPushButton("Copy all")
        close_b = QtWidgets.QPushButton("Close")
        row.addStretch(1)
        row.addWidget(copy_b)
        row.addWidget(close_b)
        layout.addLayout(row)
        copy_b.clicked.connect(lambda: QtWidgets.QApplication.clipboard().setText(edit.toPlainText()))
        close_b.clicked.connect(dialog.accept)
        dialog.exec()

    def mousePressEvent(self, event):
        if event.button() == QtCore.Qt.LeftButton:
            self._drag_pos = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
        super(NodeInfoPopup, self).mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self._drag_pos is not None and event.buttons() & QtCore.Qt.LeftButton:
            self.move(event.globalPosition().toPoint() - self._drag_pos)
        super(NodeInfoPopup, self).mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        self._drag_pos = None
        super(NodeInfoPopup, self).mouseReleaseEvent(event)

    def keyPressEvent(self, event):
        if event.key() == QtCore.Qt.Key_Escape:
            self.hide()
            return
        super(NodeInfoPopup, self).keyPressEvent(event)



def _resource_path(filename):
    return icon_path(filename)


def show_about():
    """Show creator, version and license information for distributed copies."""
    dialog = QtWidgets.QDialog()
    dialog.setWindowTitle("About NodeInfo")
    dialog.setMinimumWidth(460)
    dialog.setStyleSheet("""
        QDialog { background:#202327; }
        QLabel { color:#D8DEE9; }
        QLabel#AboutTitle { color:#FFFFFF; font-size:20px; font-weight:700; }
        QLabel#AboutSub { color:#9AA3AD; font-size:11px; }
        QPushButton { background:#30353B; color:#DDE3EA; border:1px solid #4A5057; border-radius:4px; padding:6px 12px; }
        QPushButton:hover { background:#3B424A; }
    """)
    layout = QtWidgets.QVBoxLayout(dialog)
    layout.setContentsMargins(20, 18, 20, 18)
    layout.setSpacing(10)

    logo = QtWidgets.QLabel()
    logo_path = _resource_path("drg_nodeinfo_logo.png")
    if os.path.exists(logo_path):
        pix = QtGui.QPixmap(logo_path)
        if not pix.isNull():
            logo.setPixmap(pix.scaledToWidth(360, QtCore.Qt.SmoothTransformation))
            logo.setAlignment(QtCore.Qt.AlignCenter)
            layout.addWidget(logo)

    title = QtWidgets.QLabel("NodeInfo %s  •  %s %s" % (__version__, config.SUITE_NAME, config.VERSION))
    title.setObjectName("AboutTitle")
    title.setAlignment(QtCore.Qt.AlignCenter)
    layout.addWidget(title)

    byline = QtWidgets.QLabel("Created by %s" % __author__)
    byline.setAlignment(QtCore.Qt.AlignCenter)
    layout.addWidget(byline)

    description = QtWidgets.QLabel(
        "A Houdini-inspired node inspector for Foundry Nuke. "
        "Inspect performance, memory and image information directly from the Node Graph."
    )
    description.setWordWrap(True)
    description.setAlignment(QtCore.Qt.AlignCenter)
    description.setObjectName("AboutSub")
    layout.addWidget(description)

    copyright_label = QtWidgets.QLabel(
        "%s\nLicensed under the %s License.\n\n"
        "Independent third-party tool. Not affiliated with or endorsed by Foundry." %
        (__copyright__, __license__)
    )
    copyright_label.setWordWrap(True)
    copyright_label.setAlignment(QtCore.Qt.AlignCenter)
    copyright_label.setObjectName("AboutSub")
    layout.addWidget(copyright_label)

    close_b = QtWidgets.QPushButton("Close")
    close_b.clicked.connect(dialog.accept)
    row = QtWidgets.QHBoxLayout()
    row.addStretch(1)
    row.addWidget(close_b)
    row.addStretch(1)
    layout.addLayout(row)
    dialog.exec()


def _looks_like_dag(widget):
    w = widget
    for _ in range(8):
        if w is None:
            break
        bits = [w.metaObject().className(), w.objectName(), w.windowTitle()]
        text = " ".join(str(x) for x in bits if x).lower()
        if "dag" in text or "node graph" in text or "nodegraph" in text:
            return w
        w = w.parentWidget()
    return None


def _dag_position_from_global(dag_widget, global_pos):
    """Convert Qt pixel location into Nuke DAG coordinates using current center/zoom."""
    local = dag_widget.mapFromGlobal(global_pos)
    z = float(nuke.zoom() or 1.0)
    center = nuke.center()
    if abs(z) < 1e-9:
        z = 1.0
    x = float(center[0]) + (float(local.x()) - dag_widget.width() * 0.5) / z
    y = float(center[1]) + (float(local.y()) - dag_widget.height() * 0.5) / z
    return x, y


def _node_at_dag_position(x, y):
    # Reverse order tends to prefer visually topmost nodes when overlap exists.
    nodes = list(nuke.allNodes())
    for node in reversed(nodes):
        try:
            nx, ny = node.xpos(), node.ypos()
            nw, nh = max(node.screenWidth(), 1), max(node.screenHeight(), 1)
            if nx <= x <= nx + nw and ny <= y <= ny + nh:
                return node
        except Exception:
            pass
    return None


def show_for_node(node, global_pos=None, momentary=False):
    global _popup
    if node is None:
        return
    if _popup is None:
        _popup = NodeInfoPopup()
    _popup.set_momentary(momentary)
    _popup.set_node(node)
    if global_pos is None:
        global_pos = QtGui.QCursor.pos()
    screen = QtGui.QGuiApplication.screenAt(global_pos)
    if screen is None:
        screen = QtGui.QGuiApplication.primaryScreen()
    pos = global_pos + QtCore.QPoint(18, 18)
    _popup.adjustSize()
    if screen:
        area = screen.availableGeometry()
        if pos.x() + _popup.width() > area.right():
            pos.setX(global_pos.x() - _popup.width() - 18)
        if pos.y() + _popup.height() > area.bottom():
            pos.setY(area.bottom() - _popup.height() - 8)
        pos.setX(max(area.left() + 4, pos.x()))
        pos.setY(max(area.top() + 4, pos.y()))
    _popup.move(pos)
    _popup.show()
    _popup.raise_()


def show_selected():
    try:
        show_for_node(nuke.selectedNode(), momentary=False)
    except Exception:
        nuke.message("Select a node first.")


def hide_popup():
    global _popup
    if _popup is not None:
        _popup.hide()


def _event_global_pos(event):
    try:
        return event.globalPosition().toPoint()
    except Exception:
        try:
            return event.globalPos()
        except Exception:
            return QtGui.QCursor.pos()


class AltMiddleMouseFilter(QtCore.QObject):
    def __init__(self, parent=None):
        super(AltMiddleMouseFilter, self).__init__(parent)
        self._holding_combo = False

    def _end_momentary(self):
        if self._holding_combo:
            self._holding_combo = False
            hide_popup()

    def eventFilter(self, watched, event):
        try:
            et = event.type()

            # Show only while ALT + Middle Mouse are physically held.
            if et == QtCore.QEvent.MouseButtonPress:
                if event.button() == QtCore.Qt.MiddleButton and (event.modifiers() & QtCore.Qt.AltModifier):
                    widget = watched if isinstance(watched, QtWidgets.QWidget) else None
                    dag = _looks_like_dag(widget)
                    pos = _event_global_pos(event)
                    if dag is None:
                        under = QtWidgets.QApplication.widgetAt(pos)
                        dag = _looks_like_dag(under)
                    if dag is not None:
                        x, y = _dag_position_from_global(dag, pos)
                        node = _node_at_dag_position(x, y)
                        if node is not None:
                            self._holding_combo = True
                            show_for_node(node, pos, momentary=True)
                            return True

            # Releasing MMB immediately dismisses the momentary popup.
            elif et == QtCore.QEvent.MouseButtonRelease:
                if event.button() == QtCore.Qt.MiddleButton:
                    if self._holding_combo:
                        self._end_momentary()
                        return True

            # Releasing ALT also dismisses it, even if MMB remains held.
            elif et == QtCore.QEvent.KeyRelease:
                if event.key() == QtCore.Qt.Key_Alt:
                    self._end_momentary()

            # Defensive cleanup: if Qt says the required combo is no longer held,
            # never leave a momentary popup stranded on screen.
            elif et in (QtCore.QEvent.MouseMove, QtCore.QEvent.KeyPress):
                if self._holding_combo:
                    buttons = QtWidgets.QApplication.mouseButtons()
                    mods = QtWidgets.QApplication.keyboardModifiers()
                    if not (buttons & QtCore.Qt.MiddleButton) or not (mods & QtCore.Qt.AltModifier):
                        self._end_momentary()

            elif et in (QtCore.QEvent.ApplicationDeactivate, QtCore.QEvent.WindowDeactivate):
                self._end_momentary()

        except Exception:
            print("NodeInfo event filter error:\n%s" % traceback.format_exc())
        return False


def install():
    global _filter
    # IMPORTANT: NodeInfo does not call startPerformanceTimers() automatically.
    # This keeps Nuke's native cpu/wall/memory labels hidden by default.
    app = QtWidgets.QApplication.instance()
    if app is None:
        return False
    if _filter is None:
        _filter = AltMiddleMouseFilter(app)
        app.installEventFilter(_filter)
    return True


def uninstall():
    global _filter, _popup
    app = QtWidgets.QApplication.instance()
    if app is not None and _filter is not None:
        app.removeEventFilter(_filter)
    _filter = None
    if _popup is not None:
        _popup.hide()
    return True
