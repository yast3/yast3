#!/usr/bin/env python3
"""Set hostname - run with root privileges via pkexec."""

from __future__ import annotations

import subprocess
import sys

HOSTNAME_FILE = "/etc/hostname"
HOSTS_FILE = "/etc/hosts"


def get_current_hostname() -> str:
    with open(HOSTNAME_FILE, "r") as f:
        return f.read().strip()


def load_hosts_file() -> list[str]:
    with open(HOSTS_FILE, "r") as f:
        return f.readlines()


def find_localhost_lines(lines: list[str]) -> tuple[int | None, int | None]:
    ipv4_line = None
    ipv6_line = None

    for i, line in enumerate(lines):
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue

        parts = stripped.split()
        if not parts:
            continue

        ip = parts[0]
        if "localhost" in parts:
            if ip == "127.0.0.1":
                ipv4_line = i
            elif ip == "::1":
                ipv6_line = i

    return ipv4_line, ipv6_line


def update_hosts_with_hostname(
    lines: list[str], new_hostname: str, old_hostname: str | None = None
) -> list[str]:
    updated_lines = lines.copy()

    if old_hostname:
        for i, line in enumerate(updated_lines):
            parts = line.strip().split()
            if len(parts) > 1 and old_hostname in parts[1:]:
                new_parts = [parts[0]] + [h for h in parts[1:] if h != old_hostname]
                updated_lines[i] = " ".join(new_parts) + (
                    "\n" if line.endswith("\n") else ""
                )

    ipv4_line, ipv6_line = find_localhost_lines(updated_lines)

    if ipv4_line is not None:
        line = updated_lines[ipv4_line]
        parts = line.strip().split()
        if len(parts) > 1 and new_hostname not in parts[1:]:
            localhost_idx = parts.index("localhost")
            parts.insert(localhost_idx + 1, new_hostname)
            updated_lines[ipv4_line] = " ".join(parts) + (
                "\n" if line.endswith("\n") else ""
            )

    if ipv6_line is not None:
        line = updated_lines[ipv6_line]
        parts = line.strip().split()
        if len(parts) > 1 and new_hostname not in parts[1:]:
            localhost_idx = parts.index("localhost")
            parts.insert(localhost_idx + 1, new_hostname)
            updated_lines[ipv6_line] = " ".join(parts) + (
                "\n" if line.endswith("\n") else ""
            )

    return updated_lines


def main() -> int:
    if len(sys.argv) != 2:
        print("Usage: set_hostname.py <new_hostname>", file=sys.stderr)
        return 1

    new_hostname = sys.argv[1]

    try:
        current_hostname = get_current_hostname()
    except FileNotFoundError:
        print(f"Error: {HOSTNAME_FILE} not found", file=sys.stderr)
        return 2
    except Exception as e:
        print(f"Error reading hostname: {e}", file=sys.stderr)
        return 3

    try:
        hosts_lines = load_hosts_file()
    except FileNotFoundError:
        print(f"Error: {HOSTS_FILE} not found", file=sys.stderr)
        return 4
    except Exception as e:
        print(f"Error reading hosts file: {e}", file=sys.stderr)
        return 5

    updated_hosts_lines = update_hosts_with_hostname(
        hosts_lines, new_hostname, current_hostname
    )

    try:
        with open(HOSTS_FILE, "w") as f:
            f.writelines(updated_hosts_lines)
    except Exception as e:
        print(f"Error writing {HOSTS_FILE}: {e}", file=sys.stderr)
        return 6

    try:
        result = subprocess.run(
            ["hostnamectl", "set-hostname", new_hostname],
            capture_output=True,
            text=True,
        )
        if result.returncode != 0:
            print(f"Error running hostnamectl: {result.stderr}", file=sys.stderr)
            return 7
    except Exception as e:
        print(f"Error running hostnamectl: {e}", file=sys.stderr)
        return 8

    print("OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
