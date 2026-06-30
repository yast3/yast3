"""Switch mirror functionality for repositories."""

from __future__ import annotations

from typing import Literal

from yast3.core.repositories.mirrors.opensuse import opensuse_mirrors
from yast3.core.repositories.mirrors.packman import packman_mirrors
from yast3.core.repositories.repos import RepoEntry, load_repos, save_repo_entry


def switch_mirror(
    opensuse_mirror_url: str,
    packman_mirror_url: str,
) -> Literal["ok", "permission_denied", "pkexec_failed", "error"]:
    """Switch mirrors for openSUSE and Packman repositories.

    Args:
        opensuse_mirror_url: The new mirror URL for openSUSE repositories.
        packman_mirror_url: The new mirror URL for Packman repository.

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
            new_baseurl = _replace_mirror_prefix(entry.baseurl, opensuse_mirror_url)
            if new_baseurl != entry.baseurl:
                entry.baseurl = new_baseurl
                modified_entries.append(entry)
        elif entry.id in packman_repos and entry.baseurl:
            new_baseurl = _replace_mirror_prefix(entry.baseurl, packman_mirror_url)
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


def _replace_mirror_prefix(url: str, new_prefix: str) -> str:
    """Replace the mirror prefix in a URL with a new prefix.

    Args:
        url: The original repository URL.
        new_prefix: The new mirror URL prefix.

    Returns:
        The URL with the new mirror prefix.
    """
    url_lower = url.lower()
    patterns = []

    # Build patterns from mirror lists
    for mirror in opensuse_mirrors:
        patterns.append(mirror.url.lower())
        if mirror.url.startswith("https://"):
            patterns.append(mirror.url.replace("https://", "http://", 1).lower())

    for mirror in packman_mirrors:
        patterns.append(mirror.url.lower())
        if mirror.url.startswith("https://"):
            patterns.append(mirror.url.replace("https://", "http://", 1).lower())

    # Add official download.opensuse.org prefixes
    official_prefixes = [
        "https://download.opensuse.org/",
        "http://download.opensuse.org/",
        "https://download.opensuse.org",
        "http://download.opensuse.org",
    ]
    patterns.extend([p.lower() for p in official_prefixes])

    for pattern in patterns:
        if url_lower.startswith(pattern):
            remainder = url[len(pattern):]
            if remainder and not remainder.startswith("/"):
                remainder = "/" + remainder
            return new_prefix.rstrip("/") + remainder

    # Fallback: extract path after the domain
    parsed = url.split("/", 3)
    if len(parsed) >= 4:
        path = parsed[3]
        return new_prefix.rstrip("/") + "/" + path

    return url