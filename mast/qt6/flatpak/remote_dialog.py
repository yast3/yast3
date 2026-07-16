"""Qt6 dialog for creating or editing Flatpak remotes."""

from __future__ import annotations

from typing import Literal, cast

from PySide6.QtWidgets import (
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QLabel,
    QLineEdit,
    QVBoxLayout,
    QWidget,
)

from mast.core.flatpak import FlatpakRemote
from mast.core.i18n import _

ScopeValue = Literal["system", "user"]


class RemoteDialog(QDialog):
    def __init__(
        self,
        parent: QWidget,
        title: str,
        remote: FlatpakRemote | None = None,
        edit_mode: bool = False,
    ) -> None:
        super().__init__(parent)
        self.setWindowTitle(title)

        layout = QVBoxLayout(self)
        form = QFormLayout()

        self.name_label = QLabel(remote.name if remote else "")
        self.name_input: QLineEdit | None = None

        if edit_mode:
            form.addRow(_("Name"), self.name_label)
        else:
            self.name_input = QLineEdit()
            form.addRow(_("Name"), self.name_input)

        self.url_input = QLineEdit()
        self.url_input.setText(remote.url if remote else "")
        form.addRow(_("URL"), self.url_input)

        if edit_mode:
            self.scope_value = remote.scope if remote else "system"
            form.addRow(_("Scope"), QLabel(self.scope_value))
            self.scope_combo = None
        else:
            self.scope_combo = QComboBox()
            self.scope_combo.addItem(_("System"), "system")
            self.scope_combo.addItem(_("User"), "user")
            form.addRow(_("Scope"), self.scope_combo)
            self.scope_value = "system"

        layout.addLayout(form)

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def values(self) -> tuple[str, str, ScopeValue]:
        if self.scope_combo is None:
            name = self.name_label.text() if self.name_label is not None else ""
            scope = cast(ScopeValue, self.scope_value)
        else:
            name = self.name_input.text().strip() if self.name_input is not None else ""
            scope = cast(ScopeValue, str(self.scope_combo.currentData()))

        url = self.url_input.text().strip()
        return name, url, scope
