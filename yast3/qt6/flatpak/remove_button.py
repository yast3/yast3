"""Remove Flatpak button component."""

from __future__ import annotations

from PySide6.QtWidgets import QMessageBox, QWidget

from yast3.core.i18n import _
from yast3.qt6.command_action_widget import CommandActionWidget


class RemoveFlatpakWidget(CommandActionWidget):
    """Standalone widget for triggering Flatpak removal."""

    def __init__(self, parent: QWidget | None = None):
        super().__init__(
            button_text=_("Remove Flatpak"),
            running_text=_("Removing Flatpak..."),
            dialog_title=_("Remove Flatpak"),
            command=["pkexec", "zypper", "--non-interactive", "remove", "-y", "flatpak"],
            success_output=_("Flatpak removed successfully."),
            auto_close_on_success=True,
            parent=parent,
        )

    def start_action(self) -> None:
        if self.is_running():
            return

        reply = QMessageBox.question(
            self,
            _("Confirm"),
            _("Are you sure you want to remove Flatpak?"),
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        if reply != QMessageBox.StandardButton.Yes:
            return

        super().start_action()
