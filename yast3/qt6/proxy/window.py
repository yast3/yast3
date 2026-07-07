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
from yast3.core.proxy import ProxyConfig

PROXY_FILE = "/etc/sysconfig/proxy"


class ProxyWindow(QMainWindow):
    closed = Signal()
    config: ProxyConfig

    def __init__(self):
        super().__init__()
        self.resize(640, 320)
        self.setWindowTitle(_("{} — YaST3").format(_("Proxy")))

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(12)

        self.enabled_check = QCheckBox(_("Enable Proxy"))
        layout.addWidget(self.enabled_check)

        self.http_edit = self._add_input(layout, _("HTTP Proxy"), "http://host:port")
        self.https_edit = self._add_input(layout, _("HTTPS Proxy"), "http://host:port")
        self.ftp_edit = self._add_input(layout, _("FTP Proxy"), "http://host:port")
        self.socks_edit = self._add_input(layout, _("SOCKS Proxy"), "socks://host:port")
        self.no_proxy_edit = self._add_input(
            layout,
            _("No Proxy"),
            "localhost,127.0.0.1,.example.com",
        )

        button_layout = QHBoxLayout()
        button_layout.setSpacing(12)
        button_layout.addStretch()

        self.save_btn = QPushButton(_("Save"))
        self.save_btn.clicked.connect(self.save_proxy)
        button_layout.addWidget(self.save_btn)

        layout.addLayout(button_layout)

        self.load_proxy()

    def _add_input(self, layout: QVBoxLayout, label: str, placeholder: str) -> QLineEdit:
        row = QHBoxLayout()
        row.setSpacing(12)
        row.addWidget(QLabel(label))
        edit = QLineEdit()
        edit.setPlaceholderText(placeholder)
        row.addWidget(edit)
        layout.addLayout(row)
        return edit

    def load_proxy(self) -> None:
        try:
            self.config = ProxyConfig()
            self.enabled_check.setChecked(self.config.PROXY_ENABLED == "yes")
            self.http_edit.setText(self.config.HTTP_PROXY)
            self.https_edit.setText(self.config.HTTPS_PROXY)
            self.ftp_edit.setText(self.config.FTP_PROXY)
            self.socks_edit.setText(self.config.SOCKS_PROXY)
            self.no_proxy_edit.setText(self.config.NO_PROXY)
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
        self.config.PROXY_ENABLED = "yes" if self.enabled_check.isChecked() else "no"
        self.config.HTTP_PROXY = self.http_edit.text().strip()
        self.config.HTTPS_PROXY = self.https_edit.text().strip()
        self.config.FTP_PROXY = self.ftp_edit.text().strip()
        self.config.SOCKS_PROXY = self.socks_edit.text().strip()
        self.config.NO_PROXY = self.no_proxy_edit.text().strip()

        try:
            self.config.write_pkexec()
            QMessageBox.information(
                self,
                _("Success"),
                _("Proxy configuration saved successfully."),
            )
            self.close()
        except PermissionError:
            QMessageBox.critical(
                self,
                _("Error"),
                _("Permission denied. Root permission required."),
            )
        except Exception as e:
            QMessageBox.critical(
                self,
                _("Error"),
                _("Failed to save proxy configuration: {0}").format(str(e)),
            )

    def closeEvent(self, event) -> None:
        self.closed.emit()
        self.deleteLater()
