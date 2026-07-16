"""UI components for the Languages module (TUI)."""

from textual.app import ComposeResult
from textual.containers import Horizontal, Vertical
from textual.screen import Screen
from textual.widgets import Button, DataTable, Header, Input, Label, Static, Select, TabbedContent, TabPane

from mast.core.i18n import _
from mast.core.languages import (
    get_current_language,
    get_use_utf8,
    save_language_settings,
    get_all_locales,
    install_locale,
    uninstall_locale,
    LocaleItem,
)


class LanguageSettingsPane(TabPane):
    def __init__(self, locales: list[LocaleItem]):
        super().__init__("System Language", id="system-language-tab")
        self._all_locales = locales

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
        try:
            sorted_locales = sorted(
                self._all_locales,
                key=lambda x: x.name
            )

            options = [(loc.name, loc.code) for loc in sorted_locales]
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

    def _is_locale_installed(self, locale_code: str) -> bool:
        return any(loc.code == locale_code and loc.installed for loc in self._all_locales)

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "save-btn":
            self.save_language()
        elif event.button.id == "cancel-btn":
            self.app.pop_screen()

    def save_language(self) -> None:
        lang_code = self.query_one("#language-select", Select).value

        if not lang_code:
            self.show_message(_("Error: Please select a language."), error=True)
            return

        if not self._is_locale_installed(lang_code):
            locale = next((loc for loc in self._all_locales if loc.code == lang_code), None)
            if locale:
                self._install_language_and_save(locale, lang_code)
            else:
                self.show_message(_("Error: Language '{0}' not found.").format(lang_code), error=True)
            return

        self._save_language_settings(lang_code)

    def _install_language_and_save(self, locale: LocaleItem, lang_code: str) -> None:
        status, message = install_locale(lang_code)

        if status == "ok":
            for loc in self._all_locales:
                if loc.code == lang_code:
                    loc.installed = True
                    break
            self.show_message(f"Success: {message}", success=True)
            self._save_language_settings(lang_code)
        elif status == "pkexec_failed":
            self.show_message("Error: Authentication failed.", error=True)
        else:
            self.show_message(f"Error: {message}", error=True)

    def _save_language_settings(self, lang_code: str) -> None:
        status, message = save_language_settings(lang_code, use_utf8=True)

        if status == "ok":
            locale = next((loc for loc in self._all_locales if loc.code == lang_code), None)
            lang_name = locale.name if locale else lang_code
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


class LanguageManagementPane(TabPane):
    def __init__(self, locales: list[LocaleItem]):
        super().__init__("Language Management", id="language-tab")
        self._all_locales = locales

    def compose(self) -> ComposeResult:
        with Vertical():
            yield Input(placeholder="Search", id="search-input")
            with Horizontal(classes="button-row"):
                yield Button("Install", id="install-btn", variant="primary")
                yield Button("Uninstall", id="uninstall-btn", variant="error")
            yield DataTable(id="locale-table")
            yield Static("", id="message", classes="message")

    def on_mount(self) -> None:
        self._filter_locales("")

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
        try:
            from mast.core.languages import refresh_locale_cache
            refresh_locale_cache()
            self._all_locales = get_all_locales()
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

    def install_selected(self) -> None:
        table = self.query_one("#locale-table", DataTable)
        selected_rows = table.cursor_row

        if selected_rows is None:
            self.show_message("Error: Please select a locale to install.", error=True)
            return

        loc = self._locales[selected_rows]
        if loc.installed:
            self.show_message("Error: Language is already installed.", error=True)
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
            self.show_message("Error: Language is not installed.", error=True)
            return

        self._perform_uninstall(loc)

    def _perform_install(self, loc) -> None:
        status, message = install_locale(loc.code)

        if status == "ok":
            for locale in self._all_locales:
                if locale.code == loc.code:
                    locale.installed = True
                    break
            self.show_message(f"Success: {message}", success=True)
            self._filter_locales(self.query_one("#search-input", Input).value)
        elif status == "pkexec_failed":
            self.show_message("Error: Authentication failed.", error=True)
        else:
            self.show_message(f"Error: {message}", error=True)

    def _perform_uninstall(self, loc) -> None:
        status, message = uninstall_locale(loc.code)

        if status == "ok":
            for locale in self._all_locales:
                if locale.code == loc.code:
                    locale.installed = False
                    break
            self.show_message(f"Success: {message}", success=True)
            self._filter_locales(self.query_one("#search-input", Input).value)
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
        locales = get_all_locales()
        with Vertical(classes="container"):
            yield Label("Language Configuration", classes="title")
            yield TabbedContent(
                LanguageSettingsPane(locales),
                LanguageManagementPane(locales),
            )
