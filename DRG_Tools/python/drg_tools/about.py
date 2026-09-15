# -*- coding: utf-8 -*-
"""About dialog for DRG Tools."""

import nuke
from . import config
from .paths import icon_path

try:
    from PySide6 import QtCore, QtGui, QtWidgets
except ImportError:
    from PySide2 import QtCore, QtGui, QtWidgets


def show():
    dialog = QtWidgets.QDialog()
    dialog.setWindowTitle("About DRG Tools")
    dialog.setMinimumWidth(470)
    dialog.setStyleSheet("""
        QDialog { background:#202327; }
        QLabel { color:#D8DEE9; }
        QLabel#Title { color:#FFFFFF; font-size:21px; font-weight:700; }
        QLabel#Sub { color:#9AA3AD; font-size:11px; }
        QPushButton { background:#30353B; color:#DDE3EA; border:1px solid #4A5057; border-radius:4px; padding:6px 12px; }
        QPushButton:hover { background:#3B424A; }
    """)
    layout = QtWidgets.QVBoxLayout(dialog)
    layout.setContentsMargins(22, 20, 22, 18)
    layout.setSpacing(10)

    logo = QtWidgets.QLabel()
    pix = QtGui.QPixmap(icon_path("DRG_logo.png"))
    if not pix.isNull():
        logo.setPixmap(pix.scaledToWidth(320, QtCore.Qt.SmoothTransformation))
        logo.setAlignment(QtCore.Qt.AlignCenter)
        layout.addWidget(logo)

    title = QtWidgets.QLabel("%s %s" % (config.SUITE_NAME, config.VERSION))
    title.setObjectName("Title")
    title.setAlignment(QtCore.Qt.AlignCenter)
    layout.addWidget(title)

    text = QtWidgets.QLabel(
        "Digital compositing tools for Foundry Nuke.\n"
        "Created by %s.\n\n"
        "Included in this release:\n"
        "• NodeInfo %s\n"
        "• Directional Dilate %s\n\n"
        "%s\nLicensed under the %s License.\n\n"
        "Independent third-party tools. Not affiliated with or endorsed by Foundry."
        % (config.AUTHOR, config.NODEINFO_VERSION, config.DIRECTIONAL_DILATE_VERSION,
           config.COPYRIGHT, config.LICENSE)
    )
    text.setObjectName("Sub")
    text.setWordWrap(True)
    text.setAlignment(QtCore.Qt.AlignCenter)
    layout.addWidget(text)

    close_button = QtWidgets.QPushButton("Close")
    close_button.clicked.connect(dialog.accept)
    row = QtWidgets.QHBoxLayout()
    row.addStretch(1)
    row.addWidget(close_button)
    row.addStretch(1)
    layout.addLayout(row)
    dialog.exec()
