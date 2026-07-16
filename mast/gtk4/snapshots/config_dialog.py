"""Configuration dialog for snapper settings (GTK4)."""

from __future__ import annotations

import gi

gi.require_version("Gtk", "4.0")
from gi.repository import Gtk

from mast.core.i18n import _
from mast.core.snapshots import SnapperConfig, read_config, write_config


class SnapperConfigDialog:
    def __init__(self, parent_window):
        self.parent_window = parent_window

    def show(self):
        dialog = Gtk.Dialog(
            title=_("Snapper Configuration"),
            transient_for=self.parent_window,
            modal=True,
        )
        dialog.set_default_size(500, 600)

        content_area = dialog.get_content_area()
        content_area.set_margin_top(12)
        content_area.set_margin_bottom(12)
        content_area.set_margin_start(12)
        content_area.set_margin_end(12)
        content_area.set_spacing(8)

        scrolled = Gtk.ScrolledWindow()
        scrolled.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        scrolled.set_hexpand(True)
        scrolled.set_vexpand(True)

        form_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)

        try:
            config = read_config()
        except Exception as e:
            self._show_message_dialog(
                self.parent_window,
                Gtk.MessageType.ERROR,
                _("Error"),
                _("Failed to read config: {0}").format(str(e)),
            )
            return

        fields = {}

        space_limit_label = Gtk.Label(label=_("Space Limit (fraction or absolute size)"))
        space_limit_label.set_halign(Gtk.Align.START)
        space_limit_edit = Gtk.Entry()
        space_limit_edit.set_text(config.SPACE_LIMIT)
        fields["space_limit"] = space_limit_edit
        form_box.append(space_limit_label)
        form_box.append(space_limit_edit)

        free_limit_label = Gtk.Label(label=_("Free Limit (fraction or absolute size)"))
        free_limit_label.set_halign(Gtk.Align.START)
        free_limit_edit = Gtk.Entry()
        free_limit_edit.set_text(config.FREE_LIMIT)
        fields["free_limit"] = free_limit_edit
        form_box.append(free_limit_label)
        form_box.append(free_limit_edit)

        allow_users_label = Gtk.Label(label=_("Allow Users"))
        allow_users_label.set_halign(Gtk.Align.START)
        allow_users_edit = Gtk.Entry()
        allow_users_edit.set_text(config.ALLOW_USERS)
        fields["allow_users"] = allow_users_edit
        form_box.append(allow_users_label)
        form_box.append(allow_users_edit)

        allow_groups_label = Gtk.Label(label=_("Allow Groups"))
        allow_groups_label.set_halign(Gtk.Align.START)
        allow_groups_edit = Gtk.Entry()
        allow_groups_edit.set_text(config.ALLOW_GROUPS)
        fields["allow_groups"] = allow_groups_edit
        form_box.append(allow_groups_label)
        form_box.append(allow_groups_edit)

        sync_acl_check = Gtk.CheckButton(label=_("Sync ACL"))
        sync_acl_check.set_active(config.SYNC_ACL.lower() == "yes")
        fields["sync_acl"] = sync_acl_check
        form_box.append(sync_acl_check)

        bg_compare_check = Gtk.CheckButton(label=_("Background Comparison"))
        bg_compare_check.set_active(config.BACKGROUND_COMPARISON.lower() == "yes")
        fields["background_comparison"] = bg_compare_check
        form_box.append(bg_compare_check)

        number_cleanup_check = Gtk.CheckButton(label=_("Number Cleanup"))
        number_cleanup_check.set_active(config.NUMBER_CLEANUP.lower() == "yes")
        fields["number_cleanup"] = number_cleanup_check
        form_box.append(number_cleanup_check)

        number_min_age_label = Gtk.Label(label=_("Number Min Age (seconds)"))
        number_min_age_label.set_halign(Gtk.Align.START)
        number_min_age_edit = Gtk.Entry()
        number_min_age_edit.set_text(config.NUMBER_MIN_AGE)
        fields["number_min_age"] = number_min_age_edit
        form_box.append(number_min_age_label)
        form_box.append(number_min_age_edit)

        number_limit_label = Gtk.Label(label=_("Number Limit"))
        number_limit_label.set_halign(Gtk.Align.START)
        number_limit_edit = Gtk.Entry()
        number_limit_edit.set_text(config.NUMBER_LIMIT)
        fields["number_limit"] = number_limit_edit
        form_box.append(number_limit_label)
        form_box.append(number_limit_edit)

        number_limit_important_label = Gtk.Label(label=_("Number Limit Important"))
        number_limit_important_label.set_halign(Gtk.Align.START)
        number_limit_important_edit = Gtk.Entry()
        number_limit_important_edit.set_text(config.NUMBER_LIMIT_IMPORTANT)
        fields["number_limit_important"] = number_limit_important_edit
        form_box.append(number_limit_important_label)
        form_box.append(number_limit_important_edit)

        timeline_create_check = Gtk.CheckButton(label=_("Timeline Create"))
        timeline_create_check.set_active(config.TIMELINE_CREATE.lower() == "yes")
        fields["timeline_create"] = timeline_create_check
        form_box.append(timeline_create_check)

        timeline_cleanup_check = Gtk.CheckButton(label=_("Timeline Cleanup"))
        timeline_cleanup_check.set_active(config.TIMELINE_CLEANUP.lower() == "yes")
        fields["timeline_cleanup"] = timeline_cleanup_check
        form_box.append(timeline_cleanup_check)

        timeline_min_age_label = Gtk.Label(label=_("Timeline Min Age (seconds)"))
        timeline_min_age_label.set_halign(Gtk.Align.START)
        timeline_min_age_edit = Gtk.Entry()
        timeline_min_age_edit.set_text(config.TIMELINE_MIN_AGE)
        fields["timeline_min_age"] = timeline_min_age_edit
        form_box.append(timeline_min_age_label)
        form_box.append(timeline_min_age_edit)

        timeline_hourly_label = Gtk.Label(label=_("Timeline Limit Hourly"))
        timeline_hourly_label.set_halign(Gtk.Align.START)
        timeline_hourly_edit = Gtk.Entry()
        timeline_hourly_edit.set_text(config.TIMELINE_LIMIT_HOURLY)
        fields["timeline_limit_hourly"] = timeline_hourly_edit
        form_box.append(timeline_hourly_label)
        form_box.append(timeline_hourly_edit)

        timeline_daily_label = Gtk.Label(label=_("Timeline Limit Daily"))
        timeline_daily_label.set_halign(Gtk.Align.START)
        timeline_daily_edit = Gtk.Entry()
        timeline_daily_edit.set_text(config.TIMELINE_LIMIT_DAILY)
        fields["timeline_limit_daily"] = timeline_daily_edit
        form_box.append(timeline_daily_label)
        form_box.append(timeline_daily_edit)

        timeline_weekly_label = Gtk.Label(label=_("Timeline Limit Weekly"))
        timeline_weekly_label.set_halign(Gtk.Align.START)
        timeline_weekly_edit = Gtk.Entry()
        timeline_weekly_edit.set_text(config.TIMELINE_LIMIT_WEEKLY)
        fields["timeline_limit_weekly"] = timeline_weekly_edit
        form_box.append(timeline_weekly_label)
        form_box.append(timeline_weekly_edit)

        timeline_monthly_label = Gtk.Label(label=_("Timeline Limit Monthly"))
        timeline_monthly_label.set_halign(Gtk.Align.START)
        timeline_monthly_edit = Gtk.Entry()
        timeline_monthly_edit.set_text(config.TIMELINE_LIMIT_MONTHLY)
        fields["timeline_limit_monthly"] = timeline_monthly_edit
        form_box.append(timeline_monthly_label)
        form_box.append(timeline_monthly_edit)

        timeline_yearly_label = Gtk.Label(label=_("Timeline Limit Yearly"))
        timeline_yearly_label.set_halign(Gtk.Align.START)
        timeline_yearly_edit = Gtk.Entry()
        timeline_yearly_edit.set_text(config.TIMELINE_LIMIT_YEARLY)
        fields["timeline_limit_yearly"] = timeline_yearly_edit
        form_box.append(timeline_yearly_label)
        form_box.append(timeline_yearly_edit)

        scrolled.set_child(form_box)
        content_area.append(scrolled)

        dialog.add_button(_("Cancel"), Gtk.ResponseType.CANCEL)
        dialog.add_button(_("OK"), Gtk.ResponseType.OK)

        dialog.show()

        response = dialog.run()
        dialog.destroy()

        if response == Gtk.ResponseType.OK:
            new_config = SnapperConfig()

            new_config.SPACE_LIMIT = fields["space_limit"].get_text().strip()
            new_config.FREE_LIMIT = fields["free_limit"].get_text().strip()
            new_config.ALLOW_USERS = fields["allow_users"].get_text().strip()
            new_config.ALLOW_GROUPS = fields["allow_groups"].get_text().strip()
            new_config.SYNC_ACL = "yes" if fields["sync_acl"].get_active() else "no"
            new_config.BACKGROUND_COMPARISON = "yes" if fields["background_comparison"].get_active() else "no"
            new_config.NUMBER_CLEANUP = "yes" if fields["number_cleanup"].get_active() else "no"
            new_config.NUMBER_MIN_AGE = fields["number_min_age"].get_text().strip()
            new_config.NUMBER_LIMIT = fields["number_limit"].get_text().strip()
            new_config.NUMBER_LIMIT_IMPORTANT = fields["number_limit_important"].get_text().strip()
            new_config.TIMELINE_CREATE = "yes" if fields["timeline_create"].get_active() else "no"
            new_config.TIMELINE_CLEANUP = "yes" if fields["timeline_cleanup"].get_active() else "no"
            new_config.TIMELINE_MIN_AGE = fields["timeline_min_age"].get_text().strip()
            new_config.TIMELINE_LIMIT_HOURLY = fields["timeline_limit_hourly"].get_text().strip()
            new_config.TIMELINE_LIMIT_DAILY = fields["timeline_limit_daily"].get_text().strip()
            new_config.TIMELINE_LIMIT_WEEKLY = fields["timeline_limit_weekly"].get_text().strip()
            new_config.TIMELINE_LIMIT_MONTHLY = fields["timeline_limit_monthly"].get_text().strip()
            new_config.TIMELINE_LIMIT_YEARLY = fields["timeline_limit_yearly"].get_text().strip()

            try:
                write_config(new_config)
                self._show_message_dialog(
                    self.parent_window,
                    Gtk.MessageType.INFO,
                    _("Success"),
                    _("Configuration saved successfully."),
                )
            except Exception as e:
                self._show_message_dialog(
                    self.parent_window,
                    Gtk.MessageType.ERROR,
                    _("Error"),
                    _("Failed to write config: {0}").format(str(e)),
                )

    def _show_message_dialog(self, parent, message_type, title, message):
        dialog = Gtk.MessageDialog(
            transient_for=parent,
            modal=True,
            message_type=message_type,
            buttons=Gtk.ButtonsType.OK,
            text=title,
        )
        dialog.format_secondary_text(message)
        dialog.run()
        dialog.destroy()