from PySide6.QtWidgets import (
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QHBoxLayout,
    QLabel,
    QVBoxLayout,
    QWidget,
)

from yast3.core.i18n import _
from yast3.core.repositories.mirrors.opensuse import opensuse_mirrors
from yast3.core.repositories.mirrors.packman import packman_mirrors


class SwitchMirrorDialog(QDialog):
    """Dialog for switching mirrors for openSUSE and Packman repositories."""

    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)
        self.setWindowTitle(_("Switch Mirror"))
        self.setMinimumWidth(450)

        layout = QVBoxLayout(self)
        layout.setSpacing(12)

        opensuse_layout = QHBoxLayout()
        opensuse_label = QLabel(_("openSUSE"))
        opensuse_label.setFixedWidth(80)
        opensuse_layout.addWidget(opensuse_label)
        self.opensuse_combo = QComboBox()
        self.opensuse_combo.setSizeAdjustPolicy(QComboBox.SizeAdjustPolicy.AdjustToContents)
        self.opensuse_mirrors = []
        for mirror in opensuse_mirrors:
            self.opensuse_combo.addItem(
                f"{mirror.organization} ({mirror.location})", mirror
            )
            self.opensuse_mirrors.append(mirror)
        opensuse_layout.addWidget(self.opensuse_combo)
        self.opensuse_proto_combo = QComboBox()
        self.opensuse_proto_combo.setFixedWidth(80)
        self._update_opensuse_protocols(0)
        self.opensuse_combo.currentIndexChanged.connect(self._update_opensuse_protocols)
        opensuse_layout.addWidget(self.opensuse_proto_combo)
        layout.addLayout(opensuse_layout)

        packman_layout = QHBoxLayout()
        packman_label = QLabel(_("Packman"))
        packman_label.setFixedWidth(80)
        packman_layout.addWidget(packman_label)
        self.packman_combo = QComboBox()
        self.packman_combo.setSizeAdjustPolicy(QComboBox.SizeAdjustPolicy.AdjustToContents)
        self.packman_mirrors = []
        for mirror in packman_mirrors:
            self.packman_combo.addItem(
                f"{mirror.organization} ({mirror.location})", mirror
            )
            self.packman_mirrors.append(mirror)
        packman_layout.addWidget(self.packman_combo)
        self.packman_proto_combo = QComboBox()
        self.packman_proto_combo.setFixedWidth(80)
        self._update_packman_protocols(0)
        self.packman_combo.currentIndexChanged.connect(self._update_packman_protocols)
        packman_layout.addWidget(self.packman_proto_combo)
        layout.addLayout(packman_layout)

        self.buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        self.buttons.accepted.connect(self.accept)
        self.buttons.rejected.connect(self.reject)
        layout.addWidget(self.buttons)

    def _update_opensuse_protocols(self, index: int) -> None:
        self.opensuse_proto_combo.clear()
        mirror = self.opensuse_mirrors[index]
        for proto in mirror.protocols:
            self.opensuse_proto_combo.addItem(proto.upper(), proto)

    def _update_packman_protocols(self, index: int) -> None:
        self.packman_proto_combo.clear()
        mirror = self.packman_mirrors[index]
        for proto in mirror.protocols:
            self.packman_proto_combo.addItem(proto.upper(), proto)

    def get_values(self) -> dict:
        opensuse_mirror = self.opensuse_mirrors[self.opensuse_combo.currentIndex()]
        opensuse_proto = self.opensuse_proto_combo.currentData()
        packman_mirror = self.packman_mirrors[self.packman_combo.currentIndex()]
        packman_proto = self.packman_proto_combo.currentData()
        return {
            "opensuse_mirror": f"{opensuse_proto}://{opensuse_mirror.url}",
            "packman_mirror": f"{packman_proto}://{packman_mirror.url}",
        }