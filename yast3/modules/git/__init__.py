"""Git module package."""

from ...i18n import _
from ...module import Module

from .window import GitWindow


class GitModule(Module):
    window: GitWindow | None = None

    def __init__(self):
        super().__init__(_("Git"), ("preferences-git", "settings"))

    def launch(self) -> None:
        """Launch the Git module window."""
        if self.window is None:
            self.window = GitWindow()
            self.window.setWindowTitle(self.name + ' — ' + _("YaST3"))
            self.window.closed.connect(self._on_window_closed)
        self.window.show()
        self.window.activateWindow()

    def _on_window_closed(self) -> None:
        """Handle window closed signal."""
        self.window = None


__all__ = ['GitModule']