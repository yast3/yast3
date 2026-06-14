"""Repositories module package."""

from ...module import Module

from .window import RepositoriesWindow


class RepositoriesModule(Module):
    window: RepositoriesWindow | None = None

    def __init__(self):
        super().__init__(_("Repositories"), ("system-software-install", "package-x-generic"))

    def launch(self) -> None:
        """Launch the repositories module window."""
        if self.window is None:
            self.window = RepositoriesWindow()
            self.window.setWindowTitle(self.name + ' — ' + _("YaST3"))
            self.window.closed.connect(self._on_window_closed)
        self.window.show()
        self.window.activateWindow()

    def _on_window_closed(self) -> None:
        """Handle window closed signal."""
        self.window = None


__all__ = ['RepositoriesModule']