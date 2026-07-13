"""UI components for the Languages module (TUI)."""

from textual.app import ComposeResult
from textual.containers import Horizontal, Vertical
from textual.screen import Screen
from textual.widgets import Button, DataTable, Header, Input, Label, Static, Select, TabbedContent, TabPane


class LanguageSettingsPane(TabPane):
    def __init__(self):
        super().__init__("Language", id="language-tab")

    def compose(self) -> ComposeResult:
        with Vertical():
            with Horizontal():
                yield Label("Language", classes="input-label")
                yield Select([], id="language-select")
            with Horizontal():
                yield Label("Use UTF-8", classes="input-label")
                yield Static("Yes", id="utf8-status")
            with Horizontal(classes="button-row"):
                yield Button("Save", id="save-btn", variant="primary")
                yield Button("Cancel", id="cancel-btn")
            yield Static("", id="message", classes="message")

    def on_mount(self) -> None:
        from yast3.core.i18n import _
        from yast3.core.languages import get_current_language, get_use_utf8, build_languages_map, LanguageInfo

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
            self.show_message(f"Error: {str(e)}", error=True)

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
            self.save_language()
        elif event.button.id == "cancel-btn":
            self.app.pop_screen()

    def save_language(self) -> None:
        from yast3.core.i18n import _
        from yast3.core.languages import save_language_settings

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


class LocaleManagementPane(TabPane):
    def __init__(self):
        super().__init__("Locale Management", id="locale-tab")

    def compose(self) -> ComposeResult:
        with Vertical():
            with Horizontal():
                yield Label("Search:", classes="input-label")
                yield Input(placeholder="Search by code or name...", id="search-input")
            with Horizontal(classes="button-row"):
                yield Button("Install", id="install-btn", variant="primary")
                yield Button("Uninstall", id="uninstall-btn", variant="error")
                yield Button("Refresh", id="refresh-btn")
            yield DataTable(id="locale-table")
            yield Static("", id="message", classes="message")

    def on_mount(self) -> None:
        self.refresh_locales()

    def _filter_locales(self, search_text: str) -> None:
        search_text = search_text.lower().strip()

        if not search_text:
            filtered = self._all_locales
        else:
            filtered = [
                loc for loc in self._all_locales
                if search_text in loc.code.lower() or search_text in loc.name.lower()
            ]

        self._locales = filtered
        table = self.query_one("#locale-table", DataTable)
        table.clear()
        table.add_columns("Code", "Name", "Status")

        for loc in filtered:
            status = "Installed" if loc.installed else "Not Installed"
            table.add_row(loc.code, loc.name, status)

        self.query_one("#message", Static).update("")

    def on_input_changed(self, event: Input.Changed) -> None:
        if event.input.id == "search-input":
            self._filter_locales(event.value)

    def refresh_locales(self) -> None:
        from yast3.core.languages import get_locales_with_status

        try:
            self._all_locales = get_locales_with_status()
            search_input = self.query_one("#search-input", Input)
            self._filter_locales(search_input.value)
        except Exception as e:
            self.show_message(f"Error: {str(e)}", error=True)

    def show_message(self, message: str, error: bool = False, success: bool = False) -> None:
        msg_widget = self.query_one("#message", Static)
        msg_widget.update(message)
        msg_widget.remove_class("error", "success")
        if error:
            msg_widget.add_class("error")
        elif success:
            msg_widget.add_class("success")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "install-btn":
            self.install_selected()
        elif event.button.id == "uninstall-btn":
            self.uninstall_selected()
        elif event.button.id == "refresh-btn":
            self.refresh_locales()

    def install_selected(self) -> None:
        table = self.query_one("#locale-table", DataTable)
        selected_rows = table.cursor_row

        if selected_rows is None:
            self.show_message("Error: Please select a locale to install.", error=True)
            return

        loc = self._locales[selected_rows]
        if loc.installed:
            self.show_message("Error: Locale is already installed.", error=True)
            return

        self._perform_install(loc)

    def uninstall_selected(self) -> None:
        table = self.query_one("#locale-table", DataTable)
        selected_rows = table.cursor_row

        if selected_rows is None:
            self.show_message("Error: Please select a locale to uninstall.", error=True)
            return

        loc = self._locales[selected_rows]
        if not loc.installed:
            self.show_message("Error: Locale is not installed.", error=True)
            return

        self._perform_uninstall(loc)

    def _perform_install(self, loc) -> None:
        from yast3.core.languages import install_locale

        status, message = install_locale(loc.code)

        if status == "ok":
            self.show_message(f"Success: {message}", success=True)
            self.refresh_locales()
        elif status == "pkexec_failed":
            self.show_message("Error: Authentication failed.", error=True)
        else:
            self.show_message(f"Error: {message}", error=True)

    def _perform_uninstall(self, loc) -> None:
        from yast3.core.languages import uninstall_locale

        status, message = uninstall_locale(loc.code)

        if status == "ok":
            self.show_message(f"Success: {message}", success=True)
            self.refresh_locales()
        elif status == "pkexec_failed":
            self.show_message("Error: Authentication failed.", error=True)
        else:
            self.show_message(f"Error: {message}", error=True)


class LanguagesWindow(Screen):
    CSS = """
    Screen {
        align: center middle;
    }

    .container {
        width: 80;
        height: 40;
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
        height: 3;
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

    Input {
        width: 40;
    }

    DataTable {
        height: 100%;
    }

    TabbedContent {
        height: 100%;
        width: 100%;
    }
    """

    BINDINGS = [
        ("escape", "app.pop_screen", "Back"),
        ("q", "app.pop_screen", "Back"),
    ]

    def compose(self) -> ComposeResult:
        yield Header()
        with Vertical(classes="container"):
            yield Label("Language Configuration", classes="title")
            yield TabbedContent(
                LanguageSettingsPane(),
                LocaleManagementPane(),
            )