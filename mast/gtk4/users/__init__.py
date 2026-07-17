"""Users and Groups module package - GTK4 GUI."""

from mast.core.i18n import _
from mast.gtk4.module import Module
from mast.gtk4.users.window import UsersWindow


class UsersModule(Module):
    def __init__(self):
        super().__init__(_("Users & Groups"), ("system-users", "users"))

    def _create_window(self):
        return UsersWindow()


__all__ = ["UsersModule"]