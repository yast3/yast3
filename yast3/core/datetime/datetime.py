"""Date and Time management logic."""

from __future__ import annotations

import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Literal

TIMEZONE_FILE = "/etc/timezone"
LOCALTIME_LINK = "/etc/localtime"
TIMEZONE_DIR = "/usr/share/zoneinfo"
HWCLOCK_FILE = "/etc/adjtime"
CHRONYD_CONF = "/etc/chrony.conf"
NTPD_CONF = "/etc/ntp.conf"


@dataclass
class NTPStatus:
    """Represents NTP status information."""

    enabled: bool
    synchronized: bool
    servers: list[str]


def get_current_timezone() -> str:
    """Get the current system timezone.

    Returns:
        The current timezone (e.g., "Asia/Shanghai").

    Raises:
        FileNotFoundError: If timezone file doesn't exist.
        PermissionError: If cannot read the file.
    """
    if Path(LOCALTIME_LINK).is_symlink():
        target = Path(LOCALTIME_LINK).resolve()
        if TIMEZONE_DIR in str(target):
            return str(target).replace(TIMEZONE_DIR + "/", "")

    if Path(TIMEZONE_FILE).exists():
        with open(TIMEZONE_FILE, "r") as f:
            return f.read().strip()

    return "UTC"


def get_timezone_list() -> list[str]:
    """Get a list of available timezones.

    Returns:
        List of timezone strings.
    """
    timezones = []
    tz_dir = Path(TIMEZONE_DIR)
    if tz_dir.exists() and tz_dir.is_dir():
        for path in sorted(tz_dir.rglob("*")):
            if path.is_file() and not path.is_symlink():
                rel_path = path.relative_to(tz_dir)
                timezones.append(str(rel_path))
    return timezones


def set_timezone(
    timezone: str, use_pkexec: bool = True
) -> tuple[Literal["ok", "permission_denied", "pkexec_failed", "error"], str]:
    """Set the system timezone.

    Args:
        timezone: The timezone to set (e.g., "Asia/Shanghai").
        use_pkexec: If True, use pkexec for privilege escalation.

    Returns:
        Tuple of (status, message).
    """
    tz_path = Path(TIMEZONE_DIR) / timezone
    if not tz_path.exists():
        return ("error", f"Invalid timezone: {timezone}")

    script_path = Path(__file__).parent / "set_timezone.py"

    if not use_pkexec:
        result = subprocess.run(
            [sys.executable, str(script_path), timezone],
            capture_output=True,
            text=True,
        )
        if result.returncode == 0 and result.stdout.strip() == "OK":
            return ("ok", "Timezone updated successfully")
        elif result.returncode == 6:
            return ("permission_denied", "Permission denied")
        else:
            return ("error", result.stderr.strip() or "Failed to set timezone")

    result = subprocess.run(
        ["pkexec", sys.executable, str(script_path), timezone],
        capture_output=True,
        text=True,
    )

    if result.returncode == 0 and result.stdout.strip() == "OK":
        return ("ok", "Timezone updated successfully")
    elif result.returncode == 126 or result.returncode == 127:
        return ("pkexec_failed", "Authentication failed")
    elif result.returncode == 6:
        return ("permission_denied", "Permission denied")
    else:
        return ("error", result.stderr.strip() or "Failed to set timezone")


def is_hwclock_utc() -> bool:
    """Check if hardware clock is set to UTC.

    Returns:
        True if hardware clock is UTC, False if local time.
    """
    if Path(HWCLOCK_FILE).exists():
        with open(HWCLOCK_FILE, "r") as f:
            content = f.read()
            return "UTC" in content
    return True


