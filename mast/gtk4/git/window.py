"""UI components for the Git module (GTK4)."""

import gi

gi.require_version("Gtk", "4.0")

from gi.repository import Gtk

from mast.core.i18n import _
from mast.core.git import (
    get_git_config,
    is_git_installed,
    set_git_config,
)


class GitWindow(Gtk.ApplicationWindow):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.config = None

        self.set_default_size(600, 500)

        # Main container
        self.main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
        self.main_box.set_margin_top(12)
        self.main_box.set_margin_bottom(12)
        self.main_box.set_margin_start(12)
        self.main_box.set_margin_end(12)

        if not is_git_installed():
            label = Gtk.Label(label=_("Git is not installed on this system."))
            self.main_box.append(label)
            self.set_child(self.main_box)
            self.present()
            return

        self.config = get_git_config()

        # Notebook for tabs
        self.notebook = Gtk.Notebook()

        # User tab
        self.user_tab = self._create_user_tab()
        self.notebook.append_page(self.user_tab, Gtk.Label(label=_("User")))

        # Core tab
        self.core_tab = self._create_core_tab()
        self.notebook.append_page(self.core_tab, Gtk.Label(label=_("Core")))

        # Commit tab
        self.commit_tab = self._create_commit_tab()
        self.notebook.append_page(self.commit_tab, Gtk.Label(label=_("Commit")))

        # Merge tab
        self.merge_tab = self._create_merge_tab()
        self.notebook.append_page(self.merge_tab, Gtk.Label(label=_("Merge")))

        # Other tab
        self.other_tab = self._create_other_tab()
        self.notebook.append_page(self.other_tab, Gtk.Label(label=_("Other")))

        self.main_box.append(self.notebook)

        # Button box
        button_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=12)
        button_box.set_halign(Gtk.Align.END)

        self.save_btn = Gtk.Button(label=_("Save"))
        self.save_btn.add_css_class("suggested-action")
        self.save_btn.connect("clicked", self._on_save_clicked)
        button_box.append(self.save_btn)

        self.reset_btn = Gtk.Button(label=_("Reset"))
        self.reset_btn.connect("clicked", self._on_reset_clicked)
        button_box.append(self.reset_btn)

        self.main_box.append(button_box)

        self.set_child(self.main_box)
        self.present()

    def _create_user_tab(self) -> Gtk.Box:
        """Create User settings tab."""
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
        box.set_margin_top(12)
        box.set_margin_bottom(12)
        box.set_margin_start(12)
        box.set_margin_end(12)

        # User Name
        self.name_entry = self._create_entry_row(box, _("User Name"), self.config.user_name, _("Enter your Git user name"))

        # User Email
        self.email_entry = self._create_entry_row(box, _("Email Address"), self.config.user_email, _("Enter your Git email address"))

        # Signing Key
        self.signingkey_entry = self._create_entry_row(box, _("GPG Signing Key"), self.config.user_signingkey, _("Enter GPG key ID"))

        return box

    def _create_core_tab(self) -> Gtk.Box:
        """Create Core settings tab."""
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
        box.set_margin_top(12)
        box.set_margin_bottom(12)
        box.set_margin_start(12)
        box.set_margin_end(12)

        # Editor
        self.editor_entry = self._create_entry_row(box, _("Default Editor"), self.config.core_editor, _("e.g., vim, nano, code"))

        # Auto CRLF
        self.autocrlf_combo = self._create_combo_row(box, _("Auto CRLF"), ["", "true", "false", "input"], self.config.core_autocrlf)

        # Safe CRLF
        self.safecrlf_combo = self._create_combo_row(box, _("Safe CRLF"), ["", "true", "false", "warn"], self.config.core_safecrlf)

        return box

    def _create_commit_tab(self) -> Gtk.Box:
        """Create Commit settings tab."""
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
        box.set_margin_top(12)
        box.set_margin_bottom(12)
        box.set_margin_start(12)
        box.set_margin_end(12)

        # Commit Template
        template_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=12)
        label = Gtk.Label(label=_("Commit Template"))
        label.set_size_request(150, -1)
        label.set_halign(Gtk.Align.START)
        template_box.append(label)

        self.template_entry = Gtk.Entry()
        self.template_entry.set_placeholder_text(_("Path to commit template"))
        self.template_entry.set_text(self.config.commit_template or "")
        self.template_entry.set_hexpand(True)
        template_box.append(self.template_entry)

        self.template_btn = Gtk.Button(label=_("Browse"))
        self.template_btn.connect("clicked", self._on_browse_template)
        template_box.append(self.template_btn)

        box.append(template_box)

        # GPG Sign
        self.gpgsign_check = Gtk.CheckButton(label=_("Sign commits with GPG"))
        self.gpgsign_check.set_active(self.config.commit_gpgsign)
        box.append(self.gpgsign_check)

        return box

    def _create_merge_tab(self) -> Gtk.Box:
        """Create Merge settings tab."""
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
        box.set_margin_top(12)
        box.set_margin_bottom(12)
        box.set_margin_start(12)
        box.set_margin_end(12)

        # Conflict Style
        self.conflictstyle_combo = self._create_combo_row(box, _("Conflict Style"), ["", "merge", "diff3"], self.config.merge_conflictstyle)

        # Pull Rebase
        self.rebase_combo = self._create_combo_row(box, _("Pull Rebase"), ["", "true", "false", "interactive", "preserve"], self.config.pull_rebase)

        return box

    def _create_other_tab(self) -> Gtk.Box:
        """Create Other settings tab."""
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
        box.set_margin_top(12)
        box.set_margin_bottom(12)
        box.set_margin_start(12)
        box.set_margin_end(12)

        # Color UI
        self.color_ui_check = Gtk.CheckButton(label=_("Enable color output"))
        self.color_ui_check.set_active(self.config.color_ui)
        box.append(self.color_ui_check)

        # Default Branch
        self.defaultbranch_entry = self._create_entry_row(box, _("Default Branch Name"), self.config.init_defaultbranch, _("e.g., main, master"))

        # Credential Helper
        self.credential_combo = self._create_combo_row(box, _("Credential Helper"), ["", "cache", "store", "gnome-keyring", "kwallet"], self.config.credential_helper)

        return box

    def _create_entry_row(self, parent: Gtk.Box, label_text: str, value: str, placeholder: str) -> Gtk.Entry:
        """Create a labeled entry row."""
        box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=12)

        label = Gtk.Label(label=label_text)
        label.set_size_request(150, -1)
        label.set_halign(Gtk.Align.START)
        box.append(label)

        entry = Gtk.Entry()
        entry.set_placeholder_text(placeholder)
        entry.set_text(value or "")
        entry.set_hexpand(True)
        box.append(entry)

        parent.append(box)
        return entry

    def _create_combo_row(self, parent: Gtk.Box, label_text: str, items: list, current_value: str) -> Gtk.ComboBoxText:
        """Create a labeled combo box row."""
        box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=12)

        label = Gtk.Label(label=label_text)
        label.set_size_request(150, -1)
        label.set_halign(Gtk.Align.START)
        box.append(label)

        combo = Gtk.ComboBoxText()
        for item in items:
            combo.append_text(item)
        if current_value and current_value in items:
            combo.set_active(items.index(current_value))
        else:
            combo.set_active(0)
        box.append(combo)

        parent.append(box)
        return combo

    def _on_browse_template(self, button: Gtk.Button) -> None:
        """Browse for commit template file."""
        dialog = Gtk.FileDialog()
        dialog.set_title(_("Select Commit Template"))

        def on_open_callback(dialog, result):
            try:
                file = dialog.open_finish(result)
                if file:
                    self.template_entry.set_text(file.get_path())
            except Exception:
                pass

        dialog.open(self, None, on_open_callback)

    def _on_save_clicked(self, button: Gtk.Button) -> None:
        """Save the configuration."""
        if not self.config:
            return

        user_name = self.name_entry.get_text().strip()
        user_email = self.email_entry.get_text().strip()

        if not user_name or not user_email:
            self._show_message_dialog(Gtk.MessageType.WARNING, _("Error"), _("User name and email are required."))
            return

        # Update config object
        self.config.user_name = user_name
        self.config.user_email = user_email
        self.config.user_signingkey = self.signingkey_entry.get_text().strip()
        self.config.core_editor = self.editor_entry.get_text().strip()
        self.config.core_autocrlf = self.autocrlf_combo.get_active_text() or ""
        self.config.core_safecrlf = self.safecrlf_combo.get_active_text() or ""
        self.config.commit_template = self.template_entry.get_text().strip()
        self.config.commit_gpgsign = self.gpgsign_check.get_active()
        self.config.merge_conflictstyle = self.conflictstyle_combo.get_active_text() or ""
        self.config.pull_rebase = self.rebase_combo.get_active_text() or ""
        self.config.color_ui = self.color_ui_check.get_active()
        self.config.init_defaultbranch = self.defaultbranch_entry.get_text().strip()
        self.config.credential_helper = self.credential_combo.get_active_text() or ""

        if set_git_config(self.config):
            self._show_message_dialog(Gtk.MessageType.INFO, _("Success"), _("Git configuration saved successfully."))
        else:
            self._show_message_dialog(Gtk.MessageType.ERROR, _("Error"), _("Failed to save Git configuration."))

    def _on_reset_clicked(self, button: Gtk.Button) -> None:
        """Reset all fields to original values."""
        if not self.config:
            return

        # User tab
        self.name_entry.set_text(self.config.user_name or "")
        self.email_entry.set_text(self.config.user_email or "")
        self.signingkey_entry.set_text(self.config.user_signingkey or "")

        # Core tab
        self.editor_entry.set_text(self.config.core_editor or "")
        self._set_combo_active_text(self.autocrlf_combo, self.config.core_autocrlf)
        self._set_combo_active_text(self.safecrlf_combo, self.config.core_safecrlf)

        # Commit tab
        self.template_entry.set_text(self.config.commit_template or "")
        self.gpgsign_check.set_active(self.config.commit_gpgsign)

        # Merge tab
        self._set_combo_active_text(self.conflictstyle_combo, self.config.merge_conflictstyle)
        self._set_combo_active_text(self.rebase_combo, self.config.pull_rebase)

        # Other tab
        self.color_ui_check.set_active(self.config.color_ui)
        self.defaultbranch_entry.set_text(self.config.init_defaultbranch or "")
        self._set_combo_active_text(self.credential_combo, self.config.credential_helper)

    def _set_combo_active_text(self, combo: Gtk.ComboBoxText, value: str) -> None:
        """Set combo box active item by text value."""
        model = combo.get_model()
        for i, row in enumerate(model):
            if row[0] == value:
                combo.set_active(i)
                return
        combo.set_active(0)

    def _show_message_dialog(self, msg_type: Gtk.MessageType, title: str, message: str) -> None:
        """Show a message dialog."""
        dialog = Gtk.MessageDialog(
            transient_for=self,
            modal=True,
            message_type=msg_type,
            buttons=Gtk.ButtonsType.OK,
            text=title,
        )
        dialog.set_property("secondary-text", message)
        dialog.connect("response", lambda d, r: d.destroy())
        dialog.present()