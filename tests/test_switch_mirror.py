"""Unit tests for the switch_mirror module."""

import unittest
from unittest.mock import MagicMock, patch

from yast3.core.repositories.switch_mirror import (
    _replace_opensuse_mirror_prefix,
    _replace_packman_mirror_prefix,
    _status_to_exit_code,
    switch_mirror_pkexec,
)


class TestReplaceOpensuseMirrorPrefix(unittest.TestCase):
    """Tests for _replace_opensuse_mirror_prefix function."""

    def test_known_mirror_http(self) -> None:
        """Should replace known openSUSE mirror with http protocol."""
        url = "http://download.opensuse.org/distribution/leap/15.6/repo/oss/"
        new_prefix = "https://mirrors.tuna.tsinghua.edu.cn/opensuse/"
        result = _replace_opensuse_mirror_prefix(url, new_prefix)
        self.assertEqual(result, "https://mirrors.tuna.tsinghua.edu.cn/opensuse/distribution/leap/15.6/repo/oss/")

    def test_known_mirror_https(self) -> None:
        """Should replace known openSUSE mirror with https protocol."""
        url = "https://ftp.gwdg.de/pub/opensuse/update/leap/15.6/"
        new_prefix = "http://mirrors.aliyun.com/opensuse/"
        result = _replace_opensuse_mirror_prefix(url, new_prefix)
        self.assertEqual(result, "http://mirrors.aliyun.com/opensuse/update/leap/15.6/")

    def test_known_mirror_ftp(self) -> None:
        """Should replace known openSUSE mirror with ftp protocol."""
        url = "ftp://ftp.linux.cz/pub/linux/opensuse/distribution/leap/15.6/"
        new_prefix = "https://mirrors.tuna.tsinghua.edu.cn/opensuse/"
        result = _replace_opensuse_mirror_prefix(url, new_prefix)
        self.assertEqual(result, "https://mirrors.tuna.tsinghua.edu.cn/opensuse/distribution/leap/15.6/")

    def test_opensuse_path_fallback(self) -> None:
        """Should fallback to /opensuse/ path match for unknown mirror."""
        url = "http://unknown.example.com/linux/opensuse/distribution/leap/15.6/repo/oss/"
        new_prefix = "https://mirrors.tuna.tsinghua.edu.cn/opensuse/"
        result = _replace_opensuse_mirror_prefix(url, new_prefix)
        self.assertEqual(result, "https://mirrors.tuna.tsinghua.edu.cn/opensuse/distribution/leap/15.6/repo/oss/")

    def test_domain_fallback(self) -> None:
        """Should fallback to domain replacement when no known mirror or /opensuse/ found."""
        url = "http://unknown.example.com/suse/repos/oss/"
        new_prefix = "https://mirrors.tuna.tsinghua.edu.cn/opensuse/"
        result = _replace_opensuse_mirror_prefix(url, new_prefix)
        self.assertEqual(result, "https://mirrors.tuna.tsinghua.edu.cn/opensuse/suse/repos/oss/")

    def test_case_insensitive_protocol(self) -> None:
        """Should handle uppercase protocol in URL."""
        url = "HTTP://download.opensuse.org/distribution/leap/15.6/"
        new_prefix = "https://mirrors.tuna.tsinghua.edu.cn/opensuse/"
        result = _replace_opensuse_mirror_prefix(url, new_prefix)
        self.assertEqual(result, "https://mirrors.tuna.tsinghua.edu.cn/opensuse/distribution/leap/15.6/")

    def test_case_insensitive_host(self) -> None:
        """Should handle mixed-case hostname in URL."""
        url = "https://Download.OpenSUSE.Org/distribution/leap/15.6/"
        new_prefix = "https://mirrors.tuna.tsinghua.edu.cn/opensuse/"
        result = _replace_opensuse_mirror_prefix(url, new_prefix)
        self.assertEqual(result, "https://mirrors.tuna.tsinghua.edu.cn/opensuse/distribution/leap/15.6/")

    def test_new_prefix_with_trailing_slash(self) -> None:
        """Should handle new_prefix with trailing slash."""
        url = "http://download.opensuse.org/distribution/leap/15.6/"
        new_prefix = "https://mirrors.tuna.tsinghua.edu.cn/opensuse/"
        result = _replace_opensuse_mirror_prefix(url, new_prefix)
        self.assertEqual(result, "https://mirrors.tuna.tsinghua.edu.cn/opensuse/distribution/leap/15.6/")

    def test_new_prefix_without_trailing_slash(self) -> None:
        """Should handle new_prefix without trailing slash."""
        url = "http://download.opensuse.org/distribution/leap/15.6/"
        new_prefix = "https://mirrors.tuna.tsinghua.edu.cn/opensuse"
        result = _replace_opensuse_mirror_prefix(url, new_prefix)
        self.assertEqual(result, "https://mirrors.tuna.tsinghua.edu.cn/opensuse/distribution/leap/15.6/")

    def test_no_leading_slash_in_remainder(self) -> None:
        """Should handle remainder without leading slash when known pattern doesn't match."""
        url = "http://download.opensuse.orgdistribution/leap/15.6/"
        new_prefix = "https://mirrors.tuna.tsinghua.edu.cn/opensuse/"
        result = _replace_opensuse_mirror_prefix(url, new_prefix)
        self.assertEqual(result, "https://mirrors.tuna.tsinghua.edu.cn/opensuse/leap/15.6/")

    def test_does_not_match_packman_mirror(self) -> None:
        """Should NOT match packman mirror patterns directly, uses domain fallback."""
        url = "http://ftp.fau.de/packman/suse/openSUSE_Tumbleweed/"
        new_prefix = "https://mirrors.tuna.tsinghua.edu.cn/opensuse/"
        result = _replace_opensuse_mirror_prefix(url, new_prefix)
        self.assertEqual(result, "https://mirrors.tuna.tsinghua.edu.cn/opensuse/packman/suse/openSUSE_Tumbleweed/")


