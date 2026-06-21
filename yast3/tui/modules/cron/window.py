"""UI components for the Cron module (TUI)."""

from textual.app import ComposeResult
from textual.containers import Horizontal, Vertical
from textual.screen import Screen
from textual.widgets import Button, DataTable, Header, Input, Label, Static, TabbedContent, TabPane

from yast3.core.i18n import _
from yast3.core.modules.cron import CronJob, load_cron_jobs, save_cron_jobs


class CronWindow(Screen):
    """TUI window for cron configuration."""

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
        self.user_jobs: list[CronJob] = []
        self.root_jobs: list[CronJob] = []

    def compose(self) -> ComposeResult:
        yield Header()
        with Vertical(classes="container"):
            with TabbedContent(id="tabs"):
                with TabPane(_("User Cron Jobs"), id="user-tab"):
                    yield from self._compose_cron_tab("user")
                with TabPane(_("Root Cron Jobs"), id="root-tab"):
                    yield from self._compose_cron_tab("root")
            yield Static("", id="message", classes="message")

    def _compose_cron_tab(self, mode: str) -> ComposeResult:
        with Vertical():
            with Horizontal(classes="button-row"):
                yield Button(_("Add"), id=f"add-{mode}-btn")
                yield Button(_("Edit"), id=f"edit-{mode}-btn")
                yield Button(_("Delete"), id=f"delete-{mode}-btn")
                yield Button(_("Save"), id=f"save-{mode}-btn", variant="primary")
            yield DataTable(id=f"{mode}-table")

    def on_mount(self) -> None:
        """Load cron jobs on mount."""
        self._setup_table("user")
        self._setup_table("root")
        self.load_jobs()

    def _setup_table(self, mode: str) -> None:
        """Setup table columns."""
        table = self.query_one(f"#{mode}-table", DataTable)
        table.add_columns(_("Enabled"), _("Minute"), _("Hour"), _("Day"), _("Month"), _("Weekday"), _("Command"))

    def load_jobs(self) -> None:
        """Load cron jobs."""
        user_jobs, user_error = load_cron_jobs(True)
        root_jobs, root_error = load_cron_jobs(False)

        if user_error:
            self.show_message(_("User cron error: {0}").format(user_error), error=True)
        if root_error:
            self.show_message(_("Root cron error: {0}").format(root_error), error=True)

        self.user_jobs = user_jobs
        self.root_jobs = root_jobs
        self.populate_tables()

    def populate_tables(self) -> None:
        """Populate both tables."""
        self._populate_table("user", self.user_jobs)
        self._populate_table("root", self.root_jobs)

    def _populate_table(self, mode: str, jobs: list[CronJob]) -> None:
        """Populate a single table."""
        table = self.query_one(f"#{mode}-table", DataTable)
        table.clear()

        for job in jobs:
            enabled = "✓" if job.enabled else ""
            command = job.command
            if job.comment:
                command += f"  {job.comment}"
            table.add_row(enabled, job.minute, job.hour, job.day, job.month, job.weekday, command)

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
        button_id = event.button.id
        if button_id and "-btn" in button_id:
            parts = button_id.replace("-btn", "").split("-")
            action = parts[0]
            mode = parts[1]

            if action == "add":
                self._add_job(mode)
            elif action == "edit":
                self._edit_job(mode)
            elif action == "delete":
                self._delete_job(mode)
            elif action == "save":
                self._save_jobs(mode)

    def _get_jobs(self, mode: str) -> list[CronJob]:
        """Get jobs list for mode."""
        return self.user_jobs if mode == "user" else self.root_jobs

    def _add_job(self, mode: str) -> None:
        """Add a new cron job."""
        self.app.push_screen(CronEditScreen(self, _("Add Cron Job"), mode))

    def _edit_job(self, mode: str) -> None:
        """Edit the selected cron job."""
        table = self.query_one(f"#{mode}-table", DataTable)
        jobs = self._get_jobs(mode)
        if table.cursor_row < 0 or table.cursor_row >= len(jobs):
            self.show_message(_("Please select a cron job to edit."), error=True)
            return

        job = jobs[table.cursor_row]
        self.app.push_screen(
            CronEditScreen(
                self,
                _("Edit Cron Job"),
                mode,
                job,
                table.cursor_row,
            )
        )

    def _delete_job(self, mode: str) -> None:
        """Delete the selected cron job."""
        table = self.query_one(f"#{mode}-table", DataTable)
        jobs = self._get_jobs(mode)
        if table.cursor_row < 0 or table.cursor_row >= len(jobs):
            self.show_message(_("Please select a cron job to delete."), error=True)
            return

        jobs.pop(table.cursor_row)
        self._populate_table(mode, jobs)
        self.show_message(_("Cron job deleted."), success=True)

    def _save_jobs(self, mode: str) -> None:
        """Save cron jobs."""
        jobs = self._get_jobs(mode)
        user_mode = mode == "user"
        result = save_cron_jobs(jobs, user_mode)

        if result == "ok":
            self.show_message(_("Success: Cron jobs saved successfully."), success=True)
        elif result == "permission_denied":
            self.show_message(_("Error: Permission denied. Root permission required."), error=True)
        else:
            self.show_message(_("Error: Failed to save cron jobs."), error=True)

    def add_job(self, mode: str, job: CronJob) -> None:
        """Add a new job."""
        jobs = self._get_jobs(mode)
        jobs.append(job)
        self._populate_table(mode, jobs)
        self.show_message(_("Cron job added."), success=True)

    def update_job(self, mode: str, row: int, job: CronJob) -> None:
        """Update an existing job."""
        jobs = self._get_jobs(mode)
        jobs[row] = job
        self._populate_table(mode, jobs)
        self.show_message(_("Cron job updated."), success=True)


