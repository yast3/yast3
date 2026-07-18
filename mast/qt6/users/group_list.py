"""Group list widget for Qt6."""

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

import grp
from mast.core.i18n import _
from mast.core.users import is_system_group, build_delete_group_command
from mast.qt6.command.action import CommandAction


class GroupList(QWidget):
    group_selected = Signal(grp.struct_group)
    group_added = Signal()

    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)
        self._groups: list[grp.struct_group] = []
        self._selected_group: grp.struct_group | None = None
        self._setup_ui()

    def _setup_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setSpacing(8)

        self.group_list = QTreeWidget()
        self.group_list.setColumnCount(1)
        self.group_list.setHeaderHidden(True)
        self.group_list.currentItemChanged.connect(self._on_group_selected)
        layout.addWidget(self.group_list)

        button_layout = QHBoxLayout()
        self.add_btn = QPushButton(_("Add"))
        self.add_btn.clicked.connect(self._on_add_group)
        button_layout.addWidget(self.add_btn)

        self.delete_btn = QPushButton(_("Delete"))
        self.delete_btn.clicked.connect(self._on_delete_group)
        self.delete_btn.setEnabled(False)
        button_layout.addWidget(self.delete_btn)

        layout.addLayout(button_layout)

    def set_groups(self, groups: list[grp.struct_group]) -> None:
        self._groups = groups
        self._populate_group_list()

    def _populate_group_list(self) -> None:
        self.group_list.clear()

        system_group_item = QTreeWidgetItem([_("System Groups")])
        system_group_item.setExpanded(True)
        system_group_item.setFlags(system_group_item.flags() & ~Qt.ItemFlag.ItemIsSelectable)

        user_group_item = QTreeWidgetItem([_("User Groups")])
        user_group_item.setExpanded(True)
        user_group_item.setFlags(user_group_item.flags() & ~Qt.ItemFlag.ItemIsSelectable)

        users_item = None
        for group in self._groups:
            item = QTreeWidgetItem([group.gr_name])
            item.setData(0, Qt.ItemDataRole.UserRole, group)
            if group.gr_name == "users":
                users_item = item
            if is_system_group(group):
                system_group_item.addChild(item)
            else:
                user_group_item.addChild(item)

        self.group_list.addTopLevelItem(system_group_item)
        self.group_list.addTopLevelItem(user_group_item)

        if users_item:
            self.group_list.setCurrentItem(users_item)

    def _on_group_selected(self, current: QTreeWidgetItem | None, _previous: QTreeWidgetItem | None) -> None:
        if current:
            self._selected_group = current.data(0, Qt.ItemDataRole.UserRole)
            if self._selected_group:
                is_system = is_system_group(self._selected_group)
                self.delete_btn.setEnabled(not is_system)
                self.group_selected.emit(self._selected_group)
            else:
                self.delete_btn.setEnabled(False)
        else:
            self._selected_group = None
            self.delete_btn.setEnabled(False)
            self.group_selected.emit(None)

    def _on_add_group(self) -> None:
        self.group_list.clearSelection()
        self._selected_group = None
        self.delete_btn.setEnabled(False)
        self.group_added.emit()

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
        self.current_action.action_finished.connect(self._on_delete_finished)
        self.current_action.start_action()

    def _on_delete_finished(self, success: bool, _error: str, _stdout: str) -> None:
        if success:
            self._selected_group = None
            self.delete_btn.setEnabled(False)