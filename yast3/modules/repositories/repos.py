"""Repository file reading and writing logic."""

from __future__ import annotations

import os
import re
import subprocess
import tempfile
from dataclasses import dataclass, field
from typing import Literal

REPOS_DIR = "/etc/zypp/repos.d"


@dataclass
class RepoEntry:
    """Represents a single repository entry."""
    name: str
    filename: str
    enabled: bool = True
    autorefresh: bool = True
    baseurl: str = ""
    mirrorlist: str = ""
    type: str = "rpm-md"
    gpgcheck: bool = True
    gpgkey: str = ""
    priority: int = 99
    keep_packages: bool = False
    other_options: dict = field(default_factory=dict)

    @property
    def url(self) -> str:
        """Return the URL (baseurl or mirrorlist)."""
        return self.baseurl or self.mirrorlist


def parse_repo_file(filepath: str) -> list[RepoEntry]:
    """Parse a single .repo file."""
    entries: list[RepoEntry] = []
    
    try:
        with open(filepath, "r") as f:
            content = f.read()
    except Exception:
        return entries
    
    # Split by [section] headers
    sections = re.split(r'\n\[', content)
    
    for section in sections:
        if not section.strip():
            continue
        
        # Find section name (first line before newline)
        lines = section.split('\n', 1)
        name = lines[0].strip().strip('[]')
        body = lines[1] if len(lines) > 1 else ''
        
        if not name:
            continue
        
        entry = RepoEntry(name=name, filename=os.path.basename(filepath))
        
        # Parse key=value pairs
        for line in body.split('\n'):
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            
            if '=' in line:
                key, value = line.split('=', 1)
                key = key.strip().lower()
                value = value.strip()
                
                if key == 'enabled':
                    entry.enabled = value.lower() in ('1', 'true', 'yes')
                elif key == 'autorefresh':
                    entry.autorefresh = value.lower() in ('1', 'true', 'yes')
                elif key == 'baseurl':
                    entry.baseurl = value
                elif key == 'mirrorlist':
                    entry.mirrorlist = value
                elif key == 'type':
                    entry.type = value
                elif key == 'gpgcheck':
                    entry.gpgcheck = value.lower() in ('1', 'true', 'yes')
                elif key == 'gpgkey':
                    entry.gpgkey = value
                elif key == 'priority':
                    try:
                        entry.priority = int(value)
                    except ValueError:
                        pass
                elif key == 'keep_packages':
                    entry.keep_packages = value.lower() in ('1', 'true', 'yes')
                else:
                    entry.other_options[key] = value
        
        entries.append(entry)
    
    return entries


def load_repos() -> list[RepoEntry]:
    """Load all repositories from /etc/zypp/repos.d/*.repo files."""
    entries: list[RepoEntry] = []
    
    if not os.path.isdir(REPOS_DIR):
        return entries
    
    try:
        for filename in os.listdir(REPOS_DIR):
            if filename.endswith('.repo'):
                filepath = os.path.join(REPOS_DIR, filename)
                if os.path.isfile(filepath):
                    entries.extend(parse_repo_file(filepath))
    except PermissionError:
        raise PermissionError("Cannot read repository directory")
    
    # Sort by name
    entries.sort(key=lambda e: e.name)
    return entries


