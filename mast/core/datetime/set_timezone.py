#!/usr/bin/env python3
"""Script to set timezone (requires root)."""

import sys
from pathlib import Path

TIMEZONE_FILE = "/etc/timezone"
LOCALTIME_LINK = "/etc/localtime"
TIMEZONE_DIR = "/usr/share/zoneinfo"


def main():
    if len(sys.argv) != 2:
        print("Usage: set_timezone.py <timezone>")
        sys.exit(1)

    timezone = sys.argv[1]
    tz_path = Path(TIMEZONE_DIR) / timezone

    if not tz_path.exists():
        print(f"Error: Timezone '{timezone}' not found", file=sys.stderr)
        sys.exit(1)

    try:
        with open(TIMEZONE_FILE, "w") as f:
            f.write(timezone + "\n")

        if Path(LOCALTIME_LINK).exists():
            Path(LOCALTIME_LINK).unlink()
        Path(LOCALTIME_LINK).symlink_to(tz_path)

        print("OK")
    except PermissionError:
        print("Permission denied", file=sys.stderr)
        sys.exit(6)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()