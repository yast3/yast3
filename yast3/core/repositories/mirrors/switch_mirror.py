"""Switch mirror functionality for repositories."""

from __future__ import annotations

from typing import Literal

from yast3.core.repositories.mirrors.opensuse_mirrors import opensuse_mirrors
from yast3.core.repositories.mirrors.packman_mirrors import packman_mirrors
from yast3.core.repositories.repos import RepoEntry, load_repos, save_repo_entry


def switch_mirror(
    opensuse_mirror_url: str,
    packman_mirror_url: str,
) -> Literal["ok", "permission_denied", "pkexec_failed", "error"]:
    """Switch mirrors for openSUSE and Packman repositories.

    Args:
        opensuse_mirror_url: The new mirror URL for openSUSE repositories (with protocol).
        packman_mirror_url: The new mirror URL for Packman repository (with protocol).

    Returns:
        "ok" if successful, otherwise an error status.
    """
    opensuse_repos = ["repo-oss", "repo-non-oss", "repo-update", "repo-debug", "repo-source"]
    packman_repos = ["packman"]

    try:
        entries = load_repos()
    except PermissionError:
        return "permission_denied"

    modified_entries: list[RepoEntry] = []

    for entry in entries:
        if entry.id in opensuse_repos and entry.baseurl:
            new_baseurl = _replace_opensuse_mirror_prefix(entry.baseurl, opensuse_mirror_url)
            if new_baseurl != entry.baseurl:
                entry.baseurl = new_baseurl
                modified_entries.append(entry)
        elif entry.id in packman_repos and entry.baseurl:
            new_baseurl = _replace_packman_mirror_prefix(entry.baseurl, packman_mirror_url)
            if new_baseurl != entry.baseurl:
                entry.baseurl = new_baseurl
                modified_entries.append(entry)

    if not modified_entries:
        return "ok"

    success_count = 0
    for entry in modified_entries:
        result = save_repo_entry(entry)
        if result == "ok":
            success_count += 1
        elif result in ("permission_denied", "pkexec_failed"):
            return result

    return "ok" if success_count == len(modified_entries) else "error"


def _replace_opensuse_mirror_prefix(url: str, new_prefix: str) -> str:
    """Replace the openSUSE mirror prefix in a URL with a new prefix.

    Three-tier fallback strategy:
    1. Match known openSUSE mirror patterns
    2. Search for '/opensuse/' in URL path and replace everything before it
    3. Fall back to replacing the domain with new prefix

    Args:
        url: The original repository URL.
        new_prefix: The new openSUSE mirror URL prefix (with protocol).

    Returns:
        The URL with the new mirror prefix.
    """
    url_lower = url.lower()
    patterns = []

    for mirror in opensuse_mirrors:
        for proto in mirror.protocols:
            patterns.append(f"{proto}://{mirror.url}".lower())

    for pattern in patterns:
        if url_lower.startswith(pattern):
            remainder = url[len(pattern):]
            if remainder and not remainder.startswith("/"):
                remainder = "/" + remainder
            return new_prefix.rstrip("/") + remainder

    idx = url_lower.find('/opensuse/')
    if idx != -1:
        remainder = url[idx + len('/opensuse/'):]
        return new_prefix.rstrip("/") + "/" + remainder

    parsed = url.split("/", 3)
    if len(parsed) >= 4:
        path = parsed[3]
        return new_prefix.rstrip("/") + "/" + path

    return url


def _replace_packman_mirror_prefix(url: str, new_prefix: str) -> str:
    """Replace the Packman mirror prefix in a URL with a new prefix.

    Three-tier fallback strategy:
    1. Match known Packman mirror patterns
    2. Search for '/packman/' in URL path and replace everything before it
    3. Fall back to replacing the domain with new prefix

    Args:
        url: The original repository URL.
        new_prefix: The new Packman mirror URL prefix (with protocol).

    Returns:
        The URL with the new mirror prefix.
    """
    url_lower = url.lower()
    patterns = []

    for mirror in packman_mirrors:
        for proto in mirror.protocols:
            patterns.append(f"{proto}://{mirror.url}".lower())

    for pattern in patterns:
        if url_lower.startswith(pattern):
            remainder = url[len(pattern):]
            if remainder and not remainder.startswith("/"):
                remainder = "/" + remainder
            return new_prefix.rstrip("/") + remainder

    idx = url_lower.find('/packman/')
    if idx != -1:
        remainder = url[idx + len('/packman/'):]
        return new_prefix.rstrip("/") + "/" + remainder

    parsed = url.split("/", 3)
    if len(parsed) >= 4:
        path = parsed[3]
        return new_prefix.rstrip("/") + "/" + path

    return url