"""Main application window showing module buttons."""

from textual.app import App, ComposeResult
from textual.containers import Grid, ScrollableContainer
from textual.widgets import Button, Footer, Header, Static

from yast3.core.i18n import _
from yast3.core.module import Module
from yast3.tui import (
    CronModule,
    GitModule,
    HostnameModule,
    HostsModule,
    PackagesModule,
    ProxyModule,
    RepositoriesModule,
    SSHClientModule,
)


class ModuleButton(Button):
    """A button for launching a module."""

    CSS = """
    ModuleButton {
        width: 100%;
    }
    """

    def __init__(self, module: Module) -> None:
        safe_id = module.name.lower().replace(" ", "-").replace("_", "-")
        label = f"{module.emoji} {module.name}"
        super().__init__(label, id=f"module-{safe_id}")
        self.module = module


class MainWindow(App):
    """Main YaST3 TUI application."""

    CSS = """
    .module-grid {
        grid-size: 4;
        grid-columns: 1fr 1fr 1fr 1fr;
        grid-rows: auto;
        grid-gutter: 2;
        padding: 2;
        width: 100%;
    }

    .title {
        text-align: center;
        text-style: bold;
        margin-bottom: 1;
        padding: 1;
    }

    ScrollableContainer {
        align: center top;
    }
    """

    BINDINGS = [
        ("q", "quit", "Quit"),
        ("escape", "quit", "Quit"),
    ]

    def __init__(self) -> None:
        super().__init__()
        self.modules: list[Module] = [
            HostnameModule(),
            GitModule(),
            HostsModule(),
            CronModule(),
            RepositoriesModule(),
            ProxyModule(),
            SSHClientModule(),
            PackagesModule(),
        ]

    def compose(self) -> ComposeResult:
        yield Header()
        yield Footer()
        with ScrollableContainer():
            yield Static("YaST3", classes="title")
            with Grid(classes="module-grid"):
                for module in self.modules:
                    yield ModuleButton(module)

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle module button press."""
        if isinstance(event.button, ModuleButton):
            screen = event.button.module.create_window()
            if screen:
                self.push_screen(screen)