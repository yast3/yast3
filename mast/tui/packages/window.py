"""UI components for the Packages module (TUI)."""

from textual.app import ComposeResult
from textual.containers import Vertical
from textual.screen import Screen
from textual.widgets import Button, Header, Label, Static

from mast.core.i18n import _


class PackagesWindow(Screen):
    """TUI window for packages configuration."""

    CSS = """
    Screen {
        align: center middle;
    }

    .container {
        width: 60;
        height: auto;
        padding: 2;
        border: solid green;
    }

    Button {
        margin-top: 1;
    }
    """

    BINDINGS = [
        ("escape", "app.pop_screen", "Back"),
        ("q", "app.pop_screen", "Back"),
    ]

    def compose(self) -> ComposeResult:
        yield Header()
        with Vertical(classes="container"):
            yield Label(_("Packages Management"), classes="title")
            yield Static(_("Package management functionality is not yet implemented in TUI mode."))
            yield Static(_("Please use the Qt6 GUI version for full package management features."))
            yield Button(_("Close"), id="close-btn")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button press."""
        if event.button.id == "close-btn":
            self.app.pop_screen()