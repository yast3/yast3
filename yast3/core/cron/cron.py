"""Cron job parsing and management logic."""

from __future__ import annotations

import os
import subprocess
from typing import Literal

from crontab import CronTab, CronItem

USER_CRON_DIR = "/var/spool/cron/tabs"


def _get_user_cron_path(username: str) -> str:
    """Get the cron file path for a user."""
    return os.path.join(USER_CRON_DIR, username)


def load_root_cron() -> CronTab:
    """Load root cron jobs.

    Returns:
        CronTab object.
    """
    result = subprocess.run(
        ["pkexec", "crontab", "-l"],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        return CronTab(user='root')
    
    return CronTab(user='root', tab=result.stdout)


def save_cron_jobs(jobs: list[CronItem], user_mode: bool = True) -> Literal["ok", "permission_denied", "error"]:
    """Save cron jobs to file.

    Args:
        jobs: List of CronItem objects to save.
        user_mode: True for user cron, False for root cron.

    Returns:
        "ok" on success,
        "permission_denied" if cannot write to file,
        "error" for other errors.
    """
    if user_mode:
        username = os.getlogin()
        cron_path = _get_user_cron_path(username)
    else:
        cron_path = _get_user_cron_path("root")

    header_lines = []
    result = subprocess.run(
        ["pkexec", "cat", cron_path],
        capture_output=True,
        text=True,
    )
    if result.returncode == 0:
        content = result.stdout
        existing_lines = content.splitlines() if content else []
        header_lines = existing_lines[:3]

    lines = []
    for job in jobs:
        if job.comment:
            lines.append(job.comment)
        if job.is_enabled():
            lines.append(f"{job.minute} {job.hour} {job.day} {job.month} {job.dow} {job.command}")
        else:
            lines.append(f"# {job.minute} {job.hour} {job.day} {job.month} {job.dow} {job.command}")

    content = "\n".join(header_lines + lines) + "\n"

    try:
        result = subprocess.run(
            ["pkexec", "tee", cron_path],
            input=content.encode(),
            capture_output=True,
        )
        if result.returncode != 0:
            return "permission_denied"

        return "ok"
    except PermissionError:
        return "permission_denied"
    except Exception:
        return "error"


def validate_cron_job(job: CronItem) -> tuple[bool, str]:
    """Validate a complete cron job using crontab package.

    Returns:
        Tuple of (is_valid, error_message).
    """
    try:
        CronTab(f"{job.minute} {job.hour} {job.day} {job.month} {job.dow}")
    except Exception as e:
        return False, str(e)

    if not job.command.strip():
        return False, "Command cannot be empty"

    return True, ""


def get_suggestions(field_type: str) -> list[str]:
    """Get common values for a cron field."""
    suggestions = {
        "minute": ["*", "0", "15", "30", "45", "*/5", "*/10", "*/15"],
        "hour": ["*", "0", "6", "8", "12", "18", "20", "*/2"],
        "day": ["*", "1", "15", "*/7"],
        "month": ["*", "1", "6", "12", "*/3"],
        "weekday": ["*", "0", "1-5", "6"],
    }
    return suggestions.get(field_type, [])
