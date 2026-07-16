"""GTK4 import button for predefined third-party repositories."""

from __future__ import annotations

import gi

gi.require_version("Gtk", "4.0")

from gi.repository import Gtk

from mast.core.i18n import _
from mast.core.repositories.repos import RepoEntry
from mast.core.repositories.third_party_repos import third_party_repos


class ImportRepoButton(Gtk.MenuButton):
    """Dropdown button for selecting predefined repositories to import."""

    def __init__(self, on_repo_selected, **kwargs):
        super().__init__(**kwargs)
        self._on_repo_selected = on_repo_selected
        self.set_label(_("Import"))

        popover = Gtk.Popover()
        popover_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=4)
        popover_box.set_margin_top(6)
        popover_box.set_margin_bottom(6)
        popover_box.set_margin_start(6)
        popover_box.set_margin_end(6)

        for entry in third_party_repos:
            item_btn = Gtk.Button(label=entry.name)
            item_btn.set_halign(Gtk.Align.FILL)
            item_btn.connect("clicked", self._on_item_clicked, entry)
            popover_box.append(item_btn)

        popover.set_child(popover_box)
        self.set_popover(popover)

    def _on_item_clicked(self, _button: Gtk.Button, entry: RepoEntry) -> None:
        self.popdown()
        self._on_repo_selected(entry)
