"""Users tab widget for Qt6."""

from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QComboBox,
    QFrame,
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
import re

from mast.core.users import (
    UserEntry,
    list_users,
    build_add_user_command,
    build_modify_user_command,
    build_delete_user_command,
    build_set_password_command,
    is_user_deletable,
)
from mast.qt6.command.action import CommandAction


class UsersManager(QWidget):
    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)
        self._users: list[UserEntry] = []
        self._groups: list[grp.struct_group] = []
        self._selected_user: UserEntry | None = None
        self._is_new_user = False
        self._setup_ui()
        self._load_data()

    def _setup_ui(self) -> None:
        layout = QHBoxLayout(self)
        layout.setSpacing(16)

        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        left_layout.setSpacing(8)

        self.user_list = QListWidget()
        self.user_list.setSelectionMode(QListWidget.SelectionMode.SingleSelection)
        self.user_list.currentItemChanged.connect(self._on_user_selected)
        left_layout.addWidget(self.user_list)

        button_layout = QHBoxLayout()
        self.add_btn = QPushButton(_("Add"))
        self.add_btn.clicked.connect(self._on_add_user)
        button_layout.addWidget(self.add_btn)

        self.delete_btn = QPushButton(_("Delete"))
        self.delete_btn.clicked.connect(self._on_delete_user)
        self.delete_btn.setEnabled(False)
        button_layout.addWidget(self.delete_btn)

        left_layout.addLayout(button_layout)

        layout.addWidget(left_panel, 1)

        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.VLine)
        separator.setFrameShadow(QFrame.Shadow.Sunken)
        layout.addWidget(separator)

        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        right_layout.setSpacing(8)

        form_layout = QGridLayout()
        form_layout.setSpacing(8)

        form_layout.addWidget(QLabel(_("UID")), 0, 0)
        self.uid_edit = QLineEdit()
        self.uid_edit.setReadOnly(True)
        form_layout.addWidget(self.uid_edit, 0, 1)

        form_layout.addWidget(QLabel(_("Username")), 1, 0)
        self.username_edit = QLineEdit()
        self.username_edit.setReadOnly(True)
        form_layout.addWidget(self.username_edit, 1, 1)

        form_layout.addWidget(QLabel(_("Display Name")), 3, 0)
        self.full_name_edit = QLineEdit()
        self.full_name_edit.setPlaceholderText(_("Full name"))
        form_layout.addWidget(self.full_name_edit, 3, 1)

        form_layout.addWidget(QLabel(_("Home Directory")), 4, 0)
        self.home_dir_edit = QLineEdit()
        self.home_dir_edit.setPlaceholderText(_("/home/username"))
        form_layout.addWidget(self.home_dir_edit, 4, 1)

        form_layout.addWidget(QLabel(_("Shell")), 5, 0)
        self.shell_edit = QLineEdit()
        self.shell_edit.setPlaceholderText(_("/bin/bash"))
        form_layout.addWidget(self.shell_edit, 5, 1)

        form_layout.addWidget(QLabel(_("Password")), 6, 0)
        self.password_edit = QLineEdit()
        self.password_edit.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_edit.setPlaceholderText(_("Leave empty to skip"))
        form_layout.addWidget(self.password_edit, 6, 1)

        form_layout.addWidget(QLabel(_("Primary Group")), 7, 0)
        self.primary_group_combo = QComboBox()
        form_layout.addWidget(self.primary_group_combo, 7, 1)

        groups_label = QLabel(_("Additional Groups"))
        groups_label.setAlignment(Qt.AlignmentFlag.AlignTop)
        form_layout.addWidget(groups_label, 8, 0)
        self.groups_list = QListWidget()
        form_layout.addWidget(self.groups_list, 8, 1)

        right_layout.addLayout(form_layout)

        save_layout = QHBoxLayout()
        save_layout.addStretch()
        self.save_btn = QPushButton(_("Save"))
        self.save_btn.clicked.connect(self._on_save_user)
        self.save_btn.setEnabled(False)
        save_layout.addWidget(self.save_btn)
        right_layout.addLayout(save_layout)

        layout.addWidget(right_panel, 2)

    def _load_data(self) -> None:
        try:
            self._users = list_users()
            self._groups = grp.getgrall()
            self._groups.sort(key=lambda g: g.gr_name)
            self._populate_groups_list()
            self._populate_user_list()
        except Exception as e:
            QMessageBox.warning(self, _("Error"), _("Failed to load users: {0}").format(str(e)))

    def _populate_user_list(self) -> None:
        self.user_list.clear()
        current_username = None
        try:
            import os
            current_username = os.getlogin()
        except Exception:
            pass

        selected_row = -1
        for row, user in enumerate(self._users):
            item = QListWidgetItem(user.username)
            item.setData(Qt.ItemDataRole.UserRole, user)
            self.user_list.addItem(item)
            if current_username and user.username == current_username:
                selected_row = row

        if selected_row >= 0:
            self.user_list.setCurrentRow(selected_row)

    def _populate_groups_list(self) -> None:
        self.groups_list.clear()
        for group in self._groups:
            item = QListWidgetItem(group.gr_name)
            item.setFlags(item.flags() | Qt.ItemFlag.ItemIsUserCheckable)
            item.setCheckState(Qt.CheckState.Unchecked)
            item.setData(Qt.ItemDataRole.UserRole, group)
            self.groups_list.addItem(item)

        self.primary_group_combo.clear()
        for group in self._groups:
            self.primary_group_combo.addItem(group.gr_name, group)

    def _on_user_selected(self, current: QListWidgetItem | None, _previous: QListWidgetItem | None) -> None:
        if current:
            self._is_new_user = False
            self._selected_user = current.data(Qt.ItemDataRole.UserRole)
            if self._selected_user:
                self._fill_user_form(self._selected_user)
                self.delete_btn.setEnabled(is_user_deletable(self._selected_user))
            else:
                self.delete_btn.setEnabled(False)
            self.save_btn.setEnabled(True)
        else:
            self._selected_user = None
            self._clear_form()
            self.delete_btn.setEnabled(False)
            self.save_btn.setEnabled(False)

    def _fill_user_form(self, user: UserEntry) -> None:
        is_root = user.uid == 0

        self.uid_edit.setText(str(user.uid))
        self.username_edit.setText(user.username)
        self.full_name_edit.setText(user.full_name)
        self.home_dir_edit.setText(user.home_dir)
        self.shell_edit.setText(user.shell)
        self.password_edit.clear()

        index = self.primary_group_combo.findText(user.primary_group)
        if index >= 0:
            self.primary_group_combo.setCurrentIndex(index)

        for i in range(self.groups_list.count()):
            item = self.groups_list.item(i)
            if item:
                group_name = item.text()
                checked = group_name in user.groups
                item.setCheckState(Qt.CheckState.Checked if checked else Qt.CheckState.Unchecked)

        self.full_name_edit.setReadOnly(is_root)
        self.home_dir_edit.setReadOnly(is_root)
        self.shell_edit.setReadOnly(is_root)
        self.primary_group_combo.setEnabled(not is_root)

    def _clear_form(self) -> None:
        self.username_edit.clear()
        self.full_name_edit.clear()
        self.home_dir_edit.clear()
        self.shell_edit.setText("/bin/bash")
        self.primary_group_combo.setCurrentIndex(0)
        self.password_edit.clear()
        for i in range(self.groups_list.count()):
            self.groups_list.item(i).setCheckState(Qt.CheckState.Unchecked)

    def _on_add_user(self) -> None:
        self._is_new_user = True
        self._selected_user = None
        self.user_list.clearSelection()
        self.uid_edit.clear()
        self.username_edit.setReadOnly(False)
        self.username_edit.clear()
        self.full_name_edit.clear()
        self.home_dir_edit.clear()
        self.shell_edit.setText("/bin/bash")
        index = self.primary_group_combo.findText("users")
        if index >= 0:
            self.primary_group_combo.setCurrentIndex(index)
        else:
            self.primary_group_combo.setCurrentIndex(0)
        self.password_edit.clear()
        for i in range(self.groups_list.count()):
            self.groups_list.item(i).setCheckState(Qt.CheckState.Unchecked)
        self.delete_btn.setEnabled(False)
        self.save_btn.setEnabled(True)
        self.username_edit.setFocus()

    def _on_delete_user(self) -> None:
        if not self._selected_user:
            return

        if not is_user_deletable(self._selected_user):
            QMessageBox.warning(self, _("Error"), _("This user cannot be deleted."))
            return

        reply = QMessageBox.question(
            self,
            _("Confirm"),
            _("Are you sure you want to delete user '{0}'?").format(self._selected_user.username),
        )
        if reply != QMessageBox.StandardButton.Yes:
            return

        cmd = build_delete_user_command(self._selected_user.username)
        self.current_action = CommandAction(
            text=_("Delete"),
            running_text=_("Deleting..."),
            dialog_title=_("Delete User"),
            command=cmd,
            success_output=_("User '{0}' deleted successfully.").format(self._selected_user.username),
            parent=self,
        )
        self.current_action.action_finished.connect(self._on_action_finished)
        self.current_action.start_action()

    def _on_save_user(self) -> None:
        username = self.username_edit.text().strip()
        if not username:
            QMessageBox.warning(self, _("Error"), _("Username cannot be empty"))
            return

        if self._is_new_user:
            if not re.match(r"^[a-z][a-z0-9_-]*$", username):
                QMessageBox.warning(
                    self, _("Error"),
                    _("Username must start with a lowercase letter and can only contain lowercase letters, digits, hyphens, and underscores.")
                )
                return

        full_name = self.full_name_edit.text().strip()
        home_dir = self.home_dir_edit.text().strip()
        shell = self.shell_edit.text().strip() or "/bin/bash"
        password = self.password_edit.text().strip()

        selected_groups = []
        for i in range(self.groups_list.count()):
            item = self.groups_list.item(i)
            if item and item.checkState() == Qt.CheckState.Checked:
                selected_groups.append(item.text())

        primary_group = self.primary_group_combo.currentText()

        if self._is_new_user:
            cmd = build_add_user_command(
                username=username,
                full_name=full_name,
                home_dir=home_dir,
                shell=shell,
                groups=selected_groups,
                primary_group=primary_group,
            )
            success_msg = _("User '{0}' created successfully.").format(username)
            dialog_title = _("Create User")

            self.current_action = CommandAction(
                text=_("Create"),
                running_text=_("Creating..."),
                dialog_title=dialog_title,
                command=cmd,
                success_output=success_msg,
                parent=self,
            )
            self.current_action.action_finished.connect(
                lambda s, e, o, u=username, p=password: self._on_user_action_finished(s, e, o, u, p)
            )
            self.current_action.start_action()
        else:
            cmd = build_modify_user_command(
                username=username,
                full_name=full_name,
                home_dir=home_dir,
                shell=shell,
                groups=selected_groups,
                primary_group=primary_group,
            )
            success_msg = _("User '{0}' updated successfully.").format(username)
            dialog_title = _("Update User")

            self.current_action = CommandAction(
                text=_("Update"),
                running_text=_("Updating..."),
                dialog_title=dialog_title,
                command=cmd,
                success_output=success_msg,
                parent=self,
            )
            self.current_action.action_finished.connect(
                lambda s, e, o, u=username, p=password: self._on_user_action_finished(s, e, o, u, p)
            )
            self.current_action.start_action()

    def _on_user_action_finished(self, success: bool, error: str, stdout: str, username: str, password: str) -> None:
        if success:
            if password:
                cmd = build_set_password_command(username, password)
                self.current_action = CommandAction(
                    text=_("Set Password"),
                    running_text=_("Setting password..."),
                    dialog_title=_("Set Password"),
                    command=cmd,
                    success_output=_("Password set successfully."),
                    parent=self,
                )
                self.current_action.action_finished.connect(self._on_action_finished)
                self.current_action.start_action()
            else:
                self._on_action_finished(success, error, stdout)
        else:
            self._on_action_finished(success, error, stdout)

    def _on_action_finished(self, success: bool, _error: str, _stdout: str) -> None:
        if success:
            self._load_data()
            self._clear_form()
            self.username_edit.setReadOnly(True)
            self._is_new_user = False
            self.save_btn.setEnabled(False)
            self.delete_btn.setEnabled(False)