class CronEditScreen(Screen):
    """Screen for adding/editing a cron job."""

    CSS = """
    .container {
        width: 70;
        height: auto;
        padding: 2;
        border: solid green;
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

    def __init__(
        self,
        parent: CronWindow,
        title: str,
        mode: str,
        job: CronJob | None = None,
        row: int = -1,
    ) -> None:
        super().__init__()
        self.parent_window = parent
        self.screen_title = title
        self.mode = mode
        self.edit_row = row
        self.initial_job = job or CronJob(
            enabled=True,
            minute="*",
            hour="*",
            day="*",
            month="*",
            weekday="*",
            command="",
            comment="",
        )

    def compose(self) -> ComposeResult:
        with Vertical(classes="container"):
            yield Label(self.screen_title, classes="title")
            with Horizontal():
                yield Label(_("Minute"), classes="input-label")
                yield Input(value=self.initial_job.minute, id="minute-input", placeholder="0-59 or *")
            with Horizontal():
                yield Label(_("Hour"), classes="input-label")
                yield Input(value=self.initial_job.hour, id="hour-input", placeholder="0-23 or *")
            with Horizontal():
                yield Label(_("Day"), classes="input-label")
                yield Input(value=self.initial_job.day, id="day-input", placeholder="1-31 or *")
            with Horizontal():
                yield Label(_("Month"), classes="input-label")
                yield Input(value=self.initial_job.month, id="month-input", placeholder="1-12 or *")
            with Horizontal():
                yield Label(_("Weekday"), classes="input-label")
                yield Input(value=self.initial_job.weekday, id="weekday-input", placeholder="0-7 or *")
            with Horizontal():
                yield Label(_("Command"), classes="input-label")
                yield Input(value=self.initial_job.command, id="command-input", placeholder=_("Command to execute"))
            with Horizontal():
                yield Label(_("Comment"), classes="input-label")
                yield Input(value=self.initial_job.comment, id="comment-input", placeholder=_("Optional comment"))
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
        minute = self.query_one("#minute-input", Input).value.strip()
        hour = self.query_one("#hour-input", Input).value.strip()
        day = self.query_one("#day-input", Input).value.strip()
        month = self.query_one("#month-input", Input).value.strip()
        weekday = self.query_one("#weekday-input", Input).value.strip()
        command = self.query_one("#command-input", Input).value.strip()
        comment = self.query_one("#comment-input", Input).value.strip()

        if not command:
            self.parent_window.show_message(_("Error: Command is required."), error=True)
            self.app.pop_screen()
            return

        job = CronJob(
            enabled=self.initial_job.enabled,
            minute=minute or "*",
            hour=hour or "*",
            day=day or "*",
            month=month or "*",
            weekday=weekday or "*",
            command=command,
            comment=comment,
        )

        if self.edit_row >= 0:
            self.parent_window.update_job(self.mode, self.edit_row, job)
        else:
            self.parent_window.add_job(self.mode, job)
        self.app.pop_screen()