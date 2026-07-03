"""Proxy configuration management for /etc/sysconfig/proxy."""

from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path
from typing import Literal

from configobj import ConfigObj

PROXY_CONFIG_FILE = "/etc/sysconfig/proxy"
REQUIRED_PROXY_KEYS: tuple[str, ...] = (
    "PROXY_ENABLED",
    "HTTP_PROXY",
    "HTTPS_PROXY",
    "FTP_PROXY",
    "NO_PROXY",
)


class ProxyConfig(ConfigObj):
    """Represents proxy configuration values."""

    def __init__(self) -> None:
        super().__init__(PROXY_CONFIG_FILE, file_error=True, encoding="utf-8")

    def write_pkexec(self) -> None:
        """Write the proxy configuration using pkexec for elevated privileges."""
        tmp_file = "/tmp/proxy_config_temp"
        self.filename = tmp_file
        self.write()
        self.filename = PROXY_CONFIG_FILE
        subprocess.run(
            ["pkexec", 'mv', str(tmp_file), PROXY_CONFIG_FILE],
            check=True,
        )
