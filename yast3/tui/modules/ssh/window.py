"""UI components for the SSH module (TUI)."""

import os
import subprocess
from dataclasses import dataclass

from textual.app import ComposeResult
from textual.containers import Horizontal, Vertical
from textual.screen import Screen
from textual.widgets import Button, DataTable, Header, Input, Label, Static, TabbedContent, TabPane

from yast3.core.i18n import _
from yast3.core.modules.ssh import (
    SSHConfigEntry,
    SSH_CONFIG_DIR,
    check_ssh_permissions,
    load_ssh_config,
    save_ssh_config,
)


@dataclass
class KeyInfo:
    """Represents SSH key information."""

    name: str
    algorithm: str
    size: str
    fingerprint: str
    comment: str
    has_passphrase: bool
    has_public: bool
    has_private: bool
    private_path: str
    public_path: str


class KeyManager:
    """Manages SSH key operations."""

    @staticmethod
    def list_keys() -> list[KeyInfo]:
        """List all SSH keys in ~/.ssh/ directory."""
        keys: list[KeyInfo] = []

        try:
            files = os.listdir(SSH_CONFIG_DIR)
        except (FileNotFoundError, PermissionError):
            return keys

        private_keys = set()
        for filename in files:
            filepath = os.path.join(SSH_CONFIG_DIR, filename)
            if os.path.isdir(filepath) or filename in (
                "known_hosts",
                "config",
                "authorized_keys",
            ):
                continue

            if filename.endswith(".pub"):
                continue

            if filename.endswith(
                ("_rsa", "_dsa", "_ecdsa", "_ed25519")
            ) or filename.startswith("id_"):
                private_keys.add(filename)

        public_keys = set()
        for filename in files:
            if filename.endswith(".pub"):
                base_name = filename[:-4]
                filepath = os.path.join(SSH_CONFIG_DIR, filename)
                if os.path.isfile(filepath) and base_name not in private_keys:
                    public_keys.add(base_name)

        all_keys = sorted(private_keys.union(public_keys))
        for name in all_keys:
            private_path = os.path.join(SSH_CONFIG_DIR, name)
            public_path = os.path.join(SSH_CONFIG_DIR, name + ".pub")
            has_private = os.path.exists(private_path)
            has_public = os.path.exists(public_path)

            size, algorithm, fingerprint, comment = KeyManager._get_key_info(name)
            has_passphrase = (
                KeyManager._has_passphrase(private_path) if has_private else False
            )

            keys.append(
                KeyInfo(
                    name=name,
                    algorithm=algorithm,
                    size=size,
                    fingerprint=fingerprint,
                    comment=comment,
                    has_passphrase=has_passphrase,
                    has_public=has_public,
                    has_private=has_private,
                    private_path=private_path,
                    public_path=public_path,
                )
            )

        return keys

    @staticmethod
    def _get_key_info(name: str) -> tuple[str, str, str, str]:
        """Get key size, algorithm, fingerprint and comment."""
        size = "N/A"
        algorithm = "Unknown"
        fingerprint = ""
        comment = ""

        private_path = os.path.join(SSH_CONFIG_DIR, name)
        public_path = os.path.join(SSH_CONFIG_DIR, name + ".pub")
        has_public = os.path.exists(public_path)

        filepath = public_path if has_public else private_path

        if os.path.exists(filepath):
            try:
                result = subprocess.run(
                    ["ssh-keygen", "-l", "-f", filepath],
                    capture_output=True,
                    text=True,
                    check=True,
                )
                output = result.stdout.strip()
                if output:
                    parts = output.split()
                    if len(parts) >= 3:
                        size = parts[0]
                        fingerprint = parts[1]
                        if len(parts) > 3:
                            last_part = parts[-1]
                            if last_part.startswith("(") and last_part.endswith(")"):
                                algorithm = last_part[1:-1]
                            comment = " ".join(parts[2:-1])
            except Exception:
                pass

        return (size, algorithm, fingerprint, comment)

    @staticmethod
    def _has_passphrase(private_path: str) -> bool:
        """Check if the private key is encrypted."""
        if os.path.exists(private_path):
            try:
                with open(private_path, "r") as f:
                    first_line = f.readline().strip()
                    if (
                        first_line.startswith("-----BEGIN")
                        and "ENCRYPTED" in first_line
                    ):
                        return True
            except Exception:
                pass
        return False

    @staticmethod
    def delete_key(key_info: KeyInfo) -> tuple[bool, list[str]]:
        """Delete the key pair."""
        errors: list[str] = []

        if key_info.has_private:
            try:
                os.remove(key_info.private_path)
            except Exception as e:
                errors.append(f"{key_info.name}: {str(e)}")

        if key_info.has_public:
            try:
                os.remove(key_info.public_path)
            except Exception as e:
                errors.append(f"{key_info.name}.pub: {str(e)}")

        return (len(errors) == 0, errors)

    @staticmethod
    def generate_key(name: str, key_type: str, bits: int, comment: str) -> str:
        """Generate a new SSH key."""
        private_path = os.path.join(SSH_CONFIG_DIR, name)

        try:
            cmd = ["ssh-keygen", "-t", key_type, "-b", str(bits), "-f", private_path, "-N", "", "-C", comment]
            subprocess.run(cmd, capture_output=True, text=True, check=True)
            return "ok"
        except subprocess.CalledProcessError as e:
            return f"error: {e.stderr}"
        except Exception as e:
            return f"error: {str(e)}"


