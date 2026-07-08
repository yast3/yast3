"""Unit tests for Flatpak package management core logic."""

import unittest
from subprocess import CompletedProcess
from unittest.mock import patch

from yast3.core.flatpak.package import list_flatpak_packages, list_remote_flatpak_packages


class TestListFlatpakPackages(unittest.TestCase):
    """Tests for list_flatpak_packages function."""

    @patch("yast3.core.flatpak.package.shutil.which")
    def test_returns_empty_when_flatpak_missing(self, mock_which) -> None:
        mock_which.return_value = None

        packages = list_flatpak_packages()

        self.assertEqual(packages, [])

    @patch("yast3.core.flatpak.package.subprocess.run")
    @patch("yast3.core.flatpak.package.shutil.which")
    def test_parses_installed_packages_with_installed_size(self, mock_which, mock_run) -> None:
        mock_which.return_value = "/usr/bin/flatpak"
        mock_run.return_value = CompletedProcess(
            args=["flatpak", "list"],
            returncode=0,
            stdout=(
                "org.mozilla.firefox\tFirefox\tWeb browser\t139.0\tstable\tflathub\t271.4 MB\tsystem\n"
                "org.gnome.Weather\tWeather\tForecast app\t47\tstable\tflathub\t54.8 MB\tuser\n"
            ),
            stderr="",
        )

        packages = list_flatpak_packages()

        self.assertEqual(len(packages), 2)
        self.assertEqual(packages[0].app_id, "org.mozilla.firefox")
        self.assertEqual(packages[0].installed_size, "271.4 MB")
        self.assertEqual(packages[0].scope, "system")
        self.assertEqual(packages[1].app_id, "org.gnome.Weather")
        self.assertEqual(packages[1].installed_size, "54.8 MB")
        self.assertEqual(packages[1].scope, "user")


class TestListRemoteFlatpakPackages(unittest.TestCase):
    """Tests for list_remote_flatpak_packages function."""

    @patch("yast3.core.flatpak.package.subprocess.run")
    @patch("yast3.core.flatpak.package.shutil.which")
    def test_parses_remote_packages_with_download_size(self, mock_which, mock_run) -> None:
        mock_which.return_value = "/usr/bin/flatpak"
        mock_run.return_value = CompletedProcess(
            args=["flatpak", "remote-ls"],
            returncode=0,
            stdout=(
                "org.mozilla.firefox\tFirefox\tWeb browser\t139.0\t96.6 MB\tstable\n"
                "org.gnome.Weather\tWeather\tForecast app\t47\t8.2 MB\tstable\n"
            ),
            stderr="",
        )

        packages = list_remote_flatpak_packages("flathub")

        self.assertEqual(len(packages), 2)
        self.assertEqual(packages[0].app_id, "org.mozilla.firefox")
        self.assertEqual(packages[0].download_size, "96.6 MB")
        self.assertEqual(packages[0].branch, "stable")
        self.assertEqual(packages[1].app_id, "org.gnome.Weather")
        self.assertEqual(packages[1].download_size, "8.2 MB")


if __name__ == "__main__":
    unittest.main()
