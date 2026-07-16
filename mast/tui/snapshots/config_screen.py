"""Configuration screen for snapper settings (TUI)."""

from __future__ import annotations

from textual.app import ComposeResult
from textual.containers import Vertical, Horizontal
from textual.screen import ModalScreen
from textual.widgets import Button, Input, Checkbox, Label

from mast.core.i18n import _
from mast.core.snapshots import SnapperConfig, read_config, write_config


class SnapperConfigScreen(ModalScreen[bool]):
    def __init__(self, on_config_result):
        super().__init__()
        self.on_config_result = on_config_result
        self.fields: dict[str, Input | Checkbox] = {}

    def compose(self) -> ComposeResult:
        with Vertical():
            yield Label(_("Snapper Configuration"), classes="title")

            yield Label(_("Space Limit"))
            space_limit = Input(value="", id="space_limit")
            self.fields["space_limit"] = space_limit
            yield space_limit

            yield Label(_("Free Limit"))
            free_limit = Input(value="", id="free_limit")
            self.fields["free_limit"] = free_limit
            yield free_limit

            yield Label(_("Allow Users"))
            allow_users = Input(value="", id="allow_users")
            self.fields["allow_users"] = allow_users
            yield allow_users

            yield Label(_("Allow Groups"))
            allow_groups = Input(value="", id="allow_groups")
            self.fields["allow_groups"] = allow_groups
            yield allow_groups

            sync_acl = Checkbox(_("Sync ACL"), checked=False, id="sync_acl")
            self.fields["sync_acl"] = sync_acl
            yield sync_acl

            bg_compare = Checkbox(_("Background Comparison"), checked=False, id="background_comparison")
            self.fields["background_comparison"] = bg_compare
            yield bg_compare

            number_cleanup = Checkbox(_("Number Cleanup"), checked=False, id="number_cleanup")
            self.fields["number_cleanup"] = number_cleanup
            yield number_cleanup

            yield Label(_("Number Min Age"))
            number_min_age = Input(value="", id="number_min_age")
            self.fields["number_min_age"] = number_min_age
            yield number_min_age

            yield Label(_("Number Limit"))
            number_limit = Input(value="", id="number_limit")
            self.fields["number_limit"] = number_limit
            yield number_limit

            yield Label(_("Number Limit Important"))
            number_limit_important = Input(value="", id="number_limit_important")
            self.fields["number_limit_important"] = number_limit_important
            yield number_limit_important

            timeline_create = Checkbox(_("Timeline Create"), checked=False, id="timeline_create")
            self.fields["timeline_create"] = timeline_create
            yield timeline_create

            timeline_cleanup = Checkbox(_("Timeline Cleanup"), checked=False, id="timeline_cleanup")
            self.fields["timeline_cleanup"] = timeline_cleanup
            yield timeline_cleanup

            yield Label(_("Timeline Min Age"))
            timeline_min_age = Input(value="", id="timeline_min_age")
            self.fields["timeline_min_age"] = timeline_min_age
            yield timeline_min_age

            yield Label(_("Timeline Hourly"))
            timeline_hourly = Input(value="", id="timeline_limit_hourly")
            self.fields["timeline_limit_hourly"] = timeline_hourly
            yield timeline_hourly

            yield Label(_("Timeline Daily"))
            timeline_daily = Input(value="", id="timeline_limit_daily")
            self.fields["timeline_limit_daily"] = timeline_daily
            yield timeline_daily

            yield Label(_("Timeline Weekly"))
            timeline_weekly = Input(value="", id="timeline_limit_weekly")
            self.fields["timeline_limit_weekly"] = timeline_weekly
            yield timeline_weekly

            yield Label(_("Timeline Monthly"))
            timeline_monthly = Input(value="", id="timeline_limit_monthly")
            self.fields["timeline_limit_monthly"] = timeline_monthly
            yield timeline_monthly

            yield Label(_("Timeline Yearly"))
            timeline_yearly = Input(value="", id="timeline_limit_yearly")
            self.fields["timeline_limit_yearly"] = timeline_yearly
            yield timeline_yearly

            with Horizontal():
                yield Button(_("Cancel"), id="cancel-btn")
                yield Button(_("OK"), id="ok-btn")

    def on_mount(self) -> None:
        try:
            config = read_config()
            self.fields["space_limit"].value = config.SPACE_LIMIT
            self.fields["free_limit"].value = config.FREE_LIMIT
            self.fields["allow_users"].value = config.ALLOW_USERS
            self.fields["allow_groups"].value = config.ALLOW_GROUPS
            self.fields["sync_acl"].checked = config.SYNC_ACL.lower() == "yes"
            self.fields["background_comparison"].checked = config.BACKGROUND_COMPARISON.lower() == "yes"
            self.fields["number_cleanup"].checked = config.NUMBER_CLEANUP.lower() == "yes"
            self.fields["number_min_age"].value = config.NUMBER_MIN_AGE
            self.fields["number_limit"].value = config.NUMBER_LIMIT
            self.fields["number_limit_important"].value = config.NUMBER_LIMIT_IMPORTANT
            self.fields["timeline_create"].checked = config.TIMELINE_CREATE.lower() == "yes"
            self.fields["timeline_cleanup"].checked = config.TIMELINE_CLEANUP.lower() == "yes"
            self.fields["timeline_min_age"].value = config.TIMELINE_MIN_AGE
            self.fields["timeline_limit_hourly"].value = config.TIMELINE_LIMIT_HOURLY
            self.fields["timeline_limit_daily"].value = config.TIMELINE_LIMIT_DAILY
            self.fields["timeline_limit_weekly"].value = config.TIMELINE_LIMIT_WEEKLY
            self.fields["timeline_limit_monthly"].value = config.TIMELINE_LIMIT_MONTHLY
            self.fields["timeline_limit_yearly"].value = config.TIMELINE_LIMIT_YEARLY
        except Exception as e:
            self.app.notify(_("Error: Failed to read config: {0}").format(str(e)))
            self.dismiss(False)

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "ok-btn":
            new_config = SnapperConfig()
            new_config.SPACE_LIMIT = self.fields["space_limit"].value.strip()
            new_config.FREE_LIMIT = self.fields["free_limit"].value.strip()
            new_config.ALLOW_USERS = self.fields["allow_users"].value.strip()
            new_config.ALLOW_GROUPS = self.fields["allow_groups"].value.strip()
            new_config.SYNC_ACL = "yes" if self.fields["sync_acl"].checked else "no"
            new_config.BACKGROUND_COMPARISON = "yes" if self.fields["background_comparison"].checked else "no"
            new_config.NUMBER_CLEANUP = "yes" if self.fields["number_cleanup"].checked else "no"
            new_config.NUMBER_MIN_AGE = self.fields["number_min_age"].value.strip()
            new_config.NUMBER_LIMIT = self.fields["number_limit"].value.strip()
            new_config.NUMBER_LIMIT_IMPORTANT = self.fields["number_limit_important"].value.strip()
            new_config.TIMELINE_CREATE = "yes" if self.fields["timeline_create"].checked else "no"
            new_config.TIMELINE_CLEANUP = "yes" if self.fields["timeline_cleanup"].checked else "no"
            new_config.TIMELINE_MIN_AGE = self.fields["timeline_min_age"].value.strip()
            new_config.TIMELINE_LIMIT_HOURLY = self.fields["timeline_limit_hourly"].value.strip()
            new_config.TIMELINE_LIMIT_DAILY = self.fields["timeline_limit_daily"].value.strip()
            new_config.TIMELINE_LIMIT_WEEKLY = self.fields["timeline_limit_weekly"].value.strip()
            new_config.TIMELINE_LIMIT_MONTHLY = self.fields["timeline_limit_monthly"].value.strip()
            new_config.TIMELINE_LIMIT_YEARLY = self.fields["timeline_limit_yearly"].value.strip()

            try:
                write_config(new_config)
                self.dismiss(True)
            except Exception as e:
                self.app.notify(_("Error: Failed to write config: {0}").format(str(e)))
                self.dismiss(False)
        else:
            self.dismiss(False)

    def on_dismissed(self) -> None:
        if self.on_config_result is not None:
            self.on_config_result(self.return_value)