class SSHWindow(Screen):
    """TUI window for SSH configuration."""

    CSS = """
    Screen {
        align: center middle;
    }

    .container {
        width: 100%;
        height: auto;
        max-height: 80%;
        padding: 1;
    }

    DataTable {
        height: 1fr;
    }

    .button-row {
        align: left middle;
        margin-bottom: 1;
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

    TabbedContent {
        height: 1fr;
    }
    """

    BINDINGS = [
        ("escape", "app.pop_screen", "Back"),
        ("q", "app.pop_screen", "Back"),
    ]

    def __init__(self) -> None:
        super().__init__()
        self.config_entries: list[SSHConfigEntry] = []
        self.key_list: list[KeyInfo] = []

    def compose(self) -> ComposeResult:
        yield Header()
        with Vertical(classes="container"):
            with TabbedContent(id="tabs"):
                with TabPane(_("Hosts"), id="hosts-tab"):
                    yield from self._compose_hosts_tab()
                with TabPane(_("Keys"), id="keys-tab"):
                    yield from self._compose_keys_tab()
            yield Static("", id="message", classes="message")

    def _compose_hosts_tab(self) -> ComposeResult:
        with Vertical():
            with Horizontal(classes="button-row"):
                yield Button(_("Add"), id="add-host-btn")
                yield Button(_("Edit"), id="edit-host-btn")
                yield Button(_("Delete"), id="delete-host-btn")
                yield Button(_("Save"), id="save-host-btn", variant="primary")
            yield DataTable(id="hosts-table")

    def _compose_keys_tab(self) -> ComposeResult:
        with Vertical():
            with Horizontal(classes="button-row"):
                yield Button(_("Generate"), id="generate-key-btn")
                yield Button(_("Delete"), id="delete-key-btn")
            yield DataTable(id="keys-table")

    def on_mount(self) -> None:
        """Load SSH data on mount."""
        self._check_permissions()
        self._setup_hosts_table()
        self._setup_keys_table()
        self.load_data()

    def _check_permissions(self) -> None:
        """Check SSH directory permissions."""
        issues = check_ssh_permissions()
        if issues:
            self.show_message(_("Warning: Some SSH files have insecure permissions."), error=True)

    def _setup_hosts_table(self) -> None:
        """Setup hosts table columns."""
        table = self.query_one("#hosts-table", DataTable)
        table.add_columns(_("Enabled"), _("Host Pattern"), _("Options"))

    def _setup_keys_table(self) -> None:
        """Setup keys table columns."""
        table = self.query_one("#keys-table", DataTable)
        table.add_columns(_("Name"), _("Type"), _("Bits"), _("Comment"), _("Passphrase"))

    def load_data(self) -> None:
        """Load SSH hosts and keys."""
        self._load_config()
        self._load_keys()

    def _load_config(self) -> None:
        """Load SSH config."""
        try:
            self.config_entries = load_ssh_config()
        except FileNotFoundError:
            self.config_entries = []
        except PermissionError:
            self.show_message(_("Error: Cannot read SSH config."), error=True)
            return

        self._populate_hosts_table()

    def _load_keys(self) -> None:
        """Load SSH keys."""
        self.key_list = KeyManager.list_keys()
        self._populate_keys_table()

    def _populate_hosts_table(self) -> None:
        """Populate hosts table."""
        table = self.query_one("#hosts-table", DataTable)
        table.clear()

        for entry in self.config_entries:
            enabled = "✓" if entry.enabled else ""
            option_names = list(entry.options.keys())[:3]
            options_text = ", ".join(option_names)
            if len(entry.options) > 3:
                options_text += _(" and {0} more").format(len(entry.options) - 3)
            table.add_row(enabled, entry.host, options_text)

    def _populate_keys_table(self) -> None:
        """Populate keys table."""
        table = self.query_one("#keys-table", DataTable)
        table.clear()

        for key in self.key_list:
            passphrase = _("Yes") if key.has_passphrase else _("No")
            table.add_row(key.name, key.algorithm, key.size, key.comment or "-", passphrase)

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
        if event.button.id == "add-host-btn":
            self.app.push_screen(HostEditScreen(self))
        elif event.button.id == "edit-host-btn":
            self._edit_host()
        elif event.button.id == "delete-host-btn":
            self._delete_host()
        elif event.button.id == "save-host-btn":
            self._save_config()
        elif event.button.id == "generate-key-btn":
            self.app.push_screen(GenerateKeyScreen(self))
        elif event.button.id == "delete-key-btn":
            self._delete_key()

    def _edit_host(self) -> None:
        """Edit the selected host entry."""
        table = self.query_one("#hosts-table", DataTable)
        if table.cursor_row < 0 or table.cursor_row >= len(self.config_entries):
            self.show_message(_("Please select a host to edit."), error=True)
            return

        entry = self.config_entries[table.cursor_row]
        self.app.push_screen(HostEditScreen(self, entry, table.cursor_row))

    def _delete_host(self) -> None:
        """Delete the selected host entry."""
        table = self.query_one("#hosts-table", DataTable)
        if table.cursor_row < 0 or table.cursor_row >= len(self.config_entries):
            self.show_message(_("Please select a host to delete."), error=True)
            return

        entry = self.config_entries[table.cursor_row]
        if entry.is_default():
            self.show_message(_("Cannot delete the default host entry."), error=True)
            return

        self.config_entries.pop(table.cursor_row)
        self._populate_hosts_table()
        self.show_message(_("Host entry deleted."), success=True)

    def _save_config(self) -> None:
        """Save SSH config."""
        result = save_ssh_config(self.config_entries)

        if result == "ok":
            self.show_message(_("Success: SSH config saved successfully."), success=True)
        elif result == "permission_denied":
            self.show_message(_("Error: Cannot write to SSH config."), error=True)
        else:
            self.show_message(_("Error: Failed to save SSH config."), error=True)

    def _delete_key(self) -> None:
        """Delete the selected SSH key."""
        table = self.query_one("#keys-table", DataTable)
        if table.cursor_row < 0 or table.cursor_row >= len(self.key_list):
            self.show_message(_("Please select a key to delete."), error=True)
            return

        key = self.key_list[table.cursor_row]
        success, errors = KeyManager.delete_key(key)
        if success:
            self.key_list.pop(table.cursor_row)
            self._populate_keys_table()
            self.show_message(_("Key deleted."), success=True)
        else:
            self.show_message(_("Error: {0}").format("\n".join(errors)), error=True)

    def add_host(self, host: str, options: dict) -> None:
        """Add a new host entry."""
        if not host:
            self.show_message(_("Error: Host pattern is required."), error=True)
            return

        entry = SSHConfigEntry(enabled=True, host=host, options=options)
        self.config_entries.append(entry)
        self._populate_hosts_table()
        self.show_message(_("Host entry added."), success=True)

    def update_host(self, row: int, host: str, options: dict) -> None:
        """Update an existing host entry."""
        if not host:
            self.show_message(_("Error: Host pattern is required."), error=True)
            return

        entry = self.config_entries[row]
        self.config_entries[row] = SSHConfigEntry(
            enabled=entry.enabled,
            host=host,
            options=options,
            editable=entry.editable,
        )
        self._populate_hosts_table()
        self.show_message(_("Host entry updated."), success=True)

    def generate_key(self, name: str, key_type: str, bits: int, comment: str) -> None:
        """Generate a new SSH key."""
        result = KeyManager.generate_key(name, key_type, bits, comment)
        if result == "ok":
            self._load_keys()
            self.show_message(_("Key generated successfully."), success=True)
        else:
            self.show_message(_("Error: {0}").format(result), error=True)


