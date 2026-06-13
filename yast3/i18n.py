"""Internationalization support using gettext."""

import gettext
import locale
import os

APP_NAME = "yast3"
LOCALE_DIR = os.path.join(os.path.dirname(__file__), "..", "locale")

_translations: dict[str, gettext.NullTranslations] = {}


def init_i18n(language: str | None = None) -> None:
    """Initialize gettext translations.

    Args:
        language: Language code (e.g., 'zh_CN', 'en_US'). If None, uses system locale.
    """
    if language is None:
        try:
            lang, _ = locale.getlocale()
            language = lang or "en_US"
        except Exception:
            language = "en_US"

    try:
        translation = gettext.translation(
            APP_NAME,
            localedir=LOCALE_DIR,
            languages=[language],
        )
    except FileNotFoundError:
        translation = gettext.NullTranslations()

    _translations[language] = translation


def gettext_func(domain: str = APP_NAME) -> gettext.GNUTranslations | gettext.NullTranslations:
    """Get translation function for the given domain."""
    try:
        return _translations.get(locale.getlocale()[0] or "en_US", gettext.NullTranslations())
    except Exception:
        return gettext.NullTranslations()


def _install(domain: str = APP_NAME) -> None:
    """Install the gettext function into the builtins namespace."""
    import builtins
    builtins.__dict__["_"] = gettext_func(domain)


__all__ = ["init_i18n", "_", "_install"]