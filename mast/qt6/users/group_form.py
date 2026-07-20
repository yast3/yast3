"""Group form widget for Qt6."""

from __future__ import annotations

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

import grp
from mast.core.i18n import _
from mast.core.users import UserEntry, is_system_group, build_add_group_command, build_modify_group_command
from mast.qt6.command.action import CommandAction


class GroupForm(QWidget):
    group_saved = Signal()

    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)
        self._users: list[UserEntry] = []
        self._selected_group: grp.struct_group | None = None
        self._is_new_group = False
        self._setup_ui()

    def _setup_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setSpacing(8)

        form_layout = QGridLayout()
        form_layout.setSpacing(8)

        form_layout.addWidget(QLabel(_("GID")), 0, 0)
        self.gid_edit = QLineEdit()
        self.gid_edit.setReadOnly(True)
        form_layout.addWidget(self.gid_edit, 0, 1)

        form_layout.addWidget(QLabel(_("Group Name")), 1, 0)
        self.name_edit = QLineEdit()
        self.name_edit.setReadOnly(True)
        form_layout.addWidget(self.name_edit, 1, 1)

        members_label = QLabel(_("Members"))
        members_label.setAlignment(Qt.AlignmentFlag.AlignTop)
        form_layout.addWidget(members_label, 2, 0)

        self.members_list = QListWidget()
        form_layout.addWidget(self.members_list, 2, 1)

        layout.addLayout(form_layout)

        save_layout = QHBoxLayout()
        save_layout.addStretch()
        self.save_btn = QPushButton(_("Save"))
        self.save_btn.clicked.connect(self._on_save_group)
        self.save_btn.setEnabled(False)
        save_layout.addWidget(self.save_btn)
        layout.addLayout(save_layout)

    def set_users(self, users: list[UserEntry]) -> None:
        self._users = users
        self._populate_members_list()

    def _populate_members_list(self) -> None:
        self.members_list.clear()
        for user in self._users:
            item = QListWidgetItem(user.username)
            item.setFlags(item.flags() | Qt.ItemFlag.ItemIsUserCheckable)
            item.setCheckState(Qt.CheckState.Unchecked)
            item.setData(Qt.ItemDataRole.UserRole, user)
            self.members_list.addItem(item)

    def _fill_group_form(self, group: grp.struct_group) -> None:
        self.name_edit.setText(group.gr_name)
        self.gid_edit.setText(str(group.gr_gid))

        for i in range(self.members_list.count()):
            item = self.members_list.item(i)
            user = item.data(Qt.ItemDataRole.UserRole)
            checked = user.primary_group == group.gr_name or user.username in group.gr_mem
            item.setCheckState(Qt.CheckState.Checked if checked else Qt.CheckState.Unchecked)

        self.save_btn.setEnabled(True)

    def _clear_form(self) -> None:
        self.name_edit.clear()
        self.gid_edit.clear()
        for i in range(self.members_list.count()):
            self.members_list.item(i).setCheckState(Qt.CheckState.Unchecked)
        self.save_btn.setEnabled(False)

    def _on_add_group(self) -> None:
        self._is_new_group = True
        self._selected_group = None
        self.name_edit.setReadOnly(False)
        self.name_edit.clear()
        self.gid_edit.clear()
        for i in range(self.members_list.count()):
            self.members_list.item(i).setCheckState(Qt.CheckState.Unchecked)
        self.save_btn.setEnabled(True)
        self.name_edit.setFocus()

    def _on_save_group(self) -> None:
        name = self.name_edit.text().strip()
        if not name:
            QMessageBox.warning(self, _("Error"), _("Group name cannot be empty"))
            return

        selected_members = []
        for i in range(self.members_list.count()):
            item = self.members_list.item(i)
            if item.checkState() == Qt.CheckState.Checked:
                selected_members.append(item.text())

        if self._is_new_group:
            cmd = build_add_group_command(
                name=name,
                members=selected_members,
            )
            success_msg = _("Group '{0}' created successfully.").format(name)
            dialog_title = _("Create Group")
        else:
            cmd = build_modify_group_command(
                name=name,
                members=selected_members,
            )
            success_msg = _("Group '{0}' updated successfully.").format(name)
            dialog_title = _("Update Group")

        self.current_action = CommandAction(
            text=_("Save"),
            running_text=_("Saving..."),
            dialog_title=dialog_title,
            command=cmd,
            success_output=success_msg,
            parent=self,
        )
        self.current_action.action_finished.connect(self._on_action_finished)
        self.current_action.start_action()

    def _on_action_finished(self, success: bool, _error: str, _stdout: str) -> None:
        if success:
            self.name_edit.setReadOnly(True)
            self._is_new_group = False
            self.save_btn.setEnabled(False)
            self.group_saved.emit()