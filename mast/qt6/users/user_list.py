"""User list widget for Qt6."""

from __future__ import annotations

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QHBoxLayout,
    QMessageBox,
    QPushButton,
    QTreeWidget,
    QTreeWidgetItem,
    QVBoxLayout,
    QWidget,
)

from mast.core.i18n import _
from mast.core.users import UserEntry, is_user_deletable, build_delete_user_command
from mast.qt6.command.action import CommandAction


class UserList(QWidget):
    user_selected = Signal(UserEntry)
    user_added = Signal()
    user_deleted = Signal()

    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)
        self._users: list[UserEntry] = []
        self._selected_user: UserEntry | None = None
        self._setup_ui()

    def _setup_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setSpacing(8)

        self.user_tree = QTreeWidget()
        self.user_tree.setColumnCount(1)
        self.user_tree.setHeaderHidden(True)
        self.user_tree.setSelectionMode(QTreeWidget.SelectionMode.SingleSelection)
        self.user_tree.currentItemChanged.connect(self._on_user_selected)
        layout.addWidget(self.user_tree)

        button_layout = QHBoxLayout()
        self.add_btn = QPushButton(_("Add"))
        self.add_btn.clicked.connect(self._on_add_user)
        button_layout.addWidget(self.add_btn)

        self.delete_btn = QPushButton(_("Delete"))
        self.delete_btn.clicked.connect(self._on_delete_user)
        self.delete_btn.setEnabled(False)
        button_layout.addWidget(self.delete_btn)

        layout.addLayout(button_layout)

    def set_users(self, users: list[UserEntry]) -> None:
        self._users = users
        self._populate_user_tree()

    def _populate_user_tree(self) -> None:
        self.user_tree.clear()

        system_users_item = QTreeWidgetItem([_("System Users")])
        system_users_item.setExpanded(True)
        system_users_item.setFlags(system_users_item.flags() & ~Qt.ItemFlag.ItemIsSelectable)

        local_users_item = QTreeWidgetItem([_("Local Users")])
        local_users_item.setExpanded(True)
        local_users_item.setFlags(local_users_item.flags() & ~Qt.ItemFlag.ItemIsSelectable)

        current_username = None
        try:
            import os
            current_username = os.getlogin()
        except Exception:
            pass

        system_user_items = []
        local_user_items = []
        selected_item = None

        for user in self._users:
            item = QTreeWidgetItem([user.username])
            item.setData(0, Qt.ItemDataRole.UserRole, user)

            if user.uid >= 1000:
                local_user_items.append(item)
            else:
                system_user_items.append(item)

            if current_username and user.username == current_username:
                selected_item = item

        for item in system_user_items:
            system_users_item.addChild(item)
        for item in local_user_items:
            local_users_item.addChild(item)

        self.user_tree.addTopLevelItem(system_users_item)
        self.user_tree.addTopLevelItem(local_users_item)

        if selected_item:
            self.user_tree.setCurrentItem(selected_item)

    def _on_user_selected(self, current: QTreeWidgetItem | None, _previous: QTreeWidgetItem | None) -> None:
        if current:
            self._selected_user = current.data(0, Qt.ItemDataRole.UserRole)
            if self._selected_user:
                self.delete_btn.setEnabled(is_user_deletable(self._selected_user))
                self.user_selected.emit(self._selected_user)
            else:
                self.delete_btn.setEnabled(False)
        else:
            self._selected_user = None
            self.delete_btn.setEnabled(False)
            self.user_selected.emit(None)

    def _on_add_user(self) -> None:
        self.user_tree.clearSelection()
        self._selected_user = None
        self.delete_btn.setEnabled(False)
        self.user_added.emit()

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
        self.current_action.action_finished.connect(self._on_delete_finished)
        self.current_action.start_action()

    def _on_delete_finished(self, success: bool, _error: str, _stdout: str) -> None:
        if success:
            self._selected_user = None
            self.delete_btn.setEnabled(False)
            self.user_deleted.emit()

    def select_user(self, username: str) -> None:
        root = self.user_tree.invisibleRootItem()
        for i in range(root.childCount()):
            child = root.child(i)
            if child.text(0) == username:
                self.user_tree.setCurrentItem(child)
                return
            for j in range(child.childCount()):
                grandchild = child.child(j)
                if grandchild.text(0) == username:
                    self.user_tree.setCurrentItem(grandchild)
                    return