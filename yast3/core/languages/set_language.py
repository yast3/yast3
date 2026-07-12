#!/usr/bin/env python3
"""Set language settings - requires root privileges."""

import dotenv
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
        dotenv.set_key(LOCALE_CONF_FILE, "LANG", locale_str, quote_mode='never')

        if os.path.exists(SYSCONFIG_LANGUAGE_FILE):
            dotenv.set_key(SYSCONFIG_LANGUAGE_FILE, "INSTALLED_LANGUAGES", installed_languages, quote_mode='always')

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