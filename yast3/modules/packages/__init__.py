"""Packages module package."""

from yast3.i18n import _
from yast3.module import Module
from yast3.modules.packages.winodw import PackagesWindow


class PackagesModule(Module):
    window: PackagesWindow | None = None

    def __init__(self):
        super().__init__(_("Packages"), ("package-manager", "package"))

    def launch(self) -> None:
        """Launch the packages module window."""
        if self.window is None:
            self.window = PackagesWindow()
            self.window.setWindowTitle(self.name + " — " + _("YaST3"))
        self.window.show()
        self.window.activateWindow()


__all__ = ["PackagesModule"]
