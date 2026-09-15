# -*- coding: utf-8 -*-
"""Path helpers for DRG Tools."""

from pathlib import Path

_PACKAGE_DIR = Path(__file__).resolve().parent
_PYTHON_DIR = _PACKAGE_DIR.parent
_ROOT_DIR = _PYTHON_DIR.parent
_ICONS_DIR = _ROOT_DIR / "icons"
_GIZMOS_DIR = _ROOT_DIR / "gizmos"
_DOCS_DIR = _ROOT_DIR / "docs"


def root_dir():
    return str(_ROOT_DIR)


def icon_path(filename):
    return str(_ICONS_DIR / filename)


def gizmo_path(filename):
    return str(_GIZMOS_DIR / filename)


def docs_path(filename):
    return str(_DOCS_DIR / filename)
