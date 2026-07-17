"""Users and Groups module package - Qt6 GUI."""

from mast.core.i18n import _
from mast.qt6.module import Module
from mast.qt6.users.window import UsersWindow


class UsersModule(Module):
    def __init__(self):
        super().__init__(_("Users & Groups"), ("system-users", "users"))

    def _create_window(self):
        return UsersWindow()


__all__ = ["UsersModule"]