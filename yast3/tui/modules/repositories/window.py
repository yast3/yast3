"""UI components for the Repositories module (TUI)."""

from textual.app import ComposeResult
from textual.containers import Horizontal, Vertical
from textual.screen import Screen
from textual.widgets import Button, Checkbox, DataTable, Header, Input, Label, Select, Static

from yast3.core.i18n import _
from yast3.core.modules.repositories import (
    RepoEntry,
    delete_repo_entry,
    load_repos,
    save_repo_entry,
)


class RepositoriesWindow(Screen):
    """TUI window for repositories configuration."""

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
    ]

    def __init__(self) -> None:
        super().__init__()
        self.repo_entries: list[RepoEntry] = []

    def compose(self) -> ComposeResult:
        yield Header()
        with Vertical(classes="container"):
            with Horizontal(classes="button-row"):
                yield Button(_("Add"), id="add-btn")
                yield Button(_("Edit"), id="edit-btn")
                yield Button(_("Delete"), id="delete-btn")
            yield DataTable(id="repos-table")
            yield Static("", id="message", classes="message")

    def on_mount(self) -> None:
        """Load repositories on mount."""
        table = self.query_one("#repos-table", DataTable)
        table.add_columns(_("Name"), _("URL"), _("Priority"), _("Enabled"), _("Auto Refresh"))
        self.load_repos()

    def load_repos(self) -> None:
        """Load repositories."""
        self.repo_entries.clear()
        table = self.query_one("#repos-table", DataTable)
        table.clear()

        try:
            self.repo_entries = load_repos()
        except PermissionError:
            self.show_message(
                _("Error: Cannot read repository directory. Root permission required."),
                error=True,
            )
            return

        self.populate_table()

    def populate_table(self) -> None:
        """Populate the table with repo entries."""
        table = self.query_one("#repos-table", DataTable)
        table.clear()

        for entry in self.repo_entries:
            enabled = "✓" if entry.enabled else ""
            autorefresh = "✓" if entry.autorefresh else ""
            table.add_row(entry.name, entry.url, str(entry.priority), enabled, autorefresh)

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
        if event.button.id == "add-btn":
            self.action_add()
        elif event.button.id == "edit-btn":
            self.action_edit()
        elif event.button.id == "delete-btn":
            self.action_delete()

    def action_add(self) -> None:
        """Add a new repository."""
        self.app.push_screen(RepoEditScreen(self, _("Add Repository")))

    def action_edit(self) -> None:
        """Edit the selected repository."""
        table = self.query_one("#repos-table", DataTable)
        if table.cursor_row < 0 or table.cursor_row >= len(self.repo_entries):
            self.show_message(_("Please select a repository to edit."), error=True)
            return

        entry = self.repo_entries[table.cursor_row]
        self.app.push_screen(
            RepoEditScreen(
                self,
                _("Edit Repository"),
                entry,
                table.cursor_row,
            )
        )

    def action_delete(self) -> None:
        """Delete the selected repository."""
        table = self.query_one("#repos-table", DataTable)
        if table.cursor_row < 0 or table.cursor_row >= len(self.repo_entries):
            self.show_message(_("Please select a repository to delete."), error=True)
            return

        entry = self.repo_entries[table.cursor_row]
        result = delete_repo_entry(entry)
        if result == "ok":
            self.repo_entries.pop(table.cursor_row)
            self.populate_table()
            self.show_message(_("Repository deleted."), success=True)
        else:
            self.handle_save_error(result)

    def add_repo(self, values: dict) -> None:
        """Add a new repository."""
        repo_id = values.get("id", "")
        url = values.get("baseurl") or values.get("mirrorlist")

        if not repo_id:
            self.show_message(_("Error: Repository ID is required."), error=True)
            return
        if not url:
            self.show_message(_("Error: URL is required."), error=True)
            return

        filename = f"{repo_id}.repo"
        new_entry = RepoEntry(
            id=repo_id,
            filename=filename,
            name=values.get("name", repo_id),
            enabled=values.get("enabled", True),
            autorefresh=values.get("autorefresh", True),
            baseurl=values.get("baseurl", ""),
            mirrorlist=values.get("mirrorlist", ""),
            path=values.get("path", ""),
            type=values.get("type", ""),
            gpgcheck=values.get("gpgcheck", False),
            gpgkey=values.get("gpgkey", ""),
            priority=values.get("priority", 99),
            keep_packages=values.get("keep_packages", False),
        )

        result = save_repo_entry(new_entry)
        if result == "ok":
            self.repo_entries.append(new_entry)
            self.populate_table()
            self.show_message(_("Repository added."), success=True)
        else:
            self.handle_save_error(result)

    def update_repo(self, row: int, values: dict) -> None:
        """Update an existing repository."""
        entry = self.repo_entries[row]
        repo_id = values.get("id", "")
        url = values.get("baseurl") or values.get("mirrorlist")

        if not repo_id:
            self.show_message(_("Error: Repository ID is required."), error=True)
            return
        if not url:
            self.show_message(_("Error: URL is required."), error=True)
            return

        updated_entry = RepoEntry(
            id=repo_id,
            filename=entry.filename,
            name=values.get("name", repo_id),
            enabled=values.get("enabled", True),
            autorefresh=values.get("autorefresh", True),
            baseurl=values.get("baseurl", ""),
            mirrorlist=values.get("mirrorlist", ""),
            path=values.get("path", ""),
            type=values.get("type", ""),
            gpgcheck=values.get("gpgcheck", False),
            gpgkey=values.get("gpgkey", ""),
            priority=values.get("priority", 99),
            keep_packages=values.get("keep_packages", False),
        )

        result = save_repo_entry(updated_entry)
        if result == "ok":
            self.repo_entries[row] = updated_entry
            self.populate_table()
            self.show_message(_("Repository updated."), success=True)
        else:
            self.handle_save_error(result)

    def handle_save_error(self, result: str) -> None:
        """Handle save errors."""
        if result == "permission_denied":
            self.show_message(
                _("Error: Cannot write to repository directory. Root permission required."),
                error=True,
            )
        elif result == "pkexec_failed":
            self.show_message(
                _("Error: Authentication failed or pkexec not available."),
                error=True,
            )
        else:
            self.show_message(_("Error: Failed to save repository configuration."), error=True)


