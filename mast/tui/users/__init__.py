"""Users and Groups module package - TUI."""

from textual.screen import Screen

from mast.core.i18n import _
from mast.tui.module import Module
from mast.tui.users.window import UsersWindow


class UsersModule(Module):
    def __init__(self):
        super().__init__(_("Users & Groups"), "👥")

    def create_window(self) -> Screen:
        return UsersWindow()


__all__ = ["UsersModule"]