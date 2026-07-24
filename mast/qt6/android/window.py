"""UI components for the Android module (Qt6)."""

from __future__ import annotations

import os
import threading

from PySide6.QtCore import Qt, Signal, Slot
from PySide6.QtWidgets import QMessageBox
from PySide6.QtWidgets import (
    QAbstractItemView,
    QCheckBox,
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QSplitter,
    QTabWidget,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from mast.core.android import (
    DeviceInfo,
    PackageInfo,
    get_blacklist_info,
    install_apk,
    is_adb_available,
    is_dangerous,
    is_in_blacklist,
    list_devices,
    list_packages,
    uninstall_package,
)
from mast.core.i18n import _


class AndroidWindow(QMainWindow):
    devices_loaded = Signal(list)
    packages_loaded = Signal(list)
    show_message = Signal(str, str, str)
    update_busy = Signal(bool)

    def __init__(self):
        super().__init__()

        self.devices: list[DeviceInfo] = []
        self.packages: list[PackageInfo] = []
        self.selected_device: DeviceInfo | None = None
        self._busy = False

        self.setWindowTitle(_("Android Device Manager"))
        self.setMinimumSize(1280, 720)

        if not is_adb_available():
            self._show_adb_not_found()
            return

        self._build_ui()
        self._connect_signals()
        self._load_devices()

    def _build_ui(self) -> None:
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)

        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.setStretchFactor(0, 1)
        splitter.setStretchFactor(1, 3)
        splitter.setHandleWidth(10)
        main_layout.addWidget(splitter)

        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        left_layout.setSpacing(8)
        left_layout.setContentsMargins(8, 8, 8, 8)
        splitter.addWidget(left_panel)

        device_header = QHBoxLayout()
        device_label = QLabel(_("Devices"))
        device_header.addWidget(device_label)
        device_header.addStretch()

        self.refresh_btn = QPushButton(_("Refresh"))
        device_header.addWidget(self.refresh_btn)
        left_layout.addLayout(device_header)

        self.device_list = QListWidget()
        self.device_list.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        left_layout.addWidget(self.device_list)

        self.tab_widget = QTabWidget()
        splitter.addWidget(self.tab_widget)

        self.info_tab = QWidget()
        self.tab_widget.addTab(self.info_tab, _("Device Info"))
        self._build_info_tab()

        self.packages_tab = QWidget()
        self.tab_widget.addTab(self.packages_tab, _("Packages"))
        self._build_packages_tab()

    def _build_info_tab(self) -> None:
        layout = QVBoxLayout(self.info_tab)
        layout.setSpacing(8)
        layout.setContentsMargins(16, 16, 16, 16)

        grid_layout = QHBoxLayout()

        labels = [
            (_("Serial"), 0),
            (_("Name"), 1),
            (_("Model"), 2),
            (_("Manufacturer"), 3),
            (_("Android Version"), 4),
            (_("API Level"), 5),
            (_("Status"), 6),
        ]

        self.info_labels: list[QLabel] = []

        for i, (label_text, _row) in enumerate(labels):
            row_layout = QHBoxLayout()
            label = QLabel(label_text + ":")
            label.setFixedWidth(120)
            row_layout.addWidget(label)
            value_label = QLabel("")
            value_label.setWordWrap(True)
            row_layout.addWidget(value_label)
            self.info_labels.append(value_label)
            layout.addLayout(row_layout)

        layout.addStretch()

    def _build_packages_tab(self) -> None:
        layout = QVBoxLayout(self.packages_tab)
        layout.setSpacing(8)
        layout.setContentsMargins(8, 8, 8, 8)

        filter_layout = QHBoxLayout()

        self.search_entry = QLineEdit()
        self.search_entry.setPlaceholderText(_("Search packages"))
        filter_layout.addWidget(self.search_entry)

        filter_layout.addStretch()

        self.blacklist_only = QCheckBox(_("Blacklist only"))
        filter_layout.addWidget(self.blacklist_only)

        self.system_only = QCheckBox(_("System apps"))
        filter_layout.addWidget(self.system_only)

        self.user_only = QCheckBox(_("User apps"))
        filter_layout.addWidget(self.user_only)

        layout.addLayout(filter_layout)

        action_layout = QHBoxLayout()

        self.uninstall_btn = QPushButton(_("Uninstall"))
        self.uninstall_btn.setEnabled(False)
        action_layout.addWidget(self.uninstall_btn)

        self.install_btn = QPushButton(_("Install APK"))
        action_layout.addWidget(self.install_btn)

        self.refresh_pkgs_btn = QPushButton(_("Refresh"))
        action_layout.addWidget(self.refresh_pkgs_btn)

        action_layout.addStretch()
        layout.addLayout(action_layout)

        self.package_table = QTableWidget()
        self.package_table.setColumnCount(4)
        self.package_table.setHorizontalHeaderLabels([
            _("Package"),
            _("Name"),
            _("Version"),
            _("Type"),
        ])
        self.package_table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.package_table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.package_table.horizontalHeader().setStretchLastSection(True)
        layout.addWidget(self.package_table)

    def _connect_signals(self) -> None:
        self.refresh_btn.clicked.connect(self._load_devices)
        self.device_list.currentRowChanged.connect(self._on_device_selected)
        self.search_entry.textChanged.connect(self._apply_package_filters)
        self.blacklist_only.stateChanged.connect(self._apply_package_filters)
        self.system_only.stateChanged.connect(self._apply_package_filters)
        self.user_only.stateChanged.connect(self._apply_package_filters)
        self.uninstall_btn.clicked.connect(self._uninstall_selected)
        self.install_btn.clicked.connect(self._install_apk)
        self.refresh_pkgs_btn.clicked.connect(self._load_packages)
        self.package_table.itemSelectionChanged.connect(self._on_package_selected)

        self.devices_loaded.connect(self._on_devices_loaded)
        self.packages_loaded.connect(self._on_packages_loaded)
        self.show_message.connect(self._show_message_dialog)
        self.update_busy.connect(self._set_busy)

    def _show_adb_not_found(self) -> None:
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        layout.setSpacing(16)
        layout.setContentsMargins(32, 32, 32, 32)

        label = QLabel(_("ADB Not Found"))
        label.setStyleSheet("font-size: 18pt; font-weight: bold;")
        layout.addWidget(label)

        desc = QLabel(_("ADB (Android Debug Bridge) is not installed or not in PATH. Please install Android SDK platform tools."))
        desc.setWordWrap(True)
        layout.addWidget(desc)

    def _load_devices(self) -> None:
        if self._busy:
            return
        self._busy = True
        self.refresh_btn.setEnabled(False)

        def worker():
            try:
                devices = list_devices()
                self.devices_loaded.emit(devices)
            except Exception as e:
                self.show_message.emit("error", _("Error"), str(e))
            finally:
                self.update_busy.emit(False)

        threading.Thread(target=worker, daemon=True).start()

    @Slot(list)
    def _on_devices_loaded(self, devices: list[DeviceInfo]) -> None:
        self.devices = devices
        self.device_list.clear()

        for device in devices:
            status_text = device.status
            if device.status == "device":
                status_text = _("Connected")
            elif device.status == "offline":
                status_text = _("Offline")
            elif device.status == "unauthorized":
                status_text = _("Unauthorized")

            item_text = f"{device.name} ({device.model}) - {status_text}"
            item = QListWidgetItem(item_text)
            self.device_list.addItem(item)

        if devices:
            self.device_list.setCurrentRow(0)
        else:
            self._clear_device_selection()

    def _clear_device_selection(self) -> None:
        self.selected_device = None
        for label in self.info_labels:
            label.setText("")
        self.package_table.setRowCount(0)
        self.uninstall_btn.setEnabled(False)

    @Slot(int)
    def _on_device_selected(self, row: int) -> None:
        if row < 0 or row >= len(self.devices):
            self._clear_device_selection()
            return

        device = self.devices[row]
        self.selected_device = device
        self._update_device_info(device)

        if device.status == "device":
            self._load_packages()
        else:
            self.package_table.setRowCount(0)
            self.uninstall_btn.setEnabled(False)

    def _update_device_info(self, device: DeviceInfo) -> None:
        self.info_labels[0].setText(device.serial)
        self.info_labels[1].setText(device.name)
        self.info_labels[2].setText(device.model)
        self.info_labels[3].setText(device.manufacturer)
        self.info_labels[4].setText(device.android_version)
        self.info_labels[5].setText(device.api_level)

        status_text = device.status
        if device.status == "device":
            status_text = _("Connected")
        elif device.status == "offline":
            status_text = _("Offline")
        elif device.status == "unauthorized":
            status_text = _("Unauthorized")
        self.info_labels[6].setText(status_text)

    def _load_packages(self) -> None:
        if not self.selected_device or self.selected_device.status != "device":
            return

        if self._busy:
            return
        self._busy = True
        self.refresh_pkgs_btn.setEnabled(False)
        self.install_btn.setEnabled(False)

        device = self.selected_device

        def worker():
            try:
                packages = list_packages(device.serial)
                packages.sort(key=lambda p: (not is_in_blacklist(p.package_name), p.app_name.lower()))
                self.packages_loaded.emit(packages)
            except Exception as e:
                self.show_message.emit("error", _("Error"), str(e))
            finally:
                self.update_busy.emit(False)

        threading.Thread(target=worker, daemon=True).start()

    @Slot(list)
    def _on_packages_loaded(self, packages: list[PackageInfo]) -> None:
        self.packages = packages
        self._apply_package_filters()

    def _apply_package_filters(self) -> None:
        search_text = self.search_entry.text().strip().lower()
        show_blacklist = self.blacklist_only.isChecked()
        show_system = self.system_only.isChecked()
        show_user = self.user_only.isChecked()

        self.package_table.setRowCount(0)

        for pkg in self.packages:
            if show_blacklist and not is_in_blacklist(pkg.package_name):
                continue

            if show_system and show_user:
                pass
            elif show_system and not pkg.is_system:
                continue
            elif show_user and pkg.is_system:
                continue

            if search_text:
                haystack = f"{pkg.package_name} {pkg.app_name}".lower()
                if search_text not in haystack:
                    continue

            pkg_type = _("System") if pkg.is_system else _("User")
            if is_in_blacklist(pkg.package_name):
                pkg_type = _("Blacklist")

            row = self.package_table.rowCount()
            self.package_table.insertRow(row)

            self.package_table.setItem(row, 0, QTableWidgetItem(pkg.package_name))
            self.package_table.setItem(row, 1, QTableWidgetItem(pkg.app_name))
            self.package_table.setItem(row, 2, QTableWidgetItem(pkg.version_name))
            self.package_table.setItem(row, 3, QTableWidgetItem(pkg_type))

        self.uninstall_btn.setEnabled(False)

    def _on_package_selected(self) -> None:
        selected = self.package_table.selectedItems()
        self.uninstall_btn.setEnabled(len(selected) > 0)

    def _uninstall_selected(self) -> None:
        selected = self.package_table.selectedItems()
        if not selected:
            return

        row = selected[0].row()
        if row < 0 or row >= self.package_table.rowCount():
            return

        pkg_item = self.package_table.item(row, 0)
        app_item = self.package_table.item(row, 1)
        if pkg_item is None or app_item is None:
            return
        pkg_name = pkg_item.text()
        app_name = app_item.text()

        blacklist_info = get_blacklist_info(pkg_name)
        if blacklist_info:
            if is_dangerous(pkg_name):
                msg = _('Are you sure you want to uninstall "{0}" ({1})?\n\nWARNING: This package is marked as dangerous. Uninstalling it may cause system instability or prevent the device from booting!').format(app_name, pkg_name)
            else:
                msg = _('Are you sure you want to uninstall "{0}" ({1})?\n\nThis is a known bloatware package and can be safely removed.').format(app_name, pkg_name)
        else:
            msg = _('Are you sure you want to uninstall "{0}" ({1})?\n\nThis may affect system functionality.').format(app_name, pkg_name)

        reply = QMessageBox.question(
            self,
            _("Uninstall Package"),
            msg,
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )

        if reply == QMessageBox.StandardButton.Yes:
            self._do_uninstall(pkg_name)

    def _do_uninstall(self, pkg_name: str) -> None:
        device = self.selected_device
        if not device:
            return

        if self._busy:
            return
        self._busy = True

        def worker():
            try:
                success = uninstall_package(device.serial, pkg_name)
                if success:
                    self.show_message.emit("success", _("Success"), _('Package "{0}" uninstalled successfully.').format(pkg_name))
                    self._load_packages()
                else:
                    self.show_message.emit("error", _("Error"), _('Failed to uninstall "{0}". Device may require root access.').format(pkg_name))
            except Exception as e:
                self.show_message.emit("error", _("Error"), str(e))
            finally:
                self.update_busy.emit(False)

        threading.Thread(target=worker, daemon=True).start()

    def _install_apk(self) -> None:
        file_path, _filter = QFileDialog.getOpenFileName(
            self,
            _("Select APK File"),
            "",
            _("APK Files (*.apk);;All Files (*)"),
        )

        if not file_path or not os.path.exists(file_path):
            return

        self._do_install(file_path)

    def _do_install(self, apk_path: str) -> None:
        device = self.selected_device
        if not device:
            return

        if self._busy:
            return
        self._busy = True

        def worker():
            try:
                success = install_apk(device.serial, apk_path)
                if success:
                    self.show_message.emit("success", _("Success"), _('APK "{0}" installed successfully.').format(os.path.basename(apk_path)))
                    self._load_packages()
                else:
                    self.show_message.emit("error", _("Error"), _('Failed to install "{0}".').format(os.path.basename(apk_path)))
            except Exception as e:
                self.show_message.emit("error", _("Error"), str(e))
            finally:
                self.update_busy.emit(False)

        threading.Thread(target=worker, daemon=True).start()

    @Slot(bool)
    def _set_busy(self, busy: bool) -> None:
        self._busy = busy
        self.refresh_btn.setEnabled(not busy)
        self.refresh_pkgs_btn.setEnabled(not busy)
        self.install_btn.setEnabled(not busy and self.selected_device is not None and self.selected_device.status == "device")

    @Slot(str, str, str)
    def _show_message_dialog(self, msg_type: str, title: str, message: str) -> None:
        if msg_type == "error":
            QMessageBox.critical(self, title, message)
        else:
            QMessageBox.information(self, title, message)

    def closeEvent(self, _event) -> None:
        self.deleteLater()