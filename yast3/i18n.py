"""Internationalization support using gettext."""

import gettext
import os

APP_NAME = "yast3"

# Locale search paths in priority order
LOCALE_DIRS = [
    # Development path (relative to package)
    os.path.join(os.path.dirname(__file__), "..", "locale"),
    # User local installation
    os.path.expanduser("~/.local/share/locale"),
    # System installation paths
    "/usr/local/share/locale",
    "/usr/share/locale",
]

# Global translation function
_ = gettext.gettext


def _find_locale_dir() -> str | None:
    """Find the first locale directory that exists."""
    for localedir in LOCALE_DIRS:
        if os.path.isdir(localedir):
            return localedir
    return None


def init_i18n() -> None:
    """Initialize gettext translations."""
    global _
    localedir = _find_locale_dir()

    if localedir is None:
        translation = gettext.NullTranslations()
        _ = translation.gettext
        return

    try:
        translation = gettext.translation(APP_NAME, localedir=localedir)
        _ = translation.gettext
    except FileNotFoundError:
        translation = gettext.NullTranslations()
        _ = translation.gettext