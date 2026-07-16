"""UI components for the Journal module (Qt6)."""

from __future__ import annotations

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QColor
from PySide6.QtWidgets import (
    QComboBox,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QLineEdit,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QTabWidget,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
    QGridLayout,
    QCheckBox,
)

from mast.core.i18n import _
from mast.core.journal import (
    JournalEntry,
    JournalConfig,
    get_journal_entries,
    get_journal_config,
    set_journal_config,
    clear_journal,
    PRIORITY_LEVELS,
)


class JournalWindow(QMainWindow):
    """Qt6 window for managing journal logs."""

    closed = Signal()

    def __init__(self):
        super().__init__()
        self.resize(1280, 720)

        self.system_entries: list[JournalEntry] = []
        self.user_entries: list[JournalEntry] = []
        self.current_scope = "system"
        self.config: JournalConfig | None = None

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(12)

        self._create_tabs(layout)

    def _create_tabs(self, parent_layout: QVBoxLayout) -> None:
        self.tab_widget = QTabWidget()

        system_page = QWidget()
        system_layout = QVBoxLayout(system_page)
        system_layout.setSpacing(12)
        self._create_log_page(system_layout, "system")
        self.tab_widget.addTab(system_page, _("System"))

        user_page = QWidget()
        user_layout = QVBoxLayout(user_page)
        user_layout.setSpacing(12)
        self._create_log_page(user_layout, "user")
        self.tab_widget.addTab(user_page, _("User"))

        config_page = QWidget()
        config_layout = QVBoxLayout(config_page)
        config_layout.setSpacing(12)
        self._create_config_page(config_layout)
        self.tab_widget.addTab(config_page, _("Configuration"))

        self.tab_widget.currentChanged.connect(self._on_tab_changed)
        parent_layout.addWidget(self.tab_widget)

    def _create_log_page(self, layout: QVBoxLayout, scope: str) -> None:
        filters_layout = QHBoxLayout()
        filters_layout.setSpacing(12)

        filters_layout.addWidget(QLabel(_("Priority")))
        priority_filter = QComboBox()
        priority_filter.addItem(_("All"), "all")
        for level in PRIORITY_LEVELS:
            priority_filter.addItem(level.capitalize(), level)

        filters_layout.addWidget(QLabel(_("Search")))
        search_edit = QLineEdit()
        search_edit.setPlaceholderText(_("Search messages"))
        filters_layout.addWidget(search_edit, 1)

        refresh_btn = QPushButton(_("Refresh"))
        filters_layout.addWidget(refresh_btn)

        layout.addLayout(filters_layout)

        actions_layout = QHBoxLayout()
        actions_layout.setSpacing(12)

        clear_btn = QPushButton(_("Clear"))
        actions_layout.addWidget(clear_btn)

        actions_layout.addStretch()
        layout.addLayout(actions_layout)

        table = QTableWidget()
        table.setColumnCount(5)
        table.setHorizontalHeaderLabels(
            [_("Time"), _("Priority"), _("Unit"), _("Message"), _("PID")]
        )
        table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        table.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        table.setAlternatingRowColors(True)

        table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeMode.Stretch)
        table.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)

        layout.addWidget(table)

        priority_filter.currentIndexChanged.connect(
            lambda: self.apply_filters(scope)
        )
        search_edit.textChanged.connect(lambda: self.apply_filters(scope))
        refresh_btn.clicked.connect(lambda: self.load_journal(scope))
        clear_btn.clicked.connect(lambda: self._clear_journal(scope))

        if scope == "system":
            self.system_priority_filter = priority_filter
            self.system_search_edit = search_edit
            self.system_table = table
        else:
            self.user_priority_filter = priority_filter
            self.user_search_edit = search_edit
            self.user_table = table

    def _create_config_page(self, layout: QVBoxLayout) -> None:
        grid = QGridLayout()
        grid.setSpacing(12)

        row = 0

        grid.addWidget(QLabel(_("Max File Size (e.g., 500M, 1G)")), row, 0)
        self.max_size_entry = QLineEdit()
        self.max_size_entry.setPlaceholderText(_("SystemMaxUse"))
        grid.addWidget(self.max_size_entry, row, 1)
        row += 1

        grid.addWidget(QLabel(_("Max Number of Files")), row, 0)
        self.max_files_entry = QLineEdit()
        self.max_files_entry.setPlaceholderText(_("SystemMaxFiles"))
        grid.addWidget(self.max_files_entry, row, 1)
        row += 1

        grid.addWidget(QLabel(_("Compress")), row, 0)
        self.compress_checkbox = QCheckBox()
        grid.addWidget(self.compress_checkbox, row, 1)
        row += 1

        grid.addWidget(QLabel(_("Rate Limit Interval (e.g., 30s)")), row, 0)
        self.rate_interval_entry = QLineEdit()
        self.rate_interval_entry.setPlaceholderText(_("RateLimitInterval"))
        grid.addWidget(self.rate_interval_entry, row, 1)
        row += 1

        grid.addWidget(QLabel(_("Rate Limit Burst")), row, 0)
        self.rate_burst_entry = QLineEdit()
        self.rate_burst_entry.setPlaceholderText(_("RateLimitBurst"))
        grid.addWidget(self.rate_burst_entry, row, 1)
        row += 1

        self.save_config_btn = QPushButton(_("Save Configuration"))
        self.save_config_btn.clicked.connect(self._save_config)
        grid.addWidget(self.save_config_btn, row, 0, 1, 2)

        layout.addLayout(grid)
        layout.addStretch()

    def _on_tab_changed(self, index: int) -> None:
        if index == 0:
            self.current_scope = "system"
        elif index == 1:
            self.current_scope = "user"
        elif index == 2:
            self.load_config()

    def load_journal(self, scope: str) -> None:
        try:
            if scope == "system":
                self.system_entries = get_journal_entries(scope="system")
                self.apply_filters("system")
            else:
                self.user_entries = get_journal_entries(scope="user")
                self.apply_filters("user")
        except Exception as error:
            QMessageBox.critical(
                self,
                _("Error"),
                _("Failed to load journal: {0}").format(str(error)),
            )

    def apply_filters(self, scope: str) -> None:
        if scope == "system":
            priority_filter = self.system_priority_filter.currentData()
            search_text = self.system_search_edit.text().strip().lower()
            entries = self.system_entries
            table = self.system_table
        else:
            priority_filter = self.user_priority_filter.currentData()
            search_text = self.user_search_edit.text().strip().lower()
            entries = self.user_entries
            table = self.user_table

        filtered = []
        for entry in entries:
            if priority_filter not in (None, "all"):
                priority_idx = PRIORITY_LEVELS.index(priority_filter)
                if entry.priority_num > priority_idx:
                    continue
            if search_text and search_text not in entry.message.lower():
                continue
            filtered.append(entry)

        self.populate_table(table, filtered)

    def populate_table(self, table: QTableWidget, entries: list[JournalEntry]) -> None:
        table.setRowCount(len(entries))
        for row, entry in enumerate(entries):
            self._set_text_item(table, row, 0, entry.timestamp.strftime("%Y-%m-%d %H:%M:%S"))
            self._set_priority_item(table, row, 1, entry)
            self._set_text_item(table, row, 2, entry.systemd_unit)
            self._set_text_item(table, row, 3, entry.message)
            self._set_text_item(table, row, 4, str(entry.process_id) if entry.process_id else "")

    def _set_text_item(self, table: QTableWidget, row: int, column: int, text: str) -> None:
        item = QTableWidgetItem(text)
        item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)
        table.setItem(row, column, item)

    def _set_priority_item(self, table: QTableWidget, row: int, column: int, entry: JournalEntry) -> None:
        item = QTableWidgetItem(entry.priority.capitalize())
        item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)
        item.setForeground(QColor(entry.priority_color()))
        table.setItem(row, column, item)

    def load_config(self) -> None:
        try:
            self.config = get_journal_config()
            if self.config.max_file_size:
                self.max_size_entry.setText(self.config.max_file_size)
            if self.config.max_files:
                self.max_files_entry.setText(str(self.config.max_files))
            if self.config.compress is not None:
                self.compress_checkbox.setChecked(self.config.compress)
            if self.config.rate_limit_interval:
                self.rate_interval_entry.setText(self.config.rate_limit_interval)
            if self.config.rate_limit_burst:
                self.rate_burst_entry.setText(str(self.config.rate_limit_burst))
        except Exception as error:
            QMessageBox.critical(
                self,
                _("Error"),
                _("Failed to load configuration: {0}").format(str(error)),
            )

    def _save_config(self) -> None:
        config = JournalConfig()
        config.max_file_size = self.max_size_entry.text().strip() or None
        config.max_files = int(self.max_files_entry.text().strip()) if self.max_files_entry.text().strip() else None
        config.compress = self.compress_checkbox.isChecked()
        config.rate_limit_interval = self.rate_interval_entry.text().strip() or None
        config.rate_limit_burst = int(self.rate_burst_entry.text().strip()) if self.rate_burst_entry.text().strip() else None

        try:
            success = set_journal_config(config)
            if success:
                QMessageBox.information(
                    self,
                    _("Success"),
                    _("Journal configuration saved successfully."),
                )
            else:
                QMessageBox.critical(
                    self,
                    _("Error"),
                    _("Failed to save journal configuration."),
                )
        except Exception as error:
            QMessageBox.critical(
                self,
                _("Error"),
                _("Failed to save configuration: {0}").format(str(error)),
            )

    def _clear_journal(self, scope: str) -> None:
        reply = QMessageBox.warning(
            self,
            _("Clear Journal"),
            _("Are you sure you want to clear all journal logs?"),
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )

        if reply == QMessageBox.StandardButton.Yes:
            try:
                success = clear_journal(scope)
                if success:
                    QMessageBox.information(
                        self,
                        _("Success"),
                        _("Journal cleared successfully."),
                    )
                    self.load_journal(scope)
                else:
                    QMessageBox.critical(
                        self,
                        _("Error"),
                        _("Failed to clear journal."),
                    )
            except Exception as error:
                QMessageBox.critical(
                    self,
                    _("Error"),
                    _("Failed to clear journal: {0}").format(str(error)),
                )

    def closeEvent(self, _event) -> None:
        self.closed.emit()
        self.deleteLater()
