"""UI components for the Git module (TUI)."""

from textual.app import ComposeResult
from textual.containers import Horizontal, Vertical
from textual.screen import Screen
from textual.widgets import Button, Checkbox, Header, Input, Label, Select, Static, TabbedContent, TabPane

from yast3.core.i18n import _
from yast3.core.modules.git import (
    get_git_config,
    is_git_installed,
    set_git_config,
)


class GitWindow(Screen):
    """TUI window for Git configuration."""

    CSS = """
    Screen {
        align: center middle;
    }

    .container {
        width: 80;
        height: auto;
        max-height: 30;
        padding: 1;
    }

    .input-label {
        width: 18;
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

    def __init__(self) -> None:
        super().__init__()
        self.config = None

    def compose(self) -> ComposeResult:
        yield Header()
        with Vertical(classes="container"):
            with TabbedContent(id="tabs"):
                with TabPane(_("User"), id="user-tab"):
                    yield from self._compose_user_tab()
                with TabPane(_("Core"), id="core-tab"):
                    yield from self._compose_core_tab()
                with TabPane(_("Commit"), id="commit-tab"):
                    yield from self._compose_commit_tab()
                with TabPane(_("Merge"), id="merge-tab"):
                    yield from self._compose_merge_tab()
                with TabPane(_("Other"), id="other-tab"):
                    yield from self._compose_other_tab()
            with Horizontal(classes="button-row"):
                yield Button(_("Save"), id="save-btn", variant="primary")
                yield Button(_("Reset"), id="reset-btn")
            yield Static("", id="message", classes="message")

    def _compose_user_tab(self) -> ComposeResult:
        with Vertical():
            with Horizontal():
                yield Label(_("User Name"), classes="input-label")
                yield Input(placeholder=_("Enter your Git user name"), id="user-name")
            with Horizontal():
                yield Label(_("Email Address"), classes="input-label")
                yield Input(placeholder=_("Enter your Git email address"), id="user-email")
            with Horizontal():
                yield Label(_("GPG Signing Key"), classes="input-label")
                yield Input(placeholder=_("Enter GPG key ID"), id="user-signingkey")

    def _compose_core_tab(self) -> ComposeResult:
        with Vertical():
            with Horizontal():
                yield Label(_("Default Editor"), classes="input-label")
                yield Input(placeholder=_("e.g., vim, nano, code"), id="core-editor")
            with Horizontal():
                yield Label(_("Auto CRLF"), classes="input-label")
                yield Select(
                    [("", ""), ("true", "true"), ("false", "false"), ("input", "input")],
                    id="core-autocrlf",
                    allow_blank=True,
                )
            with Horizontal():
                yield Label(_("Safe CRLF"), classes="input-label")
                yield Select(
                    [("", ""), ("true", "true"), ("false", "false"), ("warn", "warn")],
                    id="core-safecrlf",
                    allow_blank=True,
                )

    def _compose_commit_tab(self) -> ComposeResult:
        with Vertical():
            with Horizontal():
                yield Label(_("Commit Template"), classes="input-label")
                yield Input(placeholder=_("Path to commit template"), id="commit-template")
            yield Checkbox(_("Sign commits with GPG"), id="commit-gpgsign")

    def _compose_merge_tab(self) -> ComposeResult:
        with Vertical():
            with Horizontal():
                yield Label(_("Conflict Style"), classes="input-label")
                yield Select(
                    [("", ""), ("merge", "merge"), ("diff3", "diff3")],
                    id="merge-conflictstyle",
                    allow_blank=True,
                )
            with Horizontal():
                yield Label(_("Pull Rebase"), classes="input-label")
                yield Select(
                    [("", ""), ("true", "true"), ("false", "false"), ("interactive", "interactive"), ("preserve", "preserve")],
                    id="pull-rebase",
                    allow_blank=True,
                )

    def _compose_other_tab(self) -> ComposeResult:
        with Vertical():
            yield Checkbox(_("Enable color output"), id="color-ui")
            with Horizontal():
                yield Label(_("Default Branch Name"), classes="input-label")
                yield Input(placeholder=_("e.g., main, master"), id="init-defaultbranch")
            with Horizontal():
                yield Label(_("Credential Helper"), classes="input-label")
                yield Select(
                    [("", ""), ("cache", "cache"), ("store", "store"), ("gnome-keyring", "gnome-keyring"), ("kwallet", "kwallet")],
                    id="credential-helper",
                    allow_blank=True,
                )

    def on_mount(self) -> None:
        """Load git config on mount."""
        if not is_git_installed():
            self.show_message(_("Error: Git is not installed on this system."), error=True)
            return

        self.config = get_git_config()
        self._load_config()

    def _load_config(self) -> None:
        """Load config values into form."""
        if not self.config:
            return

        # User tab
        self.query_one("#user-name", Input).value = self.config.user_name or ""
        self.query_one("#user-email", Input).value = self.config.user_email or ""
        self.query_one("#user-signingkey", Input).value = self.config.user_signingkey or ""

        # Core tab
        self.query_one("#core-editor", Input).value = self.config.core_editor or ""
        self._set_select_value("core-autocrlf", self.config.core_autocrlf)
        self._set_select_value("core-safecrlf", self.config.core_safecrlf)

        # Commit tab
        self.query_one("#commit-template", Input).value = self.config.commit_template or ""
        self.query_one("#commit-gpgsign", Checkbox).value = self.config.commit_gpgsign

        # Merge tab
        self._set_select_value("merge-conflictstyle", self.config.merge_conflictstyle)
        self._set_select_value("pull-rebase", self.config.pull_rebase)

        # Other tab
        self.query_one("#color-ui", Checkbox).value = self.config.color_ui
        self.query_one("#init-defaultbranch", Input).value = self.config.init_defaultbranch or ""
        self._set_select_value("credential-helper", self.config.credential_helper)

    def _set_select_value(self, select_id: str, value: str) -> None:
        """Set select widget value."""
        try:
            select = self.query_one(f"#{select_id}", Select)
            if value:
                select.value = value
            else:
                select.value = Select.BLANK
        except Exception:
            pass

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
        elif event.button.id == "reset-btn":
            self._load_config()
            self.show_message(_("Reset to original values"), success=True)

    def _get_select_value(self, select_id: str) -> str:
        """Get select widget value."""
        try:
            select = self.query_one(f"#{select_id}", Select)
            value = select.value
            return str(value) if value != Select.BLANK else ""
        except Exception:
            return ""

    def action_save(self) -> None:
        """Save the git configuration."""
        if not self.config:
            return

        user_name = self.query_one("#user-name", Input).value.strip()
        user_email = self.query_one("#user-email", Input).value.strip()

        if not user_name or not user_email:
            self.show_message(_("Error: User name and email are required."), error=True)
            return

        # Update config object
        self.config.user_name = user_name
        self.config.user_email = user_email
        self.config.user_signingkey = self.query_one("#user-signingkey", Input).value.strip()
        self.config.core_editor = self.query_one("#core-editor", Input).value.strip()
        self.config.core_autocrlf = self._get_select_value("core-autocrlf")
        self.config.core_safecrlf = self._get_select_value("core-safecrlf")
        self.config.commit_template = self.query_one("#commit-template", Input).value.strip()
        self.config.commit_gpgsign = self.query_one("#commit-gpgsign", Checkbox).value
        self.config.merge_conflictstyle = self._get_select_value("merge-conflictstyle")
        self.config.pull_rebase = self._get_select_value("pull-rebase")
        self.config.color_ui = self.query_one("#color-ui", Checkbox).value
        self.config.init_defaultbranch = self.query_one("#init-defaultbranch", Input).value.strip()
        self.config.credential_helper = self._get_select_value("credential-helper")

        if set_git_config(self.config):
            self.show_message(_("Success: Git configuration saved successfully."), success=True)
        else:
            self.show_message(_("Error: Failed to save Git configuration."), error=True)