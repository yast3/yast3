"""Packages module package - GTK4 GUI."""

import subprocess

from mast.core.i18n import _
from mast.gtk4.module import Module


class PackagesModule(Module):
    def __init__(self):
        super().__init__(_("Packages"), ("package-manager", "package"))

    def launch(self, parent=None) -> None:
        subprocess.Popen(["myrlyn-sudo"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


__all__ = ["PackagesModule"]