def save_repo_entry(entry: RepoEntry, use_pkexec: bool = True) -> Literal["ok", "permission_denied", "pkexec_failed", "error"]:
    """Save a single repository entry to its .repo file."""
    filepath = os.path.join(REPOS_DIR, entry.filename)
    
    # Check if we need to read existing content
    existing_entries = []
    if os.path.exists(filepath):
        existing_entries = parse_repo_file(filepath)
    
    # Replace or add this entry
    found = False
    for i, e in enumerate(existing_entries):
        if e.name == entry.name:
            existing_entries[i] = entry
            found = True
            break
    
    if not found:
        existing_entries.append(entry)
    
    # Generate content
    lines = []
    for e in existing_entries:
        lines.append(f"[{e.name}]")
        lines.append(f"name={e.name}")
        lines.append(f"enabled={'1' if e.enabled else '0'}")
        lines.append(f"autorefresh={'1' if e.autorefresh else '0'}")
        if e.baseurl:
            lines.append(f"baseurl={e.baseurl}")
        if e.mirrorlist:
            lines.append(f"mirrorlist={e.mirrorlist}")
        lines.append(f"type={e.type}")
        lines.append(f"gpgcheck={'1' if e.gpgcheck else '0'}")
        if e.gpgkey:
            lines.append(f"gpgkey={e.gpgkey}")
        lines.append(f"priority={e.priority}")
        lines.append(f"keep_packages={'1' if e.keep_packages else '0'}")
        for key, value in e.other_options.items():
            lines.append(f"{key}={value}")
        lines.append("")  # Empty line between sections
    
    content = '\n'.join(lines).rstrip('\n') + '\n'
    
    # Try direct write first
    try:
        with open(filepath, "w") as f:
            f.write(content)
        return "ok"
    except PermissionError:
        if not use_pkexec:
            return "permission_denied"
    except Exception:
        return "error"
    
    # Use pkexec to get root permission
    try:
        with tempfile.NamedTemporaryFile(mode="w", suffix=".repo", delete=False) as tmp:
            tmp.write(content)
            tmp_path = tmp.name
        
        result = subprocess.run(
            ["pkexec", "cp", tmp_path, filepath],
            capture_output=True,
            text=True,
        )
        
        subprocess.run(["rm", "-f", tmp_path], capture_output=True)
        
        if result.returncode == 0:
            return "ok"
        else:
            return "pkexec_failed"
    except Exception:
        return "error"


def delete_repo_entry(entry: RepoEntry, use_pkexec: bool = True) -> Literal["ok", "permission_denied", "pkexec_failed", "error"]:
    """Delete a repository entry from its .repo file."""
    filepath = os.path.join(REPOS_DIR, entry.filename)
    
    if not os.path.exists(filepath):
        return "ok"
    
    existing_entries = parse_repo_file(filepath)
    remaining_entries = [e for e in existing_entries if e.name != entry.name]
    
    # If no entries remain, delete the file
    if not remaining_entries:
        try:
            os.remove(filepath)
            return "ok"
        except PermissionError:
            if not use_pkexec:
                return "permission_denied"
        except Exception:
            return "error"
        
        # Use pkexec
        try:
            result = subprocess.run(
                ["pkexec", "rm", filepath],
                capture_output=True,
                text=True,
            )
            if result.returncode == 0:
                return "ok"
            else:
                return "pkexec_failed"
        except Exception:
            return "error"
    
    # Otherwise, write remaining entries
    lines = []
    for e in remaining_entries:
        lines.append(f"[{e.name}]")
        lines.append(f"name={e.name}")
        lines.append(f"enabled={'1' if e.enabled else '0'}")
        lines.append(f"autorefresh={'1' if e.autorefresh else '0'}")
        if e.baseurl:
            lines.append(f"baseurl={e.baseurl}")
        if e.mirrorlist:
            lines.append(f"mirrorlist={e.mirrorlist}")
        lines.append(f"type={e.type}")
        lines.append(f"gpgcheck={'1' if e.gpgcheck else '0'}")
        if e.gpgkey:
            lines.append(f"gpgkey={e.gpgkey}")
        lines.append(f"priority={e.priority}")
        lines.append(f"keep_packages={'1' if e.keep_packages else '0'}")
        for key, value in e.other_options.items():
            lines.append(f"{key}={value}")
        lines.append("")
    
    content = '\n'.join(lines).rstrip('\n') + '\n'
    
    try:
        with open(filepath, "w") as f:
            f.write(content)
        return "ok"
    except PermissionError:
        if not use_pkexec:
            return "permission_denied"
    except Exception:
        return "error"
    
    try:
        with tempfile.NamedTemporaryFile(mode="w", suffix=".repo", delete=False) as tmp:
            tmp.write(content)
            tmp_path = tmp.name
        
        result = subprocess.run(
            ["pkexec", "cp", tmp_path, filepath],
            capture_output=True,
            text=True,
        )
        
        subprocess.run(["rm", "-f", tmp_path], capture_output=True)
        
        if result.returncode == 0:
            return "ok"
        else:
            return "pkexec_failed"
    except Exception:
        return "error"