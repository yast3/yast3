"""UI components for the Date & Time module (TUI)."""

from textual.app import ComposeResult
from textual.containers import Horizontal, Vertical
from textual.screen import Screen
from textual.widgets import Button, Checkbox, Header, Input, Label, OptionList, Static

from mast.core.i18n import _
from mast.core.datetime import (
    get_current_timezone,
    get_timezone_list,
    set_timezone,
    is_hwclock_utc,
    set_hwclock_utc,
    get_ntp_status,
    get_ntp_servers,
    set_ntp_servers,
    enable_ntp,
    disable_ntp,
    sync_time_now,
)


class DateTimeWindow(Screen):
    """TUI window for date and time configuration."""

    CSS = """
    Screen {
        align: center middle;
    }

    .container {
        width: 80;
        height: auto;
        padding: 2;
        border: solid green;
    }

    .section {
        margin-top: 2;
        padding-top: 1;
        border-top: solid gray;
    }

    .section-title {
        width: 100%;
        text-align: center;
        background: blue;
        color: white;
        margin-bottom: 1;
    }

    .input-label {
        width: 20;
        content-align: right middle;
        padding-right: 2;
    }

    .button-row {
        align: right middle;
        margin-top: 1;
        spacing: 2;
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

    OptionList {
        height: 10;
    }
    """

    BINDINGS = [
        ("escape", "app.pop_screen", "Back"),
        ("q", "app.pop_screen", "Back"),
        ("backspace", "backspace", "Delete search char"),
        ("ctrl+u", "clear_search", "Clear search"),
    ]

    def compose(self) -> ComposeResult:
        yield Header()
        with Vertical(classes="container"):
            yield Label(_("Date & Time Configuration"), classes="title")

            with Vertical(classes="section"):
                yield Label(_("Timezone"), classes="section-title")
                yield Label(_("Type to search..."), classes="input-label")
                yield OptionList(id="timezone-list")

            with Vertical(classes="section"):
                yield Label(_("Hardware Clock"), classes="section-title")
                yield Checkbox(_("Set hardware clock to UTC"), id="hwclock-check")

            with Vertical(classes="section"):
                yield Label(_("NTP Synchronization"), classes="section-title")
                yield Checkbox(_("Enable NTP synchronization"), id="ntp-check")
                with Horizontal():
                    yield Label(_("NTP Servers"), classes="input-label")
                    yield Input(placeholder=_("Enter NTP servers"), id="ntp-input")
                with Horizontal(classes="button-row"):
                    yield Button(_("Sync Now"), id="sync-now-btn")
                yield Static("", id="ntp-status")

            with Horizontal(classes="button-row"):
                yield Button(_("Save"), id="save-btn", variant="primary")

            yield Static("", id="message", classes="message")

    def on_mount(self) -> None:
        self._load_settings()

    def _load_settings(self):
        try:
            timezone = get_current_timezone()
            self.all_timezones = sorted(get_timezone_list())
            self.search_text = ""

            self._update_timezone_list("")

            filtered = [tz for tz in self.all_timezones]
            idx = filtered.index(timezone) if timezone in filtered else 0
            tz_list = self.query_one("#timezone-list", OptionList)
            tz_list.select_option(idx)
        except Exception as e:
            self.show_message(_("Error loading timezone: {0}").format(str(e)), error=True)

        try:
            utc = is_hwclock_utc()
            self.query_one("#hwclock-check", Checkbox).value = utc
        except Exception as e:
            self.show_message(_("Error loading hardware clock: {0}").format(str(e)), error=True)

        try:
            ntp_status = get_ntp_status()
            self.query_one("#ntp-check", Checkbox).value = ntp_status.enabled
            self.query_one("#ntp-input", Input).value = " ".join(ntp_status.servers)

            status_label = self.query_one("#ntp-status", Static)
            if ntp_status.synchronized:
                status_label.update(_("NTP synchronized"))
            else:
                status_label.update(_("NTP not synchronized"))
        except Exception as e:
            self.show_message(_("Error loading NTP status: {0}").format(str(e)), error=True)

    def _update_timezone_list(self, search_text):
        tz_list = self.query_one("#timezone-list", OptionList)
        tz_list.clear()
        search_text = search_text.lower()
        options = [tz for tz in self.all_timezones if search_text in tz.lower()]
        tz_list.add_options(options)

    def on_key(self, event) -> None:
        tz_list = self.query_one("#timezone-list", OptionList)
        if not tz_list.has_focus:
            return

        if event.key.isprintable() and event.key != " ":
            self.search_text += event.key
            self._update_timezone_list(self.search_text)
            if tz_list.options:
                tz_list.select_option(0)
            event.stop()
        elif event.key == "backspace":
            self.search_text = self.search_text[:-1]
            self._update_timezone_list(self.search_text)
            if tz_list.options:
                tz_list.select_option(0)
            event.stop()
        elif event.key == "ctrl+u":
            self.search_text = ""
            self._update_timezone_list("")
            event.stop()

    def action_backspace(self) -> None:
        tz_list = self.query_one("#timezone-list", OptionList)
        if tz_list.has_focus:
            self.search_text = self.search_text[:-1]
            self._update_timezone_list(self.search_text)
            if tz_list.options:
                tz_list.select_option(0)

    def action_clear_search(self) -> None:
        tz_list = self.query_one("#timezone-list", OptionList)
        if tz_list.has_focus:
            self.search_text = ""
            self._update_timezone_list("")

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
            self._on_save_all()
        elif event.button.id == "sync-now-btn":
            self._on_sync_now()

    def _on_save_all(self):
        errors = []

        tz_list = self.query_one("#timezone-list", OptionList)
        idx = tz_list.highlighted_option
        if idx is not None:
            options = tz_list.options
            if idx < len(options):
                timezone = options[idx].prompt
                status, message = set_timezone(timezone)
                if status != "ok":
                    errors.append(_("Timezone: {0}").format(message))

        utc = self.query_one("#hwclock-check", Checkbox).value
        status, message = set_hwclock_utc(utc)
        if status != "ok":
            errors.append(_("Hardware clock: {0}").format(message))

        enabled = self.query_one("#ntp-check", Checkbox).value
        servers = self.query_one("#ntp-input", Input).value.strip().split()
        if enabled:
            if not servers:
                servers = ["pool.ntp.org"]
            status, message = set_ntp_servers(servers)
            if status == "ok":
                status2, message2 = enable_ntp()
                if status2 != "ok":
                    errors.append(_("NTP: {0}").format(message2))
            else:
                errors.append(_("NTP: {0}").format(message))
        else:
            status, message = disable_ntp()
            if status != "ok":
                errors.append(_("NTP: {0}").format(message))

        if errors:
            self.show_message("\n".join(errors), error=True)
        else:
            self.show_message(_("All settings saved successfully."), success=True)

    def _on_sync_now(self):
        status, message = sync_time_now()

        if status == "ok":
            self.show_message(message, success=True)
            self._load_settings()
        elif status == "permission_denied":
            self.show_message(_("Error: Permission denied. Root permission required."), error=True)
        elif status == "pkexec_failed":
            self.show_message(_("Error: Authentication failed or pkexec not available."), error=True)
        else:
            self.show_message(_("Error: {0}").format(message), error=True)