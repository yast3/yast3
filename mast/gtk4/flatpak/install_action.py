"""Install Flatpak action component."""

from __future__ import annotations

import gi

gi.require_version("Gtk", "4.0")

from gi.repository import Gtk

from mast.core.i18n import _
from mast.gtk4.command.action import CommandAction


class InstallFlatpakAction(CommandAction):
    """Reusable action for triggering Flatpak installation."""

    def __init__(self, parent_window: Gtk.Window | None = None):
        super().__init__(
            text=_("Install Flatpak"),
            running_text=_("Installing Flatpak..."),
            dialog_title=_("Install Flatpak"),
            command=["pkexec", "zypper", "--non-interactive", "install", "-y", "flatpak"],
            success_output=_("Flatpak installed successfully."),
            auto_close_on_success=True,
            parent_window=parent_window,
        )


# Backward-compatible alias while call sites migrate from widget naming.
InstallFlatpakWidget = InstallFlatpakAction