class TestReplacePackmanMirrorPrefix(unittest.TestCase):
    """Tests for _replace_packman_mirror_prefix function."""

    def test_known_mirror_http(self) -> None:
        """Should replace known Packman mirror with http protocol."""
        url = "http://ftp.fau.de/packman/suse/openSUSE_Tumbleweed/"
        new_prefix = "https://mirrors.aliyun.com/packman/"
        result = _replace_packman_mirror_prefix(url, new_prefix)
        self.assertEqual(result, "https://mirrors.aliyun.com/packman/suse/openSUSE_Tumbleweed/")

    def test_known_mirror_https(self) -> None:
        """Should replace known Packman mirror with https protocol."""
        url = "https://ftp.gwdg.de/pub/linux/misc/packman/suse/openSUSE_Leap_15.6/"
        new_prefix = "http://mirror.karneval.cz/pub/linux/packman/"
        result = _replace_packman_mirror_prefix(url, new_prefix)
        self.assertEqual(result, "http://mirror.karneval.cz/pub/linux/packman/suse/openSUSE_Leap_15.6/")

    def test_known_mirror_ftp(self) -> None:
        """Should replace known Packman mirror with ftp protocol."""
        url = "ftp://ftp.halifax.rwth-aachen.de/packman/suse/openSUSE_Tumbleweed/"
        new_prefix = "https://mirrors.aliyun.com/packman/"
        result = _replace_packman_mirror_prefix(url, new_prefix)
        self.assertEqual(result, "https://mirrors.aliyun.com/packman/suse/openSUSE_Tumbleweed/")

    def test_packman_path_fallback(self) -> None:
        """Should fallback to /packman/ path match for unknown mirror."""
        url = "http://unknown.example.com/linux/packman/suse/openSUSE_Tumbleweed/"
        new_prefix = "https://mirrors.aliyun.com/packman/"
        result = _replace_packman_mirror_prefix(url, new_prefix)
        self.assertEqual(result, "https://mirrors.aliyun.com/packman/suse/openSUSE_Tumbleweed/")

    def test_domain_fallback(self) -> None:
        """Should fallback to domain replacement when no known mirror or /packman/ found."""
        url = "http://unknown.example.com/repo/suse/Tumbleweed/"
        new_prefix = "https://mirrors.aliyun.com/packman/"
        result = _replace_packman_mirror_prefix(url, new_prefix)
        self.assertEqual(result, "https://mirrors.aliyun.com/packman/repo/suse/Tumbleweed/")

    def test_case_insensitive_protocol(self) -> None:
        """Should handle uppercase protocol in URL."""
        url = "HTTP://ftp.fau.de/packman/suse/openSUSE_Tumbleweed/"
        new_prefix = "https://mirrors.aliyun.com/packman/"
        result = _replace_packman_mirror_prefix(url, new_prefix)
        self.assertEqual(result, "https://mirrors.aliyun.com/packman/suse/openSUSE_Tumbleweed/")

    def test_case_insensitive_host(self) -> None:
        """Should handle mixed-case hostname in URL."""
        url = "https://FTP.FAU.DE/packman/suse/openSUSE_Tumbleweed/"
        new_prefix = "https://mirrors.aliyun.com/packman/"
        result = _replace_packman_mirror_prefix(url, new_prefix)
        self.assertEqual(result, "https://mirrors.aliyun.com/packman/suse/openSUSE_Tumbleweed/")

    def test_new_prefix_with_trailing_slash(self) -> None:
        """Should handle new_prefix with trailing slash."""
        url = "http://ftp.fau.de/packman/suse/openSUSE_Tumbleweed/"
        new_prefix = "https://mirrors.aliyun.com/packman/"
        result = _replace_packman_mirror_prefix(url, new_prefix)
        self.assertEqual(result, "https://mirrors.aliyun.com/packman/suse/openSUSE_Tumbleweed/")

    def test_new_prefix_without_trailing_slash(self) -> None:
        """Should handle new_prefix without trailing slash."""
        url = "http://ftp.fau.de/packman/suse/openSUSE_Tumbleweed/"
        new_prefix = "https://mirrors.aliyun.com/packman"
        result = _replace_packman_mirror_prefix(url, new_prefix)
        self.assertEqual(result, "https://mirrors.aliyun.com/packman/suse/openSUSE_Tumbleweed/")

    def test_no_leading_slash_in_remainder(self) -> None:
        """Should handle remainder without leading slash."""
        url = "http://ftp.fau.de/packmansuse/openSUSE_Tumbleweed/"
        new_prefix = "https://mirrors.aliyun.com/packman/"
        result = _replace_packman_mirror_prefix(url, new_prefix)
        self.assertEqual(result, "https://mirrors.aliyun.com/packman/packmansuse/openSUSE_Tumbleweed/")

    def test_does_not_match_opensuse_mirror(self) -> None:
        """Should NOT match openSUSE mirror patterns directly, but may use domain fallback."""
        url = "http://download.opensuse.org/distribution/leap/15.6/repo/oss/"
        new_prefix = "https://mirrors.aliyun.com/packman/"
        result = _replace_packman_mirror_prefix(url, new_prefix)
        self.assertEqual(result, "https://mirrors.aliyun.com/packman/distribution/leap/15.6/repo/oss/")