def set_hwclock_utc(
    utc: bool, use_pkexec: bool = True
) -> tuple[Literal["ok", "permission_denied", "pkexec_failed", "error"], str]:
    """Set hardware clock to UTC or local time.

    Args:
        utc: True for UTC, False for local time.
        use_pkexec: If True, use pkexec for privilege escalation.

    Returns:
        Tuple of (status, message).
    """
    script_path = Path(__file__).parent / "set_hwclock.py"

    if not use_pkexec:
        result = subprocess.run(
            [sys.executable, str(script_path), "UTC" if utc else "LOCAL"],
            capture_output=True,
            text=True,
        )
        if result.returncode == 0 and result.stdout.strip() == "OK":
            return ("ok", "Hardware clock updated successfully")
        elif result.returncode == 6:
            return ("permission_denied", "Permission denied")
        else:
            return ("error", result.stderr.strip() or "Failed to set hardware clock")

    result = subprocess.run(
        ["pkexec", sys.executable, str(script_path), "UTC" if utc else "LOCAL"],
        capture_output=True,
        text=True,
    )

    if result.returncode == 0 and result.stdout.strip() == "OK":
        return ("ok", "Hardware clock updated successfully")
    elif result.returncode == 126 or result.returncode == 127:
        return ("pkexec_failed", "Authentication failed")
    elif result.returncode == 6:
        return ("permission_denied", "Permission denied")
    else:
        return ("error", result.stderr.strip() or "Failed to set hardware clock")


def get_ntp_status() -> NTPStatus:
    """Get NTP status information.

    Returns:
        NTPStatus object with enabled, synchronized, and servers.
    """
    servers = get_ntp_servers()
    enabled = len(servers) > 0

    synchronized = False
    try:
        result = subprocess.run(
            ["chronyc", "tracking"], capture_output=True, text=True, timeout=5
        )
        if result.returncode == 0:
            for line in result.stdout.split("\n"):
                if "Leap status" in line and "normal" in line.lower():
                    synchronized = True
                    break
    except (subprocess.CalledProcessError, FileNotFoundError, TimeoutError):
        pass

    return NTPStatus(enabled=enabled, synchronized=synchronized, servers=servers)


def get_ntp_servers() -> list[str]:
    """Get configured NTP servers.

    Returns:
        List of NTP server addresses.
    """
    servers = []

    if Path(CHRONYD_CONF).exists():
        with open(CHRONYD_CONF, "r") as f:
            for line in f:
                line = line.strip()
                if line.startswith("server ") or line.startswith("pool "):
                    parts = line.split()
                    if len(parts) > 1:
                        servers.append(parts[1])

    if not servers and Path(NTPD_CONF).exists():
        with open(NTPD_CONF, "r") as f:
            for line in f:
                line = line.strip()
                if line.startswith("server ") or line.startswith("pool "):
                    parts = line.split()
                    if len(parts) > 1:
                        servers.append(parts[1])

    return servers


def set_ntp_servers(
    servers: list[str], use_pkexec: bool = True
) -> tuple[Literal["ok", "permission_denied", "pkexec_failed", "error"], str]:
    """Set NTP servers.

    Args:
        servers: List of NTP server addresses.
        use_pkexec: If True, use pkexec for privilege escalation.

    Returns:
        Tuple of (status, message).
    """
    script_path = Path(__file__).parent / "set_ntp.py"

    if not use_pkexec:
        result = subprocess.run(
            [sys.executable, str(script_path)] + servers,
            capture_output=True,
            text=True,
        )
        if result.returncode == 0 and result.stdout.strip() == "OK":
            return ("ok", "NTP servers updated successfully")
        elif result.returncode == 6:
            return ("permission_denied", "Permission denied")
        else:
            return ("error", result.stderr.strip() or "Failed to set NTP servers")

    result = subprocess.run(
        ["pkexec", sys.executable, str(script_path)] + servers,
        capture_output=True,
        text=True,
    )

    if result.returncode == 0 and result.stdout.strip() == "OK":
        return ("ok", "NTP servers updated successfully")
    elif result.returncode == 126 or result.returncode == 127:
        return ("pkexec_failed", "Authentication failed")
    elif result.returncode == 6:
        return ("permission_denied", "Permission denied")
    else:
        return ("error", result.stderr.strip() or "Failed to set NTP servers")


