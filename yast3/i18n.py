import gettext
import os

APP_NAME = "yast3"
LOCALE_DIR = os.path.join(os.path.dirname(__file__), "..", "locale")

def init_i18n() -> None:
    try:
        translation = gettext.translation(
            APP_NAME,
            localedir=LOCALE_DIR,
        )
    except FileNotFoundError:
        translation = gettext.NullTranslations()

    translation.install()
