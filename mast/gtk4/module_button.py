"""GTK4 button widget for launching a module."""

from __future__ import annotations

from typing import Protocol, cast

from gi.repository import Gtk

from mast.core.i18n import _
from mast.gtk4.module import Module


class _GtkLaunchableModule(Protocol):
    def launch(self, parent: Gtk.ApplicationWindow | None = None) -> None: ...


class ModuleButton(Gtk.Button):
    """A button for launching a module window."""

    def __init__(self, module: Module, parent: Gtk.ApplicationWindow | None = None) -> None:
        super().__init__()
        self._module = module
        self._parent = parent

        self.set_size_request(160, 120)

        content_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        content_box.set_margin_top(16)
        content_box.set_margin_bottom(16)
        content_box.set_margin_start(16)
        content_box.set_margin_end(16)

        icon_name = self._resolve_icon_name(module)
        if icon_name:
            icon = Gtk.Image.new_from_icon_name(icon_name)
            icon.set_pixel_size(48)
            content_box.append(icon)
        else:
            emoji_label = Gtk.Label(label=module.emoji)
            content_box.append(emoji_label)

        name_label = Gtk.Label(label=module.name)
        content_box.append(name_label)

        overlay = Gtk.Overlay()
        overlay.set_child(content_box)

        if module.experimental:
            badge = Gtk.Image.new_from_icon_name("dialog-warning-symbolic")
            badge.set_pixel_size(24)
            badge.set_tooltip_text(_("Experimental"))
            badge.set_halign(Gtk.Align.END)
            badge.set_valign(Gtk.Align.START)
            badge.set_margin_top(8)
            badge.set_margin_end(8)
            overlay.add_overlay(badge)

        self.set_child(overlay)
        self.connect("clicked", self._on_clicked)

    def _resolve_icon_name(self, module: Module) -> str | None:
        display = self._parent.get_display() if self._parent else self.get_display()
        if display is None:
            return None

        icon_theme = Gtk.IconTheme.get_for_display(display)
        for name in module.icon_names:
            if icon_theme.has_icon(name):
                return name

        return None

    def _on_clicked(self, _button: Gtk.Button) -> None:
        cast(_GtkLaunchableModule, self._module).launch(self._parent)