def enable_ntp(use_pkexec: bool = True) -> tuple[Literal["ok", "permission_denied", "pkexec_failed", "error"], str]:
    """Enable NTP synchronization.

    Args:
        use_pkexec: If True, use pkexec for privilege escalation.

    Returns:
        Tuple of (status, message).
    """
    script_path = Path(__file__).parent / "enable_ntp.py"

    if not use_pkexec:
        result = subprocess.run(
            [sys.executable, str(script_path)],
            capture_output=True,
            text=True,
        )
        if result.returncode == 0 and result.stdout.strip() == "OK":
            return ("ok", "NTP enabled successfully")
        elif result.returncode == 6:
            return ("permission_denied", "Permission denied")
        else:
            return ("error", result.stderr.strip() or "Failed to enable NTP")

    result = subprocess.run(
        ["pkexec", sys.executable, str(script_path)],
        capture_output=True,
        text=True,
    )

    if result.returncode == 0 and result.stdout.strip() == "OK":
        return ("ok", "NTP enabled successfully")
    elif result.returncode == 126 or result.returncode == 127:
        return ("pkexec_failed", "Authentication failed")
    elif result.returncode == 6:
        return ("permission_denied", "Permission denied")
    else:
        return ("error", result.stderr.strip() or "Failed to enable NTP")


def disable_ntp(use_pkexec: bool = True) -> tuple[Literal["ok", "permission_denied", "pkexec_failed", "error"], str]:
    """Disable NTP synchronization.

    Args:
        use_pkexec: If True, use pkexec for privilege escalation.

    Returns:
        Tuple of (status, message).
    """
    script_path = Path(__file__).parent / "disable_ntp.py"

    if not use_pkexec:
        result = subprocess.run(
            [sys.executable, str(script_path)],
            capture_output=True,
            text=True,
        )
        if result.returncode == 0 and result.stdout.strip() == "OK":
            return ("ok", "NTP disabled successfully")
        elif result.returncode == 6:
            return ("permission_denied", "Permission denied")
        else:
            return ("error", result.stderr.strip() or "Failed to disable NTP")

    result = subprocess.run(
        ["pkexec", sys.executable, str(script_path)],
        capture_output=True,
        text=True,
    )

    if result.returncode == 0 and result.stdout.strip() == "OK":
        return ("ok", "NTP disabled successfully")
    elif result.returncode == 126 or result.returncode == 127:
        return ("pkexec_failed", "Authentication failed")
    elif result.returncode == 6:
        return ("permission_denied", "Permission denied")
    else:
        return ("error", result.stderr.strip() or "Failed to disable NTP")


def sync_time_now(use_pkexec: bool = True) -> tuple[Literal["ok", "permission_denied", "pkexec_failed", "error"], str]:
    """Force time synchronization now.

    Args:
        use_pkexec: If True, use pkexec for privilege escalation.

    Returns:
        Tuple of (status, message).
    """
    script_path = Path(__file__).parent / "sync_time.py"

    if not use_pkexec:
        result = subprocess.run(
            [sys.executable, str(script_path)],
            capture_output=True,
            text=True,
        )
        if result.returncode == 0 and result.stdout.strip() == "OK":
            return ("ok", "Time synchronized successfully")
        elif result.returncode == 6:
            return ("permission_denied", "Permission denied")
        else:
            return ("error", result.stderr.strip() or "Failed to synchronize time")

    result = subprocess.run(
        ["pkexec", sys.executable, str(script_path)],
        capture_output=True,
        text=True,
    )

    if result.returncode == 0 and result.stdout.strip() == "OK":
        return ("ok", "Time synchronized successfully")
    elif result.returncode == 126 or result.returncode == 127:
        return ("pkexec_failed", "Authentication failed")
    elif result.returncode == 6:
        return ("permission_denied", "Permission denied")
    else:
        return ("error", result.stderr.strip() or "Failed to synchronize time")