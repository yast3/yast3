"""Install Flatpak action component."""

from __future__ import annotations

from PySide6.QtCore import QObject

from mast.core.i18n import _
from mast.qt6.command.action import CommandAction


class InstallFlatpakAction(CommandAction):
    """Reusable action for triggering Flatpak installation."""

    def __init__(self, parent: QObject | None = None):
        super().__init__(
            text=_("Install Flatpak"),
            running_text=_("Installing Flatpak..."),
            dialog_title=_("Install Flatpak"),
            command=["pkexec", "zypper", "--non-interactive", "install", "-y", "flatpak"],
            success_output=_("Flatpak installed successfully."),
            auto_close_on_success=True,
            parent=parent,
        )


# Backward-compatible alias while call sites migrate from widget naming.
InstallFlatpakWidget = InstallFlatpakAction
