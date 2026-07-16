"""Journald log management core functions."""

from __future__ import annotations

import os
import subprocess
from dataclasses import dataclass
from datetime import datetime
from typing import Optional, List

from systemd import journal


PRIORITY_MAP = {
    0: "emerg",
    1: "alert",
    2: "crit",
    3: "err",
    4: "warning",
    5: "notice",
    6: "info",
    7: "debug",
}

PRIORITY_LEVELS = ["emerg", "alert", "crit", "err", "warning", "notice", "info", "debug"]


@dataclass
class JournalEntry:
    """Represents a single journal entry."""

    timestamp: datetime
    priority: str
    priority_num: int
    systemd_unit: str
    message: str
    process_id: Optional[int] = None
    host: Optional[str] = None
    facility: Optional[str] = None

    def priority_color(self) -> str:
        """Return color code based on priority."""
        colors = {
            0: "#9d2933",
            1: "#c5221f",
            2: "#c5221f",
            3: "#ea4335",
            4: "#fbbc04",
            5: "#1a73e8",
            6: "#34a853",
            7: "#5f6368",
        }
        return colors.get(self.priority_num, "#202124")


@dataclass
class JournalConfig:
    """Represents journal configuration."""

    max_file_size: Optional[str] = None
    max_files: Optional[int] = None
    compress: Optional[bool] = None
    rate_limit_interval: Optional[str] = None
    rate_limit_burst: Optional[int] = None


def get_journal_entries(
    scope: str = "system",
    priority: str = "all",
    search_term: str = "",
    limit: int = 1000,
) -> List[JournalEntry]:
    """Get journal entries with optional filtering.

    Args:
        scope: "system" or "user"
        priority: "all" or priority level (emerg, alert, crit, err, warning, notice, info, debug)
        search_term: Optional search text
        limit: Maximum number of entries to return

    Returns:
        List of JournalEntry objects
    """
    entries = []

    cmd = ["journalctl", "-n", str(limit), "-o", "json"]
    
    if scope == "user":
        cmd.append("--user")
    
    if priority != "all":
        if priority in PRIORITY_LEVELS:
            priority_num = PRIORITY_LEVELS.index(priority)
            cmd.append(f"--priority={priority_num}")

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        
        import json
        for line in result.stdout.strip().split("\n"):
            if not line:
                continue
            try:
                entry = json.loads(line)
                
                timestamp = datetime.fromtimestamp(entry.get("_SOURCE_REALTIME_TIMESTAMP", entry.get("__REALTIME_TIMESTAMP", 0)) / 1e6)
                priority_num = int(entry.get("PRIORITY", 7))
                priority_str = PRIORITY_MAP.get(priority_num, "unknown")
                systemd_unit = entry.get("_SYSTEMD_UNIT", "")
                message = entry.get("MESSAGE", "")

                if search_term and search_term.lower() not in message.lower():
                    continue

                entries.append(
                    JournalEntry(
                        timestamp=timestamp,
                        priority=priority_str,
                        priority_num=priority_num,
                        systemd_unit=systemd_unit,
                        message=message,
                        process_id=entry.get("_PID"),
                        host=entry.get("_HOSTNAME"),
                        facility=entry.get("SYSLOG_FACILITY"),
                    )
                )
            except json.JSONDecodeError:
                continue
    except subprocess.CalledProcessError:
        pass
    except Exception:
        pass

    return entries


def get_journal_config() -> JournalConfig:
    """Get current journal configuration using systemd-analyze."""
    config = JournalConfig()
    try:
        result = subprocess.run(
            ["systemd-analyze", "cat-config", "systemd/journald.conf"],
            capture_output=True,
            text=True,
            check=True,
        )

        in_journal_section = False
        for line in result.stdout.split("\n"):
            line = line.strip()

            if line.startswith("[Journal]"):
                in_journal_section = True
                continue

            if in_journal_section and "=" in line:
                if line.startswith("#"):
                    line = line[1:].strip()

                if "=" in line:
                    key, value = line.split("=", 1)
                    key = key.strip()
                    value = value.strip()

                    if key == "SystemMaxUse" and not config.max_file_size:
                        config.max_file_size = value if value else None
                    elif key == "SystemMaxFiles" and not config.max_files:
                        try:
                            config.max_files = int(value)
                        except ValueError:
                            pass
                    elif key == "Compress" and config.compress is None:
                        config.compress = value.lower() == "yes"
                    elif key == "RateLimitIntervalSec" and not config.rate_limit_interval:
                        config.rate_limit_interval = value if value else None
                    elif key == "RateLimitInterval" and not config.rate_limit_interval:
                        config.rate_limit_interval = value if value else None
                    elif key == "RateLimitBurst" and not config.rate_limit_burst:
                        try:
                            config.rate_limit_burst = int(value)
                        except ValueError:
                            pass

    except subprocess.CalledProcessError:
        config = _read_journal_config_fallback()
    except FileNotFoundError:
        config = _read_journal_config_fallback()

    return config


