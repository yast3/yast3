#!/usr/bin/env python3
"""Script to set hardware clock to UTC or LOCAL (requires root)."""

import sys
from pathlib import Path

HWCLOCK_FILE = "/etc/adjtime"


def main():
    if len(sys.argv) != 2:
        print("Usage: set_hwclock.py <UTC|LOCAL>")
        sys.exit(1)

    mode = sys.argv[1].upper()
    if mode not in ["UTC", "LOCAL"]:
        print("Error: Mode must be UTC or LOCAL", file=sys.stderr)
        sys.exit(1)

    try:
        if Path(HWCLOCK_FILE).exists():
            with open(HWCLOCK_FILE, "r") as f:
                lines = f.readlines()
        else:
            lines = ["0.0 0 0.0\n", "0\n"]

        if len(lines) >= 3:
            lines[2] = f"{mode}\n"
        else:
            lines.append(f"{mode}\n")

        with open(HWCLOCK_FILE, "w") as f:
            f.writelines(lines)

        print("OK")
    except PermissionError:
        print("Permission denied", file=sys.stderr)
        sys.exit(6)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()