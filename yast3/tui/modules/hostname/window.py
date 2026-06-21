"""UI components for the Hostname module (TUI)."""

from textual.app import ComposeResult
from textual.containers import Horizontal, Vertical
from textual.screen import Screen
from textual.widgets import Button, Header, Input, Label, Static

from yast3.core.i18n import _
from yast3.core.modules.hostname import (
    get_current_hostname,
    set_hostname,
)


class HostnameWindow(Screen):
    """TUI window for hostname configuration."""

    CSS = """
    Screen {
        align: center middle;
    }

    .container {
        width: 60;
        height: auto;
        padding: 2;
        border: solid green;
    }

    .input-label {
        width: 12;
        content-align: right middle;
        padding-right: 1;
    }

    .button-row {
        align: right middle;
        margin-top: 1;
    }

    .message {
        margin-top: 1;
        color: yellow;
    }

    .error {
        color: red;
    }

    .success {
        color: green;
    }
    """

    BINDINGS = [
        ("escape", "app.pop_screen", "Back"),
        ("q", "app.pop_screen", "Back"),
        ("ctrl+s", "save", "Save"),
    ]

    def compose(self) -> ComposeResult:
        yield Header()
        with Vertical(classes="container"):
            yield Label(_("Hostname Configuration"), classes="title")
            with Horizontal():
                yield Label(_("Hostname"), classes="input-label")
                yield Input(placeholder=_("Enter hostname"), id="hostname-input")
            with Horizontal(classes="button-row"):
                yield Button(_("Save"), id="save-btn", variant="primary")
                yield Button(_("Cancel"), id="cancel-btn")
            yield Static("", id="message", classes="message")

    def on_mount(self) -> None:
        """Load current hostname on mount."""
        try:
            current = get_current_hostname()
            self.query_one("#hostname-input", Input).value = current
        except FileNotFoundError:
            self.show_message(_("Error: /etc/hostname not found."), error=True)
        except PermissionError:
            self.show_message(
                _("Error: Cannot read /etc/hostname. Root permission required."),
                error=True,
            )
        except Exception as e:
            self.show_message(_("Error: {0}").format(str(e)), error=True)

    def show_message(self, message: str, error: bool = False, success: bool = False) -> None:
        """Display a message to the user."""
        msg_widget = self.query_one("#message", Static)
        msg_widget.update(message)
        msg_widget.remove_class("error", "success")
        if error:
            msg_widget.add_class("error")
        elif success:
            msg_widget.add_class("success")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button press."""
        if event.button.id == "save-btn":
            self.action_save()
        elif event.button.id == "cancel-btn":
            self.app.pop_screen()

    def action_save(self) -> None:
        """Save the hostname."""
        new_hostname = self.query_one("#hostname-input", Input).value.strip()

        if not new_hostname:
            self.show_message(_("Error: Hostname cannot be empty."), error=True)
            return

        if len(new_hostname) > 253:
            self.show_message(
                _("Error: Hostname is too long (maximum 253 characters)."),
                error=True,
            )
            return

        invalid_chars = set(" /\\")
        if any(c in invalid_chars for c in new_hostname):
            self.show_message(_("Error: Hostname contains invalid characters."), error=True)
            return

        status, message = set_hostname(new_hostname)

        if status == "ok":
            self.show_message(
                _("Success: Hostname changed successfully to '{0}'.").format(new_hostname),
                success=True,
            )
            self.set_timer(1.5, self.app.pop_screen)
        elif status == "permission_denied":
            self.show_message(
                _("Error: Permission denied. Root permission required."),
                error=True,
            )
        elif status == "pkexec_failed":
            self.show_message(
                _("Error: Authentication failed or pkexec not available."),
                error=True,
            )
        else:
            self.show_message(_("Error: {0}").format(message), error=True)