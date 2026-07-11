#!/usr/bin/env python3
"""Script to force time synchronization now (requires root)."""

import subprocess
import sys


def main():
    try:
        subprocess.run(["chronyc", "makestep"], check=True, capture_output=True)
        print("OK")
    except subprocess.CalledProcessError:
        try:
            subprocess.run(["ntpd", "-q"], check=True, capture_output=True)
            print("OK")
        except subprocess.CalledProcessError:
            print("Error: Failed to synchronize time", file=sys.stderr)
            sys.exit(1)
    except FileNotFoundError:
        print("Error: No NTP client found", file=sys.stderr)
        sys.exit(1)
    except PermissionError:
        print("Permission denied", file=sys.stderr)
        sys.exit(6)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()