class RepoEditScreen(Screen):
    """Screen for adding/editing a repository."""

    CSS = """
    .container {
        width: 70;
        height: auto;
        max-height: 80%;
        padding: 2;
        border: solid green;
    }

    .input-row {
        height: 3;
        margin-bottom: 1;
    }

    .input-label {
        width: 14;
        content-align: right middle;
        padding-right: 1;
    }

    Checkbox {
        margin-bottom: 1;
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
        parent: RepositoriesWindow,
        title: str,
        entry: RepoEntry | None = None,
        row: int = -1,
    ) -> None:
        super().__init__()
        self.parent_window = parent
        self.screen_title = title
        self.edit_row = row
        self.initial_entry = entry

    def compose(self) -> ComposeResult:
        with Vertical(classes="container"):
            yield Label(self.screen_title, classes="title")
            with Horizontal():
                yield Label(_("Repository ID"), classes="input-label")
                yield Input(value=self._get_value("id"), id="id-input", placeholder=_("Unique repository ID"))
            with Horizontal():
                yield Label(_("Name"), classes="input-label")
                yield Input(value=self._get_value("name"), id="name-input", placeholder=_("Display name"))
            with Horizontal():
                yield Label(_("Base URL"), classes="input-label")
                yield Input(value=self._get_value("baseurl"), id="baseurl-input", placeholder=_("Base URL"))
            with Horizontal():
                yield Label(_("Mirror List"), classes="input-label")
                yield Input(value=self._get_value("mirrorlist"), id="mirrorlist-input", placeholder=_("Mirror list URL"))
            with Horizontal():
                yield Label(_("Priority"), classes="input-label")
                yield Input(value=self._get_value("priority"), id="priority-input", placeholder=_("Priority (default 99)"))
            with Horizontal():
                yield Label(_("Type"), classes="input-label")
                yield Select(
                    [("yast2", "yast2"), ("rpm-md", "rpm-md"), ("plaindir", "plaindir")],
                    id="type-select",
                    allow_blank=True,
                )
            with Horizontal():
                yield Label(_("GPG Key"), classes="input-label")
                yield Input(value=self._get_value("gpgkey"), id="gpgkey-input", placeholder=_("GPG key URL"))
            yield Checkbox(_("Enabled"), id="enabled-check", value=self._get_bool("enabled", True))
            yield Checkbox(_("Auto Refresh"), id="autorefresh-check", value=self._get_bool("autorefresh", True))
            yield Checkbox(_("GPG Check"), id="gpgcheck-check", value=self._get_bool("gpgcheck", False))
            yield Checkbox(_("Keep Packages"), id="keep-packages-check", value=self._get_bool("keep_packages", False))
            with Horizontal(classes="button-row"):
                yield Button(_("OK"), id="ok-btn", variant="primary")
                yield Button(_("Cancel"), id="cancel-btn")

    def _get_value(self, key: str) -> str:
        """Get initial value from entry."""
        if self.initial_entry:
            val = getattr(self.initial_entry, key, "")
            if isinstance(val, int):
                return str(val)
            return val or ""
        return ""

    def _get_bool(self, key: str, default: bool) -> bool:
        """Get initial boolean value from entry."""
        if self.initial_entry:
            return getattr(self.initial_entry, key, default)
        return default

    def on_mount(self) -> None:
        """Set initial select value."""
        if self.initial_entry:
            try:
                type_select = self.query_one("#type-select", Select)
                if self.initial_entry.type:
                    type_select.value = self.initial_entry.type
            except Exception:
                pass

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button press."""
        if event.button.id == "ok-btn":
            self.action_submit()
        elif event.button.id == "cancel-btn":
            self.app.pop_screen()

    def action_submit(self) -> None:
        """Submit the form."""
        values = {
            "id": self.query_one("#id-input", Input).value.strip(),
            "name": self.query_one("#name-input", Input).value.strip(),
            "baseurl": self.query_one("#baseurl-input", Input).value.strip(),
            "mirrorlist": self.query_one("#mirrorlist-input", Input).value.strip(),
            "priority": int(self.query_one("#priority-input", Input).value.strip() or "99"),
            "type": self._get_select_value("type-select"),
            "gpgkey": self.query_one("#gpgkey-input", Input).value.strip(),
            "enabled": self.query_one("#enabled-check", Checkbox).value,
            "autorefresh": self.query_one("#autorefresh-check", Checkbox).value,
            "gpgcheck": self.query_one("#gpgcheck-check", Checkbox).value,
            "keep_packages": self.query_one("#keep-packages-check", Checkbox).value,
        }

        if self.edit_row >= 0:
            self.parent_window.update_repo(self.edit_row, values)
        else:
            self.parent_window.add_repo(values)
        self.app.pop_screen()

    def _get_select_value(self, select_id: str) -> str:
        """Get select widget value."""
        try:
            select = self.query_one(f"#{select_id}", Select)
            value = select.value
            return str(value) if value != Select.BLANK else ""
        except Exception:
            return ""