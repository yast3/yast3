"""Unit tests for proxy configuration logic."""

import tempfile
import unittest
from unittest.mock import MagicMock, patch

from mast.core.proxy import ProxyConfig


class TestProxyConfig(unittest.TestCase):
    def test_load_socks_proxy_value(self) -> None:
        content = """PROXY_ENABLED=\"yes\"
HTTP_PROXY=\"http://127.0.0.1:3128\"
HTTPS_PROXY=\"https://127.0.0.1:3129\"
FTP_PROXY=\"ftp://127.0.0.1:2121\"
SOCKS_PROXY=\"socks://127.0.0.1:1080\"
NO_PROXY=\"localhost,127.0.0.1\"
"""
        with tempfile.NamedTemporaryFile("w+", delete=False) as f:
            f.write(content)
            f.flush()
            path = f.name

        with patch("mast.core.proxy.proxy_config.PROXY_CONFIG_FILE", path):
            config = ProxyConfig()

        self.assertEqual(config.SOCKS_PROXY, "socks://127.0.0.1:1080")

    def test_save_socks_proxy_value(self) -> None:
        content = """# proxy settings
PROXY_ENABLED=\"no\"
HTTP_PROXY=\"\"
HTTPS_PROXY=\"\"
FTP_PROXY=\"\"
SOCKS_PROXY=\"\"
NO_PROXY=\"localhost\"
"""
        with tempfile.NamedTemporaryFile("w+", delete=False) as f:
            f.write(content)
            f.flush()
            path = f.name

        with patch("mast.core.proxy.proxy_config.PROXY_CONFIG_FILE", path):
            config = ProxyConfig()
            config.SOCKS_PROXY = "socks://10.0.0.1:1080"
            config.write()

        with open(path, "r") as f:
            updated = f.read()

        self.assertIn('SOCKS_PROXY = socks://10.0.0.1:1080', updated)

    @patch("mast.core.proxy.proxy_config.subprocess.run")
    def test_write_pkexec_calls_mv(self, mock_run: MagicMock) -> None:
        with tempfile.NamedTemporaryFile("w+", delete=False) as f:
            f.write('PROXY_ENABLED="no"\nHTTP_PROXY=""\nHTTPS_PROXY=""\nFTP_PROXY=""\nSOCKS_PROXY=""\nNO_PROXY="localhost"\n')
            f.flush()
            path = f.name

        with patch("mast.core.proxy.proxy_config.PROXY_CONFIG_FILE", path):
            config = ProxyConfig()
            config.write_pkexec()

        mock_run.assert_called_once()
        args, kwargs = mock_run.call_args
        self.assertEqual(args[0][0], "pkexec")
        self.assertEqual(args[0][1], "mv")
        self.assertEqual(args[0][3], path)
        self.assertTrue(kwargs.get("check", False))


if __name__ == "__main__":
    unittest.main()
