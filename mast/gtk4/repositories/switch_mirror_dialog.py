import gi

gi.require_version("Gtk", "4.0")

from gi.repository import Gtk

from mast.core.i18n import _
from mast.core.repositories.opensuse_mirrors import opensuse_mirrors
from mast.core.repositories.packman_mirrors import packman_mirrors


class SwitchMirrorDialog(Gtk.Dialog):
    """Dialog for switching mirrors for openSUSE and Packman repositories."""

    def __init__(self, parent):
        super().__init__(
            title=_("Switch Mirror"),
            transient_for=parent,
            modal=True,
        )

        self.set_default_size(450, -1)

        self.add_button(_("Cancel"), Gtk.ResponseType.CANCEL)
        self.add_button(_("OK"), Gtk.ResponseType.OK)

        content = self.get_content_area()
        content.set_spacing(12)
        content.set_margin_top(12)
        content.set_margin_bottom(12)
        content.set_margin_start(12)
        content.set_margin_end(12)

        opensuse_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=12)
        opensuse_label = Gtk.Label(label=_("openSUSE"))
        opensuse_label.set_size_request(80, -1)
        opensuse_label.set_halign(Gtk.Align.START)
        opensuse_box.append(opensuse_label)

        self.opensuse_combo = Gtk.ComboBoxText()
        self.opensuse_combo.set_hexpand(True)
        self.opensuse_mirrors = []
        for mirror in opensuse_mirrors:
            self.opensuse_combo.append_text(f"{mirror.organization} ({mirror.location})")
            self.opensuse_mirrors.append(mirror)
        self.opensuse_combo.set_active(0)
        self.opensuse_combo.connect("changed", self._on_opensuse_mirror_changed)
        opensuse_box.append(self.opensuse_combo)

        self.opensuse_proto_combo = Gtk.ComboBoxText()
        self.opensuse_proto_combo.set_size_request(80, -1)
        self.opensuse_protocols = []
        self._update_opensuse_protocols(0)
        opensuse_box.append(self.opensuse_proto_combo)
        content.append(opensuse_box)

        packman_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=12)
        packman_label = Gtk.Label(label=_("Packman"))
        packman_label.set_size_request(80, -1)
        packman_label.set_halign(Gtk.Align.START)
        packman_box.append(packman_label)

        self.packman_combo = Gtk.ComboBoxText()
        self.packman_combo.set_hexpand(True)
        self.packman_mirrors = []
        for mirror in packman_mirrors:
            self.packman_combo.append_text(f"{mirror.organization} ({mirror.location})")
            self.packman_mirrors.append(mirror)
        self.packman_combo.set_active(0)
        self.packman_combo.connect("changed", self._on_packman_mirror_changed)
        packman_box.append(self.packman_combo)

        self.packman_proto_combo = Gtk.ComboBoxText()
        self.packman_proto_combo.set_size_request(80, -1)
        self.packman_protocols = []
        self._update_packman_protocols(0)
        packman_box.append(self.packman_proto_combo)
        content.append(packman_box)

    def _on_opensuse_mirror_changed(self, combo) -> None:
        self._update_opensuse_protocols(combo.get_active())

    def _on_packman_mirror_changed(self, combo) -> None:
        self._update_packman_protocols(combo.get_active())

    def _update_opensuse_protocols(self, index: int) -> None:
        self.opensuse_proto_combo.remove_all()
        self.opensuse_protocols = []
        mirror = self.opensuse_mirrors[index]
        for proto in mirror.protocols:
            self.opensuse_proto_combo.append_text(proto.upper())
            self.opensuse_protocols.append(proto)
        self.opensuse_proto_combo.set_active(0)

    def _update_packman_protocols(self, index: int) -> None:
        self.packman_proto_combo.remove_all()
        self.packman_protocols = []
        mirror = self.packman_mirrors[index]
        for proto in mirror.protocols:
            self.packman_proto_combo.append_text(proto.upper())
            self.packman_protocols.append(proto)
        self.packman_proto_combo.set_active(0)

    def get_values(self) -> dict:
        opensuse_mirror = self.opensuse_mirrors[self.opensuse_combo.get_active()]
        opensuse_proto = self.opensuse_protocols[self.opensuse_proto_combo.get_active()]
        packman_mirror = self.packman_mirrors[self.packman_combo.get_active()]
        packman_proto = self.packman_protocols[self.packman_proto_combo.get_active()]
        return {
            "opensuse_mirror": f"{opensuse_proto}://{opensuse_mirror.url}",
            "packman_mirror": f"{packman_proto}://{packman_mirror.url}",
        }