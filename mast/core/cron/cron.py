"""Cron job management logic."""

from __future__ import annotations

import subprocess

from crontab import CronTab


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


def save_root_cron(cron: CronTab) -> bool:
    """Save root cron jobs using pkexec.

    Args:
        cron: CronTab object to save.

    Returns:
        True on success, False on failure.
    """
    result = subprocess.run(
        ["pkexec", "crontab", "-"],
        input=str(cron).encode(),
        capture_output=True,
    )
    return result.returncode == 0


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
