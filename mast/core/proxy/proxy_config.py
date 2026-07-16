import dotenv
import subprocess
import sys

PROXY_CONFIG_FILE = "/etc/sysconfig/proxy"

class ProxyConfig:
    """Represents proxy configuration values."""

    PROXY_ENABLED: str
    HTTP_PROXY: str
    HTTPS_PROXY: str
    FTP_PROXY: str
    SOCKS_PROXY: str
    NO_PROXY: str

    def __init__(self) -> None:
        self.reload()

    def reload(self) -> None:
        """Reload the proxy configuration from the file."""
        config = dotenv.dotenv_values(PROXY_CONFIG_FILE)
        self.PROXY_ENABLED = config["PROXY_ENABLED"] or 'no'
        self.HTTP_PROXY = config["HTTP_PROXY"] or ''
        self.HTTPS_PROXY = config["HTTPS_PROXY"] or ''
        self.FTP_PROXY = config["FTP_PROXY"] or ''
        self.SOCKS_PROXY = config["SOCKS_PROXY"] or ''
        self.NO_PROXY = config["NO_PROXY"] or 'localhost,127.0.0.1'

    def write(self) -> None:
        dotenv.set_key(PROXY_CONFIG_FILE, "PROXY_ENABLED", self.PROXY_ENABLED, quote_mode='always')
        dotenv.set_key(PROXY_CONFIG_FILE, "HTTP_PROXY", self.HTTP_PROXY, quote_mode='always')
        dotenv.set_key(PROXY_CONFIG_FILE, "HTTPS_PROXY", self.HTTPS_PROXY, quote_mode='always')
        dotenv.set_key(PROXY_CONFIG_FILE, "FTP_PROXY", self.FTP_PROXY, quote_mode='always')
        dotenv.set_key(PROXY_CONFIG_FILE, "SOCKS_PROXY", self.SOCKS_PROXY, quote_mode='always')
        dotenv.set_key(PROXY_CONFIG_FILE, "NO_PROXY", self.NO_PROXY, quote_mode='always')

    def write_pkexec(self) -> None:
        """Write the proxy configuration to the file using pkexec."""


        result = subprocess.run(
            ["pkexec", '--keep-cwd', sys.executable, '-m', 'mast.core.proxy',
             '--enabled', self.PROXY_ENABLED,
             '--http', self.HTTP_PROXY,
             '--https', self.HTTPS_PROXY,
             '--ftp', self.FTP_PROXY,
             '--socks', self.SOCKS_PROXY,
             '--noproxy', self.NO_PROXY],
            capture_output=True,
            text=True,
        )

        if result.returncode != 0:
            raise RuntimeError(f"Failed to write proxy configuration: {result.stderr.strip()}")