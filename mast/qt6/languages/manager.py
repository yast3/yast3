"""Locale manager widget for Qt6."""

from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QHBoxLayout,
    QHeaderView,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from mast.core.i18n import _
from mast.core.languages import LocaleItem, build_locale_install_command, build_locale_remove_command, refresh_locale_cache, get_all_locales
from mast.qt6.command.action import CommandAction


class LocaleManager(QWidget):
    def __init__(self, locales: list[LocaleItem], parent: QWidget | None = None):
        super().__init__(parent)
        self._all_locales = locales
        self._setup_ui()

    def _setup_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setSpacing(8)

        self.search_edit = QLineEdit()
        self.search_edit.setPlaceholderText(_("Search"))
        self.search_edit.setClearButtonEnabled(True)
        self.search_edit.textChanged.connect(self._on_search_changed)
        layout.addWidget(self.search_edit)

        button_layout = QHBoxLayout()

        self.install_btn = QPushButton(_("Install"))
        self.install_btn.clicked.connect(self.install_selected)
        self.install_btn.setEnabled(False)
        button_layout.addWidget(self.install_btn)

        self.uninstall_btn = QPushButton(_("Uninstall"))
        self.uninstall_btn.clicked.connect(self.uninstall_selected)
        self.uninstall_btn.setEnabled(False)
        button_layout.addWidget(self.uninstall_btn)

        layout.addLayout(button_layout)

        self.table = QTableWidget()
        self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels([
            _("Code"),
            _("Name"),
            _("Status"),
        ])

        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Interactive)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)

        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        self.table.selectionModel().selectionChanged.connect(self._on_selection_changed)

        layout.addWidget(self.table)

        self._filter_locales("")

    def _on_selection_changed(self) -> None:
        selected = self.table.currentRow() >= 0
        if selected:
            status_item = self.table.item(self.table.currentRow(), 2)
            is_installed = status_item and status_item.text() == _("Installed")
            self.install_btn.setEnabled(not is_installed)
            self.uninstall_btn.setEnabled(is_installed)
        else:
            self.install_btn.setEnabled(False)
            self.uninstall_btn.setEnabled(False)

    def _on_search_changed(self, text: str) -> None:
        self._filter_locales(text)

    def _filter_locales(self, search_text: str) -> None:
        search_text = search_text.lower().strip()

        if not search_text:
            filtered = self._all_locales
        else:
            filtered = [
                loc for loc in self._all_locales
                if search_text in loc.code.lower() or search_text in loc.name.lower()
            ]

        self.table.setRowCount(0)
        self.table.setRowCount(len(filtered))

        for row, loc in enumerate(filtered):
            self.table.setItem(row, 0, QTableWidgetItem(loc.code))
            self.table.setItem(row, 1, QTableWidgetItem(loc.name))
            status_text = _("Installed") if loc.installed else _("Not Installed")
            status_item = QTableWidgetItem(status_text)
            if loc.installed:
                status_item.setForeground(Qt.GlobalColor.green)
            self.table.setItem(row, 2, status_item)

        self.table.resizeColumnsToContents()
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Interactive)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)

    def refresh_locales(self) -> None:
        try:
            refresh_locale_cache()
            self._all_locales = get_all_locales()
            self._filter_locales(self.search_edit.text())
        except Exception as e:
            QMessageBox.warning(self, _("Error"), _("Failed to load locales: {0}").format(str(e)))

    def _reload_after_action(self, success: bool, _error: str, _stdout: str) -> None:
        if success:
            self.refresh_locales()

    def install_selected(self) -> None:
        current_row = self.table.currentRow()
        if current_row < 0:
            QMessageBox.information(self, _("Information"), _("Please select a locale to install."))
            return

        locale_code = self.table.item(current_row, 0).text()
        locale_name = self.table.item(current_row, 1).text()

        reply = QMessageBox.question(
            self,
            _("Confirm"),
            _("Are you sure you want to install locale '{0}' ({1})?").format(locale_name, locale_code),
        )
        if reply != QMessageBox.StandardButton.Yes:
            return

        self.current_action = CommandAction(
            text=_("Install"),
            running_text=_("Installing..."),
            dialog_title=_("Install Language"),
            command=build_locale_install_command(locale_code),
            success_output=_("Language '{0}' installed successfully.").format(locale_name),
            parent=self,
        )
        self.current_action.action_finished.connect(self._reload_after_action)
        self.current_action.start_action()

    def uninstall_selected(self) -> None:
        current_row = self.table.currentRow()
        if current_row < 0:
            QMessageBox.information(self, _("Information"), _("Please select a language to uninstall."))
            return

        locale_code = self.table.item(current_row, 0).text()
        locale_name = self.table.item(current_row, 1).text()

        reply = QMessageBox.question(
            self,
            _("Confirm"),
            _("Are you sure you want to uninstall language '{0}' ({1})?").format(locale_name, locale_code),
        )
        if reply != QMessageBox.StandardButton.Yes:
            return

        self.current_action = CommandAction(
            text=_("Uninstall"),
            running_text=_("Uninstalling..."),
            dialog_title=_("Uninstall Language"),
            command=build_locale_remove_command(locale_code),
            success_output=_("Language '{0}' uninstalled successfully.").format(locale_name),
            parent=self,
        )
        self.current_action.action_finished.connect(self._reload_after_action)
        self.current_action.start_action()
