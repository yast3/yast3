"""Proxy configuration management for /etc/sysconfig/proxy."""

from __future__ import annotations

import re
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Literal

from configobj import ConfigObj  # type: ignore[import-not-found]

PROXY_CONFIG_FILE = "/etc/sysconfig/proxy"
REQUIRED_PROXY_KEYS: tuple[str, ...] = (
    "PROXY_ENABLED",
    "HTTP_PROXY",
    "HTTPS_PROXY",
    "FTP_PROXY",
    "NO_PROXY",
)


@dataclass
class ProxyConfig:
    """Represents proxy configuration values."""

    enabled: bool = False
    http_proxy: str = ""
    https_proxy: str = ""
    ftp_proxy: str = ""
    no_proxy: str = ""


def _strip_quotes(value: str) -> str:
    """Remove wrapping double quotes from a value."""
    value = value.strip()
    if len(value) >= 2 and value.startswith('"') and value.endswith('"'):
        return value[1:-1]
    return value


def _parse_bool(value: str) -> bool:
    """Parse sysconfig boolean values like yes/no, true/false, 1/0."""
    return _strip_quotes(value).strip().lower() in {"yes", "true", "1", "on"}


def _create_config_obj(file_path: str | None = None) -> ConfigObj:
    """Create a ConfigObj instance for sysconfig-style proxy files."""
    options = {
        "list_values": False,
        "write_empty_values": True,
        "interpolation": False,
        "encoding": "utf-8",
    }
    if file_path is None:
        return ConfigObj(**options)
    return ConfigObj(file_path, file_error=True, **options)


def _normalize_config_lines(lines: list[str]) -> list[str]:
    """Normalize ConfigObj output to sysconfig-style assignments."""
    normalized: list[str] = []

    for line in lines:
        stripped = line.strip()
        if not stripped or stripped.startswith("#") or stripped.startswith("["):
            normalized.append(line)
            continue

        if "=" not in line:
            normalized.append(line)
            continue

        lhs, rhs = line.split("=", 1)
        normalized.append(f"{lhs.rstrip()}={rhs.lstrip()}")

    return normalized


def _load_proxy_config_obj(file_path: str = PROXY_CONFIG_FILE) -> ConfigObj:
    """Load a proxy config file into ConfigObj, or create a new object."""
    try:
        return _create_config_obj(file_path)
    except FileNotFoundError:
        return _create_config_obj(None)


def _get_missing_proxy_keys(file_path: str = PROXY_CONFIG_FILE) -> list[str]:
    """Return missing required sysconfig keys from the proxy config file."""
    config = _load_proxy_config_obj(file_path)
    return [key for key in REQUIRED_PROXY_KEYS if key not in config]


def load_proxy_config(file_path: str = PROXY_CONFIG_FILE) -> ProxyConfig:
    """Load proxy settings from /etc/sysconfig/proxy format file."""
    config = ProxyConfig()

    proxy_data = _load_proxy_config_obj(file_path)

    if "PROXY_ENABLED" in proxy_data:
        config.enabled = _parse_bool(str(proxy_data["PROXY_ENABLED"]))
    if "HTTP_PROXY" in proxy_data:
        config.http_proxy = _strip_quotes(str(proxy_data["HTTP_PROXY"]))
    if "HTTPS_PROXY" in proxy_data:
        config.https_proxy = _strip_quotes(str(proxy_data["HTTPS_PROXY"]))
    if "FTP_PROXY" in proxy_data:
        config.ftp_proxy = _strip_quotes(str(proxy_data["FTP_PROXY"]))
    if "NO_PROXY" in proxy_data:
        config.no_proxy = _strip_quotes(str(proxy_data["NO_PROXY"]))

    return config


def _quote_value(value: str) -> str:
    """Quote values in sysconfig format."""
    escaped = value.replace("\\", "\\\\").replace('"', '\\"')
    return f'"{escaped}"'


def _split_assignment_line(line: str) -> tuple[str, str] | None:
    """Split a sysconfig assignment into lhs and rhs parts."""
    match = re.match(r"^(\s*[A-Za-z_][A-Za-z0-9_]*\s*=\s*)(.*)$", line)
    if match is None:
        return None
    return match.group(1), match.group(2)


def _extract_inline_comment_suffix(rhs: str) -> str:
    """Return the inline comment suffix, including leading whitespace."""
    in_single = False
    in_double = False
    escaped = False

    for index, ch in enumerate(rhs):
        if escaped:
            escaped = False
            continue

        if ch == "\\" and in_double:
            escaped = True
            continue

        if ch == "'" and not in_double:
            in_single = not in_single
            continue

        if ch == '"' and not in_single:
            in_double = not in_double
            continue

        if ch == "#" and not in_single and not in_double:
            start = index
            while start > 0 and rhs[start - 1] in {" ", "\t"}:
                start -= 1
            return rhs[start:]

    return ""


def _build_inline_comment_suffix_map(content: str) -> dict[str, str]:
    """Collect original inline comment suffixes keyed by assignment name."""
    suffixes: dict[str, str] = {}

    for line in content.splitlines():
        split_line = _split_assignment_line(line)
        if split_line is None:
            continue

        lhs, rhs = split_line
        key = lhs.split("=", 1)[0].strip()
        suffix = _extract_inline_comment_suffix(rhs)
        if suffix:
            suffixes[key] = suffix

    return suffixes