class TestStatusToExitCode(unittest.TestCase):
    """Tests for _status_to_exit_code function."""

    def test_ok_status(self) -> None:
        """Should return exit code 0 for ok status."""
        self.assertEqual(_status_to_exit_code("ok"), 0)

    def test_permission_denied_status(self) -> None:
        """Should return exit code 1 for permission_denied status."""
        self.assertEqual(_status_to_exit_code("permission_denied"), 1)

    def test_pkexec_failed_status(self) -> None:
        """Should return exit code 2 for pkexec_failed status."""
        self.assertEqual(_status_to_exit_code("pkexec_failed"), 2)

    def test_error_status(self) -> None:
        """Should return exit code 3 for error status."""
        self.assertEqual(_status_to_exit_code("error"), 3)


class TestSwitchMirrorPkexec(unittest.TestCase):
    """Tests for switch_mirror_pkexec function."""

    @patch("yast3.core.repositories.switch_mirror.subprocess.run")
    def test_pkexec_success(self, mock_run: MagicMock) -> None:
        """Should return ok when pkexec succeeds with exit code 0."""
        mock_run.return_value.returncode = 0
        result = switch_mirror_pkexec(
            "https://mirror.example.com/opensuse/",
            "https://mirror.example.com/packman/",
        )
        self.assertEqual(result, "ok")

    @patch("yast3.core.repositories.switch_mirror.subprocess.run")
    def test_pkexec_permission_denied(self, mock_run: MagicMock) -> None:
        """Should return permission_denied when pkexec returns exit code 1."""
        mock_run.return_value.returncode = 1
        result = switch_mirror_pkexec(
            "https://mirror.example.com/opensuse/",
            "https://mirror.example.com/packman/",
        )
        self.assertEqual(result, "permission_denied")

    @patch("yast3.core.repositories.switch_mirror.subprocess.run")
    def test_pkexec_failed(self, mock_run: MagicMock) -> None:
        """Should return pkexec_failed when pkexec returns exit code 2."""
        mock_run.return_value.returncode = 2
        result = switch_mirror_pkexec(
            "https://mirror.example.com/opensuse/",
            "https://mirror.example.com/packman/",
        )
        self.assertEqual(result, "pkexec_failed")

    @patch("yast3.core.repositories.switch_mirror.subprocess.run")
    def test_pkexec_error(self, mock_run: MagicMock) -> None:
        """Should return error when pkexec returns other exit codes."""
        mock_run.return_value.returncode = 3
        result = switch_mirror_pkexec(
            "https://mirror.example.com/opensuse/",
            "https://mirror.example.com/packman/",
        )
        self.assertEqual(result, "error")

    @patch("yast3.core.repositories.switch_mirror.subprocess.run")
    def test_pkexec_calls_correct_command(self, mock_run: MagicMock) -> None:
        """Should call pkexec with the correct wrapper script and arguments."""
        mock_run.return_value.returncode = 0
        switch_mirror_pkexec(
            "https://mirror.example.com/opensuse/",
            "https://mirror.example.com/packman/",
        )
        mock_run.assert_called_once_with(
            [
                "pkexec",
                "/usr/libexec/yast3-switch-mirror",
                "--opensuse-url",
                "https://mirror.example.com/opensuse/",
                "--packman-url",
                "https://mirror.example.com/packman/",
            ],
            capture_output=True,
            text=True,
        )


if __name__ == "__main__":
    unittest.main()