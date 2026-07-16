"""Locale management using zypper commands."""

from __future__ import annotations

import subprocess
from dataclasses import dataclass
from typing import Literal

from .languages import _get_language_name


@dataclass
class LocaleItem:
    code: str
    name: str
    installed: bool


_installed_cache: set[str] | None = None
_all_locales_cache: list[str] | None = None


def _read_all_locales() -> list[str]:
    """Read all available locales using 'localectl list-locales'."""
    global _all_locales_cache
    if _all_locales_cache is not None:
        return _all_locales_cache
    
    all_locales = []
    try:
        result = subprocess.run(
            ["localectl", "list-locales"],
            capture_output=True,
            text=True,
            timeout=30,
        )
        if result.returncode == 0:
            for line in result.stdout.strip().split("\n"):
                code = line.strip()
                if not code:
                    continue
                if code in ("C", "POSIX"):
                    continue
                
                suffix_pos = code.find(".")
                if suffix_pos == -1:
                    suffix_pos = code.find("@")
                if suffix_pos != -1:
                    code = code[:suffix_pos]
                
                all_locales.append(code)
    except (FileNotFoundError, TimeoutError):
        pass
    
    _all_locales_cache = sorted(set(all_locales))
    return _all_locales_cache


def _read_installed_languages() -> set[str]:
    """Read installed languages using 'zypper --no-refresh --non-interactive locales'."""
    global _installed_cache
    if _installed_cache is not None:
        return _installed_cache
    
    installed = set()
    try:
        result = subprocess.run(
            ["zypper", "--no-refresh", "--non-interactive", "locales"],
            capture_output=True,
            text=True,
            timeout=30,
        )
        if result.returncode == 0:
            for line in result.stdout.strip().split("\n"):
                if "|" in line and not line.startswith("---"):
                    parts = line.split("|")
                    if len(parts) >= 1:
                        code = parts[0].strip()
                        if code and code != "Code":
                            installed.add(code)
    except (FileNotFoundError, TimeoutError):
        pass
    
    _installed_cache = installed
    return installed


def _invalidate_cache() -> None:
    """Invalidate the installed languages cache."""
    global _installed_cache, _all_locales_cache
    _installed_cache = None
    _all_locales_cache = None


def refresh_locale_cache() -> None:
    """Refresh the locale cache by invalidating it."""
    _invalidate_cache()


def _is_locale_installed(locale_code: str, installed_codes: set[str]) -> bool:
    """Check if a locale is installed using exact matching."""
    return locale_code in installed_codes


def get_all_locales() -> list[LocaleItem]:
    """Get all available locales from localectl."""
    installed_codes = _read_installed_languages()
    all_codes = _read_all_locales()
    locales = [
        LocaleItem(code=code, name=_get_language_name(code), installed=_is_locale_installed(code, installed_codes))
        for code in all_codes
    ]
    return sorted(locales, key=lambda x: (not x.installed, x.name))


def get_installed_locales() -> list[LocaleItem]:
    """Get installed locales."""
    installed_codes = _read_installed_languages()
    all_codes = _read_all_locales()
    return [
        LocaleItem(code=code, name=_get_language_name(code), installed=True)
        for code in all_codes
        if _is_locale_installed(code, installed_codes)
    ]


def build_locale_install_command(locale_code: str) -> list[str]:
    """Build command for installing a locale."""
    return ["pkexec", "zypper", "--no-refresh", "--non-interactive", "addlocale", locale_code]


def build_locale_remove_command(locale_code: str) -> list[str]:
    """Build command for removing a locale."""
    return ["pkexec", "zypper", "--no-refresh", "--non-interactive", "removelocale", locale_code]


def install_locale(locale_code: str) -> tuple[Literal["ok", "permission_denied", "pkexec_failed", "error"], str]:
    """Install a locale using 'pkexec zypper addlocale'."""
    try:
        result = subprocess.run(
            build_locale_install_command(locale_code),
            capture_output=True,
            text=True,
            timeout=120,
        )
        
        if result.returncode == 0:
            _invalidate_cache()
            return ("ok", f"Locale '{locale_code}' installed successfully")
        elif result.returncode == 126 or result.returncode == 127:
            return ("pkexec_failed", "Authentication failed")
        else:
            stderr = result.stderr.strip()
            return ("error", stderr if stderr else f"Failed to install locale '{locale_code}'")
    except FileNotFoundError:
        return ("error", "pkexec or zypper not found")
    except TimeoutError:
        return ("error", "Operation timed out")


def uninstall_locale(locale_code: str) -> tuple[Literal["ok", "permission_denied", "pkexec_failed", "error"], str]:
    """Uninstall a locale using 'pkexec zypper removelocale'."""
    try:
        result = subprocess.run(
            build_locale_remove_command(locale_code),
            capture_output=True,
            text=True,
            timeout=120,
        )
        
        if result.returncode == 0:
            _invalidate_cache()
            return ("ok", f"Locale '{locale_code}' uninstalled successfully")
        elif result.returncode == 126 or result.returncode == 127:
            return ("pkexec_failed", "Authentication failed")
        else:
            stderr = result.stderr.strip()
            return ("error", stderr if stderr else f"Failed to uninstall locale '{locale_code}'")
    except FileNotFoundError:
        return ("error", "pkexec or zypper not found")
    except TimeoutError:
        return ("error", "Operation timed out")