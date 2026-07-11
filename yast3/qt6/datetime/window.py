"""UI components for the Date & Time module (Qt6)."""

from __future__ import annotations

from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QCheckBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from yast3.qt6.searchable_combobox import SearchableComboBox
from yast3.core.i18n import _
from yast3.core.datetime import (
    get_current_timezone,
    get_timezone_list,
    set_timezone,
    is_hwclock_utc,
    set_hwclock_utc,
    get_ntp_status,
    get_ntp_servers,
    set_ntp_servers,
    enable_ntp,
    disable_ntp,
    sync_time_now,
)


class DateTimeWindow(QMainWindow):
    closed = Signal()

    def __init__(self):
        super().__init__()

        self.setWindowTitle(_("{} — YaST3").format(_("Date & Time")))
        self.resize(600, 500)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        layout.setSpacing(12)
        layout.setContentsMargins(16, 16, 16, 16)

        self._create_timezone_section(layout)
        self._create_hwclock_section(layout)
        self._create_ntp_section(layout)

        self._create_save_button(layout)

        self._load_settings()

    def _create_timezone_section(self, parent_layout):
        group_layout = QVBoxLayout()
        group_layout.setSpacing(8)

        input_layout = QHBoxLayout()
        input_layout.setSpacing(8)

        label = QLabel(_("Timezone"))
        label.setFixedWidth(120)
        input_layout.addWidget(label)

        self.timezone_combo = SearchableComboBox()
        self.timezone_combo.setMinimumWidth(300)

        input_layout.addWidget(self.timezone_combo)

        group_layout.addLayout(input_layout)

        parent_layout.addLayout(group_layout)

    def _create_hwclock_section(self, parent_layout):
        group_layout = QVBoxLayout()
        group_layout.setSpacing(8)

        switch_layout = QHBoxLayout()
        switch_layout.setSpacing(8)

        self.hwclock_checkbox = QCheckBox(_("Set hardware clock to UTC"))
        switch_layout.addWidget(self.hwclock_checkbox)

        group_layout.addLayout(switch_layout)

        parent_layout.addLayout(group_layout)

    def _create_ntp_section(self, parent_layout):
        group_layout = QVBoxLayout()
        group_layout.setSpacing(8)

        ntp_switch_layout = QHBoxLayout()
        ntp_switch_layout.setSpacing(8)

        self.ntp_checkbox = QCheckBox(_("Enable NTP synchronization"))
        ntp_switch_layout.addWidget(self.ntp_checkbox)

        group_layout.addLayout(ntp_switch_layout)

        servers_layout = QHBoxLayout()
        servers_layout.setSpacing(8)

        servers_label = QLabel(_("NTP Servers"))
        servers_label.setFixedWidth(120)
        servers_layout.addWidget(servers_label)

        self.ntp_entry = QLineEdit()
        self.ntp_entry.setPlaceholderText(_("Enter NTP servers separated by spaces"))
        servers_layout.addWidget(self.ntp_entry)

        group_layout.addLayout(servers_layout)

        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(8)

        self.sync_now_btn = QPushButton(_("Sync Now"))
        self.sync_now_btn.clicked.connect(self._on_sync_now)
        btn_layout.addWidget(self.sync_now_btn)

        group_layout.addLayout(btn_layout)

        self.ntp_status_label = QLabel("")
        group_layout.addWidget(self.ntp_status_label)

        parent_layout.addLayout(group_layout)

    def _create_save_button(self, parent_layout):
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(8)
        btn_layout.addStretch()

        self.save_btn = QPushButton(_("Save"))
        self.save_btn.clicked.connect(self._on_save_all)
        btn_layout.addWidget(self.save_btn)

        parent_layout.addLayout(btn_layout)

    def _load_settings(self):
        try:
            timezone = get_current_timezone()
            self.all_timezones = sorted(get_timezone_list())

            self.timezone_combo.set_items(self.all_timezones)
            self.timezone_combo.set_current_item(timezone)
        except Exception as e:
            QMessageBox.warning(self, _("Error"), _("Failed to load timezone: {0}").format(str(e)))

        try:
            utc = is_hwclock_utc()
            self.hwclock_checkbox.setChecked(utc)
        except Exception as e:
            QMessageBox.warning(self, _("Error"), _("Failed to load hardware clock setting: {0}").format(str(e)))

        try:
            ntp_status = get_ntp_status()
            self.ntp_checkbox.setChecked(ntp_status.enabled)
            self.ntp_entry.setText(" ".join(ntp_status.servers))

            if ntp_status.synchronized:
                self.ntp_status_label.setText(_("NTP synchronized"))
            else:
                self.ntp_status_label.setText(_("NTP not synchronized"))
        except Exception as e:
            QMessageBox.warning(self, _("Error"), _("Failed to load NTP status: {0}").format(str(e)))

    def _on_save_all(self):
        errors = []

        timezone = self.timezone_combo.currentText()
        if timezone:
            status, message = set_timezone(timezone)
            if status != "ok":
                errors.append(_("Timezone: {0}").format(message))

        utc = self.hwclock_checkbox.isChecked()
        status, message = set_hwclock_utc(utc)
        if status != "ok":
            errors.append(_("Hardware clock: {0}").format(message))

        enabled = self.ntp_checkbox.isChecked()
        servers = self.ntp_entry.text().strip().split()
        if enabled:
            if not servers:
                servers = ["pool.ntp.org"]
            status, message = set_ntp_servers(servers)
            if status == "ok":
                status2, message2 = enable_ntp()
                if status2 != "ok":
                    errors.append(_("NTP: {0}").format(message2))
            else:
                errors.append(_("NTP: {0}").format(message))
        else:
            status, message = disable_ntp()
            if status != "ok":
                errors.append(_("NTP: {0}").format(message))

        if errors:
            QMessageBox.critical(self, _("Error"), "\n".join(errors))
        else:
            QMessageBox.information(self, _("Success"), _("All settings saved successfully."))

    def _on_sync_now(self):
        status, message = sync_time_now()

        if status == "ok":
            QMessageBox.information(self, _("Success"), message)
            self._load_settings()
        elif status == "permission_denied":
            QMessageBox.critical(self, _("Error"), _("Permission denied. Root permission required."))
        elif status == "pkexec_failed":
            QMessageBox.critical(self, _("Error"), _("Authentication failed or pkexec not available."))
        else:
            QMessageBox.critical(self, _("Error"), message)

    def closeEvent(self, _event):
        self.closed.emit()
        self.deleteLater()