"""Groups tab widget for Qt6."""

from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QFrame,
    QGridLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
    QWidget,
    QTreeWidget,
    QTreeWidgetItem,
)

import grp
from mast.core.i18n import _
from mast.core.users import (
    UserEntry,
    list_users,
    build_add_group_command,
    build_modify_group_command,
    build_delete_group_command,
    is_system_group,
)
from mast.qt6.command.action import CommandAction


class GroupsTab(QWidget):
    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)
        self._groups: list[grp.struct_group] = []
        self._users: list[UserEntry] = []
        self._selected_group: grp.struct_group | None = None
        self._is_new_group = False
        self._setup_ui()
        self._load_data()

    def _setup_ui(self) -> None:
        layout = QHBoxLayout(self)
        layout.setSpacing(16)

        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        left_layout.setSpacing(8)

        left_group = QGroupBox(_("Groups"))
        left_group_layout = QVBoxLayout(left_group)

        self.group_list = QTreeWidget()
        self.group_list.setColumnCount(1)
        self.group_list.setHeaderHidden(True)
        self.group_list.currentItemChanged.connect(self._on_group_selected)
        left_group_layout.addWidget(self.group_list)

        button_layout = QHBoxLayout()
        self.add_btn = QPushButton(_("Add"))
        self.add_btn.clicked.connect(self._on_add_group)
        button_layout.addWidget(self.add_btn)

        self.delete_btn = QPushButton(_("Delete"))
        self.delete_btn.clicked.connect(self._on_delete_group)
        self.delete_btn.setEnabled(False)
        button_layout.addWidget(self.delete_btn)

        left_group_layout.addLayout(button_layout)
        left_layout.addWidget(left_group)

        layout.addWidget(left_panel, 1)

        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.VLine)
        separator.setFrameShadow(QFrame.Shadow.Sunken)
        layout.addWidget(separator)

        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        right_layout.setSpacing(8)

        right_group = QGroupBox(_("Group Details"))
        right_group_layout = QVBoxLayout(right_group)

        form_layout = QGridLayout()
        form_layout.setSpacing(8)

        form_layout.addWidget(QLabel(_("Group Name")), 0, 0)
        self.name_edit = QLineEdit()
        self.name_edit.setReadOnly(True)
        form_layout.addWidget(self.name_edit, 0, 1)

        form_layout.addWidget(QLabel(_("GID")), 1, 0)
        self.gid_edit = QLineEdit()
        self.gid_edit.setReadOnly(True)
        form_layout.addWidget(self.gid_edit, 1, 1)

        right_group_layout.addLayout(form_layout)

        members_label = QLabel(_("Members"))
        right_group_layout.addWidget(members_label)

        self.members_list = QListWidget()
        self.members_list.setSelectionMode(QListWidget.SelectionMode.MultiSelection)
        right_group_layout.addWidget(self.members_list)

        right_layout.addWidget(right_group)

        save_layout = QHBoxLayout()
        save_layout.addStretch()
        self.save_btn = QPushButton(_("Save"))
        self.save_btn.clicked.connect(self._on_save_group)
        self.save_btn.setEnabled(False)
        save_layout.addWidget(self.save_btn)
        right_layout.addLayout(save_layout)

        layout.addWidget(right_panel, 2)

    def _load_data(self) -> None:
        try:
            self._groups = grp.getgrall()
            self._groups.sort(key=lambda g: g.gr_name)
            self._users = list_users()
            self._populate_group_list()
            self._populate_members_list()
        except Exception as e:
            QMessageBox.warning(self, _("Error"), _("Failed to load groups: {0}").format(str(e)))

    def _populate_group_list(self) -> None:
        self.group_list.clear()

        system_group_item = QTreeWidgetItem([_("System Groups")])
        system_group_item.setExpanded(True)
        system_group_item.setFlags(system_group_item.flags() & ~Qt.ItemFlag.ItemIsSelectable)

        user_group_item = QTreeWidgetItem([_("User Groups")])
        user_group_item.setExpanded(True)
        user_group_item.setFlags(user_group_item.flags() & ~Qt.ItemFlag.ItemIsSelectable)

        for group in self._groups:
            item = QTreeWidgetItem([group.gr_name])
            item.setData(0, Qt.ItemDataRole.UserRole, group)
            if is_system_group(group):
                system_group_item.addChild(item)
            else:
                user_group_item.addChild(item)

        self.group_list.addTopLevelItem(system_group_item)
        self.group_list.addTopLevelItem(user_group_item)

    def _populate_members_list(self) -> None:
        self.members_list.clear()
        for user in self._users:
            item = QListWidgetItem(user.username)
            item.setData(Qt.ItemDataRole.UserRole, user)
            self.members_list.addItem(item)

    def _on_group_selected(self, current: QTreeWidgetItem | None, _previous: QTreeWidgetItem | None) -> None:
        if current:
            self._is_new_group = False
            self._selected_group = current.data(0, Qt.ItemDataRole.UserRole)
            if self._selected_group:
                self._fill_group_form(self._selected_group)
                self.delete_btn.setEnabled(True)
                self.save_btn.setEnabled(True)
            else:
                self.delete_btn.setEnabled(False)
                self.save_btn.setEnabled(False)
        else:
            self._selected_group = None
            self._clear_form()
            self.delete_btn.setEnabled(False)
            self.save_btn.setEnabled(False)

    def _fill_group_form(self, group: grp.struct_group) -> None:
        self.name_edit.setText(group.gr_name)
        self.gid_edit.setText(str(group.gr_gid))

        for i in range(self.members_list.count()):
            item = self.members_list.item(i)
            username = item.text()
            item.setSelected(username in group.gr_mem)

    def _clear_form(self) -> None:
        self.name_edit.clear()
        self.gid_edit.clear()
        self.members_list.clearSelection()

    def _on_add_group(self) -> None:
        self._is_new_group = True
        self._selected_group = None
        self.group_list.clearSelection()
        self.name_edit.setReadOnly(False)
        self.name_edit.clear()
        self.gid_edit.clear()
        self.members_list.clearSelection()
        self.delete_btn.setEnabled(False)
        self.save_btn.setEnabled(True)
        self.name_edit.setFocus()

    def _on_delete_group(self) -> None:
        if not self._selected_group:
            return

        reply = QMessageBox.question(
            self,
            _("Confirm"),
            _("Are you sure you want to delete group '{0}'?").format(self._selected_group.gr_name),
        )
        if reply != QMessageBox.StandardButton.Yes:
            return

        cmd = build_delete_group_command(self._selected_group.gr_name)
        self.current_action = CommandAction(
            text=_("Delete"),
            running_text=_("Deleting..."),
            dialog_title=_("Delete Group"),
            command=cmd,
            success_output=_("Group '{0}' deleted successfully.").format(self._selected_group.gr_name),
            parent=self,
        )
        self.current_action.action_finished.connect(self._on_action_finished)
        self.current_action.start_action()

    def _on_save_group(self) -> None:
        name = self.name_edit.text().strip()
        if not name:
            QMessageBox.warning(self, _("Error"), _("Group name cannot be empty"))
            return

        selected_members = []
        for i in range(self.members_list.count()):
            if self.members_list.item(i).isSelected():
                selected_members.append(self.members_list.item(i).text())

        if self._is_new_group:
            cmd = build_add_group_command(
                name=name,
                members=selected_members,
            )
            success_msg = _("Group '{0}' created successfully.").format(name)
            dialog_title = _("Create Group")

            self.current_action = CommandAction(
                text=_("Create"),
                running_text=_("Creating..."),
                dialog_title=dialog_title,
                command=cmd,
                success_output=success_msg,
                parent=self,
            )
            self.current_action.action_finished.connect(self._on_action_finished)
            self.current_action.start_action()
        else:
            cmd = build_modify_group_command(
                name=name,
                members=selected_members,
            )
            success_msg = _("Group '{0}' updated successfully.").format(name)
            dialog_title = _("Update Group")

            self.current_action = CommandAction(
                text=_("Update"),
                running_text=_("Updating..."),
                dialog_title=dialog_title,
                command=cmd,
                success_output=success_msg,
                parent=self,
            )
            self.current_action.action_finished.connect(self._on_action_finished)
            self.current_action.start_action()

    def _on_action_finished(self, success: bool, _error: str, _stdout: str) -> None:
        if success:
            self._load_data()
            self._clear_form()
            self.name_edit.setReadOnly(True)
            self._is_new_group = False
            self.save_btn.setEnabled(False)
            self.delete_btn.setEnabled(False)