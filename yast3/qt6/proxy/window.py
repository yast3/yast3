"""UI components for the Proxy module."""

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

from yast3.core.i18n import _
from yast3.core.proxy import ProxyConfig, load_proxy_config, save_proxy_config

PROXY_FILE = "/etc/sysconfig/proxy"


class ProxyWindow(QMainWindow):
    closed = Signal()

    def __init__(self):
        super().__init__()
        self.resize(640, 360)
        self.setWindowTitle(_("Proxy Configuration — YaST3"))

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        self.enabled_check = QCheckBox(_("Enable Proxy"))
        layout.addWidget(self.enabled_check)

        self.http_edit = self._add_input(layout, _("HTTP Proxy"), _("http://host:port"))
        self.https_edit = self._add_input(layout, _("HTTPS Proxy"), _("http://host:port"))
        self.ftp_edit = self._add_input(layout, _("FTP Proxy"), _("http://host:port"))
        self.no_proxy_edit = self._add_input(
            layout,
            _("No Proxy"),
            _("localhost,127.0.0.1,.example.com"),
        )

        button_layout = QHBoxLayout()
        button_layout.addStretch()

        self.save_btn = QPushButton(_("Save"))
        self.save_btn.clicked.connect(self.save_proxy)
        button_layout.addWidget(self.save_btn)

        layout.addLayout(button_layout)

        self.load_proxy()

    def _add_input(self, layout: QVBoxLayout, label: str, placeholder: str) -> QLineEdit:
        row = QHBoxLayout()
        row.addWidget(QLabel(label))
        edit = QLineEdit()
        edit.setPlaceholderText(placeholder)
        row.addWidget(edit)
        layout.addLayout(row)
        return edit

    def load_proxy(self) -> None:
        try:
            config = load_proxy_config()
            self.enabled_check.setChecked(config.enabled)
            self.http_edit.setText(config.http_proxy)
            self.https_edit.setText(config.https_proxy)
            self.ftp_edit.setText(config.ftp_proxy)
            self.no_proxy_edit.setText(config.no_proxy)
        except FileNotFoundError:
            QMessageBox.warning(self, _("Error"), _("{0} not found.").format(PROXY_FILE))
        except PermissionError:
            QMessageBox.warning(
                self,
                _("Error"),
                _("Cannot read {0}. Root permission required.").format(PROXY_FILE),
            )
        except Exception as e:
            QMessageBox.warning(
                self,
                _("Error"),
                _("Failed to load proxy configuration: {0}").format(str(e)),
            )

    def save_proxy(self) -> None:
        config = ProxyConfig(
            enabled=self.enabled_check.isChecked(),
            http_proxy=self.http_edit.text().strip(),
            https_proxy=self.https_edit.text().strip(),
            ftp_proxy=self.ftp_edit.text().strip(),
            no_proxy=self.no_proxy_edit.text().strip(),
        )

        status, message = save_proxy_config(config)

        if status == "ok":
            QMessageBox.information(
                self,
                _("Success"),
                _("Proxy configuration saved successfully."),
            )
            self.close()
        elif status == "permission_denied":
            QMessageBox.critical(
                self,
                _("Error"),
                _("Permission denied. Root permission required."),
            )
        elif status == "pkexec_failed":
            QMessageBox.critical(
                self,
                _("Error"),
                _("Authentication failed or pkexec not available."),
            )
        else:
            QMessageBox.critical(
                self,
                _("Error"),
                _("Failed to save proxy configuration: {0}").format(message),
            )

    def closeEvent(self, event) -> None:
        self.closed.emit()
        self.deleteLater()
