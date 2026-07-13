"""Locale manager widget (GTK4)."""

import gi

gi.require_version("Gtk", "4.0")

from gi.repository import Gtk

from yast3.core.i18n import _
from yast3.core.languages import LocaleItem, get_locales_with_status, build_locale_install_command, build_locale_remove_command, refresh_locale_cache
from yast3.gtk4.command.action import CommandAction


class LocaleManager(Gtk.Box):
    def __init__(self):
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        self.set_margin_top(8)
        self.set_margin_bottom(8)
        self.set_margin_start(8)
        self.set_margin_end(8)
        self._all_locales: list[LocaleItem] = []
        self._setup_ui()

    def _setup_ui(self) -> None:
        search_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)

        search_label = Gtk.Label(label=_("Search:"))
        search_box.append(search_label)

        self.search_entry = Gtk.Entry()
        self.search_entry.set_placeholder_text(_("Search by code or name..."))
        self.search_entry.connect("changed", self._on_search_changed)
        search_box.append(self.search_entry)

        self.append(search_box)

        button_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)

        self.install_btn = Gtk.Button(label=_("Install"))
        self.install_btn.connect("clicked", self._on_install_clicked)
        self.install_btn.set_sensitive(False)
        button_box.append(self.install_btn)

        self.uninstall_btn = Gtk.Button(label=_("Uninstall"))
        self.uninstall_btn.connect("clicked", self._on_uninstall_clicked)
        self.uninstall_btn.set_sensitive(False)
        button_box.append(self.uninstall_btn)

        button_box.append(Gtk.Box())
        button_box.set_hexpand(True)

        self.refresh_btn = Gtk.Button(label=_("Refresh"))
        self.refresh_btn.connect("clicked", self._on_refresh_clicked)
        button_box.append(self.refresh_btn)

        self.append(button_box)

        self._create_list_view()

    def _create_list_view(self) -> None:
        self.list_store = Gtk.ListStore(str, str, str, bool)

        self.tree_view = Gtk.TreeView(model=self.list_store)
        self.tree_view.set_hexpand(True)
        self.tree_view.set_vexpand(True)

        code_renderer = Gtk.CellRendererText()
        code_column = Gtk.TreeViewColumn(_("Code"), code_renderer, text=0)
        code_column.set_resizable(True)
        self.tree_view.append_column(code_column)

        name_renderer = Gtk.CellRendererText()
        name_column = Gtk.TreeViewColumn(_("Name"), name_renderer, text=1)
        name_column.set_resizable(True)
        name_column.set_expand(True)
        self.tree_view.append_column(name_column)

        status_renderer = Gtk.CellRendererText()
        status_column = Gtk.TreeViewColumn(_("Status"), status_renderer, text=2)
        status_column.set_resizable(True)
        status_renderer.set_property("cell-background", "white")
        status_column.set_cell_data_func(status_renderer, self._status_cell_data_func)
        self.tree_view.append_column(status_column)

        self.selection = self.tree_view.get_selection()
        self.selection.set_mode(Gtk.SelectionMode.SINGLE)
        self.selection.connect("changed", self._on_selection_changed)

        scrolled = Gtk.ScrolledWindow()
        scrolled.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        scrolled.set_child(self.tree_view)
        self.append(scrolled)

        self._refresh_locales()

    def _on_selection_changed(self, selection) -> None:
        model, tree_iter = selection.get_selected()
        if tree_iter is not None:
            status = model.get_value(tree_iter, 2)
            is_installed = status == _("Installed")
            self.install_btn.set_sensitive(not is_installed)
            self.uninstall_btn.set_sensitive(is_installed)
        else:
            self.install_btn.set_sensitive(False)
            self.uninstall_btn.set_sensitive(False)

    def _on_search_changed(self, entry: Gtk.Entry) -> None:
        search_text = entry.get_text()
        self._filter_locales(search_text)

    def _status_cell_data_func(self, column, cell, model, tree_iter, data) -> None:
        is_installed = model.get_value(tree_iter, 3)
        if is_installed:
            cell.set_property("foreground", "#008000")
        else:
            cell.set_property("foreground", "#000000")

    def _filter_locales(self, search_text: str) -> None:
        search_text = search_text.lower().strip()

        if not search_text:
            filtered = self._all_locales
        else:
            filtered = [
                loc for loc in self._all_locales
                if search_text in loc.code.lower() or search_text in loc.name.lower()
            ]

        self.list_store.clear()
        for loc in filtered:
            status_text = _("Installed") if loc.installed else _("Not Installed")
            self.list_store.append([loc.code, loc.name, status_text, loc.installed])
        self.tree_view.columns_autosize()

    def _refresh_locales(self) -> None:
        try:
            self._all_locales = get_locales_with_status()
            search_text = self.search_entry.get_text()
            self._filter_locales(search_text)
        except Exception as e:
            self._show_message_dialog(Gtk.MessageType.WARNING, _("Error"), _("Failed to load locales: {0}").format(str(e)))

    def _on_refresh_clicked(self, button: Gtk.Button) -> None:
        self._refresh_locales()

    def _reload_after_action(self, success: bool, _error: str, _stdout: str) -> None:
        if success:
            refresh_locale_cache()
            self._refresh_locales()

    def _get_parent_window(self) -> Gtk.Window | None:
        widget = self.get_parent()
        while widget is not None:
            if isinstance(widget, Gtk.Window):
                return widget
            widget = widget.get_parent()
        return None

    def _on_install_clicked(self, button: Gtk.Button) -> None:
        model, tree_iter = self.selection.get_selected()
        if tree_iter is None:
            self._show_message_dialog(Gtk.MessageType.INFO, _("Information"), _("Please select a locale to install."))
            return

        locale_code = model.get_value(tree_iter, 0)
        locale_name = model.get_value(tree_iter, 1)

        confirm_dialog = Gtk.MessageDialog(
            transient_for=self.get_root(),
            modal=True,
            message_type=Gtk.MessageType.QUESTION,
            buttons=Gtk.ButtonsType.YES_NO,
            text=_("Confirm"),
        )
        confirm_dialog.set_property("secondary-text", _("Are you sure you want to install locale '{0}' ({1})?").format(locale_name, locale_code))
        confirm_dialog.connect("response", self._on_install_confirm_response, locale_code, locale_name)
        confirm_dialog.present()

    def _on_install_confirm_response(self, dialog, response_id, locale_code: str, locale_name: str) -> None:
        if response_id == Gtk.ResponseType.YES:
            self.current_action = CommandAction(
                text=_("Install"),
                running_text=_("Installing..."),
                dialog_title=_("Install Locale"),
                command=build_locale_install_command(locale_code),
                success_output=_("Locale '{0}' installed successfully.").format(locale_name),
                parent_window=self._get_parent_window(),
            )
            self.current_action.connect_finished(self._reload_after_action)
            self.current_action.start_action()
        dialog.destroy()

    def _on_uninstall_clicked(self, button: Gtk.Button) -> None:
        model, tree_iter = self.selection.get_selected()
        if tree_iter is None:
            self._show_message_dialog(Gtk.MessageType.INFO, _("Information"), _("Please select a locale to uninstall."))
            return

        locale_code = model.get_value(tree_iter, 0)
        locale_name = model.get_value(tree_iter, 1)

        confirm_dialog = Gtk.MessageDialog(
            transient_for=self.get_root(),
            modal=True,
            message_type=Gtk.MessageType.QUESTION,
            buttons=Gtk.ButtonsType.YES_NO,
            text=_("Confirm"),
        )
        confirm_dialog.set_property("secondary-text", _("Are you sure you want to uninstall locale '{0}' ({1})?").format(locale_name, locale_code))
        confirm_dialog.connect("response", self._on_uninstall_confirm_response, locale_code, locale_name)
        confirm_dialog.present()

    def _on_uninstall_confirm_response(self, dialog, response_id, locale_code: str, locale_name: str) -> None:
        if response_id == Gtk.ResponseType.YES:
            self.current_action = CommandAction(
                text=_("Uninstall"),
                running_text=_("Uninstalling..."),
                dialog_title=_("Uninstall Locale"),
                command=build_locale_remove_command(locale_code),
                success_output=_("Locale '{0}' uninstalled successfully.").format(locale_name),
                parent_window=self._get_parent_window(),
            )
            self.current_action.connect_finished(self._reload_after_action)
            self.current_action.start_action()
        dialog.destroy()

    def _show_message_dialog(self, msg_type: Gtk.MessageType, title: str, message: str) -> None:
        dialog = Gtk.MessageDialog(
            transient_for=self.get_root(),
            modal=True,
            message_type=msg_type,
            buttons=Gtk.ButtonsType.OK,
            text=title,
        )
        dialog.set_property("secondary-text", message)
        dialog.connect("response", lambda d, r: d.destroy())
        dialog.present()