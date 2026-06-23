"""Cron job parsing and management logic."""

from __future__ import annotations

import os
import subprocess
from dataclasses import dataclass
from typing import Literal

from crontab import CronTab

USER_CRON_DIR = "/var/spool/cron/tabs"
ROOT_CRON_PATH = "/var/spool/cron/root"


@dataclass
class CronJob:
    """Represents a single cron job entry."""

    minute: str
    hour: str
    day: str
    month: str
    weekday: str
    command: str
    comment: str = ""
    enabled: bool = True

    def __str__(self) -> str:
        """Convert to cron file format string."""
        line = f"{self.minute} {self.hour} {self.day} {self.month} {self.weekday} {self.command}"
        if not self.enabled:
            line = "# " + line
        return line

    def schedule_str(self) -> str:
        """Get the schedule string for validation."""
        return f"{self.minute} {self.hour} {self.day} {self.month} {self.weekday}"


def _parse_cron_line(line: str) -> tuple[CronJob | None, str | None]:
    """Parse a single cron line.

    Returns:
        Tuple of (CronJob object if valid, standalone comment if any).
    """
    stripped = line.strip()

    if not stripped:
        return None, None

    if stripped.startswith("#"):
        content = stripped[1:].lstrip()
        parts = content.split(None, 5)
        if len(parts) == 6:
            try:
                int(parts[0])
                return CronJob(
                    minute=parts[0],
                    hour=parts[1],
                    day=parts[2],
                    month=parts[3],
                    weekday=parts[4],
                    command=parts[5],
                    comment="",
                    enabled=False,
                ), None
            except ValueError:
                pass
        return None, content

    comment = ""
    content = stripped

    if "#" in content:
        idx = content.find("#")
        comment = content[idx:].strip()
        content = content[:idx].strip()

    parts = content.split(None, 5)
    if len(parts) != 6:
        return None, None

    return CronJob(
        minute=parts[0],
        hour=parts[1],
        day=parts[2],
        month=parts[3],
        weekday=parts[4],
        command=parts[5],
        comment=comment,
        enabled=True,
    ), None


def _get_user_cron_path(username: str) -> str:
    """Get the cron file path for a user."""
    return os.path.join(USER_CRON_DIR, username)


def load_cron_jobs(user_mode: bool = True) -> tuple[list[CronJob], str | None]:
    """Load cron jobs from file.

    Args:
        user_mode: True for user cron, False for root cron.

    Returns:
        Tuple of (list of CronJob, error message or None).
    """
    jobs: list[CronJob] = []

    if user_mode:
        username = os.getlogin()
        cron_path = _get_user_cron_path(username)
    else:
        cron_path = ROOT_CRON_PATH

    if not os.path.exists(cron_path):
        return jobs, None

    try:
        with open(cron_path, "r") as f:
            lines = f.readlines()
    except PermissionError:
        return jobs, "Permission denied. Cannot read cron file."
    except Exception as e:
        return jobs, f"Failed to read cron file: {str(e)}"

    pending_comment = ""

    for line in lines:
        line = line.rstrip("\n\r")
        job, comment = _parse_cron_line(line)

        if comment is not None:
            if pending_comment:
                pending_comment += "\n" + comment
            else:
                pending_comment = comment
            continue

        if job is not None:
            if pending_comment:
                job.comment = pending_comment + (" " + job.comment if job.comment else "")
                pending_comment = ""
            jobs.append(job)

    return jobs, None


def save_cron_jobs(jobs: list[CronJob], user_mode: bool = True) -> Literal["ok", "permission_denied", "error"]:
    """Save cron jobs to file.

    Args:
        jobs: List of CronJob objects to save.
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
        cron_path = ROOT_CRON_PATH

    lines = []
    for job in jobs:
        if job.comment:
            lines.append(job.comment)
        lines.append(str(job))

    content = "\n".join(lines) + "\n"

    try:
        if user_mode:
            with open(cron_path, "w") as f:
                f.write(content)
        else:
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


def validate_cron_job(job: CronJob) -> tuple[bool, str]:
    """Validate a complete cron job using crontab package.

    Returns:
        Tuple of (is_valid, error_message).
    """
    try:
        CronTab(job.schedule_str())
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