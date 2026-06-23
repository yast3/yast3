"""Dialog components for the Repositories module."""

from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QSpinBox,
    QVBoxLayout,
    QWidget,
)

from yast3.core.i18n import _
from yast3.core.modules.repositories import RepoEntry


class RepoEditDialog(QDialog):
    """Dialog for adding or editing a repository entry."""

    def __init__(self, parent: QWidget | None = None, entry: RepoEntry | None = None):
        super().__init__(parent)
        self.setWindowTitle(
            _("Add Repository") if entry is None else _("Edit Repository")
        )
        self.setMinimumWidth(500)

        layout = QVBoxLayout(self)

        # Repository ID
        id_layout = QHBoxLayout()
        id_layout.addWidget(QLabel(_("ID")))
        self.id_edit = QLineEdit(entry.id if entry else "")
        id_layout.addWidget(self.id_edit)
        layout.addLayout(id_layout)

        # Repository Name
        name_layout = QHBoxLayout()
        name_layout.addWidget(QLabel(_("Name")))
        self.name_edit = QLineEdit(entry.name if entry else "")
        name_layout.addWidget(self.name_edit)
        layout.addLayout(name_layout)

        # Enabled
        self.enabled_check = QCheckBox(_("Enabled"))
        self.enabled_check.setChecked(entry.enabled if entry else True)
        layout.addWidget(self.enabled_check)

        # Autorefresh
        self.autorefresh_check = QCheckBox(_("Auto Refresh"))
        self.autorefresh_check.setChecked(entry.autorefresh if entry else True)
        layout.addWidget(self.autorefresh_check)

        # URL Type
        url_type_layout = QHBoxLayout()
        url_type_layout.addWidget(QLabel(_("URL Type")))
        self.url_type_combo = QComboBox()
        self.url_type_combo.addItems([_("Base URL"), _("Mirror List")])
        url_type_layout.addWidget(self.url_type_combo)
        layout.addLayout(url_type_layout)

        # URL
        url_layout = QHBoxLayout()
        url_layout.addWidget(QLabel(_("URL")))
        self.url_edit = QLineEdit(
            entry.baseurl
            if entry and entry.baseurl
            else (entry.mirrorlist if entry else "")
        )
        url_layout.addWidget(self.url_edit)
        layout.addLayout(url_layout)

        # Path
        path_layout = QHBoxLayout()
        path_layout.addWidget(QLabel(_("Path")))
        self.path_edit = QLineEdit(entry.path if entry else "")
        path_layout.addWidget(self.path_edit)
        layout.addLayout(path_layout)

        # Type
        type_layout = QHBoxLayout()
        type_layout.addWidget(QLabel(_("Type")))
        self.type_combo = QComboBox()
        self.type_combo.addItems(
            ["rpm-md", "rpm-dir", "plaindir", "yum", "yast2", "obsolete"]
        )
        self.type_combo.setCurrentText(entry.type if entry else "rpm-md")
        type_layout.addWidget(self.type_combo)
        layout.addLayout(type_layout)

        # GPG Check
        self.gpgcheck_check = QCheckBox(_("Check GPG signature"))
        self.gpgcheck_check.setChecked(entry.gpgcheck if entry else True)
        layout.addWidget(self.gpgcheck_check)

        # GPG Key URL
        gpgkey_layout = QHBoxLayout()
        gpgkey_layout.addWidget(QLabel(_("GPG Key URL")))
        self.gpgkey_edit = QLineEdit(entry.gpgkey if entry else "")
        gpgkey_layout.addWidget(self.gpgkey_edit)
        layout.addLayout(gpgkey_layout)

        # Priority
        priority_layout = QHBoxLayout()
        priority_layout.addWidget(QLabel(_("Priority")))
        self.priority_spin = QSpinBox()
        self.priority_spin.setRange(1, 99)
        self.priority_spin.setValue(entry.priority if entry else 99)
        priority_layout.addWidget(self.priority_spin)
        layout.addLayout(priority_layout)

        # Keep Packages
        self.keep_packages_check = QCheckBox(_("Keep packages"))
        self.keep_packages_check.setChecked(entry.keep_packages if entry else False)
        layout.addWidget(self.keep_packages_check)

        # Buttons
        self.buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        self.buttons.accepted.connect(self.accept)
        self.buttons.rejected.connect(self.reject)
        layout.addWidget(self.buttons)

    def get_values(self) -> dict:
        url_type = self.url_type_combo.currentIndex()
        return {
            "id": self.id_edit.text().strip(),
            "name": self.name_edit.text().strip(),
            "enabled": self.enabled_check.isChecked(),
            "autorefresh": self.autorefresh_check.isChecked(),
            "baseurl": self.url_edit.text().strip() if url_type == 0 else "",
            "mirrorlist": self.url_edit.text().strip() if url_type == 1 else "",
            "path": self.path_edit.text().strip(),
            "type": self.type_combo.currentText(),
            "gpgcheck": self.gpgcheck_check.isChecked(),
            "gpgkey": self.gpgkey_edit.text().strip(),
            "priority": self.priority_spin.value(),
            "keep_packages": self.keep_packages_check.isChecked(),
        }