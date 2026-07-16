"""About dialog for MaST Qt6 application."""

from __future__ import annotations

from PySide6.QtWidgets import QMessageBox, QWidget

from mast.core import GITHUB_URL, LICENSE_NAME, __version__
from mast.core.i18n import _


def show_about_dialog(parent: QWidget | None = None) -> None:
    text = (
        f"<h1>MaST</h1>"
        f"<p>{_('Version: {}').format(__version__)}</p>"
        f"<p>{_('License: {}').format(LICENSE_NAME)}</p>"
        f"<p><a href=\"{GITHUB_URL}\">{GITHUB_URL}</a></p>"
    )

    QMessageBox.about(parent, _("About MaST"), text)