class HostEditScreen(Screen):
    """Screen for adding/editing a host entry."""

    CSS = """
    .container {
        width: 60;
        height: auto;
        padding: 2;
        border: solid green;
    }

    .input-row {
        height: 3;
        margin-bottom: 1;
    }

    .input-label {
        width: 10;
        content-align: right middle;
        padding-right: 1;
    }

    Input {
        width: 1fr;
    }

    .button-row {
        align: right middle;
        height: 3;
        margin-top: 1;
    }

    Button {
        margin-left: 1;
    }
    """

    BINDINGS = [
        ("escape", "app.pop_screen", "Cancel"),
    ]

    def __init__(
        self,
        parent: SSHWindow,
        entry: SSHConfigEntry | None = None,
        row: int = -1,
    ) -> None:
        super().__init__()
        self.parent_window = parent
        self.edit_row = row
        self.initial_entry = entry

    def compose(self) -> ComposeResult:
        with Vertical(classes="container"):
            yield Label(_("Edit Host Entry") if self.edit_row >= 0 else _("Add Host Entry"), classes="title")
            with Horizontal(classes="input-row"):
                yield Label(_("Host"), classes="input-label")
                yield Input(value=self._get_host(), id="host-input", placeholder=_("Host pattern"))
            with Horizontal(classes="input-row"):
                yield Label(_("HostName"), classes="input-label")
                yield Input(value=self._get_option("HostName"), id="hostname-input", placeholder=_("Real hostname"))
            with Horizontal(classes="input-row"):
                yield Label(_("Port"), classes="input-label")
                yield Input(value=self._get_option("Port"), id="port-input", placeholder=_("Port number"))
            with Horizontal(classes="input-row"):
                yield Label(_("User"), classes="input-label")
                yield Input(value=self._get_option("User"), id="user-input", placeholder=_("Username"))
            with Horizontal(classes="input-row"):
                yield Label(_("IdentityFile"), classes="input-label")
                yield Input(value=self._get_option("IdentityFile"), id="identity-input", placeholder=_("Key file path"))
            with Horizontal(classes="button-row"):
                yield Button(_("OK"), id="ok-btn", variant="primary")
                yield Button(_("Cancel"), id="cancel-btn")

    def _get_host(self) -> str:
        """Get initial host value."""
        return self.initial_entry.host if self.initial_entry else ""

    def _get_option(self, key: str) -> str:
        """Get initial option value."""
        if self.initial_entry:
            return self.initial_entry.get_option(key, "")
        return ""

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button press."""
        if event.button.id == "ok-btn":
            self.action_submit()
        elif event.button.id == "cancel-btn":
            self.app.pop_screen()

    def action_submit(self) -> None:
        """Submit the form."""
        host = self.query_one("#host-input", Input).value.strip()
        options = {}

        hostname = self.query_one("#hostname-input", Input).value.strip()
        if hostname:
            options["HostName"] = hostname

        port = self.query_one("#port-input", Input).value.strip()
        if port:
            options["Port"] = port

        user = self.query_one("#user-input", Input).value.strip()
        if user:
            options["User"] = user

        identity = self.query_one("#identity-input", Input).value.strip()
        if identity:
            options["IdentityFile"] = identity

        if self.edit_row >= 0:
            self.parent_window.update_host(self.edit_row, host, options)
        else:
            self.parent_window.add_host(host, options)
        self.app.pop_screen()


class GenerateKeyScreen(Screen):
    """Screen for generating an SSH key."""

    CSS = """
    .container {
        width: 60;
        height: auto;
        padding: 2;
        border: solid green;
    }

    .input-row {
        height: 3;
        margin-bottom: 1;
    }

    .input-label {
        width: 10;
        content-align: right middle;
        padding-right: 1;
    }

    .button-row {
        align: right middle;
        margin-top: 1;
    }
    """

    BINDINGS = [
        ("escape", "app.pop_screen", "Cancel"),
    ]

    def __init__(self, parent: SSHWindow) -> None:
        super().__init__()
        self.parent_window = parent

    def compose(self) -> ComposeResult:
        with Vertical(classes="container"):
            yield Label(_("Generate SSH Key"), classes="title")
            with Horizontal():
                yield Label(_("Name"), classes="input-label")
                yield Input(value="id_rsa", id="name-input", placeholder=_("Key filename"))
            with Horizontal():
                yield Label(_("Type"), classes="input-label")
                yield Input(value="rsa", id="type-input", placeholder=_("rsa, ed25519, ecdsa"))
            with Horizontal():
                yield Label(_("Bits"), classes="input-label")
                yield Input(value="4096", id="bits-input", placeholder=_("Key bits"))
            with Horizontal():
                yield Label(_("Comment"), classes="input-label")
                yield Input(placeholder=_("Optional comment"), id="comment-input")
            with Horizontal(classes="button-row"):
                yield Button(_("OK"), id="ok-btn", variant="primary")
                yield Button(_("Cancel"), id="cancel-btn")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button press."""
        if event.button.id == "ok-btn":
            name = self.query_one("#name-input", Input).value.strip()
            key_type = self.query_one("#type-input", Input).value.strip()
            bits = int(self.query_one("#bits-input", Input).value.strip() or "4096")
            comment = self.query_one("#comment-input", Input).value.strip()
            self.parent_window.generate_key(name, key_type, bits, comment)
            self.app.pop_screen()
        elif event.button.id == "cancel-btn":
            self.app.pop_screen()