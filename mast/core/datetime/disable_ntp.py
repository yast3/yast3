#!/usr/bin/env python3
"""Script to disable NTP synchronization (requires root)."""

import subprocess
import sys


def main():
    try:
        subprocess.run(["systemctl", "disable", "--now", "chronyd"], check=True)
        print("OK")
    except subprocess.CalledProcessError:
        try:
            subprocess.run(["systemctl", "disable", "--now", "ntpd"], check=True)
            print("OK")
        except subprocess.CalledProcessError:
            print("Error: Failed to disable NTP service", file=sys.stderr)
            sys.exit(1)
    except PermissionError:
        print("Permission denied", file=sys.stderr)
        sys.exit(6)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()