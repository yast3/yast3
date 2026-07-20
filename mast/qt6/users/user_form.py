"""User form widget for Qt6."""

from __future__ import annotations

from PySide6.QtCore import Qt, Signal
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
import re
from mast.core.i18n import _
from mast.core.users import (
    UserEntry,
    build_add_user_command,
    build_modify_user_command,
    build_set_password_command,
)
from mast.qt6.command.action import CommandAction


class UserForm(QWidget):
    user_saved = Signal(str)

    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)
        self._groups: list[grp.struct_group] = []
        self._selected_user: UserEntry | None = None
        self._is_new_user = False
        self._setup_ui()

    def _setup_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setSpacing(8)

        form_layout = QGridLayout()
        form_layout.setSpacing(8)

        form_layout.addWidget(QLabel(_("UID")), 0, 0)
        self.uid_edit = QLineEdit()
        self.uid_edit.setEnabled(False)
        form_layout.addWidget(self.uid_edit, 0, 1)

        form_layout.addWidget(QLabel(_("Username")), 1, 0)
        self.username_edit = QLineEdit()
        self.username_edit.setEnabled(False)
        self.username_edit.textChanged.connect(self._on_username_changed)
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

        layout.addLayout(form_layout)

        save_layout = QHBoxLayout()
        save_layout.addStretch()
        self.save_btn = QPushButton(_("Save"))
        self.save_btn.clicked.connect(self._on_save_user)
        self.save_btn.setEnabled(False)
        save_layout.addWidget(self.save_btn)
        layout.addLayout(save_layout)

    def set_groups(self, groups: list[grp.struct_group]) -> None:
        self._groups = groups
        self._populate_groups_list()

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

    def _fill_user_form(self, user: UserEntry) -> None:
        is_root = user.uid == 0
        is_system_user = user.uid > 0 and user.uid < 1000

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

        if is_system_user:
            self.full_name_edit.setEnabled(False)
            self.home_dir_edit.setEnabled(False)
            self.shell_edit.setEnabled(False)
            self.password_edit.setEnabled(False)
            self.primary_group_combo.setEnabled(False)
            self.groups_list.setEnabled(False)
            self.save_btn.setEnabled(False)
        elif is_root:
            self.full_name_edit.setEnabled(False)
            self.home_dir_edit.setEnabled(False)
            self.shell_edit.setEnabled(False)
            self.password_edit.setEnabled(True)
            self.primary_group_combo.setEnabled(False)
            self.groups_list.setEnabled(False)
            self.save_btn.setEnabled(True)
        else:
            self.full_name_edit.setEnabled(True)
            self.home_dir_edit.setEnabled(True)
            self.shell_edit.setEnabled(True)
            self.password_edit.setEnabled(True)
            self.primary_group_combo.setEnabled(True)
            self.groups_list.setEnabled(True)
            self.save_btn.setEnabled(True)

    def _clear_form(self) -> None:
        self.username_edit.clear()
        self.full_name_edit.clear()
        self.home_dir_edit.clear()
        self.shell_edit.setText("/bin/bash")
        self.primary_group_combo.setCurrentIndex(0)
        self.password_edit.clear()
        for i in range(self.groups_list.count()):
            self.groups_list.item(i).setCheckState(Qt.CheckState.Unchecked)
        self.save_btn.setEnabled(False)

    def _on_username_changed(self, username: str) -> None:
        home_dir = self.home_dir_edit.text().strip()
        if not home_dir or home_dir.startswith("/home/"):
            self.home_dir_edit.setText(f"/home/{username}")

    def _on_add_user(self) -> None:
        self._is_new_user = True
        self._selected_user = None
        self.uid_edit.clear()
        self.username_edit.setEnabled(True)
        self.username_edit.clear()
        self.full_name_edit.clear()
        self.full_name_edit.setEnabled(True)
        self.home_dir_edit.clear()
        self.home_dir_edit.setEnabled(True)
        self.shell_edit.setText("/bin/bash")
        self.shell_edit.setEnabled(True)
        self.password_edit.clear()
        self.password_edit.setEnabled(True)
        self.primary_group_combo.setEnabled(True)
        index = self.primary_group_combo.findText("users")
        if index >= 0:
            self.primary_group_combo.setCurrentIndex(index)
        else:
            self.primary_group_combo.setCurrentIndex(0)
        self.groups_list.setEnabled(True)
        for i in range(self.groups_list.count()):
            self.groups_list.item(i).setCheckState(Qt.CheckState.Unchecked)
        self.save_btn.setEnabled(True)
        self.username_edit.setFocus()

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
        else:
            is_root = self._selected_user and self._selected_user.uid == 0
            if is_root:
                if password:
                    cmd = build_set_password_command(username, password)
                    success_msg = _("Password set successfully.")
                    dialog_title = _("Set Password")
                    self.current_action = CommandAction(
                        text=_("Save"),
                        running_text=_("Setting password..."),
                        dialog_title=dialog_title,
                        command=cmd,
                        success_output=success_msg,
                        parent=self,
                    )
                    self.current_action.action_finished.connect(
                        lambda s, e, o, u=username: self._on_action_finished(s, e, o, u)
                    )
                    self.current_action.start_action()
                    return
                else:
                    QMessageBox.warning(self, _("Error"), _("No changes to save."))
                    return
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
            text=_("Save"),
            running_text=_("Saving..."),
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
                self.current_action.action_finished.connect(
                    lambda s, e, o, u=username: self._on_action_finished(s, e, o, u)
                )
                self.current_action.start_action()
            else:
                self._on_action_finished(success, error, stdout, username)
        else:
            self._on_action_finished(success, error, stdout, username)

    def _on_action_finished(self, success: bool, _error: str, _stdout: str, username: str = "") -> None:
        if success:
            self.username_edit.setReadOnly(True)
            self._is_new_user = False
            self.user_saved.emit(username)