"""Group manager widget for Qt6."""

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

from mast.qt6.users.group_list import GroupList
from mast.qt6.users.group_form import GroupForm


class GroupManager(QWidget):
    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)
        self._groups: list[grp.struct_group] = []
        self._users: list[UserEntry] = []
        self._setup_ui()
        self._load_data()

    def _setup_ui(self) -> None:
        layout = QHBoxLayout(self)
        layout.setSpacing(16)

        self.group_list = GroupList()
        self.group_list.group_selected.connect(self._on_group_selected)
        self.group_list.group_added.connect(self._on_add_group)
        layout.addWidget(self.group_list, 1)

        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.VLine)
        separator.setFrameShadow(QFrame.Shadow.Sunken)
        layout.addWidget(separator)

        self.group_form = GroupForm()
        self.group_form.group_saved.connect(self._on_group_saved)
        layout.addWidget(self.group_form, 2)

    def _load_data(self) -> None:
        try:
            self._groups = grp.getgrall()
            self._groups.sort(key=lambda g: g.gr_name)
            self._users = list_users()
            self.group_form.set_users(self._users)
            self.group_list.set_groups(self._groups)
        except Exception as e:
            QMessageBox.warning(self, _("Error"), _("Failed to load groups: {0}").format(str(e)))

    def _on_group_selected(self, group: grp.struct_group) -> None:
        if group:
            self.group_form._is_new_group = False
            self.group_form._selected_group = group
            self.group_form._fill_group_form(group)
        else:
            self.group_form._clear_form()

    def _on_add_group(self) -> None:
        self.group_form._on_add_group()

    def _on_group_saved(self) -> None:
        self._load_data()