"""MaST core library - UI-independent logic."""

import importlib.metadata
from pathlib import Path

from mast.core.i18n import _, init_i18n

try:
    __version__ = importlib.metadata.version("mast")
except importlib.metadata.PackageNotFoundError:
    __version__ = "0.0.0"

GITHUB_URL = "https://github.com/guoyunhe/mast"
LICENSE_NAME = "GNU General Public License v3.0"


def get_license_text() -> str:
    license_path = Path(__file__).resolve().parent.parent.parent / "LICENSE"
    return license_path.read_text() if license_path.exists() else ""


__all__ = ["_", "init_i18n", "__version__", "GITHUB_URL", "LICENSE_NAME", "get_license_text"]