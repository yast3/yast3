"""Unit tests for the switch_mirror module."""

import unittest

from yast3.core.repositories.mirrors.switch_mirror import (
    _replace_opensuse_mirror_prefix,
    _replace_packman_mirror_prefix,
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


if __name__ == "__main__":
    unittest.main()