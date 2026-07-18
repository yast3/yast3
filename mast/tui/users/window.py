"""UI components for the Users & Groups module (TUI)."""

from __future__ import annotations

import grp
import os
import re
import subprocess

from textual.app import ComposeResult
from textual.containers import Horizontal, Vertical
from textual.screen import Screen
from textual.widgets import Button, DataTable, Header, Input, Label, Static, TabbedContent, TabPane

from mast.core.i18n import _
from mast.core.users import (
    UserEntry,
    list_users,
    build_add_user_command,
    build_modify_user_command,
    build_delete_user_command,
    build_set_password_command,
    is_user_deletable,
    is_system_group,
    build_add_group_command,
    build_modify_group_command,
    build_delete_group_command,
)


class UsersWindow(Screen):
    """TUI window for Users & Groups management."""

    CSS = """
    .container {
        width: 100%;
        height: 1fr;
        padding: 1;
    }

    .button-row {
        align: left middle;
        margin-bottom: 1;
    }

    .message {
        margin-top: 1;
        color: yellow;
    }

    .error {
        color: red;
    }

    .success {
        color: green;
    }

    TabbedContent {
        height: 1fr;
    }

    DataTable {
        height: 1fr;
    }

    Input {
        width: 40;
    }

    .label-right {
        width: 15;
        content-align: right middle;
        padding-right: 1;
    }
    """

    BINDINGS = [
        ("escape", "app.pop_screen", "Back"),
        ("q", "app.pop_screen", "Back"),
    ]

    def __init__(self) -> None:
        super().__init__()
        self._users: list[UserEntry] = []
        self._groups: list[grp.struct_group] = []
        self._selected_user: UserEntry | None = None
        self._selected_group: grp.struct_group | None = None
        self._is_new_user = False
        self._is_new_group = False

    def compose(self) -> ComposeResult:
        yield Header()
        with Vertical(classes="container"):
            with TabbedContent(id="tabs"):
                with TabPane(_("Users"), id="users-tab"):
                    yield from self._compose_users_tab()
                with TabPane(_("Groups"), id="groups-tab"):
                    yield from self._compose_groups_tab()
            yield Static("", id="message", classes="message")

    def _compose_users_tab(self) -> ComposeResult:
        with Vertical():
            with Horizontal(classes="button-row"):
                yield Button(_("Add"), id="add-user-btn")
                yield Button(_("Delete"), id="delete-user-btn", disabled=True)
                yield Button(_("Save"), id="save-user-btn", disabled=True)
            yield DataTable(id="users-table")
            with Vertical():
                with Horizontal():
                    yield Label(_("UID:"), classes="label-right")
                    yield Input(id="uid-input")
                with Horizontal():
                    yield Label(_("Username:"), classes="label-right")
                    yield Input(id="username-input")
                with Horizontal():
                    yield Label(_("Display Name:"), classes="label-right")
                    yield Input(id="fullname-input")
                with Horizontal():
                    yield Label(_("Home Directory:"), classes="label-right")
                    yield Input(id="homedir-input")
                with Horizontal():
                    yield Label(_("Shell:"), classes="label-right")
                    yield Input(id="shell-input", value="/bin/bash")
                with Horizontal():
                    yield Label(_("Password:"), classes="label-right")
                    yield Input(id="password-input", password=True)
                with Horizontal():
                    yield Label(_("Primary Group:"), classes="label-right")
                    yield Input(id="primary-group-input")
                with Horizontal():
                    yield Label(_("Additional Groups:"), classes="label-right")
                    yield DataTable(id="user-groups-table")

    def _compose_groups_tab(self) -> ComposeResult:
        with Vertical():
            with Horizontal(classes="button-row"):
                yield Button(_("Add"), id="add-group-btn")
                yield Button(_("Delete"), id="delete-group-btn", disabled=True)
                yield Button(_("Save"), id="save-group-btn", disabled=True)
            yield DataTable(id="groups-table")
            with Vertical():
                with Horizontal():
                    yield Label(_("GID:"), classes="label-right")
                    yield Input(id="gid-input")
                with Horizontal():
                    yield Label(_("Group Name:"), classes="label-right")
                    yield Input(id="group-name-input")
                yield Static(_("Members (use space to toggle):"))
                yield DataTable(id="group-members-table")

    def on_mount(self) -> None:
        self._setup_users_table()
        self._setup_user_groups_table()
        self._setup_groups_table()
        self._setup_group_members_table()
        self._load_users()

    def _setup_users_table(self) -> None:
        table = self.query_one("#users-table", DataTable)
        table.add_columns(_("Username"), _("Full Name"))

    def _setup_user_groups_table(self) -> None:
        table = self.query_one("#user-groups-table", DataTable)
        table.add_columns(_("Group"), _("Selected"))

    def _setup_groups_table(self) -> None:
        table = self.query_one("#groups-table", DataTable)
        table.add_columns(_("Group"), _("Type"))

    def _setup_group_members_table(self) -> None:
        table = self.query_one("#group-members-table", DataTable)
        table.add_columns(_("User"), _("Member"))

    def _load_users(self) -> None:
        try:
            self._users = list_users()
            self._groups = grp.getgrall()
            self._groups.sort(key=lambda g: g.gr_name)
            self._populate_users_table()
            self._populate_user_groups_table()
        except Exception as e:
            self.show_message(_("Failed to load users: {0}").format(str(e)), error=True)

    def _load_groups(self) -> None:
        try:
            self._groups = grp.getgrall()
            self._groups.sort(key=lambda g: g.gr_name)
            self._users = list_users()
            self._populate_groups_table()
            self._populate_group_members_table()

            for idx, group in enumerate(self._groups):
                if group.gr_name == "users":
                    table = self.query_one("#groups-table", DataTable)
                    table.move_cursor(row=idx)
                    self._fill_group_form(group)
                    break
        except Exception as e:
            self.show_message(_("Failed to load groups: {0}").format(str(e)), error=True)

    def _populate_users_table(self) -> None:
        table = self.query_one("#users-table", DataTable)
        table.clear()

        current_username = None
        try:
            current_username = os.getlogin()
        except Exception:
            pass

        for user in self._users:
            table.add_row(user.username, user.full_name)

        if current_username:
            for idx, user in enumerate(self._users):
                if user.username == current_username:
                    table.move_cursor(row=idx)
                    break

    def _populate_user_groups_table(self) -> None:
        table = self.query_one("#user-groups-table", DataTable)
        table.clear()

        for group in self._groups:
            table.add_row(group.gr_name, "")

    def _populate_groups_table(self) -> None:
        table = self.query_one("#groups-table", DataTable)
        table.clear()

        for group in self._groups:
            group_type = _("System") if is_system_group(group) else _("User")
            table.add_row(group.gr_name, group_type)

    def _populate_group_members_table(self) -> None:
        table = self.query_one("#group-members-table", DataTable)
        table.clear()

        for user in self._users:
            table.add_row(user.username, "")

    def _fill_user_form(self, user: UserEntry) -> None:
        is_root = user.uid == 0

        self.query_one("#uid-input", Input).value = str(user.uid)
        self.query_one("#uid-input", Input).disabled = True
        self.query_one("#username-input", Input).value = user.username
        self.query_one("#username-input", Input).disabled = True
        self.query_one("#fullname-input", Input).value = user.full_name
        self.query_one("#homedir-input", Input).value = user.home_dir
        self.query_one("#shell-input", Input).value = user.shell
        self.query_one("#primary-group-input", Input).value = user.primary_group
        self.query_one("#password-input", Input).value = ""

        groups_table = self.query_one("#user-groups-table", DataTable)
        for row_key in groups_table.rows:
            group_name = groups_table.get_cell(row_key, _("Group"))
            selected = "✓" if group_name in user.groups else ""
            groups_table.update_cell(row_key, _("Selected"), selected)

        self.query_one("#fullname-input", Input).disabled = is_root
        self.query_one("#homedir-input", Input).disabled = is_root
        self.query_one("#shell-input", Input).disabled = is_root
        self.query_one("#primary-group-input", Input).disabled = is_root

    def _clear_user_form(self) -> None:
        self.query_one("#uid-input", Input).value = ""
        self.query_one("#uid-input", Input).disabled = True
        self.query_one("#username-input", Input).value = ""
        self.query_one("#username-input", Input).disabled = False
        self.query_one("#fullname-input", Input).value = ""
        self.query_one("#homedir-input", Input).value = ""
        self.query_one("#shell-input", Input).value = "/bin/bash"
        self.query_one("#primary-group-input", Input).value = "users"
        self.query_one("#password-input", Input).value = ""

        groups_table = self.query_one("#user-groups-table", DataTable)
        for row_key in groups_table.rows:
            groups_table.update_cell(row_key, _("Selected"), "")

    def _fill_group_form(self, group: grp.struct_group) -> None:
        self.query_one("#gid-input", Input).value = str(group.gr_gid)
        self.query_one("#gid-input", Input).disabled = True
        self.query_one("#group-name-input", Input).value = group.gr_name
        self.query_one("#group-name-input", Input).disabled = True

        members_table = self.query_one("#group-members-table", DataTable)
        for idx, row_key in enumerate(members_table.rows):
            user = self._users[idx]
            selected = "✓" if user.primary_group == group.gr_name or user.username in group.gr_mem else ""
            members_table.update_cell(row_key, _("Member"), selected)

    def _clear_group_form(self) -> None:
        self.query_one("#gid-input", Input).value = ""
        self.query_one("#gid-input", Input).disabled = True
        self.query_one("#group-name-input", Input).value = ""
        self.query_one("#group-name-input", Input).disabled = False

        members_table = self.query_one("#group-members-table", DataTable)
        for row_key in members_table.rows:
            members_table.update_cell(row_key, _("Member"), "")

    def show_message(self, message: str, error: bool = False, success: bool = False) -> None:
        msg_widget = self.query_one("#message", Static)
        msg_widget.update(message)
        msg_widget.remove_class("error", "success")
        if error:
            msg_widget.add_class("error")
        elif success:
            msg_widget.add_class("success")

    def _handle_users_table_selection(self, table: DataTable) -> None:
        selected = table.cursor_row is not None and 0 <= table.cursor_row < len(self._users)

        delete_btn = self.query_one("#delete-user-btn", Button)
        save_btn = self.query_one("#save-user-btn", Button)
        delete_btn.disabled = not selected
        save_btn.disabled = not selected

        if selected:
            self._is_new_user = False
            self._selected_user = self._users[table.cursor_row]
            self._fill_user_form(self._selected_user)
            delete_btn.disabled = not is_user_deletable(self._selected_user)

    def _toggle_group_selection(self, table: DataTable) -> None:
        if table.cursor_row is not None:
            for row_key in table.rows:
                idx = list(table.rows).index(row_key)
                if idx == table.cursor_row:
                    current = table.get_cell(row_key, _("Selected"))
                    new_val = "" if current == "✓" else "✓"
                    table.update_cell(row_key, _("Selected"), new_val)
                    break

    def _handle_groups_table_selection(self, table: DataTable) -> None:
        selected = table.cursor_row is not None and 0 <= table.cursor_row < len(self._groups)

        delete_btn = self.query_one("#delete-group-btn", Button)
        save_btn = self.query_one("#save-group-btn", Button)

        if selected:
            self._is_new_group = False
            self._selected_group = self._groups[table.cursor_row]
            self._fill_group_form(self._selected_group)
            is_system = is_system_group(self._selected_group)
            delete_btn.disabled = is_system
            save_btn.disabled = is_system
        else:
            delete_btn.disabled = True
            save_btn.disabled = True

    def _toggle_member_selection(self, table: DataTable) -> None:
        if table.cursor_row is not None:
            for row_key in table.rows:
                idx = list(table.rows).index(row_key)
                if idx == table.cursor_row:
                    current = table.get_cell(row_key, _("Member"))
                    new_val = "" if current == "✓" else "✓"
                    table.update_cell(row_key, _("Member"), new_val)
                    break

    def on_button_pressed(self, event: Button.Pressed) -> None:
        button_id = event.button.id
        if button_id == "add-user-btn":
            self._on_add_user()
        elif button_id == "delete-user-btn":
            self._on_delete_user()
        elif button_id == "save-user-btn":
            self._on_save_user()
        elif button_id == "add-group-btn":
            self._on_add_group()
        elif button_id == "delete-group-btn":
            self._on_delete_group()
        elif button_id == "save-group-btn":
            self._on_save_group()

    def on_data_table_cursor_moved(self, event) -> None:
        table = event.data_table
        table_id = table.id
        if table_id == "users-table":
            self._handle_users_table_selection(table)
        elif table_id == "user-groups-table":
            self._toggle_group_selection(table)
        elif table_id == "groups-table":
            self._handle_groups_table_selection(table)
        elif table_id == "group-members-table":
            self._toggle_member_selection(table)

    def on_tabbed_content_tab_changed(self, event) -> None:
        if event.new_tab.id == "groups-tab":
            self._load_groups()

    def _on_add_user(self) -> None:
        self._is_new_user = True
        self._selected_user = None
        table = self.query_one("#users-table", DataTable)
        table.move_cursor(row=-1)
        self._clear_user_form()
        self.query_one("#delete-user-btn", Button).disabled = True
        self.query_one("#save-user-btn", Button).disabled = False

    def _on_delete_user(self) -> None:
        if not self._selected_user:
            self.show_message(_("Please select a user to delete."), error=True)
            return

        if not is_user_deletable(self._selected_user):
            self.show_message(_("This user cannot be deleted."), error=True)
            return

        cmd = build_delete_user_command(self._selected_user.username)
        self._run_command(cmd, _("User deleted successfully."))

    def _on_save_user(self) -> None:
        username = self.query_one("#username-input", Input).value.strip()
        if not username:
            self.show_message(_("Username cannot be empty."), error=True)
            return

        if self._is_new_user and not re.match(r"^[a-z][a-z0-9_-]*$", username):
            self.show_message(_("Username must start with a lowercase letter."), error=True)
            return

        full_name = self.query_one("#fullname-input", Input).value.strip()
        home_dir = self.query_one("#homedir-input", Input).value.strip()
        shell = self.query_one("#shell-input", Input).value.strip() or "/bin/bash"
        password = self.query_one("#password-input", Input).value.strip()
        primary_group = self.query_one("#primary-group-input", Input).value.strip()

        selected_groups = []
        groups_table = self.query_one("#user-groups-table", DataTable)
        for row_key in groups_table.rows:
            if groups_table.get_cell(row_key, _("Selected")) == "✓":
                selected_groups.append(groups_table.get_cell(row_key, _("Group")))

        if self._is_new_user:
            cmd = build_add_user_command(
                username=username,
                full_name=full_name,
                home_dir=home_dir,
                shell=shell,
                groups=selected_groups,
                primary_group=primary_group,
            )
            success_msg = _("User created successfully.")
        else:
            cmd = build_modify_user_command(
                username=username,
                full_name=full_name,
                home_dir=home_dir,
                shell=shell,
                groups=selected_groups,
                primary_group=primary_group,
            )
            success_msg = _("User updated successfully.")

        if self._run_command(cmd, success_msg) and password:
            cmd = build_set_password_command(username, password)
            self._run_command(cmd, _("Password set successfully."))

    def _on_add_group(self) -> None:
        self._is_new_group = True
        self._selected_group = None
        table = self.query_one("#groups-table", DataTable)
        table.move_cursor(row=-1)
        self._clear_group_form()
        self.query_one("#delete-group-btn", Button).disabled = True
        self.query_one("#save-group-btn", Button).disabled = False

    def _on_delete_group(self) -> None:
        if not self._selected_group:
            self.show_message(_("Please select a group to delete."), error=True)
            return

        cmd = build_delete_group_command(self._selected_group.gr_name)
        self._run_command(cmd, _("Group deleted successfully."))

    def _on_save_group(self) -> None:
        group_name = self.query_one("#group-name-input", Input).value.strip()
        if not group_name:
            self.show_message(_("Group name cannot be empty."), error=True)
            return

        if self._is_new_group and not re.match(r"^[a-z][a-z0-9_-]*$", group_name):
            self.show_message(_("Group name must start with a lowercase letter."), error=True)
            return

        selected_users = []
        members_table = self.query_one("#group-members-table", DataTable)
        for row_key in members_table.rows:
            if members_table.get_cell(row_key, _("Member")) == "✓":
                selected_users.append(members_table.get_cell(row_key, _("User")))

        if self._is_new_group:
            cmd = build_add_group_command(group_name)
            success_msg = _("Group created successfully.")
        else:
            cmd = build_modify_group_command(group_name, selected_users)
            success_msg = _("Group updated successfully.")

        self._run_command(cmd, success_msg)

    def _run_command(self, cmd: list[str], success_msg: str) -> bool:
        try:
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode == 0:
                self.show_message(success_msg, success=True)
                tabs = self.query_one("#tabs", TabbedContent)
                if tabs.active == "users-tab":
                    self._load_users()
                else:
                    self._load_groups()
                return True
            else:
                self.show_message(_("Error: {0}").format(result.stderr), error=True)
        except Exception as e:
            self.show_message(_("Error: {0}").format(str(e)), error=True)
        return False