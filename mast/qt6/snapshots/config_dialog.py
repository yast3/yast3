"""Configuration dialog for snapper settings (Qt6)."""

from __future__ import annotations

from PySide6.QtWidgets import (
    QCheckBox,
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QVBoxLayout,
    QWidget,
)

from mast.core.i18n import _
from mast.core.snapshots import SnapperConfig, read_config, write_config


class SnapperConfigDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle(_("Snapper Configuration"))
        self.resize(500, 600)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(12)

        scroll_widget = QWidget()
        scroll_layout = QFormLayout(scroll_widget)
        scroll_layout.setSpacing(8)

        try:
            self.config = read_config()
        except Exception as e:
            QMessageBox.critical(self, _("Error"), _("Failed to read config: {0}").format(str(e)))
            self.reject()
            return

        self.fields = {}

        space_limit_label = QLabel(_("Space Limit (fraction or absolute size)"))
        space_limit_edit = QLineEdit(self.config.SPACE_LIMIT)
        self.fields["space_limit"] = space_limit_edit
        scroll_layout.addRow(space_limit_label, space_limit_edit)

        free_limit_label = QLabel(_("Free Limit (fraction or absolute size)"))
        free_limit_edit = QLineEdit(self.config.FREE_LIMIT)
        self.fields["free_limit"] = free_limit_edit
        scroll_layout.addRow(free_limit_label, free_limit_edit)

        allow_users_label = QLabel(_("Allow Users"))
        allow_users_edit = QLineEdit(self.config.ALLOW_USERS)
        self.fields["allow_users"] = allow_users_edit
        scroll_layout.addRow(allow_users_label, allow_users_edit)

        allow_groups_label = QLabel(_("Allow Groups"))
        allow_groups_edit = QLineEdit(self.config.ALLOW_GROUPS)
        self.fields["allow_groups"] = allow_groups_edit
        scroll_layout.addRow(allow_groups_label, allow_groups_edit)

        sync_acl_check = QCheckBox(_("Sync ACL"))
        sync_acl_check.setChecked(self.config.SYNC_ACL.lower() == "yes")
        self.fields["sync_acl"] = sync_acl_check
        scroll_layout.addRow(sync_acl_check)

        bg_compare_check = QCheckBox(_("Background Comparison"))
        bg_compare_check.setChecked(self.config.BACKGROUND_COMPARISON.lower() == "yes")
        self.fields["background_comparison"] = bg_compare_check
        scroll_layout.addRow(bg_compare_check)

        number_cleanup_check = QCheckBox(_("Number Cleanup"))
        number_cleanup_check.setChecked(self.config.NUMBER_CLEANUP.lower() == "yes")
        self.fields["number_cleanup"] = number_cleanup_check
        scroll_layout.addRow(number_cleanup_check)

        number_min_age_label = QLabel(_("Number Min Age (seconds)"))
        number_min_age_edit = QLineEdit(self.config.NUMBER_MIN_AGE)
        self.fields["number_min_age"] = number_min_age_edit
        scroll_layout.addRow(number_min_age_label, number_min_age_edit)

        number_limit_label = QLabel(_("Number Limit"))
        number_limit_edit = QLineEdit(self.config.NUMBER_LIMIT)
        self.fields["number_limit"] = number_limit_edit
        scroll_layout.addRow(number_limit_label, number_limit_edit)

        number_limit_important_label = QLabel(_("Number Limit Important"))
        number_limit_important_edit = QLineEdit(self.config.NUMBER_LIMIT_IMPORTANT)
        self.fields["number_limit_important"] = number_limit_important_edit
        scroll_layout.addRow(number_limit_important_label, number_limit_important_edit)

        timeline_create_check = QCheckBox(_("Timeline Create"))
        timeline_create_check.setChecked(self.config.TIMELINE_CREATE.lower() == "yes")
        self.fields["timeline_create"] = timeline_create_check
        scroll_layout.addRow(timeline_create_check)

        timeline_cleanup_check = QCheckBox(_("Timeline Cleanup"))
        timeline_cleanup_check.setChecked(self.config.TIMELINE_CLEANUP.lower() == "yes")
        self.fields["timeline_cleanup"] = timeline_cleanup_check
        scroll_layout.addRow(timeline_cleanup_check)

        timeline_min_age_label = QLabel(_("Timeline Min Age (seconds)"))
        timeline_min_age_edit = QLineEdit(self.config.TIMELINE_MIN_AGE)
        self.fields["timeline_min_age"] = timeline_min_age_edit
        scroll_layout.addRow(timeline_min_age_label, timeline_min_age_edit)

        timeline_hourly_label = QLabel(_("Timeline Limit Hourly"))
        timeline_hourly_edit = QLineEdit(self.config.TIMELINE_LIMIT_HOURLY)
        self.fields["timeline_limit_hourly"] = timeline_hourly_edit
        scroll_layout.addRow(timeline_hourly_label, timeline_hourly_edit)

        timeline_daily_label = QLabel(_("Timeline Limit Daily"))
        timeline_daily_edit = QLineEdit(self.config.TIMELINE_LIMIT_DAILY)
        self.fields["timeline_limit_daily"] = timeline_daily_edit
        scroll_layout.addRow(timeline_daily_label, timeline_daily_edit)

        timeline_weekly_label = QLabel(_("Timeline Limit Weekly"))
        timeline_weekly_edit = QLineEdit(self.config.TIMELINE_LIMIT_WEEKLY)
        self.fields["timeline_limit_weekly"] = timeline_weekly_edit
        scroll_layout.addRow(timeline_weekly_label, timeline_weekly_edit)

        timeline_monthly_label = QLabel(_("Timeline Limit Monthly"))
        timeline_monthly_edit = QLineEdit(self.config.TIMELINE_LIMIT_MONTHLY)
        self.fields["timeline_limit_monthly"] = timeline_monthly_edit
        scroll_layout.addRow(timeline_monthly_label, timeline_monthly_edit)

        timeline_yearly_label = QLabel(_("Timeline Limit Yearly"))
        timeline_yearly_edit = QLineEdit(self.config.TIMELINE_LIMIT_YEARLY)
        self.fields["timeline_limit_yearly"] = timeline_yearly_edit
        scroll_layout.addRow(timeline_yearly_label, timeline_yearly_edit)

        layout.addWidget(scroll_widget)

        button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        layout.addWidget(button_box)

        button_box.accepted.connect(self._on_ok)
        button_box.rejected.connect(self.reject)

    def _on_ok(self):
        new_config = SnapperConfig()

        new_config.SPACE_LIMIT = self.fields["space_limit"].text().strip()
        new_config.FREE_LIMIT = self.fields["free_limit"].text().strip()
        new_config.ALLOW_USERS = self.fields["allow_users"].text().strip()
        new_config.ALLOW_GROUPS = self.fields["allow_groups"].text().strip()
        new_config.SYNC_ACL = "yes" if self.fields["sync_acl"].isChecked() else "no"
        new_config.BACKGROUND_COMPARISON = "yes" if self.fields["background_comparison"].isChecked() else "no"
        new_config.NUMBER_CLEANUP = "yes" if self.fields["number_cleanup"].isChecked() else "no"
        new_config.NUMBER_MIN_AGE = self.fields["number_min_age"].text().strip()
        new_config.NUMBER_LIMIT = self.fields["number_limit"].text().strip()
        new_config.NUMBER_LIMIT_IMPORTANT = self.fields["number_limit_important"].text().strip()
        new_config.TIMELINE_CREATE = "yes" if self.fields["timeline_create"].isChecked() else "no"
        new_config.TIMELINE_CLEANUP = "yes" if self.fields["timeline_cleanup"].isChecked() else "no"
        new_config.TIMELINE_MIN_AGE = self.fields["timeline_min_age"].text().strip()
        new_config.TIMELINE_LIMIT_HOURLY = self.fields["timeline_limit_hourly"].text().strip()
        new_config.TIMELINE_LIMIT_DAILY = self.fields["timeline_limit_daily"].text().strip()
        new_config.TIMELINE_LIMIT_WEEKLY = self.fields["timeline_limit_weekly"].text().strip()
        new_config.TIMELINE_LIMIT_MONTHLY = self.fields["timeline_limit_monthly"].text().strip()
        new_config.TIMELINE_LIMIT_YEARLY = self.fields["timeline_limit_yearly"].text().strip()

        try:
            write_config(new_config)
            QMessageBox.information(self, _("Success"), _("Configuration saved successfully."))
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, _("Error"), _("Failed to write config: {0}").format(str(e)))