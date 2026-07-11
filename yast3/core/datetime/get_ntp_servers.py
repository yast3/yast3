#!/usr/bin/env python3
"""Script to read NTP servers from chrony configuration files."""

import sys
from pathlib import Path

CHRONYD_CONF = "/etc/chrony.conf"
CHRONYD_D_DIR = "/etc/chrony.d"
NTPD_CONF = "/etc/ntp.conf"


def read_servers_from_file(filepath):
    """Read NTP servers from a configuration file."""
    servers = []
    if Path(filepath).exists():
        with open(filepath, "r") as f:
            for line in f:
                line = line.strip()
                if line.startswith("server ") or line.startswith("pool "):
                    parts = line.split()
                    if len(parts) > 1:
                        servers.append(parts[1])
    return servers


def main():
    servers = []

    servers.extend(read_servers_from_file(CHRONYD_CONF))

    chronyd_d = Path(CHRONYD_D_DIR)
    if chronyd_d.exists() and chronyd_d.is_dir():
        for conf_file in sorted(chronyd_d.glob("*.conf")):
            servers.extend(read_servers_from_file(str(conf_file)))

    if not servers:
        servers.extend(read_servers_from_file(NTPD_CONF))

    print(";".join(servers))


if __name__ == "__main__":
    main()