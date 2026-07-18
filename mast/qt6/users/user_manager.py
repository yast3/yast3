"""User manager widget for Qt6."""

from __future__ import annotations

from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QMessageBox,
    QWidget,
)

import grp
from mast.core.i18n import _
from mast.core.users import UserEntry, list_users

from mast.qt6.users.user_list import UserList
from mast.qt6.users.user_form import UserForm


class UserManager(QWidget):
    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)
        self._users: list[UserEntry] = []
        self._groups: list[grp.struct_group] = []
        self._setup_ui()
        self._load_data()

    def _setup_ui(self) -> None:
        layout = QHBoxLayout(self)
        layout.setSpacing(16)

        self.user_list = UserList()
        self.user_list.user_selected.connect(self._on_user_selected)
        self.user_list.user_added.connect(self._on_add_user)
        layout.addWidget(self.user_list, 1)

        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.VLine)
        separator.setFrameShadow(QFrame.Shadow.Sunken)
        layout.addWidget(separator)

        self.user_form = UserForm()
        self.user_form.user_saved.connect(self._on_user_saved)
        layout.addWidget(self.user_form, 2)

    def _load_data(self) -> None:
        try:
            self._users = list_users()
            self._groups = grp.getgrall()
            self._groups.sort(key=lambda g: g.gr_name)
            self.user_form.set_groups(self._groups)
            self.user_list.set_users(self._users)
        except Exception as e:
            QMessageBox.warning(self, _("Error"), _("Failed to load users: {0}").format(str(e)))

    def _on_user_selected(self, user: UserEntry) -> None:
        if user:
            self.user_form._is_new_user = False
            self.user_form._selected_user = user
            self.user_form._fill_user_form(user)
        else:
            self.user_form._clear_form()

    def _on_add_user(self) -> None:
        self.user_form._on_add_user()

    def _on_user_saved(self, username: str) -> None:
        self._load_data()
        if username:
            self.user_list.select_user(username)