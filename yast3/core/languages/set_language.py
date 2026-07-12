#!/usr/bin/env python3
"""Set language settings - requires root privileges."""

import os
import subprocess
import sys

LOCALE_CONF_FILE = "/etc/locale.conf"
SYSCONFIG_LANGUAGE_FILE = "/etc/sysconfig/language"


def main() -> None:
    if len(sys.argv) < 2:
        print("Usage: set_language.py <locale_string> [installed_languages]")
        sys.exit(1)

    locale_str = sys.argv[1]
    installed_languages = sys.argv[2] if len(sys.argv) > 2 else ""

    try:
        with open(LOCALE_CONF_FILE, "w") as f:
            f.write(f"LANG={locale_str}\n")

        if os.path.exists(SYSCONFIG_LANGUAGE_FILE):
            with open(SYSCONFIG_LANGUAGE_FILE, "r") as f:
                content = f.read()

            lines = content.split("\n")
            found_installed = False
            for i, line in enumerate(lines):
                if line.startswith("INSTALLED_LANGUAGES="):
                    lines[i] = f'INSTALLED_LANGUAGES="{installed_languages}"'
                    found_installed = True
                    break
            if not found_installed and installed_languages:
                lines.append(f'INSTALLED_LANGUAGES="{installed_languages}"')

            with open(SYSCONFIG_LANGUAGE_FILE, "w") as f:
                f.write("\n".join(lines))

        result = subprocess.run(
            ["localectl", "set-locale", f"LANG={locale_str}"],
            capture_output=True,
            text=True,
        )
        if result.returncode != 0:
            print(f"ERROR: {result.stderr}")
            sys.exit(1)

        print("OK")
    except Exception as e:
        print(f"ERROR: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()