def _read_journal_config_fallback() -> JournalConfig:
    """Fallback to reading journald.conf files directly."""
    config = JournalConfig()
    config_files = [
        "/usr/lib/systemd/journald.conf",
        "/etc/systemd/journald.conf",
    ]

    for config_file in config_files:
        try:
            with open(config_file, "r") as f:
                in_journal_section = False
                for line in f:
                    line = line.strip()

                    if line.startswith("[Journal]"):
                        in_journal_section = True
                        continue

                    if in_journal_section and "=" in line:
                        if line.startswith("#"):
                            line = line[1:].strip()

                        if "=" in line:
                            key, value = line.split("=", 1)
                            key = key.strip()
                            value = value.strip()

                            if key == "SystemMaxUse" and not config.max_file_size:
                                config.max_file_size = value if value else None
                            elif key == "SystemMaxFiles" and not config.max_files:
                                try:
                                    config.max_files = int(value)
                                except ValueError:
                                    pass
                            elif key == "Compress" and config.compress is None:
                                config.compress = value.lower() == "yes"
                            elif key == "RateLimitIntervalSec" and not config.rate_limit_interval:
                                config.rate_limit_interval = value if value else None
                            elif key == "RateLimitInterval" and not config.rate_limit_interval:
                                config.rate_limit_interval = value if value else None
                            elif key == "RateLimitBurst" and not config.rate_limit_burst:
                                try:
                                    config.rate_limit_burst = int(value)
                                except ValueError:
                                    pass
        except (FileNotFoundError, PermissionError):
            continue

    return config


def set_journal_config(config: JournalConfig) -> bool:
    """Set journal configuration using pkexec."""
    lines = []
    try:
        with open("/etc/systemd/journald.conf", "r") as f:
            lines = f.readlines()
    except FileNotFoundError:
        pass
    except PermissionError:
        pass

    new_lines = []
    for line in lines:
        stripped = line.strip()
        if stripped.startswith("SystemMaxUse="):
            if config.max_file_size:
                new_lines.append(f"SystemMaxUse={config.max_file_size}\n")
            else:
                new_lines.append(line)
        elif stripped.startswith("SystemMaxFiles="):
            if config.max_files:
                new_lines.append(f"SystemMaxFiles={config.max_files}\n")
            else:
                new_lines.append(line)
        elif stripped.startswith("Compress="):
            if config.compress is not None:
                value = "yes" if config.compress else "no"
                new_lines.append(f"Compress={value}\n")
            else:
                new_lines.append(line)
        elif stripped.startswith("RateLimitInterval="):
            if config.rate_limit_interval:
                new_lines.append(f"RateLimitInterval={config.rate_limit_interval}\n")
            else:
                new_lines.append(line)
        elif stripped.startswith("RateLimitBurst="):
            if config.rate_limit_burst:
                new_lines.append(f"RateLimitBurst={config.rate_limit_burst}\n")
            else:
                new_lines.append(line)
        else:
            new_lines.append(line)

    content = "".join(new_lines)

    cmd = ["pkexec", "tee", "/etc/systemd/journald.conf"]
    try:
        subprocess.run(cmd, input=content.encode(), check=True)
        subprocess.run(["pkexec", "systemctl", "restart", "systemd-journald"], check=True)
        return True
    except subprocess.CalledProcessError:
        return False


def clear_journal(scope: str = "system") -> bool:
    """Clear journal logs using pkexec."""
    cmd = ["pkexec", "journalctl"]
    if scope == "user":
        cmd.append("--user")
    cmd.extend(["--flush", "--rotate"])

    try:
        subprocess.run(cmd, check=True)
        subprocess.run(["pkexec", "journalctl", "--vacuum-time=1s"], check=True)
        return True
    except subprocess.CalledProcessError:
        return False
