"""User and group management utilities."""

from __future__ import annotations

import grp
import subprocess
from dataclasses import dataclass


@dataclass(slots=True)
class UserEntry:
    """Represents a system user."""

    username: str
    uid: int
    gid: int
    primary_group: str
    full_name: str
    home_dir: str
    shell: str
    groups: list[str]


SYSTEM_USERS = {"nobody", "nobody4", "noaccess", "nfsnobody"}


def list_users() -> list[UserEntry]:
    """List all system users with UID >= 1000 or root user."""
    import os
    current_username = os.getlogin()

    result = subprocess.run(
        ["getent", "passwd"],
        capture_output=True,
        text=True,
        check=True,
    )

    users: list[UserEntry] = []
    for line in result.stdout.strip().split("\n"):
        if not line:
            continue
        parts = line.split(":")
        if len(parts) < 7:
            continue

        username = parts[0]
        uid = int(parts[2])
        gid = int(parts[3])
        full_name = parts[4].split(",")[0]
        home_dir = parts[5]
        shell = parts[6]

        if username in SYSTEM_USERS:
            continue

        if uid == 0 or uid >= 1000:
            groups_result = subprocess.run(
                ["id", "-nG", username],
                capture_output=True,
                text=True,
                check=True,
            )
            groups = groups_result.stdout.strip().split()

            primary_group_result = subprocess.run(
                ["id", "-gn", username],
                capture_output=True,
                text=True,
                check=True,
            )
            primary_group = primary_group_result.stdout.strip()

            users.append(
                UserEntry(
                    username=username,
                    uid=uid,
                    gid=gid,
                    primary_group=primary_group,
                    full_name=full_name,
                    home_dir=home_dir,
                    shell=shell,
                    groups=groups,
                )
            )

    def _user_sort_key(user: UserEntry) -> tuple[int, str]:
        if user.uid == 0:
            return (0, "")
        if user.username == current_username:
            return (1, "")
        return (2, user.username)

    users.sort(key=_user_sort_key)
    return users


def is_system_group(group: grp.struct_group) -> bool:
    """Check if a group is a system group.

    System groups typically have GID < 1000 on most Linux systems.
    """
    return group.gr_gid < 1000


def build_add_user_command(
    username: str,
    full_name: str = "",
    home_dir: str = "",
    shell: str = "/bin/bash",
    groups: list[str] | None = None,
    primary_group: str = "",
) -> list[str]:
    """Build command to add a new user."""
    cmd = ["pkexec", "/usr/sbin/useradd", "-m"]

    if full_name:
        cmd.extend(["-c", full_name])
    if home_dir:
        cmd.extend(["-d", home_dir])
    if shell:
        cmd.extend(["-s", shell])
    if primary_group:
        cmd.extend(["-g", primary_group])
    if groups:
        cmd.extend(["-G", ",".join(groups)])

    cmd.append(username)
    return cmd


def build_modify_user_command(
    username: str,
    full_name: str = "",
    home_dir: str = "",
    shell: str = "",
    groups: list[str] | None = None,
    primary_group: str = "",
) -> list[str]:
    """Build command to modify an existing user."""
    cmd = ["pkexec", "/usr/sbin/usermod"]

    if full_name:
        cmd.extend(["-c", full_name])
    if home_dir:
        cmd.extend(["-d", home_dir])
    if shell:
        cmd.extend(["-s", shell])
    if primary_group:
        cmd.extend(["-g", primary_group])
    if groups is not None:
        cmd.extend(["-G", ",".join(groups)])

    cmd.append(username)
    return cmd


def build_delete_user_command(username: str) -> list[str]:
    """Build command to delete a user."""
    return ["pkexec", "/usr/sbin/userdel", "-r", username]


def build_set_password_command(username: str, password: str) -> list[str]:
    """Build command to set user password."""
    import base64
    encoded = base64.b64encode(f"{username}:{password}".encode()).decode()
    return ["pkexec", "bash", "-c", f"echo '{encoded}' | base64 -d | chpasswd"]


def is_user_deletable(user: UserEntry) -> bool:
    """Check if a user can be deleted.

    Returns False for:
    - root user (UID 0)
    - System users (nobody, nobody4, noaccess, nfsnobody)
    - Current logged-in user
    """
    if user.uid == 0:
        return False

    if user.username in SYSTEM_USERS:
        return False

    import os
    current_user = os.getlogin()
    if user.username == current_user:
        return False

    return True


def build_add_group_command(name: str, members: list[str] | None = None) -> list[str]:
    """Build command to add a new group."""
    cmd = ["pkexec", "/usr/sbin/groupadd"]

    if members:
        cmd.extend(["-M", ",".join(members)])

    cmd.append(name)
    return cmd


def build_modify_group_command(name: str, members: list[str] | None = None) -> list[str]:
    """Build command to modify a group."""
    cmd = ["pkexec", "/usr/sbin/groupmod"]

    if members is not None:
        cmd.extend(["-M", ",".join(members)])

    cmd.append(name)
    return cmd


def build_delete_group_command(name: str) -> list[str]:
    """Build command to delete a group."""
    return ["pkexec", "/usr/sbin/groupdel", name]