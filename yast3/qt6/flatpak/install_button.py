"""Install Flatpak button component."""

from __future__ import annotations

from PySide6.QtWidgets import QWidget

from yast3.core.i18n import _
from yast3.qt6.command_action_widget import CommandActionWidget


class InstallFlatpakWidget(CommandActionWidget):
    """Standalone widget for triggering Flatpak installation."""

    def __init__(self, parent: QWidget | None = None):
        super().__init__(
            button_text=_("Install Flatpak"),
            running_text=_("Installing Flatpak..."),
            dialog_title=_("Install Flatpak"),
            command=["pkexec", "zypper", "--non-interactive", "install", "-y", "flatpak"],
            success_output=_("Flatpak installed successfully."),
            auto_close_on_success=True,
            parent=parent,
        )
