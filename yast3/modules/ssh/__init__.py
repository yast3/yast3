"""SSH client configuration module package."""

import os
import stat

from PySide6.QtWidgets import QMessageBox

from yast3.i18n import _
from yast3.module import Module
from yast3.modules.ssh.ssh import check_ssh_permissions, fix_ssh_permissions
from yast3.modules.ssh.window import SSHWindow


class SSHClientModule(Module):
    window: SSHWindow | None = None

    def __init__(self):
        super().__init__(_("SSH Client"), ("network-server", "network"))

    def launch(self) -> None:
        """Launch the SSH client module window."""
        if self.window is None:
            self.window = SSHWindow()
            self.window.setWindowTitle(self.name + " — " + _("YaST3"))
            self.window.closed.connect(self._on_window_closed)

        # Check SSH permissions before showing the window
        self._check_and_fix_permissions()

        self.window.show()
        self.window.activateWindow()

    def _check_and_fix_permissions(self) -> None:
        """Check SSH directory permissions and prompt user to fix insecure ones."""
        issues = check_ssh_permissions()
        if not issues:
            return

        # Build detail message showing each issue
        lines = []
        for issue in issues:
            name = os.path.basename(issue.path) or ".ssh"
            current = stat.filemode(issue.current_mode)
            expected = stat.filemode(issue.expected_mode)
            lines.append(f"  {name}: {current} → {expected}")

        detail = "\n".join(lines)

        reply = QMessageBox.warning(
            self.window,
            _("SSH Permission Warning"),
            _(
                "The following SSH items have insecure permissions:\n\n"
                "{0}\n\n"
                "Would you like to fix them now?"
            ).format(detail),
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.Yes,
        )

        if reply == QMessageBox.StandardButton.Yes:
            failed = fix_ssh_permissions(issues)
            if failed:
                failed_names = "\n".join(
                    f"  {os.path.basename(p) or '.ssh'}" for p in failed
                )
                QMessageBox.critical(
                    self.window,
                    _("Error"),
                    _(
                        "Failed to fix permissions for the following items:\n\n" "{0}"
                    ).format(failed_names),
                )
            else:
                QMessageBox.information(
                    self.window,
                    _("Success"),
                    _("SSH permissions have been fixed successfully."),
                )

    def _on_window_closed(self) -> None:
        """Handle window closed signal."""
        self.window = None


__all__ = ["SSHClientModule"]
