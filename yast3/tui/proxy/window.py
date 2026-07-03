"""UI components for the Proxy module (TUI)."""

from textual.app import ComposeResult
from textual.containers import Horizontal, Vertical
from textual.screen import Screen
from textual.widgets import Button, Header, Input, Label, Static

from yast3.core.i18n import _
from yast3.core.proxy import ProxyConfig

PROXY_FILE = "/etc/sysconfig/proxy"


class ProxyWindow(Screen):
    """TUI window for proxy configuration."""

    CSS = """
    Screen {
        align: center middle;
    }

    .container {
        width: 90;
        height: auto;
        padding: 2;
        border: solid green;
    }

    .input-label {
        width: 14;
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
        ("ctrl+e", "toggle_enabled", "Toggle Enabled"),
    ]

    def __init__(self) -> None:
        super().__init__()
        self.config = ProxyConfig()
        self.proxy_enabled = False

    def compose(self) -> ComposeResult:
        yield Header()
        with Vertical(classes="container"):
            yield Label(_("Proxy Configuration"), classes="title")
            with Horizontal(classes="button-row"):
                yield Button(id="enabled-btn", variant="default")
            with Horizontal():
                yield Label(_("HTTP Proxy"), classes="input-label")
                yield Input(placeholder="http://host:port", id="http-input")
            with Horizontal():
                yield Label(_("HTTPS Proxy"), classes="input-label")
                yield Input(placeholder="http://host:port", id="https-input")
            with Horizontal():
                yield Label(_("FTP Proxy"), classes="input-label")
                yield Input(placeholder="http://host:port", id="ftp-input")
            with Horizontal():
                yield Label(_("No Proxy"), classes="input-label")
                yield Input(
                    placeholder="localhost,127.0.0.1,.example.com",
                    id="no-proxy-input",
                )
            with Horizontal(classes="button-row"):
                yield Button(_("Save"), id="save-btn", variant="primary")
                yield Button(_("Cancel"), id="cancel-btn")
            yield Static("", id="message", classes="message")

    def on_mount(self) -> None:
        self._refresh_enabled_button()
        try:
            self.proxy_enabled = self.config.get("PROXY_ENABLED") == "yes"
            self.query_one("#http-input", Input).value = str(self.config.get("HTTP_PROXY", ""))
            self.query_one("#https-input", Input).value = str(self.config.get("HTTPS_PROXY", ""))
            self.query_one("#ftp-input", Input).value = str(self.config.get("FTP_PROXY", ""))
            self.query_one("#no-proxy-input", Input).value = str(self.config.get("NO_PROXY", ""))
            self._refresh_enabled_button()
        except FileNotFoundError:
            self.show_message(_("Error: {0} not found.").format(PROXY_FILE), error=True)
        except PermissionError:
            self.show_message(
                _("Error: Cannot read {0}. Root permission required.").format(PROXY_FILE),
                error=True,
            )
        except Exception as e:
            self.show_message(
                _("Error: Failed to load proxy configuration: {0}").format(str(e)),
                error=True,
            )

    def _refresh_enabled_button(self) -> None:
        button = self.query_one("#enabled-btn", Button)
        state = _("Enabled") if self.proxy_enabled else _("Disabled")
        button.label = _("Proxy State: {0}").format(state)

    def show_message(self, message: str, error: bool = False, success: bool = False) -> None:
        msg_widget = self.query_one("#message", Static)
        msg_widget.update(message)
        msg_widget.remove_class("error", "success")
        if error:
            msg_widget.add_class("error")
        elif success:
            msg_widget.add_class("success")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "save-btn":
            self.action_save()
        elif event.button.id == "cancel-btn":
            self.app.pop_screen()
        elif event.button.id == "enabled-btn":
            self.action_toggle_enabled()

    def action_toggle_enabled(self) -> None:
        self.proxy_enabled = not self.proxy_enabled
        self._refresh_enabled_button()

    def action_save(self) -> None:
        self.config.update({
            "PROXY_ENABLED": "yes" if self.proxy_enabled else "no",
            "HTTP_PROXY": self.query_one("#http-input", Input).value.strip(),
            "HTTPS_PROXY": self.query_one("#https-input", Input).value.strip(),
            "FTP_PROXY": self.query_one("#ftp-input", Input).value.strip(),
            "NO_PROXY": self.query_one("#no-proxy-input", Input).value.strip(),
        })

        try:
            self.config.write_pkexec()
            self.show_message(_("Success: Proxy configuration saved successfully."), success=True)
            self.set_timer(1.5, self.app.pop_screen)
        except PermissionError:
            self.show_message(
                _("Error: Permission denied. Root permission required."),
                error=True,
            )
        except Exception as e:
            self.show_message(
                _("Error: Failed to save proxy configuration: {0}").format(str(e)),
                error=True,
            )
