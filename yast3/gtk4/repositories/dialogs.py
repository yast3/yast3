"""Dialog components for the Repositories module (GTK4)."""

import gi

gi.require_version("Gtk", "4.0")

from gi.repository import Gtk

from yast3.core.i18n import _
from yast3.core.repositories import RepoEntry


class RepoEditDialog(Gtk.Dialog):
    """Dialog for adding or editing a repository entry."""

    def __init__(self, parent, entry: RepoEntry | None = None):
        super().__init__(
            title=_("Add Repository") if entry is None else _("Edit Repository"),
            transient_for=parent,
            modal=True,
        )
        self.entry = entry

        self.set_default_size(500, -1)

        # Add buttons
        self.add_button(_("Cancel"), Gtk.ResponseType.CANCEL)
        self.add_button(_("OK"), Gtk.ResponseType.OK)

        # Content area
        content = self.get_content_area()
        content.set_spacing(8)
        content.set_margin_top(12)
        content.set_margin_bottom(12)
        content.set_margin_start(12)
        content.set_margin_end(12)

        # Repository ID
        self.id_entry = self._create_entry_row(content, _("ID"), entry.id if entry else "")

        # Repository Name
        self.name_entry = self._create_entry_row(content, _("Name"), entry.name if entry else "")

        # Enabled
        self.enabled_check = Gtk.CheckButton(label=_("Enabled"))
        self.enabled_check.set_active(entry.enabled if entry else True)
        content.append(self.enabled_check)

        # Autorefresh
        self.autorefresh_check = Gtk.CheckButton(label=_("Auto Refresh"))
        self.autorefresh_check.set_active(entry.autorefresh if entry else True)
        content.append(self.autorefresh_check)

        # URL Type
        url_type_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=12)
        url_type_label = Gtk.Label(label=_("URL Type"))
        url_type_label.set_size_request(100, -1)
        url_type_label.set_halign(Gtk.Align.START)
        url_type_box.append(url_type_label)
        self.url_type_combo = Gtk.ComboBoxText()
        self.url_type_combo.append_text(_("Base URL"))
        self.url_type_combo.append_text(_("Mirror List"))
        self.url_type_combo.set_active(0)
        url_type_box.append(self.url_type_combo)
        content.append(url_type_box)

        # URL
        url_value = entry.baseurl if entry and entry.baseurl else (entry.mirrorlist if entry else "")
        self.url_entry = self._create_entry_row(content, _("URL"), url_value)

        # Path
        self.path_entry = self._create_entry_row(content, _("Path"), entry.path if entry else "")

        # Type
        type_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=12)
        type_label = Gtk.Label(label=_("Type"))
        type_label.set_size_request(100, -1)
        type_label.set_halign(Gtk.Align.START)
        type_box.append(type_label)
        self.type_combo = Gtk.ComboBoxText()
        for t in ["rpm-md", "rpm-dir", "plaindir", "yum", "yast2", "obsolete"]:
            self.type_combo.append_text(t)
        # Set active type
        if entry and entry.type:
            for i, t in enumerate(["rpm-md", "rpm-dir", "plaindir", "yum", "yast2", "obsolete"]):
                if t == entry.type:
                    self.type_combo.set_active(i)
                    break
        else:
            self.type_combo.set_active(0)
        type_box.append(self.type_combo)
        content.append(type_box)

        # GPG Check
        self.gpgcheck_check = Gtk.CheckButton(label=_("Check GPG signature"))
        self.gpgcheck_check.set_active(entry.gpgcheck if entry else True)
        content.append(self.gpgcheck_check)

        # GPG Key URL
        self.gpgkey_entry = self._create_entry_row(content, _("GPG Key URL"), entry.gpgkey if entry else "")

        # Priority
        priority_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=12)
        priority_label = Gtk.Label(label=_("Priority"))
        priority_label.set_size_request(100, -1)
        priority_label.set_halign(Gtk.Align.START)
        priority_box.append(priority_label)
        self.priority_spin = Gtk.SpinButton()
        self.priority_spin.set_range(1, 99)
        self.priority_spin.set_value(entry.priority if entry else 99)
        self.priority_spin.set_increments(1, 10)
        priority_box.append(self.priority_spin)
        content.append(priority_box)

        # Keep Packages
        self.keep_packages_check = Gtk.CheckButton(label=_("Keep packages"))
        self.keep_packages_check.set_active(entry.keep_packages if entry else False)
        content.append(self.keep_packages_check)

    def _create_entry_row(self, parent: Gtk.Box, label: str, value: str) -> Gtk.Entry:
        """Create a labeled entry row."""
        box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=12)

        label_widget = Gtk.Label(label=label)
        label_widget.set_size_request(100, -1)
        label_widget.set_halign(Gtk.Align.START)
        box.append(label_widget)

        entry = Gtk.Entry()
        entry.set_text(value)
        entry.set_hexpand(True)
        box.append(entry)

        parent.append(box)
        return entry

    def get_values(self) -> dict:
        """Get the dialog values."""
        url_type = self.url_type_combo.get_active()
        return {
            "id": self.id_entry.get_text().strip(),
            "name": self.name_entry.get_text().strip(),
            "enabled": self.enabled_check.get_active(),
            "autorefresh": self.autorefresh_check.get_active(),
            "baseurl": self.url_entry.get_text().strip() if url_type == 0 else "",
            "mirrorlist": self.url_entry.get_text().strip() if url_type == 1 else "",
            "path": self.path_entry.get_text().strip(),
            "type": self.type_combo.get_active_text(),
            "gpgcheck": self.gpgcheck_check.get_active(),
            "gpgkey": self.gpgkey_entry.get_text().strip(),
            "priority": int(self.priority_spin.get_value()),
            "keep_packages": self.keep_packages_check.get_active(),
        }