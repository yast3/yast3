"""User list widget for Qt6."""

from __future__ import annotations

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QHBoxLayout,
    QListWidget,
    QListWidgetItem,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from mast.core.i18n import _
from mast.core.users import UserEntry, is_user_deletable, build_delete_user_command
from mast.qt6.command.action import CommandAction


class UserList(QWidget):
    user_selected = Signal(UserEntry)
    user_added = Signal()

    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)
        self._users: list[UserEntry] = []
        self._selected_user: UserEntry | None = None
        self._setup_ui()

    def _setup_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setSpacing(8)

        self.user_list = QListWidget()
        self.user_list.setSelectionMode(QListWidget.SelectionMode.SingleSelection)
        self.user_list.currentItemChanged.connect(self._on_user_selected)
        layout.addWidget(self.user_list)

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
        self._populate_user_list()

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

    def _on_user_selected(self, current: QListWidgetItem | None, _previous: QListWidgetItem | None) -> None:
        if current:
            self._selected_user = current.data(Qt.ItemDataRole.UserRole)
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
        self.user_list.clearSelection()
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

    def select_user(self, username: str) -> None:
        for i in range(self.user_list.count()):
            item = self.user_list.item(i)
            if item and item.text() == username:
                self.user_list.setCurrentItem(item)
                break