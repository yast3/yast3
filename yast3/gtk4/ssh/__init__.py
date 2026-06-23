"""SSH client configuration module package - GTK4 GUI."""

import os
import stat

import gi

gi.require_version("Gtk", "4.0")

from gi.repository import Gtk

from yast3.core.i18n import _
from yast3.core.module import Module
from yast3.core.ssh import check_ssh_permissions, fix_ssh_permissions
from yast3.gtk4.ssh.window import SSHWindow


class SSHClientModule(Module):
    window: SSHWindow | None = None

    def __init__(self):
        super().__init__(_("SSH Client"), ("network-server", "network"), "🔐")

    def launch(self, parent: Gtk.ApplicationWindow | None = None) -> None:
        """Launch the SSH client module window."""
        if self.window is None:
            self.window = SSHWindow()
            self.window.set_title(self.name + " — " + _("YaST3"))
            self.window.connect("close-request", self._on_window_closed)

        # Check SSH permissions before showing the window
        self._check_and_fix_permissions()

        self.window.present()

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

        dialog = Gtk.MessageDialog(
            transient_for=self.window,
            modal=True,
            message_type=Gtk.MessageType.WARNING,
            buttons=Gtk.ButtonsType.YES_NO,
            text=_("SSH Permission Warning"),
        )
        dialog.format_secondary_text(
            _(
                "The following SSH items have insecure permissions:\n\n"
                "{0}\n\n"
                "Would you like to fix them now?"
            ).format(detail)
        )
        dialog.connect("response", self._on_permission_dialog_response, issues)
        dialog.present()

    def _on_permission_dialog(self, dialog, response_id, issues) -> None:
        """Handle permission dialog response."""
        if response_id == Gtk.ResponseType.YES:
            failed = fix_ssh_permissions(issues)
            if failed:
                failed_names = "\n".join(
                    f"  {os.path.basename(p) or '.ssh'}" for p in failed
                )
                error_dialog = Gtk.MessageDialog(
                    transient_for=self.window,
                    modal=True,
                    message_type=Gtk.MessageType.ERROR,
                    buttons=Gtk.ButtonsType.OK,
                    text=_("Error"),
                )
                error_dialog.format_secondary_text(
                    _(
                        "Failed to fix permissions for the following items:\n\n" "{0}"
                    ).format(failed_names)
                )
                error_dialog.connect("response", lambda d, r: d.destroy())
                error_dialog.present()
            else:
                success_dialog = Gtk.MessageDialog(
                    transient_for=self.window,
                    modal=True,
                    message_type=Gtk.MessageType.INFO,
                    buttons=Gtk.ButtonsType.OK,
                    text=_("Success"),
                )
                success_dialog.format_secondary_text(_("SSH permissions have been fixed successfully."))
                success_dialog.connect("response", lambda d, r: d.destroy())
                success_dialog.present()
        dialog.destroy()

    def _on_permission_dialog_response(self, dialog, response_id, issues) -> None:
        """Handle permission dialog response."""
        self._on_permission_dialog(dialog, response_id, issues)

    def _on_window_closed(self, window) -> None:
        """Handle window closed signal."""
        self.window = None


__all__ = ["SSHClientModule"]