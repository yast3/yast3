"""Unit tests for proxy configuration logic."""

import tempfile
import unittest
from unittest.mock import MagicMock, patch

from yast3.core.proxy import (
    ProxyConfig,
    ensure_proxy_config_options,
    load_proxy_config,
    save_proxy_config,
)


class TestLoadProxyConfig(unittest.TestCase):
    def test_load_full_proxy_config(self) -> None:
        content = """# proxy settings
PROXY_ENABLED=\"yes\"
HTTP_PROXY=\"http://127.0.0.1:3128\"
HTTPS_PROXY=\"https://127.0.0.1:3129\"
FTP_PROXY=\"ftp://127.0.0.1:2121\"
NO_PROXY=\"localhost,127.0.0.1,.local\"
"""
        with tempfile.NamedTemporaryFile("w+", delete=False) as f:
            f.write(content)
            f.flush()
            path = f.name

        config = load_proxy_config(path)

        self.assertTrue(config.enabled)
        self.assertEqual(config.http_proxy, "http://127.0.0.1:3128")
        self.assertEqual(config.https_proxy, "https://127.0.0.1:3129")
        self.assertEqual(config.ftp_proxy, "ftp://127.0.0.1:2121")
        self.assertEqual(config.no_proxy, "localhost,127.0.0.1,.local")

    def test_load_defaults_when_keys_missing(self) -> None:
        with tempfile.NamedTemporaryFile("w+", delete=False) as f:
            f.write("HTTP_PROXY=\"http://proxy:8080\"\n")
            f.flush()
            path = f.name

        config = load_proxy_config(path)

        self.assertFalse(config.enabled)
        self.assertEqual(config.http_proxy, "http://proxy:8080")
        self.assertEqual(config.https_proxy, "")
        self.assertEqual(config.ftp_proxy, "")
        self.assertEqual(config.no_proxy, "")


class TestSaveProxyConfig(unittest.TestCase):
    def test_save_proxy_config_direct_write(self) -> None:
        config = ProxyConfig(
            enabled=True,
            http_proxy="http://proxy:8080",
            https_proxy="https://proxy:8443",
            ftp_proxy="",
            no_proxy="localhost,127.0.0.1",
        )

        with tempfile.NamedTemporaryFile("r+", delete=False) as f:
            path = f.name

        status, _message = save_proxy_config(config, use_pkexec=False, file_path=path)

        self.assertEqual(status, "ok")
        with open(path, "r") as f:
            content = f.read()

        self.assertIn('PROXY_ENABLED="yes"', content)
        self.assertIn('HTTP_PROXY="http://proxy:8080"', content)
        self.assertIn('HTTPS_PROXY="https://proxy:8443"', content)
        self.assertIn('FTP_PROXY=""', content)
        self.assertIn('NO_PROXY="localhost,127.0.0.1"', content)

    @patch("yast3.core.proxy.proxy._write_proxy_config")
    def test_save_proxy_config_permission_denied(self, mock_write: MagicMock) -> None:
        mock_write.side_effect = PermissionError("denied")
        config = ProxyConfig(enabled=False)

        status, _message = save_proxy_config(config, use_pkexec=False)

        self.assertEqual(status, "permission_denied")

    @patch("yast3.core.proxy.proxy.subprocess.run")
    def test_save_proxy_config_pkexec_success(self, mock_run: MagicMock) -> None:
        mock_run.return_value.returncode = 0
        mock_run.return_value.stdout = "OK\n"
        mock_run.return_value.stderr = ""

        status, _message = save_proxy_config(ProxyConfig(enabled=True), use_pkexec=True)

        self.assertEqual(status, "ok")

    @patch("yast3.core.proxy.proxy.subprocess.run")
    def test_save_proxy_config_pkexec_auth_failed(self, mock_run: MagicMock) -> None:
        mock_run.return_value.returncode = 126
        mock_run.return_value.stdout = ""
        mock_run.return_value.stderr = "auth failed"

        status, _message = save_proxy_config(ProxyConfig(enabled=True), use_pkexec=True)

        self.assertEqual(status, "pkexec_failed")

    def test_save_proxy_config_preserves_comments(self) -> None:
        original_content = """# Global proxy settings
PROXY_ENABLED=\"no\"   # keep this comment
HTTP_PROXY=\"http://old:8080\"
# middle comment
CUSTOM_OPTION=\"custom\"
NO_PROXY=\"localhost\" # keep no_proxy comment
"""
        with tempfile.NamedTemporaryFile("w+", delete=False) as f:
            f.write(original_content)
            f.flush()
            path = f.name

        config = ProxyConfig(
            enabled=True,
            http_proxy="http://new:8080",
            https_proxy="https://new:8443",
            ftp_proxy="",
            no_proxy="127.0.0.1",
        )

        status, _message = save_proxy_config(config, use_pkexec=False, file_path=path)
        self.assertEqual(status, "ok")

        with open(path, "r") as f:
            content = f.read()

        self.assertIn("# Global proxy settings", content)
        self.assertIn("# middle comment", content)
        self.assertIn('CUSTOM_OPTION="custom"', content)
        self.assertIn('PROXY_ENABLED="yes"   # keep this comment', content)
        self.assertIn('NO_PROXY="127.0.0.1" # keep no_proxy comment', content)
        self.assertIn('HTTPS_PROXY="https://new:8443"', content)
        self.assertIn('FTP_PROXY=""', content)


class TestEnsureProxyConfigOptions(unittest.TestCase):
    def test_fills_missing_options(self) -> None:
        with tempfile.NamedTemporaryFile("w+", delete=False) as f:
            f.write('HTTP_PROXY="http://proxy:8080"\n')
            f.flush()
            path = f.name

        status, message = ensure_proxy_config_options(use_pkexec=False, file_path=path)

        self.assertEqual(status, "ok")
        self.assertIn("PROXY_ENABLED", message)
        config = load_proxy_config(path)
        self.assertFalse(config.enabled)
        self.assertEqual(config.http_proxy, "http://proxy:8080")

        with open(path, "r") as f:
            content = f.read()
        self.assertIn('PROXY_ENABLED="no"', content)
        self.assertIn('HTTPS_PROXY=""', content)
        self.assertIn('FTP_PROXY=""', content)
        self.assertIn('NO_PROXY=""', content)

    def test_when_complete_returns_already_complete(self) -> None:
        config = ProxyConfig(
            enabled=True,
            http_proxy="http://proxy:8080",
            https_proxy="https://proxy:8443",
            ftp_proxy="",
            no_proxy="localhost,127.0.0.1",
        )
        with tempfile.NamedTemporaryFile("r+", delete=False) as f:
            path = f.name
        save_proxy_config(config, use_pkexec=False, file_path=path)

        status, message = ensure_proxy_config_options(use_pkexec=False, file_path=path)

        self.assertEqual(status, "ok")
        self.assertEqual(message, "Proxy configuration is already complete")


if __name__ == "__main__":
    unittest.main()
