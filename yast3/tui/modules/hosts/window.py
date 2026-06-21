"""UI components for the Hosts module (TUI)."""

from textual.app import ComposeResult
from textual.containers import Horizontal, Vertical
from textual.screen import Screen
from textual.widgets import Button, DataTable, Header, Input, Label, Static

from yast3.core.i18n import _
from yast3.core.modules.hosts import HostEntry, load_hosts, save_hosts

HOSTS_FILE = "/etc/hosts"


class HostsWindow(Screen):
    """TUI window for hosts configuration."""

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
    """

    BINDINGS = [
        ("escape", "app.pop_screen", "Back"),
        ("q", "app.pop_screen", "Back"),
        ("a", "add", "Add"),
        ("e", "edit", "Edit"),
        ("d", "delete", "Delete"),
        ("s", "save", "Save"),
    ]

    def __init__(self) -> None:
        super().__init__()
        self.hosts_entries: list[HostEntry] = []

    def compose(self) -> ComposeResult:
        yield Header()
        with Vertical(classes="container"):
            with Horizontal(classes="button-row"):
                yield Button(_("Add"), id="add-btn")
                yield Button(_("Edit"), id="edit-btn")
                yield Button(_("Delete"), id="delete-btn")
                yield Button(_("Save"), id="save-btn", variant="primary")
            yield DataTable(id="hosts-table")
            yield Static("", id="message", classes="message")

    def on_mount(self) -> None:
        """Load hosts on mount."""
        table = self.query_one("#hosts-table", DataTable)
        table.add_columns(_("Enabled"), _("IP Address"), _("Hostname"), _("Comment"))
        self.load_hosts()

    def load_hosts(self) -> None:
        """Load hosts from /etc/hosts file."""
        self.hosts_entries.clear()
        table = self.query_one("#hosts-table", DataTable)
        table.clear()

        try:
            self.hosts_entries = load_hosts()
        except PermissionError:
            self.show_message(
                _("Error: Cannot read {0}. Root permission required.").format(HOSTS_FILE),
                error=True,
            )
            return
        except FileNotFoundError:
            self.show_message(_("Error: {0} not found.").format(HOSTS_FILE), error=True)
            return

        self.populate_table()

    def populate_table(self) -> None:
        """Populate the table with host entries."""
        table = self.query_one("#hosts-table", DataTable)
        table.clear()

        for entry in self.hosts_entries:
            enabled = "✓" if entry.enabled and entry.editable else ""
            hostnames = " ".join(entry.hostnames)
            table.add_row(enabled, entry.ip, hostnames, entry.comment)

    def show_message(self, message: str, error: bool = False, success: bool = False) -> None:
        """Display a message to the user."""
        msg_widget = self.query_one("#message", Static)
        msg_widget.update(message)
        msg_widget.remove_class("error", "success")
        if error:
            msg_widget.add_class("error")
        elif success:
            msg_widget.add_class("success")

    def action_add(self) -> None:
        """Add a new host entry."""
        self.app.push_screen(HostsEditScreen(self, _("Add Host Entry")))

    def action_edit(self) -> None:
        """Edit the selected host entry."""
        table = self.query_one("#hosts-table", DataTable)
        if table.cursor_row < 0 or table.cursor_row >= len(self.hosts_entries):
            self.show_message(_("Please select a host entry to edit."), error=True)
            return

        entry = self.hosts_entries[table.cursor_row]
        self.app.push_screen(
            HostsEditScreen(
                self,
                _("Edit Host Entry"),
                entry.ip,
                " ".join(entry.hostnames),
                entry.comment,
                table.cursor_row,
            )
        )

    def action_delete(self) -> None:
        """Delete the selected host entry."""
        table = self.query_one("#hosts-table", DataTable)
        if table.cursor_row < 0 or table.cursor_row >= len(self.hosts_entries):
            self.show_message(_("Please select a host entry to delete."), error=True)
            return

        self.hosts_entries.pop(table.cursor_row)
        self.populate_table()
        self.show_message(_("Entry deleted."), success=True)

    def action_save(self) -> None:
        """Save hosts to /etc/hosts file."""
        result = save_hosts(self.hosts_entries)

        if result == "ok":
            self.show_message(_("Success: Hosts file saved successfully."), success=True)
        elif result == "permission_denied":
            self.show_message(
                _("Error: Cannot write to {0}. Root permission required.").format(HOSTS_FILE),
                error=True,
            )
        elif result == "pkexec_failed":
            self.show_message(
                _("Error: Authentication failed or pkexec not available."),
                error=True,
            )
        else:
            self.show_message(_("Error: Failed to save hosts file."), error=True)

    def add_entry(self, ip: str, hostname: str, comment: str) -> None:
        """Add a new entry."""
        hostnames = hostname.split() if hostname else []
        if ip and hostnames:
            comment_sep = "\t# " if comment else ""
            self.hosts_entries.append(
                HostEntry(
                    enabled=True,
                    ip=ip,
                    hostnames=hostnames,
                    comment_sep=comment_sep,
                    comment=comment,
                    editable=True,
                )
            )
            self.populate_table()
            self.show_message(_("Entry added."), success=True)
        else:
            self.show_message(_("Error: IP address and hostname are required."), error=True)

    def update_entry(self, row: int, ip: str, hostname: str, comment: str) -> None:
        """Update an existing entry."""
        hostnames = hostname.split() if hostname else []
        if ip and hostnames:
            entry = self.hosts_entries[row]
            new_comment_sep = entry.comment_sep if entry.comment_sep else ("\t# " if comment else "")
            self.hosts_entries[row] = HostEntry(
                enabled=entry.enabled,
                ip=ip,
                hostnames=hostnames,
                comment_sep=new_comment_sep,
                comment=comment,
                editable=entry.editable,
            )
            self.populate_table()
            self.show_message(_("Entry updated."), success=True)
        else:
            self.show_message(_("Error: IP address and hostname are required."), error=True)


class HostsEditScreen(Screen):
    """Screen for adding/editing a host entry."""

    CSS = """
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
    """

    BINDINGS = [
        ("escape", "app.pop_screen", "Cancel"),
    ]

    def __init__(
        self,
        parent: HostsWindow,
        title: str,
        ip: str = "",
        hostname: str = "",
        comment: str = "",
        row: int = -1,
    ) -> None:
        super().__init__()
        self.parent_window = parent
        self.screen_title = title
        self.initial_ip = ip
        self.initial_hostname = hostname
        self.initial_comment = comment
        self.edit_row = row

    def compose(self) -> ComposeResult:
        with Vertical(classes="container"):
            yield Label(self.screen_title, classes="title")
            with Horizontal():
                yield Label(_("IP Address"), classes="input-label")
                yield Input(value=self.initial_ip, id="ip-input")
            with Horizontal():
                yield Label(_("Hostname"), classes="input-label")
                yield Input(value=self.initial_hostname, id="hostname-input")
            with Horizontal():
                yield Label(_("Comment"), classes="input-label")
                yield Input(value=self.initial_comment, id="comment-input")
            with Horizontal(classes="button-row"):
                yield Button(_("OK"), id="ok-btn", variant="primary")
                yield Button(_("Cancel"), id="cancel-btn")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button press."""
        if event.button.id == "ok-btn":
            self.action_submit()
        elif event.button.id == "cancel-btn":
            self.app.pop_screen()

    def action_submit(self) -> None:
        """Submit the form."""
        ip = self.query_one("#ip-input", Input).value.strip()
        hostname = self.query_one("#hostname-input", Input).value.strip()
        comment = self.query_one("#comment-input", Input).value.strip()

        if self.edit_row >= 0:
            self.parent_window.update_entry(self.edit_row, ip, hostname, comment)
        else:
            self.parent_window.add_entry(ip, hostname, comment)
        self.app.pop_screen()