"""YaST3 core library - UI-independent logic."""

import importlib.metadata

from yast3.core.i18n import _, init_i18n

try:
    __version__ = importlib.metadata.version("yast3")
except importlib.metadata.PackageNotFoundError:
    __version__ = "0.0.0"

GITHUB_URL = "https://github.com/yast3/yast3"

__all__ = ["_", "init_i18n", "__version__", "GITHUB_URL"]