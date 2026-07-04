"""Qt6 import button for predefined third-party repositories."""

from __future__ import annotations

from PySide6.QtCore import Signal
from PySide6.QtGui import QAction
from PySide6.QtWidgets import QMenu, QToolButton

from yast3.core.i18n import _
from yast3.core.repositories.repos import RepoEntry
from yast3.core.repositories.third_party_repos import third_party_repos


class ImportRepoButton(QToolButton):
    """Dropdown button that emits selected predefined repository."""

    repo_selected = Signal(object)

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setText(_("Import"))
        self.setPopupMode(QToolButton.ToolButtonPopupMode.InstantPopup)

        menu = QMenu(self)
        self.setMenu(menu)
        self._populate_menu()

    def _populate_menu(self) -> None:
        menu = self.menu()
        if menu is None:
            return

        menu.clear()
        for template in third_party_repos:
            action = QAction(template.name, self)
            action.triggered.connect(
                lambda _checked=False, repo=template: self.repo_selected.emit(repo)
            )
            menu.addAction(action)
