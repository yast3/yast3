"""UI components for the Languages module (TUI)."""

from textual.app import ComposeResult
from textual.containers import Horizontal, Vertical
from textual.screen import Screen
from textual.widgets import Button, Header, Label, Static, Select

from yast3.core.i18n import _
from yast3.core.languages import (
    get_current_language,
    get_use_utf8,
    build_languages_map,
    save_language_settings,
    LanguageInfo,
)


class LanguagesWindow(Screen):
    """TUI window for language configuration."""

    CSS = """
    Screen {
        align: center middle;
    }

    .container {
        width: 70;
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

    Select {
        width: 40;
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
            yield Label(_("Language Configuration"), classes="title")
            with Horizontal():
                yield Label(_("Language"), classes="input-label")
                yield Select([], id="language-select")
            with Horizontal():
                yield Label(_("Use UTF-8"), classes="input-label")
                yield Static(_("Yes"), id="utf8-status")
            with Horizontal(classes="button-row"):
                yield Button(_("Save"), id="save-btn", variant="primary")
                yield Button(_("Cancel"), id="cancel-btn")
            yield Static("", id="message", classes="message")

    def on_mount(self) -> None:
        """Load current language settings on mount."""
        try:
            languages_map = build_languages_map()
            self._language_info: dict[str, LanguageInfo] = languages_map

            sorted_languages = sorted(
                languages_map.items(),
                key=lambda x: x[1].name_english
            )

            options = [(info.name, code) for code, info in sorted_languages]
            select = self.query_one("#language-select", Select)
            select.set_options(options)

            current_lang = get_current_language()
            select.value = current_lang

            utf8_status = get_use_utf8()
            self.query_one("#utf8-status", Static).update(_("Yes") if utf8_status else _("No"))
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
        """Save the language settings."""
        lang_code = self.query_one("#language-select", Select).value

        if not lang_code:
            self.show_message(_("Error: Please select a language."), error=True)
            return

        status, message = save_language_settings(lang_code, use_utf8=True)

        if status == "ok":
            info = self._language_info.get(lang_code)
            lang_name = info.name if info else lang_code
            self.show_message(
                _("Success: Language changed to '{0}'. Changes take effect after logout.").format(lang_name),
                success=True,
            )
            self.set_timer(2.0, self.app.pop_screen)
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