def _restore_inline_comment_spacing(
    original_content: str, current_content: str
) -> str:
    """Restore original inline comment spacing after ConfigObj writes a file."""
    suffixes = _build_inline_comment_suffix_map(original_content)
    restored_lines: list[str] = []

    for line in current_content.splitlines():
        split_line = _split_assignment_line(line)
        if split_line is None:
            restored_lines.append(line)
            continue

        lhs, rhs = split_line
        key = lhs.split("=", 1)[0].strip()
        suffix = suffixes.get(key)
        if suffix:
            value = rhs.split("#", 1)[0].rstrip()
            restored_lines.append(f"{lhs}{value}{suffix}")
        else:
            restored_lines.append(line)

    content = "\n".join(restored_lines)
    if not content.endswith("\n"):
        content += "\n"
    return content


def _apply_proxy_values(proxy_data: ConfigObj, config: ProxyConfig) -> None:
    """Apply proxy values to a ConfigObj object."""
    enabled = "yes" if config.enabled else "no"
    proxy_data["PROXY_ENABLED"] = _quote_value(enabled)
    proxy_data["HTTP_PROXY"] = _quote_value(config.http_proxy)
    proxy_data["HTTPS_PROXY"] = _quote_value(config.https_proxy)
    proxy_data["FTP_PROXY"] = _quote_value(config.ftp_proxy)
    proxy_data["NO_PROXY"] = _quote_value(config.no_proxy)


def _rewrite_proxy_file(proxy_data: ConfigObj, file_path: str) -> None:
    """Write proxy data and normalize assignment formatting."""
    try:
        with open(file_path, "r") as f:
            original_content = f.read()
    except FileNotFoundError:
        original_content = ""

    proxy_data.filename = file_path
    proxy_data.write()

    with open(file_path, "r") as f:
        written_content = f.read()

    content = _restore_inline_comment_spacing(original_content, written_content)
    content = "\n".join(_normalize_config_lines(content.splitlines()))
    if not content.endswith("\n"):
        content += "\n"

    with open(file_path, "w") as f:
        f.write(content)


def _write_proxy_config(config: ProxyConfig, file_path: str = PROXY_CONFIG_FILE) -> None:
    """Write proxy config to the target file."""
    proxy_data = _load_proxy_config_obj(file_path)
    _apply_proxy_values(proxy_data, config)
    _rewrite_proxy_file(proxy_data, file_path)


def save_proxy_config(
    config: ProxyConfig,
    use_pkexec: bool = True,
    file_path: str = PROXY_CONFIG_FILE,
) -> tuple[Literal["ok", "permission_denied", "pkexec_failed", "error"], str]:
    """Save proxy configuration values.

    Args:
        config: Proxy config to persist.
        use_pkexec: Use pkexec helper script for privileged write.
        file_path: Target file path. For non-default paths, write directly.

    Returns:
        Tuple of (status, message).
    """
    if not use_pkexec or file_path != PROXY_CONFIG_FILE:
        try:
            _write_proxy_config(config, file_path)
            return ("ok", "Proxy configuration updated successfully")
        except PermissionError:
            return ("permission_denied", "Permission denied")
        except Exception as e:
            return ("error", str(e) or "Failed to save proxy configuration")

    script_path = Path(__file__).parent / "set_proxy.py"
    enabled = "yes" if config.enabled else "no"

    result = subprocess.run(
        [
            "pkexec",
            sys.executable,
            str(script_path),
            "--enabled",
            enabled,
            "--http",
            config.http_proxy,
            "--https",
            config.https_proxy,
            "--ftp",
            config.ftp_proxy,
            "--no-proxy",
            config.no_proxy,
        ],
        capture_output=True,
        text=True,
    )

    if result.returncode == 0 and result.stdout.strip() == "OK":
        return ("ok", "Proxy configuration updated successfully")
    if result.returncode in (126, 127):
        return ("pkexec_failed", "Authentication failed")
    if result.returncode == 6:
        return ("permission_denied", "Permission denied")

    return (
        "error",
        result.stderr.strip() or "Failed to save proxy configuration",
    )


def ensure_proxy_config_options(
    use_pkexec: bool = True,
    file_path: str = PROXY_CONFIG_FILE,
) -> tuple[Literal["ok", "permission_denied", "pkexec_failed", "error"], str]:
    """Check /etc/sysconfig/proxy and fill missing standard options.

    Missing options are written back with default values:
    - PROXY_ENABLED="no"
    - HTTP_PROXY=""
    - HTTPS_PROXY=""
    - FTP_PROXY=""
    - NO_PROXY=""
    """
    try:
        missing_keys = _get_missing_proxy_keys(file_path)
    except PermissionError:
        return ("permission_denied", "Permission denied")
    except Exception as e:
        return ("error", str(e) or "Failed to inspect proxy configuration")

    if not missing_keys:
        return ("ok", "Proxy configuration is already complete")

    try:
        config = load_proxy_config(file_path)
    except PermissionError:
        return ("permission_denied", "Permission denied")
    except Exception as e:
        return ("error", str(e) or "Failed to load proxy configuration")

    status, message = save_proxy_config(
        config,
        use_pkexec=use_pkexec,
        file_path=file_path,
    )
    if status != "ok":
        return (status, message)

    return (
        "ok",
        "Filled missing proxy options: " + ", ".join(missing_keys),
    )
